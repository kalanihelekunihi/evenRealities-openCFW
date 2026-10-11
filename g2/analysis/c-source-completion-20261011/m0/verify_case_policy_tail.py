#!/usr/bin/env python3
"""Bounded stock/source 0x7e90 final idle/reset decision."""
from pathlib import Path
import subprocess,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_policy_tail_candidate.c'
stub=H/'policy_tail_oracle_stubs.c'
stub.write_text('#include <stdint.h>\n'+''.join('__attribute__((noinline,used)) void '+n+'('+args+'){'+body+'__asm__ volatile("nop");}\n' for n,args,body in [('case_policy_task_notify','uint32_t a','(void)a;'),('case_policy_flash_write','uint32_t a,uint32_t b,uint32_t c','(void)a;(void)b;(void)c;'),('case_init_wake_mask','uint32_t a','(void)a;'),('case_init_wake_config','uint32_t a','(void)a;'),('case_policy_wake_arm','uint32_t a,uint32_t b','(void)a;(void)b;'),('case_policy_system_reset','void','')]))
objs=[]
for s in (src,stub):
 o=H/(s.stem+'.oracle.o');objs.append(o)
 subprocess.run(['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c',str(s),'-o',str(o)],check=True)
elf=H/'policy_tail_oracle.elf'
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x00100000',*[str(o) for o in objs],'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
names=['case_policy_task_notify','case_policy_flash_write','case_init_wake_mask','case_init_wake_config','case_policy_wake_arm','case_policy_system_reset']
orig=dict(zip([0x0800aa24,0x0800598c,0x08005094,0x080050a8,0x080050e8,0x0800b600],names))
checked=0
for count,armed,handles in itertools.product((0,29,30,31),(0,1),(0,1)):
 pair=[]
 for native in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F)
  u.mem_map(0x00100000,0x10000)
  for a,b in seg:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_map(0x40007000,0x1000)
  u.mem_write(0x20000893,bytes([count]));u.mem_write(0x200000bb,bytes([armed]))
  for j,offset in enumerate((0x28,0x2c,0x30)):u.mem_write(0x200000b8+offset,(0x11111111*(j+1) if handles else 0).to_bytes(4,'little'))
  u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20001001)
  if native:u.reg_write(UC_ARM_REG_R4,0x2000087c);u.reg_write(UC_ARM_REG_R7,0x200000b8)
  else:u.reg_write(UC_ARM_REG_R0,0x2000087c)
  calls=[];lookup=orig if native else {sym[n]&~1:n for n in names}
  def hook(u,a,size,ctx):
   if native and a in (0x08007eda,0x08007ed6):u.emu_stop();return
   if a in lookup:
    n=lookup[a];args=[] if n=='case_policy_system_reset' else [u.reg_read(UC_ARM_REG_R0)]
    if n in ('case_policy_flash_write','case_policy_wake_arm'):args.append(u.reg_read(UC_ARM_REG_R1))
    if n=='case_policy_flash_write':args.append(u.reg_read(UC_ARM_REG_R2))
    calls.append((n,tuple(args)));u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((0x08007e90 if native else sym['case_policy_tail_7e90'])|1,0x20001000,count=10000)
  pair.append((calls,bytes(u.mem_read(0x200000b8,0x34)),bytes(u.mem_read(0x40007018,4)),u.reg_read(UC_ARM_REG_PC) if native else u.reg_read(UC_ARM_REG_R0)))
 a,b=pair
 assert a[:3]==b[:3],(count,armed,handles,a,b)
 assert b[3]==(1 if a[3]==0x08007ed6 else 0),(count,armed,handles,a,b)
 checked+=1
print('PASS_CASE_POLICY_TAIL',checked)
