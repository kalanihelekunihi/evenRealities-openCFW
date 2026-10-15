#!/usr/bin/env python3
"""Controlled native/C comparison of four Apollo master BLE event leaves."""
from pathlib import Path
import hashlib,struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *

root=Path(__file__).resolve().parents[3]
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
src=root/'components/audio/uart_thread_source_candidate/display_ble_master_short_children.c'
functions=[0x50366e,0x5037bc,0x5037c4,0x5037d0]
children=[0x503540,0x503568,0x4bb25c,0x4bb21c]
stub='''#include <stdint.h>
volatile uint8_t audio_ble_subsystem_state_20071670[0xa0];
'''+''.join(f'void audio_ble_master_child_{a:x}(void*a,void*b){{(void)a;(void)b;}}\n' if a in (0x503540,0x503568) else f'void audio_ble_master_child_{a:x}(uint32_t a){{(void)a;}}\n' for a in children)
with tempfile.TemporaryDirectory() as directory:
    temp=Path(directory);st=temp/'stub.c';st.write_text(stub);elf=temp/'fixture.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb',
                    '-O2','-nostdlib','-Wl,-Ttext=0x100000',
                    '-Wl,-e,audio_ble_master_event_50366e',str(src),str(st),'-o',str(elf)],check=True)
    with elf.open('rb') as f:
        obj=ELFFile(f)
        segments=[(s['p_vaddr'],s.data()) for s in obj.iter_segments() if s['p_type']=='PT_LOAD']
        symbols={s.name:s['st_value'] for s in obj.get_section_by_name('.symtab').iter_symbols()}
    cases=0
    for native in functions:
        for event_byte in (0,1,0xff):
            for connection in (0,1,0xff):
                pair=[]
                for compiled in (False,True):
                    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
                    u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
                    u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
                    u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
                    for addr,data in segments:u.mem_write(addr,data)
                    state=symbols['audio_ble_subsystem_state_20071670'] if compiled else 0x20071670
                    u.mem_write(state+0x9c,b'\xa5')
                    message=0x20071000;record=0x20071100
                    u.mem_write(message,bytes([connection,0,event_byte,event_byte]))
                    u.mem_write(record,struct.pack('<I',0x12345678)+b'\xaa'*12)
                    trace=[]
                    for child in children:
                        name=f'audio_ble_master_child_{child:x}'
                        address=symbols[name] if compiled else child
                        def hook(uc,pc,width,user,child=child):
                            r0=uc.reg_read(UC_ARM_REG_R0);r1=uc.reg_read(UC_ARM_REG_R1)
                            trace.append((child,r0,r1==record) if child in (0x503540,0x503568) else (child,r0))
                            uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
                        u.hook_add(UC_HOOK_CODE,hook,begin=address&~1,end=address&~1)
                    u.reg_write(UC_ARM_REG_SP,0x200ff000)
                    u.reg_write(UC_ARM_REG_LR,0x600001)
                    u.reg_write(UC_ARM_REG_R0,message);u.reg_write(UC_ARM_REG_R1,record)
                    start=symbols[f'audio_ble_master_event_{native:x}'] if compiled else native
                    try:u.emu_start(start|1,0x600000,count=3000)
                    except Exception as err:raise AssertionError((native,event_byte,connection,compiled,hex(u.reg_read(UC_ARM_REG_PC)),trace)) from err
                    pair.append((trace,bytes(u.mem_read(record,8)),bytes(u.mem_read(state+0x9c,1))))
                assert pair[0]==pair[1],(native,event_byte,connection,pair)
                cases+=1
print('PASS_DISPLAY_BLE_MASTER_SHORT_NATIVE',cases)
