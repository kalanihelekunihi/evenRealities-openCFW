from pathlib import Path
import json,struct,sys,itertools,hashlib
D=Path(__file__).resolve().parent;s=D.parent/'case-deferred-event-closure-2026-10-08/verify.py';text=s.read_text().split('# Direct copy helper:')[0];ns={'__file__':str(s)};exec(text,ns)
from unicorn import UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
Q=ns['Q'];BUF=ns['BUF'];EVENT=ns['EVENT'];rows=[];K=0x20000128;CRIT=0x2000019c
for length,start,seq,bits,depth in itertools.product([1,2,10],[0,1],[(),(8,),(0x40,),(8,0x40),(8,8,0x40)],[0,0x100,0xffffff],[0,1,2]):
 if start>=length or len(seq)>length:continue
 vals=[]
 for entry in [0x0800b0fc,ns['symbols']['case_drain_negative_callbacks']]:
  mask=int(depth>0);u=ns['fixture'](length,len(seq),(start+len(seq))%length,16,-1,mask);u.mem_write(Q+12,struct.pack('<I',BUF+((start-1)%length)*16));u.mem_write(K,bytes(64));u.mem_write(K,struct.pack('<I',0x20007000));u.mem_write(K+8,struct.pack('<I',1));u.mem_write(K+20,struct.pack('<I',1));u.mem_write(0x20000164,struct.pack('<I',Q));u.mem_write(CRIT,struct.pack('<I',depth));u.mem_write(EVENT,struct.pack('<IIIIII',bits,0,EVENT+12,0xffffffff,EVENT+12,EVENT+12));calls=[];writes=[]
  for i,flags in enumerate(seq):u.mem_write(BUF+((start+i)%length)*16,struct.pack('<iIII',-2,0x0800bf8d,EVENT,flags))
  def code(u,a,n,data):
   assert a not in [0x0800cba0,0x0800c1cc,0x0800c0a0],('unexpected_task_remove_unblock_yield',hex(a))
   if a==0x0800bf8c:calls.append([u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1)])
  def write(u,access,a,n,v,data):
   if Q<=a<Q+72:
    assert u.reg_read(UC_ARM_REG_PRIMASK)==1,('unmasked_dequeue_write',hex(a));writes.append([hex(a),n,hex(v),1])
  u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,write);u.reg_write(UC_ARM_REG_IPSR,0);u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20000001);u.emu_start(entry|1,0x20000000,count=100000);assert u.reg_read(UC_ARM_REG_PC)==0x20000000
  expected=bits
  for f in seq:expected|=f
  assert struct.unpack('<I',u.mem_read(EVENT,4))[0]==expected
  assert struct.unpack('<I',u.mem_read(Q+0x38,4))[0]==0
  assert struct.unpack('<I',u.mem_read(CRIT,4))[0]==depth
  assert u.reg_read(UC_ARM_REG_PRIMASK)==mask
  assert calls==[[EVENT,f] for f in seq]
  vals.append((bytes(u.mem_read(Q,72)),bytes(u.mem_read(BUF-16,224)),bytes(u.mem_read(EVENT,24)),bytes(u.mem_read(K,64)),bytes(u.mem_read(CRIT,4)),u.reg_read(UC_ARM_REG_PRIMASK),calls,writes))
 assert vals[0]==vals[1],('consumer',length,start,seq,bits,depth)
 rows.append(dict(length=length,first_slot=start,queued_flags=list(seq),initial_bits=hex(bits),final_bits=hex(expected),initial_critical_depth=depth,final_primask=mask,callbacks=len(seq)))
(D/'results.json').write_text(json.dumps(dict(status='PASS',cases=len(rows),comparisons=rows,firmware_sha256=hashlib.sha256(ns['ns']['blob']).hexdigest(),elf_sha256=hashlib.sha256(ns['ns']['elf'].read_bytes()).hexdigest(),limits=['Original command-drain0800b0fc and reconstructed negative-command subset; real original callback0800bf8c,event-set0800c4de and scheduler suspend/resume/critical routines execute. No entry stubs.','Synthetic scheduler running/task-count/current-TCB/global state; pending-ready/ticks/yields zero, event and queue wait lists empty. Not an actual task or hardware trace.','Only nonblocking receive/negative commands. Positive timer commands, wait-bit consumption, waiters, deletion, cancellation and real scheduling excluded.','All queue writes PRIMASK1 and critical depth restored. Original critical entry/exit are nesting-based, not general PRIMASK save/restore; fixtures maintain coherent initial mask/depth.']),indent=2)+'\n');print('PASS',len(rows),'negative command drains with real event-bit application')
