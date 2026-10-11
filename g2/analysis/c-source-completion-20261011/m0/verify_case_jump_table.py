#!/usr/bin/env python3
"""Compare native and sourced 0x9190 compact Thumb jump-table control flow."""
from pathlib import Path
import random,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
S=R/'g2/components/case/startup_candidate_20261011/application_boot_jump_table_candidate.c'
with tempfile.TemporaryDirectory() as d:
 d=Path(d);o=d/'x.o';e=d/'x.elf'
 subprocess.run(['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c',str(S),'-o',str(o)],check=True)
 subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x100000',str(o),'-o',str(e)],check=True,stderr=subprocess.DEVNULL)
 with e.open('rb') as f:
  elf=ELFFile(f);sym={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
  seg=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD']
 rng=random.Random(0x9190)
 for i in range(256):
  maximum=rng.randrange(1,32);selector=rng.randrange(0,maximum+16)
  offsets=bytes(rng.randrange(32,128) for _ in range(maximum+1))
  destination=(0x300101+2*offsets[min(selector,maximum)])&~1
  regs=[rng.getrandbits(32) for _ in range(3)]
  outcomes=[]
  for native in (True,False):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
   u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F)
   u.mem_map(0x100000,0x10000)
   for a,b in seg:u.mem_write(a,b)
   u.mem_map(0x20000000,0x10000);u.mem_map(0x300000,0x1000)
   u.mem_write(0x300100,bytes([maximum])+offsets)
   for reg,val in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2),regs):u.reg_write(reg,val)
   u.reg_write(UC_ARM_REG_R3,selector);u.reg_write(UC_ARM_REG_R4,0x12345678)
   u.reg_write(UC_ARM_REG_R5,0x87654321);u.reg_write(UC_ARM_REG_SP,0x20007fc0)
   u.reg_write(UC_ARM_REG_LR,0x300101)
   u.emu_start((0x08009190 if native else sym['case_boot_jump_table_dispatch_9190'])|1,destination,count=30)
   outcomes.append(tuple(u.reg_read(reg) for reg in (UC_ARM_REG_PC,UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_SP)))
  assert outcomes[0]==outcomes[1],(i,maximum,selector,outcomes)
 print('PASS_CASE_JUMP_TABLE',256)
