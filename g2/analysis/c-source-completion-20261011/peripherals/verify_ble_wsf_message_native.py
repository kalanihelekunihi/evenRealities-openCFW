#!/usr/bin/env python3
"""Native/C WSF message allocation and send call effects."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_wsf_message.c'
stub='''
#include <stdint.h>
__attribute__((naked)) void *WsfBufAlloc(uint16_t n){__asm volatile("bx lr");}
__attribute__((naked)) void *WsfTaskMsgQueue(void){__asm volatile("bx lr");}
__attribute__((naked)) void WsfMsgEnq(void*q,uint8_t h,void*m){__asm volatile("bx lr");}
__attribute__((naked)) void WsfTaskSetReady(uint8_t h,uint8_t n){__asm volatile("bx lr");}
'''
with tempfile.TemporaryDirectory() as td:
 mock=Path(td)/'mock.c';mock.write_text(stub);elf=Path(td)/'candidate.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,WsfMsgAlloc',str(S),str(mock),'-o',str(elf)],check=True)
 with elf.open('rb') as f:x=ELFFile(f);seg=[(s['p_vaddr'],s.data()) for s in x.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in x.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 for mode in ('alloc','send'):
  for value in ((0,1,12,65535) if mode=='alloc' else (0,1,7,255)):
   for success in ((False,True) if mode=='alloc' else (True,)):
    pair=[]
    for is_c in (False,True):
     u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
     u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
     for a,d in seg:u.mem_write(a,d)
     u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,value);u.reg_write(UC_ARM_REG_R1,0x2007f100)
     seen=[]
     def hook(uc,a,size,_):
      if a in (0x530446,sym['WsfBufAlloc']&~1):seen.append(('bufalloc',uc.reg_read(UC_ARM_REG_R0)));uc.reg_write(UC_ARM_REG_R0,0x2007f000 if success else 0);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
      if a in (0x52b97c,sym['WsfTaskMsgQueue']&~1):seen.append(('queue',));uc.reg_write(UC_ARM_REG_R0,0x2007f200);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
      if a in (0x4bf9de,sym['WsfMsgEnq']&~1):seen.append(('enq',uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1),uc.reg_read(UC_ARM_REG_R2)));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
      if a in (0x52b95e,sym['WsfTaskSetReady']&~1):seen.append(('ready',uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1)));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
     u.hook_add(UC_HOOK_CODE,hook)
     u.emu_start((sym['WsfMsgAlloc' if mode=='alloc' else 'WsfMsgSend'] if is_c else (0x4bf99e if mode=='alloc' else 0x4bf9ba))|1,0x600000,count=300)
     pair.append((seen,u.reg_read(UC_ARM_REG_R0) if mode=='alloc' else None))
    assert pair[0]==pair[1],(mode,value,success,pair)
    cases+=1
 print('PASS_BLE_WSF_MESSAGE_NATIVE',cases)
