#!/usr/bin/env python3
"""Compare the Apollo audio terminal predicate with pinned stock Thumb."""
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
SRC = G2 / 'components/audio/uart_thread_source_candidate/display_audio_terminal_mode_45bbf4.c'
OUT = G2 / 'build/c-firmware/20261015/main-audio-terminal-mode-45bbf4'
PAYLOAD_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    blob = (G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PAYLOAD_SHA:
        raise RuntimeError('Apollo payload changed')
    with tempfile.TemporaryDirectory() as td:
        shim, elf = Path(td) / 'shim.c', Path(td) / 'oracle.elf'
        shim.write_text('#include <stdint.h>\n__attribute__((noinline)) '
                        'uint32_t audio_settings_terminal_mode(void){return 0;}\n')
        subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                        '-std=c11', '-ffreestanding', '-fno-builtin', '-O2', '-nostdlib',
                        '-Wl,-Ttext=0x100000',
                        '-Wl,-e,audio_uart_display_audio_terminal_mode_45bbf4',
                        str(SRC), str(shim), '-o', str(elf)], check=True)
        syms = {p[2]: int(p[0], 16) for line in subprocess.check_output(
            ['arm-none-eabi-nm', str(elf)], text=True).splitlines()
            if len(p := line.split()) == 3}
        with elf.open('rb') as f:
            segments = [(s['p_vaddr'], s.data()) for s in ELFFile(f).iter_segments()
                        if s['p_type'] == 'PT_LOAD']

        def run(compiled, value):
            cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            cpu.mem_map(0x400000, 0x400000)
            cpu.mem_write(0x438000, blob)
            cpu.mem_map(0x100000, 0x100000)
            for address, data in segments:
                cpu.mem_write(address, data)
            cpu.mem_map(0x20000000, 0x400000)
            target = (syms['audio_settings_terminal_mode'] if compiled else 0x46c630) & ~1
            trace = []
            def hook(cpu, address, size, _):
                if address != target:
                    return
                trace.append('terminal_mode')
                cpu.reg_write(A.UC_ARM_REG_R0, value)
                cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
            cpu.hook_add(UC_HOOK_CODE, hook)
            cpu.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
            cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
            start = (syms['audio_uart_display_audio_terminal_mode_45bbf4']
                     if compiled else 0x45bbf4)
            cpu.emu_start(start | 1, 0x600000, count=50)
            return trace, cpu.reg_read(A.UC_ARM_REG_R0)

        cases = 0
        for value in (0, 1, 2, 0xffffffff):
            stock, rebuilt = run(False, value), run(True, value)
            if stock != rebuilt:
                raise RuntimeError(f'terminal predicate mismatch {value}: {stock} != {rebuilt}')
            cases += 1
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_AUDIO_TERMINAL_MODE_ORACLE',
               'cases': cases, 'source_sha256': hashlib.sha256(SRC.read_bytes()).hexdigest(),
               'payload_sha256': PAYLOAD_SHA,
               'limits': ['Terminal-mode child is cut at its call boundary.',
                          'Four controlled return values; live settings state remains open.']}
    (OUT / 'oracle.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], cases)

if __name__ == '__main__': main()
