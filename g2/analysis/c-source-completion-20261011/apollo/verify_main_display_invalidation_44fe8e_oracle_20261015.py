#!/usr/bin/env python3
"""Compare LVGL display invalidation counter and default-display path."""
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
SRC = G2 / 'components/audio/uart_thread_source_candidate/display_invalidation_control_44fe8e.c'
OUT = G2 / 'build/c-firmware/20261015/main-display-invalidation-44fe8e'
PAYLOAD_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
SHIM = '''#include <stdint.h>
__attribute__((noinline)) void *audio_uart_display_default_get(void) {return 0;}
__attribute__((noinline)) void audio_uart_lvgl_log(uint32_t a,const char*b,uint32_t c,const char*d,const char*e,...)
{(void)a;(void)b;(void)c;(void)d;(void)e;}
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
                        '-Wl,-Ttext=0x100000', '-Wl,-e,audio_uart_lv_display_invalidation_44fe8e',
                        str(SRC), str(shim), '-o', str(elf)], check=True)
        syms = {p[2]: int(p[0], 16) for line in subprocess.check_output(
            ['arm-none-eabi-nm', str(elf)], text=True).splitlines()
            if len(p := line.split()) == 3}
        with elf.open('rb') as f:
            segments = [(s['p_vaddr'], s.data()) for s in ELFFile(f).iter_segments()
                        if s['p_type'] == 'PT_LOAD']

        def run(compiled, direct, default, enabled, counter):
            cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            cpu.mem_map(0x400000, 0x400000)
            cpu.mem_write(0x438000, blob)
            cpu.mem_map(0x100000, 0x100000)
            for address, data in segments:
                cpu.mem_write(address, data)
            cpu.mem_map(0x20000000, 0x400000)
            display = 0x20011000
            cpu.mem_write(display, bytes(0x300))
            cpu.mem_write(display + 0x264, counter.to_bytes(4, 'little'))
            targets = {(syms['audio_uart_display_default_get'] if compiled else 0x44fa1a) & ~1: 'default',
                       (syms['audio_uart_lvgl_log'] if compiled else 0x44d25c) & ~1: 'log'}
            trace = []
            def hook(cpu, address, size, _):
                key = targets.get(address)
                if key is None:
                    return
                if key == 'log':
                    trace.append((key, cpu.reg_read(A.UC_ARM_REG_R0), cpu.reg_read(A.UC_ARM_REG_R2)))
                    result = 0
                else:
                    trace.append((key,))
                    result = display if default else 0
                cpu.reg_write(A.UC_ARM_REG_R0, result)
                cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
            cpu.hook_add(UC_HOOK_CODE, hook)
            cpu.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
            cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
            cpu.reg_write(A.UC_ARM_REG_R0, display if direct else 0)
            cpu.reg_write(A.UC_ARM_REG_R1, enabled)
            entry = syms['audio_uart_lv_display_invalidation_44fe8e'] if compiled else 0x44fe8e
            cpu.emu_start(entry | 1, 0x600000, count=1000)
            return trace, bytes(cpu.mem_read(display + 0x264, 4))

        cases = list(itertools.product((False, True), (False, True),
                                       (0, 1, 256, 257), (0, 5)))
        for case in cases:
            native, source = run(False, *case), run(True, *case)
            if native != source:
                raise AssertionError((case, native, source))
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_DISPLAY_INVALIDATION_ORACLE',
               'cases': len(cases), 'source_sha256': hashlib.sha256(SRC.read_bytes()).hexdigest(),
               'payload_sha256': PAYLOAD_SHA, 'hardware_proof': False}
    (OUT / 'oracle.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], len(cases))


if __name__ == '__main__':
    main()
