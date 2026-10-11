#!/usr/bin/env python3
"""Two full CASE policy turns through changed-service child cuts."""
from pathlib import Path
import itertools,subprocess,sys
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
STOCK=(ROOT/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
subprocess.run([sys.executable,str(HERE/'verify_case_policy_iteration.py')],check=True,capture_output=True)
with (HERE/'policy_iteration_oracle.elf').open('rb') as stream:
 e=ELFFile(stream);symbols={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};segments=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
cases=0
for first_l,first_r,final_l,final_r,silent in itertools.product((0,1),(0,1),(0,1),(0,1),(0,1)):
 pair=[]
 for native in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(STOCK)+4095)&~4095);u.mem_write(0x08000000,STOCK)
  u.mem_map(0x00100000,0x200000)
  for addr,data in segments:u.mem_write(addr,data)
  u.mem_map(0x20000000,0x10000);u.mem_map(0x40007000,0x1000);u.mem_map(0xe000e000,0x1000)
  u.mem_write(0x2000088c,bytes((first_l,first_r)))
  u.mem_write(0x20000891,b'\x01');u.mem_write(0x200000bf,bytes((silent,)))
  u.mem_write(0x20000884,(1).to_bytes(4,'little'));u.mem_write(0x20000888,(17).to_bytes(4,'little'))
  u.reg_write(UC_ARM_REG_SP,0x20007fe8);u.reg_write(UC_ARM_REG_LR,0x20001001)
  entry=0x08007214 if native else symbols['case_policy_task_iteration_7214']&~1
  lowers=({0x0800ce34:'service_update',0x08009170:'log',0x08006b80:'led_l',0x08006b98:'led_r',0x0800bb74:'refresh',0x080018e4:'maintenance',0x0800a7b0:'wait'} if native else
   {symbols['case_policy_service_update']&~1:'service_update',symbols['case_policy_log']&~1:'log',symbols['case_policy_led_left_clear']&~1:'led_l',symbols['case_policy_led_right_clear']&~1:'led_r',symbols['case_policy_refresh']&~1:'refresh',symbols['case_policy_service_maintenance']&~1:'maintenance',symbols['case_policy_wait']&~1:'wait'})
  entries=[];calls=[]
  def hook(uc,addr,size,opaque):
   if addr==entry:
    entries.append((uc.reg_read(UC_ARM_REG_SP),uc.reg_read(UC_ARM_REG_LR)))
    if len(entries)==3:uc.emu_stop();return
   kind=lowers.get(addr)
   if kind:
    calls.append((kind,uc.reg_read(UC_ARM_REG_R0) if kind in ('log','led_l','led_r','wait') else 0))
    if kind=='service_update':uc.mem_write(0x2000088c,bytes((final_l,final_r)))
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((0x08007200 if native else symbols['case_policy_task_7200'])|1,0,count=200000)
  assert len(entries)==3,(first_l,first_r,final_l,final_r,silent,native,entries,calls)
  pair.append((calls,bytes(u.mem_read(0x2000087c,0x68)),entries))
 assert pair[0][:2]==pair[1][:2],(first_l,first_r,final_l,final_r,silent,pair)
 assert [sp for sp,_ in pair[0][2]]==[0x20007fc0]*3
 assert [lr for _,lr in pair[0][2]]==[0x20001001,0x08007edb,0x08007edb]
 cases+=1
print('PASS_CASE_POLICY_REENTRY_CHANGED_SERVICE',cases)
