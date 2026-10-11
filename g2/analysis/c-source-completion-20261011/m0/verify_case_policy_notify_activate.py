#!/usr/bin/env python3
"""Bounded native/source task-notify core and scheduler activation comparisons."""
from pathlib import Path
import random,subprocess,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3];folder=R/'g2/components/case/startup_candidate_20261011'
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
objs=[]
for base in ('application_policy_notify_core_candidate','application_boot_scheduler_activate_candidate'):
 obj=H/(base+'.oracle.o');subprocess.run(flags+[str(folder/(base+'.c')),'-o',str(obj)],check=True);objs.append(obj)
stub=H/'application_policy_notify_activate.oracle_stub.c';stubobj=H/'application_policy_notify_activate.oracle_stub.o';elf=H/'application_policy_notify_activate.oracle.elf'
stub.write_text('''#include <stdint.h>\nvoid case_policy_scheduler_lock(void){}\nuint32_t case_policy_scheduler_unlock(void){return 0;}\nvoid case_policy_task_unlink(uint32_t x){(void)x;}\nvoid case_policy_task_list_insert(uint32_t x,uint32_t y){(void)x;(void)y;}\nvoid case_policy_task_wake_cleanup(void){}\nuint32_t case_policy_task_reschedule(void){return 0;}\nvoid case_policy_task_wake_dispatch(void){}\nvoid case_boot_idle_task_entry(void*x){(void)x;}\nconst char case_boot_idle_task_name[5]="IDLE";\nuint32_t case_boot_task_create(void(*f)(void*),const char*n,uint32_t a,void*b,uint32_t c,uint32_t d,uint32_t e){(void)f;(void)n;(void)a;(void)b;(void)c;(void)d;(void)e;return 0;}\nuint32_t case_boot_scheduler_ready(void){return 0;}\nvoid case_boot_scheduler_run(void){}\n''')
subprocess.run(flags+[str(stub),'-o',str(stubobj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x00100000',*[str(x) for x in objs],str(stubobj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
rng=random.Random(0xc2f8)
for name,naddr in [('notify',0x0800c2f8),('activate',0x0800c284)]:
 for i in range(80):
  mem=bytearray(0x10000);task=0x20000300;struct.pack_into('<I',mem,0x128,task)
  struct.pack_into('<I',mem,0x128+20,i&1);struct.pack_into('<I',mem,0x128+48,0)
  struct.pack_into('<I',mem,0x300+40,i&1);mem[0x300+0x58]=i%3
  struct.pack_into('<I',mem,0x14a4,i%4)
  pair=[]
  for native in (True,False):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
   u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F)
   u.mem_map(0x00100000,0x10000)
   for a,b in seg:u.mem_write(a,b)
   u.mem_map(0x20000000,0x10000);u.mem_write(0x20000000,bytes(mem))
   u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20001001);u.reg_write(UC_ARM_REG_R0,task if i&1 else 0)
   mapping=({0x0800bffc:'lock',0x0800c014:'unlock',0x0800bf2c:'unlink',0x0800bfe2:'insert',0x0800b260:'cleanup',0x0800c0a0:'reschedule',0x0800c390:'dispatch',0x0800ca06:'create',0x0800cd20:'ready',0x0800c57c:'run'} if native else {sym['case_policy_'+x]&~1:k for x,k in [('scheduler_lock','lock'),('scheduler_unlock','unlock'),('task_unlink','unlink'),('task_list_insert','insert'),('task_wake_cleanup','cleanup'),('task_reschedule','reschedule'),('task_wake_dispatch','dispatch')]}|{sym['case_boot_'+x]&~1:k for x,k in [('task_create','create'),('scheduler_ready','ready'),('scheduler_run','run')]})
   trace=[]
   def hook(uc,a,size,_):
    k=mapping.get(a)
    if k is None:return
    if k=='create':
     sp=uc.reg_read(UC_ARM_REG_SP);trace.append((k,uc.reg_read(UC_ARM_REG_R2),uc.reg_read(UC_ARM_REG_R3),tuple(struct.unpack('<III',bytes(uc.mem_read(sp,12))))))
     uc.reg_write(UC_ARM_REG_R0,0 if i%3==0 else 0x20000500)
    else:
     trace.append((k,uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1)) if k=='insert' else (k,uc.reg_read(UC_ARM_REG_R0)) if k=='unlink' else (k,))
     if k=='ready':uc.reg_write(UC_ARM_REG_R0,0 if i%3==1 else 1)
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   entry=naddr if native else sym['case_policy_task_notify_core' if name=='notify' else 'case_boot_scheduler_activate']
   u.emu_start(entry|1,0x20001000,count=2000)
   pair.append((bytes(u.mem_read(0x20000128,0x40)),bytes(u.mem_read(task,0x60)),trace))
  assert pair[0]==pair[1],(name,i,pair[0][2],pair[1][2])
 print('PASS_CASE_POLICY_'+name.upper(),80)
