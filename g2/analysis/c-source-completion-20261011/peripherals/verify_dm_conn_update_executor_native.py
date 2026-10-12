#!/usr/bin/env python3
"""Compare source-derived four-event DM update dispatch with native effects."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_dm_conn_update_executor.c'
SHIM='''#include <stdint.h>
uint8_t audio_ble_dm_master_state_b[12];
void audio_ble_dm_conn_update_trace_entry(const void*a,const void*b){(void)a;(void)b;}
uint8_t audio_ble_dm_conn_update_invalid_event_action(const void*a){(void)a;return 0;}
void audio_ble_dm_conn_update_invalid_action(uint8_t a){(void)a;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'shim.c').write_text(SHIM);elf=t/'dm.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_dm_conn_upd_execute_4b6532',str(S),str(t/'shim.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 def run(c,event,present):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in seg:u.mem_write(a,d)
  base=sy['audio_ble_dm_master_state_b'] if c else 0x20073fd8
  u.mem_write(0x20081000,bytes((1,0,event,0))+bytes(20))
  table1=0x20090000;table2=0x20090100
  if present:
   u.mem_write(base+4,struct.pack('<I',table1));u.mem_write(base+8,struct.pack('<I',table2))
  for tab in (table1,table2):
   for i in range(2):u.mem_write(tab+4*i,struct.pack('<I',0x200a0001+0x10*((tab==table2)*2+i)))
  effects=[]
  addr={((sy['audio_ble_dm_conn_update_trace_entry']&~1) if c else 0x52a63c):'trace'}
  for i in range(4):addr[0x200a0000+0x10*i]=f'action{i}'
  def hook(uc,a,size,user):
   k=addr.get(a)
   if not k:return
   if k=='trace':effects.append('trace')
   else:effects.append((k,uc.reg_read(UC_ARM_REG_R0)==0x20082000,uc.reg_read(UC_ARM_REG_R1)==0x20081000))
   uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.reg_write(UC_ARM_REG_R0,0x20082000);u.reg_write(UC_ARM_REG_R1,0x20081000);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
  u.emu_start(((sy['audio_ble_dm_conn_upd_execute_4b6532']&~1) if c else 0x4b6532)|1,0x600000,count=30000)
  return effects
 cases=0
 for event in (0x70,0x71,0x72,0x73):
  for present in (0,1):
   a=run(False,event,present);b=run(True,event,present)
   assert a==b,(event,present,a,b)
   cases+=1
 print('PASS_DM_CONN_UPDATE_EXECUTOR_NATIVE',cases)
