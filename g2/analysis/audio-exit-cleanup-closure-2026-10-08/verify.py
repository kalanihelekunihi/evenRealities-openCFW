from pathlib import Path
import json,struct,itertools,hashlib,sys
D=Path(__file__).resolve().parent;s=D.parent/'audio-thread-flags-closure-2026-10-08/verify.py';text=s.read_text().split('for id,flags,old,state,ipsr,mask,basepri,running')[0];ns={'__file__':str(s)};exec(text,ns)
from unicorn import *
from unicorn.arm_const import *
rows=[];peers={0x4494d8:'timer_stop',0x44953e:'timer_delete',0x449bec:'queue_delete'}
for timer,queue,context in itertools.product([0,0x20006800],[0,0x20006a00],[(0,0,0),(15,0,0),(15,1,0),(15,0,0x30),(15,1,0x30)]):
 vals=[];ipsr,mask,base=context
 for entry in [0x53cdc2,ns['symbols']['audio_exit_logger_disabled']]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4);u.mem_map(0x438000,(len(ns['raw'])+4095)&~4095);u.mem_write(0x438000,ns['raw']);u.mem_map(0x20000000,0x80000);u.mem_map(0x100000,0x10000);u.mem_map(0xe000e000,0x2000)
  for a,b in ns['segments']:u.mem_write(a,b)
  u.mem_write(0x20074a98,struct.pack('<I',timer));u.mem_write(0x20003fa4,struct.pack('<I',queue));u.mem_write(0x200040f4,bytes(4));u.mem_write(0x20004543,b'\0');u.mem_write(0x20074a3c,struct.pack('<I',1));u.mem_write(0x20074a58,bytes(4));calls=[];returns=[];pending={};boundary=[]
  def code(u,a,n,d):
   if a in pending:returns.append([pending.pop(a),hex(u.reg_read(UC_ARM_REG_R0))])
   if a==0x4c9c3c:calls.append(['request',u.reg_read(UC_ARM_REG_R0)])
   if a in peers:
    calls.append([peers[a],hex(u.reg_read(UC_ARM_REG_R0))])
    if ipsr==0:boundary.extend([peers[a],hex(u.reg_read(UC_ARM_REG_R0))]);u.emu_stop();return
    pending[u.reg_read(UC_ARM_REG_LR)&~1]=peers[a]
   if a==0x449376:boundary.extend(['delay_before_entry',hex(u.reg_read(UC_ARM_REG_R0))]);u.emu_stop()
   assert a not in [0x43d574,0x43ce9e],'logger_not_disabled'
  u.hook_add(UC_HOOK_CODE,code);u.reg_write(UC_ARM_REG_IPSR,ipsr);u.reg_write(UC_ARM_REG_PRIMASK,mask);u.reg_write(UC_ARM_REG_BASEPRI,base);u.reg_write(UC_ARM_REG_SP,0x2007e000);u.reg_write(UC_ARM_REG_LR,0x20000001);u.emu_start(entry|1,0x20000000,count=30000);assert boundary
  if ipsr:
   assert u.mem_read(0x20074a98,4)==bytes(4) and u.mem_read(0x20003fa4,4)==bytes(4)
   assert all(v=='0xfffffffa' for _,v in returns),returns
  else:assert u.mem_read(0x20074a98,4)==struct.pack('<I',timer) and u.mem_read(0x20003fa4,4)==struct.pack('<I',queue)
  assert u.reg_read(UC_ARM_REG_PRIMASK)==mask;assert u.reg_read(UC_ARM_REG_BASEPRI)==base
  vals.append((bytes(u.mem_read(0x20074a98,4)),bytes(u.mem_read(0x20003fa4,4)),calls,returns,boundary))
 assert vals[0]==vals[1];rows.append(dict(timer=hex(timer),queue=hex(queue),ipsr=ipsr,primask=mask,basepri=base,calls=vals[0][2],peer_returns=vals[0][3],boundary=vals[0][4]))
(D/'results.json').write_text(json.dumps(dict(status='PASS',cases=len(rows),comparisons=rows,firmware_sha256=hashlib.sha256(ns['blob']).hexdigest(),elf_sha256=hashlib.sha256(ns['elf'].read_bytes()).hexdigest(),limits=['Selected actual/native logger-disabled exit; first request uses NULL event-group fixture and actual event-flags rejection. Not a successful producer-stop request.','Task-context timer/queue live objects stop before OS peer; ISR wrapper error returns execute actually and handles are cleared. ISR invocation is synthetic, not observed/known-reachable audio thread behavior.','Delay never executes; no object free, producer quiescence or daemon drain proved.']),indent=2)+'\n');print('PASS',len(rows),'exit prefix/rejection paths')
