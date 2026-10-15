#!/usr/bin/env python3
"""Controlled native/C comparison of Apollo ATT CSF state setter 0x52d090."""
from pathlib import Path
import hashlib,struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *

root=Path(__file__).resolve().parents[3]
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
src=root/'components/audio/uart_thread_source_candidate/display_ble_csf_state.c'
stub='''#include <stdint.h>
volatile uint8_t audio_ble_csf_state_20073e04[16];
uint32_t audio_ble_hci_vendor_log_enabled_4c9c50(void){return 0;}
int32_t audio_l2c_strncmp(const char*a,const char*b,uint32_t n){(void)a;(void)b;(void)n;return 0;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
void audio_ble_wsf_trace(const char*a,...){(void)a;}
'''
with tempfile.TemporaryDirectory() as directory:
    temp=Path(directory);st=temp/'stub.c';st.write_text(stub);elf=temp/'fixture.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb',
                    '-O2','-nostdlib','-Wl,-Ttext=0x100000',
                    '-Wl,-e,audio_ble_dm_service_state_reset_52d090',str(src),str(st),'-o',str(elf)],check=True)
    with elf.open('rb') as f:
        obj=ELFFile(f)
        segments=[(s['p_vaddr'],s.data()) for s in obj.iter_segments() if s['p_type']=='PT_LOAD']
        symbols={s.name:s['st_value'] for s in obj.get_section_by_name('.symtab').iter_symbols()}
    cases=0
    for connection in (0,1,2,3):
        for state in (0,1,3):
            for prior in (0,2):
                for enabled in (0,1):
                    for mask in (0,2):
                        for stop_at in (0,1,2,3,4):
                            pair=[]
                            for compiled in (False,True):
                                u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
                                u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
                                u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
                                u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
                                for addr,data in segments:u.mem_write(addr,data)
                                rows=symbols['audio_ble_csf_state_20073e04'] if compiled else 0x20073e04
                                u.mem_write(rows,bytes([0xaa,prior,0xbb,prior,0xcc,prior])+b'\xdd'*10)
                                trace=[];compares=[0]
                                hooks=[('enabled','audio_ble_hci_vendor_log_enabled_4c9c50',0x4c9c50),
                                       ('strncmp','audio_l2c_strncmp',0x44b610),
                                       ('flags','audio_log_flags',0x43d0ce),
                                       ('extended','audio_log_extended',0x43d574),
                                       ('wsf','audio_ble_wsf_trace',0x52a63c)]
                                for kind,symbol,native in hooks:
                                    addr=symbols[symbol] if compiled else native
                                    def hook(uc,pc,width,user,kind=kind):
                                        regs=tuple(uc.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3))
                                        if kind=='enabled':
                                            trace.append((kind,));uc.reg_write(UC_ARM_REG_R0,enabled)
                                        elif kind=='strncmp':
                                            compares[0]+=1
                                            a=bytes(uc.mem_read(regs[0],regs[2])).split(b'\0')[0]
                                            b=bytes(uc.mem_read(regs[1],regs[2])).split(b'\0')[0]
                                            trace.append((kind,a,b,regs[2]))
                                            uc.reg_write(UC_ARM_REG_R0,0 if compares[0]==stop_at else 1)
                                        elif kind=='flags':
                                            trace.append((kind,));uc.reg_write(UC_ARM_REG_R0,mask)
                                        elif kind=='extended':
                                            strings=tuple(bytes(uc.mem_read(p,150)).split(b'\0')[0] for p in regs[1:4])
                                            line,fmt=struct.unpack('<II',uc.mem_read(uc.reg_read(UC_ARM_REG_SP),8))
                                            trace.append((kind,regs[0],*strings,line,bytes(uc.mem_read(fmt,120)).split(b'\0')[0]))
                                        else:
                                            trace.append((kind,bytes(uc.mem_read(regs[0],100)).split(b'\0')[0],
                                                          bytes(uc.mem_read(regs[1],120)).split(b'\0')[0],regs[2],regs[3]))
                                        uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
                                    u.hook_add(UC_HOOK_CODE,hook,begin=addr&~1,end=addr&~1)
                                u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
                                u.reg_write(UC_ARM_REG_R0,connection);u.reg_write(UC_ARM_REG_R1,state)
                                try:u.emu_start((symbols['audio_ble_dm_service_state_reset_52d090'] if compiled else 0x52d090)|1,0x600000,count=15000)
                                except Exception as err:raise AssertionError((connection,state,prior,enabled,mask,stop_at,compiled,hex(u.reg_read(UC_ARM_REG_PC)),trace)) from err
                                pair.append((bytes(u.mem_read(rows,16)),trace))
                            assert pair[0]==pair[1],(connection,state,prior,enabled,mask,stop_at,pair)
                            cases+=1
print('PASS_DISPLAY_BLE_CSF_NATIVE',cases)
