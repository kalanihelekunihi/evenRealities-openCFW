#!/usr/bin/env python3
"""Compare native CASE 0x01fc and standalone C little-endian reader."""
from pathlib import Path
import random,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_boot_le32_read_candidate.c'
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
with tempfile.TemporaryDirectory() as d:
 d=Path(d);o=d/'s.o';subprocess.run(flags+[str(src),'-o',str(o)],check=True)
 elf=d/'o.elf';subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x100000',str(o),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
 with elf.open('rb') as f:
  e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
 rng=random.Random(0x1fc)
 for i in range(256):
  sample=bytes(rng.getrandbits(8) for _ in range(8));pair=[]
  for native in (True,False):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
   u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F);u.mem_map(0x100000,0x10000)
   for a,b in seg:u.mem_write(a,b)
   u.mem_map(0x20000000,0x10000);u.mem_write(0x20000100,sample)
   u.reg_write(UC_ARM_REG_R0,0x20000100);u.reg_write(UC_ARM_REG_R2,rng.getrandbits(32))
   u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20008001)
   u.emu_start((0x080001fc if native else sym['case_boot_read_le32'])|1,0x20008000,count=100)
   pair.append(u.reg_read(UC_ARM_REG_R0))
  assert pair[0]==pair[1]==int.from_bytes(sample[:4],'little'),(i,sample.hex(),pair)
 print('PASS_CASE_LE32_READ',256)
