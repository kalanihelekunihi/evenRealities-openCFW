#!/usr/bin/env python3
"""Compare three LVGL image text style wrappers with native Apollo."""
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
SRC = G2 / 'components/audio/uart_thread_source_candidate/display_image_text_style_498640.c'
OUT = G2 / 'build/c-firmware/20261015/main-image-text-style-498640'
PAYLOAD_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
WRAPPERS = ((0x498640, 'audio_uart_lv_image_text_font_498640', 0x5a),
            (0x49864a, 'audio_uart_lv_image_letter_space_49864a', 0x5b),
            (0x498654, 'audio_uart_lv_image_line_space_498654', 0x5c))
SHIM = '''#include <stdint.h>
__attribute__((noinline)) uint32_t audio_uart_lv_style_property_44bdea(void*a,uint32_t b,uint32_t c)
{(void)a;(void)b;(void)c;return 0;}
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
                        '-Wl,-Ttext=0x100000', '-Wl,-e,audio_uart_lv_image_text_font_498640',
                        str(SRC), str(shim), '-o', str(elf)], check=True)
        syms = {p[2]: int(p[0], 16) for line in subprocess.check_output(
            ['arm-none-eabi-nm', str(elf)], text=True).splitlines()
            if len(p := line.split()) == 3}
        with elf.open('rb') as f:
            segments = [(s['p_vaddr'], s.data()) for s in ELFFile(f).iter_segments()
                        if s['p_type'] == 'PT_LOAD']
        count = 0
        for address, name, property_id in WRAPPERS:
            for part in (0, 1, 3, 0xffffffff):
                for result in (0, 0x12345678, 0xffffffff):
                    outcomes = []
                    for compiled in (False, True):
                        cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
                        cpu.mem_map(0x400000, 0x400000)
                        cpu.mem_write(0x438000, blob)
                        cpu.mem_map(0x100000, 0x100000)
                        for start, data in segments:
                            cpu.mem_write(start, data)
                        cpu.mem_map(0x20000000, 0x400000)
                        target = syms['audio_uart_lv_style_property_44bdea'] & ~1 if compiled else 0x44bdea
                        trace = []
                        def hook(cpu, pc, size, _):
                            if pc == target:
                                trace.append(tuple(cpu.reg_read(reg) for reg in
                                                   (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1, A.UC_ARM_REG_R2)))
                                cpu.reg_write(A.UC_ARM_REG_R0, result)
                                cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
                        cpu.hook_add(UC_HOOK_CODE, hook)
                        cpu.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
                        cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
                        cpu.reg_write(A.UC_ARM_REG_R0, 0x20011000)
                        cpu.reg_write(A.UC_ARM_REG_R1, part)
                        cpu.emu_start((syms[name] if compiled else address) | 1,
                                      0x600000, count=100)
                        outcomes.append((cpu.reg_read(A.UC_ARM_REG_R0), trace))
                    if outcomes[0] != outcomes[1] or outcomes[0][1] != [(0x20011000, part, property_id)]:
                        raise AssertionError((name, part, result, outcomes))
                    count += 1
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_IMAGE_TEXT_STYLE_ORACLE',
               'cases': count, 'source_sha256': hashlib.sha256(SRC.read_bytes()).hexdigest(),
               'payload_sha256': PAYLOAD_SHA, 'hardware_proof': False}
    (OUT / 'oracle.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], count)


if __name__ == '__main__':
    main()
