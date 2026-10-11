#!/usr/bin/env python3
"""Bounded deferred-task cleanup original/source comparison."""
from pathlib import Path
import subprocess,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_boot_idle_maintenance_candidate.c';obj=H/'application_boot_idle_maintenance.oracle.o';stub=H/'application_boot_idle_maintenance.oracle_stub.c';stubobj=H/'application_boot_idle_maintenance.oracle_stub.o';elf=H/'application_boot_idle_maintenance.oracle.elf'
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
subprocess.run(flags+[str(src),'-o',str(obj)],check=True)
stub.write_text('''#include <stdint.h>\nvoid case_policy_scheduler_lock(void){}\nuint32_t case_policy_scheduler_unlock(void){return 0;}\nvoid case_policy_task_unlink(uint32_t x){(void)x;}\nvoid case_boot_task_reclaim(uint32_t x){(void)x;}\n''')
subprocess.run(flags+[str(stub),'-o',str(stubobj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x00100000',str(obj),str(stubobj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
for i in range(80):
 mem=bytearray(0x10000);task=0x20000300;struct.pack_into('<I',mem,0x128+4,i%4);struct.pack_into('<I',mem,0x128+8,10+i);struct.pack_into('<I',mem,0x1490+12,0x20002000);struct.pack_into('<I',mem,0x2000+12,task)
 pair=[]
 for native in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F)
  u.mem_map(0x00100000,0x10000)
  for a,b in seg:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_write(0x20000000,bytes(mem))
  u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20001001)
  cuts=({0x0800bffc:'lock',0x0800c014:'unlock',0x0800bf2c:'unlink',0x0800adb8:'reclaim'} if native else {sym['case_policy_scheduler_lock']&~1:'lock',sym['case_policy_scheduler_unlock']&~1:'unlock',sym['case_policy_task_unlink']&~1:'unlink',sym['case_boot_task_reclaim']&~1:'reclaim'})
  trace=[]
  def hook(uc,a,size,_):
   k=cuts.get(a)
   if k is None:return
   trace.append((k,uc.reg_read(UC_ARM_REG_R0)) if k in ('unlink','reclaim') else (k,))
   uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((0x0800ace4 if native else sym['case_boot_idle_maintenance'])|1,0x20001000,count=2000)
  pair.append((bytes(u.mem_read(0x20000128,0x10)),trace))
 assert pair[0]==pair[1],(i,pair)
print('PASS_CASE_POLICY_IDLE_MAINTENANCE',80)
