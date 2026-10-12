#!/usr/bin/env python3
"""Native/C host-address mapping and resolving-list removal message."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
B=B.read_bytes()[32:];S=R/'components/audio/uart_thread_source_candidate/display_ble_dm_privacy_remove.c'
stub='''
#include <stdint.h>
uint8_t audio_ble_dm_handler_state[0x18];
__attribute__((naked)) void *WsfMsgAlloc(uint16_t n){__asm volatile("bx lr");}
__attribute__((naked)) void WsfMsgSend(uint8_t h,void*m){__asm volatile("bx lr");}
'''
with tempfile.TemporaryDirectory() as td:
 mock=Path(td)/'mock.c';mock.write_text(stub);elf=Path(td)/'candidate.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,DmHostAddrType',str(S),str(mock),'-o',str(elf)],check=True)
 with elf.open('rb') as f:x=ELFFile(f);seg=[(s['p_vaddr'],s.data()) for s in x.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in x.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 for mode in ('type','message'):
  for flag in (0,1):
   for value in ((0,1,2,3,4) if mode=='type' else (0,1)):
    pair=[]
    for is_c in (False,True):
     u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
     u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
     for a,d in seg:u.mem_write(a,d)
     state=sym['audio_ble_dm_handler_state'] if is_c else 0x20073b78
     u.mem_write(state+0x16,bytes((flag,)));u.mem_write(state+0x0c,bytes((7,)))
     buf=0x2007f100;addr=0x2007f000;u.mem_write(addr,bytes((1,2,3,4,5,6)));u.mem_write(buf,bytes([0xa5]*12))
     u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,3 if mode=='message' else value);u.reg_write(UC_ARM_REG_R1,addr);u.reg_write(UC_ARM_REG_R2,0x1234)
     seen=[]
     def hook(uc,a,size,_):
      if a in (0x4bf99e,sym['WsfMsgAlloc']&~1):seen.append(('alloc',uc.reg_read(UC_ARM_REG_R0)));uc.reg_write(UC_ARM_REG_R0,0 if value==0 else buf);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
      if a in (0x4bf9ba,sym['WsfMsgSend']&~1):seen.append(('send',uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1)-buf));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
     u.hook_add(UC_HOOK_CODE,hook)
     entry=(sym['DmHostAddrType' if mode=='type' else 'DmPrivRemDevFromResList'] if is_c else (0x4d2aa8 if mode=='type' else 0x4d2880))
     u.emu_start(entry|1,0x600000,count=500)
     pair.append(u.reg_read(UC_ARM_REG_R0) if mode=='type' else (seen,bytes(u.mem_read(buf,12))))
    assert pair[0]==pair[1],(mode,flag,value,pair)
    cases+=1
 print('PASS_BLE_DM_PRIVACY_REMOVE_NATIVE',cases)
