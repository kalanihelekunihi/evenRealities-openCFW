#!/usr/bin/env python3
"""Compare four audio page pointer selectors and list scan to native Apollo."""
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
SRC = G2 / 'components/audio/uart_thread_source_candidate/display_audio_page_selectors_45f66a.c'
OUT = G2 / 'build/c-firmware/20261015/main-audio-page-selectors-45f66a'
PAYLOAD_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
FUNCTIONS = ((0x45f66a, 'audio_uart_display_audio_handler_b_45f66a'),
             (0x45f6a8, 'audio_uart_display_audio_handler_a_45f6a8'),
             (0x45f8e6, 'audio_uart_display_audio_current_45f8e6'),
             (0x45fcb2, 'audio_uart_display_audio_is_active_45fcb2'))


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
                        '-Wl,-Ttext=0x100000', '-Wl,-e,audio_uart_display_audio_current_45f8e6',
                        str(SRC), '-o', str(elf)], check=True)
        syms = {p[2]: int(p[0], 16) for line in subprocess.check_output(
            ['arm-none-eabi-nm', str(elf)], text=True).splitlines()
            if len(p := line.split()) == 3}
        with elf.open('rb') as f:
            segments = [(s['p_vaddr'], s.data()) for s in ELFFile(f).iter_segments()
                        if s['p_type'] == 'PT_LOAD']

        def run(compiled, index, null_page, first, second, state_a, state_b):
            cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            cpu.mem_map(0x400000, 0x400000)
            cpu.mem_write(0x438000, blob)
            cpu.mem_map(0x100000, 0x100000)
            for address, data in segments:
                cpu.mem_write(address, data)
            cpu.mem_map(0x20000000, 0x400000)
            page, a, b = 0x20011000, 0x20012000, 0x20013000
            for address in (page, a, b): cpu.mem_write(address, bytes(0x100))
            put(cpu, page, a if first else 0)
            put(cpu, page + 4, b if second else 0)
            put(cpu, page + 8, a if first else 0)
            put(cpu, a + 0x20, b if second else 0)
            cpu.mem_write(a + 0x1c, bytes([state_a]))
            cpu.mem_write(b + 0x1c, bytes([state_b]))
            cpu.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
            cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
            cpu.reg_write(A.UC_ARM_REG_R0, 0 if null_page else page)
            address, name = FUNCTIONS[index]
            cpu.emu_start((syms[name] if compiled else address) | 1,
                          0x600000, count=1000)
            return cpu.reg_read(A.UC_ARM_REG_R0)

        cases = list(itertools.product(range(4), (False, True), (False, True),
                                       (False, True), (0, 2), (0, 2)))
        for case in cases:
            native, source = run(False, *case), run(True, *case)
            if native != source:
                raise AssertionError((case, native, source))
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_AUDIO_PAGE_SELECTORS_ORACLE',
               'cases': len(cases), 'source_sha256': hashlib.sha256(SRC.read_bytes()).hexdigest(),
               'payload_sha256': PAYLOAD_SHA, 'hardware_proof': False,
               'scope': 'null and populated pointer slots, active-list traversal and event-state checks'}
    (OUT / 'oracle.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], len(cases))


if __name__ == '__main__': main()
