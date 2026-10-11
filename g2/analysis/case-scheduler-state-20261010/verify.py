#!/usr/bin/env python3
"""Compare CASE scheduler state source and original body."""
from pathlib import Path
import hashlib
import itertools
import json
import struct
import subprocess

from elftools.elf.elffile import ELFFile
from unicorn import UC_ARCH_ARM, UC_MODE_MCLASS, UC_MODE_THUMB, Uc
from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0, UC_ARM_REG_SP

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = ROOT / 'g2/components/case/source_candidate_20261010/scheduler_state.c'
FIRMWARE = ROOT / 'g2/blobs/official/g2-2.2.6.10/firmware_box.bin'
GCC = Path('/tmp/opencfw-arm-gnu/arm-gnu-toolchain-13.3.rel1-darwin-arm64-arm-none-eabi/bin/arm-none-eabi-gcc')
ELF = HERE / 'scheduler_state.elf'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def execute(entry, active, suspended, raw, segments):
    cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    cpu.mem_map(0x08000000, 0x10000)
    cpu.mem_write(0x08000000, raw)
    cpu.mem_map(0x00100000, 0x10000)
    for address, data in segments:
        cpu.mem_write(address, data)
    cpu.mem_map(0x20000000, 0x10000)
    cpu.mem_write(0x2000013c, struct.pack('<I', active))
    cpu.mem_write(0x20000158, struct.pack('<I', suspended))
    cpu.reg_write(UC_ARM_REG_SP, 0x20008000)
    cpu.reg_write(UC_ARM_REG_LR, 0x20000001)
    cpu.emu_start(entry | 1, 0x20000000, count=100)
    assert cpu.reg_read(UC_ARM_REG_PC) == 0x20000000
    return (cpu.reg_read(UC_ARM_REG_R0), cpu.reg_read(UC_ARM_REG_SP),
            bytes(cpu.mem_read(0x20000128, 0x34)))


def main():
    image = FIRMWARE.read_bytes()
    assert sha(FIRMWARE) == '36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374'
    raw = image[32:]
    assert hashlib.sha256(raw).hexdigest() == '773b6d4cfdaf0a5a74a557e3babe8222a0ae813436b76a7437c1096d2c60d677'
    assert struct.unpack_from('<I', raw, 0xca68)[0] == 0x20000128
    command = [str(GCC), '-mcpu=cortex-m0plus', '-mthumb', '-O2', '-ffreestanding',
               '-fno-builtin', '-nostdlib', '-Wl,-Ttext=0x100000',
               '-Wl,-e,case_scheduler_state', str(SOURCE), '-o', str(ELF)]
    subprocess.run(command, cwd=ROOT, check=True)
    with ELF.open('rb') as stream:
        elf = ELFFile(stream)
        segments = [(segment['p_vaddr'], segment.data()) for segment in elf.iter_segments()
                    if segment['p_type'] == 'PT_LOAD']
        symbols = {symbol.name: symbol['st_value'] for symbol in
                   elf.get_section_by_name('.symtab').iter_symbols()}
    cases = []
    for active, suspended in itertools.product((0, 1, 0xffffffff), repeat=2):
        original = execute(0x0800ca4c, active, suspended, raw, segments)
        candidate = execute(symbols['case_scheduler_state'], active, suspended, raw, segments)
        assert original == candidate, (active, suspended, original, candidate)
        cases.append({'active': active, 'suspended': suspended, 'return': original[0]})
    result = {'status': 'PASS', 'cases': len(cases), 'original_extent_bytes': 26,
              'firmware_sha256': sha(FIRMWARE), 'source_sha256': sha(SOURCE),
              'compiler_sha256': sha(GCC), 'elf_sha256': sha(ELF), 'command': command,
              'results': cases,
              'scope': 'Scheduler state return, RAM and stack; state writers and scheduling are separate.'}
    (HERE / 'results.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'status': 'PASS', 'cases': len(cases)}))


if __name__ == '__main__':
    main()
