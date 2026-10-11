#!/usr/bin/env python3
"""Native/source task-create wrapper ABI and storage comparison."""
from pathlib import Path
import random,subprocess,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_boot_task_create_candidate.c';obj=H/'application_boot_task_create.oracle.o';stub=H/'application_boot_task_create.oracle_stub.c';stubobj=H/'application_boot_task_create.oracle_stub.o';elf=H/'application_boot_task_create.oracle.elf'
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
subprocess.run(flags+[str(src),'-o',str(obj)],check=True)
stub.write_text('''#include <stdint.h>\nvoid case_boot_task_initialize(void(*a)(void*),const char*b,uint32_t c,void*d,uint32_t e,uint32_t*f,uint32_t g,uint32_t h){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;(void)g;(void)h;}\nvoid case_boot_task_register(uint32_t x){(void)x;}\n''')
subprocess.run(flags+[str(stub),'-o',str(stubobj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x00100000',str(obj),str(stubobj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
rng=random.Random(0xca06)
for i in range(96):
 storage=0x200015d0;end=0x2000162c;priority=i%8;result=0x20003000+i*4;pair=[];seed=bytes(rng.randrange(256) for _ in range(0x60))
 for native in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F)
  u.mem_map(0x00100000,0x10000)
  for a,b in seg:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_write(storage,seed)
  sp=0x20007fc0;u.mem_write(sp,struct.pack('<III',priority,end,storage))
  u.reg_write(UC_ARM_REG_SP,sp);u.reg_write(UC_ARM_REG_LR,0x20001001);u.reg_write(UC_ARM_REG_R0,0x0800ae5d);u.reg_write(UC_ARM_REG_R1,0x0800c2e8);u.reg_write(UC_ARM_REG_R2,0x80);u.reg_write(UC_ARM_REG_R3,0)
  mapping=({0x0800ae96:'initialize',0x0800ac08:'register'} if native else {sym['case_boot_task_initialize']&~1:'initialize',sym['case_boot_task_register']&~1:'register'})
  trace=[]
  def hook(uc,a,size,_):
   kind=mapping.get(a)
   if kind is None:return
   s=uc.reg_read(UC_ARM_REG_SP)
   if kind=='initialize':
    args=struct.unpack('<IIII',bytes(uc.mem_read(s,16)))
    trace.append((kind,uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1),uc.reg_read(UC_ARM_REG_R2),uc.reg_read(UC_ARM_REG_R3),args[0],args[2],args[3]))
    uc.mem_write(args[1],struct.pack('<I',result))
   else:trace.append((kind,uc.reg_read(UC_ARM_REG_R0)))
   uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((0x0800ca06 if native else sym['case_boot_task_create'])|1,0x20001000,count=1000)
  pair.append((u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(storage,0x60)),trace))
 assert pair[0]==pair[1],(i,pair)
print('PASS_CASE_BOOT_TASK_CREATE',96)
