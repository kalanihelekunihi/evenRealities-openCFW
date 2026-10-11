#!/usr/bin/env python3
"""Bounded original/source MSPI timing-window center comparison."""
from pathlib import Path
import struct
import subprocess
import tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS
from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0, UC_ARM_REG_SP

ROOT = Path(__file__).resolve().parents[4]
STOCK = (ROOT / 'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin').read_bytes()
SOURCE = ROOT / 'g2/components/bootloader/nor_mspi_power/timing_scan.c'
with tempfile.TemporaryDirectory() as tmp:
    tmp = Path(tmp)
    wrapper = tmp / 'window.c'
    wrapper.write_text(f'#include "{SOURCE}"\nunsigned source_window(const unsigned *p) {{return window_center(*p);}}\n')
    obj, image = tmp / 'window.o', tmp / 'window.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m33','-mthumb',
                    '-O2','-ffunction-sections','-fdata-sections','-c',str(wrapper),'-o',str(obj)],check=True)
    subprocess.run(['arm-none-eabi-ld','--gc-sections','-e','source_window',
                    '-Ttext=0x500000','-o',str(image),str(obj)],check=True)
    with image.open('rb') as stream:
        elf=ELFFile(stream)
        entry=next(s['st_value'] & ~1 for s in elf.get_section_by_name('.symtab').iter_symbols() if s.name=='source_window')
        segments=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD']
    patterns=[0,1,2,3,0xffffffff,0x80000000,0x0000ffff,0xffff0000,
              0x00010001,0x7ffffffe,0x80000003,0x40000001]
    patterns += [(0x9e3779b9*i ^ (0x7f4a7c15*(i>>2)))&0xffffffff for i in range(1,257)]
    for bits in patterns:
        pair=[]
        for native in (True,False):
            cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
            cpu.mem_map(0x410000,0x40000);cpu.mem_write(0x410000,STOCK)
            cpu.mem_map(0x500000,0x10000)
            if not native:
                for address,payload in segments: cpu.mem_write(address,payload)
            cpu.mem_map(0x20000000,0x30000)
            cpu.mem_write(0x20010000,struct.pack('<I',bits))
            cpu.reg_write(UC_ARM_REG_R0,0x20010000)
            cpu.reg_write(UC_ARM_REG_SP,0x2002f000)
            cpu.reg_write(UC_ARM_REG_LR,0x500e01)
            try:
                cpu.emu_start((0x41ff74 if native else entry)|1,0x500e00,count=2000)
            except Exception as exc:
                raise AssertionError((hex(bits),native,hex(cpu.reg_read(UC_ARM_REG_PC)))) from exc
            assert cpu.reg_read(UC_ARM_REG_PC)==0x500e00,(hex(bits),native,hex(cpu.reg_read(UC_ARM_REG_PC)))
            pair.append(cpu.reg_read(UC_ARM_REG_R0))
        assert pair[0]==pair[1],(hex(bits),pair)
    print('PASS_BOOT_TIMING_WINDOW_CENTER',len(patterns))
