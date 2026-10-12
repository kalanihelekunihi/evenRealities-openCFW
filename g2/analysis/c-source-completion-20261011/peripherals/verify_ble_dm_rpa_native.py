#!/usr/bin/env python3
"""Actual C/native DM RPA pointer and invalid-connection warning effects."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_dm_rpa_access.c'
STUB='''#include <stdint.h>
uint8_t audio_dm_connection_records[512];volatile uint8_t audio_ble_trace_level_cell;
uint32_t trace_count,trace_value;
uint32_t g2_smp_candidate_compare(void*a,uint32_t b,uint32_t c,uint32_t d){(void)a;(void)b;(void)c;(void)d;return 1;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
void audio_ble_wsf_trace(const char*a,const char*b,uint32_t c){(void)a;(void)b;trace_count++;trace_value=c;}
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
  for conn in (0,1,3):
   pair=[]
   for compiled in (False,True):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B)
    u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
    for addr,data in seg:u.mem_write(addr,data)
    base=sy['audio_dm_connection_records'] if compiled else 0x200712a4
    calls=[]
    if not compiled:
     def hook(uc,pc,n,user):
      if pc==0x4c9c50:uc.reg_write(UC_ARM_REG_R0,0)
      elif pc==0x52a63c:calls.append(uc.reg_read(UC_ARM_REG_R2))
      uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
     for addr in (0x4c9c50,0x52a63c):u.hook_add(UC_HOOK_CODE,hook,begin=addr,end=addr)
    u.reg_write(UC_ARM_REG_R0,conn);u.reg_write(UC_ARM_REG_SP,0x200ff000)
    u.reg_write(UC_ARM_REG_LR,0x600001)
    u.emu_start((sy[name] if compiled else native)|1,0x600000,count=3000)
    if compiled:
     n=int.from_bytes(u.mem_read(sy['trace_count'],4),'little')
     calls=[int.from_bytes(u.mem_read(sy['trace_value'],4),'little')]*n
    result=u.reg_read(UC_ARM_REG_R0)
    pair.append((result-base if result else 0,calls))
   assert pair[0]==pair[1],(name,conn,pair)
print('PASS_BLE_DM_RPA_NATIVE 6')
