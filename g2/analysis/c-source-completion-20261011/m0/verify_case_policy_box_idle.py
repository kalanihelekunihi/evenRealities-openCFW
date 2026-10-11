#!/usr/bin/env python3
"""Bounded original/source 0x7494 box idle path."""
from pathlib import Path
import subprocess,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_policy_box_idle_candidate.c'
stub=H/'policy_box_idle_oracle_stubs.c'
stub.write_text('#include <stdint.h>\n__attribute__((noinline,used)) void case_policy_log(uint32_t x){(void)x;__asm__ volatile("nop");}\n__attribute__((noinline,used)) void case_policy_idle_clear(void){__asm__ volatile("nop");}\n')
objs=[]
for s in (src,stub):
 o=H/(s.stem+'.oracle.o');objs.append(o)
 subprocess.run(['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c',str(s),'-o',str(o)],check=True)
elf=H/'policy_box_idle_oracle.elf'
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x00100000',*[str(o) for o in objs],'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
checked=0
for on,count,eligible,clearing,mode in itertools.product((0,1),(0,29,30,31),(0,1),(0,1),(0,1)):
 pair=[]
 for native in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F)
  u.mem_map(0x00100000,0x10000)
  for a,b in seg:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000)
  u.mem_write(0x20000880,b'\x01');u.mem_write(0x2000088c,bytes([on,on]))
  u.mem_write(0x20000893,bytes([count]));u.mem_write(0x20000896,bytes([clearing]));u.mem_write(0x200000f5,bytes([mode]))
  u.mem_write(0x200008ad,b'\x01');u.mem_write(0x200008c9,b'\x01')
  if not eligible:u.mem_write(0x200008ad,b'\x00')
  u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20001001)
  if native:
   u.reg_write(UC_ARM_REG_R4,0x2000087c);u.reg_write(UC_ARM_REG_R7,0x200000b8)
   u.mem_write(0x20007fc0,(0x200008bc).to_bytes(4,'little'));u.mem_write(0x20007fc4,(0x2000089c).to_bytes(4,'little'))
  else:
   u.reg_write(UC_ARM_REG_R0,0x2000087c);u.reg_write(UC_ARM_REG_R1,0x2000089c);u.reg_write(UC_ARM_REG_R2,0x200008bc)
  calls=[];lookup=({0x08009170:'log',0x08009a14:'clear'} if native else {sym['case_policy_log']&~1:'log',sym['case_policy_idle_clear']&~1:'clear'})
  def hook(u,a,size,ctx):
   if native and a in (0x08007376,0x080075e2,0x080077ae):u.emu_stop();return
   if a in lookup:
    calls.append((lookup[a],u.reg_read(UC_ARM_REG_R0) if lookup[a]=='log' else 0));u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((0x08007494 if native else sym['case_policy_box_idle_7494'])|1,0x20001000,count=10000)
  pair.append((calls,bytes(u.mem_read(0x2000087c,0x30)),u.reg_read(UC_ARM_REG_PC) if native else u.reg_read(UC_ARM_REG_R0)))
 a,b=pair
 assert a[:2]==b[:2],(on,count,eligible,clearing,mode,a,b)
 expected={0x08007376:0,0x080075e2:1,0x080077ae:2}[a[2]]
 assert b[2]==expected,(on,count,eligible,clearing,mode,a,b)
 checked+=1
print('PASS_CASE_POLICY_BOX_IDLE',checked)
