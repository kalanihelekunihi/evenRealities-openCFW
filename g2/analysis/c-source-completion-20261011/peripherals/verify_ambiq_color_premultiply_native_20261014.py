#!/usr/bin/env python3
"""Compare Apollo premultiplied ARGB output against native instructions."""
from pathlib import Path
import random
import subprocess
import tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import UC_ARM_REG_LR,UC_ARM_REG_SP,UC_ARM_REG_R0

root=Path(__file__).resolve().parents[3]
source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/color_premultiply.c'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as temp:
    image=Path(temp)/'color.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55',
                    '-mthumb','-std=c11','-ffreestanding','-fno-builtin',
                    '-O2','-nostdlib','-Wl,-Ttext=0x100000',str(source),
                    '-o',str(image)],check=True,capture_output=True)
    with image.open('rb') as file:
        elf=ELFFile(file)
        segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments()
                  if s['p_type']=='PT_LOAD']
        candidate=next(s['st_value'] for s in
                       elf.get_section_by_name('.symtab').iter_symbols()
                       if s.name=='audio_uart_ambiq_color_premultiply_4b15b4')
    def run(compiled,value):
        uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
        uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,blob)
        uc.mem_map(0x100000,0x200000);uc.mem_map(0x20000000,0x100000)
        for address,data in segments:uc.mem_write(address,data)
        uc.reg_write(UC_ARM_REG_R0,value)
        uc.reg_write(UC_ARM_REG_SP,0x200f0000)
        uc.reg_write(UC_ARM_REG_LR,0x300001)
        uc.emu_start((candidate if compiled else 0x4b15b4)|1,0x300000,count=150)
        return uc.reg_read(UC_ARM_REG_R0)
    rng=random.Random(0x4b15b4)
    values=[0,0xffffffff,0x01010101,0x7f80ff01,0xff123456]
    values += [(a<<24)|(r<<16)|(g<<8)|b
               for a in (0,1,2,127,128,254,255)
               for r,g,b in ((0,255,1),(128,127,254),(255,255,255))]
    values += [rng.getrandbits(32) for _ in range(128)]
    for value in values:
        native=run(False,value)
        compiled=run(True,value)
        assert compiled==native,(hex(value),hex(native),hex(compiled))
    print('PASS_AMBIQ_COLOR_PREMULTIPLY_NATIVE',len(values))
