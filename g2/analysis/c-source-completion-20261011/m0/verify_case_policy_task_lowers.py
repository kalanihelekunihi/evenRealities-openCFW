#!/usr/bin/env python3
"""Bounded native/source scheduler sleep and cancel-core comparisons."""
from pathlib import Path
import random,subprocess,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_policy_task_lowers_candidate.c';obj=H/'application_policy_task_lowers.oracle.o';stub=H/'application_policy_task_lowers.oracle_stub.c';stub_obj=H/'application_policy_task_lowers.oracle_stub.o';elf=H/'application_policy_task_lowers.oracle.elf'
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
subprocess.run(flags+[str(src),'-o',str(obj)],check=True)
names=['case_policy_task_sleep_enter','case_policy_task_sleep_enqueue','case_policy_task_sleep_exit','case_policy_task_reschedule','case_policy_scheduler_lock','case_policy_task_valid','case_policy_task_unlink','case_policy_task_list_insert','case_policy_scheduler_unlock']
stub.write_text('#include <stdint.h>\n'+'\n'.join(('uint32_t '+n+'(uint32_t x){(void)x;return 0;}' if n.endswith(('exit','reschedule','valid','unlock')) else 'void '+n+'(uint32_t x,uint32_t y){(void)x;(void)y;}' if n.endswith(('enqueue','insert')) else 'void '+n+'(uint32_t x){(void)x;}' if n.endswith('unlink') else 'void '+n+'(void){}') for n in names)+'\n')
subprocess.run(flags+[str(stub),'-o',str(stub_obj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x00100000',str(obj),str(stub_obj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
kinds=['enter','enqueue','exit','reschedule','lock','valid','unlink','insert','unlock']
native={a:k for a,k in zip([0x0800c380,0x0800abb0,0x0800cc0c,0x0800c0a0,0x0800bffc,0x0800b330,0x0800bf2c,0x0800bfe2,0x0800c014],kinds)}
source={sym[n]&~1:k for n,k in zip(names,kinds)}
rng=random.Random(0xc228);counts={'sleep':0,'cancel':0}
for kind in ('sleep','cancel'):
 for i in range(96):
  task=0x20000300;current=0x20000400
  sched=bytearray(rng.randrange(256) for _ in range(0x38));struct.pack_into('<I',sched,0,task if i%5==0 else current);struct.pack_into('<I',sched,0x30,0)
  taskbytes=bytearray(rng.randrange(256) for _ in range(0x40));currentbytes=bytearray(rng.randrange(256) for _ in range(0x40));struct.pack_into('<I',taskbytes,0x2c,i%5);struct.pack_into('<I',currentbytes,0x2c,(i+2)%5)
  arg=([0,1,2,10][i%4] if kind=='sleep' else task)
  pair=[]
  for is_native in (True,False):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
   u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F)
   u.mem_map(0x00100000,0x10000)
   for a,b in seg:u.mem_write(a,b)
   u.mem_map(0x20000000,0x10000);u.mem_write(0x20000128,bytes(sched));u.mem_write(task,bytes(taskbytes));u.mem_write(current,bytes(currentbytes))
   u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20001001);u.reg_write(UC_ARM_REG_R0,arg)
   trace=[]
   def hook(uc,addr,size,_):
    name=(native if is_native else source).get(addr)
    if name is None:return
    r0=uc.reg_read(UC_ARM_REG_R0);r1=uc.reg_read(UC_ARM_REG_R1)
    trace.append((name,r0,r1) if name in ('enqueue','insert') else (name,r0) if name in ('valid','unlink') else (name,))
    if name in ('valid','exit','reschedule','unlock'):uc.reg_write(UC_ARM_REG_R0,{'valid':i&1,'exit':i%3==0 and 5,'reschedule':17,'unlock':19}[name])
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   entry=(0x0800c128 if kind=='sleep' else 0x0800c228) if is_native else sym['case_policy_task_'+('sleep' if kind=='sleep' else 'cancel_core')]
   u.emu_start(entry|1,0x20001000,count=2000)
   pair.append((u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(0x20000128,0x38)),trace))
  assert pair[0]==pair[1],(kind,i,pair[0],pair[1])
  counts[kind]+=1
print('PASS_CASE_POLICY_TASK_LOWERS',counts)
