#!/usr/bin/env python3
"""Bounded stock/source 0x738a dual fake-standby counters."""
from pathlib import Path
import subprocess,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_policy_fake_standby_candidate.c'
stub=H/'policy_fake_standby_oracle_stubs.c'
stub.write_text('#include <stdint.h>\n__attribute__((noinline,used)) void case_policy_log(uint32_t n){(void)n;__asm__ volatile("nop");}\n__attribute__((noinline,used)) void case_policy_fake_standby_set(uint32_t n){(void)n;__asm__ volatile("nop");}\n__attribute__((noinline,used)) void case_policy_fake_standby_clear(void){__asm__ volatile("nop");}\n')
objs=[]
for s in (src,stub):
 o=H/(s.stem+'.oracle.o');objs.append(o)
 subprocess.run(['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c',str(s),'-o',str(o)],check=True)
elf=H/'policy_fake_standby_oracle.elf'
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x00100000',*[str(o) for o in objs],'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
cases=list(itertools.product((0,1),(0,1),(0,1),(0,1),(0,301,302),(0,1)))
for i,(state_l,left_ready,state_r,right_ready,counter,water) in enumerate(cases):
 pair=[]
 for native in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F)
  u.mem_map(0x00100000,0x10000)
  for a,b in seg:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000)
  u.mem_write(0x2000088c,bytes([state_l,state_r]));u.mem_write(0x200008ad,bytes([left_ready]));u.mem_write(0x200008c9,bytes([right_ready]));u.mem_write(0x200008af,bytes([water]));u.mem_write(0x200008cb,bytes([water]))
  u.mem_write(0x200008b4,counter.to_bytes(2,'little'));u.mem_write(0x200008d0,(counter+1).to_bytes(2,'little'))
  u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20001001)
  if native:
   u.reg_write(UC_ARM_REG_R4,0x2000087c);u.reg_write(UC_ARM_REG_R7,0x200000b8)
   u.mem_write(0x20007fc0,(0x200008bc).to_bytes(4,'little'));u.mem_write(0x20007fc4,(0x2000089c).to_bytes(4,'little'))
  else:
   u.reg_write(UC_ARM_REG_R0,0x2000087c);u.reg_write(UC_ARM_REG_R1,0x2000089c);u.reg_write(UC_ARM_REG_R2,0x200008bc)
  calls=[];lookup=({0x08009170:'log',0x08003a00:'set',0x080013b8:'clear'} if native else {sym['case_policy_log']&~1:'log',sym['case_policy_fake_standby_set']&~1:'set',sym['case_policy_fake_standby_clear']&~1:'clear'})
  def hook(u,a,size,ctx):
   if native and a==0x08007482:u.emu_stop();return
   if a in lookup:
    calls.append((lookup[a],u.reg_read(UC_ARM_REG_R0) if lookup[a]!='clear' else 0));u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((0x0800738a if native else sym['case_policy_fake_standby_counters_738a'])|1,0x20001000,count=10000)
  pair.append((calls,bytes(u.mem_read(0x2000087c,0x60)),u.reg_read(UC_ARM_REG_PC) if native else 0))
 a,b=pair
 assert a[:2]==b[:2],(i,cases[i],a[0],b[0],[(j,x,y) for j,(x,y) in enumerate(zip(a[1],b[1])) if x!=y])
 assert a[2]==0x08007482,(i,cases[i],a)
print('PASS_CASE_POLICY_FAKE_STANDBY',len(cases))
