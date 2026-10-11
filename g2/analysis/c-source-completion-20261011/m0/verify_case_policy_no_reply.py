#!/usr/bin/env python3
"""Bounded native/source no-reply counter, log and reset transitions."""
from pathlib import Path
import subprocess,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_policy_no_reply_candidate.c'
stub=H/'policy_no_reply_oracle_stubs.c'
stub.write_text('#include <stdint.h>\n__attribute__((noinline,used)) void case_policy_log(uint32_t x){(void)x;__asm__ volatile("nop");}\n__attribute__((noinline,used)) void case_policy_log_number(uint32_t x,uint32_t y){(void)x;(void)y;__asm__ volatile("nop");}\n__attribute__((noinline,used)) void case_policy_refresh(void){__asm__ volatile("nop");}\n__attribute__((noinline,used)) void case_policy_no_reply_reset(uint32_t x,uint32_t y){(void)x;(void)y;__asm__ volatile("nop");}\n')
objs=[]
for s in (src,stub):
 o=H/(s.stem+'.oracle.o');objs.append(o)
 subprocess.run(['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c',str(s),'-o',str(o)],check=True)
elf=H/'policy_no_reply_oracle.elf'
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x00100000',*[str(o) for o in objs],'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
NUMBER={0x08007ce8,0x08007d0c,0x08007d30,0x08007d5c,0x08007d88,0x08007db4}
cases=list(itertools.product((0,7,8),(0,14,15,178,179,209),(0,7,8),(0,14,15,178,179,209),(0,1),(0,1)))
for i,(lc,ls,rc,rs,silent,reset_mode) in enumerate(cases):
 pair=[]
 for native in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F)
  u.mem_map(0x00100000,0x10000)
  for a,b in seg:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000)
  for offset,value in ((0x40,lc),(0x44,ls),(0x5c,rc),(0x60,rs)):u.mem_write(0x2000087c+offset,value.to_bytes(4,'little'))
  u.mem_write(0x200000bf,bytes([silent,reset_mode]))
  u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20001001)
  if native:u.reg_write(UC_ARM_REG_R4,0x2000087c)
  else:u.reg_write(UC_ARM_REG_R0,0x2000087c)
  calls=[];lookup=({0x08009170:'log',0x0800bb74:'refresh',0x08009a9c:'reset'} if native else {sym['case_policy_log']&~1:'log',sym['case_policy_log_number']&~1:'log',sym['case_policy_refresh']&~1:'refresh',sym['case_policy_no_reply_reset']&~1:'reset'})
  def hook(u,a,size,ctx):
   if native and a==0x08007abc:u.emu_stop();return
   if a in lookup:
    kind=lookup[a];r0=u.reg_read(UC_ARM_REG_R0);r1=u.reg_read(UC_ARM_REG_R1)
    calls.append((kind,r0,r1) if kind=='reset' or (kind=='log' and r0 in NUMBER) else (kind,r0 if kind=='log' else 0))
    u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((0x080079b0 if native else sym['case_policy_no_reply_79b0'])|1,0x20001000,count=10000)
  pair.append((calls,bytes(u.mem_read(0x2000087c,0x64))))
 assert pair[0]==pair[1],(i,cases[i],pair[0][0],pair[1][0],[(j,x,y) for j,(x,y) in enumerate(zip(pair[0][1],pair[1][1])) if x!=y])
print('PASS_CASE_POLICY_NO_REPLY',len(cases))
