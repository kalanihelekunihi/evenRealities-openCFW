#!/usr/bin/env python3
"""Compare Apollo owner walk against pinned stock Thumb code."""
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
SRC = G2 / 'components/audio/uart_thread_source_candidate/display_audio_find_owner_45fcd2.c'
OUT = G2 / 'build/c-firmware/20261015/main-audio-find-owner-45fcd2'
PAYLOAD_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
SHIM = ('#include <stdint.h>\n'
        '__attribute__((noinline)) void *audio_uart_lv_obj_parent_44dca2(void*a)'
        '{(void)a;return 0;}\n')

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
                        '-Wl,-Ttext=0x100000', '-Wl,-e,audio_uart_display_audio_find_owner_45fcd2',
                        str(SRC), str(shim), '-o', str(elf)], check=True)
        syms = {p[2]: int(p[0], 16) for line in subprocess.check_output(
            ['arm-none-eabi-nm', str(elf)], text=True).splitlines()
            if len(p := line.split()) == 3}
        with elf.open('rb') as f:
            segments = [(s['p_vaddr'], s.data()) for s in ELFFile(f).iter_segments()
                        if s['p_type'] == 'PT_LOAD']

        def run(compiled, object_valid, first_valid, second_valid,
                first_candidate, second_candidate, first_match, second_match):
            cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            cpu.mem_map(0x400000, 0x400000)
            cpu.mem_write(0x438000, blob)
            cpu.mem_map(0x100000, 0x100000)
            for address, data in segments:
                cpu.mem_write(address, data)
            cpu.mem_map(0x20000000, 0x400000)
            obj, first, second, c1, c2 = (0x20011000, 0x20012000, 0x20013000,
                                          0x20014000, 0x20015000)
            for address in (obj, first, second, c1, c2):
                cpu.mem_write(address, bytes(64))
            put(cpu, first + 16, c1 if first_candidate else 0)
            put(cpu, second + 16, c2 if second_candidate else 0)
            put(cpu, c1 + 24, first if first_match else second)
            put(cpu, c2 + 24, second if second_match else first)
            target = (syms['audio_uart_lv_obj_parent_44dca2'] if compiled else 0x44dca2) & ~1
            trace = []
            def hook(cpu, address, size, _):
                if address != target:
                    return
                arg = cpu.reg_read(A.UC_ARM_REG_R0)
                trace.append(arg)
                result = (first if first_valid else 0) if arg == obj else (
                    second if second_valid else 0) if arg == first else 0
                cpu.reg_write(A.UC_ARM_REG_R0, result)
                cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
            cpu.hook_add(UC_HOOK_CODE, hook)
            cpu.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
            cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
            cpu.reg_write(A.UC_ARM_REG_R0, obj if object_valid else 0)
            start = syms['audio_uart_display_audio_find_owner_45fcd2'] if compiled else 0x45fcd2
            cpu.emu_start(start | 1, 0x600000, count=150)
            return cpu.reg_read(A.UC_ARM_REG_R0), trace

        cases = 0
        for args in itertools.product((False, True), repeat=7):
            stock, rebuilt = run(False, *args), run(True, *args)
            if stock != rebuilt:
                raise RuntimeError(f'owner mismatch {args}: {stock} != {rebuilt}')
            cases += 1
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_AUDIO_FIND_OWNER_ORACLE',
               'cases': cases, 'source_sha256': hashlib.sha256(SRC.read_bytes()).hexdigest(),
               'payload_sha256': PAYLOAD_SHA, 'stock_entry': '0x45fcd2',
               'limits': ['Parent lookup is hooked; live object graph remains open.']}
    (OUT / 'oracle.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], cases)

if __name__ == '__main__': main()
