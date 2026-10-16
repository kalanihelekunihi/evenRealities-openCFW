#!/usr/bin/env python3
"""Compare Apollo audio entry uniqueness against pinned stock Thumb."""
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
SRC = G2 / 'components/audio/uart_thread_source_candidate/display_audio_unique_45fb44.c'
OUT = G2 / 'build/c-firmware/20261015/main-audio-unique-45fb44'
PAYLOAD_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'

def put(cpu, address, value):
    cpu.mem_write(address, (value & 0xffffffff).to_bytes(4, 'little'))

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    blob = (G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PAYLOAD_SHA:
        raise RuntimeError('Apollo payload changed')
    with tempfile.TemporaryDirectory() as td:
        elf = Path(td) / 'oracle.elf'
        subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                        '-std=c11', '-ffreestanding', '-fno-builtin', '-O2', '-nostdlib',
                        '-Wl,-Ttext=0x100000',
                        '-Wl,-e,audio_uart_display_audio_unique_45fb44',
                        str(SRC), '-o', str(elf)], check=True)
        syms = {p[2]: int(p[0], 16) for line in subprocess.check_output(
            ['arm-none-eabi-nm', str(elf)], text=True).splitlines()
            if len(p := line.split()) == 3}
        with elf.open('rb') as f:
            segments = [(s['p_vaddr'], s.data()) for s in ELFFile(f).iter_segments()
                        if s['p_type'] == 'PT_LOAD']

        def run(compiled, state_valid, ident, left, right):
            cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            cpu.mem_map(0x400000, 0x400000)
            cpu.mem_write(0x438000, blob)
            cpu.mem_map(0x100000, 0x100000)
            for address, data in segments:
                cpu.mem_write(address, data)
            cpu.mem_map(0x20000000, 0x400000)
            state, left1, left2, right1, right2 = (
                0x20011000, 0x20012000, 0x20012100, 0x20013000, 0x20013100)
            for address in (state, left1, left2, right1, right2):
                cpu.mem_write(address, bytes(64))
            put(cpu, state + 8, left1 if left else 0)
            put(cpu, state + 12, right1 if right else 0)
            if left:
                put(cpu, left1, 7 if left == 1 else 8)
                if left == 3:
                    put(cpu, left1 + 32, left2)
                    put(cpu, left2, 7)
            if right:
                put(cpu, right1, 7 if right == 1 else 8)
                if right == 3:
                    put(cpu, right1 + 32, right2)
                    put(cpu, right2, 7)
            cpu.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
            cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
            cpu.reg_write(A.UC_ARM_REG_R0, state if state_valid else 0)
            cpu.reg_write(A.UC_ARM_REG_R1, ident)
            start = syms['audio_uart_display_audio_unique_45fb44'] if compiled else 0x45fb44
            cpu.emu_start(start | 1, 0x600000, count=120)
            return cpu.reg_read(A.UC_ARM_REG_R0)

        cases = 0
        for args in itertools.product((False, True), (0, 7, 8),
                                      (0, 1, 2, 3), (0, 1, 2, 3)):
            stock, rebuilt = run(False, *args), run(True, *args)
            if stock != rebuilt:
                raise RuntimeError(f'audio unique mismatch {args}: {stock} != {rebuilt}')
            cases += 1
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_AUDIO_UNIQUE_ORACLE',
               'cases': cases, 'source_sha256': hashlib.sha256(SRC.read_bytes()).hexdigest(),
               'payload_sha256': PAYLOAD_SHA,
               'limits': ['Both linked lists, first and second entry matches are covered.',
                          'Live concurrent list mutation remains open.']}
    (OUT / 'oracle.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], cases)

if __name__ == '__main__': main()
