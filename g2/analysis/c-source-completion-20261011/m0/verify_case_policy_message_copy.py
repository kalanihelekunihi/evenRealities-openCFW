#!/usr/bin/env python3
"""Native/source scheduler ring copy, wrap, count and zero-width notification."""
from pathlib import Path
import random,subprocess,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_policy_message_copy_candidate.c';obj=H/'application_policy_message_copy.oracle.o';stub=H/'application_policy_message_copy.oracle_stub.c';stubobj=H/'application_policy_message_copy.oracle_stub.o';elf=H/'application_policy_message_copy.oracle.elf'
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
subprocess.run(flags+[str(src),'-o',str(obj)],check=True)
stub.write_text('#include <stdint.h>\nuint32_t case_policy_task_notify_resume(uint32_t a){(void)a;return 0;}\n')
subprocess.run(flags+[str(stub),'-o',str(stubobj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x00100000',str(obj),str(stubobj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
rng=random.Random(0xad48)
for i in range(96):
 queue=0x20002000;args=0x20002100;base=0x20002200;width=(i%5)*4;mode=i%3;count=i%4;offset=(i%4)*width;ring=bytearray(rng.randrange(256) for _ in range(48));payload=bytes(rng.randrange(256) for _ in range(24));pair=[]
 for native in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F)
  u.mem_map(0x00100000,0x10000)
  for a,b in seg:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_write(args,payload);u.mem_write(base,bytes(ring))
  qbase=0 if width==0 and i%2 else base
  for off,value in [(0,qbase),(4,base+offset),(8,base+48 if width else 0x20002300),(12,base+offset),(56,count),(64,width)]:u.mem_write(queue+off,struct.pack('<I',value))
  u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20008001);u.reg_write(UC_ARM_REG_R0,queue);u.reg_write(UC_ARM_REG_R1,args);u.reg_write(UC_ARM_REG_R2,mode)
  cut=0x0800cb38 if native else sym['case_policy_task_notify_resume']&~1;trace=[]
  def hook(uc,a,size,_):
   if a==cut:trace.append(uc.reg_read(UC_ARM_REG_R0));uc.reg_write(UC_ARM_REG_R0,7);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((0x0800ad48 if native else sym['case_policy_message_copy'])|1,0x20008000,count=500)
  pair.append((u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(queue,68)),bytes(u.mem_read(base,48)),trace))
 assert pair[0]==pair[1],(i,pair)
print('PASS_CASE_POLICY_MESSAGE_COPY',96)
