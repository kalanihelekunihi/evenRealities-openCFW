#!/usr/bin/env python3
"""Compare LVGL image pivot getter and percentage decoder to native Apollo."""
import hashlib
import itertools
import json
import subprocess
import tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import UC_ARCH_ARM, UC_MODE_THUMB, Uc
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
SRC = G2 / 'components/audio/uart_thread_source_candidate/display_image_pivot_498b82.c'
OUT = G2 / 'build/c-firmware/20261015/main-image-pivot-498b82'
PAYLOAD_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
SHIM = '''#include <stdint.h>
__attribute__((noinline)) void audio_uart_lvgl_log(uint32_t a,const char*b,uint32_t c,const char*d,const char*e,...)
{(void)a;(void)b;(void)c;(void)d;(void)e;}
'''


def put(cpu, address, value):
    cpu.mem_write(address, (value & 0xffffffff).to_bytes(4, 'little'))


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
                        '-Wl,-Ttext=0x100000', '-Wl,-e,audio_uart_lv_image_get_pivot_498b82',
                        str(SRC), str(shim), '-o', str(elf)], check=True)
        syms = {p[2]: int(p[0], 16) for line in subprocess.check_output(
            ['arm-none-eabi-nm', str(elf)], text=True).splitlines()
            if len(p := line.split()) == 3}
        with elf.open('rb') as f:
            segments = [(s['p_vaddr'], s.data()) for s in ELFFile(f).iter_segments()
                        if s['p_type'] == 'PT_LOAD']

        def run(compiled, pivot, dimension, getter):
            cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            cpu.mem_map(0x400000, 0x400000)
            cpu.mem_write(0x438000, blob)
            cpu.mem_map(0x100000, 0x100000)
            for address, data in segments:
                cpu.mem_write(address, data)
            cpu.mem_map(0x20000000, 0x400000)
            image, output = 0x20011000, 0x20012000
            cpu.mem_write(image, bytes(0x100))
            cpu.mem_write(output, bytes(8))
            for offset, value in ((0x3c, dimension), (0x40, dimension + 1),
                                  (0x50, pivot), (0x54, pivot)):
                put(cpu, image + offset, value)
            cpu.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
            cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
            if getter:
                cpu.reg_write(A.UC_ARM_REG_R0, image)
                cpu.reg_write(A.UC_ARM_REG_R1, output)
                entry = syms['audio_uart_lv_image_get_pivot_498b82'] if compiled else 0x498b82
            else:
                cpu.reg_write(A.UC_ARM_REG_R0, pivot)
                cpu.reg_write(A.UC_ARM_REG_R1, dimension)
                entry = syms['audio_uart_lv_image_coord_px_451600'] if compiled else 0x451600
            cpu.emu_start(entry | 1, 0x600000, count=1000)
            return bytes(cpu.mem_read(output, 8)) if getter else cpu.reg_read(A.UC_ARM_REG_R0)

        pivots = (0, 1, 20, 0xffffffff, 0x20000000, 0x20000001,
                  0x20000064, 0x2fffffff, 0x30000000, 0xa0000000,
                  0x1fffffff, 0x60000001)
        dimensions = (0, 1, 37, 100, 65535)
        cases = list(itertools.product(pivots, dimensions, (False, True)))
        for case in cases:
            native, source = run(False, *case), run(True, *case)
            if native != source:
                raise AssertionError((case, native, source))
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_IMAGE_PIVOT_ORACLE',
               'cases': len(cases), 'source_sha256': hashlib.sha256(SRC.read_bytes()).hexdigest(),
               'payload_sha256': PAYLOAD_SHA, 'hardware_proof': False,
               'scope': 'coordinate encoding edges and two-axis image pivot storage'}
    (OUT / 'oracle.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], len(cases))


if __name__ == '__main__': main()
