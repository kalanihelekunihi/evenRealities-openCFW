#!/usr/bin/env python3
"""Compare Apollo audio route helper with the pinned stock Thumb body."""
import hashlib
import itertools
import json
import subprocess
import tempfile
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import UC_ARCH_ARM, UC_HOOK_CODE, UC_MODE_THUMB, Uc
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
SRC = G2 / 'components/audio/uart_thread_source_candidate/display_audio_route_45f876.c'
OUT = G2 / 'build/c-firmware/20261015/main-audio-route-45f876'
PAYLOAD_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
CALLS = {'find': (0x45f840, 'audio_uart_display_audio_find_45f840'),
         'queue': (0x45f58c, 'audio_uart_display_audio_queue_45f58c')}
SHIM = '''#include <stdint.h>
__attribute__((noinline)) void *audio_uart_display_audio_find_45f840(void *s,uint32_t id)
{(void)s;(void)id;return 0;}
__attribute__((noinline)) void audio_uart_display_audio_queue_45f58c(void *s,uint32_t id)
{(void)s;(void)id;}
'''

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    blob = (G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PAYLOAD_SHA:
        raise RuntimeError('Apollo payload changed')
    with tempfile.TemporaryDirectory() as td:
        shim, elf = Path(td) / 'shim.c', Path(td) / 'oracle.elf'
        shim.write_text(SHIM)
        subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                        '-std=c11', '-ffreestanding', '-fno-builtin', '-O2', '-nostdlib',
                        '-Wl,-Ttext=0x100000', '-Wl,-e,audio_uart_display_audio_route_45f876',
                        str(SRC), str(shim), '-o', str(elf)], check=True)
        syms = {p[2]: int(p[0], 16) for line in subprocess.check_output(
            ['arm-none-eabi-nm', str(elf)], text=True).splitlines()
            if len(p := line.split()) == 3}
        with elf.open('rb') as f:
            segments = [(s['p_vaddr'], s.data()) for s in ELFFile(f).iter_segments()
                        if s['p_type'] == 'PT_LOAD']

        def run(compiled, state_valid, ident, found):
            cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            cpu.mem_map(0x400000, 0x400000)
            cpu.mem_write(0x438000, blob)
            cpu.mem_map(0x100000, 0x100000)
            for address, data in segments:
                cpu.mem_write(address, data)
            cpu.mem_map(0x20000000, 0x400000)
            state = 0x20012000 if state_valid else 0
            targets = {(syms[name] if compiled else address) & ~1: key
                       for key, (address, name) in CALLS.items()}
            trace = []
            def hook(cpu, address, size, _):
                key = targets.get(address)
                if key is None:
                    return
                trace.append((key, cpu.reg_read(A.UC_ARM_REG_R0),
                              cpu.reg_read(A.UC_ARM_REG_R1)))
                cpu.reg_write(A.UC_ARM_REG_R0,
                              0x20013000 if key == 'find' and found else 0)
                cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
            cpu.hook_add(UC_HOOK_CODE, hook)
            cpu.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
            cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
            cpu.reg_write(A.UC_ARM_REG_R0, state)
            cpu.reg_write(A.UC_ARM_REG_R1, ident)
            start = syms['audio_uart_display_audio_route_45f876'] if compiled else 0x45f876
            cpu.emu_start(start | 1, 0x600000, count=100)
            return trace, cpu.reg_read(A.UC_ARM_REG_R0)

        cases = 0
        for args in itertools.product((False, True), (0, 1, 7), (False, True)):
            stock, rebuilt = run(False, *args), run(True, *args)
            if stock != rebuilt:
                raise RuntimeError(f'audio route mismatch {args}: {stock} != {rebuilt}')
            cases += 1
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_AUDIO_ROUTE_ORACLE',
               'cases': cases, 'source_sha256': hashlib.sha256(SRC.read_bytes()).hexdigest(),
               'payload_sha256': PAYLOAD_SHA,
               'limits': ['Find and queue children are cut at call boundaries.',
                          '12 controlled state/id/find combinations; live queue effects remain open.']}
    (OUT / 'oracle.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], cases)

if __name__ == '__main__': main()
