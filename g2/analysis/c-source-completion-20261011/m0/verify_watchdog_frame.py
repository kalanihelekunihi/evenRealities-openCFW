#!/usr/bin/env python3
"""Compare stock/source 0x2c8e frame arguments and payload bytes."""
from pathlib import Path
import subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
FW=(ROOT/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
SRC=ROOT/'g2/components/case/legacy_default_candidate_20261010/watchdog_frame_candidate.c';obj=HERE/'watchdog_frame_candidate.o';elf=HERE/'watchdog_frame_candidate.elf';ld=HERE/'watchdog_frame_candidate.ld'
subprocess.run(['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-c',str(SRC),'-o',str(obj)],check=True)
ld.write_text('case_watchdog_frame_pack = 0x0010f001;\nSECTIONS { . = 0x00100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }\n')
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-T',str(ld),str(obj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as stream:
 e=ELFFile(stream);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
for enabled in [0,1,2,0xffffffff]:
 pair=[]
 for original in [True,False]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(FW)+4095)&~4095);u.mem_write(0x08000000,FW)
  u.mem_map(0x00100000,0x10000)
  for a,b in segments:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.reg_write(UC_ARM_REG_R0,enabled);u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20001001)
  calls=[]
  def hook(uc,address,size,user):
   if address!=(0x08009004 if original else 0x0010f000):return
   p=uc.reg_read(UC_ARM_REG_R2)
   calls.append((uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1),uc.mem_read(p,1)[0]))
   uc.reg_write(UC_ARM_REG_R0,0x76543210);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((0x08002c8e if original else sym['case_legacy_watchdog_set'])|1,0x20001000,count=1000)
  pair.append((calls,u.reg_read(UC_ARM_REG_R0)))
 assert pair[0]==pair[1],(enabled,pair)
print('PASS_WATCHDOG_FRAME',4)
