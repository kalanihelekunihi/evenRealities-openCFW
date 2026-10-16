#!/usr/bin/env python3
"""Compare diagnostic-disabled Apollo registry dispatch paths."""
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
SRC = G2 / 'components/audio/uart_thread_source_candidate/display_audio_scheduler_44228a.c'
OUT = G2 / 'build/c-firmware/20261015/main-audio-scheduler-core-44228a'
PAYLOAD_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
CALLS = {'terminal': (0x45bbf4, 'audio_uart_display_audio_terminal_mode_45bbf4'),
         'enqueue': (0x45f3c8, 'audio_uart_display_audio_enqueue_45f3c8'),
         'route': (0x45f876, 'audio_uart_display_audio_route_45f876'),
         'set_mode': (0x45fe32, 'audio_uart_display_audio_set_mode_45fe32')}
SHIM = '''#include <stdint.h>
volatile uint32_t audio_uart_user_registry_count;
uint8_t audio_uart_user_registry_rows[16];
uint32_t audio_uart_display_audio_handle;
uint32_t audio_uart_display_mode;
uint32_t audio_uart_display_background;
__attribute__((noinline)) uint32_t audio_uart_display_audio_terminal_mode_45bbf4(void){return 0;}
__attribute__((noinline)) uint32_t audio_uart_display_audio_enqueue_45f3c8(void*a,void*b){(void)a;(void)b;return 0;}
__attribute__((noinline)) uint32_t audio_uart_display_audio_route_45f876(void*a,uint32_t b){(void)a;(void)b;return 0;}
__attribute__((noinline)) uint32_t audio_uart_display_audio_set_mode_45fe32(uint32_t a,uint32_t b){(void)a;(void)b;return 0;}
__attribute__((noinline)) uint32_t audio_log_level(void){return 0;}
__attribute__((noinline)) void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...)
{(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
__attribute__((noinline)) uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...)
{(void)a;(void)b;(void)c;return 0;}
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
                        '-Wl,-e,audio_uart_display_audio_schedule_44228a',
                        str(SRC), str(shim), '-o', str(elf)], check=True)
        syms = {p[2]: int(p[0], 16) for line in subprocess.check_output(
            ['arm-none-eabi-nm', str(elf)], text=True).splitlines()
            if len(p := line.split()) == 3}
        with elf.open('rb') as f:
            segments = [(s['p_vaddr'], s.data()) for s in ELFFile(f).iter_segments()
                        if s['p_type'] == 'PT_LOAD']

        def run(compiled, config_mode, terminal, operation, ident,
                row_match, callback_valid, log_mask):
            cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            cpu.mem_map(0x400000, 0x400000)
            cpu.mem_write(0x438000, blob)
            cpu.mem_map(0x100000, 0x100000)
            for address, data in segments:
                cpu.mem_write(address, data)
            cpu.mem_map(0x20000000, 0x400000)
            count, rows, handle, mode, background = (
                (syms[n] for n in ('audio_uart_user_registry_count',
                                   'audio_uart_user_registry_rows',
                                   'audio_uart_display_audio_handle',
                                   'audio_uart_display_mode',
                                   'audio_uart_display_background')) if compiled else
                (0x200744d4, 0x20066230, 0x200744d0, 0x200744dc, 0x200744e0))
            current, config = 0x20014000, 0x20015000
            cpu.mem_write(current, bytes(64))
            cpu.mem_write(config, bytes(64))
            put(cpu, current + 28, 0x1357)
            put(cpu, current + 32, 0x2468)
            put(cpu, count, 1)
            put(cpu, rows, ident if row_match else ident + 1)
            put(cpu, rows + 8, 0x20018001 if callback_valid else 0)
            put(cpu, rows + 12, config)
            put(cpu, config, 0x30 if ident == 0x30 else 0x33)
            cpu.mem_write(config + 11, bytes([config_mode]))
            put(cpu, handle, current)
            put(cpu, mode, 9)
            put(cpu, background, 11)
            targets = {(syms[name] if compiled else address) & ~1: key
                       for key, (address, name) in CALLS.items()}
            targets[0x20018000] = 'callback'
            targets[(syms['audio_log_level'] if compiled else 0x43d0ce) & ~1] = 'log_level'
            targets[(syms['audio_log_extended'] if compiled else 0x43d574) & ~1] = 'log_extended'
            targets[(syms['compressed_log_output'] if compiled else 0x43ce9e) & ~1] = 'log_compact'
            regs = (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                    A.UC_ARM_REG_R2, A.UC_ARM_REG_R3)
            trace = []
            def cstring(ptr):
                return bytes(cpu.mem_read(ptr, 160)).split(b'\x00', 1)[0].decode('utf-8')
            def hook(cpu, address, size, _):
                key = targets.get(address)
                if key is None:
                    return
                vals = tuple(cpu.reg_read(r) for r in regs)
                if key == 'log_extended':
                    sp = cpu.reg_read(A.UC_ARM_REG_SP)
                    trace.append((key, vals[0], *(cstring(v) for v in vals[1:]),
                                  get(cpu, sp), cstring(get(cpu, sp + 4)), get(cpu, sp + 8)))
                elif key == 'log_compact':
                    trace.append((key, vals[0], cstring(vals[1]), cstring(vals[2]), vals[3]))
                elif key != 'log_level':
                    trace.append((key, vals[:4 if key == 'callback' else
                                            0 if key == 'terminal' else 2]))
                cpu.reg_write(A.UC_ARM_REG_R0,
                              terminal if key == 'terminal' else
                              log_mask if key == 'log_level' else 0)
                cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
            cpu.hook_add(UC_HOOK_CODE, hook)
            cpu.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
            cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
            for reg, value in zip(regs, (ident, operation, 0x5678, 0x9abc)):
                cpu.reg_write(reg, value)
            start = syms['audio_uart_display_audio_schedule_44228a'] if compiled else 0x44228a
            cpu.emu_start(start | 1, 0x600000, count=500)
            return trace, get(cpu, mode), get(cpu, background)

        cases = 0
        for args in itertools.product((0, 1, 2), (0, 1), (1, 2),
                                      (0x30, 4, 7), (False, True),
                                      (False, True), (0, 1, 2, 4, 7)):
            stock, rebuilt = run(False, *args), run(True, *args)
            if stock != rebuilt:
                raise RuntimeError(f'scheduler core mismatch {args}: {stock} != {rebuilt}')
            cases += 1
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_AUDIO_SCHEDULER_CORE_ORACLE',
               'cases': cases, 'source_sha256': hashlib.sha256(SRC.read_bytes()).hexdigest(),
               'payload_sha256': PAYLOAD_SHA,
               'limits': ['Registration, callback, logging and child calls are hooked.',
                          'Live dispatcher, queue and display effects remain open.']}
    (OUT / 'oracle.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], cases)

if __name__ == '__main__': main()
