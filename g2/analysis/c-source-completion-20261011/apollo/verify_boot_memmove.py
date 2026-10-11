#!/usr/bin/env python3
"""Bounded stock/source overlap-copy comparison for Boot 0x4276bc."""
from pathlib import Path
import subprocess
import tempfile

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS
from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_SP

ROOT = Path(__file__).resolve().parents[4]
stock = (ROOT / 'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin').read_bytes()
source = ROOT / 'g2/components/bootloader/runtime_memory/boot_memmove.c'
with tempfile.TemporaryDirectory() as directory:
    directory = Path(directory)
    obj, elfpath = directory / 'memmove.o', directory / 'memmove.elf'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m33', '-mthumb',
                    '-O2', '-ffreestanding', '-fno-builtin',
                    '-c', str(source), '-o', str(obj)], check=True)
    subprocess.run(['arm-none-eabi-ld', '-Ttext=0x500000', '-o', str(elfpath),
                    str(obj)], check=True)
    with elfpath.open('rb') as stream:
        elf = ELFFile(stream)
        symbols = {s.name: s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
        segments = [(p['p_vaddr'], p.data()) for p in elf.iter_segments() if p['p_type'] == 'PT_LOAD']
    cases = 0
    for dst in range(0, 12):
        for src in range(0, 12):
            for size in (0, 1, 2, 3, 4, 5, 7, 8, 15, 16, 17, 31, 32, 33):
                initial = bytes((i * 73 + 19) & 255 for i in range(96))
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
                    cpu.mem_write(0x20001000, initial)
                    cpu.reg_write(UC_ARM_REG_R0, 0x20001000 + dst)
                    cpu.reg_write(UC_ARM_REG_R1, 0x20001000 + src)
                    cpu.reg_write(UC_ARM_REG_R2, size)
                    cpu.reg_write(UC_ARM_REG_SP, 0x2002f000)
                    cpu.reg_write(UC_ARM_REG_LR, 0x50f001)
                    entry = 0x4276bc if native else symbols['opencfw_boot_memmove'] & ~1
                    try:
                        cpu.emu_start(entry | 1, 0x50f000, count=5000)
                    except Exception as exc:
                        raise AssertionError((dst, src, size, native,
                                              hex(cpu.reg_read(UC_ARM_REG_PC)))) from exc
                    results.append((bytes(cpu.mem_read(0x20001000, 96)),
                                    cpu.reg_read(UC_ARM_REG_SP),
                                    cpu.reg_read(UC_ARM_REG_PC)))
                assert results[0] == results[1], (dst, src, size, results)
                cases += 1
    print('PASS_BOOT_MEMMOVE', cases)
