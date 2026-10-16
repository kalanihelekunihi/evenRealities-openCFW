#!/usr/bin/env python3
"""Compare stock and C DM reset dispatch state, timer and callback effects."""
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
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/display_ble_dm_stack_reset_536918.c'
PAYLOAD = G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT = G2 / 'build/c-firmware/20261015/main-dm-stack-reset-536918'
PINNED_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
SHIM = '''#include <stdint.h>
uint8_t audio_ble_dm_stack_rows_200738dc[0x20];
uint8_t audio_ble_dm_handler_state[0x18];
__attribute__((noinline)) void WsfTimerStop(void *p){(void)p;}
__attribute__((noinline)) void audio_ble_dm_stack_state_init(void){}
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
                        '-Wl,-e,audio_ble_dm_stack_reset_536918',
                        str(SOURCE), str(shim), '-o', str(elf)], check=True)
        with elf.open('rb') as f:
            image = ELFFile(f)
            segments = [(s['p_vaddr'], s.data()) for s in image.iter_segments()
                        if s['p_type'] == 'PT_LOAD']
            symbols = {s.name: s['st_value'] for s in
                       image.get_section_by_name('.symtab').iter_symbols()}

        def run(compiled, state, seed):
            cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            cpu.mem_map(0x400000, 0x400000)
            cpu.mem_write(0x438000, blob)
            cpu.mem_map(0x100000, 0x100000)
            for address, data in segments:
                cpu.mem_write(address, data)
            cpu.mem_map(0x20000000, 0x100000)
            rows = symbols['audio_ble_dm_stack_rows_200738dc'] if compiled else 0x200738dc
            dm = symbols['audio_ble_dm_handler_state'] if compiled else 0x20073b78
            initial = bytearray((seed + i * 7) & 0xff for i in range(32))
            initial[0x18] = state
            cpu.mem_write(rows, bytes(initial))
            cpu.mem_write(dm, bytes(24))
            cpu.mem_write(dm + 8, (0x110001).to_bytes(4, 'little'))
            timer = (symbols['WsfTimerStop'] & ~1) if compiled else 0x52a4d2
            reset = (symbols['audio_ble_dm_stack_state_init'] & ~1) if compiled else 0x55ba70
            calls = []
            def hook(uc, addr, size, user):
                if addr == timer:
                    calls.append(('timer', uc.reg_read(A.UC_ARM_REG_R0) - rows))
                elif addr == 0x110000:
                    event = uc.reg_read(A.UC_ARM_REG_R0)
                    calls.append(('callback', bytes(uc.mem_read(event + 2, 2)).hex()))
                elif addr == reset:
                    calls.append(('reset',))
                else:
                    return
                uc.reg_write(A.UC_ARM_REG_PC, uc.reg_read(A.UC_ARM_REG_LR))
            cpu.hook_add(UC_HOOK_CODE, hook)
            cpu.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
            cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
            try:
                cpu.emu_start((symbols['audio_ble_dm_stack_reset_536918'] if compiled else 0x536918) | 1,
                              0x600000, count=1000)
            except Exception as exc:
                raise RuntimeError(f'{compiled=} {state=} {seed=} pc={cpu.reg_read(A.UC_ARM_REG_PC):#x} calls={calls}') from exc
            return calls, bytes(cpu.mem_read(rows, 32))

        cases = 0
        for state in (0, 1, 2, 3, 4, 0x7f, 0xff):
            for seed in (0, 0x45, 0xa5):
                stock = run(False, state, seed)
                candidate = run(True, state, seed)
                if stock != candidate:
                    raise RuntimeError(f'{state=} {seed=}: {stock} != {candidate}')
                cases += 1
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_DM_STACK_RESET_ORACLE',
               'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
               'payload_sha256': PINNED_SHA, 'cases': cases,
               'comparison_scope': 'Native timer call, callback event bytes, stack state reset and init call.',
               'limits': ['The callback receives two native stack bytes with no visible initialization; only event bytes 2 and 3 are compared.',
                          'Final RAM placement and controller behavior remain open.']}
    path = OUT / 'oracle-receipt.json'
    path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], cases, sha(path))

if __name__ == '__main__': main()
