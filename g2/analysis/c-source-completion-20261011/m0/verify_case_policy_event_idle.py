#!/usr/bin/env python3
"""Bounded shared-event and idle standby original/source control check."""
from pathlib import Path
import subprocess,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_policy_event_idle_candidate.c'
stubs=[('case_policy_event_peek','uint32_t x','(void)x;return 0;','uint32_t'),('case_policy_event_clear','uint32_t x,uint32_t y','(void)x;(void)y;','void'),('case_policy_event_signal','uint32_t x,uint32_t y','(void)x;(void)y;','void'),('case_policy_fake_standby_clear','void','','void'),('case_policy_elapsed','uint32_t *x','(void)x;','void'),('case_policy_log','uint32_t x','(void)x;','void'),('case_init_pmic_read','uint32_t x,uint8_t *y,uint32_t z','(void)x;(void)y;(void)z;','void'),('case_init_power_set','uint32_t x','(void)x;','void'),('case_init_boost_set','uint32_t x','(void)x;','void'),('case_init_wake_mask','uint32_t x','(void)x;','void'),('case_init_wake_config','uint32_t x','(void)x;','void'),('case_init_wake_clock','void','','void')]
stub=H/'policy_event_idle_oracle_stubs.c'
stub.write_text('#include <stdint.h>\n'+''.join('__attribute__((noinline,used)) '+ret+' '+n+'('+args+'){'+body+'__asm__ volatile("nop");}\n' for n,args,body,ret in stubs))
objs=[]
for s in (src,stub):
 o=H/(s.stem+'.oracle.o');objs.append(o)
 subprocess.run(['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c',str(s),'-o',str(o)],check=True)
elf=H/'policy_event_idle_oracle.elf'
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x00100000',*[str(o) for o in objs],'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
orig=dict(zip([0x0800a816,0x0800a7d2,0x0800aaf0,0x080013b8,0x0800a01e,0x08009170,0x080035d4,0x08002c8e,0x08002c30,0x08005094,0x080050a8,0x080050c4],[x[0] for x in stubs]))
checked=0
for active,bits,state1,state3,elapsed,silent in itertools.product((0,1),(0,2,0x1000,0x1002),(0,1),(0,1),(0,0xcb1,0xcb2),(0,1)):
 pair=[]
 for native in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F)
  u.mem_map(0x00100000,0x10000)
  for a,b in seg:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_map(0x40007000,0x1000)
  u.mem_write(0x200000bb,bytes([active]));u.mem_write(0x200000bf,bytes([silent]));u.mem_write(0x2000087d,bytes([state1]));u.mem_write(0x2000087f,bytes([state3]))
  for off,val in ((0x10,0x22334455),(0x38,0x55667788)):u.mem_write(0x200000b8+off,val.to_bytes(4,'little'))
  u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20001001)
  if native:u.reg_write(UC_ARM_REG_R4,0x2000087c);u.reg_write(UC_ARM_REG_R7,0x200000b8)
  else:u.reg_write(UC_ARM_REG_R0,0x2000087c)
  calls=[];lookup=orig if native else {sym[n]&~1:n for n,_,_,_ in stubs}
  def hook(u,a,size,ctx):
   if native and a==0x08007e90:u.emu_stop();return
   if a in lookup:
    n=lookup[a];r0=u.reg_read(UC_ARM_REG_R0);r1=u.reg_read(UC_ARM_REG_R1)
    args=[] if n in ('case_policy_fake_standby_clear','case_init_wake_clock','case_policy_elapsed') else [r0]
    if n in ('case_policy_event_clear','case_policy_event_signal'):args.append(r1)
    if n=='case_init_pmic_read':args.append(u.reg_read(UC_ARM_REG_R2))
    calls.append((n,tuple(args)))
    if n=='case_policy_event_peek':u.reg_write(UC_ARM_REG_R0,bits)
    if n=='case_policy_elapsed':u.mem_write(r0,elapsed.to_bytes(4,'little'))
    u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((0x08007b2e if native else sym['case_policy_event_idle_7b2e'])|1,0x20001000,count=10000)
  pair.append((calls,bytes(u.mem_read(0x200000b8,0x40)),bytes(u.mem_read(0x40007018,4))))
 assert pair[0]==pair[1],(active,bits,state1,state3,elapsed,silent,pair[0][0],pair[1][0])
 checked+=1
print('PASS_CASE_POLICY_EVENT_IDLE',checked)
