#!/usr/bin/env python3
"""Original/source intrusive-list insertion and unlink over valid list states."""
from pathlib import Path
import random,subprocess,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_policy_task_queue_candidate.c';obj=H/'application_policy_task_queue.list_oracle.o';elf=H/'application_policy_task_queue.list_oracle.elf'
subprocess.run(['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x00100000',str(obj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
rng=random.Random(0xbfe2);checked=0
for method in ('case_policy_task_list_insert','case_policy_task_list_insert_sorted'):
 for i in range(96):
  memory=bytearray(0x1000);base=0x20002000;lst=base;sent=lst+8;nodes=[base+0x100,base+0x140,base+0x180]
  def put(a,v):struct.pack_into('<I',memory,a-base,v)
  put(lst,0);put(lst+4,sent);put(sent,0xffffffff);put(sent+4,sent);put(sent+8,sent)
  keys=[rng.randrange(1,100) for _ in nodes]
  if i%5==0:keys[-1]=0xffffffff
  for node,key in zip(nodes,keys):put(node,key)
  pair=[]
  for native in (True,False):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
   u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F)
   u.mem_map(0x00100000,0x10000)
   for a,b in seg:u.mem_write(a,b)
   u.mem_map(0x20000000,0x10000);u.mem_write(base,bytes(memory))
   u.reg_write(UC_ARM_REG_SP,0x20007fc0)
   def call(name,args):
    entry={'case_policy_task_list_insert':0x0800bfe2,'case_policy_task_list_insert_sorted':0x0800bfb0,'case_policy_task_unlink':0x0800bf2c}[name] if native else sym[name]
    u.reg_write(UC_ARM_REG_LR,0x20001001);u.reg_write(UC_ARM_REG_R0,args[0]);u.reg_write(UC_ARM_REG_R1,args[1] if len(args)>1 else 0)
    u.emu_start(entry|1,0x20001000,count=2000)
   for node in nodes:call(method,(lst,node))
   # Remove a middle node while preserving the other two links.
   call('case_policy_task_unlink',(nodes[1],))
   pair.append(bytes(u.mem_read(base,0x1a0)))
  assert pair[0]==pair[1],(method,i)
  checked+=1
print('PASS_CASE_POLICY_LIST_OPS',checked)
