#!/usr/bin/env python3
"""Compare LVGL decoder selection 0x48925a against Apollo S200 calls."""
from pathlib import Path
import subprocess
import tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UcError, UC_ARCH_ARM, UC_HOOK_CODE, UC_MODE_MCLASS, UC_MODE_THUMB
from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3, UC_ARM_REG_SP

root=Path(__file__).resolve().parents[3]
source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/decoder_find.c'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
lower=[('audio_uart_lv_image_memzero_488f40',0x488f40),
       ('audio_uart_lv_cache_enabled_4d5104',0x4d5104),
       ('audio_uart_lv_cache_lookup_4d4dca',0x4d4dca),
       ('audio_uart_lv_cache_entry_4d5396',0x4d5396),
       ('audio_uart_lv_decoder_release_4d4e72',0x4d4e72),
       ('audio_uart_lv_fs_file_open_4c6d9a',0x4c6d9a),
       ('audio_uart_lv_fs_file_seek_4c6fba',0x4c6fba),
       ('audio_uart_lv_fs_file_close_4c6ee0',0x4c6ee0),
       ('audio_uart_lv_list_first',0x482cd8),
       ('audio_uart_lv_list_next',0x482cf0),
       ('audio_uart_lv_color_bpp_440f44',0x440f44),
       ('audio_uart_font_path_duplicate',0x4547c6),
       ('audio_uart_lv_cache_add_4d4eea',0x4d4eea),
       ('audio_uart_lv_free',0x44f758),
       ('audio_uart_lvgl_log',0x44d25c)]
with tempfile.TemporaryDirectory() as directory:
    stub=Path(directory)/'lower.c'
    stub.write_text('typedef unsigned u32;\nunsigned char audio_uart_display_lv_root[1024];\n'+'\n'.join(
        f'u32 {name}(u32 a,u32 b,u32 c,u32 d,u32 e){{return 0;}}'
        for name,_ in lower))
    image=Path(directory)/'find.elf'
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

    def run(compiled,kind,cache_active,cache_hit,file_open_status,
            list_count,info_results,add_result,prestride,source_word,cf):
        uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
        uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,blob)
        uc.mem_map(0x100000,0x200000);uc.mem_map(0x20000000,0x100000)
        for address,data in segments:uc.mem_write(address,data)
        out,source_ptr,cache,entry,data,node1,node2,info_callback,dupe=tuple(
            0x20005000+i*0x1000 for i in range(9))
        native_root=0x2006f548;source_root=symbols['audio_uart_display_lv_root']
        for root_address in (native_root,source_root):
            uc.mem_write(root_address+0x138,cache.to_bytes(4,'little'))
        uc.mem_write(out,bytes(76));uc.mem_write(source_ptr+16,source_word.to_bytes(4,'little'))
        uc.mem_write(out+12,source_ptr.to_bytes(4,'little'))
        uc.mem_write(out+16,bytes([kind]))
        for node in (node1,node2):
            uc.mem_write(node,(info_callback|1).to_bytes(4,'little'))
            uc.mem_write(node+4,(0x2000e000).to_bytes(4,'little'))
        cached_decoder=0x2000f000
        for off,value in ((8,cf<<8),(12,0x00100020),(16,8),(20,cached_decoder)):
            uc.mem_write(data+off,value.to_bytes(4,'little'))
        trace=[];node_calls=0
        def cstr(emu,address):return bytes(emu.mem_read(address,160)).split(b'\0',1)[0]
        def hook(emu,address,size,user):
            nonlocal node_calls
            r=[emu.reg_read(reg) for reg in (UC_ARM_REG_R0,UC_ARM_REG_R1,
                                               UC_ARM_REG_R2,UC_ARM_REG_R3)]
            root_address=source_root if compiled else native_root
            if address==info_callback:
                i=node_calls;node_calls+=1
                status=info_results[min(i,len(info_results)-1)]
                trace.append(('info',r[0] in (node1,node2),r[1]==out,r[2]==out+32,status))
                if status==1:
                    for off,value in ((0,cf<<8),(4,0x00100020),(8,prestride)):
                        emu.mem_write(out+32+off,value.to_bytes(4,'little'))
                result=status
            else:
                name=next(name for name,native in lower
                          if (symbols[name]&~1 if compiled else native)==address)
                if name==lower[0][0]:
                    trace.append(('zero',r[0]==out+32,r[1]));emu.mem_write(r[0],bytes(r[1]));result=0
                elif name==lower[1][0]:trace.append(('enabled',r[0]==cache));result=cache_active
                elif name==lower[2][0]:
                    trace.append(('lookup',r[0]==cache,bytes(emu.mem_read(r[1],5)),r[2]));result=entry if cache_hit else 0
                elif name==lower[3][0]:trace.append(('entry',r[0]==entry));result=data
                elif name==lower[4][0]:trace.append(('release',r[0]==cache,r[1]==entry,r[2]));result=0
                elif name==lower[5][0]:trace.append(('open',r[0]==out+20,r[1]==source_ptr,r[2]));result=file_open_status
                elif name==lower[6][0]:trace.append(('seek',r[0]==out+20,r[1],r[2]));result=0
                elif name==lower[7][0]:trace.append(('close',r[0]==out+20));result=0
                elif name==lower[8][0]:trace.append(('first',r[0]==root_address+0x128));result=node1 if list_count else 0
                elif name==lower[9][0]:
                    trace.append(('next',r[0]==root_address+0x128,r[1] in (node1,node2)))
                    result=node2 if list_count>1 and r[1]==node1 else 0
                elif name==lower[10][0]:trace.append(('bpp',r[0]));result=8
                elif name==lower[11][0]:trace.append(('duplicate',r[0]==source_ptr));result=dupe
                elif name==lower[12][0]:
                    key=bytes(emu.mem_read(r[1],24))
                    trace.append(('add',r[0]==cache,key[:4]==dupe.to_bytes(4,'little'),
                                  key[4],key[8:20],key[20:24],r[2]))
                    result=entry if add_result else 0
                elif name==lower[13][0]:trace.append(('free',r[0]==dupe));result=0
                else:
                    message=int.from_bytes(emu.mem_read(emu.reg_read(UC_ARM_REG_SP),4),'little')
                    trace.append(('log',r[0],cstr(emu,r[1]),r[2],cstr(emu,r[3]),cstr(emu,message)))
                    result=0
            emu.reg_write(UC_ARM_REG_R0,result)
            emu.reg_write(UC_ARM_REG_PC,emu.reg_read(UC_ARM_REG_LR))
        for name,native in lower:
            target=symbols[name]&~1 if compiled else native
            uc.hook_add(UC_HOOK_CODE,hook,begin=target,end=target)
        uc.hook_add(UC_HOOK_CODE,hook,begin=info_callback,end=info_callback)
        uc.reg_write(UC_ARM_REG_SP,0x200ff000);uc.reg_write(UC_ARM_REG_LR,0x600001)
        uc.reg_write(UC_ARM_REG_R0,out);uc.reg_write(UC_ARM_REG_R1,out+32)
        start=symbols['audio_uart_lv_decoder_find_48925a'] if compiled else 0x48925a
        try:uc.emu_start(start|1,0x600000,count=600);terminal='return'
        except UcError:terminal='fault'
        return trace,terminal,uc.reg_read(UC_ARM_REG_R0),bytes(uc.mem_read(out+32,12))

    cases=0
    for kind in (0,1,2):
     for cache_active in (0,1):
      for cache_hit in (0,1):
       for file_open_status in (0,2):
        for list_count,info_results in ((0,(0,)),(1,(0,)),(1,(1,)),(2,(0,1))):
         for add_result in (0,1):
          for prestride in (0,8):
           for source_word,cf in ((0,11),(1,11),(1,20)):
            args=(kind,cache_active,cache_hit,file_open_status,
                  list_count,info_results,add_result,prestride,source_word,cf)
            native=run(False,*args);candidate=run(True,*args)
            assert native==candidate,(args,native,candidate)
            cases+=1
    print('PASS_LV_DECODER_FIND_NATIVE',cases)
