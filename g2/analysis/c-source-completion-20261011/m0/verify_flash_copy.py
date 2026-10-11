#!/usr/bin/env python3
"""Compare stock/source 64-word flash transfer and controller side effects."""
from pathlib import Path
import subprocess,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
FW=(ROOT/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
SRC=ROOT/'g2/components/case/legacy_default_candidate_20261010/flash_copy_candidate.c';obj=HERE/'flash_copy_candidate.o';elf=HERE/'flash_copy_candidate.elf';ld=HERE/'flash_copy_candidate.ld'
subprocess.run(['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-c',str(SRC),'-o',str(obj)],check=True)
ld.write_text('SECTIONS { . = 0x00100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }\n')
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-T',str(ld),str(obj),'-o',str(elf)],check=True)
with elf.open('rb') as stream:
 e=ELFFile(stream);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
for seed,initial in itertools.product([0,1,7,0x55],[0,0xffffffff,0x77777777]):
 pair=[]
 for original in [True,False]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(FW)+4095)&~4095);u.mem_write(0x08000000,FW)
  u.mem_map(0x00100000,0x10000)
  for a,b in segments:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_map(0x40022000,0x1000)
  data=bytes((i+seed)&255 for i in range(256));u.mem_write(0x20004000,data)
  u.mem_write(0x40022014,initial.to_bytes(4,'little'))
  u.reg_write(UC_ARM_REG_R0,0x20003000);u.reg_write(UC_ARM_REG_R1,0x20004000)
  u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20001001)
  writes=[]
  def hook(uc,access,address,size,value,user):
   if address==0x40022014 or 0x20003000<=address<0x20003100:writes.append((address,size,value))
  u.hook_add(UC_HOOK_MEM_WRITE,hook)
  u.emu_start((0x08003f38 if original else sym['case_flash_copy_operation'])|1,0x20001000,count=10000)
  assert u.reg_read(UC_ARM_REG_PC)==0x20001000
  pair.append((writes,bytes(u.mem_read(0x20003000,256)),bytes(u.mem_read(0x40022014,4))))
 assert pair[0]==pair[1],(seed,initial,pair)
print('PASS_FLASH_COPY',12)
