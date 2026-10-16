#!/usr/bin/env python3
"""Compare Apollo audio entry activation and state transitions."""
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
SRC = G2 / 'components/audio/uart_thread_source_candidate/display_audio_page_activate_45f60e.c'
OUT = G2 / 'build/c-firmware/20261015/main-audio-page-activate-45f60e'
PAYLOAD_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
CALLS = {'find': (0x45f840, 'audio_uart_display_audio_find_45f840'),
         'remove': (0x45f8ba, 'audio_uart_display_audio_remove_45f8ba'),
         'start': (0x45ef24, 'audio_uart_display_audio_start_45ef24')}
SHIM = '#include <stdint.h>\n' + '\n'.join(
    f'__attribute__((noinline)) uint32_t {name}(void*a,uint32_t b)'
    '{(void)a;(void)b;return 0;}' for _, name in CALLS.values()) + '\n'


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
                        '-Wl,-Ttext=0x100000', '-Wl,-e,audio_uart_display_audio_activate_45f60e',
                        str(SRC), str(shim), '-o', str(elf)], check=True)
        syms = {p[2]: int(p[0], 16) for line in subprocess.check_output(
            ['arm-none-eabi-nm', str(elf)], text=True).splitlines()
            if len(p := line.split()) == 3}
        with elf.open('rb') as f:
            segments = [(s['p_vaddr'], s.data()) for s in ELFFile(f).iter_segments()
                        if s['p_type'] == 'PT_LOAD']

        def run(compiled, entry_state, entry_flag, first, second,
                busy, id_valid, found):
            cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            cpu.mem_map(0x400000, 0x400000)
            cpu.mem_write(0x438000, blob)
            cpu.mem_map(0x100000, 0x100000)
            for address, data in segments:
                cpu.mem_write(address, data)
            cpu.mem_map(0x20000000, 0x400000)
            state, entry, other = 0x20011000, 0x20012000, 0x20013000
            for address in (state, entry, other): cpu.mem_write(address, bytes(0x100))
            put(cpu, state, entry if first else other)
            put(cpu, state + 4, entry if second else other)
            put(cpu, state + 12, other)
            cpu.mem_write(state + 20, bytes([busy]))
            cpu.mem_write(entry + 11, bytes([entry_flag]))
            cpu.mem_write(entry + 0x1c, bytes([entry_state]))
            targets = {(syms[name] if compiled else address) & ~1: key
                       for key, (address, name) in CALLS.items()}
            trace = []
            def hook(cpu, address, size, _):
                key = targets.get(address)
                if key is None:
                    return
                r0, r1 = cpu.reg_read(A.UC_ARM_REG_R0), cpu.reg_read(A.UC_ARM_REG_R1)
                trace.append((key, r0, r1 if key in ('find', 'start') else 0))
                cpu.reg_write(A.UC_ARM_REG_R0, entry if key == 'find' and found else 0)
                cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
            cpu.hook_add(UC_HOOK_CODE, hook)
            cpu.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
            cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
            cpu.reg_write(A.UC_ARM_REG_R0, state)
            cpu.reg_write(A.UC_ARM_REG_R1, 0x42 if id_valid else 0)
            start = syms['audio_uart_display_audio_activate_45f60e'] if compiled else 0x45f60e
            cpu.emu_start(start | 1, 0x600000, count=1000)
            return trace, bytes(cpu.mem_read(state, 24)), bytes(cpu.mem_read(entry, 36))

        cases = list(itertools.product((0, 1, 2), (0, 1), (False, True),
                                       (False, True), (0, 1), (False, True),
                                       (False, True)))
        for case in cases:
            native, source = run(False, *case), run(True, *case)
            if native != source:
                raise AssertionError((case, native, source))
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_AUDIO_PAGE_ACTIVATE_ORACLE',
               'cases': len(cases), 'source_sha256': hashlib.sha256(SRC.read_bytes()).hexdigest(),
               'payload_sha256': PAYLOAD_SHA, 'hardware_proof': False,
               'scope': 'entry state, control flag, current/head slots, busy flag and child calls'}
    (OUT / 'oracle.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], len(cases))


if __name__ == '__main__': main()
