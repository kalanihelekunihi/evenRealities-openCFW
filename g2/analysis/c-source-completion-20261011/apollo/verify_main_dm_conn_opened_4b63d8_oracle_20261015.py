#!/usr/bin/env python3
"""Compare compiled connection-open action with pinned Apollo Main calls."""
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
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/display_ble_dm_conn_opened_4b63d8.c'
UPSTREAM = ROOT / 'third-party/upstream/cordio/ble-host/sources/stack/dm/dm_conn.c'
PAYLOAD = G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT = G2 / 'build/c-firmware/20261015/main-dm-conn-opened-4b63d8'
PINNED_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
SHIM = '''#include <stdint.h>
uint8_t audio_ble_dm_handler_state[0x18];
__attribute__((noinline)) void audio_ble_copy_address6_4d293c(void*a,const void*b){(void)a;(void)b;}
__attribute__((noinline)) uint32_t audio_ble_pair_address_type_4d2aa8(uint32_t a){return a;}
__attribute__((noinline)) uint8_t *HciGetBdAddr(void){return (uint8_t*)0x200714e0;}
__attribute__((noinline)) void audio_ble_dm_dev_pass_priv_4b2ea6(uint8_t a,uint8_t b,uint32_t c,uint32_t d){(void)a;(void)b;(void)c;(void)d;}
__attribute__((noinline)) uint32_t audio_ble_dm_conn_num_4b62ca(void){return 0;}
__attribute__((noinline)) void audio_ble_dm_dev_pass_conn_cte_4b3008(uint8_t a,uint8_t b){(void)a;(void)b;}
__attribute__((noinline)) void audio_ble_dm_conn_exec_callback_4b62ea(void*a){(void)a;}
'''
CHILDREN = {
    'copy': ('audio_ble_copy_address6_4d293c', 0x4d293c),
    'type': ('audio_ble_pair_address_type_4d2aa8', 0x4d2aa8),
    'hci': ('HciGetBdAddr', 0x530d30),
    'priv': ('audio_ble_dm_dev_pass_priv_4b2ea6', 0x4b2ea6),
    'num': ('audio_ble_dm_conn_num_4b62ca', 0x4b62ca),
    'cte': ('audio_ble_dm_dev_pass_conn_cte_4b3008', 0x4b3008),
    'callback': ('audio_ble_dm_conn_exec_callback_4b62ea', 0x4b62ea),
}

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PINNED_SHA:
        raise RuntimeError('Apollo payload changed')
    upstream = UPSTREAM.read_text()
    start = upstream.index('void dmConnSmActConnOpened(')
    end = upstream.index('\n}', start)
    body = upstream[start:end]
    for term in ('BdaCpy', 'DmHostAddrType', 'HciGetBdAddr',
                 'dmDevPassEvtToDevPriv', 'dmDevPassEvtToConnCte', 'dmConnExecCback'):
        if term not in body:
            raise RuntimeError('Cordio open action source changed')
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        shim, elf = Path(td) / 'shim.c', Path(td) / 'oracle.elf'
        shim.write_text(SHIM)
        subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4',
                        '-mthumb', '-std=c11', '-ffreestanding', '-fno-builtin',
                        '-O2', '-nostdlib', '-Wl,-Ttext=0x100000',
                        '-Wl,-e,audio_ble_dm_conn_sm_act_opened_4b63d8',
                        str(SOURCE), str(shim), '-o', str(elf)], check=True)
        with elf.open('rb') as f:
            image = ELFFile(f)
            segments = [(s['p_vaddr'], s.data()) for s in image.iter_segments()
                        if s['p_type'] == 'PT_LOAD']
            symbols = {s.name: s['st_value'] for s in
                       image.get_section_by_name('.symtab').iter_symbols()}

        def run(compiled, role, count, local_type, addr_type, seed):
            cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            cpu.mem_map(0x400000, 0x400000)
            cpu.mem_write(0x438000, blob)
            cpu.mem_map(0x100000, 0x100000)
            for address, data in segments:
                cpu.mem_write(address, data)
            cpu.mem_map(0x20000000, 0x80000)
            ccb = bytes(((seed + i * 3) & 0xff for i in range(64)))
            msg = bytearray(((seed + i * 7) & 0xff for i in range(64)))
            msg[6:8] = b'\x34\x12'
            msg[8] = role
            msg[9] = addr_type
            cpu.mem_write(0x20001000, ccb)
            cpu.mem_write(0x20002000, bytes(msg))
            state = symbols['audio_ble_dm_handler_state'] if compiled else 0x20073b78
            state_bytes = bytearray(0x18)
            state_bytes[:6] = bytes((0x90 + i for i in range(6)))
            state_bytes[0x0d] = local_type if role == 0 else 1 - local_type
            state_bytes[0x0e] = local_type if role != 0 else 1 - local_type
            cpu.mem_write(state, bytes(state_bytes))
            cpu.mem_write(0x200714e0, b'ABCDEF')
            addresses = {(symbols[name] & ~1) if compiled else native: label
                         for label, (name, native) in CHILDREN.items()}
            calls = []
            regs = (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                    A.UC_ARM_REG_R2, A.UC_ARM_REG_R3)
            def hook(uc, addr, size, user):
                label = addresses.get(addr)
                if label is None:
                    return
                a = tuple(uc.reg_read(x) for x in regs)
                if label == 'copy':
                    data = bytes(uc.mem_read(a[1], 6))
                    calls.append((label, a[0] - 0x20001000, data))
                    uc.mem_write(a[0], data)
                elif label == 'type':
                    calls.append((label, a[0] & 0xff))
                    typ = a[0] & 0xff
                    uc.reg_write(A.UC_ARM_REG_R0, 0 if typ == 2 else 1 if typ == 3 else typ)
                elif label == 'hci':
                    calls.append((label,))
                    uc.reg_write(A.UC_ARM_REG_R0, 0x200714e0)
                elif label == 'num':
                    calls.append((label,))
                    uc.reg_write(A.UC_ARM_REG_R0, count)
                elif label == 'priv':
                    calls.append((label, a[0] & 0xff, a[1] & 0xff, a[2], a[3]))
                elif label == 'cte':
                    calls.append((label, a[0] & 0xff, a[1] & 0xff))
                else:
                    calls.append((label, a[0] - 0x20002000,
                                  bytes(uc.mem_read(0x20002000, 64))))
                uc.reg_write(A.UC_ARM_REG_PC, uc.reg_read(A.UC_ARM_REG_LR))
            cpu.hook_add(UC_HOOK_CODE, hook)
            cpu.reg_write(A.UC_ARM_REG_R0, 0x20001000)
            cpu.reg_write(A.UC_ARM_REG_R1, 0x20002000)
            cpu.reg_write(A.UC_ARM_REG_SP, 0x2007ff00)
            cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
            entry = symbols['audio_ble_dm_conn_sm_act_opened_4b63d8'] if compiled else 0x4b63d8
            cpu.emu_start(entry | 1, 0x600000, count=3000)
            return calls, bytes(cpu.mem_read(0x20001000, 64)), bytes(cpu.mem_read(0x20002000, 64))

        cases = 0
        for role in (0, 1, 2):
            for count in (0, 1, 2):
                for local_type in (0, 1):
                    for addr_type in (0, 2, 3):
                        for seed in (0, 0x55):
                            stock = run(False, role, count, local_type, addr_type, seed)
                            candidate = run(True, role, count, local_type, addr_type, seed)
                            if stock != candidate:
                                raise RuntimeError(f'{role=} {count=} {local_type=} {addr_type=} {seed=}: {stock} != {candidate}')
                            cases += 1
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_DM_CONN_OPENED_ORACLE',
               'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
               'upstream_source': str(UPSTREAM.relative_to(ROOT)),
               'upstream_sha256': sha(UPSTREAM), 'payload_sha256': PINNED_SHA,
               'cases': cases,
               'comparison_scope': 'Native address copies, CCB/message bytes, role branches and child call order/arguments.',
               'limits': ['Seven helper effects are cut at native call boundaries; full connection lifecycle and hardware behavior remain open.']}
    path = OUT / 'oracle-receipt.json'
    path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], cases)

if __name__ == '__main__': main()
