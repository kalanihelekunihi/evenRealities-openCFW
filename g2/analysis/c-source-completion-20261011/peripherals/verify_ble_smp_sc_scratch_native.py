#!/usr/bin/env python3
"""Actual C/stock secure-connection scratch allocation/free effects."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_smp_sc_scratch.c'
STUB='''#include <stdint.h>
uint32_t alloc_calls,free_calls,fail_index,alloc_sizes[5],freed[5];
void *WsfBufAlloc(uint16_t n){uint32_t i=alloc_calls++;alloc_sizes[i]=n;return i==fail_index?0:(void *)(0x20083000u+i*0x100u);}
void WsfBufFree(void *p){freed[free_calls++]=(uint32_t)p;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2',
                 '-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,SmpScAllocScratchBuffers',
                 str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD']
  sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 for fail in (5,2):
  for preexisting in (False,True):
   for entry,native in (('SmpScAllocScratchBuffers',0x56cdc0),('SmpScFreeScratchBuffers',0x56ce4e)):
    pair=[]
    for compiled in (False,True):
     u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
     u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B)
     u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
     for a,d in seg:u.mem_write(a,d)
     ccb=0x20080000;sc=0x20080100
     u.mem_write(ccb+0x48,sc.to_bytes(4,'little'))
     u.mem_write(sc,bytes(0x30))
     if preexisting:u.mem_write(sc+0x14,(0x20084000).to_bytes(4,'little'))
     if compiled:u.mem_write(sy['fail_index'],fail.to_bytes(4,'little'))
     calls=[]
     if not compiled:
      def hook(uc,pc,n,user):
       if pc==0x530446:
        i=len(calls);size=uc.reg_read(UC_ARM_REG_R0)&0xffff
        calls.append(('a',size))
        uc.reg_write(UC_ARM_REG_R0,0 if i==fail else 0x20083000+i*0x100)
       else:calls.append(('f',uc.reg_read(UC_ARM_REG_R0)))
       uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
      for a in (0x530446,0x5304d4):u.hook_add(UC_HOOK_CODE,hook,begin=a,end=a)
     u.reg_write(UC_ARM_REG_R0,ccb);u.reg_write(UC_ARM_REG_SP,0x200ff000)
     u.reg_write(UC_ARM_REG_LR,0x600001)
     u.emu_start((sy[entry] if compiled else native)|1,0x600000,count=5000)
     if compiled:
      get=lambda name:int.from_bytes(u.mem_read(sy[name],4),'little')
      sizes=u.mem_read(sy['alloc_sizes'],get('alloc_calls')*4)
      frees=u.mem_read(sy['freed'],get('free_calls')*4)
      calls=[('a',int.from_bytes(sizes[i:i+4],'little')) for i in range(0,len(sizes),4)]
      calls += [('f',int.from_bytes(frees[i:i+4],'little')) for i in range(0,len(frees),4)]
     result=u.reg_read(UC_ARM_REG_R0)&0xff if entry=='SmpScAllocScratchBuffers' else None
     pair.append((result,bytes(u.mem_read(sc,0x30)),calls))
    assert pair[0]==pair[1],(fail,preexisting,entry,pair)
print('PASS_BLE_SMP_SC_SCRATCH_NATIVE 8')
