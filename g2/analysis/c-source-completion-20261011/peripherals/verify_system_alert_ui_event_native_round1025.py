#!/usr/bin/env python3
"""Compare compiled system-alert UI callback with official Apollo Thumb."""
from pathlib import Path
import hashlib,json,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *

root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/system-alert-ui-event-native-round1025';out.mkdir(parents=True,exist_ok=True)
src=root/'components/audio/uart_thread_source_candidate/system_alert_ui_event_4d3354.c'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
native={'audio_system_alert_page_init_4d2f48':0x4d2f48,
        'audio_system_alert_page_update_4d30ba':0x4d30ba,
        'audio_log_flags':0x43d0ce,'audio_log_extended':0x43d574,
        'compressed_log_output':0x43ce9e}
with tempfile.TemporaryDirectory() as td:
    td=Path(td);elf=td/'c.elf';stubs=td/'stubs.s';storage=td/'storage.c'
    storage.write_text('#include <stdint.h>\nuint8_t audio_uart_registry_context_20003bd0[8];\n')
    lines=['.syntax unified','.thumb','.section .text.oracle_stubs,"ax",%progbits']
    for name in native:lines += [f'.global {name}','.thumb_func',f'{name}:','  bx lr']
    lines+=['.section .note.GNU-stack,"",%progbits'];stubs.write_text('\n'.join(lines)+'\n')
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2',
                    '-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_registry_callback_4d3354',
                    str(src),str(storage),str(stubs),'-o',str(elf)],check=True)
    with elf.open('rb') as f:
        image=ELFFile(f)
        segments=[(v['p_vaddr'],v.data()) for v in image.iter_segments() if v['p_type']=='PT_LOAD']
        sym={v.name:v['st_value'] for v in image.get_section_by_name('.symtab').iter_symbols()}
    cases=[0,2,3,4,5,6]
    for event in cases:
        observations=[]
        for compiled in (False,True):
            u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
            u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
            u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
            for addr,data in segments:u.mem_write(addr,data)
            def cell(name,addr):return sym[name] if compiled else addr
            ctx=cell('audio_uart_registry_context_20003bd0',0x20003bd0)
            parent=cell('audio_system_alert_parent_200749ec',0x200749ec)
            active=cell('audio_system_alert_active_20075025',0x20075025)
            page=cell('audio_system_alert_page_id_20003bcc',0x20003bcc)
            u.mem_write(ctx+4,(0x55667788).to_bytes(4,'little'))
            u.mem_write(parent,(0x11223344).to_bytes(4,'little'))
            u.mem_write(active,b'\x7a');u.mem_write(page,(0xdeadbeef).to_bytes(4,'little'))
            u.reg_write(UC_ARM_REG_R0,event);u.reg_write(UC_ARM_REG_R1,0x12345678)
            u.reg_write(UC_ARM_REG_R2,7);u.reg_write(UC_ARM_REG_R3,0x20081000)
            u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
            address_map={((sym[name] if compiled else addr)&~1):name for name,addr in native.items()}
            calls=[]
            def hook(uc,address,size,user):
                name=address_map.get(address)
                if name is None:return
                if name!='audio_log_flags':
                    calls.append((name,uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1),uc.reg_read(UC_ARM_REG_R2)))
                uc.reg_write(UC_ARM_REG_R0,0)
                uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
            u.hook_add(UC_HOOK_CODE,hook)
            entry=sym['audio_uart_registry_callback_4d3354'] if compiled else 0x4d3354
            u.emu_start(entry|1,0x600000,count=10000)
            observations.append((u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(ctx+4,4)),
                                 bytes(u.mem_read(active,1)),bytes(u.mem_read(page,4)),calls))
        assert observations[0]==observations[1],(event,observations)
receipt={'round':1025,'status':'PASS_SYSTEM_ALERT_UI_EVENT_NATIVE',
         'component':'Apollo system-alert UI create/update/exit effects',
         'source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
         'official_image_sha256':hashlib.sha256(blob).hexdigest(),
         'native_entry':'0x4d3354','events':cases,
         'validation':'Actual compiled Cortex-M4 C versus official Thumb return, child-call and RAM-cell effects',
         'whole_image_complete':False,'hardware_proof':False,
         'gates':['Logging-enabled paths and child bodies remain open',
                  'Registry context ownership, full image placement and hardware proof remain open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],len(cases))
