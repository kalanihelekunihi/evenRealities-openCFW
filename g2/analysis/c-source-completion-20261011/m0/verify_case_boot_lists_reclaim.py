#!/usr/bin/env python3
"""Native/source initial-list, registry and task-reclaim comparisons."""
from pathlib import Path
import random,subprocess,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3];folder=R/'g2/components/case/startup_candidate_20261011'
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
objs=[]
for base in ('application_boot_scheduler_lists_candidate','application_boot_task_reclaim_candidate'):
 obj=H/(base+'.oracle.o');subprocess.run(flags+[str(folder/(base+'.c')),'-o',str(obj)],check=True);objs.append(obj)
stub=H/'application_boot_lists_reclaim.oracle_stub.c';stubobj=H/'application_boot_lists_reclaim.oracle_stub.o';elf=H/'application_boot_lists_reclaim.oracle.elf'
stub.write_text('''#include <stdint.h>\nvoid case_policy_task_list_initialize(uint32_t x){(void)x;}\nvoid case_boot_heap_free(uint32_t x){(void)x;}\n''')
subprocess.run(flags+[str(stub),'-o',str(stubobj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x00100000',*[str(x) for x in objs],str(stubobj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
rng=random.Random(0xaf70)
for kind,naddr in [('first_task_prepare',0x0800af70),('scheduler_register',0x0800c0b8),('task_reclaim',0x0800adb8)]:
 for i in range(48):
  mem=bytearray(0x10000);task=0x20000300;mem[0x300+0x59]=i%3;struct.pack_into('<I',mem,0x300+0x30,0x20002000+i*4)
  for j in range(i%9):struct.pack_into('<I',mem,0xfb4+j*8,0x8001000+j)
  pair=[]
  for native in (True,False):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
   u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F)
   u.mem_map(0x00100000,0x10000)
   for a,b in seg:u.mem_write(a,b)
   u.mem_map(0x20000000,0x10000);u.mem_write(0x20000000,bytes(mem))
   u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20001001);u.reg_write(UC_ARM_REG_R0,task if kind=='task_reclaim' else 0x20000500);u.reg_write(UC_ARM_REG_R1,0x0800acdc)
   cuts=({0x0800bf94:'list',0x0800c030:'free'} if native else {sym['case_policy_task_list_initialize']&~1:'list',sym['case_boot_heap_free']&~1:'free'})
   trace=[]
   def hook(uc,a,size,_):
    k=cuts.get(a)
    if k is None:return
    trace.append((k,uc.reg_read(UC_ARM_REG_R0)))
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   entry=naddr if native else sym['case_boot_'+kind]
   u.emu_start(entry|1,0x20001000,count=10000)
   pair.append((bytes(u.mem_read(0x20000128,0x40)),bytes(u.mem_read(0x20000fb4,0x40)),trace))
  assert pair[0]==pair[1],(kind,i,pair[0][2],pair[1][2])
 print('PASS_CASE_BOOT_'+kind.upper(),48)
