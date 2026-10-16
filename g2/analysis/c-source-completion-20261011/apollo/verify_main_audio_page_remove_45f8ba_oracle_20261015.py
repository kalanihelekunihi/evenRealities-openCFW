#!/usr/bin/env python3
"""Compare stock and C audio removal at the page setter boundary."""
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
SRC = G2 / 'components/audio/uart_thread_source_candidate/display_audio_page_remove_45f8ba.c'
OUT = G2 / 'build/c-firmware/20261015/main-audio-page-remove-45f8ba'
PAYLOAD_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
SHIM = ('#include <stdint.h>\n'
        '__attribute__((noinline)) void audio_uart_page_43ded4(uint32_t a,uint32_t b)'
        '{(void)a;(void)b;}\n')

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
                        '-Wl,-Ttext=0x100000', '-Wl,-e,audio_uart_display_audio_remove_45f8ba',
                        str(SRC), str(shim), '-o', str(elf)], check=True)
        syms = {p[2]: int(p[0], 16) for line in subprocess.check_output(
            ['arm-none-eabi-nm', str(elf)], text=True).splitlines()
            if len(p := line.split()) == 3}
        with elf.open('rb') as f:
            segments = [(s['p_vaddr'], s.data()) for s in ELFFile(f).iter_segments()
                        if s['p_type'] == 'PT_LOAD']

        def run(compiled, present, page, old):
            cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            cpu.mem_map(0x400000, 0x400000)
            cpu.mem_write(0x438000, blob)
            cpu.mem_map(0x100000, 0x100000)
            for address, data in segments:
                cpu.mem_write(address, data)
            cpu.mem_map(0x20000000, 0x400000)
            entry = 0x20012000
            cpu.mem_write(entry, bytes(64))
            cpu.mem_write(entry + 4, page.to_bytes(4, 'little'))
            cpu.mem_write(entry + 28, bytes([old]))
            target = (syms['audio_uart_page_43ded4'] if compiled else 0x43ded4) & ~1
            trace = []
            def hook(cpu, address, size, _):
                if address != target:
                    return
                trace.append((cpu.reg_read(A.UC_ARM_REG_R0), cpu.reg_read(A.UC_ARM_REG_R1)))
                cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
            cpu.hook_add(UC_HOOK_CODE, hook)
            cpu.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
            cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
            cpu.reg_write(A.UC_ARM_REG_R0, entry if present else 0)
            start = syms['audio_uart_display_audio_remove_45f8ba'] if compiled else 0x45f8ba
            cpu.emu_start(start | 1, 0x600000, count=100)
            return trace, bytes(cpu.mem_read(entry, 32))

        cases = 0
        for present, page, old in itertools.product(
                (False, True), (0, 1, 0x12345678, 0xffffffff), (0, 1, 2, 255)):
            stock = run(False, present, page, old)
            rebuilt = run(True, present, page, old)
            if stock != rebuilt:
                raise RuntimeError(f'removal mismatch {present=} {page=} {old=}: {stock} != {rebuilt}')
            cases += 1
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_AUDIO_PAGE_REMOVE_ORACLE',
               'cases': cases, 'source_sha256': hashlib.sha256(SRC.read_bytes()).hexdigest(),
               'payload_sha256': PAYLOAD_SHA, 'stock_entry': '0x45f8ba',
               'limits': ['Page setter is hooked; live page effects are not compared.']}
    (OUT / 'oracle.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], cases)

if __name__ == '__main__': main()
