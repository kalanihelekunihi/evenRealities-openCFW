#!/usr/bin/env python3
"""Native/source task event routing at scheduler queue child cuts."""
from pathlib import Path
import random,subprocess,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_policy_event_dispatch_candidate.c';obj=H/'application_policy_event_dispatch.oracle.o';stub=H/'application_policy_event_dispatch.oracle_stub.c';stubobj=H/'application_policy_event_dispatch.oracle_stub.o';elf=H/'application_policy_event_dispatch.oracle.elf'
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
subprocess.run(flags+[str(src),'-o',str(obj)],check=True)
stub.write_text('#include <stdint.h>\nuint32_t case_policy_irq_event_dispatch(uint32_t a,uint32_t b,uint32_t c,uint32_t d){(void)a;(void)b;(void)c;(void)d;return 0;}\nuint32_t case_policy_task_lookup(uint32_t a){(void)a;return 0;}\nuint32_t case_policy_task_message_send(uint32_t a,const uint32_t*b,uint32_t c,uint32_t d){(void)a;(void)b;(void)c;(void)d;return 0;}\nuint32_t case_policy_task_message_special(uint32_t a,const uint32_t*b,uint32_t c,uint32_t d){(void)a;(void)b;(void)c;(void)d;return 0;}\n')
subprocess.run(flags+[str(stub),'-o',str(stubobj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x00100000',str(obj),str(stubobj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
rng=random.Random(0xcd80)
for i in range(72):
 task=0x20002000;op=i%8;value=rng.getrandbits(32);option=rng.getrandbits(32);timeout=rng.randrange(100);mode=i%3;present=i%11!=0;result=rng.getrandbits(32);pair=[]
 for original in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F)
  u.mem_map(0x00100000,0x10000)
  for a,b in seg:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_write(0x20000164,struct.pack('<I',0x20002100 if present else 0));u.mem_write(0x20007fc0,struct.pack('<I',timeout))
  u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20008001);u.reg_write(UC_ARM_REG_R0,task);u.reg_write(UC_ARM_REG_R1,op);u.reg_write(UC_ARM_REG_R2,value);u.reg_write(UC_ARM_REG_R3,option)
  cuts=({0x0800ca4c:'lookup',0x0800c686:'send',0x0800c7a8:'special'} if original else {sym['case_policy_task_lookup']&~1:'lookup',sym['case_policy_task_message_send']&~1:'send',sym['case_policy_task_message_special']&~1:'special'})
  trace=[]
  def hook(uc,a,size,_):
   k=cuts.get(a)
   if k is None:return
   if k=='lookup':trace.append((k,));uc.reg_write(UC_ARM_REG_R0,mode)
   else:
    p=uc.reg_read(UC_ARM_REG_R1);args=tuple(struct.unpack('<III',uc.mem_read(p,12)))
    meta=struct.unpack('<I',uc.mem_read(uc.reg_read(UC_ARM_REG_SP),4))[0]
    trace.append((k,uc.reg_read(UC_ARM_REG_R0),args,uc.reg_read(UC_ARM_REG_R2),uc.reg_read(UC_ARM_REG_R3),meta))
    uc.reg_write(UC_ARM_REG_R0,result)
   uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((0x0800cd80 if original else sym['case_policy_task_event_send'])|1,0x20008000,count=300)
  pair.append((u.reg_read(UC_ARM_REG_R0),trace))
 assert pair[0]==pair[1],(i,pair)
print('PASS_CASE_POLICY_EVENT_DISPATCH',72)
