#!/usr/bin/env python3
"""Native/source task notify and scheduler-start gate comparisons."""
from pathlib import Path
import random,subprocess,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3];folder=R/'g2/components/case/startup_candidate_20261011'
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
objs=[]
for base in ('application_policy_task_notify_candidate','application_boot_scheduler_start_candidate'):
 obj=H/(base+'.oracle.o');subprocess.run(flags+[str(folder/(base+'.c')),'-o',str(obj)],check=True);objs.append(obj)
stub=H/'application_policy_start_notify.oracle_stub.c';stubobj=H/'application_policy_start_notify.oracle_stub.o';elf=H/'application_policy_start_notify.oracle.elf'
stub.write_text('''#include <stdint.h>\nvoid case_policy_task_notify_core(uint32_t x){(void)x;}\nvoid case_boot_scheduler_activate(void){}\n''')
subprocess.run(flags+[str(stub),'-o',str(stubobj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x00100000',*[str(x) for x in objs],str(stubobj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
rng=random.Random(0xa900)
for name,naddr in [('task_notify',0x0800aa24),('scheduler_start',0x0800a900)]:
 for i in range(96):
  arg=0 if i%3==0 else 0x20000300;state=i%3;priority=rng.randrange(2**32);pair=[]
  for native in (True,False):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
   u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F)
   u.mem_map(0x00100000,0x10000)
   for a,b in seg:u.mem_write(a,b)
   u.mem_map(0x20000000,0x10000);u.mem_write(0x20000178,struct.pack('<I',state))
   u.mem_map(0xe000e000,0x1000);u.mem_write(0xe000ed1c,struct.pack('<I',priority))
   u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20001001);u.reg_write(UC_ARM_REG_R0,arg)
   child=(0x0800c2f8 if name=='task_notify' else 0x0800c284) if native else sym['case_policy_task_notify_core' if name=='task_notify' else 'case_boot_scheduler_activate']&~1
   calls=[]
   def hook(uc,a,size,_):
    if a!=child:return
    calls.append(uc.reg_read(UC_ARM_REG_R0) if name=='task_notify' else 1)
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   entry=naddr if native else sym['case_policy_task_notify' if name=='task_notify' else 'case_boot_scheduler_start']
   u.emu_start(entry|1,0x20001000,count=500)
   pair.append((u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(0x20000178,4)),bytes(u.mem_read(0xe000ed1c,4)),calls))
  assert pair[0]==pair[1],(name,i,pair)
 print('PASS_CASE_POLICY_'+name.upper(),96)
