#!/usr/bin/env python3
"""One composed 0x7214 policy iteration, idle/service native comparison."""
from pathlib import Path
import subprocess,itertools,re
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
combined=H/'policy_iteration_sources.o'
sources=sorted((R/'g2/components/case/startup_candidate_20261011').glob('application_policy_*.c'))
objects=[]
for source in sources:
 obj=H/(source.stem+'.iteration.o');objects.append(str(obj))
 subprocess.run(['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-c',str(source),'-o',str(obj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-r',*objects,'-o',str(combined)],check=True)
nm=subprocess.check_output(['/opt/homebrew/bin/arm-none-eabi-nm','-u',str(combined)],text=True)
undefined=[line.split()[-1] for line in nm.splitlines() if line.strip()]
stub=H/'policy_iteration_oracle_stubs.S'
assembly=['.syntax unified','.thumb','.text']
for n in undefined:
 if n in ('case_crt_initial_data','case_policy_ota_probe_template'):continue
 assembly.extend(['.global '+n,'.thumb_func',n+':','bx lr'])
assembly.extend(['.section .rodata',' .global case_crt_initial_data','case_crt_initial_data:','.space 104',' .global case_policy_ota_probe_template','case_policy_ota_probe_template:','.space 12'])
stub.write_text('\n'.join(assembly)+'\n')
stubobj=H/'policy_iteration_oracle_stubs.o'
subprocess.run(['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-c',str(stub),'-o',str(stubobj)],check=True)
elf=H/'policy_iteration_oracle.elf'
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x00100000',str(combined),str(stubobj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
checked=0
for seconds,idle,mode,active,state3,state4 in itertools.product((0,1,4,5),(0,1,9,11),(0,1),(0,),(0,1),(0,1)):
 pair=[]
 for native in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F)
  u.mem_map(0x00100000,0x200000)
  for a,b in seg:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_map(0x40007000,0x1000);u.mem_map(0xe000e000,0x1000)
  u.mem_write(0x20000884,seconds.to_bytes(4,'little'));u.mem_write(0x20000888,(17).to_bytes(4,'little'))
  u.mem_write(0x20000891,bytes([active]));u.mem_write(0x200000f5,bytes([mode]))
  u.mem_write(0x2000087f,bytes([state3]));u.mem_write(0x20000880,bytes([state4]))
  u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20001001)
  if native:
   u.reg_write(UC_ARM_REG_R4,0x2000087c);u.reg_write(UC_ARM_REG_R5,0);u.reg_write(UC_ARM_REG_R6,idle)
   u.mem_write(0x20007fc0,(0x200008bc).to_bytes(4,'little'));u.mem_write(0x20007fc4,(0x2000089c).to_bytes(4,'little'))
  else:
   u.mem_write(0x20007000,(0x2000087c).to_bytes(4,'little')+idle.to_bytes(4,'little')+bytes([0,0,0,0]));u.reg_write(UC_ARM_REG_R0,0x20007000)
  calls=[];lookup=({0x0800d154:'service_idle',0x0800a7b0:'wait'} if native else {sym['case_policy_service_idle']&~1:'service_idle',sym['case_policy_wait']&~1:'wait'})
  def hook(u,a,size,ctx):
   if native and a==0x08007ed6:u.emu_stop();return
   if a in lookup:
    n=lookup[a];calls.append((n,u.reg_read(UC_ARM_REG_R0) if n=='wait' else 0));u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  try:u.emu_start((0x08007214 if native else sym['case_policy_task_iteration_7214'])|1,0x20001000,count=100000)
  except Exception as exc:raise AssertionError((seconds,idle,mode,active,state3,state4,native,hex(u.reg_read(UC_ARM_REG_PC)),calls)) from exc
  r5=u.reg_read(UC_ARM_REG_R5) if native else u.mem_read(0x20007008,1)[0]
  r6=u.reg_read(UC_ARM_REG_R6) if native else int.from_bytes(u.mem_read(0x20007004,4),'little')
  pair.append((calls,bytes(u.mem_read(0x2000087c,0x64)),r5,r6))
 assert pair[0]==pair[1],(seconds,idle,mode,active,state3,state4,pair[0][0],pair[1][0],[(j,x,y) for j,(x,y) in enumerate(zip(pair[0][1],pair[1][1])) if x!=y],pair[0][2:],pair[1][2:])
 checked+=1
print('PASS_CASE_POLICY_ITERATION_IDLE_SERVICE',checked)
entry_checked=0
for seconds,state3,state4 in itertools.product((0,4),(0,1),(0,1)):
 pair=[]
 for native in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F)
  u.mem_map(0x00100000,0x200000)
  for a,b in seg:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_map(0x40007000,0x1000);u.mem_map(0xe000e000,0x1000)
  u.mem_write(0x20000884,seconds.to_bytes(4,'little'));u.mem_write(0x2000087f,bytes([state3]));u.mem_write(0x20000880,bytes([state4]))
  u.reg_write(UC_ARM_REG_SP,0x20007fe8);u.reg_write(UC_ARM_REG_LR,0x20001001)
  calls=[];lookup=({0x0800d154:'service_idle',0x0800a7b0:'wait'} if native else {sym['case_policy_service_idle']&~1:'service_idle',sym['case_policy_wait']&~1:'wait'})
  entries=0
  def hook(u,a,size,ctx):
   nonlocal_entries[0] += 1 if not native and a==(sym['case_policy_task_iteration_7214']&~1) else 0
   if native and a==0x08007ed6:u.emu_stop();return
   if not native and nonlocal_entries[0]==2 and a==(sym['case_policy_task_iteration_7214']&~1):u.emu_stop();return
   if a in lookup:
    n=lookup[a];calls.append((n,u.reg_read(UC_ARM_REG_R0) if n=='wait' else 0));u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  nonlocal_entries=[0]
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((0x08007200 if native else sym['case_policy_task_7200'])|1,0x20001000,count=100000)
  pair.append((calls,bytes(u.mem_read(0x2000087c,0x64))))
 assert pair[0]==pair[1],(seconds,state3,state4,pair[0][0],pair[1][0])
 entry_checked+=1
print('PASS_CASE_POLICY_ENTRY_FIRST_TURN',entry_checked)
changed_checked=0
for initial_l,initial_r,final_l,final_r,silent in itertools.product((0,1),(0,1),(0,1),(0,1),(0,1)):
 pair=[]
 for native in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F)
  u.mem_map(0x00100000,0x200000)
  for a,b in seg:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_map(0x40007000,0x1000);u.mem_map(0xe000e000,0x1000)
  u.mem_write(0x2000088c,bytes([initial_l,initial_r]));u.mem_write(0x20000891,b'\x01');u.mem_write(0x200000bf,bytes([silent]))
  u.mem_write(0x20000884,(1).to_bytes(4,'little'));u.mem_write(0x20000888,(17).to_bytes(4,'little'))
  u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20001001)
  if native:
   u.reg_write(UC_ARM_REG_R4,0x2000087c);u.reg_write(UC_ARM_REG_R5,0);u.reg_write(UC_ARM_REG_R6,0)
   u.mem_write(0x20007fc0,(0x200008bc).to_bytes(4,'little'));u.mem_write(0x20007fc4,(0x2000089c).to_bytes(4,'little'))
  else:
   u.mem_write(0x20007000,(0x2000087c).to_bytes(4,'little')+bytes(8));u.reg_write(UC_ARM_REG_R0,0x20007000)
  calls=[]
  lookup=({0x0800ce34:'service_update',0x08009170:'log',0x08006b80:'led_l',0x08006b98:'led_r',0x0800bb74:'refresh',0x080018e4:'maintenance',0x0800a7b0:'wait'} if native else {sym['case_policy_service_update']&~1:'service_update',sym['case_policy_log']&~1:'log',sym['case_policy_led_left_clear']&~1:'led_l',sym['case_policy_led_right_clear']&~1:'led_r',sym['case_policy_refresh']&~1:'refresh',sym['case_policy_service_maintenance']&~1:'maintenance',sym['case_policy_wait']&~1:'wait'})
  def hook(u,a,size,ctx):
   if native and a==0x08007ed6:u.emu_stop();return
   if a in lookup:
    n=lookup[a];calls.append((n,u.reg_read(UC_ARM_REG_R0) if n in ('log','led_l','led_r','wait') else 0))
    if n=='service_update':u.mem_write(0x2000088c,bytes([final_l,final_r]))
    u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  try:u.emu_start((0x08007214 if native else sym['case_policy_task_iteration_7214'])|1,0x20001000,count=100000)
  except Exception as exc:raise AssertionError((initial_l,initial_r,final_l,final_r,silent,native,hex(u.reg_read(UC_ARM_REG_PC)),calls)) from exc
  r5=u.reg_read(UC_ARM_REG_R5) if native else u.mem_read(0x20007008,1)[0]
  r6=u.reg_read(UC_ARM_REG_R6) if native else int.from_bytes(u.mem_read(0x20007004,4),'little')
  pair.append((calls,bytes(u.mem_read(0x2000087c,0x68)),r5,r6))
 assert pair[0]==pair[1],(initial_l,initial_r,final_l,final_r,silent,pair[0][0],pair[1][0],[(j,x,y) for j,(x,y) in enumerate(zip(pair[0][1],pair[1][1])) if x!=y],pair[0][2:],pair[1][2:])
 changed_checked+=1
print('PASS_CASE_POLICY_ITERATION_CHANGED_SERVICE',changed_checked)
