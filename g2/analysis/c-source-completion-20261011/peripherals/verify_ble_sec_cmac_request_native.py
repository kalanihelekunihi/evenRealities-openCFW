#!/usr/bin/env python3
"""Actual stock/C queued CMAC request with stack args and token effects."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_sec_cmac_request.c'
STUB='''#include <stdint.h>
uint8_t audio_ble_stack_state_20072cb8[128];uint32_t allocation,alloc_size,copy_dest,copy_src,subkey_buf;
void *WsfMsgAlloc(uint16_t n){alloc_size=n;return (void *)allocation;}
void Calc128Cpy(uint8_t*d,uint8_t*s){copy_dest=(uint32_t)d;copy_src=(uint32_t)s;for(int i=0;i<16;i++)d[i]=s[i];}
void secCmacGenSubkey1(void*p){subkey_buf=(uint32_t)p;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2',
                 '-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,SecCmac',
                 str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD']
  sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 for allocated in (False,True):
  pair=[]
  for compiled in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B)
   u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   key,text,buf=0x20081000,0x20081100,0x20081200
   u.mem_write(key,bytes(range(0x10,0x20)));u.mem_write(buf,bytes([0xa5]*100))
   state=sy['audio_ble_stack_state_20072cb8'] if compiled else 0x20072cb8
   u.mem_write(state+0x38,bytes([0x7f]))
   if compiled:u.mem_write(sy['allocation'],(buf if allocated else 0).to_bytes(4,'little'))
   calls=[]
   if not compiled:
    def hook(uc,pc,n,user):
     if pc==0x4bf99e:
      calls.append(('alloc',uc.reg_read(UC_ARM_REG_R0)))
      uc.reg_write(UC_ARM_REG_R0,buf if allocated else 0)
     elif pc==0x542a44:
      d,s=uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1)
      calls.append(('copy',d,s));uc.mem_write(d,bytes(uc.mem_read(s,16)))
     else:calls.append(('subkey',uc.reg_read(UC_ARM_REG_R0)))
     uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    for a in (0x4bf99e,0x542a44,0x53653a):u.hook_add(UC_HOOK_CODE,hook,begin=a,end=a)
   sp=0x200ff000;u.mem_write(sp,(0x1234).to_bytes(4,'little')+(0x1c).to_bytes(4,'little'))
   u.reg_write(UC_ARM_REG_R0,key);u.reg_write(UC_ARM_REG_R1,text)
   u.reg_write(UC_ARM_REG_R2,0x41);u.reg_write(UC_ARM_REG_R3,0x23)
   u.reg_write(UC_ARM_REG_SP,sp);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start((sy['SecCmac'] if compiled else 0x53665c)|1,0x600000,count=4000)
   if compiled:
    val=lambda n:int.from_bytes(u.mem_read(sy[n],4),'little')
    calls=[('alloc',val('alloc_size'))]
    if allocated:calls += [('copy',val('copy_dest'),val('copy_src')),('subkey',val('subkey_buf'))]
   pair.append((u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(buf,100)),bytes(u.mem_read(state+0x38,1)),calls))
  assert pair[0]==pair[1],(allocated,pair)
print('PASS_BLE_SEC_CMAC_REQUEST_NATIVE 2')
