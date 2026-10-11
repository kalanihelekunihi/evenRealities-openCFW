#!/usr/bin/env python3
"""Native/source immediate scheduler message insertion at copy/wake cuts."""
from pathlib import Path
import random,subprocess,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_policy_task_message_special_candidate.c';obj=H/'application_policy_task_message_special.oracle.o';stub=H/'application_policy_task_message_special.oracle_stub.c';stubobj=H/'application_policy_task_message_special.oracle_stub.o';elf=H/'application_policy_task_message_special.oracle.elf'
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
subprocess.run(flags+[str(src),'-o',str(obj)],check=True)
stub.write_text('#include <stdint.h>\nvoid case_policy_message_copy(uint32_t a,const uint32_t*b,uint32_t c){(void)a;(void)b;(void)c;}\nuint32_t case_boot_pool_wake_waiter(uint32_t a){(void)a;return 0;}\n')
subprocess.run(flags+[str(stub),'-o',str(stubobj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x00100000',str(obj),str(stubobj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
rng=random.Random(0xc7a8)
for i in range(80):
 scheduler=0x20002200;args=0x20002300;notify=0x20002400 if i%3 else 0;mode=2 if i%9==0 else 0;meta=1;count=i%4;capacity=1 if mode==2 else 2;seq=255 if i%2 else i%6;waiters=i%3==1;wake=i%4==0;pair=[]
 for native in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F)
  u.mem_map(0x00100000,0x10000)
  for a,b in seg:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000)
  u.mem_write(scheduler+56,struct.pack('<I',count));u.mem_write(scheduler+60,struct.pack('<I',capacity));u.mem_write(scheduler+36,struct.pack('<I',int(waiters)));u.mem_write(scheduler+69,bytes((seq,)));u.mem_write(args,struct.pack('<III',4,i,0x20001000));u.mem_write(0x20007fc0,struct.pack('<I',meta))
  if notify:u.mem_write(notify,struct.pack('<I',0))
  u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20008001);u.reg_write(UC_ARM_REG_R0,scheduler);u.reg_write(UC_ARM_REG_R1,args);u.reg_write(UC_ARM_REG_R2,notify);u.reg_write(UC_ARM_REG_R3,mode)
  cuts=({0x0800ad48:'copy',0x0800cba0:'wake'} if native else {sym['case_policy_message_copy']&~1:'copy',sym['case_boot_pool_wake_waiter']&~1:'wake'})
  trace=[]
  def hook(uc,a,size,_):
   k=cuts.get(a)
   if k is None:return
   trace.append((k,uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1),uc.reg_read(UC_ARM_REG_R2)) if k=='copy' else (k,uc.reg_read(UC_ARM_REG_R0)))
   if k=='wake':uc.reg_write(UC_ARM_REG_R0,int(wake))
   uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((0x0800c7a8 if native else sym['case_policy_task_message_special'])|1,0x20008000,count=250)
  pair.append((u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(scheduler+64,8)),bytes(u.mem_read(notify,4)) if notify else None,trace))
 assert pair[0]==pair[1],(i,pair)
print('PASS_CASE_TASK_MESSAGE_SPECIAL',80)
