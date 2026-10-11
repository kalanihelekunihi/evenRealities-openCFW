#!/usr/bin/env python3
"""Compare CASE task event-clear path with compiled source critical helpers."""
from pathlib import Path
import hashlib
import itertools
import json
import struct
import subprocess

from elftools.elf.elffile import ELFFile
from unicorn import UC_ARCH_ARM, UC_MODE_MCLASS, UC_MODE_THUMB, Uc
from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_PRIMASK, UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_SP

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = ROOT / 'g2/components/case/source_candidate_20261010/event_clear_task.c'
CRITICAL = ROOT / 'g2/components/case/source_candidate_20261010/critical_providers.c'
FIRMWARE = ROOT / 'g2/blobs/official/g2-2.2.6.10/firmware_box.bin'
GCC = Path('/tmp/opencfw-arm-gnu/arm-gnu-toolchain-13.3.rel1-darwin-arm64-arm-none-eabi/bin/arm-none-eabi-gcc')
ELF = HERE / 'event_clear_task.elf'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def execute(entry, group, before, bits, nest, mask, raw, segments, limited=False):
    cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    cpu.mem_map(0x08000000, 0x10000)
    cpu.mem_write(0x08000000, raw)
    cpu.mem_map(0x00100000, 0x10000)
    for address, data in segments:
        cpu.mem_write(address, data)
    cpu.mem_map(0x20000000, 0x10000)
    cpu.mem_write(0x20005000, struct.pack('<I', before))
    cpu.mem_write(0x2000019c, struct.pack('<I', nest))
    cpu.reg_write(UC_ARM_REG_SP, 0x20008000)
    cpu.reg_write(UC_ARM_REG_LR, 0x20000001)
    cpu.reg_write(UC_ARM_REG_R0, group)
    cpu.reg_write(UC_ARM_REG_R1, bits)
    cpu.reg_write(UC_ARM_REG_PRIMASK, mask)
    cpu.emu_start(entry | 1, 0x20000000, count=40 if limited else 400)
    pc = cpu.reg_read(UC_ARM_REG_PC)
    return (pc == 0x20000000, cpu.reg_read(UC_ARM_REG_R0) if not limited else None,
            struct.unpack('<I', cpu.mem_read(0x20005000, 4))[0],
            struct.unpack('<I', cpu.mem_read(0x2000019c, 4))[0],
            cpu.reg_read(UC_ARM_REG_PRIMASK), cpu.reg_read(UC_ARM_REG_SP))


def main():
    image = FIRMWARE.read_bytes()
    assert sha(FIRMWARE) == '36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374'
    raw = image[32:]
    assert hashlib.sha256(raw).hexdigest() == '773b6d4cfdaf0a5a74a557e3babe8222a0ae813436b76a7437c1096d2c60d677'
    command = [str(GCC), '-mcpu=cortex-m0plus', '-mthumb', '-O2', '-ffreestanding',
               '-fno-builtin', '-nostdlib', '-Wl,-Ttext=0x100000',
               '-Wl,-e,xEventGroupClearBits', str(SOURCE), str(CRITICAL), '-o', str(ELF)]
    subprocess.run(command, cwd=ROOT, check=True)
    with ELF.open('rb') as stream:
        elf = ELFFile(stream)
        segments = [(segment['p_vaddr'], segment.data()) for segment in elf.iter_segments()
                    if segment['p_type'] == 'PT_LOAD']
        symbols = {symbol.name: symbol['st_value'] for symbol in
                   elf.get_section_by_name('.symtab').iter_symbols()}
    entry = symbols['xEventGroupClearBits']
    count = 0
    for before, bits, nest, mask in itertools.product(
            (0, 0xf0, 0xffffff), (0, 1, 0xff, 0xffffff), (0, 1, 2), (0, 1)):
        original = execute(0x0800c44c, 0x20005000, before, bits, nest, mask, raw, segments)
        candidate = execute(entry, 0x20005000, before, bits, nest, mask, raw, segments)
        assert original == candidate, (before, bits, nest, mask, original, candidate)
        assert original[0] and original[1] == before
        count += 1
    invalid = 0
    for group, bits in ((0, 0), (0, 1), (0x20005000, 0x1000000),
                        (0x20005000, 0xffffffff)):
        original = execute(0x0800c44c, group, 0xf0, bits, 0, 0, raw, segments, limited=True)
        candidate = execute(entry, group, 0xf0, bits, 0, 0, raw, segments, limited=True)
        assert original[0] is False and candidate[0] is False
        assert original[2:5] == candidate[2:5] == (0xf0, 0, 1)
        invalid += 1
    result = {'status': 'PASS', 'returning_cases': count, 'nonreturning_prefix_cases': invalid,
              'original_extent_bytes': 42, 'firmware_sha256': sha(FIRMWARE),
              'source_sha256': sha(SOURCE), 'critical_source_sha256': sha(CRITICAL),
              'compiler_sha256': sha(GCC), 'elf_sha256': sha(ELF), 'command': command,
              'scope': 'Full valid-path state and bounded invalid nonreturn prefix; no physical concurrency.'}
    (HERE / 'results.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'status': 'PASS', 'returning': count, 'nonreturning_prefix': invalid}))


if __name__ == '__main__':
    main()
