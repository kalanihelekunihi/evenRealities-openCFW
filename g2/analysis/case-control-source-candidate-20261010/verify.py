#!/usr/bin/env python3
"""Compare original CASE control register effects with compiled C."""
from pathlib import Path
import hashlib
import itertools
import json
import struct
import subprocess
import sys

from elftools.elf.elffile import ELFFile
from unicorn import UC_ARCH_ARM, UC_MODE_MCLASS, UC_MODE_THUMB, UC_HOOK_MEM_WRITE, Uc
from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_SP

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = ROOT / 'g2/components/case/source_candidate_20261010/control_providers.c'
FIRMWARE = ROOT / 'g2/blobs/official/g2-2.2.6.10/firmware_box.bin'
GCC = Path('/tmp/opencfw-arm-gnu/arm-gnu-toolchain-13.3.rel1-darwin-arm64-arm-none-eabi/bin/arm-none-eabi-gcc')
ELF = HERE / 'control.elf'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def execute(entry, args, firmware, segments):
    cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    cpu.mem_map(0x08000000, 0x10000)
    cpu.mem_write(0x08000000, firmware)
    cpu.mem_map(0x00100000, 0x10000)
    for address, data in segments:
        cpu.mem_write(address, data)
    cpu.mem_map(0x20000000, 0x10000)
    cpu.mem_map(0x50000000, 0x1000)
    cpu.mem_write(0x50000018, struct.pack('<I', 0x12345678))
    cpu.mem_write(0x50000028, struct.pack('<I', 0x9abcdef0))
    cpu.reg_write(UC_ARM_REG_SP, 0x20008000)
    cpu.reg_write(UC_ARM_REG_LR, 0x20000001)
    for register, value in zip((UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2), args):
        cpu.reg_write(register, value)
    writes = []
    cpu.hook_add(UC_HOOK_MEM_WRITE, lambda _u, _access, address, size, value, _data:
                 writes.append((address, size, value)) if 0x50000000 <= address < 0x50001000 else None)
    cpu.emu_start(entry | 1, 0x20000000, count=100)
    assert cpu.reg_read(UC_ARM_REG_PC) == 0x20000000
    return {'writes': writes,
            'registers': [struct.unpack('<I', cpu.mem_read(a, 4))[0]
                          for a in (0x50000018, 0x50000028)],
            'stack': cpu.reg_read(UC_ARM_REG_SP)}


def main():
    image = FIRMWARE.read_bytes()
    assert sha(FIRMWARE) == '36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374'
    firmware = image[32:]
    assert hashlib.sha256(firmware).hexdigest() == '773b6d4cfdaf0a5a74a557e3babe8222a0ae813436b76a7437c1096d2c60d677'
    command = [str(GCC), '-mcpu=cortex-m0plus', '-mthumb', '-O2', '-ffreestanding',
               '-fno-builtin', '-nostdlib', '-Wl,-Ttext=0x100000', '-Wl,-e,case_control_a',
               str(SOURCE), '-o', str(ELF)]
    subprocess.run(command, check=True, cwd=ROOT)
    with ELF.open('rb') as stream:
        elf = ELFFile(stream)
        segments = [(segment['p_vaddr'], segment.data()) for segment in elf.iter_segments()
                    if segment['p_type'] == 'PT_LOAD']
        symbols = {symbol.name: symbol['st_value'] for symbol in
                   elf.get_section_by_name('.symtab').iter_symbols()}
    entries = {
        'case_control_a': (0x08006b80, symbols['case_control_a']),
        'case_control_b': (0x08006b98, symbols['case_control_b']),
        'case_control_write': (0x08004e9e, symbols['case_control_write']),
    }
    cases = []
    for name, (original, candidate) in entries.items():
        inputs = ((0x50000000, mask, enable)
                  for mask, enable in itertools.product((0, 0x40, 0x80, 0xffffffff),
                                                        (0, 1, 2, 0xffffffff))) if name == 'case_control_write' else \
                 ((enable, 0, 0) for enable in (0, 1, 2, 0xffffffff))
        for args in inputs:
            actual = execute(original, args, firmware, segments)
            produced = execute(candidate, args, firmware, segments)
            assert actual == produced, (name, args, actual, produced)
            cases.append({'entry': name, 'args': args, 'effects': actual})
    result = {'status': 'PASS', 'cases': len(cases), 'source_sha256': sha(SOURCE),
              'elf_sha256': sha(ELF), 'firmware_sha256': sha(FIRMWARE),
              'compiler_sha256': sha(GCC), 'command': command, 'python': sys.executable,
              'cases_detail': cases,
              'scope': 'Register writes and SP in scalar emulator; physical peripheral effect is unverified.'}
    (HERE / 'results.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'status': 'PASS', 'cases': len(cases)}))


if __name__ == '__main__':
    main()
