#!/usr/bin/env python3
"""Compare all-idle 0x7214 transition through native OTA-decision boundary."""
from pathlib import Path
import subprocess,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
FW=(ROOT/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
SRC=ROOT/'g2/components/case/startup_candidate_20261011/application_policy_idle_candidate.c'
stub=HERE/'policy_idle_oracle_stubs.c';stub.write_text('void case_policy_periodic_power_check(void){}\nvoid case_policy_standby_idle(void){}\n')
objs=[]
for source in (SRC,stub):
 obj=HERE/(source.stem+'.oracle.o');objs.append(obj)
 subprocess.run(['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-c',str(source),'-o',str(obj)],check=True)
elf=HERE/'policy_idle_oracle.elf';subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x00100000',*[str(x) for x in objs],'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as stream:
 e=ELFFile(stream);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
checked=0
for seconds,idle in itertools.product((0,1,4,5,0xffffffff),(0,1,9,11)):
 pair=[]
 for original in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(FW)+4095)&~4095);u.mem_write(0x08000000,FW);u.mem_map(0x00100000,0x10000)
  for a,b in segments:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_write(0x20000884,seconds.to_bytes(4,'little'));u.mem_write(0x20000888,(17).to_bytes(4,'little'))
  sp=0x20007fc0;u.reg_write(UC_ARM_REG_SP,sp);u.reg_write(UC_ARM_REG_LR,0x20001001)
  if original:
   u.mem_write(sp,(0x200008bc).to_bytes(4,'little')+(0x2000089c).to_bytes(4,'little'))
   u.reg_write(UC_ARM_REG_R4,0x2000087c);u.reg_write(UC_ARM_REG_R5,0);u.reg_write(UC_ARM_REG_R6,idle)
   def stop(u,a,size,user):
    if a==0x08007376:u.emu_stop()
   u.hook_add(UC_HOOK_CODE,stop)
   u.emu_start(0x08007215,0x20001000,count=10000)
   assert u.reg_read(UC_ARM_REG_PC)==0x08007376,(seconds,idle,hex(u.reg_read(UC_ARM_REG_PC)))
   out_idle=u.reg_read(UC_ARM_REG_R6)
  else:
   u.mem_write(0x20007000,(0x2000087c).to_bytes(4,'little')+idle.to_bytes(4,'little'))
   u.reg_write(UC_ARM_REG_R0,0x20007000)
   u.emu_start(sym['case_policy_idle_step_7214']|1,0x20001000,count=10000)
   assert u.reg_read(UC_ARM_REG_R0)==1
   out_idle=int.from_bytes(u.mem_read(0x20007004,4),'little')
  pair.append((bytes(u.mem_read(0x20000884,8)),out_idle))
 assert pair[0]==pair[1],(seconds,idle,pair)
 checked+=1
print('PASS_CASE_POLICY_IDLE',checked)
