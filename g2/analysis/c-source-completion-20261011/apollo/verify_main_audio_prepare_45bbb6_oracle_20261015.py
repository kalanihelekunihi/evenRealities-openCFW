#!/usr/bin/env python3
"""Compare Apollo display preparation flag and lock sequence with stock."""
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
SRC = G2 / 'components/audio/uart_thread_source_candidate/display_audio_prepare_45bbb6.c'
OUT = G2 / 'build/c-firmware/20261015/main-audio-prepare-45bbb6'
PAYLOAD_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
SHIM = ('#include <stdint.h>\n'
        'volatile uint32_t audio_uart_display_audio_flag_cell;\n'
        '__attribute__((noinline)) void audio_uart_display_audio_acquire_45baf0(void){}\n'
        '__attribute__((noinline)) void audio_uart_display_audio_release_45bb58(void){}\n')

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
                        '-Wl,-Ttext=0x100000', '-Wl,-e,audio_uart_display_audio_prepare_45bbb6',
                        str(SRC), str(shim), '-o', str(elf)], check=True)
        syms = {p[2]: int(p[0], 16) for line in subprocess.check_output(
            ['arm-none-eabi-nm', str(elf)], text=True).splitlines()
            if len(p := line.split()) == 3}
        with elf.open('rb') as f:
            segments = [(s['p_vaddr'], s.data()) for s in ELFFile(f).iter_segments()
                        if s['p_type'] == 'PT_LOAD']

        def run(compiled, initial):
            cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            cpu.mem_map(0x400000, 0x400000)
            cpu.mem_write(0x438000, blob)
            cpu.mem_map(0x100000, 0x100000)
            for address, data in segments:
                cpu.mem_write(address, data)
            cpu.mem_map(0x20000000, 0x400000)
            flag = syms['audio_uart_display_audio_flag_cell'] if compiled else 0x200749e4
            cpu.mem_write(flag, initial.to_bytes(4, 'little'))
            targets = {
                (syms['audio_uart_display_audio_acquire_45baf0'] if compiled else 0x45baf0) & ~1: 'acquire',
                (syms['audio_uart_display_audio_release_45bb58'] if compiled else 0x45bb58) & ~1: 'release',
            }
            trace = []
            def hook(cpu, address, size, _):
                key = targets.get(address)
                if key is None:
                    return
                trace.append(key)
                cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
            cpu.hook_add(UC_HOOK_CODE, hook)
            cpu.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
            cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
            start = syms['audio_uart_display_audio_prepare_45bbb6'] if compiled else 0x45bbb6
            cpu.emu_start(start | 1, 0x600000, count=100)
            return trace, int.from_bytes(cpu.mem_read(flag, 4), 'little')

        cases = 0
        for initial in (0, 1, 2, 0xffffffff):
            stock, rebuilt = run(False, initial), run(True, initial)
            if stock != rebuilt:
                raise RuntimeError(f'prepare mismatch {initial=}: {stock} != {rebuilt}')
            cases += 1
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_AUDIO_PREPARE_ORACLE',
               'cases': cases, 'source_sha256': hashlib.sha256(SRC.read_bytes()).hexdigest(),
               'payload_sha256': PAYLOAD_SHA,
               'limits': ['Acquire/release are hooked; native lock effects remain open.']}
    (OUT / 'oracle.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], cases)

if __name__ == '__main__': main()
