#!/usr/bin/env python3
"""Bounded CASE 0xaa48 stock/C callback registration selector oracle."""
from pathlib import Path
import random,struct,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_boot_transport_register_candidate.c'
obj=H/'transport_register.oracle.o';stub=H/'transport_register.oracle_stub.c';stubobj=H/'transport_register.oracle_stub.o';elf=H/'transport_register.oracle.elf'
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
subprocess.run(flags+[str(src),'-o',str(obj)],check=True)
stub.write_text('#include <stdint.h>\nvoid case_boot_transport_entry_8558(uint32_t x){(void)x;}\nuint32_t case_boot_transport_heap_allocate(uint32_t n){return n;}\nvoid case_boot_heap_free(uint32_t x){(void)x;}\nuint32_t case_boot_transport_register_dynamic(uint32_t a,uint32_t b,uint32_t c,uint32_t d,uint32_t e){(void)a;(void)b;(void)c;(void)d;(void)e;return 0;}\nuint32_t case_boot_transport_register_static(uint32_t a,uint32_t b,uint32_t c,uint32_t d,uint32_t e,uint32_t f){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;return 0;}\n')
subprocess.run(flags+[str(stub),'-o',str(stubobj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x100000',str(obj),str(stubobj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
rng=random.Random(0xaa48)
for i in range(384):
 mode=i%3;flags=i%4;storage=0 if i%11==0 else 0x20002000;allocation=i%7!=0;created=i%5!=0
 callback=0 if i%13==0 else 0x12345679;entry=rng.choice([0,0x56781235]);buffer=rng.choice([0,0x20004000]);size=rng.choice([0,1,43,44,80])
 pair=[]
 for native in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F);u.mem_map(0x00100000,0x10000)
  for a,b in seg:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_write(0x20002000,struct.pack('<IIII',entry,0,buffer,size));u.reg_write(UC_ARM_REG_R0,callback);u.reg_write(UC_ARM_REG_R1,mode);u.reg_write(UC_ARM_REG_R2,flags);u.reg_write(UC_ARM_REG_R3,storage);u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20008001)
  targets=({0x0800b3e8:'alloc',0x0800ccc0:'dynamic',0x0800ccf2:'static',0x0800c030:'free'} if native else {sym['case_boot_transport_heap_allocate']&~1:'alloc',sym['case_boot_transport_register_dynamic']&~1:'dynamic',sym['case_boot_transport_register_static']&~1:'static',sym['case_boot_heap_free']&~1:'free'})
  calls=[]
  def hook(uc,a,n,_):
   kind=targets.get(a)
   if kind is None:return
   x=uc.reg_read(UC_ARM_REG_R0);y=uc.reg_read(UC_ARM_REG_R1);z=uc.reg_read(UC_ARM_REG_R2);w=uc.reg_read(UC_ARM_REG_R3)
   if kind in ('dynamic','static'):
    sp=uc.reg_read(UC_ARM_REG_SP);arg4=struct.unpack('<I',uc.mem_read(sp,4))[0];arg5=struct.unpack('<I',uc.mem_read(sp+4,4))[0]
    calls.append((kind,x,y,z,w,'trampoline' if arg4==(0x08008559 if native else sym['case_boot_transport_entry_8558']) else hex(arg4),arg5 if kind=='static' else None))
   elif kind=='alloc':calls.append((kind,x))
   else:calls.append((kind,x))
   uc.reg_write(UC_ARM_REG_R0,(0x20003000 if allocation else 0) if kind=='alloc' else (0x20005000 if created else 0) if kind in ('dynamic','static') else 0)
   uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((0x0800aa48 if native else sym['case_boot_transport_register'])|1,0x20008000,count=3000)
  pair.append((calls,u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(0x20003000,8))))
 assert pair[0]==pair[1],(i,mode,flags,storage,allocation,created,callback,entry,buffer,size,pair)
print('PASS_CASE_TRANSPORT_REGISTER',384)
