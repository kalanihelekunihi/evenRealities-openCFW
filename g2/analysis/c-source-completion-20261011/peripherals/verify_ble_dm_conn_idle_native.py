#!/usr/bin/env python3
"""Bounded actual C/stock DM idle-mask and trace-disabled path."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_dm_conn_idle.c'
STUB='''#include <stdint.h>
uint8_t audio_dm_connection_records[256];volatile uint8_t audio_ble_trace_level_cell;
uint32_t in_use,lock_count,unlock_count,trace_count,trace_conn,trace_mask;
void WsfTaskLock(void){lock_count++;}void WsfTaskUnlock(void){unlock_count++;}
uint8_t DmConnInUse(uint8_t c){(void)c;return in_use;}
uint32_t g2_smp_candidate_compare(void*a,uint32_t b,uint32_t c,uint32_t d){(void)a;(void)b;(void)c;(void)d;return 1;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
void audio_ble_wsf_trace(const char*a,const char*b,uint32_t c,uint32_t d){(void)a;(void)b;trace_count++;trace_conn=c;trace_mask=d;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2',
                 '-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,DmConnSetIdle',
                 str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD']
  sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 for in_use in (0,1):
  for idle in (0,1):
   pair=[]
   for compiled in (False,True):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B)
    u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
    for a,d in seg:u.mem_write(a,d)
    base=sy['audio_dm_connection_records'] if compiled else 0x200712a4
    slot=base+0x30-0x22
    u.mem_write(slot,(0x5a5a).to_bytes(2,'little'))
    if compiled:u.mem_write(sy['in_use'],in_use.to_bytes(4,'little'))
    calls=[]
    if not compiled:
     def hook(uc,pc,n,user):
      if pc==0x4b6ec6:uc.reg_write(UC_ARM_REG_R0,in_use)
      elif pc==0x4c9c50:uc.reg_write(UC_ARM_REG_R0,0)
      elif pc==0x52a63c:
       calls.append(('trace',uc.reg_read(UC_ARM_REG_R2),uc.reg_read(UC_ARM_REG_R3)))
      elif pc==0x52b8c8:calls.append(('lock',))
      elif pc==0x52b8d0:calls.append(('unlock',))
      uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
     for a in (0x4b6ec6,0x4c9c50,0x52a63c,0x52b8c8,0x52b8d0):
      u.hook_add(UC_HOOK_CODE,hook,begin=a,end=a)
    u.reg_write(UC_ARM_REG_R0,1);u.reg_write(UC_ARM_REG_R1,0x0600)
    u.reg_write(UC_ARM_REG_R2,idle);u.reg_write(UC_ARM_REG_SP,0x200ff000)
    u.reg_write(UC_ARM_REG_LR,0x600001)
    u.emu_start((sy['DmConnSetIdle'] if compiled else 0x4b71dc)|1,0x600000,count=8000)
    if compiled:
     get=lambda n:int.from_bytes(u.mem_read(sy[n],4),'little')
     calls=[('lock',)]*get('lock_count')+[('unlock',)]*get('unlock_count')
     if get('trace_count'):calls.append(('trace',get('trace_conn'),get('trace_mask')))
    pair.append((bytes(u.mem_read(slot,2)),calls))
   assert pair[0]==pair[1],(in_use,idle,pair)
print('PASS_BLE_DM_CONN_IDLE_NATIVE 4')
