#!/usr/bin/env python3
"""Original/source idle standby call and register sequence through WFI child."""
from pathlib import Path
import subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
FW=(ROOT/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
SRC=ROOT/'g2/components/case/startup_candidate_20261011/application_policy_standby_candidate.c'
names=['policy_log','init_pmic_read','init_power_set','init_boost_set','init_wake_mask','init_wake_config','init_wake_clock']
orig=[0x08009170,0x080035d4,0x08002c8e,0x08002c30,0x08005094,0x080050a8,0x080050c4]
stub=HERE/'policy_standby_oracle_stubs.c';stub.write_text('#include <stdint.h>\n'+''.join('__attribute__((noinline,used)) void case_'+n+'(void){__asm__ volatile("nop");}\n' for n in names))
objs=[]
for source in (SRC,stub):
 obj=HERE/(source.stem+'.oracle.o');objs.append(obj)
 subprocess.run(['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-c',str(source),'-o',str(obj)],check=True)
elf=HERE/'policy_standby_oracle.elf';subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x00100000',*[str(x) for x in objs],'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as stream:
 e=ELFFile(stream);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
for silent in (0,1):
 pair=[]
 for original in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(FW)+4095)&~4095);u.mem_write(0x08000000,FW);u.mem_map(0x00100000,0x10000)
  for a,b in segments:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_map(0x40007000,0x1000);u.mem_write(0x200000bf,bytes([silent]))
  sp=0x20007fc0;u.reg_write(UC_ARM_REG_SP,sp);u.reg_write(UC_ARM_REG_LR,0x20001001)
  if original:
   u.reg_write(UC_ARM_REG_R4,0x2000087c);u.reg_write(UC_ARM_REG_R5,0);u.reg_write(UC_ARM_REG_R6,10)
   u.mem_write(sp,(0x200008bc).to_bytes(4,'little')+(0x2000089c).to_bytes(4,'little'))
  lookup={a:n for a,n in zip(orig if original else [sym['case_'+n]&~1 for n in names],names)}
  calls=[]
  def hook(u,a,size,user):
   if a in lookup:
    calls.append((lookup[a],None if lookup[a]=='init_wake_clock' else u.reg_read(UC_ARM_REG_R0)))
    if lookup[a]=='init_wake_clock':u.emu_stop()
    else:u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((0x08007214 if original else sym['case_policy_standby_idle'])|1,0x20001000,count=10000)
  pair.append((calls,bytes(u.mem_read(0x40007018,4))))
 assert pair[0]==pair[1],(silent,pair)
print('PASS_CASE_POLICY_STANDBY',2)
