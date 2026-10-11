#!/usr/bin/env python3
"""Bounded stock/source MSPI status getter 0x4264ba comparison."""
from pathlib import Path
import struct
import subprocess
import tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS
from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_SP

ROOT = Path(__file__).resolve().parents[4]
stock = (ROOT / 'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin').read_bytes()
source = ROOT / 'g2/components/bootloader/source_candidate_20261010/mspi_interrupt_status.c'
with tempfile.TemporaryDirectory() as directory:
    directory = Path(directory)
    obj, elfpath = directory / 'status.o', directory / 'status.elf'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m33', '-mthumb',
                    '-O2', '-ffreestanding', '-fno-builtin', '-I',
                    str(ROOT / 'g2/components/foundation/ambiq_mspi'), '-c', str(source),
                    '-o', str(obj)], check=True)
    assert not subprocess.check_output(['arm-none-eabi-nm', '-u', str(obj)]).strip()
    subprocess.run(['arm-none-eabi-ld', '-e', 'am_hal_mspi_interrupt_status_get',
                    '-Ttext=0x500000', '-o', str(elfpath), str(obj)], check=True)
    with elfpath.open('rb') as stream:
        elf = ELFFile(stream)
        symbol = next(s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()
                      if s.name == 'am_hal_mspi_interrupt_status_get')
        segments = [(p['p_vaddr'], p.data()) for p in elf.iter_segments() if p['p_type'] == 'PT_LOAD']
    cases = 0
    for handle in (0, 0x20001000):
        for magic in (0, 0x01bebebe, 0x03bebebe):
            for enabled in (0, 1):
                pair = []
                for native in (True, False):
                    cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
                    cpu.mem_map(0x410000, 0x40000)
                    cpu.mem_write(0x410000, stock)
                    cpu.mem_map(0x500000, 0x10000)
                    if not native:
                        for address, payload in segments:
                            cpu.mem_write(address, payload)
                    cpu.mem_map(0x20000000, 0x30000)
                    cpu.mem_map(0x40060000, 0x1000)
                    cpu.mem_write(0x20001000, struct.pack('<II', magic, 0))
                    cpu.mem_write(0x20002000, struct.pack('<I', 0xdeadbeef))
                    cpu.mem_write(0x40060200, struct.pack('<I', 0x00ff00ff))
                    cpu.mem_write(0x40060204, struct.pack('<I', 0x12345678))
                    cpu.reg_write(UC_ARM_REG_R0, handle)
                    cpu.reg_write(UC_ARM_REG_R1, 0x20002000)
                    cpu.reg_write(UC_ARM_REG_R2, enabled)
                    cpu.reg_write(UC_ARM_REG_SP, 0x2002f000)
                    cpu.reg_write(UC_ARM_REG_LR, 0x50f001)
                    cpu.emu_start((0x4264ba if native else symbol & ~1) | 1,
                                  0x50f000, count=500)
                    pair.append((cpu.reg_read(UC_ARM_REG_R0),
                                 bytes(cpu.mem_read(0x20002000, 4)),
                                 cpu.reg_read(UC_ARM_REG_SP), cpu.reg_read(UC_ARM_REG_PC)))
                assert pair[0] == pair[1], (handle, magic, enabled, pair)
                cases += 1
    print('PASS_BOOT_MSPI_IRQ_STATUS', cases)
