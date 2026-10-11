#!/usr/bin/env python3
"""Controlled SysTick/scheduler-run native/source MMIO comparison."""
from pathlib import Path
import random,subprocess,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3];folder=R/'g2/components/case/startup_candidate_20261011'
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
objs=[]
for base in ('application_boot_scheduler_run_candidate','application_boot_systick_candidate'):
 obj=H/(base+'.oracle.o');subprocess.run(flags+[str(folder/(base+'.c')),'-o',str(obj)],check=True);objs.append(obj)
stub=H/'application_boot_scheduler_run.oracle_stub.c';stubobj=H/'application_boot_scheduler_run.oracle_stub.o';elf=H/'application_boot_scheduler_run.oracle.elf'
stub.write_text('''#include <stdint.h>\nuint32_t case_policy_sensor_divide(uint32_t a,uint32_t b){(void)a;(void)b;return 0;}\nvoid case_boot_context_switch(void){}\n''')
subprocess.run(flags+[str(stub),'-o',str(stubobj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x00100000',*[str(x) for x in objs],str(stubobj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
rng=random.Random(0xc57c)
for i in range(96):
 initial=rng.randrange(2**32);clock=rng.randrange(2**32);pair=[]
 for native in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F)
  u.mem_map(0x00100000,0x10000)
  for a,b in seg:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_write(0x20000124,struct.pack('<I',clock));u.mem_write(0x2000019c,struct.pack('<I',i+1))
  u.mem_map(0xe000e000,0x1000);u.mem_write(0xe000ed20,struct.pack('<I',initial))
  u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20001001)
  div=0x08000160 if native else sym['case_policy_sensor_divide']&~1
  context=0x080000cc if native else sym['case_boot_context_switch']&~1
  trace=[]
  def hook(uc,a,size,_):
   if a==div:
    trace.append(('divide',uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1)))
    uc.reg_write(UC_ARM_REG_R0,clock//1000)
   elif a==context:trace.append(('context',))
   else:return
   uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((0x0800c57c if native else sym['case_boot_scheduler_run'])|1,0x20001000,count=2000)
  pair.append((bytes(u.mem_read(0xe000e010,0x20)),bytes(u.mem_read(0x2000019c,4)),trace))
 assert pair[0]==pair[1],(i,pair)
print('PASS_CASE_BOOT_SCHEDULER_RUN',96)
