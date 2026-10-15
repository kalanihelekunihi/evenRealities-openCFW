#!/usr/bin/env python3
"""Compare compiled RequestDisplayStop child arguments with official Thumb."""
from pathlib import Path
import hashlib,json,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *

root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/system-alert-close-native-round1033';out.mkdir(parents=True,exist_ok=True)
src=root/'components/audio/uart_thread_source_candidate/system_alert_close_464c36.c'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
native={'audio_uart_master_request_core_464772':0x464772,
        'audio_log_flags':0x43d0ce,'audio_log_extended':0x43d574,
        'compressed_log_output':0x43ce9e}
with tempfile.TemporaryDirectory() as td:
    td=Path(td);elf=td/'c.elf';stubs=td/'stubs.s'
    lines=['.syntax unified','.thumb','.section .text.oracle_stubs,"ax",%progbits']
    for name in native:lines += [f'.global {name}','.thumb_func',f'{name}:','  bx lr']
    lines+=['.section .note.GNU-stack,"",%progbits'];stubs.write_text('\n'.join(lines)+'\n')
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2',
                    '-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_system_alert_close_464c36',
                    str(src),str(stubs),'-o',str(elf)],check=True)
    with elf.open('rb') as f:
        image=ELFFile(f)
        segments=[(v['p_vaddr'],v.data()) for v in image.iter_segments() if v['p_type']=='PT_LOAD']
        sym={v.name:v['st_value'] for v in image.get_section_by_name('.symtab').iter_symbols()}
    cases=[(0x21,0),(0x21,5),(0x10021,0x10005),(0xffff0021,0x20000)]
    for application_id,length in cases:
        traces=[]
        for compiled in (False,True):
            u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
            u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
            u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
            for addr,data in segments:u.mem_write(addr,data)
            u.reg_write(UC_ARM_REG_R0,application_id);u.reg_write(UC_ARM_REG_R1,0x20081000)
            u.reg_write(UC_ARM_REG_R2,length);u.reg_write(UC_ARM_REG_R3,0x12345678)
            u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
            addresses={((sym[name] if compiled else addr)&~1):name for name,addr in native.items()}
            calls=[]
            def hook(uc,address,size,user):
                name=addresses.get(address)
                if name is None:return
                if name=='audio_uart_master_request_core_464772':
                    regs=[uc.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)]
                    sp=uc.reg_read(UC_ARM_REG_SP)
                    extra=[int.from_bytes(uc.mem_read(sp+i*4,4),'little') for i in range(3)]
                    calls.append(tuple(regs+extra))
                uc.reg_write(UC_ARM_REG_R0,0)
                uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
            u.hook_add(UC_HOOK_CODE,hook)
            entry=sym['audio_system_alert_close_464c36'] if compiled else 0x464c36
            u.emu_start(entry|1,0x600000,count=4000)
            traces.append(calls)
        assert traces[0]==traces[1],((application_id,length),traces)
receipt={'round':1033,'status':'PASS_SYSTEM_ALERT_CLOSE_NATIVE',
         'component':'Apollo RequestDisplayStop packet-child argument contract',
         'source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
         'official_image_sha256':hashlib.sha256(blob).hexdigest(),
         'native_entry':'0x464c36','native_child':'0x464772','cases':cases,
         'validation':'Actual compiled Cortex-M4 C versus official Thumb seven-argument child call',
         'whole_image_complete':False,'hardware_proof':False,
         'gates':['Logging-enabled effects and downstream packet runtime remain open',
                  'Full image placement and hardware proof remain open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],len(cases))
