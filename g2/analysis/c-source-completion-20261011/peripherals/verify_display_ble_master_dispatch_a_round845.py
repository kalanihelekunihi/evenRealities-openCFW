#!/usr/bin/env python3
"""Controlled native/C comparison of Apollo BLE master dispatch 0x503b92."""
from pathlib import Path
import hashlib,struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *

root=Path(__file__).resolve().parents[3]
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
src=root/'components/audio/uart_thread_source_candidate/display_ble_master_dispatch_a.c'
children=[0x50366e,0x50367c,0x5037bc,0x5037c4,0x5037d0,0x50393e,0x503b24]
stub='''#include <stdint.h>
uint8_t audio_ble_discovery_connection_records_200717b0[0x90];
volatile uint8_t audio_ble_subsystem_state_20071670[0xa0];
'''+''.join(f'void audio_ble_master_event_{a:x}(void*a,void*b){{(void)a;(void)b;}}\n' for a in children)
with tempfile.TemporaryDirectory() as directory:
    temp=Path(directory);st=temp/'stub.c';st.write_text(stub);elf=temp/'fixture.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb',
                    '-O2','-nostdlib','-Wl,-Ttext=0x100000',
                    '-Wl,-e,audio_ble_comm_master_dispatch_a',str(src),str(st),'-o',str(elf)],check=True)
    with elf.open('rb') as f:
        obj=ELFFile(f)
        segments=[(s['p_vaddr'],s.data()) for s in obj.iter_segments() if s['p_type']=='PT_LOAD']
        symbols={s.name:s['st_value'] for s in obj.get_section_by_name('.symtab').iter_symbols()}
    cases=0
    for event in (0x20,0x24,0x25,0x26,0x27,0x28,0x37,0x40,0x4a,0x4b,0x4c,0x4d):
        for connection in (0,1,2,3,4,0x101):
            pair=[]
            for compiled in (False,True):
                u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
                u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
                u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
                u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
                for address,data in segments:u.mem_write(address,data)
                rows=symbols['audio_ble_discovery_connection_records_200717b0'] if compiled else 0x200717b0
                state=symbols['audio_ble_subsystem_state_20071670'] if compiled else 0x20071670
                u.mem_write(state,b'\xa5'*0xa0)
                message=0x20073000
                u.mem_write(message,struct.pack('<HBB',connection,event,0))
                trace=[]
                for native in children:
                    name=f'audio_ble_master_event_{native:x}'
                    address=symbols[name] if compiled else native
                    def hook(uc,pc,width,user,native=native):
                        r0=uc.reg_read(UC_ARM_REG_R0);r1=uc.reg_read(UC_ARM_REG_R1)
                        trace.append((native,r0==message,None if r1==0 else r1-rows))
                        uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
                    u.hook_add(UC_HOOK_CODE,hook,begin=address&~1,end=address&~1)
                u.reg_write(UC_ARM_REG_SP,0x200ff000)
                u.reg_write(UC_ARM_REG_LR,0x600001)
                u.reg_write(UC_ARM_REG_R0,message)
                try:u.emu_start((symbols['audio_ble_comm_master_dispatch_a'] if compiled else 0x503b92)|1,0x600000,count=3000)
                except Exception as err:raise AssertionError((event,connection,compiled,hex(u.reg_read(UC_ARM_REG_PC)),trace)) from err
                pair.append((trace,bytes(u.mem_read(state,0xa0))))
            assert pair[0]==pair[1],(event,connection,pair)
            cases+=1
print('PASS_DISPLAY_BLE_MASTER_DISPATCH_A_NATIVE',cases)
