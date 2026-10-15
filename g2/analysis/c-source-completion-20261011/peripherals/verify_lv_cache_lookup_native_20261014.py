#!/usr/bin/env python3
"""Compare LVGL cache acquire 0x4d4dca with Apollo S200."""
from pathlib import Path
import subprocess
import tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UcError, UC_ARCH_ARM, UC_HOOK_CODE, UC_MODE_MCLASS, UC_MODE_THUMB
from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3, UC_ARM_REG_SP

root=Path(__file__).resolve().parents[3]
source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/cache_lookup.c'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
lower=[('audio_uart_lv_lock_core',0x4d4666),
       ('audio_uart_lv_unlock_core',0x4d4696),
       ('audio_uart_font_cache_acquire_data',0x4d53c6),
       ('audio_uart_lvgl_log',0x44d25c)]
with tempfile.TemporaryDirectory() as directory:
    stub=Path(directory)/'lower.c'
    stub.write_text('typedef unsigned u32;\n'+'\n'.join(
        f'u32 {name}(u32 a,u32 b,u32 c,u32 d,u32 e){{return 0;}}'
        for name,_ in lower))
    image=Path(directory)/'lookup.elf'
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

    def run(compiled,cache_present,key_present,cache_count,entry_present,userdata):
        uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
        uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,blob)
        uc.mem_map(0x100000,0x200000);uc.mem_map(0x20000000,0x100000)
        for address,data in segments:uc.mem_write(address,data)
        cache,key,manager,callback,entry=tuple(0x20005000+i*0x1000 for i in range(5))
        uc.mem_write(cache,manager.to_bytes(4,'little'))
        uc.mem_write(cache+12,cache_count.to_bytes(4,'little'))
        uc.mem_write(manager+12,(callback|1).to_bytes(4,'little'))
        calls=[]
        def cstr(emu,address):return bytes(emu.mem_read(address,160)).split(b'\0',1)[0]
        def hook(emu,address,size,user):
            r=[emu.reg_read(reg) for reg in (UC_ARM_REG_R0,UC_ARM_REG_R1,
                                               UC_ARM_REG_R2,UC_ARM_REG_R3)]
            if address==callback:
                calls.append(('callback',r[0]==cache,r[1]==key,r[2]));value=entry if entry_present else 0
            else:
                name=next(name for name,native in lower
                          if (symbols[name]&~1 if compiled else native)==address)
                if name==lower[0][0]:calls.append(('lock',r[0]==cache+28));value=0
                elif name==lower[1][0]:calls.append(('unlock',r[0]==cache+28));value=0
                elif name==lower[2][0]:calls.append(('retain',r[0]==entry));value=0
                else:
                    sp=emu.reg_read(UC_ARM_REG_SP)
                    extra=[int.from_bytes(emu.mem_read(sp+4*i,4),'little') for i in range(3)]
                    calls.append(('log',r[0],cstr(emu,r[1]),r[2],cstr(emu,r[3]),
                                  tuple(cstr(emu,p) for p in extra)));value=0
            emu.reg_write(UC_ARM_REG_R0,value)
            emu.reg_write(UC_ARM_REG_PC,emu.reg_read(UC_ARM_REG_LR))
        for name,native in lower:
            target=symbols[name]&~1 if compiled else native
            uc.hook_add(UC_HOOK_CODE,hook,begin=target,end=target)
        uc.hook_add(UC_HOOK_CODE,hook,begin=callback,end=callback)
        uc.reg_write(UC_ARM_REG_SP,0x200ff000);uc.reg_write(UC_ARM_REG_LR,0x600001)
        for reg,value in ((UC_ARM_REG_R0,cache if cache_present else 0),
                          (UC_ARM_REG_R1,key if key_present else 0),
                          (UC_ARM_REG_R2,userdata)):
            uc.reg_write(reg,value)
        start=symbols['audio_uart_lv_cache_lookup_4d4dca'] if compiled else 0x4d4dca
        try:uc.emu_start(start|1,0x600000,count=180);terminal='return'
        except UcError:terminal='fault'
        return calls,terminal,(uc.reg_read(UC_ARM_REG_R0) if terminal=='return' else None)

    cases=0
    for cache_present in (False,True):
      for key_present in (False,True):
       for cache_count in (0,1,4):
        for entry_present in (False,True):
         for userdata in (0,1,0x2000a000):
          args=(cache_present,key_present,cache_count,entry_present,userdata)
          native=run(False,*args);candidate=run(True,*args)
          assert native==candidate,(args,native,candidate)
          cases+=1
    print('PASS_LV_CACHE_LOOKUP_NATIVE',cases)
