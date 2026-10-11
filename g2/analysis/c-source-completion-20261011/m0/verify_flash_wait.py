#!/usr/bin/env python3
"""Stock/source elapsed-tick wait comparison with controlled ticks."""
from pathlib import Path
import subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
FW=(ROOT/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
SRC=ROOT/'g2/components/case/legacy_default_candidate_20261010/flash_wait_candidate.c'
obj=HERE/'flash_wait_candidate.o';elf=HERE/'flash_wait_candidate.elf';ld=HERE/'flash_wait_candidate.ld'
subprocess.run(['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-c',str(SRC),'-o',str(obj)],check=True)
ld.write_text('case_tick_word2 = 0x0010f001; SECTIONS { . = 0x00100000; .text : { *(.text*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }\n')
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-T',str(ld),str(obj),'-o',str(elf)],check=True)
with elf.open('rb') as stream:
 e=ELFFile(stream);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
cases=[(0,0,[10,10]),(1,0,[10,11]),(5,2,[10,11,15,17]),
       (3,0,[0xfffffffe,0,1]),(1,2,[100,101,102,103]),
       (0xffffffff,0,[0,0xffffffff])]
for timeout,offset,ticks in cases:
 pair=[]
 for original in [True,False]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(FW)+4095)&~4095);u.mem_write(0x08000000,FW)
  u.mem_map(0x00100000,0x10000)
  for a,b in segments:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_write(0x20000118,bytes([offset]))
  u.reg_write(UC_ARM_REG_R0,timeout);u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20001001)
  calls=[0]
  def hook(uc,address,size,user):
   if address in [0x08004eac,0x0010f000]:
    assert calls[0]<len(ticks),(timeout,offset,ticks,original,calls)
    uc.reg_write(UC_ARM_REG_R0,ticks[calls[0]]);calls[0]+=1
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((0x08004958 if original else sym['case_binary_5e_wait'])|1,0x20001000,count=1000)
  assert u.reg_read(UC_ARM_REG_PC)==0x20001000
  pair.append((calls[0],u.reg_read(UC_ARM_REG_R0)))
 assert pair[0]==pair[1],(timeout,offset,ticks,pair)
print('PASS_FLASH_WAIT_TICKS',len(cases))
