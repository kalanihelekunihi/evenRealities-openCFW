#!/usr/bin/env python3
"""Compare Apollo LV object reparenting against pinned stock Thumb."""
import hashlib
import itertools
import json
import subprocess
import tempfile
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import UC_ARCH_ARM, UC_HOOK_CODE, UC_MODE_THUMB, Uc, UcError
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
SRC = G2 / 'components/audio/uart_thread_source_candidate/display_lv_obj_set_parent_44d94c.c'
OUT = G2 / 'build/c-firmware/20261015/main-lv-obj-set-parent-44d94c'
PAYLOAD_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
CALLS = {'log': (0x44d25c, 'audio_uart_lvgl_log'),
         'invalidate': (0x440656, 'audio_uart_page_invalidate_440656'),
         'setup': (0x43e1fa, 'audio_uart_lv_obj_setup_layer_43e1fa'),
         'index': (0x44de92, 'audio_uart_lv_child_index_44de92'),
         'count': (0x44ddea, 'audio_uart_lv_child_count_44ddea'),
         'realloc': (0x44f76a, 'audio_uart_lv_realloc_44f76a'),
         'free': (0x44f758, 'audio_uart_lv_heap_free'),
         'scrollbar': (0x44f2ca, 'audio_uart_lv_scrollbar_invalidate_44f2ca'),
         'event': (0x451670, 'audio_uart_lv_obj_event_451670'),
         'mark': (0x43f648, 'audio_uart_lv_mark_layout_43f648')}
SHIM = '''#include <stdint.h>
__attribute__((noinline)) void audio_uart_lvgl_log(uint32_t a,const char*b,uint32_t c,const char*d,const char*e,...)
{(void)a;(void)b;(void)c;(void)d;(void)e;}
__attribute__((noinline)) void audio_uart_page_invalidate_440656(void*x){(void)x;}
__attribute__((noinline)) void audio_uart_lv_obj_setup_layer_43e1fa(void*x){(void)x;}
__attribute__((noinline)) int32_t audio_uart_lv_child_index_44de92(void*x){(void)x;return 0;}
__attribute__((noinline)) uint32_t audio_uart_lv_child_count_44ddea(void*x){(void)x;return 0;}
__attribute__((noinline)) void *audio_uart_lv_realloc_44f76a(void*x,uint32_t y){(void)x;(void)y;return 0;}
__attribute__((noinline)) void audio_uart_lv_heap_free(void*x){(void)x;}
__attribute__((noinline)) void audio_uart_lv_scrollbar_invalidate_44f2ca(void*x){(void)x;}
__attribute__((noinline)) uint32_t audio_uart_lv_obj_event_451670(void*x,uint32_t y,void*z)
{(void)x;(void)y;(void)z;return 0;}
__attribute__((noinline)) void audio_uart_lv_mark_layout_43f648(void*x){(void)x;}
'''

def put(cpu, address, value):
    cpu.mem_write(address, (value & 0xffffffff).to_bytes(4, 'little'))

def get(cpu, address):
    return int.from_bytes(cpu.mem_read(address, 4), 'little')

def put16(cpu, address, value):
    cpu.mem_write(address, (value & 0xffff).to_bytes(2, 'little'))

def get16(cpu, address):
    return int.from_bytes(cpu.mem_read(address, 2), 'little')

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
                        '-Wl,-Ttext=0x100000', '-Wl,-e,audio_uart_lv_obj_set_parent_44d94c',
                        str(SRC), str(shim), '-o', str(elf)], check=True)
        syms = {p[2]: int(p[0], 16) for line in subprocess.check_output(
            ['arm-none-eabi-nm', str(elf)], text=True).splitlines()
            if len(p := line.split()) == 3}
        with elf.open('rb') as f:
            segments = [(s['p_vaddr'], s.data()) for s in ELFFile(f).iter_segments()
                        if s['p_type'] == 'PT_LOAD']

        def run(compiled, old_count, index, new_count):
            cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            cpu.mem_map(0x400000, 0x400000)
            cpu.mem_write(0x438000, blob)
            cpu.mem_map(0x100000, 0x100000)
            for address, data in segments:
                cpu.mem_write(address, data)
            cpu.mem_map(0x20000000, 0x400000)
            obj, old, new, old_spec, new_spec, old_list, new_list, old_resize, new_resize = (
                0x20011000, 0x20012000, 0x20013000, 0x20014000, 0x20015000,
                0x20016000, 0x20017000, 0x20018000, 0x20019000)
            for address in (obj, old, new, old_spec, new_spec, old_list,
                            new_list, old_resize, new_resize):
                cpu.mem_write(address, bytes(256))
            put(cpu, obj + 4, old)
            put(cpu, old + 8, old_spec)
            put(cpu, new + 8, new_spec)
            put(cpu, old_spec, old_list)
            put(cpu, new_spec, new_list if new_count else 0)
            put16(cpu, old_spec + 48, old_count)
            put16(cpu, new_spec + 48, new_count)
            for i in range(old_count):
                put(cpu, old_list + i * 4, obj if i == index else 0x2001a000 + i * 4)
            for i in range(new_count):
                put(cpu, new_list + i * 4, 0x2001b000 + i * 4)
            targets = {(syms[name] if compiled else address) & ~1: key
                       for key, (address, name) in CALLS.items()}
            regs = (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1, A.UC_ARM_REG_R2)
            widths = {'log': 1, 'invalidate': 1, 'setup': 1,
                      'index': 1, 'count': 1, 'realloc': 2, 'free': 1,
                      'scrollbar': 1, 'event': 3, 'mark': 1}
            trace = []
            def hook(cpu, address, size, _):
                key = targets.get(address)
                if key is None:
                    return
                values = tuple(cpu.reg_read(r) for r in regs)
                trace.append((key, values[:widths[key]]))
                result = 0
                if key == 'index':
                    result = index
                elif key == 'count':
                    spec = old_spec if values[0] == old else new_spec
                    result = get16(cpu, spec + 48)
                elif key == 'realloc':
                    dest = old_resize if values[0] == old_list else new_resize
                    if values[0] and values[1]:
                        cpu.mem_write(dest, bytes(cpu.mem_read(values[0], values[1])))
                    result = dest
                cpu.reg_write(A.UC_ARM_REG_R0, result)
                cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
            cpu.hook_add(UC_HOOK_CODE, hook)
            cpu.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
            cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
            cpu.reg_write(A.UC_ARM_REG_R0, obj)
            cpu.reg_write(A.UC_ARM_REG_R1, new)
            start = syms['audio_uart_lv_obj_set_parent_44d94c'] if compiled else 0x44d94c
            cpu.emu_start(start | 1, 0x600000, count=700)
            state = (get(cpu, obj + 4), get(cpu, old_spec), get16(cpu, old_spec + 48),
                     get(cpu, new_spec), get16(cpu, new_spec + 48),
                     bytes(cpu.mem_read(old_list, old_count * 4)),
                     bytes(cpu.mem_read(old_resize, old_count * 4)),
                     bytes(cpu.mem_read(new_resize, (new_count + 1) * 4)))
            return trace, state

        def run_invalid(compiled, kind):
            cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            cpu.mem_map(0x400000, 0x400000)
            cpu.mem_write(0x438000, blob)
            cpu.mem_map(0x100000, 0x100000)
            for address, data in segments:
                cpu.mem_write(address, data)
            cpu.mem_map(0x20000000, 0x400000)
            obj, parent = 0x20011000, 0x20012000
            cpu.mem_write(obj, bytes(64))
            cpu.mem_write(parent, bytes(64))
            if kind != 'screen':
                put(cpu, obj + 4, parent)
            target = (syms['audio_uart_lvgl_log'] if compiled else 0x44d25c) & ~1
            trace = []
            def cstring(ptr):
                return bytes(cpu.mem_read(ptr, 160)).split(b'\x00', 1)[0].decode('utf-8')
            def hook(cpu, address, size, _):
                if address != target:
                    return
                sp = cpu.reg_read(A.UC_ARM_REG_SP)
                trace.append((cpu.reg_read(A.UC_ARM_REG_R0),
                              cstring(cpu.reg_read(A.UC_ARM_REG_R1)),
                              cpu.reg_read(A.UC_ARM_REG_R2),
                              cstring(cpu.reg_read(A.UC_ARM_REG_R3)),
                              cstring(get(cpu, sp)),
                              cstring(get(cpu, sp + 4)) if kind != 'screen' else None,
                              cstring(get(cpu, sp + 8)) if kind != 'screen' else None))
                cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
            cpu.hook_add(UC_HOOK_CODE, hook)
            cpu.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
            cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
            cpu.reg_write(A.UC_ARM_REG_R0, 0 if kind == 'object' else obj)
            cpu.reg_write(A.UC_ARM_REG_R1, 0 if kind == 'parent' else parent)
            start = syms['audio_uart_lv_obj_set_parent_44d94c'] if compiled else 0x44d94c
            try:
                cpu.emu_start(start | 1, 0x600000, count=150)
                outcome = 'return'
            except UcError:
                outcome = 'fault'
            return trace, outcome

        cases = 0
        for old_count, new_count in itertools.product((1, 2, 3), (0, 1, 2)):
            for index in range(old_count):
                args = (old_count, index, new_count)
                stock, rebuilt = run(False, *args), run(True, *args)
                if stock != rebuilt:
                    raise RuntimeError(f'LV parent mismatch {args}: {stock} != {rebuilt}')
                cases += 1
        for kind in ('object', 'parent', 'screen'):
            stock, rebuilt = run_invalid(False, kind), run_invalid(True, kind)
            if stock != rebuilt:
                raise RuntimeError(f'LV parent assertion mismatch {kind}: {stock} != {rebuilt}')
            cases += 1
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_LV_OBJ_SET_PARENT_ORACLE',
               'cases': cases, 'source_sha256': hashlib.sha256(SRC.read_bytes()).hexdigest(),
               'payload_sha256': PAYLOAD_SHA,
               'limits': ['Valid reparenting and three assertion paths compared.',
                          'Heap behavior and live UI effects remain open.']}
    (OUT / 'oracle.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], cases)

if __name__ == '__main__': main()
