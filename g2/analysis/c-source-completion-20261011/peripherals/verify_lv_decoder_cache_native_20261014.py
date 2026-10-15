#!/usr/bin/env python3
"""Compare LVGL image cache lookup 0x489460 with Apollo S200."""
from pathlib import Path
import subprocess
import tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_HOOK_CODE, UC_MODE_MCLASS, UC_MODE_THUMB
from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_SP

root=Path(__file__).resolve().parents[3]
source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/decoder_cache.c'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
lower=[('audio_uart_lv_cache_lookup_4d4dca',0x4d4dca),
       ('audio_uart_lv_cache_entry_4d5396',0x4d5396)]
with tempfile.TemporaryDirectory() as directory:
    stub=Path(directory)/'lower.c'
    stub.write_text('typedef unsigned u32;\n'+'\n'.join(
        f'u32 {name}(u32 a,u32 b,u32 c){{return 0;}}' for name,_ in lower))
    image=Path(directory)/'cache.elf'
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

    def run(compiled,found,source_word,source_type):
        uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
        uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,blob)
        uc.mem_map(0x100000,0x200000);uc.mem_map(0x20000000,0x100000)
        for address,data in segments:uc.mem_write(address,data)
        out,entry,data=0x20005000,0x20006000,0x20007000
        uc.mem_write(out,bytes(76));uc.mem_write(data+12,(0x20008000).to_bytes(4,'little'))
        uc.mem_write(data+16,(0x20009000).to_bytes(4,'little'))
        for off,value in ((12,source_word),(64,0x2000a000)):
            uc.mem_write(out+off,value.to_bytes(4,'little'))
        uc.mem_write(out+16,bytes([source_type]));calls=[]
        def hook(emu,address,size,user):
            name=next(name for name,native in lower
                      if (symbols[name]&~1 if compiled else native)==address)
            if name==lower[0][0]:
                key=emu.reg_read(UC_ARM_REG_R1)
                calls.append(('lookup',emu.reg_read(UC_ARM_REG_R0),
                              bytes(emu.mem_read(key+4,5)),emu.reg_read(UC_ARM_REG_R2)))
                value=entry if found else 0
            else:
                calls.append(('entry',emu.reg_read(UC_ARM_REG_R0)));value=data
            emu.reg_write(UC_ARM_REG_R0,value)
            emu.reg_write(UC_ARM_REG_PC,emu.reg_read(UC_ARM_REG_LR))
        for name,native in lower:
            target=symbols[name]&~1 if compiled else native
            uc.hook_add(UC_HOOK_CODE,hook,begin=target,end=target)
        uc.reg_write(UC_ARM_REG_SP,0x200ff000);uc.reg_write(UC_ARM_REG_LR,0x600001)
        uc.reg_write(UC_ARM_REG_R0,out)
        entrypoint=symbols['audio_uart_lv_decoder_cache_489460'] if compiled else 0x489460
        uc.emu_start(entrypoint|1,0x600000,count=100)
        return calls,bytes(uc.mem_read(out,76)),uc.reg_read(UC_ARM_REG_R0)&255

    cases=0
    for found in (False,True):
        for source_word in (0,0x2000b000,0xffffffff):
            for source_type in (0,1,2,3,255):
                args=(found,source_word,source_type)
                native=run(False,*args);candidate=run(True,*args)
                assert native==candidate,(args,native,candidate)
                cases+=1
    print('PASS_LV_DECODER_CACHE_NATIVE',cases)
