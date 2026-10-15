#!/usr/bin/env python3
"""Compare system-alert four-call style helper with official Thumb."""
from pathlib import Path
import hashlib,json,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *

root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/system-alert-page-style-native-round1029';out.mkdir(parents=True,exist_ok=True)
src=root/'components/audio/uart_thread_source_candidate/system_alert_page_style_4d2b9c.c'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
native={'audio_uart_page_44122a':0x44122a,'audio_uart_page_441238':0x441238,
        'audio_uart_page_44120e':0x44120e,'audio_uart_page_44121c':0x44121c}
with tempfile.TemporaryDirectory() as td:
    td=Path(td);elf=td/'c.elf';stubs=td/'stubs.s'
    lines=['.syntax unified','.thumb','.section .text.oracle_stubs,"ax",%progbits']
    for name in native:lines += [f'.global {name}','.thumb_func',f'{name}:','  bx lr']
    lines+=['.section .note.GNU-stack,"",%progbits'];stubs.write_text('\n'.join(lines)+'\n')
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2',
                    '-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_system_alert_page_style_4d2b9c',
                    str(src),str(stubs),'-o',str(elf)],check=True)
    with elf.open('rb') as f:
        image=ELFFile(f)
        segments=[(v['p_vaddr'],v.data()) for v in image.iter_segments() if v['p_type']=='PT_LOAD']
        sym={v.name:v['st_value'] for v in image.get_section_by_name('.symtab').iter_symbols()}
    for value,selector in ((0,0),(12,0),(0x12345678,0x55)):
        traces=[]
        for compiled in (False,True):
            u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
            u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
            u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
            for addr,data in segments:u.mem_write(addr,data)
            u.reg_write(UC_ARM_REG_R0,0x20081000);u.reg_write(UC_ARM_REG_R1,value)
            u.reg_write(UC_ARM_REG_R2,selector);u.reg_write(UC_ARM_REG_SP,0x200ff000)
            u.reg_write(UC_ARM_REG_LR,0x600001)
            address_map={((sym[name] if compiled else addr)&~1):name for name,addr in native.items()}
            calls=[]
            def hook(uc,address,size,user):
                name=address_map.get(address)
                if name is None:return
                calls.append((name,uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1),uc.reg_read(UC_ARM_REG_R2)))
                uc.reg_write(UC_ARM_REG_R0,0)
                uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
            u.hook_add(UC_HOOK_CODE,hook)
            entry=sym['audio_system_alert_page_style_4d2b9c'] if compiled else 0x4d2b9c
            u.emu_start(entry|1,0x600000,count=3000)
            traces.append(calls)
        assert traces[0]==traces[1],((value,selector),traces)
receipt={'round':1029,'status':'PASS_SYSTEM_ALERT_PAGE_STYLE_NATIVE',
         'component':'Apollo system-alert four-call style helper order/arguments',
         'source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
         'official_image_sha256':hashlib.sha256(blob).hexdigest(),
         'native_call_target':'0x4d2b9c','cases':3,
         'validation':'Actual compiled Cortex-M4 C versus official Thumb ordered lower calls',
         'whole_image_complete':False,'hardware_proof':False,
         'gates':['Lower LVGL effects and full image/hardware proof remain open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],3)
