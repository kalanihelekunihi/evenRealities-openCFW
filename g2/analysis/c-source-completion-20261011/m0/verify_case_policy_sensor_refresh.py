#!/usr/bin/env python3
"""Original/source 0x3a3c/0x3a60 RAM effects and preserved caller bytes."""
from pathlib import Path
import subprocess,random
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_policy_sensor_refresh_candidate.c'
obj=H/'application_policy_sensor_refresh_candidate.oracle.o'
subprocess.run(['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
elf=H/'policy_sensor_refresh_oracle.elf';subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x00100000',str(obj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
rng=random.Random(0x3a3c3a60);checked=0
for side in ('left','right'):
 for i in range(80):
  seed=bytes(rng.randrange(256) for _ in range(0x68));prior=rng.randrange(256);active=i&1
  pair=[]
  for native in (True,False):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
   u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F)
   u.mem_map(0x00100000,0x10000)
   for a,b in seg:u.mem_write(a,b)
   u.mem_map(0x20000000,0x10000);u.mem_write(0x2000087c,seed)
   u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20001001)
   if native:
    u.reg_write(UC_ARM_REG_R0,0x2000089c if side=='left' else 0x200008bc)
    u.reg_write(UC_ARM_REG_R3,prior);u.reg_write(UC_ARM_REG_R2,prior)
   else:
    u.reg_write(UC_ARM_REG_R0,0x2000089c if side=='left' else 0x200008bc)
    u.reg_write(UC_ARM_REG_R1,prior);u.reg_write(UC_ARM_REG_R2,active)
   entry=(0x08003a3c if side=='left' else 0x08003a60) if native else sym['case_policy_sensor_'+side+'_refresh']
   u.emu_start(entry|1,0x20001000,count=1000)
   retained=u.reg_read(UC_ARM_REG_R3 if side=='left' else UC_ARM_REG_R2) if native else u.reg_read(UC_ARM_REG_R0)
   pair.append((bytes(u.mem_read(0x2000087c,0x68)),retained&0xff))
  assert pair[0]==pair[1],(side,i,[(x[0].hex(),x[1]) for x in pair])
  checked+=1
print('PASS_CASE_POLICY_SENSOR_REFRESH',checked)
