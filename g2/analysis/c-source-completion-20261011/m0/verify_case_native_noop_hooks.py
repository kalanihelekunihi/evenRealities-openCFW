#!/usr/bin/env python3
"""Check authentic single-instruction CASE no-op hooks against C."""
from pathlib import Path
import random,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_boot_native_noop_hooks_candidate.c'
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
with tempfile.TemporaryDirectory() as d:
 d=Path(d);o=d/'s.o';subprocess.run(flags+[str(src),'-o',str(o)],check=True)
 elf=d/'o.elf';subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x100000',str(o),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
 with elf.open('rb') as f:
  e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
 rng=random.Random(0x5c26)
 for addr in (0x5c26,0x5e6c,0x5efc,0x5efe):
  assert F[addr:addr+2]==b'\x70\x47'
  name=f'case_boot_hook_{addr:04x}'
  for i in range(128):
   regs=[rng.getrandbits(32) for _ in range(4)];pair=[]
   for native in (True,False):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
    u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F);u.mem_map(0x100000,0x10000)
    for a,b in seg:u.mem_write(a,b)
    u.mem_map(0x20000000,0x10000)
    for reg,val in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),regs):u.reg_write(reg,val)
    u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20008001)
    u.emu_start((0x08000000+addr if native else sym[name])|1,0x20008000,count=20)
    pair.append([u.reg_read(reg) for reg in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)])
   assert pair[0]==pair[1]==regs,(name,i,pair,regs)
 print('PASS_CASE_NATIVE_NOOP_HOOKS',512)
