#!/usr/bin/env python3
"""Compare system-alert update branches and lower calls with Apollo Thumb."""
from pathlib import Path
import hashlib,json,re,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *

root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/system-alert-page-update-native-round1031';out.mkdir(parents=True,exist_ok=True)
src=root/'components/audio/uart_thread_source_candidate/system_alert_page_update_4d30ba.c'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
with tempfile.TemporaryDirectory() as td:
    td=Path(td);elf=td/'c.elf';obj=td/'source.o';stubs=td/'stubs.s';storage=td/'storage.c'
    storage.write_text('#include <stdint.h>\n'
        'uint32_t audio_system_alert_parent_200749ec, audio_system_alert_child_200749f0;\n'
        'uint32_t audio_system_alert_page_id_20003bcc; uint8_t audio_system_alert_active_20075025;\n'
        'uint32_t audio_system_alert_message_notify;\n'
        'const uint8_t audio_system_alert_icon_disconnect_7747e4[16]={0x19,0x06};\n'
        'const uint8_t audio_system_alert_icon_connect_772928[16]={0x19,0x06};\n')
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2',
                    '-c',str(src),'-o',str(obj)],check=True)
    imports=[line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','-u',str(obj)],text=True).splitlines()]
    data={'audio_system_alert_parent_200749ec','audio_system_alert_child_200749f0',
          'audio_system_alert_page_id_20003bcc','audio_system_alert_active_20075025',
          'audio_system_alert_icon_disconnect_7747e4','audio_system_alert_icon_connect_772928'}
    data.add('audio_system_alert_message_notify')
    code=[name for name in imports if name not in data]
    special={'audio_log_flags':0x43d0ce,'audio_log_extended':0x43d574,
             'compressed_log_output':0x43ce9e,'audio_uart_device_role_get':0x45a568}
    native={name:special.get(name) or int(re.search(r'_([0-9a-f]{6})$',name).group(1),16) for name in code}
    lines=['.syntax unified','.thumb','.section .text.oracle_stubs,"ax",%progbits']
    for name in code:lines += [f'.global {name}','.thumb_func',f'{name}:','  bx lr']
    lines+=['.section .note.GNU-stack,"",%progbits'];stubs.write_text('\n'.join(lines)+'\n')
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2',
                    '-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_system_alert_page_update_4d30ba',
                    str(src),str(storage),str(stubs),'-o',str(elf)],check=True)
    with elf.open('rb') as f:
        image=ELFFile(f)
        segments=[(v['p_vaddr'],v.data()) for v in image.iter_segments() if v['p_type']=='PT_LOAD']
        sym={v.name:v['st_value'] for v in image.get_section_by_name('.symtab').iter_symbols()}
    one={'audio_uart_page_44d878','audio_uart_page_498668','audio_uart_page_499416',
         'audio_uart_page_44104c','audio_uart_page_460084','audio_uart_page_43f66c',
         'audio_uart_device_role_get'}
    two={'audio_uart_page_498680','audio_uart_page_43f506','audio_uart_page_43f568',
         'audio_uart_page_43f0e0','audio_uart_page_43f142','audio_uart_page_43ded4',
         'audio_uart_page_43dfa4','audio_uart_page_45fffe','audio_uart_page_49942e'}
    arity={name:(1 if name in one else 2 if name in two else
                 4 if name in {'audio_uart_page_43f6b8','audio_system_alert_close_464c36'} else 3)
           for name in code}
    cases=[(None,0,0,0),(None,0,1,0),(None,0,1,1),(None,0,2,0),
           (None,0,2,1),(None,0,3,1),(bytes([5]),1,1,1),
           (bytes([7]),1,2,1),(bytes([7]),0,2,0)]
    for payload,length,mode,role in cases:
        observations=[]
        for compiled in (False,True):
            u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
            u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
            u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
            for addr,segment in segments:u.mem_write(addr,segment)
            def cell(name,addr):return sym[name] if compiled else addr
            parent=cell('audio_system_alert_parent_200749ec',0x200749ec)
            child=cell('audio_system_alert_child_200749f0',0x200749f0)
            page=cell('audio_system_alert_page_id_20003bcc',0x20003bcc)
            active=cell('audio_system_alert_active_20075025',0x20075025)
            mode_addr=cell('audio_system_alert_message_notify',0x200749f4)
            font=cell('audio_system_alert_font_200746e0',0x200746e0)
            for addr,value in ((parent,0x20082000),(child,0x20083000),(page,0xdeadbeef),
                               (mode_addr,mode),(font,0x12345678)):
                u.mem_write(addr,value.to_bytes(4,'little'))
            u.mem_write(active,b'\x7a')
            payload_addr=0x20081000
            if payload is not None:u.mem_write(payload_addr,payload)
            u.reg_write(UC_ARM_REG_R0,payload_addr if payload is not None else 0)
            u.reg_write(UC_ARM_REG_R1,length);u.reg_write(UC_ARM_REG_R2,0);u.reg_write(UC_ARM_REG_R3,0)
            u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
            addresses={((sym[name] if compiled else addr)&~1):name for name,addr in native.items()}
            calls=[]
            def normalized(name,args):
                args=list(args)
                if name=='audio_uart_page_498680':
                    d=cell('audio_system_alert_icon_disconnect_7747e4',0x7747e4)
                    c=cell('audio_system_alert_icon_connect_772928',0x772928)
                    args[1]='disconnect' if args[1]==d else 'connect' if args[1]==c else hex(args[1])
                if name in ('audio_uart_page_460084','audio_uart_page_45fffe'):
                    p=args[0];s=bytes(uc_byte for uc_byte in u.mem_read(p,32)).split(b'\0')[0]
                    args[0]=s.decode('ascii','replace')
                return tuple(args)
            def hook(uc,address,size,user):
                name=addresses.get(address)
                if name is None:return
                regs=[uc.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)]
                if name not in ('audio_log_flags','audio_log_extended','compressed_log_output'):
                    calls.append((name,normalized(name,regs[:arity[name]])))
                if name=='audio_uart_page_498668':result=0x20084000
                elif name=='audio_uart_page_499416':result=0x20085000
                elif name=='audio_uart_page_460084':result=0x1001
                elif name=='audio_uart_page_45fffe':result=0x20086000
                elif name=='audio_uart_page_44104c':result=regs[0]^0x00a50000
                elif name=='audio_uart_device_role_get':result=role
                else:result=0
                uc.reg_write(UC_ARM_REG_R0,result)
                uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
            u.hook_add(UC_HOOK_CODE,hook)
            entry=sym['audio_system_alert_page_update_4d30ba'] if compiled else 0x4d30ba
            u.emu_start(entry|1,0x600000,count=50000)
            observations.append((bytes(u.mem_read(page,4)),bytes(u.mem_read(active,1)),calls))
        assert observations[0]==observations[1],((payload,length,mode,role),observations)
receipt={'round':1031,'status':'PASS_SYSTEM_ALERT_PAGE_UPDATE_NATIVE',
         'component':'Apollo system-alert page update payload/mode/role branches',
         'source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
         'official_image_sha256':hashlib.sha256(blob).hexdigest(),
         'native_entry':'0x4d30ba','cases':len(cases),
         'validation':'Actual compiled Cortex-M4 C versus official Thumb ordered lower calls and RAM effects',
         'whole_image_complete':False,'hardware_proof':False,
         'gates':['Logging-enabled effects and icon ROM allocation extents remain open',
                  'Lower LVGL bodies, final image placement and hardware proof remain open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],len(cases),len(code))
