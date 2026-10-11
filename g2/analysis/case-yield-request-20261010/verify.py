#!/usr/bin/env python3
"""Compare original and compiled CASE PendSV request effects."""
from pathlib import Path
import hashlib
import json
import struct
import subprocess

from elftools.elf.elffile import ELFFile
from unicorn import UC_ARCH_ARM, UC_HOOK_MEM_WRITE, UC_MODE_MCLASS, UC_MODE_THUMB, Uc
from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_PRIMASK, UC_ARM_REG_R0, UC_ARM_REG_SP

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = ROOT / 'g2/components/case/source_candidate_20261010/yield_request.c'
FIRMWARE = ROOT / 'g2/blobs/official/g2-2.2.6.10/firmware_box.bin'
GCC = Path('/tmp/opencfw-arm-gnu/arm-gnu-toolchain-13.3.rel1-darwin-arm64-arm-none-eabi/bin/arm-none-eabi-gcc')
ELF = HERE / 'yield_request.elf'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def execute(entry, arg0, mask, raw, segments):
    cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    cpu.mem_map(0x08000000, 0x10000)
    cpu.mem_write(0x08000000, raw)
    cpu.mem_map(0x00100000, 0x10000)
    for address, data in segments:
        cpu.mem_write(address, data)
    cpu.mem_map(0x20000000, 0x10000)
    cpu.mem_map(0xe000e000, 0x1000)
    cpu.reg_write(UC_ARM_REG_SP, 0x20008000)
    cpu.reg_write(UC_ARM_REG_LR, 0x20000001)
    cpu.reg_write(UC_ARM_REG_R0, arg0)
    cpu.reg_write(UC_ARM_REG_PRIMASK, mask)
    writes = []
    cpu.hook_add(UC_HOOK_MEM_WRITE, lambda _u, _access, address, size, value, _data:
                 writes.append((address, size, value)) if address == 0xe000ed04 else None)
    cpu.emu_start(entry | 1, 0x20000000, count=100)
    assert cpu.reg_read(UC_ARM_REG_PC) == 0x20000000
    return (writes, cpu.reg_read(UC_ARM_REG_R0), cpu.reg_read(UC_ARM_REG_PRIMASK),
            cpu.reg_read(UC_ARM_REG_SP), bytes(cpu.mem_read(0xe000ed04, 4)))


def main():
    image = FIRMWARE.read_bytes()
    assert sha(FIRMWARE) == '36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374'
    raw = image[32:]
    assert hashlib.sha256(raw).hexdigest() == '773b6d4cfdaf0a5a74a557e3babe8222a0ae813436b76a7437c1096d2c60d677'
    assert struct.unpack_from('<I', raw, 0xc0b4)[0] == 0xe000ed00
    command = [str(GCC), '-mcpu=cortex-m0plus', '-mthumb', '-O2', '-ffreestanding',
               '-fno-builtin', '-nostdlib', '-Wl,-Ttext=0x100000', '-Wl,-e,case_yield_request',
               str(SOURCE), '-o', str(ELF)]
    subprocess.run(command, cwd=ROOT, check=True)
    with ELF.open('rb') as stream:
        elf = ELFFile(stream)
        segments = [(segment['p_vaddr'], segment.data()) for segment in elf.iter_segments()
                    if segment['p_type'] == 'PT_LOAD']
        symbols = {symbol.name: symbol['st_value'] for symbol in
                   elf.get_section_by_name('.symtab').iter_symbols()}
    count = 0
    for arg0 in (0, 1, 0xffffffff):
        for mask in (0, 1):
            original = execute(0x0800c0a0, arg0, mask, raw, segments)
            candidate = execute(symbols['case_yield_request'], arg0, mask, raw, segments)
            assert original == candidate, (arg0, mask, original, candidate)
            assert original[0] == [(0xe000ed04, 4, 0x10000000)]
            count += 1
    result = {'status': 'PASS', 'cases': count, 'original_extent_bytes': 18,
              'firmware_sha256': sha(FIRMWARE), 'source_sha256': sha(SOURCE),
              'compiler_sha256': sha(GCC), 'elf_sha256': sha(ELF), 'command': command,
              'scope': 'ICSR write, return register, PRIMASK and SP; physical PendSV handling unverified.'}
    (HERE / 'results.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'status': 'PASS', 'cases': count}))


if __name__ == '__main__':
    main()
