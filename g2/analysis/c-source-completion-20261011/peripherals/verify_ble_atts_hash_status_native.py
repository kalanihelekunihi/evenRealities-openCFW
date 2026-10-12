#!/usr/bin/env python3
"""Actual C/native ATT hash update state transitions with trace disabled."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_atts_hash_status_set.c'
STUB='''#include <stdint.h>
uint8_t audio_ble_connection_state_table[32];volatile uint8_t audio_ble_trace_level_cell;
uint32_t pending_count,trace_count;
uint32_t g2_smp_candidate_compare(void*a,uint32_t b,uint32_t c,uint32_t d){(void)a;(void)b;(void)c;(void)d;return 1;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
void audio_ble_wsf_trace(const char*a,const char*b,...){(void)a;(void)b;trace_count++;}
void attsCheckPendDbHashReadRsp(void){pending_count++;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2',
                 '-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000',
                 '-Wl,-e,attsCsfSetHashUpdateStatus',str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD']
  sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 for initial,target in ((0,0),(0,1),(1,0),(1,1)):
  pair=[]
  for compiled in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B)
   u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   state=sy['audio_ble_connection_state_table'] if compiled else 0x20073e04
   u.mem_write(state,bytes([0,2,0,2,0,1]+[0]*26));u.mem_write(state+0xc,bytes([initial]))
   calls=[]
   if not compiled:
    def hook(uc,pc,n,user):
     if pc==0x4c9c50:uc.reg_write(UC_ARM_REG_R0,0)
     elif pc==0x52a63c:calls.append('trace')
     elif pc==0x534dd8:calls.append('pending')
     uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    for addr in (0x4c9c50,0x52a63c,0x534dd8):u.hook_add(UC_HOOK_CODE,hook,begin=addr,end=addr)
   u.reg_write(UC_ARM_REG_R0,target);u.reg_write(UC_ARM_REG_SP,0x200ff000)
   u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start((sy['attsCsfSetHashUpdateStatus'] if compiled else 0x52c6c0)|1,0x600000,count=5000)
   if compiled:
    n=lambda x:int.from_bytes(u.mem_read(sy[x],4),'little')
    calls=['trace']*n('trace_count')+['pending']*n('pending_count')
   pair.append((bytes(u.mem_read(state,16)),calls))
  assert pair[0]==pair[1],(initial,target,pair)
print('PASS_BLE_ATTS_HASH_STATUS_NATIVE 4')
