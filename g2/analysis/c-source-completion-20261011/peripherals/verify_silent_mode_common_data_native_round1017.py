#!/usr/bin/env python3
"""Compare compiled silent-mode callback branches with official Apollo Thumb."""
from pathlib import Path
import hashlib,json,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *

root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/silent-mode-common-data-native-round1017';out.mkdir(parents=True,exist_ok=True)
src=root/'components/audio/uart_thread_source_candidate/silent_mode_common_data_46949a.c'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
native={'audio_silent_mode_status_get':0x46919e,'audio_silent_mode_notify_app':0x49bf24,
        'audio_silent_mode_set_status':0x4691bc,'audio_uart_device_role_get':0x45a568,
        'audio_system_alert_command_45a8ee':0x45a8ee,'audio_log_flags':0x43d0ce,
        'audio_log_extended':0x43d574,'compressed_log_output':0x43ce9e}
with tempfile.TemporaryDirectory() as td:
    td=Path(td);elf=td/'c.elf';stubs=td/'stubs.s'
    lines=['.syntax unified','.thumb','.section .text.oracle_stubs,"ax",%progbits']
    for name in native:
        lines += [f'.global {name}','.thumb_func',f'{name}:','  bx lr']
    lines+=['.section .note.GNU-stack,"",%progbits']
    stubs.write_text('\n'.join(lines)+'\n')
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2',
                    '-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_registry_callback_46949a',
                    str(src),str(stubs),'-o',str(elf)],check=True)
    with elf.open('rb') as f:
        image=ELFFile(f)
        segments=[(v['p_vaddr'],v.data()) for v in image.iter_segments() if v['p_type']=='PT_LOAD']
        sym={v.name:v['st_value'] for v in image.get_section_by_name('.symtab').iter_symbols()}
    cases=[(3,b'\x01',1,0,1),(4,None,1,0,1),(4,b'\x01',0,0,1),
           (4,b'\x01',1,0,0),(4,b'\x01',1,0,1),(4,b'\x00',1,1,0),
           (4,b'\x00',1,1,1),(4,b'\x01',1,1,1),(4,b'\x02',1,0,1)]
    results=[]
    for event,payload,length,current,role in cases:
        observations=[]
        for compiled in (False,True):
            u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
            u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
            u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
            for addr,data in segments:u.mem_write(addr,data)
            data_addr=0x20080000
            if payload is not None:u.mem_write(data_addr,payload)
            status_addr=sym['audio_silent_mode_ui_status'] if compiled else 0x2007501d
            change_addr=sym['audio_silent_mode_change_from_app'] if compiled else 0x2007501e
            u.mem_write(status_addr,b'\x7a');u.mem_write(change_addr,b'\x01')
            u.reg_write(UC_ARM_REG_R0,event)
            u.reg_write(UC_ARM_REG_R1,data_addr if payload is not None else 0)
            u.reg_write(UC_ARM_REG_R2,length);u.reg_write(UC_ARM_REG_R3,0)
            u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
            addresses={((sym[name] if compiled else addr)&~1):name for name,addr in native.items()}
            calls=[]
            def hook(uc,address,size,user):
                name=addresses.get(address)
                if name is None:return
                if name!='audio_log_flags':calls.append((name,uc.reg_read(UC_ARM_REG_R0)))
                result=current if name=='audio_silent_mode_status_get' else role if name=='audio_uart_device_role_get' else 0
                uc.reg_write(UC_ARM_REG_R0,result)
                uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
            u.hook_add(UC_HOOK_CODE,hook)
            entry=sym['audio_uart_registry_callback_46949a'] if compiled else 0x46949a
            u.emu_start(entry|1,0x600000,count=30000)
            observations.append((u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(status_addr,1)),calls))
        assert observations[0]==observations[1],((event,payload,length,current,role),observations)
        results.append({'event':event,'payload':None if payload is None else payload.hex(),
                        'length':length,'current':current,'role':role,
                        'status':observations[0][1].hex(),'calls':observations[0][2]})
receipt={'round':1017,'status':'PASS_SILENT_MODE_COMMON_DATA_NATIVE',
         'component':'Apollo silent-mode callback nonlogging branches',
         'source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
         'official_image_sha256':hashlib.sha256(blob).hexdigest(),
         'native_entry':'0x46949a','cases':results,
         'validation':'Actual compiled Cortex-M4 C versus official Thumb return, RAM byte, and controlled child-call effects',
         'whole_image_complete':False,'hardware_proof':False,
         'gates':['Logging-enabled branches and lower child bodies remain unqualified',
                  'Full image placement and hardware proof remain open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],len(results))
