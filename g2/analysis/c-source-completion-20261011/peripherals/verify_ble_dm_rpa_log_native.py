#!/usr/bin/env python3
"""Actual C/native invalid DM RPA WARN diagnostic argument effects."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_dm_rpa_access.c'
STUB='''#include <stdint.h>
#include <stdarg.h>
uint8_t audio_dm_connection_records[512];volatile uint8_t audio_ble_trace_level_cell=1;
uint32_t log_count,log_level,log_path,log_name,log_line,log_format,log_conn;
uint32_t g2_smp_candidate_compare(void*a,uint32_t b,uint32_t c,uint32_t n){(void)a;const uint8_t*x=(void*)b,*y=(void*)c;for(uint32_t i=0;i<n;i++)if(x[i]!=y[i])return 1;return 0;}
uint32_t audio_log_flags(void){return 2;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){
 (void)b;log_count++;log_level=a;log_path=(uint32_t)c;log_name=(uint32_t)d;log_line=e;log_format=(uint32_t)f;
 va_list v;va_start(v,f);log_conn=va_arg(v,uint32_t);va_end(v);}
void audio_ble_wsf_trace(const char*a,const char*b,...){(void)a;(void)b;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2',
                 '-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000',
                 '-Wl,-e,DmConnPeerRpa',str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD']
  sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 for name,native in (('DmConnPeerRpa',0x4b6f28),('DmConnLocalRpa',0x4b707c)):
  pair=[]
  for compiled in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B)
   u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   logs=[]
   def read_str(a):return bytes(u.mem_read(a,160)).split(b'\0')[0].decode(errors='replace')
   if not compiled:
    def hook(uc,pc,n,user):
     if pc==0x4c9c50:uc.reg_write(UC_ARM_REG_R0,1)
     elif pc==0x44b610:
      x,y,size=[uc.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2)]
      uc.reg_write(UC_ARM_REG_R0,int(bytes(uc.mem_read(x,size))!=bytes(uc.mem_read(y,size))))
     elif pc==0x43d0ce:uc.reg_write(UC_ARM_REG_R0,2)
     elif pc==0x43d574:
      sp=uc.reg_read(UC_ARM_REG_SP)
      line,fmt,conn=[int.from_bytes(uc.mem_read(sp+i,4),'little') for i in (0,4,8)]
      logs.append((uc.reg_read(UC_ARM_REG_R0),read_str(uc.reg_read(UC_ARM_REG_R2)),
                   read_str(uc.reg_read(UC_ARM_REG_R3)),line,read_str(fmt),conn))
     uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    for addr in (0x4c9c50,0x44b610,0x43d0ce,0x43d574):u.hook_add(UC_HOOK_CODE,hook,begin=addr,end=addr)
   u.reg_write(UC_ARM_REG_R0,0);u.reg_write(UC_ARM_REG_SP,0x200ff000)
   u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start((sy[name] if compiled else native)|1,0x600000,count=5000)
   if compiled:
    get=lambda n:int.from_bytes(u.mem_read(sy[n],4),'little')
    if get('log_count'):
     logs=[(get('log_level'),read_str(get('log_path')),read_str(get('log_name')),
            get('log_line'),read_str(get('log_format')),get('log_conn'))]
   pair.append((u.reg_read(UC_ARM_REG_R0),logs))
  assert pair[0]==pair[1],(name,pair)
print('PASS_BLE_DM_RPA_LOG_NATIVE 2')
