#!/usr/bin/env python3
"""Compare Apollo S200 draw-image entry 0x53f42a call decisions with C."""
from pathlib import Path
import subprocess
import tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_HOOK_CODE, UC_MODE_MCLASS, UC_MODE_THUMB
from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3, UC_ARM_REG_SP

root=Path(__file__).resolve().parents[3]
source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/image.c'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
lower=[('audio_uart_lvgl_log',0x44d25c),('audio_uart_ambiq_draw_image_core_53f548',0x53f548)]

with tempfile.TemporaryDirectory() as directory:
    stub=Path(directory)/'lower.c'
    stub.write_text('typedef unsigned u32;\n'+'\n'.join(
        f'void {name}(u32 a,u32 b,u32 c,u32 d,u32 e){{}}' for name,_ in lower))
    image=Path(directory)/'image.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb',
                    '-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib',
                    '-Wl,-Ttext=0x100000',str(source),str(stub),'-o',str(image)],
                   check=True,capture_output=True)
    with image.open('rb') as file:
        elf=ELFFile(file)
        segments=[(segment['p_vaddr'],segment.data()) for segment in elf.iter_segments()
                  if segment['p_type']=='PT_LOAD']
        symbols={sym.name:sym['st_value']
                 for sym in elf.get_section_by_name('.symtab').iter_symbols()}

    def run(compiled,blend,tiled,transformed,width,height,radius,mask):
        uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
        uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,blob)
        uc.mem_map(0x100000,0x200000);uc.mem_map(0x20000000,0x100000)
        for address,data in segments:uc.mem_write(address,data)
        unit,descriptor,area=0x20005000,0x20006000,0x20007000
        data=bytearray(108)
        def put(off,val):data[off:off+4]=val.to_bytes(4,'little')
        put(0x24,(height<<16)|width)
        put(0x2c,radius);put(0x30,transformed);put(0x34,0x100)
        put(0x38,0x100);put(0x68,mask)
        data[0x50]=0;data[0x51]=(blend&7)|(0x10 if tiled else 0)
        uc.mem_write(descriptor,bytes(data));calls=[]
        def cstr(emu,address):
            return bytes(emu.mem_read(address,180)).split(b'\0',1)[0]
        def hook(emu,address,size,user):
            name=next(name for name,native in lower
                      if (symbols[name]&~1 if compiled else native)==address)
            r=[emu.reg_read(reg) for reg in (UC_ARM_REG_R0,UC_ARM_REG_R1,
                                               UC_ARM_REG_R2,UC_ARM_REG_R3)]
            if name=='audio_uart_lvgl_log':
                message=int.from_bytes(emu.mem_read(emu.reg_read(UC_ARM_REG_SP),4),'little')
                calls.append(('log',r[0],cstr(emu,r[1]),r[2],cstr(emu,r[3]),
                              cstr(emu,message)))
            else:
                calls.append(('core',r[0]==unit,r[1]==descriptor,r[2]==area))
            emu.reg_write(UC_ARM_REG_PC,emu.reg_read(UC_ARM_REG_LR))
        for name,native in lower:
            target=symbols[name]&~1 if compiled else native
            uc.hook_add(UC_HOOK_CODE,hook,begin=target,end=target)
        uc.reg_write(UC_ARM_REG_SP,0x200ff000);uc.reg_write(UC_ARM_REG_LR,0x600001)
        for reg,value in ((UC_ARM_REG_R0,unit),(UC_ARM_REG_R1,descriptor),
                          (UC_ARM_REG_R2,area)):
            uc.reg_write(reg,value)
        entry=symbols['audio_uart_ambiq_draw_image_53f42a'] if compiled else 0x53f42a
        uc.emu_start(entry|1,0x600000,count=600)
        return calls

    cases=0
    for blend in range(8):
        for tiled in (False,True):
            for transformed in (0,1):
                for width,height in ((16,16),(3,16),(16,7)):
                    for radius,mask in ((0,0),(1,0),(0,1),(1,1)):
                        args=(blend,tiled,transformed,width,height,radius,mask)
                        native=run(False,*args);candidate=run(True,*args)
                        assert native==candidate,(args,native,candidate)
                        cases+=1
    print('PASS_AMBIQ_DRAW_IMAGE_ENTRY_NATIVE',cases)
