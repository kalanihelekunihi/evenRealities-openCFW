#!/usr/bin/env python3
"""Compare native and C scan report filtering and AD-type traversal."""
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
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/display_ble_dm_stack_hci_scan_complete_5368b6.c'
PAYLOAD = G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT = G2 / 'build/c-firmware/20261015/main-dm-stack-hci-scan-complete-5368b6'
PINNED_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
SHIM = '''#include <stdint.h>
uint8_t audio_ble_dm_stack_rows_200738dc[0x20];
uint8_t audio_ble_dm_handler_state[0x18];
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
                        '-Wl,-e,audio_ble_dm_stack_hci_scan_complete_5368b6',
                        str(SOURCE), str(shim), '-o', str(elf)], check=True)
        with elf.open('rb') as f:
            image = ELFFile(f)
            segments = [(s['p_vaddr'], s.data()) for s in image.iter_segments()
                        if s['p_type'] == 'PT_LOAD']
            symbols = {s.name: s['st_value'] for s in
                       image.get_section_by_name('.symtab').iter_symbols()}

        def run(compiled, state, mask, pending, report_type, fields):
            cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            cpu.mem_map(0x400000, 0x400000)
            cpu.mem_write(0x438000, blob)
            cpu.mem_map(0x100000, 0x100000)
            for address, data in segments:
                cpu.mem_write(address, data)
            cpu.mem_map(0x20000000, 0x100000)
            rows = symbols['audio_ble_dm_stack_rows_200738dc'] if compiled else 0x200738dc
            dm = symbols['audio_ble_dm_handler_state'] if compiled else 0x20073b78
            initial = bytearray((i * 9 + 0x3d) & 0xff for i in range(32))
            initial[0x18], initial[0x1c], initial[0x1d] = state, pending, mask
            cpu.mem_write(rows, bytes(initial))
            cpu.mem_write(dm, bytes(24))
            cpu.mem_write(dm + 8, (0x110001).to_bytes(4, 'little'))
            cpu.mem_write(0x20002000, fields + bytes(32-len(fields)))
            event = bytearray((i * 7 + 0x23) & 0xff for i in range(16))
            event[2] = 6
            event[4:8] = (0x20002000).to_bytes(4, 'little')
            event[8] = len(fields)
            event[10] = report_type
            cpu.mem_write(0x20001000, bytes(event))
            calls = []
            def hook(uc, addr, size, user):
                if addr == 0x110000:
                    calls.append(('callback', uc.reg_read(A.UC_ARM_REG_R0)))
                    uc.reg_write(A.UC_ARM_REG_PC, uc.reg_read(A.UC_ARM_REG_LR))
            cpu.hook_add(UC_HOOK_CODE, hook)
            cpu.reg_write(A.UC_ARM_REG_R0, 0x20001000)
            cpu.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
            cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
            entry = symbols['audio_ble_dm_stack_hci_scan_complete_5368b6'] if compiled else 0x5368b6
            cpu.emu_start(entry | 1, 0x600000, count=1000)
            return calls, bytes(cpu.mem_read(rows, 32)), bytes(cpu.mem_read(0x20001000, 16))

        cases = 0
        for state in (1, 2, 3):
            for mask in (0, 1, 3):
                for pending in (0, 1):
                    for report_type in (0, 4):
                        for fields in (bytes((2, 1, 1)), bytes((2, 1, 2)),
                                       bytes((2, 9, 0, 2, 1, 1)), bytes((2, 9, 0))):
                            stock = run(False, state, mask, pending, report_type, fields)
                            candidate = run(True, state, mask, pending, report_type, fields)
                            if stock != candidate:
                                raise RuntimeError(f'{state=} {mask=} {pending=} {report_type=} {fields.hex()}: {stock} != {candidate}')
                            cases += 1
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_DM_STACK_HCI_SCAN_COMPLETE_ORACLE',
               'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
               'payload_sha256': PINNED_SHA, 'cases': cases,
               'comparison_scope': 'Native scan report state/mask filtering, AD field traversal, pending flag and callback.',
               'limits': ['Only bounded, valid AD field examples are compared; final radio/controller behavior remains open.']}
    path = OUT / 'oracle-receipt.json'
    path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], cases, sha(path))

if __name__ == '__main__': main()
