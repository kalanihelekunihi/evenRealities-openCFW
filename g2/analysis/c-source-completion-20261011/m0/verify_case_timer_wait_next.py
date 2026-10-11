#!/usr/bin/env python3
"""CASE 0xade8 stock/C timer-list wait selection oracle."""
from pathlib import Path
import random,struct,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_boot_timer_wait_next_candidate.c';obj=H/'timer_wait_next.oracle.o';elf=H/'timer_wait_next.oracle.elf'
subprocess.run(['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x100000',str(obj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
rng=random.Random(0xade8)
for i in range(128):
 desired=rng.getrandbits(32);present=i%2;pair=[]
 for native in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F);u.mem_map(0x00100000,0x10000)
  for a,b in seg:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000)
  u.mem_write(0x20000170,struct.pack('<I',0x20001000));u.mem_write(0x20001000,struct.pack('<4I',present,0,0,0x20002000));u.mem_write(0x20002000,struct.pack('<I',desired))
  u.reg_write(UC_ARM_REG_R0,0x20003000);u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20008001)
  u.emu_start((0x0800ade8 if native else sym['case_boot_timer_wait_next'])|1,0x20008000,count=100)
  pair.append((u.reg_read(UC_ARM_REG_R0),struct.unpack('<I',bytes(u.mem_read(0x20003000,4)))[0]))
 assert pair[0]==pair[1],(i,pair)
print('PASS_CASE_TIMER_WAIT_NEXT',128)
