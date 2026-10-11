#!/usr/bin/env python3
"""Stock/source mode bit and lower output-pointer comparison."""
from pathlib import Path
import struct,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
FW=(ROOT/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
SRC=ROOT/'g2/components/case/legacy_default_candidate_20261010/flash_mode_candidate.c'
obj=HERE/'flash_mode_candidate.o';elf=HERE/'flash_mode_candidate.elf';ld=HERE/'flash_mode_candidate.ld'
subprocess.run(['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-c',str(SRC),'-o',str(obj)],check=True)
ld.write_text('case_flash_mode_registers = 0x0010f001; SECTIONS { . = 0x00100000; .text : { *(.text*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }\n')
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-T',str(ld),str(obj),'-o',str(elf)],check=True)
with elf.open('rb') as stream:
 e=ELFFile(stream);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
rows=[]
for word in [0,1,0x000fffff,0x00100000,0x00100001,0xffffffff]:
 pair=[]
 for original in [True,False]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(FW)+4095)&~4095);u.mem_write(0x08000000,FW)
  u.mem_map(0x00100000,0x10000)
  for a,b in segments:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20001001)
  calls=[]
  def hook(uc,address,size,user):
   if address in [0x08004a00,0x0010f000]:
    p=uc.reg_read(UC_ARM_REG_R0);calls.append(p)
    assert 0x20007f00<=p<0x20008000
    uc.mem_write(p,struct.pack('<7I',0,0,0,0,0,0,word))
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((0x08002f46 if original else sym['case_binary_5e_flash_mode'])|1,0x20001000,count=500)
  assert len(calls)==1 and u.reg_read(UC_ARM_REG_PC)==0x20001000
  pair.append(u.reg_read(UC_ARM_REG_R0))
 assert pair[0]==pair[1],(word,pair)
 rows.append((word,pair[0]))
print('PASS_FLASH_MODE_BIT',len(rows))
