#!/usr/bin/env python3
"""Bounded actual ARM C/native close and resume event effects (valid conn 1)."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_discovery_events.c'
STUB='''#include <stdint.h>
uint8_t audio_ble_subsystem_rows_200733fc[48],audio_ble_discovery_connection_records_200717b0[0x100];
uint8_t mode[4];const void *audio_ble_profile_dispatch_slot=mode;
uintptr_t audio_ble_service_dispatch_20074348;
void audio_ble_service_discovery_start(uint8_t x){(void)x;}
void audio_ble_service_discovery_followup_5336e0(uint8_t x){(void)x;}
void audio_ble_discovery_config_resume(uint8_t x,uint32_t y){(void)x;(void)y;}
void audio_ble_dm_conn_set_idle(uint8_t x,uint8_t y,uint8_t z){(void)x;(void)y;(void)z;}
uint8_t *audio_ble_pair_record(uint8_t x){(void)x;return 0;}
void audio_ble_pair_record_clear_a(uint8_t*x,uint8_t y){(void)x;(void)y;}
void audio_ble_pair_record_clear_b(uint8_t*x,uint8_t y){(void)x;(void)y;}
void audio_ble_pair_record_attach(uint8_t*x,uint32_t y){(void)x;(void)y;}
uint8_t audio_ble_connection_is_active_4bad26(uint8_t x){(void)x;return 0;}
void g2_wsf_candidate_buffer_free_word(uint32_t x){(void)x;}
void audio_uart_buffer_zero(void*x,uint32_t n,uint32_t v){volatile uint8_t*p=x;for(uint32_t i=0;i<n;i++)p[i]=(uint8_t)v;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_discovery_close_5320c2',str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sym={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 for kind in ('close','resume'):
  results=[]
  for compiled in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   row=sym['audio_ble_subsystem_rows_200733fc'] if compiled else 0x200733fc
   mode=sym['mode'] if compiled else 0x20074400
   if not compiled:u.mem_write(0x20074360,mode.to_bytes(4,'little'))
   u.mem_write(mode,b'\x00\x00\x00\x00')
   data=bytearray(range(16));data[0:4]=b'\x00'*4;data[4:8]=b'\x00'*4;data[12]=0
   if kind=='resume':data[13]=1;data[0:4]=b'\x10\x20\x03\x20'
   u.mem_write(row,bytes(data))
   msg=0x20080000;u.mem_write(msg,b'\x01\x00\x2c\x00\x01\x00\x00\x00')
   calls=[]
   mapping=[('dispatch',None,sym['audio_ble_service_dispatch_20074348'] if compiled else 0x20074348),('start','audio_ble_service_discovery_start',0x531d60),('zero','audio_uart_buffer_zero',0x43c0e4),('resume','audio_ble_discovery_config_resume',0x56c3a6)]
   for name,cname,stock in mapping:
    if name=='dispatch':
     target=0x100f01;u.mem_write(stock,target.to_bytes(4,'little'))
    else:target=sym[cname] if compiled else stock
    def hook(uc,pc,size,user,name=name):
     calls.append((name,uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1)))
     uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook,begin=target&~1,end=target&~1)
   entry=(sym['audio_ble_discovery_close_5320c2'] if kind=='close' else sym['audio_ble_discovery_resume_53223c']) if compiled else (0x5320c2 if kind=='close' else 0x53223c)
   u.reg_write(UC_ARM_REG_R0,msg);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start(entry|1,0x600000,count=1000)
   results.append((bytes(u.mem_read(row,16)),[(n,a if n!='resume' else 1,b if n!='resume' else 0) for n,a,b in calls]))
  assert results[0]==results[1],(kind,results)
print('PASS_BLE_DISCOVERY_EVENTS_NATIVE 2')
