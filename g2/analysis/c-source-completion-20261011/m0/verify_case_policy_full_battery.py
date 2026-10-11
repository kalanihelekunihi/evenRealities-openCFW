#!/usr/bin/env python3
"""Stock/source full-battery task transition to 0x7376."""
from pathlib import Path
import subprocess,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_policy_full_battery_candidate.c'
names=['case_policy_flash_write','case_policy_log','case_init_pmic_read','case_init_power_set','case_init_boost_set','case_init_wake_mask','case_init_wake_config','case_init_wake_clock']
stub=H/'policy_full_battery_oracle_stubs.c'
stub.write_text('#include <stdint.h>\n'+''.join('__attribute__((noinline,used)) void '+n+'('+args+'){'+body+'__asm__ volatile("nop");}\n' for n,args,body in [('case_policy_flash_write','uint32_t a,uint32_t b,uint32_t c','(void)a;(void)b;(void)c;'),('case_policy_log','uint32_t a','(void)a;'),('case_init_pmic_read','uint32_t a,uint8_t *b,uint32_t c','(void)a;(void)b;(void)c;'),('case_init_power_set','uint32_t a','(void)a;'),('case_init_boost_set','uint32_t a','(void)a;'),('case_init_wake_mask','uint32_t a','(void)a;'),('case_init_wake_config','uint32_t a','(void)a;'),('case_init_wake_clock','void','')]))
objs=[]
for s in (src,stub):
 o=H/(s.stem+'.oracle.o');objs.append(o)
 subprocess.run(['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c',str(s),'-o',str(o)],check=True)
elf=H/'policy_full_battery_oracle.elf'
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x00100000',*[str(o) for o in objs],'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
orig=dict(zip([0x0800598c,0x08009170,0x080035d4,0x08002c8e,0x08002c30,0x08005094,0x080050a8,0x080050c4],names))
checked=0
for eligible,r5,silent in itertools.product((0,1),(0,4,5,6,255),(0,1)):
 pair=[]
 for native in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F)
  u.mem_map(0x00100000,0x10000)
  for a,b in seg:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_map(0x40007000,0x1000)
  u.mem_write(0x2000088c,b'\x01\x01');u.mem_write(0x200008ad,b'\x01');u.mem_write(0x200008c9,bytes([eligible]));u.mem_write(0x200000bf,bytes([silent]))
  u.mem_write(0x200008b4,(0x1234).to_bytes(2,'little'));u.mem_write(0x200008d0,(0x5678).to_bytes(2,'little'))
  u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20001001)
  if native:
   u.reg_write(UC_ARM_REG_R4,0x2000087c);u.reg_write(UC_ARM_REG_R5,r5)
   u.mem_write(0x20007fc0,(0x200008bc).to_bytes(4,'little'));u.mem_write(0x20007fc4,(0x2000089c).to_bytes(4,'little'))
  else:
   u.reg_write(UC_ARM_REG_R0,0x2000087c);u.reg_write(UC_ARM_REG_R1,0x2000089c);u.reg_write(UC_ARM_REG_R2,0x200008bc);u.reg_write(UC_ARM_REG_R3,r5)
  calls=[];lookup=orig if native else {sym[n]&~1:n for n in names}
  def hook(u,a,size,ctx):
   if native and a==0x08007376:u.emu_stop();return
   if a in lookup:
    name=lookup[a];args=[] if name=='case_init_wake_clock' else [u.reg_read(UC_ARM_REG_R0)]
    if name=='case_policy_flash_write':args +=[u.reg_read(UC_ARM_REG_R1),u.reg_read(UC_ARM_REG_R2)]
    if name=='case_init_pmic_read':args +=[u.reg_read(UC_ARM_REG_R2)]
    calls.append((name,tuple(args)));u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((0x080072bc if native else sym['case_policy_full_battery_step_72bc'])|1,0x20001000,count=10000)
  pair.append((calls,bytes(u.mem_read(0x2000087c,0x60)),bytes(u.mem_read(0x40007018,4)),u.reg_read(UC_ARM_REG_R5) if native else u.reg_read(UC_ARM_REG_R0)))
 a,b=pair
 assert a==b,(eligible,r5,silent,a,b)
 checked+=1
print('PASS_CASE_POLICY_FULL_BATTERY',checked)
