#!/usr/bin/env python3
"""Actual ARM C/stock retry frame preserves inherited R2/R3 bytes."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_smp_sc_fail_retry.c'
STUB='''#include <stdint.h>
uint8_t observed[8];uint32_t call_count;
void SmpScGetCancelMsgWithReattempt(uint8_t c,void*p,uint8_t r){uint8_t*x=p;x[0]=c;x[1]=0;x[2]=3;x[3]=r;}
void smpSmExecute(void*c,void*p){(void)c;uint8_t*x=p;for(int i=0;i<8;i++)observed[i]=x[i];call_count++;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2',
                 '-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,smpScFailWithReattempt',
                 str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD']
  sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 for incoming in ((0x11223344,0x55667788),(0xa5a5a5a5,0x10203040)):
  pair=[]
  for compiled in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B)
   u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   ccb=0x20080000;u.mem_write(ccb+0x3d,bytes([7]))
   if not compiled:
    def hook(uc,pc,n,user):
     if pc==0x56d188:
      c,p,r=uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1),uc.reg_read(UC_ARM_REG_R2)
      uc.mem_write(p,bytes([c&255,0,3,r&255]))
     else:
      p=uc.reg_read(UC_ARM_REG_R1)
      uc.mem_write(sy['observed'],bytes(uc.mem_read(p,8)))
      uc.mem_write(sy['call_count'],(1).to_bytes(4,'little'))
     uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    for a in (0x56d188,0x56ee62):u.hook_add(UC_HOOK_CODE,hook,begin=a,end=a)
   u.reg_write(UC_ARM_REG_R0,ccb);u.reg_write(UC_ARM_REG_R2,incoming[0])
   u.reg_write(UC_ARM_REG_R3,incoming[1]);u.reg_write(UC_ARM_REG_SP,0x200ff000)
   u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start((sy['smpScFailWithReattempt'] if compiled else 0x56d304)|1,0x600000,count=3000)
   pair.append((bytes(u.mem_read(sy['observed'],8)),int.from_bytes(u.mem_read(sy['call_count'],4),'little')))
  assert pair[0]==pair[1],(incoming,pair)
print('PASS_BLE_SMP_SC_FAIL_RETRY_NATIVE 2')
