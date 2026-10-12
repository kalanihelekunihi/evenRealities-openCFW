#!/usr/bin/env python3
"""Actual ARM C/native SMP transition and fallback comparisons with controlled tables."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_smp_sm_execute.c'
STUB='''#include <stdint.h>
uint8_t audio_ble_smp_handler_state[0xfc];volatile uint8_t audio_ble_trace_level_cell;
uint8_t audio_dm_conn_role(uint8_t x){(void)x;return 0;}
uint32_t g2_smp_candidate_compare(void*a,uint32_t b,uint32_t c,uint32_t d){(void)a;(void)b;(void)c;(void)d;return 1;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
void audio_ble_wsf_trace(const char*a,const char*b,...){(void)a;(void)b;}
const char *smpStateStr(uint8_t x){(void)x;return "";}
const char *smpEventStr(uint8_t x){(void)x;return "";}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib',
                 '-Wl,-Ttext=0x100000','-Wl,-e,smpSmExecute',str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD']
  sym={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 for case in ('match','fallback'):
  pair=[]
  for compiled in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B)
   u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   state=sym['audio_ble_smp_handler_state'] if compiled else 0x20070aec
   ptr=lambda v:v.to_bytes(4,'little')
   u.mem_write(state+0xe8,ptr(0x20080000))
   u.mem_write(0x20080000,ptr(0x20080100)+ptr(0x20080200)+ptr(0x20080300))
   u.mem_write(0x20080100,ptr(0x20080400))
   u.mem_write(0x20080200,ptr(0x500001))
   u.mem_write(0x20080300,b'\x02\x00\x00\x03\x00\x00\x04\x00\x00\x05\x00\x00\x00\x00\x00')
   u.mem_write(0x20080400,b'\x07\x09\x00\x00\x00\x00')
   ccb=0x20080500;msg=0x20080600
   c=bytearray(0x4c);c[0x3d]=1;u.mem_write(ccb,bytes(c));u.mem_write(msg,b'\x01\x00'+(b'\x07' if case=='match' else b'\x09')+b'\x00')
   hits=[]
   def hook(uc,pc,n,user):
    if pc==0x500000:hits.append('action')
    elif pc not in (0x4c9c50,0x52a63c,0x4b73c4):return
    uc.reg_write(UC_ARM_REG_R0,0)
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   if not compiled:
    for a in (0x4c9c50,0x52a63c,0x4b73c4):u.hook_add(UC_HOOK_CODE,hook,begin=a,end=a)
   u.hook_add(UC_HOOK_CODE,hook,begin=0x500000,end=0x500000)
   u.reg_write(UC_ARM_REG_R0,ccb);u.reg_write(UC_ARM_REG_R1,msg)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start((sym['smpSmExecute'] if compiled else 0x56ee62)|1,0x600000,count=10000)
   pair.append((u.mem_read(ccb+0x3e,1),hits))
  assert pair[0]==pair[1],(case,pair)
print('PASS_BLE_SMP_EXECUTE_NATIVE 2')
