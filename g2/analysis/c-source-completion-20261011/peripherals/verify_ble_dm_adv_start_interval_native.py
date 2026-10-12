#!/usr/bin/env python3
"""Actual compiled-C/native DM advertising start and interval effects."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_dm_adv_start_interval.c'
STUB='''#include <stdint.h>
uint8_t audio_ble_dm_handler_state[0x18],audio_ble_dm_adv_control[0x30];
uint8_t *WsfMsgAlloc(uint16_t n){(void)n;return 0;}
void WsfMsgSend(uint8_t h,void *p){(void)h;(void)p;}
void WsfTaskLock(void){} void WsfTaskUnlock(void){}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,DmAdvStart',str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD']
  sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 for count,allocated in ((0,True),(1,True),(2,True),(1,False)):
  pair=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B)
   u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   state=sy['audio_ble_dm_handler_state'] if is_c else 0x20073b78
   u.mem_write(state+0xc,b'\x09');handles=0x20080000;dur=0x20080010;maxev=0x20080020;packet=0x20080100
   u.mem_write(handles,b'\x01\x00');u.mem_write(dur,b'\x34\x12\x78\x56');u.mem_write(maxev,b'\x07\x08');u.mem_write(packet,bytes([0xa5]*14))
   alloc=(sy['WsfMsgAlloc']&~1) if is_c else 0x4bf99e
   send=(sy['WsfMsgSend']&~1) if is_c else 0x4bf9ba
   calls=[]
   def hook(uc,pc,n,user):
    if pc==alloc:calls.append(('alloc',uc.reg_read(UC_ARM_REG_R0)&0xffff));uc.reg_write(UC_ARM_REG_R0,packet if allocated else 0)
    else:calls.append(('send',uc.reg_read(UC_ARM_REG_R0)&0xff,uc.reg_read(UC_ARM_REG_R1)==packet))
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   for addr in (alloc,send):u.hook_add(UC_HOOK_CODE,hook,begin=addr,end=addr)
   u.reg_write(UC_ARM_REG_R0,count);u.reg_write(UC_ARM_REG_R1,handles);u.reg_write(UC_ARM_REG_R2,dur);u.reg_write(UC_ARM_REG_R3,maxev)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start((sy['DmAdvStart'] if is_c else 0x4b31ea)|1,0x600000,count=1000)
   pair.append((calls,bytes(u.mem_read(packet,14))))
  assert pair[0]==pair[1],(count,allocated,pair)
 for handle in (0,1):
  pair=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B)
   u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   state=sy['audio_ble_dm_adv_control'] if is_c else 0x20073394
   u.mem_write(state,bytes([0xa5]*0x30));calls=[]
   lock=(sy['WsfTaskLock']&~1) if is_c else 0x52b8c8
   unlock=(sy['WsfTaskUnlock']&~1) if is_c else 0x52b8d0
   def hook(uc,pc,n,user):calls.append('lock' if pc==lock else 'unlock');uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   for addr in (lock,unlock):u.hook_add(UC_HOOK_CODE,hook,begin=addr,end=addr)
   u.reg_write(UC_ARM_REG_R0,handle);u.reg_write(UC_ARM_REG_R1,0x1234);u.reg_write(UC_ARM_REG_R2,0x5678)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start((sy['DmAdvSetInterval'] if is_c else 0x4b3292)|1,0x600000,count=1000)
   pair.append((calls,bytes(u.mem_read(state,0x30))))
  assert pair[0]==pair[1],(handle,pair)
print('PASS_BLE_DM_ADV_START_INTERVAL_NATIVE 6')
