#!/usr/bin/env python3
"""Original Thumb queue/lifetime tests, explicit provider stubs, no hardware."""
from pathlib import Path
import json,struct,hashlib,capstone,unicorn
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
B=(ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes();BASE=0x437fe0
SHA='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
assert len(B)==3523396 and hashlib.sha256(B).hexdigest()==SHA
raw={int(r['entry'],16):r for r in map(json.loads,(ROOT/'g2/research/corpus/apollo-main/ghidra/open-2026-09-29/functions-000.jsonl').read_text().splitlines())}
entries=[0x476ace,0x4c4910,0x4c4b7e,0x4c46c0,0x4a19c0,0x4bf99e,0x4bf9b0,0x4bf9ba,0x4bf9de,0x4bf9ec,0x538c24,0x538c4a,0x52b95e,0x52b97c,0x52b9d0,0x4c4da4,0x4c4dd0,0x4d0af6,0x4d0b1c,0x4490e2]
md=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_THUMB|capstone.CS_MODE_MCLASS)
records=[];lines=[]
for a in entries:
 r=raw[a];z=int(r['body_end_inclusive'],16)+1;data=B[a-BASE:z-BASE];assert hashlib.sha256(data).hexdigest()==r['body_sha256']
 ins=list(md.disasm(data,a));assert sum(i.size for i in ins)==len(data)
 records.append({'entry':hex(a),'end':hex(z),'sha256':r['body_sha256'],'raw_decompiled':r['decompiled']})
 lines.append('\n%s %s sha256=%s'%(hex(a),hex(z),r['body_sha256']))
 lines.extend('%08x %-10s %-8s %s'%(i.address,i.bytes.hex(),i.mnemonic,i.op_str) for i in ins)
(OUT/'disassembly.txt').write_text('\n'.join(lines)+'\n')
def f32(a):return struct.unpack_from('<I',B,a-BASE)[0]
OS=f32(0x52bac4);Q=f32(0x52bac8);CTX=0x20074074;HANDLES=0x20077000;DATA=0x20077200;STOP=0x10000000
R=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]
STUB={0x43d0ce:'log',0x43d574:'log',0x43ce9e:'log',0x530446:'buf_alloc',0x5304d4:'buf_free',0x52b8a4:'cs_enter',0x52b8b6:'cs_exit',0x52b8d8:'wake',0x52a574:'timer_update',0x52b99e:'ready_sleep',0x52a542:'timer_expired',0x4a06d4:'master',0x4b73c4:'role',0x539dea:'att_copy_boundary',0x4497b6:'mutex_acquire',0x44981c:'mutex_release',0x4490cc:'tick',0x4494d8:'timer_stop',0x4767a8:'reschedule_delays',0x47697e:'delay_cccd',0x4c543e:'ring_event',0x4d0c36:'tx_complete',0x4d0b64:'tx_wait',0x44900e:'irq',0x454820:'create_static',0x4491fe:'terminate',0x4abcbc:'callback_manager_deinit'}
class M:
 def __init__(self):
  self.u=unicorn.Uc(unicorn.UC_ARCH_ARM,unicorn.UC_MODE_THUMB|unicorn.UC_MODE_MCLASS)
  self.u.mem_map(0x437000,0x35e000);self.u.mem_write(BASE,B);self.u.mem_map(0x20000000,0x100000);self.u.mem_map(STOP,4096)
  self.u.mem_write(CTX,struct.pack('<BBHIH',1,9,0,HANDLES,7));self.u.mem_write(HANDLES,struct.pack('<HHH',16,18,19));self.u.mem_write(DATA,bytes.fromhex('001a9401'))
  self.w32(OS+9*4,0x4a19c1);self.heap=0x20080000;self.calls=[];self.fail=False;self.role=0;self.timer=0;self.wait_action=None
  self.u.hook_add(unicorn.UC_HOOK_CODE,self.hook)
 def w32(self,a,v):self.u.mem_write(a,struct.pack('<I',v))
 def r32(self,a):return struct.unpack('<I',self.u.mem_read(a,4))[0]
 def hook(self,u,a,n,_):
  if a not in STUB:
   assert any(e<=a<int(raw[e]['body_end_inclusive'],16)+1 for e in entries),hex(a);return
  name=STUB[a];v=[u.reg_read(r) for r in R];c={'call':name,'args':v};ret=0
  if name=='buf_alloc':
   if not self.fail:ret=self.heap;self.heap+=0x100
   c['result']=ret
  elif name=='buf_free':c['queue_head']=self.r32(Q)
  elif name=='role':ret=self.role
  elif name=='tx_wait' and self.wait_action:self.wait_action(self)
  elif name=='att_copy_boundary':c['payload']=bytes(u.mem_read(v[3],v[2])).hex()
  elif name=='create_static':c['stack_args']=list(struct.unpack('<III',u.mem_read(u.reg_read(UC_ARM_REG_SP),12)));ret=0x1234
  elif name=='timer_expired':ret=self.timer;self.timer=0
  if name not in ('log','cs_enter','cs_exit','timer_update','ready_sleep'):self.calls.append(c)
  u.reg_write(R[0],ret);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
 def run(self,a,*args):
  self.u.reg_write(UC_ARM_REG_SP,0x200ff000);self.u.reg_write(UC_ARM_REG_LR,STOP|1)
  for r,v in zip(R,args):self.u.reg_write(r,v)
  self.u.emu_start(a|1,STOP,count=20000);assert self.u.reg_read(UC_ARM_REG_PC)==STOP
  return self.u.reg_read(R[0])
 def named(self,n):return [c for c in self.calls if c['call']==n]
 def send(self):self.run(0x4c4b7e,DATA,4)
 def event(self,event,conn=1):
  p=0x20078000;self.u.mem_write(p,struct.pack('<HBBIHH',conn,event,0,DATA,4,18));self.run(0x4c4910,0,p)
 def dispatch(self):self.run(0x52b9d0,0,0,0,0)
CASES=[]
def save(name,m,**extra):CASES.append({'case':name,'calls':m.calls,**extra})
# Entire stock message queue path; only allocator backing and scheduler wake are stubs.
m=M();m.send();head=m.r32(Q);assert head==0x20080000 and m.r32(Q+4)==head
assert bytes(m.u.mem_read(head+4,1))==b'\x09' and m.r32(head+12)==DATA
assert m.named('buf_alloc')[0]['args'][0]==20 and m.named('wake');m.dispatch()
assert m.r32(Q)==m.r32(Q+4)==0 and [c['args'][0] for c in m.named('buf_free')]==[head]
assert m.named('att_copy_boundary')[0]['args'][3]==DATA
save('accepted_envelope_freed_after_handler',m)
# Existing queued record survives close; dispatch drops it and only frees its envelope.
for name,setup in [('zero_connection',lambda m:m.u.mem_write(CTX,b'\0')),('different_connection',lambda m:m.u.mem_write(CTX,b'\2')),('null_handles',lambda m:m.w32(CTX+4,0)),('zero_handle',lambda m:m.u.mem_write(HANDLES,b'\0\0'))]:
 m=M();m.send();setup(m);m.dispatch();assert not m.named('att_copy_boundary') and len(m.named('tx_complete'))==1 and len(m.named('buf_free'))==1;save('queued_drop_'+name,m)
m=M();m.send();head=m.r32(Q);m.event(0x28);assert m.r32(Q)==head and not m.named('buf_free');m.dispatch();assert not m.named('att_copy_boundary') and len(m.named('buf_free'))==1;save('close_keeps_queued_message_then_drop',m)
m=M();m.send();m.event(0x28);m.event(0x27);m.dispatch();assert len(m.named('att_copy_boundary'))==1
save('same_connection_id_reopen_accepts_old_tx',m,epoch_after=struct.unpack('<H',m.u.mem_read(CTX+8,2))[0])
m=M();m.send();m.u.mem_write(CTX+8,struct.pack('<H',99));m.dispatch();assert m.named('att_copy_boundary');save('epoch_change_alone_does_not_guard_tx',m)
# FIFO and automatic envelope cleanup for ignored message events.
m=M();m.send();m.u.mem_write(DATA,b'ABCD');m.send();m.dispatch();assert len(m.named('buf_free'))==2
assert [c['payload'] for c in m.named('att_copy_boundary')]==['41424344']*2
save('two_fifo_envelopes_share_borrowed_payload',m)
m=M();m.send();m.u.mem_write(m.r32(Q)+10,b'\xfe');m.dispatch();assert not m.named('att_copy_boundary') and len(m.named('buf_free'))==1;save('unknown_event_envelope_still_freed',m)
for name,setup in [('disconnected',lambda m:m.u.mem_write(CTX,b'\0')),('null_handles',lambda m:m.w32(CTX+4,0)),('zero_handle',lambda m:m.u.mem_write(HANDLES,b'\0\0')),('allocation_failure',lambda m:setattr(m,'fail',True))]:
 m=M();setup(m);m.send();assert not m.r32(Q) and not m.named('buf_free');assert len(m.named('tx_complete'))==(1 if name=='allocation_failure' else 0);save('send_'+name,m)
# WSF timer callback is not an allocated message and is not auto-freed.
m=M();m.timer=0x20079000;m.u.mem_write(m.timer+8,bytes(4)+b'\x09');m.u.mem_write(OS+0x3c,b'\x02');m.dispatch();assert not m.named('buf_free');save('timer_callback_not_message_free',m)
# Delayed CCCD cancellation uses a separate 64-slot callback table.
for name,initialized,matching in [('uninitialized',False,False),('no_match',True,False),('matches',True,True)]:
 m=M();m.send();head=m.r32(Q);m.w32(f32(0x476c2c),int(initialized));table=f32(0x476c6c)
 m.w32(table,0x4c46d1 if matching else 0x12345679);m.w32(table+4,0x4c46d1 if matching else 0)
 m.w32(table+8,0x12345679);m.run(0x476ace,0x4c46d1)
 assert m.r32(Q)==head and not m.named('buf_free') and m.r32(table+8)==0x12345679
 if matching:assert m.r32(table)==m.r32(table+4)==0 and len(m.named('reschedule_delays'))==1
 else:assert not m.named('reschedule_delays')
 save('cancel_cccd_'+name,m)
# Connection is read again after the semaphore wait; no transaction snapshot.
m=M();m.wait_action=lambda m:m.u.mem_write(CTX,b'\0');m.send();assert m.r32(Q)
m.dispatch();assert not m.named('att_copy_boundary') and len(m.named('buf_free'))==1
save('disconnect_during_wait_enqueues_zero_connection_then_drops',m)
# Task creation executes the original CMSIS wrapper down to static-kernel-create.
attrs=[]
for name,entry,attr,state,wantprio,wantstack in [('ring',0x4c4da4,0x75b8a4,0x20004120,46,4096),('ble_wsf',0x4d0af6,0x75b838,0x20004068,49,16384)]:
 m=M();m.run(entry);c=m.named('create_static')[0];assert c['args'][2]==wantstack//4 and c['stack_args'][0]==wantprio and m.r32(state+8)==0x1234
 data=B[attr-BASE:attr-BASE+36];attrs.append({'name':name,'address':hex(attr),'bytes':data.hex(),'sha256':hashlib.sha256(data).hexdigest(),'priority':wantprio,'stack_bytes':wantstack})
 save('create_'+name,m)
# Local termination wrappers do not traverse or free pending WSF messages.
for name,entry,state in [('ring',0x4c4dd0,0x20004120),('ble_wsf',0x4d0b1c,0x20004068)]:
 for present in (False,True):
  m=M();m.send();head=m.r32(Q);m.w32(state+8,0x1234 if present else 0);m.run(entry)
  assert m.r32(Q)==head and not m.named('buf_free') and not m.r32(state+8)
  assert len(m.named('terminate'))==int(present);save('terminate_%s_%s'%(name,present),m)
report={'input_sha256':SHA,'capstone':capstone.__version__,'unicorn':unicorn.__version__,'scope':'original queue/send/dispatcher and task wrappers; ATT, master preprocessing, RTOS and callback deinit provider explicitly stubbed','functions':records,'task_attributes':attrs,'case_count':len(CASES),'cases':CASES}
(OUT/'validation.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS',len(CASES),'cases;',len(records),'body hashes')
