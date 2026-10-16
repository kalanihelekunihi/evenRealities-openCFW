#!/usr/bin/env python3
"""Compare native and C scan-start dispatch and both LE HCI commands."""
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
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/display_ble_dm_dispatch_scan_start_536820.c'
PAYLOAD = G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT = G2 / 'build/c-firmware/20261015/main-dm-dispatch-scan-start-536820'
PINNED_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
SHIM = '''#include <stdint.h>
uint8_t audio_ble_dm_stack_rows_200738dc[0x20];
uint8_t audio_ble_dm_handler_state[0x18];
__attribute__((noinline)) void *audio_ble_hci_cmd_alloc_52ae38(uint16_t a,uint16_t b){(void)a;(void)b;return 0;}
__attribute__((noinline)) void audio_ble_hci_cmd_send(void *p){(void)p;}
'''

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PINNED_SHA:
        raise RuntimeError('Apollo payload changed')
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        shim, elf = Path(td) / 'shim.c', Path(td) / 'oracle.elf'
        shim.write_text(SHIM)
        subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4',
                        '-mthumb', '-std=c11', '-ffreestanding', '-fno-builtin',
                        '-O2', '-nostdlib', '-Wl,-Ttext=0x100000',
                        '-Wl,-e,audio_ble_dm_dispatch_536820',
                        str(SOURCE), str(shim), '-o', str(elf)], check=True)
        with elf.open('rb') as f:
            image = ELFFile(f)
            segments = [(s['p_vaddr'], s.data()) for s in image.iter_segments()
                        if s['p_type'] == 'PT_LOAD']
            symbols = {s.name: s['st_value'] for s in
                       image.get_section_by_name('.symtab').iter_symbols()}

        def run(compiled, state, mode, own_addr, privacy, allocated):
            cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            cpu.mem_map(0x400000, 0x400000)
            cpu.mem_write(0x438000, blob)
            cpu.mem_map(0x100000, 0x100000)
            for address, data in segments:
                cpu.mem_write(address, data)
            cpu.mem_map(0x20000000, 0x100000)
            rows = symbols['audio_ble_dm_stack_rows_200738dc'] if compiled else 0x200738dc
            dm = symbols['audio_ble_dm_handler_state'] if compiled else 0x20073b78
            initial = bytearray((i * 7 + 0x31) & 0xff for i in range(32))
            initial[0x18] = state
            initial[0x10:0x12] = (0x1234).to_bytes(2, 'little')
            initial[0x14:0x16] = (0x5678).to_bytes(2, 'little')
            cpu.mem_write(rows, bytes(initial))
            handler = bytearray(24)
            handler[0x0f], handler[0x13], handler[0x16] = own_addr, 0x35, privacy
            cpu.mem_write(dm, bytes(handler))
            message = bytearray((i * 11 + 0x26) & 0xff for i in range(24))
            message[5], message[7], message[8], message[9], message[12] = 0x03, mode, 0xcd, 0xab, 0x01
            cpu.mem_write(0x20001000, bytes(message))
            cpu.mem_write(0x20002000, bytes((0xa5,) * 16))
            cpu.mem_write(0x20002100, bytes((0xa5,) * 16))
            alloc_addr = (symbols['audio_ble_hci_cmd_alloc_52ae38'] & ~1) if compiled else 0x52ae38
            send_addr = (symbols['audio_ble_hci_cmd_send'] & ~1) if compiled else 0x52ae5e
            calls = []
            alloc_count = 0
            def hook(uc, addr, size, user):
                nonlocal alloc_count
                if addr == alloc_addr:
                    calls.append(('alloc', uc.reg_read(A.UC_ARM_REG_R0) & 0xffff,
                                  uc.reg_read(A.UC_ARM_REG_R1) & 0xffff))
                    result = (0x20002000 + alloc_count * 0x100) if allocated else 0
                    alloc_count += 1
                    uc.reg_write(A.UC_ARM_REG_R0, result)
                elif addr == send_addr:
                    p = uc.reg_read(A.UC_ARM_REG_R0)
                    calls.append(('send', bytes(uc.mem_read(p + 3, 7 if p == 0x20002000 else 2)).hex()))
                else:
                    return
                uc.reg_write(A.UC_ARM_REG_PC, uc.reg_read(A.UC_ARM_REG_LR))
            cpu.hook_add(UC_HOOK_CODE, hook)
            cpu.reg_write(A.UC_ARM_REG_R0, 0x20001000)
            cpu.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
            cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
            entry = symbols['audio_ble_dm_dispatch_536820'] if compiled else 0x536820
            cpu.emu_start(entry | 1, 0x600000, count=2000)
            return calls, bytes(cpu.mem_read(rows, 32))

        cases = 0
        for state in (0, 1, 2, 3):
            for mode in (0, 1, 2, 4):
                for own_addr in (0, 1, 4):
                    for privacy in (0, 1):
                        for allocated in (False, True):
                            stock = run(False, state, mode, own_addr, privacy, allocated)
                            candidate = run(True, state, mode, own_addr, privacy, allocated)
                            if stock != candidate:
                                raise RuntimeError(f'{state=} {mode=} {own_addr=} {privacy=} {allocated=}: {stock} != {candidate}')
                            cases += 1
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_DM_DISPATCH_SCAN_START_ORACLE',
               'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
               'payload_sha256': PINNED_SHA, 'cases': cases,
               'comparison_scope': 'Native scan state, own address mapping, HCI allocation and seven/two-byte payloads.',
               'limits': ['Command allocator and sender effects, full RAM placement and radio behavior remain open.']}
    path = OUT / 'oracle-receipt.json'
    path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], cases, sha(path))

if __name__ == '__main__': main()
