#!/usr/bin/env python3
"""Compare compiled silent-mode notification packet with official Apollo Thumb."""
from pathlib import Path
import hashlib,json,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *

root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/silent-mode-notify-app-native-round1021';out.mkdir(parents=True,exist_ok=True)
src=root/'components/audio/uart_thread_source_candidate/silent_mode_notify_app_49bf24.c'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
native={'audio_uart_buffer_zero':0x48949c,'audio_settings_notify_common':0x49bbfc,
        'audio_log_flags':0x43d0ce,'audio_log_extended':0x43d574,
        'compressed_log_output':0x43ce9e}
with tempfile.TemporaryDirectory() as td:
    td=Path(td);elf=td/'c.elf';stubs=td/'stubs.s'
    lines=['.syntax unified','.thumb','.section .text.oracle_stubs,"ax",%progbits']
    for name in native:lines += [f'.global {name}','.thumb_func',f'{name}:','  bx lr']
    lines+=['.section .note.GNU-stack,"",%progbits'];stubs.write_text('\n'.join(lines)+'\n')
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2',
                    '-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_silent_mode_notify_app',
                    str(src),str(stubs),'-o',str(elf)],check=True)
    with elf.open('rb') as f:
        image=ELFFile(f)
        segments=[(v['p_vaddr'],v.data()) for v in image.iter_segments() if v['p_type']=='PT_LOAD']
        sym={v.name:v['st_value'] for v in image.get_section_by_name('.symtab').iter_symbols()}
    values=[0,1,255,0x12345678]
    for value in values:
        packets=[]
        for compiled in (False,True):
            u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
            u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
            u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
            for addr,data in segments:u.mem_write(addr,data)
            u.mem_write(0x200fe000,bytes([0xa5]*0x1000))
            u.reg_write(UC_ARM_REG_R0,value)
            u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
            address_map={((sym[name] if compiled else addr)&~1):name for name,addr in native.items()}
            captured=[]
            def hook(uc,address,size,user):
                name=address_map.get(address)
                if name is None or (name=='audio_uart_buffer_zero' and not compiled):return
                if name=='audio_uart_buffer_zero':
                    uc.mem_write(uc.reg_read(UC_ARM_REG_R0),bytes(uc.reg_read(UC_ARM_REG_R1)))
                elif name=='audio_settings_notify_common':
                    captured.append(bytes(uc.mem_read(uc.reg_read(UC_ARM_REG_R0),104)))
                uc.reg_write(UC_ARM_REG_R0,0)
                uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
            u.hook_add(UC_HOOK_CODE,hook)
            entry=sym['audio_silent_mode_notify_app'] if compiled else 0x49bf24
            u.emu_start(entry|1,0x600000,count=10000)
            assert len(captured)==1,(value,compiled,len(captured))
            packets.append(captured[0])
        assert packets[0]==packets[1],(value,packets)
receipt={'round':1021,'status':'PASS_SILENT_MODE_NOTIFY_APP_NATIVE',
         'component':'Apollo silent-mode 104-byte notification packet',
         'source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
         'official_image_sha256':hashlib.sha256(blob).hexdigest(),
         'native_entry':'0x49bf24','values':values,
         'validation':'Actual compiled Cortex-M4 C versus official Thumb 104-byte packet at controlled notify child',
         'whole_image_complete':False,'hardware_proof':False,
         'gates':['Logging-enabled effects and downstream nanopb send remain unqualified',
                  'Full image placement and hardware proof remain open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],len(values))
