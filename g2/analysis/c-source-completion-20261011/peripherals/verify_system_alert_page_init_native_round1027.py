#!/usr/bin/env python3
"""Compare system-alert MainPage ordered calls and RAM cells with Apollo Thumb."""
from pathlib import Path
import hashlib,json,re,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *

root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/system-alert-page-init-native-round1027';out.mkdir(parents=True,exist_ok=True)
src=root/'components/audio/uart_thread_source_candidate/system_alert_page_init_4d2f48.c'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
with tempfile.TemporaryDirectory() as td:
    td=Path(td);elf=td/'c.elf';obj=td/'source.o';stubs=td/'stubs.s';storage=td/'storage.c'
    storage.write_text('#include <stdint.h>\nuint32_t audio_system_alert_parent_200749ec;\n')
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2',
                    '-c',str(src),'-o',str(obj)],check=True)
    imports=[line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','-u',str(obj)],text=True).splitlines()]
    imports=[name for name in imports if name!='audio_system_alert_parent_200749ec']
    native={name:(0x45a568 if name=='audio_uart_device_role_get' else
                  int(re.search(r'_([0-9a-f]{6})$',name).group(1),16)) for name in imports}
    lines=['.syntax unified','.thumb','.section .text.oracle_stubs,"ax",%progbits']
    for name in imports:lines += [f'.global {name}','.thumb_func',f'{name}:','  bx lr']
    lines+=['.section .note.GNU-stack,"",%progbits'];stubs.write_text('\n'.join(lines)+'\n')
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2',
                    '-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_system_alert_page_init_4d2f48',
                    str(src),str(storage),str(stubs),'-o',str(elf)],check=True)
    with elf.open('rb') as f:
        image=ELFFile(f)
        segments=[(v['p_vaddr'],v.data()) for v in image.iter_segments() if v['p_type']=='PT_LOAD']
        sym={v.name:v['st_value'] for v in image.get_section_by_name('.symtab').iter_symbols()}
    arity={'audio_uart_page_43de82':1,'audio_uart_page_44104c':1,
           'audio_uart_device_role_get':0,'audio_uart_page_43f6b8':4}
    for name in imports:
        if name not in arity:arity[name]=3 if name.startswith('audio_uart_page_441') or name=='audio_system_alert_page_style_4d2b9c' else 2
    for role in (0,1):
        observations=[]
        for compiled in (False,True):
            u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
            u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
            u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
            for addr,data in segments:u.mem_write(addr,data)
            parent=sym['audio_system_alert_parent_200749ec'] if compiled else 0x200749ec
            child=sym['audio_system_alert_child_200749f0'] if compiled else 0x200749f0
            u.mem_write(parent,(0).to_bytes(4,'little'));u.mem_write(child,(0).to_bytes(4,'little'))
            u.reg_write(UC_ARM_REG_R0,0x20081000);u.reg_write(UC_ARM_REG_R1,0x12345678)
            u.reg_write(UC_ARM_REG_R2,7);u.reg_write(UC_ARM_REG_SP,0x200ff000)
            u.reg_write(UC_ARM_REG_LR,0x600001)
            addresses={((sym[name] if compiled else addr)&~1):name for name,addr in native.items()}
            calls=[];created=[0]
            def hook(uc,address,size,user):
                name=addresses.get(address)
                if name is None:return
                regs=[uc.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)]
                calls.append((name,tuple(regs[:arity[name]])))
                if name=='audio_uart_page_43de82':
                    result=0x20082000 if created[0]==0 else 0x20083000
                    created[0]+=1
                elif name=='audio_uart_page_44104c':result=(regs[0]^0x00a50000)&0xffffffff
                elif name=='audio_uart_device_role_get':result=role
                else:result=0
                uc.reg_write(UC_ARM_REG_R0,result)
                uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
            u.hook_add(UC_HOOK_CODE,hook)
            entry=sym['audio_system_alert_page_init_4d2f48'] if compiled else 0x4d2f48
            u.emu_start(entry|1,0x600000,count=30000)
            observations.append((bytes(u.mem_read(parent,4)),bytes(u.mem_read(child,4)),calls))
        assert observations[0]==observations[1],(role,observations)
receipt={'round':1027,'status':'PASS_SYSTEM_ALERT_PAGE_INIT_NATIVE',
         'component':'Apollo system-alert MainPage ordered construction',
         'source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
         'official_image_sha256':hashlib.sha256(blob).hexdigest(),
         'native_entry':'0x4d2f48','roles':[0,1],
         'validation':'Actual compiled Cortex-M4 C versus official Thumb ordered child calls and parent/child RAM writes',
         'whole_image_complete':False,'hardware_proof':False,
         'gates':['Lower LVGL/style implementations and live display effects remain open',
                  'Final image placement and hardware proof remain open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],len(imports))
