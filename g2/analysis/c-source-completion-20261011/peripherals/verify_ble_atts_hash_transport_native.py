#!/usr/bin/env python3
"""Actual C/native ATT packet allocation and bearer transport effects."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_atts_hash_transport.c'
STUB='''#include <stdint.h>
uint8_t audio_ble_att_common_state[0x64];
uint8_t *WsfMsgAlloc(uint16_t n){(void)n;return 0;}
void L2cDataReq(uint16_t c,uint16_t h,uint16_t n,uint8_t*p){(void)c;(void)h;(void)n;(void)p;}
void WsfMsgFree(void*p){(void)p;}
void callback(uint8_t*c,uint8_t s,uint16_t n,uint8_t*p){(void)c;(void)s;(void)n;(void)p;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2',
                 '-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000',
                 '-Wl,-e,attL2cDataReq',str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD']
  sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 for mode in ('alloc','legacy','no_callback','callback'):
  pair=[]
  for compiled in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B)
   u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   state=sy['audio_ble_att_common_state'] if compiled else 0x200610ac
   ccb,packet=0x20080000,0x20080100;u.mem_write(ccb+0xc,(0x1234).to_bytes(2,'little'))
   callback=sy['callback'] if compiled else 0x100100
   if mode=='callback':u.mem_write(state+0x54,(callback|1).to_bytes(4,'little'))
   calls=[]
   addrs={'alloc':(sy['WsfMsgAlloc']&~1) if compiled else 0x4bf99e,
          'send':(sy['L2cDataReq']&~1) if compiled else 0x530bbc,
          'free':(sy['WsfMsgFree']&~1) if compiled else 0x4bf9b0,
          'callback':callback&~1}
   def hook(uc,pc,n,user):
    regs=tuple(uc.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3))
    if pc==addrs['alloc']:
     calls.append(('alloc',regs[0]));uc.reg_write(UC_ARM_REG_R0,packet)
    elif pc==addrs['send']:calls.append(('send',regs[0],regs[1],regs[2],regs[3]-packet))
    elif pc==addrs['free']:calls.append(('free',regs[0]-packet))
    else:calls.append(('callback',regs[0]-ccb,regs[1],regs[2],regs[3]-packet))
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   for a in addrs.values():u.hook_add(UC_HOOK_CODE,hook,begin=a,end=a)
   if mode=='alloc':
    u.reg_write(UC_ARM_REG_R0,23);u.reg_write(UC_ARM_REG_R1,5)
    start=sy['WsfMsgDataAlloc'] if compiled else 0x4bf990
   else:
    u.reg_write(UC_ARM_REG_R0,ccb);u.reg_write(UC_ARM_REG_R1,0 if mode=='legacy' else 1)
    u.reg_write(UC_ARM_REG_R2,17);u.reg_write(UC_ARM_REG_R3,packet)
    start=sy['attL2cDataReq'] if compiled else 0x4b50ba
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start(start|1,0x600000,count=1500)
   pair.append(calls)
  assert pair[0]==pair[1],(mode,pair)
print('PASS_BLE_ATTS_HASH_TRANSPORT_NATIVE 4')
