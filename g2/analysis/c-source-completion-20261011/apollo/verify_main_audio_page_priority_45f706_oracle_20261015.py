#!/usr/bin/env python3
"""Compare Apollo audio priority guard return values with stock Thumb code."""
import hashlib
import itertools
import json
import subprocess
import tempfile
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import UC_ARCH_ARM, UC_MODE_THUMB, Uc
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
SRC = G2 / 'components/audio/uart_thread_source_candidate/display_audio_page_priority_45f706.c'
OUT = G2 / 'build/c-firmware/20261015/main-audio-page-priority-45f706'
PAYLOAD_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    blob = (G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PAYLOAD_SHA:
        raise RuntimeError('Apollo payload changed')
    with tempfile.TemporaryDirectory() as td:
        elf = Path(td) / 'oracle.elf'
        subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                        '-std=c11', '-ffreestanding', '-fno-builtin', '-O2', '-nostdlib',
                        '-Wl,-Ttext=0x100000', '-Wl,-e,audio_uart_display_audio_priority_45f706',
                        str(SRC), '-o', str(elf)], check=True)
        syms = {p[2]: int(p[0], 16) for line in subprocess.check_output(
            ['arm-none-eabi-nm', str(elf)], text=True).splitlines()
            if len(p := line.split()) == 3}
        with elf.open('rb') as f:
            segments = [(s['p_vaddr'], s.data()) for s in ELFFile(f).iter_segments()
                        if s['p_type'] == 'PT_LOAD']

        def run(compiled, state_valid, entry_valid, has_current, mode, own_priority, current_priority):
            cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            cpu.mem_map(0x400000, 0x400000)
            cpu.mem_write(0x438000, blob)
            cpu.mem_map(0x100000, 0x100000)
            for address, data in segments:
                cpu.mem_write(address, data)
            cpu.mem_map(0x20000000, 0x400000)
            state, entry, current = 0x20011000, 0x20012000, 0x20013000
            for address in (state, entry, current):
                cpu.mem_write(address, bytes(64))
            cpu.mem_write(state, (current if has_current else 0).to_bytes(4, 'little'))
            cpu.mem_write(entry + 11, bytes([mode]))
            cpu.mem_write(entry + 22, bytes([own_priority]))
            cpu.mem_write(current + 22, bytes([current_priority]))
            cpu.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
            cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
            cpu.reg_write(A.UC_ARM_REG_R0, state if state_valid else 0)
            cpu.reg_write(A.UC_ARM_REG_R1, entry if entry_valid else 0)
            start = syms['audio_uart_display_audio_priority_45f706'] if compiled else 0x45f706
            cpu.emu_start(start | 1, 0x600000, count=100)
            return cpu.reg_read(A.UC_ARM_REG_R0)

        cases = 0
        for args in itertools.product((False, True), (False, True), (False, True),
                                      (0, 1, 2), (0, 1, 22, 255), (0, 1, 22, 255)):
            stock, rebuilt = run(False, *args), run(True, *args)
            if stock != rebuilt:
                raise RuntimeError(f'priority mismatch {args}: {stock} != {rebuilt}')
            cases += 1
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_AUDIO_PAGE_PRIORITY_ORACLE',
               'cases': cases, 'source_sha256': hashlib.sha256(SRC.read_bytes()).hexdigest(),
               'payload_sha256': PAYLOAD_SHA, 'stock_entry': '0x45f706',
               'limits': ['Controlled pointer, mode and priority comparisons only.']}
    (OUT / 'oracle.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], cases)

if __name__ == '__main__': main()
