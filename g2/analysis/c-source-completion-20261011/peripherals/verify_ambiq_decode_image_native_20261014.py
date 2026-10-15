#!/usr/bin/env python3
"""Compare Ambiq decoder wrapper 0x4b0f50 against Apollo S200."""
from pathlib import Path
import subprocess
import tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_HOOK_CODE, UC_MODE_MCLASS, UC_MODE_THUMB
from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3, UC_ARM_REG_SP

root=Path(__file__).resolve().parents[3]
source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/decode.c'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
lower=[('audio_uart_lv_image_decoder_open_488f9c',0x488f9c),
       ('audio_uart_lv_image_decoder_close_48908c',0x48908c),
       ('audio_uart_ambiq_color_format_src_4b05a4',0x4b05a4),
       ('audio_uart_lvgl_log',0x44d25c)]

with tempfile.TemporaryDirectory() as directory:
    stub=Path(directory)/'lower.c'
    stub.write_text('typedef unsigned u32;\n'+'\n'.join(
        f'u32 {name}(u32 a,u32 b,u32 c,u32 d,u32 e){{return 0;}}'
        for name,_ in lower))
    image=Path(directory)/'decode.elf'
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

    def run(compiled,opened,header,fmt,format_valid,mask,transformed):
        uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
        uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,blob)
        uc.mem_map(0x100000,0x200000);uc.mem_map(0x20000000,0x100000)
        for address,data in segments:uc.mem_write(address,data)
        src,out,image_header=0x20005000,0x20006000,0x20007000
        uc.mem_write(out,bytes(64));uc.mem_write(image_header,(fmt<<8).to_bytes(4,'little'))
        calls=[]
        def cstr(emu,address):
            return bytes(emu.mem_read(address,180)).split(b'\0',1)[0]
        def hook(emu,address,size,user):
            name=next(name for name,native in lower
                      if (symbols[name]&~1 if compiled else native)==address)
            r=[emu.reg_read(reg) for reg in (UC_ARM_REG_R0,UC_ARM_REG_R1,
                                               UC_ARM_REG_R2,UC_ARM_REG_R3)]
            if name==lower[0][0]:
                calls.append(('open',r[0]==out,r[1]==src,
                              bytes(emu.mem_read(r[2],5)),r[3]))
                emu.mem_write(out+0x2c,(image_header if header else 0).to_bytes(4,'little'))
                result=opened
            elif name==lower[1][0]:
                calls.append(('close',r[0]==out));result=0
            elif name==lower[2][0]:
                calls.append(('format',r[0]));result=1 if format_valid else 0xffffffff
            else:
                message=int.from_bytes(emu.mem_read(emu.reg_read(UC_ARM_REG_SP),4),'little')
                calls.append(('log',r[0],cstr(emu,r[1]),r[2],cstr(emu,r[3]),
                              cstr(emu,message)));result=0
            emu.reg_write(UC_ARM_REG_R0,result)
            emu.reg_write(UC_ARM_REG_PC,emu.reg_read(UC_ARM_REG_LR))
        for name,native in lower:
            target=symbols[name]&~1 if compiled else native
            uc.hook_add(UC_HOOK_CODE,hook,begin=target,end=target)
        uc.reg_write(UC_ARM_REG_SP,0x200ff000);uc.reg_write(UC_ARM_REG_LR,0x600001)
        for reg,value in ((UC_ARM_REG_R0,src),(UC_ARM_REG_R1,transformed),
                          (UC_ARM_REG_R2,out),(UC_ARM_REG_R3,mask)):
            uc.reg_write(reg,value)
        entry=symbols['audio_uart_ambiq_decode_image_4b0f50'] if compiled else 0x4b0f50
        uc.emu_start(entry|1,0x600000,count=500)
        return calls,uc.reg_read(UC_ARM_REG_R0)&0xff

    cases=0
    for opened in (0,1,2):
        for header in (False,True):
            for fmt in (6,7,14):
                for format_valid in (False,True):
                    for mask in (0,1,256):
                        for transformed in (0,1,256):
                            args=(opened,header,fmt,format_valid,mask,transformed)
                            native=run(False,*args);candidate=run(True,*args)
                            assert native==candidate,(args,native,candidate)
                            cases+=1
    print('PASS_AMBIQ_DECODE_IMAGE_NATIVE',cases)
