#!/usr/bin/env python3
"""Controlled pool initialization and free-list coalescing comparisons."""
from pathlib import Path
import random,subprocess,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3];folder=R/'g2/components/case/startup_candidate_20261011'
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
objs=[]
for base in ('application_boot_pool_initialize_candidate','application_boot_heap_insert_candidate'):
 obj=H/(base+'.oracle.o');subprocess.run(flags+[str(folder/(base+'.c')),'-o',str(obj)],check=True);objs.append(obj)
stub=H/'application_boot_pool_insert.oracle_stub.c';stubobj=H/'application_boot_pool_insert.oracle_stub.o';elf=H/'application_boot_pool_insert.oracle.elf'
stub.write_text('''#include <stdint.h>\nvoid case_boot_pool_prepare(uint32_t a,uint32_t b){(void)a;(void)b;}\n''')
subprocess.run(flags+[str(stub),'-o',str(stubobj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x00100000',*[str(x) for x in objs],str(stubobj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
rng=random.Random(0xafcc)
for kind,naddr in [('pool_initialize',0x0800ae74),('heap_insert',0x0800afcc)]:
 for i in range(96):
  mem=bytearray(0x10000);region=0x200014b8;block=0x20003500;prior=0x20003400;next=0x20004000;sent=0x20000194
  def put(a,v):struct.pack_into('<I',mem,a&0xffff,v)
  if kind=='heap_insert':
   put(0x17c,0x20003000);put(sent,prior if i%3 else next);put(sent+4,0)
   put(prior,next);put(prior+4,0x100 if i%3 else 0x80)
   put(block,0);put(block+4,0xb00 if i%2 else 0x100)
   put(next,0x20003000);put(next+4,0x100)
  pair=[]
  for native in (True,False):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
   u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F)
   u.mem_map(0x00100000,0x10000)
   for a,b in seg:u.mem_write(a,b)
   u.mem_map(0x20000000,0x10000);u.mem_write(0x20000000,bytes(mem))
   sp=0x20007fc0;u.reg_write(UC_ARM_REG_SP,sp);u.reg_write(UC_ARM_REG_LR,0x20001001)
   if kind=='pool_initialize':
    u.reg_write(UC_ARM_REG_R0,10);u.reg_write(UC_ARM_REG_R1,16);u.reg_write(UC_ARM_REG_R2,0 if i&1 else 0x20001508);u.reg_write(UC_ARM_REG_R3,i%4);u.mem_write(sp,struct.pack('<I',region))
   else:u.reg_write(UC_ARM_REG_R0,block)
   child=0x0800c616 if native else sym['case_boot_pool_prepare']&~1;trace=[]
   def hook(uc,a,size,_):
    if a!=child:return
    trace.append((uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1)))
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   u.emu_start((naddr if native else sym['case_boot_'+kind])|1,0x20001000,count=1000)
   pair.append((bytes(u.mem_read(region,0x50)) if kind=='pool_initialize' else bytes(u.mem_read(sent,8))+bytes(u.mem_read(prior,8))+bytes(u.mem_read(block,8))+bytes(u.mem_read(next,8)),trace))
  assert pair[0]==pair[1],(kind,i,pair)
 print('PASS_CASE_BOOT_'+kind.upper(),96)
