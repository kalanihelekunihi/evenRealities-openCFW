#!/usr/bin/env python3
"""Compare mask position float conversion and rectangle forwarding."""
from pathlib import Path
import itertools
import subprocess
import tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import (UC_ARM_REG_PC,UC_ARM_REG_LR,UC_ARM_REG_SP,
                               UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,
                               UC_ARM_REG_R3,UC_ARM_REG_S0,UC_ARM_REG_S1)

root=Path(__file__).resolve().parents[3]
source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/mask_position.c'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
lower=[('audio_uart_nema_float_position_5228b0',0x5228b0),
       ('audio_uart_nema_mask_rectangle_522ae0',0x522ae0)]
with tempfile.TemporaryDirectory() as temp:
    stub=Path(temp)/'lower.c'
    stub.write_text('void audio_uart_nema_float_position_5228b0(float a,float b) '
                    '__attribute__((pcs("aapcs-vfp")));\n'
                    'void audio_uart_nema_float_position_5228b0(float a,float b){}\n'
                    'unsigned audio_uart_nema_mask_rectangle_522ae0('
                    'int a,int b,int c,int d){return 0;}\n')
    image=Path(temp)/'mask_position.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4',
                    '-mthumb','-mfpu=fpv4-sp-d16','-mfloat-abi=hard',
                    '-std=c11','-ffreestanding','-fno-builtin','-O2',
                    '-nostdlib','-Wl,-Ttext=0x100000',str(source),str(stub),
                    '-o',str(image)],check=True,capture_output=True)
    with image.open('rb') as file:
        elf=ELFFile(file)
        segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments()
                  if s['p_type']=='PT_LOAD']
        symbols={s.name:s['st_value'] for s in
                 elf.get_section_by_name('.symtab').iter_symbols()}
    regs=(UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)
    def run(compiled,values):
        uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
        uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,blob)
        uc.mem_map(0x100000,0x200000);uc.mem_map(0x20000000,0x100000)
        for address,data in segments:uc.mem_write(address,data)
        trace=[]
        def hook(emu,address,size,user):
            for name,native in lower:
                target=(symbols[name]&~1) if compiled else native
                if address!=target:continue
                if name==lower[0][0]:
                    trace.append(('float',emu.reg_read(UC_ARM_REG_S0),
                                  emu.reg_read(UC_ARM_REG_S1)))
                else:
                    trace.append(('rectangle',tuple(emu.reg_read(r) for r in regs)))
                emu.reg_write(UC_ARM_REG_R0,0x12345678)
                emu.reg_write(UC_ARM_REG_PC,emu.reg_read(UC_ARM_REG_LR))
                return
        uc.hook_add(UC_HOOK_CODE,hook)
        for reg,value in zip(regs,values):uc.reg_write(reg,value&0xffffffff)
        uc.reg_write(UC_ARM_REG_SP,0x200f0000)
        uc.reg_write(UC_ARM_REG_LR,0x300001)
        start=(symbols['audio_uart_ambiq_mask_position_4b1ad4'] if compiled
               else 0x4b1ad4)
        uc.emu_start(start|1,0x300000,count=100)
        return uc.reg_read(UC_ARM_REG_R0),trace
    cases=[(x,y,w,h) for x,y in itertools.product(
            (-100,-1,0,1,123456),(0,1,45,65535))
            for w,h in ((0,0),(12,34),(65535,777))]
    cases += [(0x7fffffff,-0x80000000,1,2)]
    for values in cases:
        native=run(False,values)
        candidate=run(True,values)
        assert candidate==native,(values,native,candidate)
    print('PASS_AMBIQ_MASK_POSITION_NATIVE',len(cases))
