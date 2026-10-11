#!/usr/bin/env python3
"""Compare 0x3a00 fake standby state mutation with source on randomized RAM."""
from pathlib import Path
import random, subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn.arm_const import *

H=Path(__file__).resolve().parent; R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_policy_fake_standby_lowers_candidate.c'
obj=H/'application_policy_fake_standby_lowers.oracle.o'; elf=H/'application_policy_fake_standby_lowers.oracle.elf'
subprocess.run(['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
stub=H/'application_policy_fake_standby_lowers.oracle_stub.c';stub_obj=H/'application_policy_fake_standby_lowers.oracle_stub.o'
stub.write_text('''#include <stdint.h>\nvoid case_policy_task_cancel(uint32_t x){(void)x;}\nvoid case_policy_log(uint32_t x){(void)x;}\n''')
subprocess.run(['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c',str(stub),'-o',str(stub_obj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x00100000',str(obj),str(stub_obj),'-o',str(elf)],check=True)
with elf.open('rb') as f:
 e=ELFFile(f); sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}; seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
rng=random.Random(0x3a00); checked=0
for side in (0,1,2,0xffffffff):
 for i in range(64):
  seed=bytes(rng.randrange(256) for _ in range(0x68)); pair=[]
  for native in (True,False):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
   u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F)
   u.mem_map(0x00100000,0x10000)
   for a,b in seg:u.mem_write(a,b)
   u.mem_map(0x20000000,0x10000);u.mem_write(0x2000087c,seed)
   u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20001001);u.reg_write(UC_ARM_REG_R0,side)
   u.emu_start((0x08003a00 if native else sym['case_policy_fake_standby_set'])|1,0x20001000,count=1000)
   pair.append(bytes(u.mem_read(0x2000087c,0x68)))
  assert pair[0]==pair[1],(side,i)
  checked+=1
print('PASS_CASE_POLICY_FAKE_STANDBY_SET',checked)
checked=0
for enabled in (0,1,2):
 for i in range(32):
  shared=bytearray(rng.randrange(256) for _ in range(0x40));shared[7]=enabled
  state=bytes(rng.randrange(256) for _ in range(0x68)); pair=[]
  for native in (True,False):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
   u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F)
   u.mem_map(0x00100000,0x10000)
   for a,b in seg:u.mem_write(a,b)
   u.mem_map(0x20000000,0x10000);u.mem_write(0x200000b8,bytes(shared));u.mem_write(0x2000087c,state)
   u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20001001)
   calls=[]
   def hook(uc,addr,size,_):
    kinds={0x0800aa00:'cancel',0x08009170:'log'} if native else {sym['case_policy_task_cancel']&~1:'cancel',sym['case_policy_log']&~1:'log'}
    if addr in kinds:
     calls.append((kinds[addr],uc.reg_read(UC_ARM_REG_R0)))
     uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   entry=0x080013b8 if native else sym['case_policy_fake_standby_clear']
   u.emu_start(entry|1,0x20001000,count=2000)
   pair.append((bytes(u.mem_read(0x200000b8,0x40)),bytes(u.mem_read(0x2000087c,0x68)),calls))
  assert pair[0]==pair[1],(enabled,i,pair[0][2],pair[1][2])
  checked+=1
print('PASS_CASE_POLICY_FAKE_STANDBY_CLEAR',checked)
