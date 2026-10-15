#!/usr/bin/env python3
"""Compare Apollo color-register index gate and child call."""
from pathlib import Path
import itertools
import subprocess
import tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import (UC_ARM_REG_PC,UC_ARM_REG_LR,UC_ARM_REG_SP,
                               UC_ARM_REG_R0,UC_ARM_REG_R1)

root=Path(__file__).resolve().parents[3]
source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/color_register.c'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as temp:
    stub=Path(temp)/'child.c'
    stub.write_text('unsigned audio_uart_nema_child_514846(unsigned a,unsigned b)'
                    '{return 0;}\n')
    image=Path(temp)/'register.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55',
                    '-mthumb','-std=c11','-ffreestanding','-fno-builtin',
                    '-O2','-nostdlib','-Wl,-Ttext=0x100000',str(source),
                    str(stub),'-o',str(image)],check=True,capture_output=True)
    with image.open('rb') as file:
        elf=ELFFile(file)
        segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments()
                  if s['p_type']=='PT_LOAD']
        symbols={s.name:s['st_value'] for s in
                 elf.get_section_by_name('.symtab').iter_symbols()}
    def run(compiled,index,color):
        uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
        uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,blob)
        uc.mem_map(0x100000,0x200000);uc.mem_map(0x20000000,0x100000)
        for address,data in segments:uc.mem_write(address,data)
        trace=[]
        target=(symbols['audio_uart_nema_child_514846']&~1 if compiled
                else 0x514846)
        def hook(emu,address,size,user):
            if address!=target:return
            trace.append((emu.reg_read(UC_ARM_REG_R0),
                          emu.reg_read(UC_ARM_REG_R1)))
            emu.reg_write(UC_ARM_REG_R0,0x12345678)
            emu.reg_write(UC_ARM_REG_PC,emu.reg_read(UC_ARM_REG_LR))
        uc.hook_add(UC_HOOK_CODE,hook)
        uc.reg_write(UC_ARM_REG_R0,index)
        uc.reg_write(UC_ARM_REG_R1,color)
        uc.reg_write(UC_ARM_REG_SP,0x200f0000)
        uc.reg_write(UC_ARM_REG_LR,0x300001)
        start=(symbols['audio_uart_ambiq_color_register_4b1474'] if compiled
               else 0x4b1474)
        uc.emu_start(start|1,0x300000,count=100)
        return uc.reg_read(UC_ARM_REG_R0),trace
    indices=(0,1,2,3,4,5,0xffffffff,0xffffff80,0x40000000)
    colors=(0,0x80abcdef,0xffffffff)
    for index,color in itertools.product(indices,colors):
        native=run(False,index,color)
        candidate=run(True,index,color)
        assert candidate==native,(hex(index),hex(color),native,candidate)
    print('PASS_AMBIQ_COLOR_REGISTER_NATIVE',len(indices)*len(colors))
