#!/usr/bin/env python3
"""Bounded native/source scheduler-pool and heap-release comparisons."""
from pathlib import Path
import random,subprocess,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3];folder=R/'g2/components/case/startup_candidate_20261011'
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
objs=[]
for base in ('application_boot_scheduler_pool_candidate','application_boot_heap_free_candidate'):
 obj=H/(base+'.oracle.o');subprocess.run(flags+[str(folder/(base+'.c')),'-o',str(obj)],check=True);objs.append(obj)
stub=H/'application_boot_pool_heap.oracle_stub.c';stubobj=H/'application_boot_pool_heap.oracle_stub.o';elf=H/'application_boot_pool_heap.oracle.elf'
stub.write_text('''#include <stdint.h>\nvoid case_boot_pool_initialize(uint32_t a,uint32_t b,uint32_t c,uint32_t d,uint32_t e){(void)a;(void)b;(void)c;(void)d;(void)e;}\nvoid case_policy_task_sleep_enter(void){}\nuint32_t case_policy_task_sleep_exit(void){return 0;}\nvoid case_boot_heap_insert(uint32_t a){(void)a;}\n''')
subprocess.run(flags+[str(stub),'-o',str(stubobj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x00100000',*[str(x) for x in objs],str(stubobj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
rng=random.Random(0xc5d0)
for kind,naddr in [('pool',0x0800c5d0),('free',0x0800c030)]:
 for i in range(96):
  region=0x200014b8;block=0x20003000;mem=bytearray(0x10000);struct.pack_into('<I',mem,0x17c+20,0x80000000);struct.pack_into('<I',mem,0x17c+4,i*16)
  struct.pack_into('<I',mem,block&0xffff,0);struct.pack_into('<I',mem,(block+4)&0xffff,0x80000040+i)
  pair=[]
  for native in (True,False):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
   u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F)
   u.mem_map(0x00100000,0x10000)
   for a,b in seg:u.mem_write(a,b)
   u.mem_map(0x20000000,0x10000);u.mem_write(0x20000000,bytes(mem))
   sp=0x20007fc0;u.reg_write(UC_ARM_REG_SP,sp);u.reg_write(UC_ARM_REG_LR,0x20001001)
   if kind=='pool':
    u.reg_write(UC_ARM_REG_R0,10);u.reg_write(UC_ARM_REG_R1,16);u.reg_write(UC_ARM_REG_R2,0x20001508);u.reg_write(UC_ARM_REG_R3,region);u.mem_write(sp,struct.pack('<I',i&1))
   else:u.reg_write(UC_ARM_REG_R0,0 if i%4==0 else block+8)
   cuts=({0x0800ae74:'init',0x0800c380:'enter',0x0800afcc:'insert',0x0800cc0c:'exit'} if native else {sym['case_boot_pool_initialize']&~1:'init',sym['case_policy_task_sleep_enter']&~1:'enter',sym['case_boot_heap_insert']&~1:'insert',sym['case_policy_task_sleep_exit']&~1:'exit'})
   trace=[]
   def hook(uc,a,size,_):
    k=cuts.get(a)
    if k is None:return
    if k=='init':trace.append((k,uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1),uc.reg_read(UC_ARM_REG_R2),uc.reg_read(UC_ARM_REG_R3),struct.unpack('<I',bytes(uc.mem_read(uc.reg_read(UC_ARM_REG_SP),4)))[0]))
    else:trace.append((k,uc.reg_read(UC_ARM_REG_R0)) if k=='insert' else (k,))
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   u.emu_start((naddr if native else sym['case_boot_scheduler_pool' if kind=='pool' else 'case_boot_heap_free'])|1,0x20001000,count=1000)
   pair.append((u.reg_read(UC_ARM_REG_R0) if kind=='pool' else None,bytes(u.mem_read(region,0x50)) if kind=='pool' else bytes(u.mem_read(block,8))+bytes(u.mem_read(0x2000017c,0x18)),trace))
  assert pair[0]==pair[1],(kind,i,pair)
 print('PASS_CASE_BOOT_'+kind.upper(),96)
