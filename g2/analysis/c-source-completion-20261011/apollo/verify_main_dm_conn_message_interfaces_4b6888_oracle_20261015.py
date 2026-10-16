#!/usr/bin/env python3
"""Compare compiled Cordio DM message interfaces against pinned stock calls."""
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
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/display_ble_dm_conn_message_interfaces_4b6888.c'
UPSTREAM = ROOT / 'third-party/upstream/cordio/ble-host/sources/stack/dm/dm_conn.c'
PAYLOAD = G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT = G2 / 'build/c-firmware/20261015/main-dm-conn-message-interfaces-4b6888'
PINNED_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
SHIM = '''#include <stdint.h>
__attribute__((noinline)) void *dmConnCcbById(uint8_t a){(void)a;return 0;}
__attribute__((noinline)) void audio_ble_dm_conn_sm_execute_533ef4(void*a,void*b){(void)a;(void)b;}
__attribute__((noinline)) void audio_ble_dm_conn_upd_execute_4b6532(void*a,void*b){(void)a;(void)b;}
'''
CHILDREN = {
    'lookup': ('dmConnCcbById', 0x4b62a8),
    'execute': ('audio_ble_dm_conn_sm_execute_533ef4', 0x533ef4),
    'update': ('audio_ble_dm_conn_upd_execute_4b6532', 0x4b6532),
}
ENTRIES = [('audio_ble_dm_conn_msg_handler_4b6888', 0x4b6888),
           ('audio_ble_dm_conn_upd_msg_handler_4b6a16', 0x4b6a16)]

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PINNED_SHA:
        raise RuntimeError('Apollo payload changed')
    upstream = UPSTREAM.read_text()
    for name, terms in [('dmConnMsgHandler', ('dmConnCcbById', 'dmConnSmExecute')),
                        ('dmConnUpdMsgHandler', ('dmConnCcbById', 'DM_CONN_SM_ST_CONNECTED', 'dmConnUpdExecute'))]:
        start = upstream.index('void ' + name + '(')
        body = upstream[start:upstream.index('\n}', start)]
        if not all(term in body for term in terms):
            raise RuntimeError(f'Cordio {name} changed')
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        shim, elf = Path(td) / 'shim.c', Path(td) / 'oracle.elf'
        shim.write_text(SHIM)
        subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4',
                        '-mthumb', '-std=c11', '-ffreestanding', '-fno-builtin',
                        '-O2', '-nostdlib', '-Wl,-Ttext=0x100000',
                        '-Wl,-e,audio_ble_dm_conn_msg_handler_4b6888',
                        str(SOURCE), str(shim), '-o', str(elf)], check=True)
        with elf.open('rb') as f:
            image = ELFFile(f)
            segments = [(s['p_vaddr'], s.data()) for s in image.iter_segments()
                        if s['p_type'] == 'PT_LOAD']
            symbols = {s.name: s['st_value'] for s in
                       image.get_section_by_name('.symtab').iter_symbols()}

        def run(compiled, name, native, param, found, state, event):
            cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            cpu.mem_map(0x400000, 0x400000)
            cpu.mem_write(0x438000, blob)
            cpu.mem_map(0x100000, 0x100000)
            for address, data in segments:
                cpu.mem_write(address, data)
            cpu.mem_map(0x20000000, 0x10000)
            ccb = bytearray(64)
            ccb[0x15] = state
            msg = bytearray(range(64))
            msg[:2] = param.to_bytes(2, 'little')
            msg[2] = event
            cpu.mem_write(0x20001000, bytes(ccb))
            cpu.mem_write(0x20002000, bytes(msg))
            addresses = {(symbols[symbol] & ~1) if compiled else stock: label
                         for label, (symbol, stock) in CHILDREN.items()}
            calls = []
            def hook(uc, addr, size, user):
                label = addresses.get(addr)
                if label is None:
                    return
                a = uc.reg_read(A.UC_ARM_REG_R0)
                b = uc.reg_read(A.UC_ARM_REG_R1)
                if label == 'lookup':
                    calls.append((label, a & 0xff))
                    uc.reg_write(A.UC_ARM_REG_R0, 0x20001000 if found else 0)
                else:
                    calls.append((label, a, b))
                uc.reg_write(A.UC_ARM_REG_PC, uc.reg_read(A.UC_ARM_REG_LR))
            cpu.hook_add(UC_HOOK_CODE, hook)
            cpu.reg_write(A.UC_ARM_REG_R0, 0x20002000)
            cpu.reg_write(A.UC_ARM_REG_SP, 0x2000ff00)
            cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
            entry = symbols[name] if compiled else native
            cpu.emu_start(entry | 1, 0x600000, count=300)
            return calls, bytes(cpu.mem_read(0x20001000, 64)), bytes(cpu.mem_read(0x20002000, 64))

        cases = 0
        for name, native in ENTRIES:
            for param in (0, 1, 0x1234, 0xffff):
                for found in (False, True):
                    for state in (0, 3, 7):
                        for event in (0, 0x25, 0xff):
                            stock = run(False, name, native, param, found, state, event)
                            candidate = run(True, name, native, param, found, state, event)
                            if stock != candidate:
                                raise RuntimeError(f'{name=} {param=} {found=} {state=} {event=}: {stock} != {candidate}')
                            cases += 1
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_DM_CONN_MESSAGE_INTERFACES_ORACLE',
               'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
               'upstream_source': str(UPSTREAM.relative_to(ROOT)),
               'upstream_sha256': sha(UPSTREAM), 'payload_sha256': PINNED_SHA,
               'cases': cases,
               'comparison_scope': 'Native CCB lookup, connected gate, child calls and unchanged RAM over message variants.',
               'limits': ['CCB lookup and executor effects are cut at native call boundaries.',
                          'The connection state-machine executor is a newly exposed C source obligation.']}
    path = OUT / 'oracle-receipt.json'
    path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], cases)

if __name__ == '__main__': main()
