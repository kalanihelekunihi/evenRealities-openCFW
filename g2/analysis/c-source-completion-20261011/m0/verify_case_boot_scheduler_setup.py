#!/usr/bin/env python3
"""Controlled original/source scheduler initialize and ready comparisons."""
from pathlib import Path
import subprocess,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3];folder=R/'g2/components/case/startup_candidate_20261011'
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
objs=[]
for base in ('application_boot_scheduler_initialize_candidate','application_boot_scheduler_ready_candidate','application_policy_task_queue_candidate'):
 obj=H/(base+'.setup_oracle.o');subprocess.run(flags+[str(folder/(base+'.c')),'-o',str(obj)],check=True);objs.append(obj)
stub=H/'application_boot_scheduler_setup.oracle_stub.c';stubobj=H/'application_boot_scheduler_setup.oracle_stub.o';elf=H/'application_boot_scheduler_setup.oracle.elf'
stub.write_text('''#include <stdint.h>\nvoid case_policy_scheduler_lock(void){}\nuint32_t case_policy_scheduler_unlock(void){return 0;}\nuint32_t case_boot_scheduler_pool(uint32_t a,uint32_t b,uint32_t c,uint32_t d,uint32_t e){(void)a;(void)b;(void)c;(void)d;(void)e;return 0;}\nvoid case_boot_scheduler_register(uint32_t a,const char*b){(void)a;(void)b;}\nconst char case_boot_scheduler_name[]="SYSTEM";\nvoid case_boot_service_task_entry(void*x){(void)x;}\nconst char case_boot_service_task_name[]="Tm r Svc";\nuint32_t case_boot_task_create(void(*f)(void*),const char*n,uint32_t a,void*b,uint32_t c,uint32_t d,uint32_t e){(void)f;(void)n;(void)a;(void)b;(void)c;(void)d;(void)e;return 0;}\n''')
subprocess.run(flags+[str(stub),'-o',str(stubobj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x00100000',*[str(x) for x in objs],str(stubobj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
for name,naddr in [('initialize',0x0800ac84),('ready',0x0800cd20)]:
 for i in range(64):
  mem=bytearray(0x10000);initial=0 if name=='initialize' and i%3 else 0x20000500
  struct.pack_into('<I',mem,0x164,initial)
  pair=[]
  for native in (True,False):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
   u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F)
   u.mem_map(0x00100000,0x10000)
   for a,b in seg:u.mem_write(a,b)
   u.mem_map(0x20000000,0x10000);u.mem_write(0x20000000,bytes(mem))
   u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20001001)
   nativecuts={0x0800bffc:'lock',0x0800c014:'unlock',0x0800c5d0:'pool',0x0800c0b8:'register',0x0800ac84:'init',0x0800ca06:'create'}
   sourcecuts={sym['case_policy_scheduler_lock']&~1:'lock',sym['case_policy_scheduler_unlock']&~1:'unlock',sym['case_boot_scheduler_pool']&~1:'pool',sym['case_boot_scheduler_register']&~1:'register',sym['case_boot_scheduler_initialize']&~1:'init',sym['case_boot_task_create']&~1:'create'}
   cuts=nativecuts if native else sourcecuts
   trace=[]
   def hook(uc,a,size,_):
    k=cuts.get(a)
    if k is None or (k=='init' and name=='initialize'):return
    r0=uc.reg_read(UC_ARM_REG_R0);sp=uc.reg_read(UC_ARM_REG_SP)
    trace.append((k,uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1),uc.reg_read(UC_ARM_REG_R2),uc.reg_read(UC_ARM_REG_R3),struct.unpack('<I',bytes(uc.mem_read(sp,4)))[0]) if k=='pool' else (k,uc.reg_read(UC_ARM_REG_R2),uc.reg_read(UC_ARM_REG_R3),struct.unpack('<III',bytes(uc.mem_read(sp,12)))) if k=='create' else (k,r0) if k=='register' else (k,))
    if k=='pool':uc.reg_write(UC_ARM_REG_R0,0x20000500)
    if k=='create':uc.reg_write(UC_ARM_REG_R0,0x20000600)
    if k=='init':uc.mem_write(0x20000164,struct.pack('<I',0x20000500))
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   entry=naddr if native else sym['case_boot_scheduler_'+name]
   u.emu_start(entry|1,0x20001000,count=2000)
   pair.append((bytes(u.mem_read(0x20000164,0x20)),bytes(u.mem_read(0x200015a8,0x30)),u.reg_read(UC_ARM_REG_R0) if name=='ready' else None,trace))
  assert pair[0]==pair[1],(name,i,pair[0][3],pair[1][3])
 print('PASS_CASE_BOOT_SCHEDULER_'+name.upper(),64)
