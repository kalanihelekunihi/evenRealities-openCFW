#!/usr/bin/env python3
"""Compare original CASE acknowledgement payload with compiled source."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_SP

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = ROOT / 'g2/components/case/source_candidate_20261010/ack_provider.c'
FIRMWARE = ROOT / 'g2/blobs/official/g2-2.2.6.10/firmware_box.bin'
GCC = Path('/tmp/opencfw-arm-gnu/arm-gnu-toolchain-13.3.rel1-darwin-arm64-arm-none-eabi/bin/arm-none-eabi-gcc')
ELF = HERE / 'ack.elf'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def execute(entry, child, value, firmware, segments):
    cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    cpu.mem_map(0x08000000, 0x10000)
    cpu.mem_write(0x08000000, firmware)
    cpu.mem_map(0x00100000, 0x10000)
    for address, data in segments:
        cpu.mem_write(address, data)
    cpu.mem_map(0x20000000, 0x10000)
    cpu.reg_write(UC_ARM_REG_SP, 0x20008000)
    cpu.reg_write(UC_ARM_REG_LR, 0x20000001)
    cpu.reg_write(UC_ARM_REG_R0, value)
    calls = []

    def intercept(machine, address, size, _):
        if address != child:
            return
        pointer = machine.reg_read(UC_ARM_REG_R0)
        length = machine.reg_read(UC_ARM_REG_R1)
        assert length == 5
        calls.append({'length': length, 'payload': bytes(machine.mem_read(pointer, length)).hex()})
        machine.reg_write(UC_ARM_REG_PC, machine.reg_read(UC_ARM_REG_LR))

    cpu.hook_add(UC_HOOK_CODE, intercept)
    cpu.emu_start(entry | 1, 0x20000000, count=200)
    assert cpu.reg_read(UC_ARM_REG_PC) == 0x20000000
    assert len(calls) == 1
    return calls, cpu.reg_read(UC_ARM_REG_SP)


def main():
    image = FIRMWARE.read_bytes()
    assert sha(FIRMWARE) == '36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374'
    firmware = image[32:]
    assert hashlib.sha256(firmware).hexdigest() == '773b6d4cfdaf0a5a74a557e3babe8222a0ae813436b76a7437c1096d2c60d677'
    assert firmware[0x68e8:0x68f0].hex() == '0001030100000000'
    command = [str(GCC), '-mcpu=cortex-m0plus', '-mthumb', '-O2', '-ffreestanding',
               '-fno-builtin', '-nostdlib', '-Wl,-Ttext=0x100000',
               '-Wl,-e,case_ack', '-Wl,--defsym=case_send=0x00100f01',
               str(SOURCE), '-o', str(ELF)]
    subprocess.run(command, cwd=ROOT, check=True)
    with ELF.open('rb') as stream:
        elf = ELFFile(stream)
        segments = [(segment['p_vaddr'], segment.data()) for segment in elf.iter_segments()
                    if segment['p_type'] == 'PT_LOAD']
        symbols = {symbol.name: symbol['st_value'] for symbol in
                   elf.get_section_by_name('.symtab').iter_symbols()}
    values = [*range(256), 0x100, 0x15d, 0x10000, 0xffffffff]
    for value in values:
        original = execute(0x080068d0, 0x0800680c, value, firmware, segments)
        candidate = execute(symbols['case_ack'], 0x00100f00, value, firmware, segments)
        assert original == candidate, (value, original, candidate)
        assert original[0][0]['payload'] == bytes([value & 0xff, 1, 3, 1, 0]).hex()
    result = {'status': 'PASS', 'cases': len(values), 'source_sha256': sha(SOURCE),
              'elf_sha256': sha(ELF), 'compiler_sha256': sha(GCC), 'command': command,
              'firmware_sha256': sha(FIRMWARE), 'python': sys.executable,
              'scope': 'Payload bytes, send length and restored SP; send transport is an explicit child boundary.'}
    (HERE / 'results.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'status': 'PASS', 'cases': len(values)}))


if __name__ == '__main__':
    main()
