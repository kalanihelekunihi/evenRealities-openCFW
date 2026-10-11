#!/usr/bin/env python3
"""Compare CASE deferred event-clear wrapper call contract with compiled C."""
from pathlib import Path
import hashlib
import json
import struct
import subprocess

from elftools.elf.elffile import ELFFile
from unicorn import UC_ARCH_ARM, UC_HOOK_CODE, UC_MODE_MCLASS, UC_MODE_THUMB, Uc
from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3, UC_ARM_REG_SP

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = ROOT / 'g2/components/case/source_candidate_20261010/event_clear_isr.c'
FIRMWARE = ROOT / 'g2/blobs/official/g2-2.2.6.10/firmware_box.bin'
GCC = Path('/tmp/opencfw-arm-gnu/arm-gnu-toolchain-13.3.rel1-darwin-arm64-arm-none-eabi/bin/arm-none-eabi-gcc')
ELF = HERE / 'event_clear_isr.elf'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def execute(entry, child, callback, event, bits, result, raw, segments):
    cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    cpu.mem_map(0x08000000, 0x10000)
    cpu.mem_write(0x08000000, raw)
    cpu.mem_map(0x00100000, 0x10000)
    for address, data in segments:
        cpu.mem_write(address, data)
    cpu.mem_map(0x20000000, 0x10000)
    cpu.reg_write(UC_ARM_REG_SP, 0x20008000)
    cpu.reg_write(UC_ARM_REG_LR, 0x20000001)
    cpu.reg_write(UC_ARM_REG_R0, event)
    cpu.reg_write(UC_ARM_REG_R1, bits)
    calls = []

    def intercept(machine, address, _size, _):
        if address != child:
            return
        values = [machine.reg_read(reg) for reg in
                  (UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3)]
        assert values[0] == callback, values
        calls.append(('timer_pend_isr', *values[1:]))
        machine.reg_write(UC_ARM_REG_R0, result)
        machine.reg_write(UC_ARM_REG_PC, machine.reg_read(UC_ARM_REG_LR))

    cpu.hook_add(UC_HOOK_CODE, intercept)
    cpu.emu_start(entry | 1, 0x20000000, count=200)
    assert cpu.reg_read(UC_ARM_REG_PC) == 0x20000000
    assert len(calls) == 1
    return calls, cpu.reg_read(UC_ARM_REG_R0), cpu.reg_read(UC_ARM_REG_SP)


def main():
    image = FIRMWARE.read_bytes()
    assert sha(FIRMWARE) == '36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374'
    raw = image[32:]
    assert hashlib.sha256(raw).hexdigest() == '773b6d4cfdaf0a5a74a557e3babe8222a0ae813436b76a7437c1096d2c60d677'
    assert struct.unpack_from('<I', raw, 0xc488)[0] == 0x0800bf85
    command = [str(GCC), '-mcpu=cortex-m0plus', '-mthumb', '-O2', '-ffreestanding',
               '-fno-builtin', '-nostdlib', '-Wl,-Ttext=0x100000',
               '-Wl,-e,xEventGroupClearBitsFromISR',
               '-Wl,--defsym=xTimerPendFunctionCallFromISR=0x00100f01',
               '-Wl,--defsym=vEventGroupClearBitsCallback=0x00100f11',
               str(SOURCE), '-o', str(ELF)]
    subprocess.run(command, cwd=ROOT, check=True)
    with ELF.open('rb') as stream:
        elf = ELFFile(stream)
        segments = [(segment['p_vaddr'], segment.data()) for segment in elf.iter_segments()
                    if segment['p_type'] == 'PT_LOAD']
        symbols = {symbol.name: symbol['st_value'] for symbol in
                   elf.get_section_by_name('.symtab').iter_symbols()}
    cases = []
    for event in (0, 0x20005000):
        for bits in (0, 1, 0x800000, 0xffffffff):
            for result in (0, 1, 0xffffffff):
                original = execute(0x0800c478, 0x0800ce0c, 0x0800bf85,
                                   event, bits, result, raw, segments)
                candidate = execute(symbols['xEventGroupClearBitsFromISR'],
                                    0x00100f00, 0x00100f11,
                                    event, bits, result, raw, segments)
                assert original == candidate, (event, bits, result, original, candidate)
                cases.append({'event': event, 'bits': bits, 'child_result': result})
    result = {'status': 'PASS', 'cases': len(cases), 'original_extent_bytes': 20,
              'firmware_sha256': sha(FIRMWARE), 'source_sha256': sha(SOURCE),
              'compiler_sha256': sha(GCC), 'elf_sha256': sha(ELF), 'command': command,
              'results': cases,
              'scope': 'Deferred-call argument/return contract; timer queue and callback bodies external.'}
    (HERE / 'results.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'status': 'PASS', 'cases': len(cases)}))


if __name__ == '__main__':
    main()
