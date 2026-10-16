#!/usr/bin/env python3
"""Compare image rotation, pivot, and scale transformation sequences."""
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
SRC = G2 / 'components/audio/uart_thread_source_candidate/display_image_transform_setters_4988dc.c'
OUT = G2 / 'build/c-firmware/20261015/main-image-transform-setters-4988dc'
PAYLOAD_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
CALLS = {
    'layout': (0x43f66c, 'audio_uart_page_43f66c'),
    'width': (0x43fd9e, 'audio_uart_lv_obj_width_43fd9e'),
    'height': (0x43fdda, 'audio_uart_lv_obj_height_43fdda'),
    'pivot': (0x498b82, 'audio_uart_lv_image_get_pivot_498b82'),
    'transform': (0x488cda, 'audio_uart_ambiq_transform_area_488cda'),
    'invalidate': (0x4405d4, 'audio_uart_lv_invalidate_area_4405d4'),
    'display': (0x44dc0a, 'audio_uart_lv_display_for_object'),
    'enable': (0x44fe8e, 'audio_uart_lv_display_invalidation_44fe8e'),
    'refresh': (0x452d42, 'audio_uart_lv_refresh_draw_452d42'),
    'log': (0x44d25c, 'audio_uart_lvgl_log'),
}
SHIM = '#include <stdint.h>\n' + '\n'.join(
    f'__attribute__((noinline)) uint32_t {name}(void*a,void*b,void*c,void*d)'
    '{(void)a;(void)b;(void)c;(void)d;return 0;}'
    for key, (_, name) in CALLS.items() if key != 'log') + \
    '\n__attribute__((noinline)) void audio_uart_lvgl_log(uint32_t a,const char*b,uint32_t c,const char*d,const char*e,...){(void)a;(void)b;(void)c;(void)d;(void)e;}\n'
WRAPPERS = ((0x4988dc, 'audio_uart_lv_image_set_rotation_4988dc'),
            (0x498a14, 'audio_uart_lv_image_set_pivot_498a14'),
            (0x4991e0, 'audio_uart_lv_image_scale_update_4991e0'))


def put(cpu, address, value):
    cpu.mem_write(address, (value & 0xffffffff).to_bytes(4, 'little'))


def get(cpu, address):
    return int.from_bytes(cpu.mem_read(address, 4), 'little')


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
                        '-Wl,-Ttext=0x100000', '-Wl,-e,audio_uart_lv_image_set_rotation_4988dc',
                        str(SRC), str(shim), '-o', str(elf)], check=True)
        syms = {p[2]: int(p[0], 16) for line in subprocess.check_output(
            ['arm-none-eabi-nm', str(elf)], text=True).splitlines()
            if len(p := line.split()) == 3}
        with elf.open('rb') as f:
            segments = [(s['p_vaddr'], s.data()) for s in ELFFile(f).iter_segments()
                        if s['p_type'] == 'PT_LOAD']

        def run(compiled, entry_index, align, current, requested):
            cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            cpu.mem_map(0x400000, 0x400000)
            cpu.mem_write(0x438000, blob)
            cpu.mem_map(0x100000, 0x100000)
            for address, data in segments:
                cpu.mem_write(address, data)
            cpu.mem_map(0x20000000, 0x400000)
            image = 0x20011000
            cpu.mem_write(image, bytes(0x100))
            for offset, value in ((20, 7), (24, 11), (0x3c, 13), (0x40, 17),
                                  (0x44, current if entry_index == 0 else 50),
                                  (0x48, current if entry_index == 2 else 256),
                                  (0x4c, 256), (0x50, current if entry_index == 1 else 2),
                                  (0x54, 3), (0x58, align << 8)):
                put(cpu, image + offset, value)
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
                r3 = cpu.reg_read(A.UC_ARM_REG_R3)
                result = 0
                if key == 'pivot':
                    put(cpu, r1, get(cpu, image + 0x50))
                    put(cpu, r1 + 4, get(cpu, image + 0x54))
                    trace.append((key, r0))
                elif key == 'transform':
                    sp = cpu.reg_read(A.UC_ARM_REG_SP)
                    sx, sy, pivot_ptr = (get(cpu, sp + offset) for offset in (0, 4, 8))
                    trace.append((key, r1, r2, r3, sx, sy,
                                  get(cpu, pivot_ptr), get(cpu, pivot_ptr + 4)))
                    for offset, value in enumerate((-2, -3, 19, 23)):
                        put(cpu, r0 + 4 * offset, value)
                elif key == 'invalidate':
                    trace.append((key, r0, tuple(get(cpu, r1 + 4 * i) for i in range(4))))
                elif key == 'enable':
                    trace.append((key, r0, r1))
                else:
                    trace.append((key, r0))
                result = {'width': 13, 'height': 17, 'display': 0x20017000}.get(key, 0)
                cpu.reg_write(A.UC_ARM_REG_R0, result)
                cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))

            cpu.hook_add(UC_HOOK_CODE, hook)
            cpu.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
            cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
            cpu.reg_write(A.UC_ARM_REG_R0, image)
            cpu.reg_write(A.UC_ARM_REG_R1, requested & 0xffffffff)
            cpu.reg_write(A.UC_ARM_REG_R2, (requested + 1) & 0xffffffff)
            address, name = WRAPPERS[entry_index]
            cpu.emu_start((syms[name] if compiled else address) | 1,
                          0x600000, count=10000)
            return trace, bytes(cpu.mem_read(image + 0x44, 0x18))

        cases = list(itertools.product(range(3), (9, 11, 12),
                                       (0, 30), (0, 40)))
        for case in cases:
            native, source = run(False, *case), run(True, *case)
            if native != source:
                raise AssertionError((case, native, source))
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_IMAGE_TRANSFORM_SETTERS_ORACLE',
               'cases': len(cases), 'source_sha256': hashlib.sha256(SRC.read_bytes()).hexdigest(),
               'payload_sha256': PAYLOAD_SHA, 'hardware_proof': False,
               'scope': 'rotation/pivot/scale calls, areas and state with controlled transform children'}
    (OUT / 'oracle.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], len(cases))


if __name__ == '__main__':
    main()
