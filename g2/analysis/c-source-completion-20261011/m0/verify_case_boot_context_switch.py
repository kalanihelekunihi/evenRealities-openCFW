#!/usr/bin/env python3
"""Architectural register comparison of original/source first PSP handoff."""
from pathlib import Path
import subprocess,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_boot_context_switch_candidate.c';obj=H/'application_boot_context_switch.oracle.o';elf=H/'application_boot_context_switch.oracle.elf'
subprocess.run(['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x00100000',str(obj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
for i in range(32):
 pair=[]
 for native in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F)
  u.mem_map(0x00100000,0x10000)
  for a,b in seg:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_write(0x20000128,struct.pack('<I',0x20000300));u.mem_write(0x20000300,struct.pack('<I',0x20002000+i*4))
  words=[0x11110000+i,0x22220000+i,0x33330000+i,0x44440000+i,0x55550000+i,0x66660001,0x00102001,0x77770000+i]
  u.mem_write(0x20002020+i*4,struct.pack('<8I',*words));u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20001001)
  u.emu_start((0x080000cc if native else sym['case_boot_context_switch'])|1,0x00102000,count=100)
  pair.append(tuple(u.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_LR,UC_ARM_REG_SP,UC_ARM_REG_PSP,UC_ARM_REG_CONTROL,UC_ARM_REG_PRIMASK,UC_ARM_REG_PC)))
 assert pair[0]==pair[1],(i,pair)
print('PASS_CASE_BOOT_CONTEXT_SWITCH',32)
