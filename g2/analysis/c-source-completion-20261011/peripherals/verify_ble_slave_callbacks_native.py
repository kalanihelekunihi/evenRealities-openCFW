#!/usr/bin/env python3
"""Bounded original/C effects for the three native slave delayed callbacks."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *

R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_slave_proc_callbacks.c'
STUB='''
#include <stdint.h>
uint8_t *audio_ble_slave_mode_context;
uint8_t *audio_ble_profile_connection_context;
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...){(void)a;(void)b;(void)c;return 0;}
__attribute__((noinline)) void audio_ble_slave_security_state(uint8_t a){asm volatile(""::"r"(a));}
__attribute__((noinline)) void *audio_wsf_msg_alloc(uint16_t a){asm volatile(""::"r"(a));return 0;}
void audio_wsf_msg_send(uint8_t a,void*b){(void)a;(void)b;}
'''
with tempfile.TemporaryDirectory() as td:
    src=Path(td)/'stubs.c';src.write_text(STUB);e=Path(td)/'x.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib',
                    '-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_slave_open_followup',str(S),str(src),'-o',str(e)],check=True)
    with e.open('rb') as f:
        x=ELFFile(f)
        seg=[(s['p_vaddr'],s.data()) for s in x.iter_segments() if s['p_type']=='PT_LOAD']
        sym={s.name:s['st_value'] for s in x.get_section_by_name('.symtab').iter_symbols()}
    tests=[('audio_ble_slave_open_followup',0x46f098,0,False),
           ('audio_ble_slave_open_watchdog',0x46f350,0,False),
           ('audio_ble_slave_open_watchdog',0x46f350,1,False),
           ('audio_ble_slave_open_watchdog',0x46f350,255,False),
           ('audio_ble_slave_disconnect_followup',0x46effc,0,False),
           ('audio_ble_slave_disconnect_followup',0x46effc,1,False),
           ('audio_ble_slave_disconnect_followup',0x46effc,0,True),
           ('audio_ble_slave_disconnect_followup',0x46effc,1,True)]
    for name,native,arg,allocated in tests:
        pair=[]
        for is_c in (False,True):
            u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
            u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
            u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B)
            u.mem_map(0x100000,0x100000)
            u.mem_map(0x20000000,0x100000)
            for a,d in seg:u.mem_write(a,d)
            u.mem_write(0x20074330,struct.pack('<I',0x20030000))
            u.mem_write(0x2007432c,struct.pack('<I',0x20031000))
            u.mem_write(0x20031054,b'\x03')
            if is_c:
                u.mem_write(sym['audio_ble_slave_mode_context'],struct.pack('<I',0x20030000))
                u.mem_write(sym['audio_ble_profile_connection_context'],struct.pack('<I',0x20031000))
            u.reg_write(UC_ARM_REG_SP,0x200ff000)
            u.reg_write(UC_ARM_REG_LR,0x600001)
            u.reg_write(UC_ARM_REG_R0,arg)
            events=[]
            def hook(uc,a,size,_):
                if a in (0x43d0ce,sym['audio_log_flags']&~1):
                    uc.reg_write(UC_ARM_REG_R0,0)
                    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
                elif a in (0x4b82e8,sym['audio_ble_slave_security_state']&~1):
                    events.append(('security',uc.reg_read(UC_ARM_REG_R0)&255))
                    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
                elif a in (0x4bf99e,sym['audio_wsf_msg_alloc']&~1):
                    events.append(('alloc',uc.reg_read(UC_ARM_REG_R0)))
                    uc.reg_write(UC_ARM_REG_R0,0x20032000 if allocated else 0)
                    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
                elif a in (0x4bf9ba,sym['audio_wsf_msg_send']&~1):
                    events.append(('send',uc.reg_read(UC_ARM_REG_R0),
                                   bytes(uc.mem_read(uc.reg_read(UC_ARM_REG_R1),10))))
                    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
            u.hook_add(UC_HOOK_CODE,hook)
            u.emu_start((sym[name] if is_c else native)|1,0x600000,count=400)
            pair.append((events,u.mem_read(0x20030020,1)[0]))
        assert pair[0]==pair[1],(name,arg,pair)
    print('PASS_BLE_SLAVE_CALLBACKS_NATIVE',len(tests))
