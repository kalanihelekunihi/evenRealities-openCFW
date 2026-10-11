#!/usr/bin/env python3
"""Bounded CASE 0xa93c stock/C worker descriptor selector oracle."""
from pathlib import Path
import random,struct,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_boot_transport_worker_candidate.c'
obj=H/'transport_worker.oracle.o';stub=H/'transport_worker.oracle_stub.c';stubobj=H/'transport_worker.oracle_stub.o';elf=H/'transport_worker.oracle.elf'
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
subprocess.run(flags+[str(src),'-o',str(obj)],check=True)
stub.write_text('#include <stdint.h>\nuint32_t case_boot_transport_worker_dynamic(uint32_t a,uint32_t b,uint32_t c,uint32_t d,uint32_t e,uint32_t*f){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;return 0;}\nuint32_t case_boot_transport_worker_static(uint32_t a,uint32_t b,uint32_t c,uint32_t d,uint32_t e,uint32_t f,uint32_t g){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;(void)g;return 0;}\n')
subprocess.run(flags+[str(stub),'-o',str(stubobj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x100000',str(obj),str(stubobj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
rng=random.Random(0xa93c)
for i in range(384):
 entry=0 if i%17==0 else 0x12345679;mode=i%3;storage=0 if i%13==0 else 0x20002000
 spec=[rng.choice([0,0x56781235]),rng.randrange(4),rng.choice([0,0x20003000]),rng.choice([0,44,91,92,120]),rng.choice([0,0x20004000]),rng.choice([0,4,128,512,1024]),rng.choice([0,1,24,56,57,100])];created=i%5!=0;pair=[]
 for native in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F);u.mem_map(0x00100000,0x10000)
  for a,b in seg:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_write(0x20002000,struct.pack('<7I',*spec));u.reg_write(UC_ARM_REG_R0,entry);u.reg_write(UC_ARM_REG_R1,mode);u.reg_write(UC_ARM_REG_R2,storage);u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20008001)
  targets=({0x0800c9a8:'dynamic',0x0800ca06:'static'} if native else {sym['case_boot_transport_worker_dynamic']&~1:'dynamic',sym['case_boot_transport_worker_static']&~1:'static'})
  calls=[]
  def hook(uc,a,n,_):
   kind=targets.get(a)
   if kind is None:return
   x=uc.reg_read(UC_ARM_REG_R0);y=uc.reg_read(UC_ARM_REG_R1);z=uc.reg_read(UC_ARM_REG_R2);w=uc.reg_read(UC_ARM_REG_R3);sp=uc.reg_read(UC_ARM_REG_SP)
   args=struct.unpack('<3I',uc.mem_read(sp,12))
   calls.append((kind,x,y,z,w,args[0],args[1] if kind=='static' else 'result_ptr',args[2] if kind=='static' else None))
   if kind=='dynamic':uc.mem_write(args[1],struct.pack('<I',0x20005000));uc.reg_write(UC_ARM_REG_R0,1 if created else 0)
   else:uc.reg_write(UC_ARM_REG_R0,0x20005000 if created else 0)
   uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((0x0800a93c if native else sym['case_boot_transport_worker'])|1,0x20008000,count=3000)
  pair.append((calls,u.reg_read(UC_ARM_REG_R0)))
 assert pair[0]==pair[1],(i,entry,mode,storage,spec,created,pair)
print('PASS_CASE_TRANSPORT_WORKER',384)
