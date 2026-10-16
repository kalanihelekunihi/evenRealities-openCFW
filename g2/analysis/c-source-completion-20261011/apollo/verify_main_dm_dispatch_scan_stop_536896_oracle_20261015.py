#!/usr/bin/env python3
"""Compare compiled scan-stop dispatch and HCI payload with pinned native."""
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
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/display_ble_dm_dispatch_scan_stop_536896.c'
UPSTREAM = ROOT / 'third-party/upstream/cordio/ble-host/sources/stack/dm/dm_scan_leg.c'
PAYLOAD = G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT = G2 / 'build/c-firmware/20261015/main-dm-dispatch-scan-stop-536896'
PINNED_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
SHIM = '''#include <stdint.h>
uint8_t audio_ble_dm_stack_rows_200738dc[0x20];
__attribute__((noinline)) void *audio_ble_hci_cmd_alloc_52ae38(uint16_t a,uint16_t b){(void)a;(void)b;return 0;}
__attribute__((noinline)) void audio_ble_hci_cmd_send(void*a){(void)a;}
'''

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PINNED_SHA:
        raise RuntimeError('Apollo payload changed')
    if 'HciLeSetScanEnableCmd(FALSE, 0)' not in UPSTREAM.read_text():
        raise RuntimeError('Cordio scan-stop contract changed')
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        shim, elf = Path(td) / 'shim.c', Path(td) / 'oracle.elf'
        shim.write_text(SHIM)
        subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4',
                        '-mthumb', '-std=c11', '-ffreestanding', '-fno-builtin',
                        '-O2', '-nostdlib', '-Wl,-Ttext=0x100000',
                        '-Wl,-e,audio_ble_dm_dispatch_536896',
                        str(SOURCE), str(shim), '-o', str(elf)], check=True)
        with elf.open('rb') as f:
            image = ELFFile(f)
            segments = [(s['p_vaddr'], s.data()) for s in image.iter_segments()
                        if s['p_type'] == 'PT_LOAD']
            symbols = {s.name: s['st_value'] for s in
                       image.get_section_by_name('.symtab').iter_symbols()}

        def run(compiled, state, allocated, seed):
            cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            cpu.mem_map(0x400000, 0x400000)
            cpu.mem_write(0x438000, blob)
            cpu.mem_map(0x100000, 0x100000)
            for address, data in segments:
                cpu.mem_write(address, data)
            cpu.mem_map(0x20000000, 0x100000)
            rows = symbols['audio_ble_dm_stack_rows_200738dc'] if compiled else 0x200738dc
            initial = bytearray((seed + i * 3) & 0xff for i in range(32))
            initial[0x18] = state
            cpu.mem_write(rows, bytes(initial))
            cpu.mem_write(0x20001000, bytes((0xa5,) * 16))
            alloc_addr = (symbols['audio_ble_hci_cmd_alloc_52ae38'] & ~1) if compiled else 0x52ae38
            send_addr = (symbols['audio_ble_hci_cmd_send'] & ~1) if compiled else 0x52ae5e
            calls = []
            def hook(uc, addr, size, user):
                if addr == alloc_addr:
                    calls.append(('alloc', uc.reg_read(A.UC_ARM_REG_R0) & 0xffff,
                                  uc.reg_read(A.UC_ARM_REG_R1) & 0xffff))
                    uc.reg_write(A.UC_ARM_REG_R0, 0x20001000 if allocated else 0)
                    uc.reg_write(A.UC_ARM_REG_PC, uc.reg_read(A.UC_ARM_REG_LR))
                elif addr == send_addr:
                    calls.append(('send', uc.reg_read(A.UC_ARM_REG_R0)))
                    uc.reg_write(A.UC_ARM_REG_PC, uc.reg_read(A.UC_ARM_REG_LR))
            cpu.hook_add(UC_HOOK_CODE, hook)
            cpu.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
            cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
            entry = symbols['audio_ble_dm_dispatch_536896'] if compiled else 0x536896
            cpu.emu_start(entry | 1, 0x600000, count=1000)
            return calls, bytes(cpu.mem_read(rows, 32)), bytes(cpu.mem_read(0x20001000, 16))

        cases = 0
        for state in (0, 1, 2, 3, 0x7f, 0xff):
            for allocated in (False, True):
                for seed in (0, 0xa5):
                    stock = run(False, state, allocated, seed)
                    candidate = run(True, state, allocated, seed)
                    if stock != candidate:
                        raise RuntimeError(f'{state=} {allocated=} {seed=}: {stock} != {candidate}')
                    cases += 1
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_DM_DISPATCH_SCAN_STOP_ORACLE',
               'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
               'upstream_source': str(UPSTREAM.relative_to(ROOT)),
               'upstream_sha256': sha(UPSTREAM), 'payload_sha256': PINNED_SHA,
               'cases': cases,
               'comparison_scope': 'Native state transition, HCI allocation opcode/length, two payload bytes and send call.',
               'limits': ['Allocator/send effects, final controller behavior and whole-image RAM placement remain open.']}
    path = OUT / 'oracle-receipt.json'
    path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], cases)

if __name__ == '__main__': main()
