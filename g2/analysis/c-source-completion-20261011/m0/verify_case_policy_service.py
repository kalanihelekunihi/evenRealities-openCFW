#!/usr/bin/env python3
"""Bounded original/source service gate calls and RAM at 0x77b0."""
from pathlib import Path
import subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_policy_service_candidate.c'
stub=H/'policy_service_oracle_stubs.c'
stub.write_text('#include <stdint.h>\n__attribute__((noinline,used)) void case_policy_wait(uint32_t n){(void)n;__asm__ volatile("nop");}\n__attribute__((noinline,used)) void case_policy_service_idle(void){__asm__ volatile("nop");}\n__attribute__((noinline,used)) void case_policy_service_update(void){__asm__ volatile("nop");}\n')
objects=[]
for s in (src,stub):
 o=H/(s.stem+'.oracle.o');objects.append(o)
 subprocess.run(['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c',str(s),'-o',str(o)],check=True)
elf=H/'policy_service_oracle.elf'
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x00100000',*[str(o) for o in objects],'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
for service in (0,1):
 for left,right in ((0,0),(1,0),(0,1),(1,1)):
  pairs=[]
  for native in (True,False):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
   u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F)
   u.mem_map(0x00100000,0x10000)
   for a,b in seg:u.mem_write(a,b)
   u.mem_map(0x20000000,0x10000)
   u.mem_write(0x2000088c,bytes([left,right]))
   u.mem_write(0x20000891,bytes([service]))
   u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20001001)
   if native:
    u.reg_write(UC_ARM_REG_R4,0x2000087c);u.mem_write(0x20007fcc,left.to_bytes(4,'little'));u.mem_write(0x20007fd4,right.to_bytes(4,'little'));u.reg_write(UC_ARM_REG_R7,0x200000b8)
   else:
    u.reg_write(UC_ARM_REG_R0,0x2000087c);u.reg_write(UC_ARM_REG_R1,0x20007f80);u.reg_write(UC_ARM_REG_R2,0x20007f81)
   calls=[]
   lookup=({0x0800a7b0:'wait',0x0800d154:'idle',0x0800ce34:'update'} if native else {sym['case_policy_wait']&~1:'wait',sym['case_policy_service_idle']&~1:'idle',sym['case_policy_service_update']&~1:'update'})
   def hook(u,a,size,ctx):
    if native and a in (0x08007eda,0x080077e8):u.emu_stop();return
    if a in lookup:
     calls.append(lookup[a]);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   u.emu_start((0x080077b0 if native else sym['case_policy_service_gate_77b0'])|1,0x20001000,count=10000)
   if native: pairs.append((calls,bytes(u.mem_read(0x2000087c,0x20)),bytes(u.mem_read(0x200000b8,8)),u.reg_read(UC_ARM_REG_PC)))
   else: pairs.append((calls,bytes(u.mem_read(0x2000087c,0x20)),bytes(u.mem_read(0x200000b8,8)),u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(0x20007f80,2))))
  a,b=pairs
  assert a[:3]==b[:3],(service,left,right,a,b)
  assert b[3]==service,(service,left,right,b)
  if service:assert b[4]==bytes([left,right]),(service,left,right,b)
  assert a[3]==(0x080077e8 if service else 0x08007eda),(service,left,right,a)
print('PASS_CASE_POLICY_SERVICE_GATE',8)
