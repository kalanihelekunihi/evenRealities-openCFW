#!/usr/bin/env python3
"""Controlled native/C effects of Main DmSecAuthRsp 0x4d24d4."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_dm_auth_rsp.c'
stub='''#include <stdint.h>
__attribute__((naked)) void *WsfMsgAlloc(uint16_t n){__asm volatile("bx lr");}
__attribute__((naked)) void SmpDmMsgSend(void*m){__asm volatile("bx lr");}
__attribute__((naked)) void __aeabi_memcpy(void*d,const void*s,unsigned n){__asm volatile("bx lr");}
'''
with tempfile.TemporaryDirectory() as td:
 mock=Path(td)/'mock.c';mock.write_text(stub);elf=Path(td)/'candidate.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,DmSecAuthRsp',str(S),str(mock),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  x=ELFFile(f);seg=[(s['p_vaddr'],s.data()) for s in x.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in x.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 for allocated in (False,True):
  for length in (0,1,3,4,8):
   for source in (False,True):
    pair=[]
    for is_c in (False,True):
     u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
     u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
     for a,d in seg:u.mem_write(a,d)
     msg=0x2007f200;src=0x2007f100;u.mem_write(msg,bytes([0xa5]*64));u.mem_write(src,bytes(range(64)))
     u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
     u.reg_write(UC_ARM_REG_R0,2);u.reg_write(UC_ARM_REG_R1,length);u.reg_write(UC_ARM_REG_R2,src if source else 0)
     seen=[]
     def hook(uc,a,size,_):
      if a in (0x4bf99e,sym['WsfMsgAlloc']&~1):seen.append(('alloc',uc.reg_read(UC_ARM_REG_R0)));uc.reg_write(UC_ARM_REG_R0,msg if allocated else 0);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
      if a in (0x439be4,sym['__aeabi_memcpy']&~1) and source:
       dst=uc.reg_read(UC_ARM_REG_R0);p=uc.reg_read(UC_ARM_REG_R1);n=uc.reg_read(UC_ARM_REG_R2);uc.mem_write(dst,bytes(uc.mem_read(p,n)));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
      if a in (0x537bd6,sym['SmpDmMsgSend']&~1):seen.append(('send',uc.reg_read(UC_ARM_REG_R0)-msg));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
     u.hook_add(UC_HOOK_CODE,hook)
     u.emu_start((sym['DmSecAuthRsp'] if is_c else 0x4d24d4)|1,0x600000,count=500)
     pair.append((seen,bytes(u.mem_read(msg,24))))
    assert pair[0]==pair[1],(allocated,length,source,pair)
    cases+=1
 print('PASS_BLE_DM_AUTH_RSP_NATIVE',cases)
