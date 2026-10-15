#!/usr/bin/env python3
"""Compare LVGL image decoder open 0x488f9c with Apollo S200 calls."""
from pathlib import Path
import subprocess
import tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UcError, UC_ARCH_ARM, UC_HOOK_CODE, UC_MODE_MCLASS, UC_MODE_THUMB
from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3, UC_ARM_REG_SP

root=Path(__file__).resolve().parents[3]
source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/decoder_open.c'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
lower=[('audio_uart_lv_image_memzero_488f40',0x488f40),
       ('audio_uart_lv_image_source_type_488cb8',0x488cb8),
       ('audio_uart_lv_image_cache_enabled_4d4b24',0x4d4b24),
       ('audio_uart_lv_decoder_cache_489460',0x489460),
       ('audio_uart_lv_decoder_find_48925a',0x48925a),
       ('audio_queue_copy_bytes',0x439be4),
       ('audio_uart_lv_decoder_default_options_4d4ccc',0x4d4ccc),
       ('audio_uart_lv_draw_flush_cache_48abb8',0x48abb8),
       ('audio_uart_lvgl_log',0x44d25c)]
with tempfile.TemporaryDirectory() as directory:
    stub=Path(directory)/'lower.c'
    stub.write_text('typedef unsigned u32;\nunsigned char audio_uart_display_lv_root[1024];\n'+'\n'.join(
        f'u32 {name}(u32 a,u32 b,u32 c,u32 d,u32 e){{return 0;}}'
        for name,_ in lower))
    image=Path(directory)/'open.elf'
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

    def run(compiled,source_present,options_present,context,skip_cache,
            cache_result,find_result,callback_result,decoded_present,flush,
            decoded_valid=True):
        uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
        uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,blob)
        uc.mem_map(0x100000,0x200000);uc.mem_map(0x20000000,0x100000)
        for address,data in segments:uc.mem_write(address,data)
        out,src,opts,decoder,decoded,callback=tuple(0x20005000+i*0x1000 for i in range(6))
        native_root=0x2006f548;source_root=symbols['audio_uart_display_lv_root']
        for root_address in (native_root,source_root):
            uc.mem_write(root_address+0x134,(0x2000c000).to_bytes(4,'little'))
        uc.mem_write(out,bytes([0x77]*76));uc.mem_write(opts,bytes([9,8,skip_cache,6,5]))
        uc.mem_write(decoder+4,(callback|1).to_bytes(4,'little'))
        uc.mem_write(decoded+20,(1 if decoded_valid else 0).to_bytes(4,'little'))
        uc.mem_write(decoded+24,(1).to_bytes(4,'little'))
        calls=[]
        def cstr(emu,address):return bytes(emu.mem_read(address,160)).split(b'\0',1)[0]
        def hook(emu,address,size,user):
            r=[emu.reg_read(reg) for reg in (UC_ARM_REG_R0,UC_ARM_REG_R1,
                                               UC_ARM_REG_R2,UC_ARM_REG_R3)]
            if address==callback:
                calls.append(('callback',r[0]==decoder,r[1]==out,
                              bytes(emu.mem_read(out+4,5))))
                emu.mem_write(out+44,(decoded if decoded_present else 0).to_bytes(4,'little'))
                emu.mem_write(out+8,bytes([int(flush)]))
                value=callback_result
            else:
                name=next(name for name,native in lower
                          if (symbols[name]&~1 if compiled else native)==address)
                if name==lower[0][0]:
                    calls.append(('zero',r[0]==out,r[1]));emu.mem_write(r[0],bytes(r[1]));value=0
                elif name==lower[1][0]:calls.append(('type',r[0]==src));value=3
                elif name==lower[2][0]:calls.append(('context',));value=context
                elif name==lower[3][0]:calls.append(('cache',r[0]==out));value=cache_result
                elif name==lower[4][0]:calls.append(('find',r[0]==out,r[1]==out+32));value=decoder if find_result else 0
                elif name==lower[5][0]:
                    calls.append(('copy',r[2],bytes(emu.mem_read(r[1],r[2]))))
                    emu.mem_write(r[0],bytes(emu.mem_read(r[1],r[2])));value=r[0]
                elif name==lower[6][0]:
                    calls.append(('defaults',r[1]));emu.mem_write(r[0],bytes([1,2,3,4,5]));value=r[0]
                elif name==lower[7][0]:calls.append(('flush',r[0]==decoded,r[1]));value=0
                else:
                    message=int.from_bytes(emu.mem_read(emu.reg_read(UC_ARM_REG_SP),4),'little')
                    sp=emu.reg_read(UC_ARM_REG_SP)
                    extra=[int.from_bytes(emu.mem_read(sp+4*i,4),'little') for i in (1,2)]
                    calls.append(('log',r[0],cstr(emu,r[1]),r[2],cstr(emu,r[3]),
                                  cstr(emu,message),tuple(cstr(emu,p) for p in extra)));value=0
            emu.reg_write(UC_ARM_REG_R0,value)
            emu.reg_write(UC_ARM_REG_PC,emu.reg_read(UC_ARM_REG_LR))
        for name,native in lower:
            target=symbols[name]&~1 if compiled else native
            uc.hook_add(UC_HOOK_CODE,hook,begin=target,end=target)
        uc.hook_add(UC_HOOK_CODE,hook,begin=callback,end=callback)
        uc.reg_write(UC_ARM_REG_SP,0x200ff000);uc.reg_write(UC_ARM_REG_LR,0x600001)
        for reg,value in ((UC_ARM_REG_R0,out),
                          (UC_ARM_REG_R1,src if source_present else 0),
                          (UC_ARM_REG_R2,opts if options_present else 0),
                          (UC_ARM_REG_R3,0)):
            uc.reg_write(reg,value)
        entry=symbols['audio_uart_lv_image_decoder_open_488f9c'] if compiled else 0x488f9c
        try:
            uc.emu_start(entry|1,0x600000,count=600);terminal='return'
        except UcError:terminal='fault'
        return calls,uc.reg_read(UC_ARM_REG_R0)&0xff,terminal

    cases=0
    for source_present in (False,True):
      for options_present in (False,True):
       for context in (0,1):
        for skip_cache in (0,1):
         for cache_result in (0,1):
          for find_result in (0,1):
           for callback_result in (0,1,2):
            for decoded_present,flush in ((False,False),(True,False),(True,True)):
             args=(source_present,options_present,context,skip_cache,
                   cache_result,find_result,callback_result,decoded_present,flush)
             native=run(False,*args);candidate=run(True,*args)
             assert native==candidate,(args,native,candidate)
             cases+=1
    for options_present in (False,True):
        args=(True,options_present,0,0,0,1,1,True,False,False)
        native=run(False,*args);candidate=run(True,*args)
        assert native[:1]+native[2:]==candidate[:1]+candidate[2:],(args,native,candidate)
        cases+=1
    print('PASS_LV_IMAGE_DECODER_OPEN_NATIVE',cases)
