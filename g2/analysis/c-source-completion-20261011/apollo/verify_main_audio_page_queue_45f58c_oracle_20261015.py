#!/usr/bin/env python3
"""Compare Apollo audio queue transitions against the pinned stock payload."""
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
SRC = G2 / 'components/audio/uart_thread_source_candidate/display_audio_page_queue_45f58c.c'
OUT = G2 / 'build/c-firmware/20261015/main-audio-page-queue-45f58c'
PAYLOAD_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
CALLS = {'find': (0x45f840, 'audio_uart_display_audio_find_45f840'),
         'ready': (0x45f8a4, 'audio_uart_display_audio_ready_45f8a4'),
         'schedule': (0x44228a, 'audio_uart_display_audio_schedule_44228a'),
         'start': (0x45ef24, 'audio_uart_display_audio_start_45ef24')}
SHIM = ('#include <stdint.h>\n'
        '__attribute__((noinline)) void *audio_uart_display_audio_find_45f840(void*a,uint32_t b)'
        '{(void)a;(void)b;return 0;}\n'
        '__attribute__((noinline)) void audio_uart_display_audio_ready_45f8a4(void*a)'
        '{(void)a;}\n'
        '__attribute__((noinline)) void audio_uart_display_audio_schedule_44228a'
        '(uint32_t a,uint32_t b,uint32_t c,uint32_t d)'
        '{(void)a;(void)b;(void)c;(void)d;}\n'
        '__attribute__((noinline)) void audio_uart_display_audio_start_45ef24(void*a,uint32_t b)'
        '{(void)a;(void)b;}\n')

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
                        '-Wl,-Ttext=0x100000', '-Wl,-e,audio_uart_display_audio_queue_45f58c',
                        str(SRC), str(shim), '-o', str(elf)], check=True)
        syms = {p[2]: int(p[0], 16) for line in subprocess.check_output(
            ['arm-none-eabi-nm', str(elf)], text=True).splitlines()
            if len(p := line.split()) == 3}
        with elf.open('rb') as f:
            segments = [(s['p_vaddr'], s.data()) for s in ELFFile(f).iter_segments()
                        if s['p_type'] == 'PT_LOAD']

        def run(compiled, state_valid, id_valid, found, active, mode,
                current, prior, callback):
            cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            cpu.mem_map(0x400000, 0x400000)
            cpu.mem_write(0x438000, blob)
            cpu.mem_map(0x100000, 0x100000)
            for address, data in segments:
                cpu.mem_write(address, data)
            cpu.mem_map(0x20000000, 0x400000)
            state, entry, other = 0x20011000, 0x20012000, 0x20013000
            for address in (state, entry, other):
                cpu.mem_write(address, bytes(64))
            put(cpu, state, other if current else 0)
            put(cpu, state + 4, other if prior else 0)
            put(cpu, entry, 0x42)
            cpu.mem_write(entry + 11, bytes([mode]))
            cpu.mem_write(entry + 28, bytes([1 if active else 0]))
            put(cpu, other + 24, 0x20018001 if callback else 0)
            targets = {(syms[name] if compiled else address) & ~1: key
                       for key, (address, name) in CALLS.items()}
            targets[0x20018000] = 'callback'
            widths = {'find': 2, 'ready': 1, 'schedule': 4, 'start': 2, 'callback': 4}
            trace = []
            regs = (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1, A.UC_ARM_REG_R2, A.UC_ARM_REG_R3)
            def hook(cpu, address, size, _):
                key = targets.get(address)
                if key is None:
                    return
                trace.append((key, tuple(cpu.reg_read(r) for r in regs[:widths[key]])))
                cpu.reg_write(A.UC_ARM_REG_R0, entry if key == 'find' and found else 0)
                cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
            cpu.hook_add(UC_HOOK_CODE, hook)
            cpu.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
            cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
            cpu.reg_write(A.UC_ARM_REG_R0, state if state_valid else 0)
            cpu.reg_write(A.UC_ARM_REG_R1, 0x42 if id_valid else 0)
            start = syms['audio_uart_display_audio_queue_45f58c'] if compiled else 0x45f58c
            cpu.emu_start(start | 1, 0x600000, count=500)
            return (trace, bytes(cpu.mem_read(state, 24)),
                    bytes(cpu.mem_read(entry, 32)), bytes(cpu.mem_read(other, 32)))

        cases = 0
        for args in itertools.product((False, True), repeat=8):
            stock, rebuilt = run(False, *args), run(True, *args)
            if stock != rebuilt:
                raise RuntimeError(f'queue mismatch {args}: {stock} != {rebuilt}')
            cases += 1
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_AUDIO_PAGE_QUEUE_ORACLE',
               'cases': cases, 'source_sha256': hashlib.sha256(SRC.read_bytes()).hexdigest(),
               'payload_sha256': PAYLOAD_SHA, 'stock_entry': '0x45f58c',
               'limits': ['Find, ready, schedule, start and callback calls are hooked.',
                          'Live callback effects remain open.']}
    (OUT / 'oracle.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], cases)

if __name__ == '__main__': main()
