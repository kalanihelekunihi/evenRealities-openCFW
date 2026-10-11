#!/usr/bin/env python3
"""Bounded original/source unsigned 64-bit divide-by-ten ABI oracle."""
from pathlib import Path
import random
import subprocess
import tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS
from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_SP

ROOT = Path(__file__).resolve().parents[4]
stock = (ROOT / 'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin').read_bytes()
source = ROOT / 'g2/components/bootloader/runtime_memory/boot_u64_div10.c'
with tempfile.TemporaryDirectory() as directory:
    directory = Path(directory)
    obj, elfpath = directory / 'div10.o', directory / 'div10.elf'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m33', '-mthumb',
                    '-O2', '-ffreestanding', '-fno-builtin', '-c', str(source),
                    '-o', str(obj)], check=True)
    assert not subprocess.check_output(['arm-none-eabi-nm', '-u', str(obj)]).strip()
    subprocess.run(['arm-none-eabi-ld', '-e', 'opencfw_boot_u64_div10', '-Ttext=0x500000',
                    '-o', str(elfpath), str(obj)], check=True)
    with elfpath.open('rb') as stream:
        elf = ELFFile(stream)
        symbol = next(s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()
                      if s.name == 'opencfw_boot_u64_div10')
        segments = [(p['p_vaddr'], p.data()) for p in elf.iter_segments() if p['p_type'] == 'PT_LOAD']
    values = [0, 1, 9, 10, 15, 16, 19, 20, 99, 100, 0xffffffff,
              0x100000000, 0xffffffffffffffff, 0x8000000000000000]
    rng = random.Random(0x415844)
    values.extend(rng.getrandbits(64) for _ in range(2000))
    for value in values:
        results = []
        for native in (True, False):
            cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
            cpu.mem_map(0x410000, 0x40000)
            cpu.mem_write(0x410000, stock)
            cpu.mem_map(0x500000, 0x10000)
            if not native:
                for address, payload in segments:
                    cpu.mem_write(address, payload)
            cpu.mem_map(0x20000000, 0x30000)
            cpu.reg_write(UC_ARM_REG_R0, value & 0xffffffff)
            cpu.reg_write(UC_ARM_REG_R1, value >> 32)
            cpu.reg_write(UC_ARM_REG_SP, 0x2002f000)
            cpu.reg_write(UC_ARM_REG_LR, 0x50f001)
            cpu.emu_start((0x415844 if native else symbol & ~1) | 1,
                          0x50f000, count=2000)
            results.append((cpu.reg_read(UC_ARM_REG_R0), cpu.reg_read(UC_ARM_REG_R1),
                            cpu.reg_read(UC_ARM_REG_SP), cpu.reg_read(UC_ARM_REG_PC)))
        assert results[0] == results[1], (hex(value), results)
        assert (results[0][1] << 32 | results[0][0]) == value // 10
    print('PASS_BOOT_U64_DIV10', len(values))
