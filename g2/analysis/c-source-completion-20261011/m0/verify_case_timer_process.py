#!/usr/bin/env python3
"""CASE b1fc stock/C timer process branch and child-call oracle."""
from pathlib import Path
import random,struct,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_boot_timer_process_candidate.c';obj=H/'timer_process.oracle.o';stub=H/'timer_process.oracle_stub.c';stubobj=H/'timer_process.oracle_stub.o';elf=H/'timer_process.oracle.elf'
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
subprocess.run(flags+[str(src),'-o',str(obj)],check=True)
stub.write_text('#include <stdint.h>\nvoid case_policy_task_sleep_enter(void){}\nuint32_t case_policy_task_sleep_exit(void){return 0;}\nuint32_t case_boot_timer_now(uint32_t *x){*x=0;return 0;}\nvoid case_boot_timer_process_due(uint32_t a,uint32_t b){(void)a;(void)b;}\nvoid case_boot_timer_queue_wait(uint32_t a,uint32_t b,uint32_t c){(void)a;(void)b;(void)c;}\nuint32_t case_policy_task_reschedule(void){return 0;}\n')
subprocess.run(flags+[str(stub),'-o',str(stubobj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x100000',str(obj),str(stubobj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
rng=random.Random(0xb1fc)
for i in range(128):
 deadline=rng.getrandbits(8);now=rng.getrandbits(8);wait=i%3==0;overflow=i%11==0;queue_nonempty=i%4==0;exit_result=i%5==0;pair=[]
 for native in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F);u.mem_map(0x00100000,0x10000)
  for a,b in seg:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_write(0x20000164,struct.pack('<5I',0x20004000,0,0,0,0x20004100));u.mem_write(0x20004100,struct.pack('<I',queue_nonempty))
  u.reg_write(UC_ARM_REG_R0,deadline);u.reg_write(UC_ARM_REG_R1,wait);u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20008001)
  targets=({0x0800c380:'enter',0x0800b284:'now',0x0800cc0c:'exit',0x0800b0a0:'due',0x0800c0e0:'wait',0x0800c0a0:'switch'} if native else {sym['case_policy_task_sleep_enter']&~1:'enter',sym['case_boot_timer_now']&~1:'now',sym['case_policy_task_sleep_exit']&~1:'exit',sym['case_boot_timer_process_due']&~1:'due',sym['case_boot_timer_queue_wait']&~1:'wait',sym['case_policy_task_reschedule']&~1:'switch'})
  calls=[]
  def hook(uc,a,size,_):
   kind=targets.get(a)
   if kind is None:return
   r0=uc.reg_read(UC_ARM_REG_R0);r1=uc.reg_read(UC_ARM_REG_R1);r2=uc.reg_read(UC_ARM_REG_R2)
   calls.append((kind,r0,r1,r2) if kind=='wait' else (kind,r0,r1) if kind=='due' else (kind,))
   if kind=='now':uc.mem_write(r0,struct.pack('<I',overflow));uc.reg_write(UC_ARM_REG_R0,now)
   elif kind=='exit':uc.reg_write(UC_ARM_REG_R0,exit_result)
   else:uc.reg_write(UC_ARM_REG_R0,0)
   uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((0x0800b1fc if native else sym['case_boot_timer_process'])|1,0x20008000,count=250)
  pair.append(calls)
 assert pair[0]==pair[1],(i,deadline,now,wait,overflow,queue_nonempty,pair)
print('PASS_CASE_TIMER_PROCESS',128)
