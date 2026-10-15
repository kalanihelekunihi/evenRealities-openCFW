#!/usr/bin/env python3
"""Compare Apollo image-color lower calls and boot-mode gate."""
from pathlib import Path
import itertools
import subprocess
import tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import (UC_ARM_REG_PC,UC_ARM_REG_LR,UC_ARM_REG_SP,
                               UC_ARM_REG_R0,UC_ARM_REG_R1)

root=Path(__file__).resolve().parents[3]
source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/image_color.c'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
lower=[('audio_uart_ambiq_color_premultiply_4b15b4',0x4b15b4),
       ('audio_uart_ambiq_color_register_4b1474',0x4b1474)]
with tempfile.TemporaryDirectory() as temp:
    stub=Path(temp)/'lower.c'
    stub.write_text('volatile unsigned char audio_uart_nema_boot_state_200043a8[8];\n'+
                    '\n'.join(f'unsigned {name}(unsigned a,unsigned b)'
                              '{return 0;}' for name,_ in lower))
    image=Path(temp)/'color.elf'
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
    def run(compiled,mode,color):
        uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
        uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,blob)
        uc.mem_map(0x100000,0x200000);uc.mem_map(0x20000000,0x100000)
        for address,data in segments:uc.mem_write(address,data)
        state=(symbols['audio_uart_nema_boot_state_200043a8'] if compiled
               else 0x200043a8)
        uc.mem_write(state,bytes([mode]))
        trace=[]
        def hook(emu,address,size,user):
            for name,native in lower:
                target=(symbols[name]&~1) if compiled else native
                if address!=target:continue
                r0=emu.reg_read(UC_ARM_REG_R0)
                r1=emu.reg_read(UC_ARM_REG_R1)
                trace.append((name,r0,r1 if name==lower[1][0] else None))
                if name==lower[0][0]:emu.reg_write(UC_ARM_REG_R0,r0^0x12345678)
                emu.reg_write(UC_ARM_REG_PC,emu.reg_read(UC_ARM_REG_LR))
                return
        uc.hook_add(UC_HOOK_CODE,hook)
        uc.reg_write(UC_ARM_REG_R0,color)
        uc.reg_write(UC_ARM_REG_SP,0x200f0000)
        uc.reg_write(UC_ARM_REG_LR,0x300001)
        start=(symbols['audio_uart_ambiq_image_color_513e4c'] if compiled
               else 0x513e4c)
        uc.emu_start(start|1,0x300000,count=100)
        return trace
    cases=0
    for mode,color in itertools.product((0,1,2,255),
            (0,0xff000000,0x11223344,0xffffffff,0x7f102030)):
        native=run(False,mode,color)
        candidate=run(True,mode,color)
        assert candidate==native,(mode,color,native,candidate)
        cases+=1
    print('PASS_AMBIQ_IMAGE_COLOR_NATIVE',cases)
