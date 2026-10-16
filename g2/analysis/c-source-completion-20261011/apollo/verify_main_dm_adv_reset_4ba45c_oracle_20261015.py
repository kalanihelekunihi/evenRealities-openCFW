#!/usr/bin/env python3
"""Compare pinned Cordio legacy advertising reset routing to C."""
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
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/display_ble_dm_adv_reset_4ba45c.c'
UPSTREAM = ROOT / 'third-party/upstream/cordio/ble-host/sources/stack/dm/dm_adv_leg.c'
PAYLOAD = G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT = G2 / 'build/c-firmware/20261015/main-dm-adv-reset-4ba45c'
PINNED_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
SHIM = '''#include <stdint.h>
uint8_t audio_ble_dm_adv_control[64];
uint8_t audio_ble_dm_handler_state[24];
__attribute__((noinline)) void WsfTimerStop(void *p){(void)p;}
__attribute__((noinline)) void audio_ble_dm_adv_lower(void){}
'''

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PINNED_SHA or \
            'void dmAdvReset(void)' not in UPSTREAM.read_text():
        raise RuntimeError('Apollo payload or Cordio source changed')
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        shim, elf = Path(td) / 'shim.c', Path(td) / 'oracle.elf'
        shim.write_text(SHIM)
        subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4',
                        '-mthumb', '-std=c11', '-ffreestanding', '-fno-builtin',
                        '-O2', '-nostdlib', '-Wl,-Ttext=0x100000',
                        '-Wl,-e,audio_ble_dm_adv_reset_4ba45c',
                        str(SOURCE), str(shim), '-o', str(elf)], check=True)
        with elf.open('rb') as f:
            image = ELFFile(f)
            segments = [(s['p_vaddr'], s.data()) for s in image.iter_segments()
                        if s['p_type'] == 'PT_LOAD']
            symbols = {s.name: s['st_value'] for s in
                       image.get_section_by_name('.symtab').iter_symbols()}
        def run(compiled, state, adv_type, seed):
            cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            cpu.mem_map(0x400000, 0x400000)
            cpu.mem_write(0x438000, blob)
            cpu.mem_map(0x100000, 0x100000)
            for address, data in segments:
                cpu.mem_write(address, data)
            cpu.mem_map(0x20000000, 0x100000)
            adv = symbols['audio_ble_dm_adv_control'] if compiled else 0x20073394
            dm = symbols['audio_ble_dm_handler_state'] if compiled else 0x20073b78
            data = bytearray((seed + i * 7) & 0xff for i in range(64))
            data[0x18] = adv_type
            data[0x1d] = state
            cpu.mem_write(adv, bytes(data))
            cpu.mem_write(dm + 8, (0x20007001).to_bytes(4, 'little'))
            timer = (symbols['WsfTimerStop'] if compiled else 0x52a4d2) & ~1
            lower = (symbols['audio_ble_dm_adv_lower'] if compiled else 0x4b30e4) & ~1
            calls = []
            def hook(uc, addr, size, user):
                if addr == timer:
                    calls.append(('timer', uc.reg_read(A.UC_ARM_REG_R0) - adv))
                    uc.reg_write(A.UC_ARM_REG_PC, uc.reg_read(A.UC_ARM_REG_LR))
                elif addr == lower:
                    calls.append(('lower',))
                    uc.reg_write(A.UC_ARM_REG_PC, uc.reg_read(A.UC_ARM_REG_LR))
                elif addr == 0x20007000:
                    ptr = uc.reg_read(A.UC_ARM_REG_R0)
                    calls.append(('callback', bytes(uc.mem_read(ptr+2, 2)).hex()))
                    uc.reg_write(A.UC_ARM_REG_PC, uc.reg_read(A.UC_ARM_REG_LR))
            cpu.hook_add(UC_HOOK_CODE, hook)
            cpu.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
            cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
            entry = symbols['audio_ble_dm_adv_reset_4ba45c'] if compiled else 0x4ba45c
            cpu.emu_start(entry | 1, 0x600000, count=500)
            return calls
        cases = 0
        for state in (0, 1, 2, 5):
            for adv_type in (0, 1, 2):
                for seed in (0, 0xa5):
                    stock = run(False, state, adv_type, seed)
                    candidate = run(True, state, adv_type, seed)
                    if stock != candidate:
                        raise RuntimeError(f'{state=} {adv_type=} {seed=}: {stock} != {candidate}')
                    cases += 1
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_DM_ADV_RESET_ORACLE',
               'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
               'upstream_source': str(UPSTREAM.relative_to(ROOT)), 'upstream_sha256': sha(UPSTREAM),
               'payload_sha256': PINNED_SHA, 'cases': cases,
               'comparison_scope': 'Legacy advertising reset state/type condition, timer stop, initialized callback bytes and lower reset call.',
               'limits': ['Timer and lower-reset child effects, uninitialized callback param, final placement and hardware behavior remain open.']}
    path = OUT / 'oracle-receipt.json'
    path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], cases, sha(path))

if __name__ == '__main__': main()
