#!/usr/bin/env python3
"""Compare LVGL image stretch/tile alignment against native Apollo."""
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
SRC = G2 / 'components/audio/uart_thread_source_candidate/display_image_update_align_4992cc.c'
OUT = G2 / 'build/c-firmware/20261015/main-image-update-align-4992cc'
PAYLOAD_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
CALLS = {
    'rotation': (0x4988dc, 'audio_uart_lv_image_set_rotation_4988dc'),
    'pivot': (0x498a14, 'audio_uart_lv_image_set_pivot_498a14'),
    'layout': (0x43f66c, 'audio_uart_page_43f66c'),
    'width': (0x43fd9e, 'audio_uart_lv_obj_width_43fd9e'),
    'height': (0x43fdda, 'audio_uart_lv_obj_height_43fdda'),
    'scale': (0x4991e0, 'audio_uart_lv_image_scale_update_4991e0'),
}
SHIM = '#include <stdint.h>\n' + '\n'.join(
    f'__attribute__((noinline)) uint32_t {name}(void*a,uint32_t b,uint32_t c)'
    '{(void)a;(void)b;(void)c;return 0;}' for _, name in CALLS.values()) + '\n'


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
                        '-Wl,-Ttext=0x100000', '-Wl,-e,audio_uart_lv_image_update_align_4992cc',
                        str(SRC), str(shim), '-o', str(elf)], check=True)
        syms = {p[2]: int(p[0], 16) for line in subprocess.check_output(
            ['arm-none-eabi-nm', str(elf)], text=True).splitlines()
            if len(p := line.split()) == 3}
        with elf.open('rb') as f:
            segments = [(s['p_vaddr'], s.data()) for s in ELFFile(f).iter_segments()
                        if s['p_type'] == 'PT_LOAD']

        def run(compiled, align, width, height, object_width, object_height):
            cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            cpu.mem_map(0x400000, 0x400000)
            cpu.mem_write(0x438000, blob)
            cpu.mem_map(0x100000, 0x100000)
            for address, data in segments:
                cpu.mem_write(address, data)
            cpu.mem_map(0x20000000, 0x400000)
            image = 0x20011000
            cpu.mem_write(image, bytes(0x100))
            for offset, value in ((0x3c, width), (0x40, height), (0x58, align << 8)):
                cpu.mem_write(image + offset, (value & 0xffffffff).to_bytes(4, 'little'))
            targets = {(syms[name] if compiled else address) & ~1: key
                       for key, (address, name) in CALLS.items()}
            trace = []

            def hook(cpu, address, size, _):
                key = targets.get(address)
                if key is None:
                    return
                r0 = cpu.reg_read(A.UC_ARM_REG_R0)
                r1 = cpu.reg_read(A.UC_ARM_REG_R1)
                r2 = cpu.reg_read(A.UC_ARM_REG_R2)
                trace.append((key, r0, *( (r1, r2) if key in ('pivot', 'scale') else
                                          (r1,) if key == 'rotation' else () )))
                result = {'width': object_width, 'height': object_height}.get(key, 0)
                cpu.reg_write(A.UC_ARM_REG_R0, result & 0xffffffff)
                cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))

            cpu.hook_add(UC_HOOK_CODE, hook)
            cpu.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
            cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
            cpu.reg_write(A.UC_ARM_REG_R0, image)
            entry = syms['audio_uart_lv_image_update_align_4992cc'] if compiled else 0x4992cc
            cpu.emu_start(entry | 1, 0x600000, count=10000)
            return trace, bytes(cpu.mem_read(image, 0x60))

        cases = list(itertools.product((0, 10, 11, 12, 13), (0, 1, 13),
                                       (0, 1, 21), (0, 52), (0, 42)))
        for case in cases:
            native, source = run(False, *case), run(True, *case)
            if native != source:
                raise AssertionError((case, native, source))
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_IMAGE_UPDATE_ALIGN_ORACLE',
               'cases': len(cases), 'source_sha256': hashlib.sha256(SRC.read_bytes()).hexdigest(),
               'payload_sha256': PAYLOAD_SHA, 'hardware_proof': False,
               'scope': 'stretch/tile/default branch calls and signed scale outputs; children stubbed'}
    (OUT / 'oracle.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], len(cases))


if __name__ == '__main__':
    main()
