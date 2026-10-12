#!/usr/bin/env python3
"""Bounded connected stock/C F4 buffer composition with stacked arguments."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_smp_sc_f4.c'
STUB='''#include <stdint.h>
uint32_t alloc_result,alloc_size,alloc_ccb,alloc_msg,cmac_key,cmac_text,cmac_len,cmac_ccb,cmac_msg,cmac_count;
uint8_t *SmpScAlloc(uint8_t n,void *c,uint8_t *m){alloc_size=n;alloc_ccb=(uint32_t)c;alloc_msg=(uint32_t)m;return (uint8_t *)alloc_result;}
void SmpScCmac(const uint8_t *k,uint8_t *t,uint8_t n,void *c,uint8_t *m){cmac_key=(uint32_t)k;cmac_text=(uint32_t)t;cmac_len=n;cmac_ccb=(uint32_t)c;cmac_msg=(uint32_t)m;cmac_count++;}
void *memcpy(void *d,const void *s,unsigned long n){uint8_t *a=d;const uint8_t *b=s;for(unsigned long i=0;i<n;i++)a[i]=b[i];return d;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2',
                 '-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000',
                 '-Wl,-e,SmpScCalcF4',str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
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
   ccb,msg,uu,vv,key,buf=0x20080000,0x20080100,0x20080200,0x20080300,0x20080400,0x20080500
   u.mem_write(uu,bytes(range(32)));u.mem_write(vv,bytes(range(0x80,0xa0)))
   u.mem_write(key,bytes(range(0x20,0x40)));u.mem_write(buf,bytes([0xa5]*80))
   if compiled:u.mem_write(sy['alloc_result'],(buf if allocated else 0).to_bytes(4,'little'))
   calls=[]
   if not compiled:
    def hook(uc,pc,n,user):
     if pc==0x56cf04:
      calls.append(('alloc',uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1),uc.reg_read(UC_ARM_REG_R2)))
      uc.reg_write(UC_ARM_REG_R0,buf if allocated else 0)
     else:
      sp=uc.reg_read(UC_ARM_REG_SP)
      calls.append(('cmac',uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1),uc.reg_read(UC_ARM_REG_R2),uc.reg_read(UC_ARM_REG_R3),int.from_bytes(uc.mem_read(sp,4),'little')))
     uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    for a in (0x56cf04,0x56cec2):u.hook_add(UC_HOOK_CODE,hook,begin=a,end=a)
   sp=0x200ff000;u.mem_write(sp,(0x5a).to_bytes(4,'little')+key.to_bytes(4,'little'))
   u.reg_write(UC_ARM_REG_R0,ccb);u.reg_write(UC_ARM_REG_R1,msg)
   u.reg_write(UC_ARM_REG_R2,uu);u.reg_write(UC_ARM_REG_R3,vv)
   u.reg_write(UC_ARM_REG_SP,sp);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start((sy['SmpScCalcF4'] if compiled else 0x56cf2c)|1,0x600000,count=10000)
   if compiled:
    val=lambda name:int.from_bytes(u.mem_read(sy[name],4),'little')
    calls=[('alloc',val('alloc_size'),val('alloc_ccb'),val('alloc_msg'))]
    if val('cmac_count'):calls.append(('cmac',val('cmac_key'),val('cmac_text'),val('cmac_len'),val('cmac_ccb'),val('cmac_msg')))
   pair.append((bytes(u.mem_read(buf,80)),calls))
  assert pair[0]==pair[1],(allocated,pair)
print('PASS_BLE_SMP_SC_F4_NATIVE 2')
