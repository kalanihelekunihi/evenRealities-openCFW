#!/usr/bin/env python3
"""Compare native and source CASE 0x5f44 status-word OR."""
from pathlib import Path
import random,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
S=R/'g2/components/case/startup_candidate_20261011/application_boot_sensor_flags_candidate.c'
with tempfile.TemporaryDirectory() as d:
 d=Path(d);o=d/'x.o';e=d/'x.elf'
 subprocess.run(['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c',str(S),'-o',str(o)],check=True)
 subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x100000',str(o),'-o',str(e)],check=True,stderr=subprocess.DEVNULL)
 with e.open('rb') as f:
  elf=ELFFile(f);sym={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
  seg=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD']
 rng=random.Random(0x5f44)
 for i in range(256):
  addr=0x20001000+4*rng.randrange(0,64);a=rng.getrandbits(32);b=rng.getrandbits(32)
  observed=[]
  for native in (True,False):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
   u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F)
   u.mem_map(0x100000,0x10000)
   for p,data in seg:u.mem_write(p,data)
   u.mem_map(0x20000000,0x10000);u.mem_map(0x300000,0x1000)
   u.mem_write(addr+0x88,a.to_bytes(4,'little'));u.mem_write(addr+0x8c,b.to_bytes(4,'little'))
   u.reg_write(UC_ARM_REG_R0,addr);u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x300001)
   u.emu_start((0x08005f44 if native else sym['case_boot_sensor_flags_5f44'])|1,0x300000,count=30)
   observed.append(u.reg_read(UC_ARM_REG_R0))
  assert observed[0]==observed[1]==(a|b),(i,a,b,observed)
 print('PASS_CASE_SENSOR_FLAGS',256)
