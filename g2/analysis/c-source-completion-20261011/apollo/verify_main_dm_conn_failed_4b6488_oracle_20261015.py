#!/usr/bin/env python3
"""Compare compiled Cordio connection-failure action with Apollo native calls."""
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import UC_ARCH_ARM, UC_HOOK_CODE, UC_MODE_THUMB, Uc
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/display_ble_dm_conn_failed_4b6488.c'
UPSTREAM = ROOT / 'third-party/upstream/cordio/ble-host/sources/stack/dm/dm_conn.c'
PAYLOAD = G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT = G2 / 'build/c-firmware/20261015/main-dm-conn-failed-4b6488'
PINNED_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
SHIM = '''#include <stdint.h>
__attribute__((noinline)) void audio_ble_dm_ccb_dealloc_4b5ef0(void*a){(void)a;}
__attribute__((noinline)) uint32_t audio_ble_dm_conn_num_4b62ca(void){return 0;}
__attribute__((noinline)) void audio_ble_dm_dev_pass_priv_4b2ea6(uint8_t a,uint8_t b,uint32_t c,uint32_t d){(void)a;(void)b;(void)c;(void)d;}
__attribute__((noinline)) void audio_ble_dm_conn_exec_callback_4b62ea(void*a){(void)a;}
'''
CHILDREN = {
    'dealloc': ('audio_ble_dm_ccb_dealloc_4b5ef0', 0x4b5ef0),
    'num': ('audio_ble_dm_conn_num_4b62ca', 0x4b62ca),
    'dev_priv': ('audio_ble_dm_dev_pass_priv_4b2ea6', 0x4b2ea6),
    'callback': ('audio_ble_dm_conn_exec_callback_4b62ea', 0x4b62ea),
}

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PINNED_SHA:
        raise RuntimeError('Apollo payload changed')
    upstream = UPSTREAM.read_text()
    start = upstream.index('void dmConnSmActConnFailed(')
    end = upstream.index('\n}', start)
    body = upstream[start:end]
    for term in ('dmConnCcbDealloc', 'dmConnNum',
                 'dmDevPassEvtToDevPriv', 'dmConnExecCback'):
        if term not in body:
            raise RuntimeError('Cordio close action source changed')
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        shim, elf = Path(td) / 'shim.c', Path(td) / 'oracle.elf'
        shim.write_text(SHIM)
        subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4',
                        '-mthumb', '-std=c11', '-ffreestanding', '-fno-builtin',
                        '-O2', '-nostdlib', '-Wl,-Ttext=0x100000',
                        '-Wl,-e,audio_ble_dm_conn_sm_act_failed_4b6488',
                        str(SOURCE), str(shim), '-o', str(elf)], check=True)
        with elf.open('rb') as f:
            image = ELFFile(f)
            segments = [(s['p_vaddr'], s.data()) for s in image.iter_segments()
                        if s['p_type'] == 'PT_LOAD']
            symbols = {s.name: s['st_value'] for s in
                       image.get_section_by_name('.symtab').iter_symbols()}

        def run(compiled, role, count, conn_id, initial_event):
            cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            cpu.mem_map(0x400000, 0x400000)
            cpu.mem_write(0x438000, blob)
            cpu.mem_map(0x100000, 0x100000)
            for address, data in segments:
                cpu.mem_write(address, data)
            cpu.mem_map(0x20000000, 0x10000)
            ccb = bytearray(64)
            ccb[0x10] = conn_id
            ccb[0x19] = role
            msg = bytearray((initial_event,) * 64)
            cpu.mem_write(0x20001000, bytes(ccb))
            cpu.mem_write(0x20002000, bytes(msg))
            addresses = {(symbols[name] & ~1) if compiled else native: label
                         for label, (name, native) in CHILDREN.items()}
            calls = []
            def hook(uc, addr, size, user):
                label = addresses.get(addr)
                if label is None:
                    return
                args = tuple(uc.reg_read(x) for x in
                             (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                              A.UC_ARM_REG_R2, A.UC_ARM_REG_R3))
                if label == 'dealloc':
                    calls.append((label, args[0]))
                elif label == 'num':
                    calls.append((label,))
                    uc.reg_write(A.UC_ARM_REG_R0, count)
                elif label == 'dev_priv':
                    calls.append((label, args[0] & 0xff, args[1] & 0xff,
                                  args[2], args[3]))
                else:
                    calls.append((label, args[0],
                                  bytes(uc.mem_read(0x20002000, 64))))
                uc.reg_write(A.UC_ARM_REG_PC, uc.reg_read(A.UC_ARM_REG_LR))
            cpu.hook_add(UC_HOOK_CODE, hook)
            cpu.reg_write(A.UC_ARM_REG_R0, 0x20001000)
            cpu.reg_write(A.UC_ARM_REG_R1, 0x20002000)
            cpu.reg_write(A.UC_ARM_REG_SP, 0x2000ff00)
            cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
            entry = symbols['audio_ble_dm_conn_sm_act_failed_4b6488'] if compiled else 0x4b6488
            cpu.emu_start(entry | 1, 0x600000, count=2000)
            return calls, bytes(cpu.mem_read(0x20001000, 64)), bytes(cpu.mem_read(0x20002000, 64))

        cases = 0
        for role in (0, 1, 2):
            for count in (0, 1):
                for conn_id in (0, 1, 0x7f, 0xff):
                    for event in (0, 0x55, 0xff):
                        stock = run(False, role, count, conn_id, event)
                        candidate = run(True, role, count, conn_id, event)
                        if stock != candidate:
                            raise RuntimeError(f'{role=} {count=} {conn_id=} {event=}: {stock} != {candidate}')
                        cases += 1
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_DM_CONN_FAILED_ORACLE',
               'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
               'upstream_source': str(UPSTREAM.relative_to(ROOT)),
               'upstream_sha256': sha(UPSTREAM), 'payload_sha256': PINNED_SHA,
               'cases': cases,
               'comparison_scope': 'Native call order, arguments, and CCB/message mutations over role/count/connection/event variants.',
               'limits': ['Four child effects are cut at their native call boundaries; complete connection lifecycle and hardware behavior remain open.']}
    path = OUT / 'oracle-receipt.json'
    path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], cases)

if __name__ == '__main__': main()
