#!/usr/bin/env python3
"""Actual compiled-C/native slave disconnect and Cordio message effects."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_slave_disconnect.c'
STUB='''#include <stdint.h>
uint8_t audio_ble_dm_handler_state[0x18];
void *WsfMsgAlloc(uint16_t n){(void)n;return 0;}
void WsfMsgSend(uint8_t h,void*p){(void)h;(void)p;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_slave_disconnect_event',str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 def run(compiled,conn,alloc):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in seg:u.mem_write(a,d)
  state=sy['audio_ble_dm_handler_state'] if compiled else 0x20073b78
  u.mem_write(state+12,b'\x37');packet=0x20085000;u.mem_write(packet,bytes([0xa5]*36));trace=[]
  for name,cs,ns in [('alloc','WsfMsgAlloc',0x4bf99e),('send','WsfMsgSend',0x4bf9ba)]:
   a=(sy[cs]&~1) if compiled else ns
   def hook(uc,pc,n,user,name=name):
    if name=='alloc':trace.append(('alloc',uc.reg_read(UC_ARM_REG_R0)));uc.reg_write(UC_ARM_REG_R0,packet if alloc else 0)
    else:trace.append(('send',uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1)==packet,bytes(uc.mem_read(packet,36))))
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook,begin=a,end=a)
  u.reg_write(UC_ARM_REG_R0,conn);u.reg_write(UC_ARM_REG_R7,0x12345678)
  u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
  u.emu_start((sy['audio_ble_slave_disconnect_event'] if compiled else 0x4bb04a)|1,0x600000,count=3000)
  return trace,bytes(u.mem_read(packet,36)),u.reg_read(UC_ARM_REG_R0)
 cases=0
 for conn in (0,1,0x34,0xff,0x1234):
  for alloc in (0,1):
   a,b=run(False,conn,alloc),run(True,conn,alloc)
   assert a==b,(conn,alloc,a,b)
   cases+=1
 print('PASS_BLE_SLAVE_DISCONNECT_NATIVE',cases)
