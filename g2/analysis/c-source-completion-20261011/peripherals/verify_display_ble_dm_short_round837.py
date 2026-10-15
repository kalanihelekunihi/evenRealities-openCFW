#!/usr/bin/env python3
"""Controlled native/C comparison of four authenticated Apollo BLE DM leaves."""
from pathlib import Path
import hashlib,struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *

root=Path(__file__).resolve().parents[3]
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
src=root/'components/audio/uart_thread_source_candidate/display_ble_dm_short.c'
stub='''#include <stdint.h>
uint8_t audio_ble_discovery_connection_records_200717b0[0x300];
uint8_t audio_ble_dm_conn_state_table_20067a30[2000];
uint8_t audio_ble_dm_database_hash_20068215[16];
int32_t g2_lfs_memcmp(const void*a,const void*b,uint32_t n){(void)a;(void)b;(void)n;return 0;}
uint32_t audio_ble_hci_vendor_log_enabled_4c9c50(void){return 0;}
int32_t audio_l2c_strncmp(const char*a,const char*b,uint32_t n){(void)a;(void)b;(void)n;return 0;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
void audio_ble_wsf_trace(const char*a,...){(void)a;}
void audio_ble_dm_service_state_reset_52d090(uint32_t a,uint32_t b){(void)a;(void)b;}
void audio_ble_dm_advertising_resume_4b5a44(uint32_t a,uint32_t b,uint32_t c){(void)a;(void)b;(void)c;}
'''
functions=[('audio_ble_dm_connection_record_get',0x4bb07c),
           ('audio_ble_dm_connection_state_set',0x47b438),
           ('audio_ble_comm_dm_connected_53480c',0x53480c),
           ('audio_ble_comm_dm_dispatch_b',0x53484c)]
with tempfile.TemporaryDirectory() as directory:
    temp=Path(directory);st=temp/'stub.c';st.write_text(stub);elf=temp/'fixture.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb',
                    '-O2','-nostdlib','-Wl,-Ttext=0x100000',
                    '-Wl,-e,audio_ble_comm_dm_dispatch_b',str(src),str(st),'-o',str(elf)],check=True)
    with elf.open('rb') as f:
        obj=ELFFile(f)
        segments=[(s['p_vaddr'],s.data()) for s in obj.iter_segments() if s['p_type']=='PT_LOAD']
        symbols={s.name:s['st_value'] for s in obj.get_section_by_name('.symtab').iter_symbols()}
    cases=0
    for name,native in functions:
        for event in (0x12,0x15,0x17):
            for embedded in (0x12,0x15):
                for connection in (1,2):
                    for found in (0,0x20072000):
                        for state in (0,3):
                            pair=[]
                            for compiled in (False,True):
                                u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
                                u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
                                u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
                                u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
                                for addr,data in segments:u.mem_write(addr,data)
                                records=(symbols['audio_ble_discovery_connection_records_200717b0'] if compiled else 0x200717b0)
                                states=(symbols['audio_ble_dm_conn_state_table_20067a30'] if compiled else 0x20067a30)
                                u.mem_write(records+0x30*(connection-1),struct.pack('<I',found))
                                u.mem_write(states,bytes([0xaa])*2000)
                                u.mem_write(0x20072000,bytes([0xbb])*200)
                                msg=0x20073000
                                data=bytearray(16);data[0]=connection;data[2]=event;data[10]=embedded
                                u.mem_write(msg,bytes(data))
                                trace=[]
                                hookaddr=(symbols['audio_ble_comm_dm_disconnect_5346e4'] if compiled else 0x5346e4)
                                def hook(uc,pc,width,user):
                                    trace.append(('disconnect',uc.reg_read(UC_ARM_REG_R0)))
                                    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
                                u.hook_add(UC_HOOK_CODE,hook,begin=hookaddr&~1,end=hookaddr&~1)
                                u.reg_write(UC_ARM_REG_SP,0x200ff000)
                                u.reg_write(UC_ARM_REG_LR,0x600001)
                                if name=='audio_ble_dm_connection_record_get':
                                    u.reg_write(UC_ARM_REG_R0,connection)
                                elif name=='audio_ble_dm_connection_state_set':
                                    u.reg_write(UC_ARM_REG_R0,found)
                                    u.reg_write(UC_ARM_REG_R1,state)
                                else:u.reg_write(UC_ARM_REG_R0,msg)
                                try:u.emu_start((symbols[name] if compiled else native)|1,0x600000,count=2000)
                                except Exception as err:raise AssertionError((name,event,embedded,connection,found,state,compiled,hex(u.reg_read(UC_ARM_REG_PC)),trace)) from err
                                pair.append((u.reg_read(UC_ARM_REG_R0) if name=='audio_ble_dm_connection_record_get' else None,
                                             trace,bytes(u.mem_read(states,2000)),bytes(u.mem_read(0x20072000,200))))
                            assert pair[0]==pair[1],(name,event,embedded,connection,found,state,pair)
                            cases+=1
print('PASS_DISPLAY_BLE_DM_SHORT_NATIVE',cases)
