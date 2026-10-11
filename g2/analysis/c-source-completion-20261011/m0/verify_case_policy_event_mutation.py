#!/usr/bin/env python3
"""Native/source thread-mode event clear and signal wrapper comparisons."""
from pathlib import Path
import random,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_policy_event_mutation_candidate.c';obj=H/'application_policy_event_mutation.oracle.o';stub=H/'application_policy_event_mutation.oracle_stub.c';stubobj=H/'application_policy_event_mutation.oracle_stub.o';elf=H/'application_policy_event_mutation.oracle.elf'
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
subprocess.run(flags+[str(src),'-o',str(obj)],check=True)
stub.write_text('#include <stdint.h>\nuint32_t case_policy_event_receive(uint32_t a,uint32_t b){(void)a;(void)b;return 0;}\nuint32_t case_policy_event_receive_irq(uint32_t a){(void)a;return 0;}\nuint32_t case_policy_event_irq_apply(uint32_t a,uint32_t b,uint32_t c,uint32_t d){(void)a;(void)b;(void)c;(void)d;return 0;}\nuint32_t case_policy_task_event_send(uint32_t a,uint32_t b,uint32_t c,uint32_t d,uint32_t e){(void)a;(void)b;(void)c;(void)d;(void)e;return 0;}\n')
subprocess.run(flags+[str(stub),'-o',str(stubobj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x00100000',str(obj),str(stubobj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
rng=random.Random(0xa7d2)
for i in range(96):
 which=i&1;event=0 if i%13==0 else 0x20002000;mask=(0x01000000 if i%11==0 else rng.randrange(0x1000000));result=rng.getrandbits(32);pair=[]
 for native in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F)
  u.mem_map(0x00100000,0x10000)
  for a,b in seg:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000)
  u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20008001);u.reg_write(UC_ARM_REG_R0,event);u.reg_write(UC_ARM_REG_R1,mask)
  cuts=({0x0800c44c:'receive',0x0800cd80:'send'} if native else {sym['case_policy_event_receive']&~1:'receive',sym['case_policy_task_event_send']&~1:'send'})
  trace=[]
  def hook(uc,a,size,_):
   k=cuts.get(a)
   if k is None:return
   trace.append((k,uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1),uc.reg_read(UC_ARM_REG_R2)))
   uc.reg_write(UC_ARM_REG_R0,result);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  entry=0x0800a7d2 if which==0 else 0x0800aaf0
  source='case_policy_event_clear' if which==0 else 'case_policy_event_signal'
  u.emu_start((entry if native else sym[source])|1,0x20008000,count=200)
  pair.append((u.reg_read(UC_ARM_REG_R0),trace))
 assert pair[0]==pair[1],(i,pair)
print('PASS_CASE_POLICY_EVENT_MUTATION',96)
