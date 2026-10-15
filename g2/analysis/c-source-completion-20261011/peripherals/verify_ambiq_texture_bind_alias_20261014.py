#!/usr/bin/env python3
"""Check image-path alias forwards all seven texture binder arguments."""
from pathlib import Path
import random
import subprocess
import tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import (UC_ARM_REG_PC,UC_ARM_REG_LR,UC_ARM_REG_SP,
                               UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,
                               UC_ARM_REG_R3)

root=Path(__file__).resolve().parents[3]
source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/texture_bind_alias.c'
with tempfile.TemporaryDirectory() as temp:
    stub=Path(temp)/'lower.c'
    stub.write_text('void audio_uart_nema_bind_tex_4b1298(unsigned a,unsigned b,'
                    'unsigned c,unsigned d,unsigned e,unsigned f,unsigned g){}\n')
    image=Path(temp)/'alias.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4',
                    '-mthumb','-std=c11','-ffreestanding','-fno-builtin',
                    '-O2','-nostdlib','-Wl,-Ttext=0x100000',str(source),
                    str(stub),'-o',str(image)],check=True,capture_output=True)
    with image.open('rb') as file:
        elf=ELFFile(file)
        segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments()
                  if s['p_type']=='PT_LOAD']
        symbols={s.name:s['st_value'] for s in
                 elf.get_section_by_name('.symtab').iter_symbols()}
    rng=random.Random(0x4b1298)
    cases=[(0,0,0,0,0,0,0),(0xffffffff,)*7]
    cases += [tuple(rng.getrandbits(32) for _ in range(7))
              for _ in range(254)]
    regs=(UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)
    for args in cases:
        uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
        uc.mem_map(0x100000,0x200000);uc.mem_map(0x20000000,0x100000)
        for address,data in segments:uc.mem_write(address,data)
        stack=0x200f0000
        uc.mem_write(stack,b''.join(x.to_bytes(4,'little') for x in args[4:]))
        observed=[]
        target=symbols['audio_uart_nema_bind_tex_4b1298']&~1
        def hook(emu,address,size,user):
            if address!=target:return
            sp=emu.reg_read(UC_ARM_REG_SP)
            values=tuple(emu.reg_read(r) for r in regs)+tuple(
                int.from_bytes(emu.mem_read(sp+i*4,4),'little')
                for i in range(3))
            observed.append(values)
            emu.reg_write(UC_ARM_REG_PC,emu.reg_read(UC_ARM_REG_LR))
        uc.hook_add(UC_HOOK_CODE,hook)
        for reg,value in zip(regs,args):uc.reg_write(reg,value)
        uc.reg_write(UC_ARM_REG_SP,stack)
        uc.reg_write(UC_ARM_REG_LR,0x300001)
        uc.emu_start(symbols['audio_uart_ambiq_texture_bind_4b1298']|1,
                     0x300000,count=100)
        assert observed==[args],(args,observed)
    print('PASS_AMBIQ_TEXTURE_BIND_ALIAS',len(cases))
