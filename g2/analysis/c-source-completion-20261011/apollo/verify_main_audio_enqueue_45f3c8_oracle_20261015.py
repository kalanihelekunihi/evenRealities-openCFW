#!/usr/bin/env python3
"""Compare Apollo audio enqueue registration against pinned stock Thumb."""
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
SRC = G2 / 'components/audio/uart_thread_source_candidate/display_audio_enqueue_45f3c8.c'
OUT = G2 / 'build/c-firmware/20261015/main-audio-enqueue-45f3c8'
PAYLOAD_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
CALLS = {'unique': (0x45fb44, 'audio_uart_display_audio_unique_45fb44'),
         'alloc': (0x474cd2, 'codec_allocate'),
         'copy': (0x439c04, 'audio_uart_display_area_copy_439c04'),
         'fatal': (0x45f402, 'audio_uart_display_audio_allocation_fatal_45f402'),
         'parent': (0x44d94c, 'audio_uart_lv_obj_set_parent_44d94c'),
         'flags': (0x43ded4, 'audio_uart_page_43ded4'),
         'layout': (0x43f66c, 'audio_uart_page_43f66c'),
         'width': (0x43fd9e, 'audio_uart_lv_obj_width_43fd9e'),
         'height': (0x43fdda, 'audio_uart_lv_obj_height_43fdda'),
         'set_x': (0x43f0e0, 'audio_uart_page_43f0e0'),
         'set_y': (0x43f142, 'audio_uart_page_43f142')}
SHIM = '''#include <stdint.h>
__attribute__((noinline)) uint32_t audio_uart_display_audio_unique_45fb44(void*a,uint32_t b){(void)a;(void)b;return 0;}
__attribute__((noinline)) void *codec_allocate(uint32_t a){(void)a;return 0;}
__attribute__((noinline)) void *audio_uart_display_area_copy_439c04(void*a,const void*b,uint32_t c){(void)a;(void)b;(void)c;return a;}
__attribute__((noinline)) void audio_uart_display_audio_allocation_fatal_45f402(void){}
__attribute__((noinline)) void audio_uart_lv_obj_set_parent_44d94c(void*a,void*b){(void)a;(void)b;}
__attribute__((noinline)) void audio_uart_page_43ded4(void*a,uint32_t b){(void)a;(void)b;}
__attribute__((noinline)) void audio_uart_page_43f66c(void*a){(void)a;}
__attribute__((noinline)) int32_t audio_uart_lv_obj_width_43fd9e(void*a){(void)a;return 0;}
__attribute__((noinline)) int32_t audio_uart_lv_obj_height_43fdda(void*a){(void)a;return 0;}
__attribute__((noinline)) void audio_uart_page_43f0e0(void*a,int32_t b){(void)a;(void)b;}
__attribute__((noinline)) void audio_uart_page_43f142(void*a,int32_t b){(void)a;(void)b;}
'''

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
                        '-Wl,-Ttext=0x100000',
                        '-Wl,-e,audio_uart_display_audio_enqueue_45f3c8',
                        str(SRC), str(shim), '-o', str(elf)], check=True)
        syms = {p[2]: int(p[0], 16) for line in subprocess.check_output(
            ['arm-none-eabi-nm', str(elf)], text=True).splitlines()
            if len(p := line.split()) == 3}
        with elf.open('rb') as f:
            segments = [(s['p_vaddr'], s.data()) for s in ELFFile(f).iter_segments()
                        if s['p_type'] == 'PT_LOAD']

        def run(compiled, valid, unique, mode, ready, direction, prior, defaults):
            cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            cpu.mem_map(0x400000, 0x400000)
            cpu.mem_write(0x438000, blob)
            cpu.mem_map(0x100000, 0x100000)
            for address, data in segments:
                cpu.mem_write(address, data)
            cpu.mem_map(0x20000000, 0x400000)
            state, config, entry, obj, pa, pb, head = (
                0x20011000, 0x20012000, 0x20013000, 0x20014000,
                0x20015000, 0x20016000, 0x20017000)
            for address in (state, config, entry, obj, pa, pb, head):
                cpu.mem_write(address, bytes(256))
            put(cpu, config, 0x30)
            put(cpu, config + 4, obj)
            put(cpu, config + 12, 0 if defaults else 111)
            put(cpu, config + 16, 0 if defaults else 222)
            cpu.mem_write(config + 20, b'\x00\x00' if defaults else b'\x06\x00')
            cpu.mem_write(config + 22, bytes([0 if defaults else 9]))
            cpu.mem_write(config + 8, bytes([direction]))
            cpu.mem_write(config + 11, bytes([mode]))
            cpu.mem_write(config + 23, bytes([ready]))
            put(cpu, state + 28, pa)
            put(cpu, state + 32, pb)
            put(cpu, state + (12 if mode == 0 else 8), head if prior else 0)
            targets = {(syms[name] if compiled else address) & ~1: key
                       for key, (address, name) in CALLS.items()}
            regs = (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                    A.UC_ARM_REG_R2, A.UC_ARM_REG_R3)
            trace = []
            widths = {'unique': 2, 'alloc': 1, 'copy': 3, 'parent': 2,
                      'flags': 2, 'layout': 1, 'width': 1, 'height': 1,
                      'set_x': 2, 'set_y': 2, 'fatal': 0}
            def hook(cpu, address, size, _):
                key = targets.get(address)
                if key is None:
                    return
                values = tuple(cpu.reg_read(r) for r in regs)
                trace.append((key, values[:widths[key]]))
                if key == 'copy':
                    cpu.mem_write(values[0], bytes(cpu.mem_read(values[1], values[2])))
                result = (1 if unique else 0) if key == 'unique' else \
                         entry if key == 'alloc' else \
                         values[0] if key == 'copy' else \
                         51 if key == 'width' else 61 if key == 'height' else 0
                cpu.reg_write(A.UC_ARM_REG_R0, result)
                cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
            cpu.hook_add(UC_HOOK_CODE, hook)
            cpu.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
            cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
            cpu.reg_write(A.UC_ARM_REG_R0, state if valid else 0)
            cpu.reg_write(A.UC_ARM_REG_R1, config)
            start = syms['audio_uart_display_audio_enqueue_45f3c8'] if compiled else 0x45f3c8
            cpu.emu_start(start | 1, 0x600000, count=700)
            memory = (bytes(cpu.mem_read(entry, 40)), bytes(cpu.mem_read(obj + 16, 4)),
                      bytes(cpu.mem_read(head + 36, 4)),
                      tuple(get(cpu, state + off) for off in (4, 8, 12)))
            return trace, cpu.reg_read(A.UC_ARM_REG_R0), memory

        cases = 0
        for args in itertools.product((False, True), (False, True),
                                      (0, 1), (0, 1), (0, 1, 2),
                                      (False, True), (False, True)):
            stock, rebuilt = run(False, *args), run(True, *args)
            if stock != rebuilt:
                raise RuntimeError(f'enqueue mismatch {args}: {stock} != {rebuilt}')
            cases += 1
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_AUDIO_ENQUEUE_ORACLE',
               'cases': cases, 'source_sha256': hashlib.sha256(SRC.read_bytes()).hexdigest(),
               'payload_sha256': PAYLOAD_SHA,
               'limits': ['Successful allocation, list insertion, geometry and child calls compared.',
                          'Allocation-failure diagnostic and live effects remain open.']}
    (OUT / 'oracle.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], cases)

if __name__ == '__main__': main()
