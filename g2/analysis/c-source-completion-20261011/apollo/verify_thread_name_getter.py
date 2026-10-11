#!/usr/bin/env python3
"""Bounded native/source comparison for the stock 0x418372 TCB name accessor."""
from pathlib import Path
import struct
import subprocess
import tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS
from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0, UC_ARM_REG_SP

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
stock = (ROOT / 'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin').read_bytes()
source = ROOT / 'g2/components/bootloader/thread_creation/thread_name_getter.c'

with tempfile.TemporaryDirectory() as temp:
    temp = Path(temp)
    obj = temp / 'name.o'
    stub = temp / 'stub.S'
    stubobj = temp / 'stub.o'
    elfpath = temp / 'name.elf'
    cc = ['/usr/bin/clang', '--target=arm-none-eabi', '-mcpu=cortex-m33', '-mthumb']
    subprocess.run(cc + ['-O2', '-ffreestanding', '-fno-builtin', '-c', str(source), '-o', str(obj)], check=True)
    stub.write_text('.syntax unified\n.thumb\n.text\n.global opencfw_bl_mask_interrupts\n.thumb_func\nopencfw_bl_mask_interrupts:\nbx lr\n')
    subprocess.run(cc + ['-c', str(stub), '-o', str(stubobj)], check=True)
    subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld', '-Ttext=0x00500000',
                    str(obj), str(stubobj), '-o', str(elfpath)], check=True)
    with elfpath.open('rb') as stream:
        elf = ELFFile(stream)
        entry = next(s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()
                     if s.name == 'opencfw_boot_thread_name_get') & ~1
        segments = [(s['p_vaddr'], s.data()) for s in elf.iter_segments() if s['p_type'] == 'PT_LOAD']

    for label, argument, current, expected in [
        ('explicit', 0x20010000, 0, 0x20010034),
        ('current', 0, 0x20010100, 0x20010134),
        ('explicit-over-current', 0x20010000, 0x20010100, 0x20010034),
    ]:
        results = []
        for native in (True, False):
            u = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
            u.mem_map(0x00410000, 0x40000)
            u.mem_write(0x00410000, stock)
            u.mem_map(0x00500000, 0x10000)
            if not native:
                for address, data in segments:
                    u.mem_write(address, data)
            u.mem_map(0x20000000, 0x30000)
            u.mem_write(0x20027134, struct.pack('<I', current))
            u.reg_write(UC_ARM_REG_R0, argument)
            u.reg_write(UC_ARM_REG_SP, 0x2002f000)
            u.reg_write(UC_ARM_REG_LR, 0x0050f001)
            u.emu_start((0x00418372 if native else entry) | 1, 0x0050f000, count=1000)
            results.append((u.reg_read(UC_ARM_REG_R0), u.reg_read(UC_ARM_REG_SP)))
        assert results[0] == results[1] == (expected, 0x2002f000), (label, results)
    print('PASS_BOOT_THREAD_NAME_GETTER', 3)
