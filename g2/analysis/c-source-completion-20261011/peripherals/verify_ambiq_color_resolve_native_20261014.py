#!/usr/bin/env python3
"""Compare Apollo color pack and byte resolver outputs directly."""
from pathlib import Path
import random
import subprocess
import tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import (UC_ARM_REG_LR,UC_ARM_REG_SP,UC_ARM_REG_R0,
                               UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)

root=Path(__file__).resolve().parents[3]
source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/color_resolve.c'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
functions=(('audio_uart_ambiq_color_pack_4b15a6',0x4b15a6,4),
           ('audio_uart_ambiq_color_resolve_4b06a8',0x4b06a8,2))
with tempfile.TemporaryDirectory() as temp:
    image=Path(temp)/'color_resolve.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55',
                    '-mthumb','-std=c11','-ffreestanding','-fno-builtin',
                    '-O2','-nostdlib','-Wl,-Ttext=0x100000',str(source),
                    '-o',str(image)],check=True,capture_output=True)
    with image.open('rb') as file:
        elf=ELFFile(file)
        segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments()
                  if s['p_type']=='PT_LOAD']
        symbols={s.name:s['st_value'] for s in
                 elf.get_section_by_name('.symtab').iter_symbols()}
    regs=(UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)
    def run(compiled,function,args):
        uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
        uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,blob)
        uc.mem_map(0x100000,0x200000);uc.mem_map(0x20000000,0x100000)
        for address,data in segments:uc.mem_write(address,data)
        for reg,value in zip(regs,args):uc.reg_write(reg,value)
        uc.reg_write(UC_ARM_REG_SP,0x200f0000)
        uc.reg_write(UC_ARM_REG_LR,0x300001)
        name,native,_=function
        uc.emu_start((symbols[name] if compiled else native)|1,
                     0x300000,count=100)
        return uc.reg_read(UC_ARM_REG_R0)
    rng=random.Random(0x4b06a8)
    cases=0
    for function in functions:
        values=[(0,)*function[2],(0xffffffff,)*function[2]]
        values += [tuple(rng.getrandbits(32) for _ in range(function[2]))
                   for _ in range(128)]
        for args in values:
            native=run(False,function,args)
            candidate=run(True,function,args)
            assert candidate==native,(function[0],args,native,candidate)
            cases+=1
    print('PASS_AMBIQ_COLOR_RESOLVE_NATIVE',cases)
