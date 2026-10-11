#!/usr/bin/env python3
"""Native/source CASE 0x4a00 option MMIO read comparison."""
from pathlib import Path
import random,subprocess,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_boot_option_read_candidate.c';obj=H/'boot_option_read.oracle.o';elf=H/'boot_option_read.oracle.elf'
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
subprocess.run(flags+[str(src),'-o',str(obj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x00100000',str(obj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
rng=random.Random(0x4a00)
for i in range(96):
 selector=[1,4,8,0,2,0xffffffff][i%6];registers=[rng.getrandbits(32) for _ in range(5)];initial=[rng.getrandbits(32) for _ in range(7)];initial[1]=selector;pair=[]
 for native in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F)
  u.mem_map(0x00100000,0x10000)
  for a,b in seg:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_map(0x40022000,0x1000)
  for a,v in zip([0x40022020,0x4002202c,0x40022030,0x4002204c,0x40022050],registers):u.mem_write(a,struct.pack('<I',v))
  u.mem_write(0x20003000,struct.pack('<7I',*initial))
  u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20008001);u.reg_write(UC_ARM_REG_R0,0x20003000)
  u.emu_start((0x08004a00 if native else sym['case_boot_read_option_words'])|1,0x20008000,count=500)
  pair.append(bytes(u.mem_read(0x20003000,28)))
 assert pair[0]==pair[1],(i,pair)
print('PASS_CASE_BOOT_OPTION_READ',96)
