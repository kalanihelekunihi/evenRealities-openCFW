#!/usr/bin/env python3
"""Native/source task priority restoration at scheduler list cuts."""
from pathlib import Path
import random,subprocess,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_policy_task_notify_resume_candidate.c';obj=H/'application_policy_task_notify_resume.oracle.o';stub=H/'application_policy_task_notify_resume.oracle_stub.c';stubobj=H/'application_policy_task_notify_resume.oracle_stub.o';elf=H/'application_policy_task_notify_resume.oracle.elf'
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
subprocess.run(flags+[str(src),'-o',str(obj)],check=True)
stub.write_text('#include <stdint.h>\nvoid case_policy_task_unlink(uint32_t a){(void)a;}\nvoid case_policy_task_list_insert(uint32_t a,uint32_t b){(void)a;(void)b;}\n')
subprocess.run(flags+[str(stub),'-o',str(stubobj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x00100000',str(obj),str(stubobj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
rng=random.Random(0xcb38)
for i in range(96):
 task=0 if i%13==0 else 0x20002000;depth=i%4+1;priority=rng.randrange(15);inherited=rng.randrange(15);max_priority=rng.randrange(15);pair=[]
 for native in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F)
  u.mem_map(0x00100000,0x10000)
  for a,b in seg:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_write(0x20000128,struct.pack('<I',0x20002000));u.mem_write(0x20000138,struct.pack('<I',max_priority))
  for off,v in [(44,priority),(76,inherited),(80,depth)]:u.mem_write(0x20002000+off,struct.pack('<I',v))
  u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20008001);u.reg_write(UC_ARM_REG_R0,task)
  cuts=({0x0800bf2c:'unlink',0x0800bfe2:'insert'} if native else {sym['case_policy_task_unlink']&~1:'unlink',sym['case_policy_task_list_insert']&~1:'insert'})
  trace=[]
  def hook(uc,a,size,_):
   k=cuts.get(a)
   if k is not None:trace.append((k,uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1)) if k=='insert' else (k,uc.reg_read(UC_ARM_REG_R0)));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((0x0800cb38 if native else sym['case_policy_task_notify_resume'])|1,0x20008000,count=250)
  pair.append((u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(0x20002018,60)),bytes(u.mem_read(0x20000138,4)),trace))
 assert pair[0]==pair[1],(i,pair)
print('PASS_CASE_TASK_NOTIFY_RESUME',96)
