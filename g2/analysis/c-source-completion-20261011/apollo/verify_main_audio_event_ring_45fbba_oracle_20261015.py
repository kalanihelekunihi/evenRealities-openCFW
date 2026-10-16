#!/usr/bin/env python3
"""Compare Apollo audio event ring predicates and dequeue with stock Thumb."""
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
SRC = G2 / 'components/audio/uart_thread_source_candidate/display_audio_event_ring_45fbba.c'
OUT = G2 / 'build/c-firmware/20261015/main-audio-event-ring-45fbba'
PAYLOAD_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
FUNCTIONS = {'empty': (0x45fbba, 'audio_uart_display_audio_ring_empty_45fbba'),
             'full': (0x45fbd0, 'audio_uart_display_audio_ring_full_45fbd0'),
             'dequeue': (0x45fc5a, 'audio_uart_display_audio_dequeue_45fc5a')}

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    blob = (G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PAYLOAD_SHA:
        raise RuntimeError('Apollo payload changed')
    with tempfile.TemporaryDirectory() as td:
        elf = Path(td) / 'oracle.elf'
        subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                        '-std=c11', '-ffreestanding', '-fno-builtin', '-O2', '-nostdlib',
                        '-Wl,-Ttext=0x100000', '-Wl,-e,audio_uart_display_audio_dequeue_45fc5a',
                        str(SRC), '-o', str(elf)], check=True)
        syms = {p[2]: int(p[0], 16) for line in subprocess.check_output(
            ['arm-none-eabi-nm', str(elf)], text=True).splitlines()
            if len(p := line.split()) == 3}
        with elf.open('rb') as f:
            segments = [(s['p_vaddr'], s.data()) for s in ELFFile(f).iter_segments()
                        if s['p_type'] == 'PT_LOAD']

        def run(compiled, kind, state_valid, output_valid, count, index, fill):
            cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            cpu.mem_map(0x400000, 0x400000)
            cpu.mem_write(0x438000, blob)
            cpu.mem_map(0x100000, 0x100000)
            for address, data in segments:
                cpu.mem_write(address, data)
            cpu.mem_map(0x20000000, 0x400000)
            state, output = 0x20011000, 0x20012000
            cpu.mem_write(state, bytes([fill]) * 256)
            cpu.mem_write(output, bytes([0xa5]) * 12)
            cpu.mem_write(state + 36 + 192, bytes([index]))
            cpu.mem_write(state + 36 + 194, bytes([count]))
            cpu.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
            cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
            cpu.reg_write(A.UC_ARM_REG_R0,
                          (state if kind == 'dequeue' else state + 36) if state_valid else 0)
            cpu.reg_write(A.UC_ARM_REG_R1, output if output_valid else 0)
            stock_addr, name = FUNCTIONS[kind]
            start = syms[name] if compiled else stock_addr
            cpu.emu_start(start | 1, 0x600000, count=200)
            return (cpu.reg_read(A.UC_ARM_REG_R0), bytes(cpu.mem_read(state, 256)),
                    bytes(cpu.mem_read(output, 12)))

        cases = 0
        for kind, state_valid, output_valid, count, index, fill in itertools.product(
                FUNCTIONS, (False, True), (False, True), (0, 1, 15, 16),
                (0, 15), (0, 0x55)):
            stock, rebuilt = run(False, kind, state_valid, output_valid, count, index, fill), \
                run(True, kind, state_valid, output_valid, count, index, fill)
            if stock != rebuilt:
                raise RuntimeError(f'ring mismatch {(kind, state_valid, output_valid, count, index, fill)}: '
                                   f'{stock[0]} != {rebuilt[0]}')
            cases += 1
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_AUDIO_EVENT_RING_ORACLE',
               'cases': cases, 'source_sha256': hashlib.sha256(SRC.read_bytes()).hexdigest(),
               'payload_sha256': PAYLOAD_SHA,
               'limits': ['Controlled ring indices and counts; concurrent producer/consumer effects remain open.']}
    (OUT / 'oracle.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], cases)

if __name__ == '__main__': main()
