#!/usr/bin/env python3
"""Bounded stock/C first-allocation oracle for CASE heap 0xb3e8/0xae0c."""
from pathlib import Path
import subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_boot_heap_allocate_candidate.c'
obj=H/'heap_allocate.oracle.o';stub=H/'heap_allocate.oracle_stub.c';stubobj=H/'heap_allocate.oracle_stub.o';elf=H/'heap_allocate.oracle.elf'
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
subprocess.run(flags+[str(src),'-o',str(obj)],check=True)
stub.write_text('#include <stdint.h>\nvoid case_policy_task_sleep_enter(void){}\nuint32_t case_policy_task_sleep_exit(void){return 0;}\nvoid case_boot_heap_insert(uint32_t x){(void)x;}\n')
subprocess.run(flags+[str(stub),'-o',str(stubobj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x100000',str(obj),str(stubobj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
for size in (0,1,7,8,9,16,32,64,255,512,2048,3000,4000,0x80000000):
 pair=[]
 for native in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F);u.mem_map(0x00100000,0x10000)
  for a,b in seg:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.reg_write(UC_ARM_REG_R0,size);u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20008001)
  targets=({0x0800c380:'enter',0x0800cc0c:'exit',0x0800afcc:'insert'} if native else {sym['case_policy_task_sleep_enter']&~1:'enter',sym['case_policy_task_sleep_exit']&~1:'exit',sym['case_boot_heap_insert']&~1:'insert'})
  calls=[]
  def hook(uc,a,n,_):
   kind=targets.get(a)
   if kind is None:return
   calls.append((kind,uc.reg_read(UC_ARM_REG_R0)) if kind=='insert' else (kind,));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((0x0800b3e8 if native else sym['case_boot_transport_heap_allocate'])|1,0x20008000,count=10000)
  pair.append((calls,u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(0x2000017c,0x20)),bytes(u.mem_read(0x20001c88,0x30)),bytes(u.mem_read(0x20002880,8))))
 assert pair[0]==pair[1],(size,pair)
print('PASS_CASE_HEAP_ALLOCATE_INITIAL',14)
