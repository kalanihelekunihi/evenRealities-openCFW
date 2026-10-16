#!/usr/bin/env python3
"""Compare bounded LVGL image source setter against official Apollo bytes."""
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
SRC = G2 / 'components/audio/uart_thread_source_candidate/display_image_set_src_498680.c'
OUT = G2 / 'build/c-firmware/20261015/main-image-set-src-498680'
PAYLOAD_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
CALLS = {
    'invalidate': (0x440656, 'audio_uart_display_size_changed'),
    'type': (0x488cb8, 'audio_uart_lv_image_source_type_488cb8'),
    'info': (0x488f6a, 'audio_uart_lv_image_header_488f6a'),
    'snprintf': (0x483fd0, 'audio_uart_lv_snprintf_483fd0'),
    'free': (0x44f758, 'audio_uart_lv_heap_free'),
    'duplicate': (0x4547c6, 'audio_uart_font_path_duplicate'),
    'font': (0x498640, 'audio_uart_lv_image_text_font_498640'),
    'letter': (0x49864a, 'audio_uart_lv_image_letter_space_49864a'),
    'line': (0x498654, 'audio_uart_lv_image_line_space_498654'),
    'size': (0x489546, 'audio_uart_page_event_calculate_489546'),
    'relayout': (0x43ffa0, 'audio_uart_page_relayout_43ffa0'),
    'align': (0x4992cc, 'audio_uart_lv_image_update_align_4992cc'),
    'refresh_draw': (0x452d42, 'audio_uart_lv_refresh_draw_452d42'),
    'log': (0x44d25c, 'audio_uart_lvgl_log'),
}
SHIM = '#include <stdint.h>\n' + '\n'.join(
    f'__attribute__((noinline)) uint32_t {name}(void*a,void*b,void*c,void*d)'
    '{(void)a;(void)b;(void)c;(void)d;return 0;}'
    for key, (_, name) in CALLS.items() if key != 'log') + \
    '\n__attribute__((noinline)) void audio_uart_lvgl_log(uint32_t a,const char*b,uint32_t c,const char*d,const char*e,...){(void)a;(void)b;(void)c;(void)d;(void)e;}\n'


def put(cpu, address, value):
    cpu.mem_write(address, (value & 0xffffffff).to_bytes(4, 'little'))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    blob = (G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
    digest = hashlib.sha256(blob).hexdigest()
    if digest != PAYLOAD_SHA:
        raise RuntimeError('Apollo payload changed')
    with tempfile.TemporaryDirectory() as td:
        shim, elf = Path(td) / 'shim.c', Path(td) / 'oracle.elf'
        shim.write_text(SHIM)
        subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                        '-std=c11', '-ffreestanding', '-fno-builtin', '-O2', '-nostdlib',
                        '-Wl,-Ttext=0x100000', '-Wl,-e,audio_uart_page_498680',
                        str(SRC), str(shim), '-o', str(elf)], check=True)
        syms = {p[2]: int(p[0], 16) for line in subprocess.check_output(
            ['arm-none-eabi-nm', str(elf)], text=True).splitlines()
            if len(p := line.split()) == 3}
        with elf.open('rb') as f:
            segments = [(s['p_vaddr'], s.data()) for s in ELFFile(f).iter_segments()
                        if s['p_type'] == 'PT_LOAD']

        def run(compiled, source_type, old_type, allocated, same, rotation, header_ok, buffer_valid):
            cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            cpu.mem_map(0x400000, 0x400000)
            cpu.mem_write(0x438000, blob)
            cpu.mem_map(0x100000, 0x100000)
            for address, data in segments:
                cpu.mem_write(address, data)
            cpu.mem_map(0x20000000, 0x400000)
            image, source, duplicate, old = (0x20011000, 0x20013000,
                                             0x20014000, 0x20015000)
            cpu.mem_write(image, bytes(0x100))
            cpu.mem_write(source, b'abc\0' + bytes(0x7c))
            cpu.mem_write(duplicate, bytes(0x80))
            put(cpu, image + 0x2c, source if same else old)
            put(cpu, image + 0x44, rotation)
            put(cpu, image + 0x48, 256)
            put(cpu, image + 0x4c, 256)
            put(cpu, image + 0x58, 0xa5010000 | old_type)
            put(cpu, source + 20, source if buffer_valid else 0)
            put(cpu, source + 24, source)
            targets = {(syms[name] if compiled else addr) & ~1: key
                       for key, (addr, name) in CALLS.items()}
            trace = []

            def string(cpu, address):
                return bytes(cpu.mem_read(address, 256)).split(b'\0', 1)[0].decode('ascii')

            def hook(cpu, address, size, _):
                key = targets.get(address)
                if key is None:
                    return
                r0 = cpu.reg_read(A.UC_ARM_REG_R0)
                r1 = cpu.reg_read(A.UC_ARM_REG_R1)
                r2 = cpu.reg_read(A.UC_ARM_REG_R2)
                r3 = cpu.reg_read(A.UC_ARM_REG_R3)
                result = 0
                if key == 'type':
                    trace.append((key, r0))
                    result = source_type
                elif key == 'info':
                    trace.append((key, r0))
                    put(cpu, r1, (0x00100000 if allocated else 0) | 0x1300)
                    put(cpu, r1 + 4, (21 << 16) | 13)
                    result = 1 if header_ok else 0
                elif key == 'snprintf':
                    trace.append((key, r1, string(cpu, r2), r3))
                    cpu.mem_write(r0, b'0x20013000\0')
                    result = 10
                elif key == 'duplicate':
                    trace.append((key, r0))
                    result = duplicate
                elif key in ('font', 'letter', 'line'):
                    trace.append((key, r0, r1))
                    result = {'font': 0x20018000, 'letter': 2, 'line': 3}[key]
                elif key == 'size':
                    trace.append((key, r1, r2, r3,
                                  int.from_bytes(cpu.mem_read(cpu.reg_read(A.UC_ARM_REG_SP), 4), 'little')))
                    put(cpu, r0, 31)
                    put(cpu, r0 + 4, 7)
                elif key == 'free':
                    trace.append((key, r0))
                elif key == 'log':
                    sp = cpu.reg_read(A.UC_ARM_REG_SP)
                    fmt = string(cpu, int.from_bytes(cpu.mem_read(sp, 4), 'little'))
                    extra = ()
                    if fmt == 'failed to get image info: %s':
                        extra = (string(cpu, int.from_bytes(cpu.mem_read(sp + 4, 4), 'little')),)
                    elif fmt == 'Invalid draw buffer, unaligned_data: %p, handlers: %p':
                        extra = tuple(int.from_bytes(cpu.mem_read(sp + i, 4), 'little') for i in (4, 8))
                    trace.append((key, r0, r2, string(cpu, r1), string(cpu, r3), fmt, *extra))
                else:
                    trace.append((key, r0))
                cpu.reg_write(A.UC_ARM_REG_R0, result)
                cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))

            cpu.hook_add(UC_HOOK_CODE, hook)
            cpu.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
            cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
            cpu.reg_write(A.UC_ARM_REG_R0, image)
            cpu.reg_write(A.UC_ARM_REG_R1, source)
            entry = syms['audio_uart_page_498680'] if compiled else 0x498680
            cpu.emu_start(entry | 1, 0x600000, count=50000)
            return trace, bytes(cpu.mem_read(image + 0x2c, 0x30))

        cases = list(itertools.product((0, 1, 2, 3), (0, 1, 2, 3),
                                       (False, True), (False, True), (0, 1),
                                       (False, True), (False, True)))
        for case in cases:
            native, source = run(False, *case), run(True, *case)
            if native != source:
                raise AssertionError((case, native, source))
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_IMAGE_SET_SRC_ORACLE',
               'source_sha256': hashlib.sha256(SRC.read_bytes()).hexdigest(),
               'official_payload_sha256': digest, 'cases': len(cases),
               'scope': 'source/old type, allocated header, pointer equality, rotation, header failure and invalid buffers; controlled children',
               'hardware_proof': False}
    (OUT / 'oracle.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], len(cases))


if __name__ == '__main__':
    main()
