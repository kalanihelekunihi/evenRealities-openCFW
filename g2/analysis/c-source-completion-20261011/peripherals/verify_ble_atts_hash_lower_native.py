#!/usr/bin/env python3
"""Actual C/native ATT hash lower allocation/error/group search effects."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_atts_hash_lower.c'
STUB='''#include <stdint.h>
uint8_t audio_ble_atts_state[0x268];
uint8_t *WsfMsgDataAlloc(uint16_t n,uint8_t o){(void)n;(void)o;return 0;}
void attL2cDataReq(uint8_t*c,uint8_t s,uint16_t n,uint8_t*p){(void)c;(void)s;(void)n;(void)p;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2',
                 '-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000',
                 '-Wl,-e,attsFindByHandle',str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD']
  sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 for mode in ('find_hit','find_miss','err_alloc','err_fail','alloc'):
  pair=[]
  for compiled in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B)
   u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   state=sy['audio_ble_atts_state'] if compiled else 0x2006e5f0
   group,attrs,out,ccb,msg=0x20080000,0x20080100,0x20080200,0x20080300,0x20080400
   u.mem_write(state+0x258,group.to_bytes(4,'little'))
   u.mem_write(group,bytes(0x20));u.mem_write(group+4,attrs.to_bytes(4,'little'))
   u.mem_write(group+0x10,(0x20).to_bytes(2,'little'));u.mem_write(group+0x12,(0x22).to_bytes(2,'little'))
   u.mem_write(msg,bytes([0xa5]*0x20));u.mem_write(out,bytes(4))
   calls=[]
   addrs={'alloc':(sy['WsfMsgDataAlloc']&~1) if compiled else 0x4bf990,
          'send':(sy['attL2cDataReq']&~1) if compiled else 0x4b50ba}
   def hook(uc,pc,n,user):
    r=[uc.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)]
    if pc==addrs['alloc']:
     calls.append(('alloc',r[0],r[1]));uc.reg_write(UC_ARM_REG_R0,0 if mode=='err_fail' else msg)
    else:calls.append(('send',r[0]-ccb,r[1],r[2],r[3]-msg))
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   for a in addrs.values():u.hook_add(UC_HOOK_CODE,hook,begin=a,end=a)
   if mode.startswith('find'):
    u.reg_write(UC_ARM_REG_R0,0x21 if mode=='find_hit' else 0x30)
    u.reg_write(UC_ARM_REG_R1,out)
    start=sy['attsFindByHandle'] if compiled else 0x56c5d4
   elif mode=='alloc':
    u.reg_write(UC_ARM_REG_R0,0x23);start=sy['attMsgAlloc'] if compiled else 0x4b50ae
   else:
    u.reg_write(UC_ARM_REG_R0,ccb);u.reg_write(UC_ARM_REG_R1,0)
    u.reg_write(UC_ARM_REG_R2,8);u.reg_write(UC_ARM_REG_R3,0x1234)
    u.reg_write(UC_ARM_REG_SP,0x200ff000);u.mem_write(0x200ff000,(0x0a).to_bytes(4,'little'))
    start=sy['attsErrRsp'] if compiled else 0x534c9a
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start(start|1,0x600000,count=1500)
   result=u.reg_read(UC_ARM_REG_R0)
   if mode=='find_hit':result-=attrs
   elif mode=='find_miss':result=0
   elif mode=='alloc':result-=msg
   else:result=0
   pair.append((result,bytes(u.mem_read(out,4)),bytes(u.mem_read(msg,0x20)),calls))
  assert pair[0]==pair[1],(mode,pair)
print('PASS_BLE_ATTS_HASH_LOWER_NATIVE 5')
