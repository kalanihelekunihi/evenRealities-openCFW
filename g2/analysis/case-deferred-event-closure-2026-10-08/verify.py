"""Real original/native queue-copy paths; no kernel child replacement.
Coherent synthetic queues have no receive waiters except explicit stop-boundary cases.
"""
from pathlib import Path
import sys,struct,json,hashlib,itertools
D=Path(__file__).resolve().parent;s=D.parent/'case-uart-receive-closure-2026-10-08/verify.py';text=s.read_text().split('rows=[]')[0];start=text.index('entries={w:');end=text.index('\ndef guest',start);text=text[:start]+'entries={}'+text[end:];ns={'__file__':str(s)};exec(text,ns);symbols=ns['symbols']
from unicorn import UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
Q=0x20004000;BUF=0x20005020;ITEM=0x20003200;YIELD=0x20003000;EVENT=0x20006000
rows=[]
def fixture(length,count,index,size,lock,mask,yield_value=0,waiters=0):
 u=ns['guest'](0x20,1,0xff,0,0,0,mask,0);u.mem_map(0xe000e000,0x1000);u.mem_write(Q,b'\0'*72);u.mem_write(Q,struct.pack('<IIII',BUF,BUF+index*size,BUF+length*size,BUF+(length-1)*size));u.mem_write(Q+0x24,struct.pack('<I',waiters));u.mem_write(Q+0x38,struct.pack('<IIIbb',count,length,size,-1,lock));u.mem_write(BUF-16,b'\xa7'*(length*size+32));u.mem_write(ITEM,bytes(range(64)));u.mem_write(YIELD,struct.pack('<I',yield_value));u.mem_write(0x20000164,struct.pack('<I',Q));u.mem_write(0x200000f0,struct.pack('<I',EVENT));return u
def execute(u,entry,args,mask,atomic,stop_waiter=False):
 writes=[];boundary=[];copies=[]
 def code(u,a,n,data):
  if a==0x080001b4:copies.append([u.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2]])
  if a in [0x0800cba0,0x0800cb38]:
   assert stop_waiter,('unexpected_task_or_mutex_peer',hex(a));boundary.extend([hex(a),hex(u.reg_read(UC_ARM_REG_R0))]);u.emu_stop()
 def write(u,access,a,n,v,data):
  if Q<=a<Q+72 or BUF-16<=a<BUF+192 or a==YIELD:
   if atomic:assert u.reg_read(UC_ARM_REG_PRIMASK)==1,('queue_write_not_masked',hex(a),entry)
   writes.append([hex(a),n,hex(v),u.reg_read(UC_ARM_REG_PRIMASK)])
  if a==0xe000ed04:raise AssertionError('unexpected_pendsv_without_waiter')
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,write)
 for r,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],args):u.reg_write(r,v)
 u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20000001);u.emu_start(entry|1,0x20000000,count=30000)
 assert boundary or u.reg_read(UC_ARM_REG_PC)==0x20000000
 assert u.reg_read(UC_ARM_REG_PRIMASK)==(1 if boundary and atomic else mask)
 # Normalize write granularity: native byte-copy vs original aligned word-copy.
 state=(bytes(u.mem_read(Q,72)),bytes(u.mem_read(BUF-16,224)),bytes(u.mem_read(YIELD,4)),bytes(u.mem_read(ITEM,64)),u.reg_read(UC_ARM_REG_PRIMASK),tuple(boundary))
 return u.reg_read(UC_ARM_REG_R0),state,writes,copies
# Direct copy helper: no semaphore/mutex body, valid allocated non-overlapping buffers.
for size,length,pos,count,mask in itertools.product([1,4,16,17],[1,2,4],[0,1,2],[0,1],[0,1]):
 if pos==2 and length!=1:continue
 for index in range(length):
  vals=[]
  for entry in [0x0800ad48,symbols['case_copy_to_queue'],symbols['case_public_copy']]:
   u=fixture(length,count,index,size,-1,mask);u.mem_write(Q+12,struct.pack('<I',BUF+index*size));v=execute(u,entry,[Q,ITEM,pos],mask,False);vals.append(v)
  assert vals[0][:2]==vals[1][:2]==vals[2][:2],('copy',size,length,pos,count,index,mask)
  rows.append(dict(kind='copy_three_way',size=size,length=length,position=pos,count=count,index=index,primask=mask))
# Consumer copy leaf: advances read pointer then copies to caller-owned buffer.
for size,length,index,mask in itertools.product([1,4,16,17],[1,2,4],range(4),[0,1]):
 if index>=length:continue
 vals=[]
 for entry in [0x0800ad24,symbols['case_copy_from_queue'],symbols['case_public_read']]:
  u=fixture(length,1,0,size,-1,mask);u.mem_write(Q+12,struct.pack('<I',BUF+index*size));payload=bytes((i*3+5)%256 for i in range(length*size));u.mem_write(BUF,payload);v=execute(u,entry,[Q,ITEM],mask,False);next_index=(index+1)%length;assert bytes(u.mem_read(ITEM,size))==payload[next_index*size:(next_index+1)*size];vals.append(v)
 assert vals[0][1]==vals[1][1]==vals[2][1]
 rows.append(dict(kind='read_copy_three_way',size=size,length=length,index=index,primask=mask))
def states(length):
 return itertools.product([0,9,10],[0,9]) if length==10 else itertools.product(range(length+1),range(length))
# Complete FromISR queue paths: coherent queue state, empty waiter list.
for length,mask,lock,yield_value in itertools.product([1,2,4,10],[0,1],[-1,0,1,5,126],[0,7]):
 for count,index in states(length):
  vals=[]
  for entry in [0x0800c7a8,symbols['case_queue_send_isr']]:
   u=fixture(length,count,index,16,lock,mask,yield_value);vals.append(execute(u,entry,[Q,ITEM,YIELD,0],mask,True))
  assert vals[0][:2]==vals[1][:2],('queue',length,count,index,mask,lock,yield_value)
  assert vals[0][0]==int(count<length)
  rows.append(dict(kind='queue_isr',length=length,count=count,index=index,primask=mask,tx_lock=lock,initial_yield=yield_value,accepted=bool(vals[0][0])))
# Deferred message producer through actual/native queue, then poison producer stack.
for length,mask,flags in itertools.product([1,2,4,10],[0,1],[0,8,0x40,0xffffff]):
 for count,index in states(length):
  vals=[]
  for entry in [0x0800ce0c,symbols['case_pend_from_isr'],symbols['case_public_pend']]:
   u=fixture(length,count,index,16,-1,mask);v=execute(u,entry,[0x0800bf8d,EVENT,flags,YIELD],mask,True);copied=bytes(u.mem_read(BUF+index*16,16));u.mem_write(0x20007000,b'\xee'*0x1000);assert bytes(u.mem_read(BUF+index*16,16))==copied
   if count<length:assert copied==struct.pack('<iIII',-2,0x0800bf8d,EVENT,flags)
   vals.append(v)
  assert vals[0][:2]==vals[1][:2]==vals[2][:2],('pend',length,count,index,mask,flags)
  rows.append(dict(kind='pend_three_way_actual_queue',length=length,count=count,index=index,primask=mask,flags=hex(flags),accepted=bool(vals[0][0]),stack_poison_retains_queued_bytes=True))
# Full ISR wrapper -> deferred producer -> queue/copy/mask providers, no stubs.
for length,mask,ipsr,flags in itertools.product([1,2,4,10],[0,1],[15,16],[0,8,0x40,0xffffff,0x1000000]):
 for count,index in states(length):
  vals=[]
  for entry in [0x0800a888,symbols['case_event_flags_set']]:
   u=fixture(length,count,index,16,-1,mask);u.reg_write(UC_ARM_REG_IPSR,ipsr);v=execute(u,entry,[EVENT,flags],mask,True);assert u.reg_read(UC_ARM_REG_IPSR)==ipsr
   expected=0xfffffffc if flags&0xff000000 else flags if count<length else 0xfffffffd
   assert v[0]==expected
   if count<length and not flags&0xff000000:assert bytes(u.mem_read(BUF+index*16,16))==struct.pack('<iIII',-2,0x0800bf8d,EVENT,flags)
   vals.append(v)
  assert vals[0][:2]==vals[1][:2],('event',length,count,index,mask,ipsr,flags)
  rows.append(dict(kind='wrapper_actual_queue',length=length,count=count,index=index,primask=mask,ipsr=ipsr,flags=hex(flags),return_value=hex(vals[0][0])))
# Stop at task removal BEFORE its first instruction; state contains completed copy.
for mask,lock,index in itertools.product([0,1],[-1,0],[0,1]):
 vals=[]
 for entry in [0x0800c7a8,symbols['case_queue_send_isr']]:
  u=fixture(2,0,index,16,lock,mask,0,1);v=execute(u,entry,[Q,ITEM,YIELD,0],mask,True,True);vals.append(v)
 assert vals[0][1]==vals[1][1]
 assert bool(vals[0][1][-1])==(lock==-1)
 rows.append(dict(kind='waiter_boundary',primask=mask,tx_lock=lock,index=index,endpoint='task_removal_before_first_instruction' if lock==-1 else 'return_locked_queue'))
counts={k:sum(r['kind']==k for r in rows) for k in sorted({r['kind'] for r in rows})}
(D/'results.json').write_text(json.dumps(dict(status='PASS',cases=len(rows),case_counts=counts,comparisons=rows,firmware_sha256=hashlib.sha256(ns['blob']).hexdigest(),raw_sha256=hashlib.sha256(ns['raw']).hexdigest(),elf_sha256=hashlib.sha256(ns['elf'].read_bytes()).hexdigest(),limits=['Real original/native copy, FromISR queue, deferred producer and ISR wrapper instructions execute; no child result replacement.','Selected public copy excludes mutex body; public producer uses actual original queue peer. Minimal ABI/configuration scaffolds not full kernel configuration attribution.','Synthetic coherent queue state, item_size16 integration, allocated buffers; empty wait lists except explicit task-removal entry boundary. No actual daemon task execution, queue initialization or scheduling trace.','Actual PRIMASK save/restore providers080000f4/080000fc execute; queue/buffer writes checked mask1 and restored input mask. Direct copy helper assumes callers enforce critical section and is also tested separately with masks0/1.','Event handles/callback pointers copied by value; no referenced-object lifetime proof or device hardware claim.','No commits/index/production/firmware/device modifications.']),indent=2)+'\n');print('PASS',len(rows),counts)
