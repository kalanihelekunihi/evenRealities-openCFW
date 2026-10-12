#!/usr/bin/env python3
"""Actual C/stock DM idle INFO diagnostic branch, including two format args."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_dm_conn_idle.c'
STUB='''#include <stdint.h>
#include <stdarg.h>
uint8_t audio_dm_connection_records[256];volatile uint8_t audio_ble_trace_level_cell=1;
uint32_t log_count,log_level,log_line,log_conn,log_mask,log_path,log_name,log_format;
void WsfTaskLock(void){}void WsfTaskUnlock(void){}
uint8_t DmConnInUse(uint8_t c){(void)c;return 1;}
uint32_t g2_smp_candidate_compare(void*a,uint32_t b,uint32_t c,uint32_t n){(void)a;const uint8_t*x=(void *)b,*y=(void *)c;for(uint32_t i=0;i<n;i++)if(x[i]!=y[i])return 1;return 0;}
uint32_t audio_log_flags(void){return 2;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){
 (void)b;log_count++;log_level=a;log_path=(uint32_t)c;log_name=(uint32_t)d;log_line=e;log_format=(uint32_t)f;
 va_list v;va_start(v,f);log_conn=va_arg(v,uint32_t);log_mask=va_arg(v,uint32_t);va_end(v);}
void audio_ble_wsf_trace(const char*a,const char*b,...){(void)a;(void)b;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2',
                 '-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,DmConnSetIdle',
                 str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD']
  sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 for idle in (0,1):
  pair=[]
  for compiled in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B)
   u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   base=sy['audio_dm_connection_records'] if compiled else 0x200712a4
   slot=base+0x0e;u.mem_write(slot,(0x5a5a).to_bytes(2,'little'))
   logs=[]
   def read_str(addr):return bytes(u.mem_read(addr,160)).split(b'\0')[0].decode(errors='replace')
   if not compiled:
    def hook(uc,pc,n,user):
     if pc==0x4b6ec6:uc.reg_write(UC_ARM_REG_R0,1)
     elif pc==0x4c9c50:uc.reg_write(UC_ARM_REG_R0,1)
     elif pc==0x44b610:
      x,y,size=[uc.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2)]
      uc.reg_write(UC_ARM_REG_R0,0 if bytes(uc.mem_read(x,size))==bytes(uc.mem_read(y,size)) else 1)
     elif pc==0x43d0ce:uc.reg_write(UC_ARM_REG_R0,2)
     elif pc==0x43d574:
      sp=uc.reg_read(UC_ARM_REG_SP)
      line,fmt,conn,mask=[int.from_bytes(uc.mem_read(sp+i,4),'little') for i in (0,4,8,12)]
      logs.append((uc.reg_read(UC_ARM_REG_R0),read_str(uc.reg_read(UC_ARM_REG_R2)),
                   read_str(uc.reg_read(UC_ARM_REG_R3)),line,read_str(fmt),conn,mask))
     uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    for a in (0x52b8c8,0x52b8d0,0x4b6ec6,0x4c9c50,0x44b610,0x43d0ce,0x43d574):
     u.hook_add(UC_HOOK_CODE,hook,begin=a,end=a)
   u.reg_write(UC_ARM_REG_R0,1);u.reg_write(UC_ARM_REG_R1,0x0600)
   u.reg_write(UC_ARM_REG_R2,idle);u.reg_write(UC_ARM_REG_SP,0x200ff000)
   u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start((sy['DmConnSetIdle'] if compiled else 0x4b71dc)|1,0x600000,count=9000)
   if compiled:
    val=lambda n:int.from_bytes(u.mem_read(sy[n],4),'little')
    if val('log_count'):
     logs=[(val('log_level'),read_str(val('log_path')),read_str(val('log_name')),
            val('log_line'),read_str(val('log_format')),val('log_conn'),val('log_mask'))]
   pair.append((bytes(u.mem_read(slot,2)),logs))
  assert pair[0]==pair[1],(idle,pair)
print('PASS_BLE_DM_CONN_IDLE_LOG_NATIVE 2')
