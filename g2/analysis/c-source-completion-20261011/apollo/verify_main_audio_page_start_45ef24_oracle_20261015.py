#!/usr/bin/env python3
"""Compare Apollo audio animation start call and descriptor contracts."""
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
SRC = G2 / 'components/audio/uart_thread_source_candidate/display_audio_page_start_45ef24.c'
OUT = G2 / 'build/c-firmware/20261015/main-audio-page-start-45ef24'
PAYLOAD_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
CALLS = {
    'init': (0x4503d6, 'audio_uart_lv_anim_init_4503d6'),
    'values': (0x4506ce, 'audio_uart_lv_anim_values_4506ce'),
    'start': (0x450408, 'audio_uart_lv_anim_start_450408'),
    'owner': (0x45fcd2, 'audio_uart_display_audio_find_owner_45fcd2'),
    'prepare': (0x45bbb6, 'audio_uart_display_audio_prepare_45bbb6'),
    'parent': (0x44dca2, 'audio_uart_lv_obj_parent_44dca2'),
    'width': (0x43fd9e, 'audio_uart_lv_obj_width_43fd9e'),
    'height': (0x43fdda, 'audio_uart_lv_obj_height_43fdda'),
    'x': (0x43fc70, 'audio_uart_lv_obj_x_43fc70'),
    'y': (0x43fce0, 'audio_uart_lv_obj_y_43fce0'),
    'set_x': (0x43f0e0, 'audio_uart_page_43f0e0'),
    'set_y': (0x43f142, 'audio_uart_page_43f142'),
    'reset': (0x441488, 'audio_uart_display_audio_reset_441488'),
}
CALLBACKS = {
    'x_a': (0x45ecaf, 'audio_uart_display_anim_x_a_45ecaf'),
    'y_a': (0x45ecb7, 'audio_uart_display_anim_y_a_45ecb7'),
    'alpha': (0x45ecbf, 'audio_uart_display_anim_alpha_45ecbf'),
    'finish_b': (0x45ed4f, 'audio_uart_display_anim_finish_b_45ed4f'),
    'finish_a': (0x45ee35, 'audio_uart_display_anim_finish_a_45ee35'),
    'finish_c': (0x45eccb, 'audio_uart_display_anim_finish_c_45eccb'),
    'finish_d': (0x45ed91, 'audio_uart_display_anim_finish_d_45ed91'),
}
SHIM = '#include <stdint.h>\n' + '\n'.join(
    f'__attribute__((noinline)) uint32_t {name}(uint32_t a,uint32_t b,uint32_t c)'
    '{(void)a;(void)b;(void)c;return 0;}' for _, name in CALLS.values()) + '\n' + '\n'.join(
    f'__attribute__((noinline)) void {name}(void){{}}' for _, name in CALLBACKS.values()) + '\n'

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
                        '-Wl,-Ttext=0x100000', '-Wl,-e,audio_uart_display_audio_start_45ef24',
                        str(SRC), str(shim), '-o', str(elf)], check=True)
        syms = {p[2]: int(p[0], 16) for line in subprocess.check_output(
            ['arm-none-eabi-nm', str(elf)], text=True).splitlines()
            if len(p := line.split()) == 3}
        with elf.open('rb') as f:
            segments = [(s['p_vaddr'], s.data()) for s in ELFFile(f).iter_segments()
                        if s['p_type'] == 'PT_LOAD']

        def run(compiled, alpha, direction, forward, mode, percent, owner_valid):
            cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            cpu.mem_map(0x400000, 0x400000)
            cpu.mem_write(0x438000, blob)
            cpu.mem_map(0x100000, 0x100000)
            for address, data in segments:
                cpu.mem_write(address, data)
            cpu.mem_map(0x20000000, 0x400000)
            entry, page, parent, owner = (0x20011000, 0x20012000, 0x20013000,
                                          0x20014000)
            for address in (entry, page, parent, owner):
                cpu.mem_write(address, bytes(256))
            put(cpu, entry + 4, page)
            put(cpu, entry + 12, 0x1234)
            put(cpu, entry + 16, 0x5678)
            cpu.mem_write(entry + 8, bytes([direction]))
            cpu.mem_write(entry + 9, bytes([direction]))
            cpu.mem_write(entry + 10, bytes([alpha]))
            cpu.mem_write(entry + 11, bytes([mode]))
            cpu.mem_write(entry + 20, percent.to_bytes(2, 'little', signed=True))
            targets = {(syms[name] if compiled else address) & ~1: key
                       for key, (address, name) in CALLS.items()}
            callback_values = {(syms[name] if compiled else address) & ~1: key
                               for key, (address, name) in CALLBACKS.items()}
            def callback(word):
                return callback_values.get(word & ~1, hex(word))
            trace = []
            def hook(cpu, address, size, _):
                key = targets.get(address)
                if key is None:
                    return
                r0, r1, r2 = (cpu.reg_read(A.UC_ARM_REG_R0),
                              cpu.reg_read(A.UC_ARM_REG_R1),
                              cpu.reg_read(A.UC_ARM_REG_R2))
                if key == 'init':
                    cpu.mem_write(r0, bytes(96))
                    trace.append((key,))
                elif key == 'values':
                    trace.append((key, r1, r2))
                elif key == 'start':
                    words = [int.from_bytes(cpu.mem_read(r0 + i, 4), 'little')
                             for i in (0, 4, 16, 48)]
                    trace.append((key, words[0], callback(words[1]),
                                  callback(words[2]), words[3]))
                elif key in ('prepare',):
                    trace.append((key,))
                elif key in ('set_x', 'set_y'):
                    trace.append((key, r0, r1))
                elif key == 'reset':
                    trace.append((key, r0, r1, r2))
                else:
                    trace.append((key, r0))
                result = {'owner': owner if owner_valid else 0,
                          'parent': parent, 'width': 100, 'height': 80,
                          'x': 17, 'y': 19}.get(key, 0)
                cpu.reg_write(A.UC_ARM_REG_R0, result)
                cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
            cpu.hook_add(UC_HOOK_CODE, hook)
            cpu.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
            cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
            cpu.reg_write(A.UC_ARM_REG_R0, entry)
            cpu.reg_write(A.UC_ARM_REG_R1, forward)
            start = syms['audio_uart_display_audio_start_45ef24'] if compiled else 0x45ef24
            cpu.emu_start(start | 1, 0x600000, count=1000)
            return trace, bytes(cpu.mem_read(owner + 232, 1))

        cases = 0
        for args in itertools.product((0, 1), (0, 1, 2), (0, 1), (0, 1),
                                      (0, 50, 100), (False, True)):
            stock, rebuilt = run(False, *args), run(True, *args)
            if stock != rebuilt:
                raise RuntimeError(f'animation start mismatch {args}: {stock} != {rebuilt}')
            cases += 1
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_AUDIO_PAGE_START_ORACLE',
               'cases': cases, 'source_sha256': hashlib.sha256(SRC.read_bytes()).hexdigest(),
               'payload_sha256': PAYLOAD_SHA, 'stock_entry': '0x45ef24',
               'limits': ['Callee effects are hooked; descriptor fields, call order and arguments compared.',
                          'Live animation, callback and page behavior remain open.']}
    (OUT / 'oracle.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], cases)

if __name__ == '__main__': main()
