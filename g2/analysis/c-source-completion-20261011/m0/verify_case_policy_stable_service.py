#!/usr/bin/env python3
"""Bounded 0x7850 unchanged-service maintenance path."""
from pathlib import Path
import subprocess,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_policy_stable_service_candidate.c'
stub=H/'policy_stable_service_oracle_stubs.c'
stub.write_text('#include <stdint.h>\n__attribute__((noinline,used)) void case_policy_service_maintenance(void){__asm__ volatile("nop");}\n')
objs=[]
for s in (src,stub):
 o=H/(s.stem+'.oracle.o');objs.append(o)
 subprocess.run(['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c',str(s),'-o',str(o)],check=True)
elf=H/'policy_stable_service_oracle.elf'
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x00100000',*[str(o) for o in objs],'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
cases=itertools.product((0,9,10,11),(0,9,10,11),(0,1),(0,8,9,10,255))
checked=0
for left,right,mode,tick in cases:
 pair=[]
 for native in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F)
  u.mem_map(0x00100000,0x10000)
  for a,b in seg:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000)
  u.mem_write(0x200008b8,left.to_bytes(4,'little'));u.mem_write(0x200008d4,right.to_bytes(4,'little'));u.mem_write(0x200000f5,bytes([mode]));u.mem_write(0x20007fd0,tick.to_bytes(4,'little'))
  u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20001001)
  if native:u.reg_write(UC_ARM_REG_R4,0x2000087c)
  else:u.reg_write(UC_ARM_REG_R0,0x2000087c);u.reg_write(UC_ARM_REG_R1,tick)
  calls=[];target=0x080018e4 if native else sym['case_policy_service_maintenance']&~1
  def hook(u,a,size,ctx):
   if native and a==0x08007884:u.emu_stop();return
   if a==target:calls.append('maintenance');u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((0x08007850 if native else sym['case_policy_stable_service_7850'])|1,0x20001000,count=10000)
  pair.append((calls,bytes(u.mem_read(0x200000b8,8)),int.from_bytes(u.mem_read(0x20007fd0,4),'little') if native else u.reg_read(UC_ARM_REG_R0)))
 assert pair[0]==pair[1],(left,right,mode,tick,pair)
 checked+=1
print('PASS_CASE_POLICY_STABLE_SERVICE',checked)
