#!/usr/bin/env python3
"""Native/source PMIC GPIO write traces and sample results."""
from pathlib import Path
import random,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_pmic_bus_primitives_candidate.c';obj=H/'application_pmic_bus_primitives.oracle.o';elf=H/'application_pmic_bus_primitives.oracle.elf'
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
subprocess.run(flags+[str(src),'-o',str(obj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x00100000',str(obj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
entries=[('ack_continue',0xa3d2),('ack_last',0xa414),('read_byte',0xa436),('write_byte',0xa46c),('start',0xa4b4),('stop',0xa4dc),('ack',0xa4fa)]
rng=random.Random(0xa3d2)
for i in range(112):
 name,addr=entries[i%len(entries)];mode=i&1;value=rng.randrange(256);pin=rng.randrange(2);pair=[]
 for native in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F)
  u.mem_map(0x00100000,0x10000)
  for a,b in seg:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_write(0x20000114,bytes((mode,)))
  u.mem_map(0x50000000,0x10000);u.mem_write(0x50000410,(pin*(8 if mode else 16)).to_bytes(4,'little'))
  u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20008001);u.reg_write(UC_ARM_REG_R0,value)
  trace=[]
  def hook(uc,access,a,size,v,_):
   if a in (0x50000418,0x50000428):trace.append((a,v))
  u.hook_add(UC_HOOK_MEM_WRITE,hook)
  u.emu_start((0x08000000+addr if native else sym['case_pmic_bus_'+name])|1,0x20008000,count=200000)
  pair.append((u.reg_read(UC_ARM_REG_R0) if name in ('read_byte','ack') else None,trace))
 assert pair[0]==pair[1],(i,name,pair)
print('PASS_CASE_PMIC_BUS_PRIMITIVES',112)
