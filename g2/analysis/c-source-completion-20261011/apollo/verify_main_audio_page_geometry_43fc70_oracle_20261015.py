#!/usr/bin/env python3
"""Compare Apollo relative object geometry getters with stock Thumb."""
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
SRC = G2 / 'components/audio/uart_thread_source_candidate/display_audio_page_geometry_43fc70.c'
OUT = G2 / 'build/c-firmware/20261015/main-audio-page-geometry-43fc70'
PAYLOAD_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
FUNCTIONS = {'x': (0x43fc70, 'audio_uart_lv_obj_x_43fc70', 20,
                   0x44e486, 'audio_uart_lv_obj_x_44e486',
                   0x43efc6, 'audio_uart_lv_style_pad_left_43efc6'),
             'y': (0x43fce0, 'audio_uart_lv_obj_y_43fce0', 24,
                   0x44e498, 'audio_uart_lv_obj_y_44e498',
                   0x43f022, 'audio_uart_lv_style_pad_top_43f022')}
NAMES = {'audio_uart_lv_obj_parent_44dca2'} | {
    item for f in FUNCTIONS.values() for item in (f[4], f[6])}
SHIM = '#include <stdint.h>\n' + '\n'.join(
    f'__attribute__((noinline)) uint32_t {name}(uint32_t a,uint32_t b)'
    '{(void)a;(void)b;return 0;}' for name in sorted(NAMES)) + '\n'

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
                        '-Wl,-Ttext=0x100000', '-Wl,-e,audio_uart_lv_obj_x_43fc70',
                        str(SRC), str(shim), '-o', str(elf)], check=True)
        syms = {p[2]: int(p[0], 16) for line in subprocess.check_output(
            ['arm-none-eabi-nm', str(elf)], text=True).splitlines()
            if len(p := line.split()) == 3}
        with elf.open('rb') as f:
            segments = [(s['p_vaddr'], s.data()) for s in ELFFile(f).iter_segments()
                        if s['p_type'] == 'PT_LOAD']

        def run(compiled, axis, has_parent, own, parent_value, absolute, padding):
            cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            cpu.mem_map(0x400000, 0x400000)
            cpu.mem_write(0x438000, blob)
            cpu.mem_map(0x100000, 0x100000)
            for address, data in segments:
                cpu.mem_write(address, data)
            cpu.mem_map(0x20000000, 0x400000)
            obj, parent = 0x20011000, 0x20012000
            for address in (obj, parent):
                cpu.mem_write(address, bytes(64))
            entry, name, offset, absolute_entry, absolute_name, pad_entry, pad_name = FUNCTIONS[axis]
            put(cpu, obj + offset, own)
            put(cpu, parent + offset, parent_value)
            targets = {
                (syms['audio_uart_lv_obj_parent_44dca2'] if compiled else 0x44dca2) & ~1: 'parent',
                (syms[absolute_name] if compiled else absolute_entry) & ~1: 'absolute',
                (syms[pad_name] if compiled else pad_entry) & ~1: 'padding',
            }
            trace = []
            def hook(cpu, address, size, _):
                key = targets.get(address)
                if key is None:
                    return
                r0, r1 = cpu.reg_read(A.UC_ARM_REG_R0), cpu.reg_read(A.UC_ARM_REG_R1)
                trace.append((key, r0, r1 if key == 'padding' else 0))
                cpu.reg_write(A.UC_ARM_REG_R0, {'parent': parent if has_parent else 0,
                                                 'absolute': absolute,
                                                 'padding': padding}[key] & 0xffffffff)
                cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
            cpu.hook_add(UC_HOOK_CODE, hook)
            cpu.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
            cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
            cpu.reg_write(A.UC_ARM_REG_R0, obj)
            start = syms[name] if compiled else entry
            cpu.emu_start(start | 1, 0x600000, count=150)
            return cpu.reg_read(A.UC_ARM_REG_R0), trace

        cases = 0
        for args in itertools.product(FUNCTIONS, (False, True),
                                      (0, 100, 0xfffffffe), (0, 20),
                                      (0, 40), (0, 5)):
            stock, rebuilt = run(False, *args), run(True, *args)
            if stock != rebuilt:
                raise RuntimeError(f'geometry mismatch {args}: {stock} != {rebuilt}')
            cases += 1
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_AUDIO_PAGE_GEOMETRY_ORACLE',
               'cases': cases, 'source_sha256': hashlib.sha256(SRC.read_bytes()).hexdigest(),
               'payload_sha256': PAYLOAD_SHA,
               'limits': ['Parent, absolute coordinate and padding helpers are hooked.',
                          'Null-object fatal paths are outside this oracle.']}
    (OUT / 'oracle.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], cases)

if __name__ == '__main__': main()
