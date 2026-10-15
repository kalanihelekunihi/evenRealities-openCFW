#!/usr/bin/env python3
"""Compare valid-format mask texture calls with Apollo native."""
from pathlib import Path
import itertools
import subprocess
import tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn.arm_const import (UC_ARM_REG_PC,UC_ARM_REG_LR,UC_ARM_REG_SP,
                               UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,
                               UC_ARM_REG_R3)

root=Path(__file__).resolve().parents[3]
source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/mask_options.c'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
lower=[('audio_uart_ambiq_nema_cf_4b05a4',0x4b05a4,1),
       ('audio_uart_ambiq_texture_bind_4b1298',0x4b1298,7),
       ('audio_uart_ambiq_texture_setup_4b06c0',0x4b06c0,6),
       ('audio_uart_ambiq_mask_position_4b1ad4',0x4b1ad4,4)]
with tempfile.TemporaryDirectory() as temp:
    stub=Path(temp)/'lower.c'
    stub.write_text('typedef unsigned u32;\n'+'\n'.join(
        f'u32 {name}(u32 a,u32 b,u32 c,u32 d,u32 e,u32 f,u32 g)'
        '{return 0;} ' for name,_,_ in lower)+
        '\nu32 audio_uart_lvgl_log(void){return 0;}\n')
    image=Path(temp)/'mask.elf'
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

    def run(compiled,format_value,enable,width,height,stride):
        uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
        uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,blob)
        uc.mem_map(0x100000,0x200000);uc.mem_map(0x20000000,0x100000)
        for address,data in segments:uc.mem_write(address,data)
        ptr=0x20008000;words=[format_value<<8,(height<<16)|width,
                             stride,0,0x20009000]
        uc.mem_write(ptr,b''.join(x.to_bytes(4,'little') for x in words))
        trace=[]
        regs=(UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)
        def hook(emu,address,size,user):
            for name,native,argc in lower:
                target=(symbols[name]&~1) if compiled else native
                if address!=target:continue
                values=[emu.reg_read(reg) for reg in regs]
                sp=emu.reg_read(UC_ARM_REG_SP)
                values += [int.from_bytes(emu.mem_read(sp+i*4,4),'little')
                           for i in range(max(0,argc-4))]
                trace.append((name,tuple(values[:argc])))
                emu.reg_write(UC_ARM_REG_R0,format_value if name==lower[0][0] else 0)
                emu.reg_write(UC_ARM_REG_PC,emu.reg_read(UC_ARM_REG_LR))
                return
        uc.hook_add(UC_HOOK_CODE,hook)
        uc.reg_write(UC_ARM_REG_R0,ptr)
        uc.reg_write(UC_ARM_REG_R1,enable)
        uc.reg_write(UC_ARM_REG_SP,0x200f0000)
        uc.reg_write(UC_ARM_REG_LR,0x300001)
        start=(symbols['audio_uart_ambiq_mask_options_4b0ea6'] if compiled
               else 0x4b0ea6)
        uc.emu_start(start|1,0x300000,count=200)
        return uc.reg_read(UC_ARM_REG_R0),trace

    cases=0
    for fmt,enable,width,height,stride in itertools.product(
            (8,9),(0,1,0x100,0x101),(1,37),(1,29),(2,84)):
        native=run(False,fmt,enable,width,height,stride)
        candidate=run(True,fmt,enable,width,height,stride)
        assert candidate==native,(fmt,enable,width,height,stride,native,candidate)
        cases+=1
    print('PASS_AMBIQ_MASK_OPTIONS_NATIVE',cases)
