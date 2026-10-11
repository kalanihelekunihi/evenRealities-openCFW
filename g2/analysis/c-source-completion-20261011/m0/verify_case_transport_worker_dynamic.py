#!/usr/bin/env python3
"""Bounded CASE 0xc9a8 stock/C dynamic worker allocation oracle."""
from pathlib import Path
import random,struct,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_boot_transport_worker_storage_candidate.c'
obj=H/'transport_worker_dynamic.oracle.o';stub=H/'transport_worker_dynamic.oracle_stub.c';stubobj=H/'transport_worker_dynamic.oracle_stub.o';elf=H/'transport_worker_dynamic.oracle.elf'
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
subprocess.run(flags+[str(src),'-o',str(obj)],check=True)
stub.write_text('#include <stdint.h>\nuint32_t case_boot_transport_heap_allocate(uint32_t n){return n;}\nvoid case_boot_heap_free(uint32_t x){(void)x;}\nvoid case_boot_task_initialize(void (*a)(void*),const char*b,uint32_t c,void*d,uint32_t e,uint32_t*f,uint32_t g,uint32_t h){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;(void)g;(void)h;}\nvoid case_boot_task_register(uint32_t x){(void)x;}\nuint32_t case_boot_task_create(void (*a)(void*),const char*b,uint32_t c,void*d,uint32_t e,uint32_t f,uint32_t g){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;(void)g;return 0;}\n')
subprocess.run(flags+[str(stub),'-o',str(stubobj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x100000',str(obj),str(stubobj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
rng=random.Random(0xc9a8)
for i in range(192):
 stack_words=rng.choice([1,24,128,256,1024]);priority=rng.randrange(1,56);first=i%7!=0;second=i%5!=0;before=rng.randbytes(92);pair=[]
 for native in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F);u.mem_map(0x00100000,0x10000)
  for a,b in seg:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_write(0x20003000,before);u.reg_write(UC_ARM_REG_R0,0x12345679);u.reg_write(UC_ARM_REG_R1,0x0800d26c);u.reg_write(UC_ARM_REG_R2,stack_words);u.reg_write(UC_ARM_REG_R3,0x20005000);u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20008001);u.mem_write(0x20007fc0,struct.pack('<II',priority,0x20004000))
  targets=({0x0800b3e8:'alloc',0x0800c030:'free',0x0800ae96:'init',0x0800ac08:'register'} if native else {sym['case_boot_transport_heap_allocate']&~1:'alloc',sym['case_boot_heap_free']&~1:'free',sym['case_boot_task_initialize']&~1:'init',sym['case_boot_task_register']&~1:'register'})
  calls=[];alloc_index=[0]
  def hook(uc,a,n,_):
   kind=targets.get(a)
   if kind is None:return
   x=uc.reg_read(UC_ARM_REG_R0);y=uc.reg_read(UC_ARM_REG_R1);z=uc.reg_read(UC_ARM_REG_R2);w=uc.reg_read(UC_ARM_REG_R3)
   if kind=='init':
    args=struct.unpack('<4I',uc.mem_read(uc.reg_read(UC_ARM_REG_SP),16));calls.append((kind,x,y,z,w,args[0],args[1],args[2],args[3]));uc.mem_write(args[1],struct.pack('<I',args[2]))
   else:calls.append((kind,x))
   if kind=='alloc':
    alloc_index[0]+=1;uc.reg_write(UC_ARM_REG_R0,(0x20002000 if first else 0) if alloc_index[0]==1 else (0x20003000 if second else 0))
   uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((0x0800c9a8 if native else sym['case_boot_transport_worker_dynamic'])|1,0x20008000,count=2000)
  pair.append((calls,u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(0x20003000,92)),bytes(u.mem_read(0x20004000,4))))
 assert pair[0]==pair[1],(i,stack_words,priority,first,second,pair)
print('PASS_CASE_TRANSPORT_WORKER_DYNAMIC',192)
