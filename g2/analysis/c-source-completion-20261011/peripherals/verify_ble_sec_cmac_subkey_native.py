#!/usr/bin/env python3
"""Actual C/stock subkey-one dispatch and zero block."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_sec_cmac_subkey.c'
STUB='''#include <stdint.h>
uint32_t call_key,call_queue,call_handler,call_count;uint8_t call_plain[16];
void SecLeEncryptCmd(const uint8_t*k,const uint8_t*p,void*q,uint8_t h){call_key=(uint32_t)k;call_queue=(uint32_t)q;call_handler=h;call_count++;for(int i=0;i<16;i++)call_plain[i]=p[i];}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2',
                 '-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,secCmacGenSubkey1',
                 str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD']
  sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 for handler in (0,7,0x55):
  pair=[]
  for compiled in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B)
   u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   queue,cb=0x20080000,0x20080100
   u.mem_write(queue+0x30,cb.to_bytes(4,'little'))
   u.mem_write(cb+0x28,bytes([handler]))
   observed=[]
   if not compiled:
    def hook(uc,pc,n,user):
     key,plain,q,h=[uc.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)]
     observed.append((key,q,h,bytes(uc.mem_read(plain,16))))
     uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook,begin=0x5363ae,end=0x5363ae)
   u.reg_write(UC_ARM_REG_R0,queue);u.reg_write(UC_ARM_REG_SP,0x200ff000)
   u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start((sy['secCmacGenSubkey1'] if compiled else 0x53653a)|1,0x600000,count=3000)
   if compiled:
    v=lambda n:int.from_bytes(u.mem_read(sy[n],4),'little')
    observed=[(v('call_key'),v('call_queue'),v('call_handler'),bytes(u.mem_read(sy['call_plain'],16)))] if v('call_count') else []
   pair.append(observed)
  assert pair[0]==pair[1],(handler,pair)
print('PASS_BLE_SEC_CMAC_SUBKEY_NATIVE 3')
