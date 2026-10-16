#!/usr/bin/env python3
"""Real CMSIS/queue/heap/scheduler/critical/movement graph; no provider fixtures."""
import hashlib,itertools,json,struct
from pathlib import Path
from unicorn import UcError
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ENTRIES={'osSemaphoreNew':0x7d60c,'xQueueGenericCreate':0x97b0e,'xQueueGenericSend':0x97c50,'vQueueDelete':0x95f70}
def verify(stock,candidate,syms,baseline):
 receipt=BASE/'board/queue-lifecycle-verification.json';receipt.unlink(missing_ok=True);comparisons=0;workflows=0;overlap_calls=0
 for u in (stock,candidate):
  try:u.mem_map(0xe000e000,0x1000)
  except UcError:pass
 def word(u,a):return struct.unpack('<I',bytes(u.mem_read(a,4)))[0]
 def call_target(u,lr):
  first,second=struct.unpack('<2H',bytes(u.mem_read((lr&~1)-4,4)));assert first&0xf800==0xf000 and second&0xd000==0xd000;sign=(first>>10)&1;offset=(sign<<24)|((1^((second>>13)&1)^sign)<<23)|((1^((second>>11)&1)^sign)<<22)|((first&0x3ff)<<12)|((second&0x7ff)<<1)
  return ((lr&~1)+offset-(1<<25 if sign else 0))&0xffffffff
 assert call_target(stock,0x97b39)==0x855a0
 def snapshot(u):
  heap=bytearray(u.mem_read(0x2001e588,51212))
  if word(u,0x200077fc) and struct.unpack_from('<I',heap,4)[0]&0x80000000:
   lr=struct.unpack_from('<I',heap,8)[0];assert call_target(u,lr)==(0x855a0 if u is stock else syms['pvPortMalloc']&~1)
   if u is stock:assert lr==0x97b39
   else:struct.pack_into('<I',heap,8,0x97b39)
  return (bytes(heap),bytes(u.mem_read(0x200077fc,20)),bytes(u.mem_read(0x20002f00,0x1300)),bytes(u.mem_read(0xe000ed04,4)),u.reg_read(UC_ARM_REG_PRIMASK),u.reg_read(UC_ARM_REG_BASEPRI))
 saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
 def call(name,args):
  nonlocal comparisons
  results=[]
  for u in (stock,candidate):
   u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
   for reg,value in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),args):u.reg_write(reg,value)
   for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
   u.emu_start((ENTRIES[name] if u is stock else syms[name])|1,0x20000100,count=2000000);assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)];results.append((None if name=='vQueueDelete' else u.reg_read(UC_ARM_REG_R0),snapshot(u)))
  assert results[0]==results[1],(name,args,[(k,str(a)[:160],str(b)[:160]) for k,(a,b) in enumerate(zip(results[0],results[1])) if a!=b]);comparisons+=1;return results[0][0]
 def reset(pattern,mask):
  for u in (stock,candidate):
   u.mem_write(0x20000000,baseline[id(u)]);u.mem_write(0x2001e588,bytes([pattern])*51200);u.mem_write(0x20002f00,bytes([0x93])*0x1300);u.mem_write(0x20002f00,struct.pack('<4I',0,0,0x20003000,80));u.mem_write(0xe000ed04,bytes(4));u.reg_write(UC_ARM_REG_IPSR,0);u.reg_write(UC_ARM_REG_PRIMASK,mask);u.reg_write(UC_ARM_REG_BASEPRI,0)
 try:
  for pattern,mask,maximum,initial,static in itertools.product((0,0xa5),(0,1),(1,2,7),(0,1),(False,True)):
   reset(pattern,mask);handle=call('osSemaphoreNew',(maximum,initial,0x20002f00 if static else 0));assert handle==(0x20003000 if static else 0x2001e598)
   for count in range(initial,maximum):assert call('xQueueGenericSend',(handle,0,0,0))==1
   assert call('xQueueGenericSend',(handle,0,0,0))==0
   if maximum==1:assert call('xQueueGenericSend',(handle,0,0,2))==1
   call('vQueueDelete',(handle,))
   for u in (stock,candidate):assert word(u,0x200077fc)==(0 if static else 0x2002ad78) and word(u,0x20007800)==(0 if static else 51184) and word(u,0x2000780c)==(0 if static else 1)
   workflows+=1
  for pattern,mask,length,item,position,delta in itertools.product((0,0xa5),(0,1),(1,3),(1,4,17),(0,1),(-1,0,1)):
   reset(pattern,mask);handle=call('xQueueGenericCreate',(length,item,0));assert handle==0x2001e598
   for index in range(length):
    destination=word(stock,handle+4 if position==0 else handle+12);assert call('xQueueGenericSend',(handle,destination+delta,0,position))==1;overlap_calls+=1
   assert call('xQueueGenericSend',(handle,0x20004000,0,0))==0
   if length==1:assert call('xQueueGenericSend',(handle,handle+80+delta,0,2))==1;overlap_calls+=1
   call('vQueueDelete',(handle,))
   for u in (stock,candidate):assert word(u,0x20007800)==51184 and word(u,0x20007808)==1 and word(u,0x2000780c)==1
   workflows+=1
 finally:
  for u in (stock,candidate):u.mem_write(0x20000000,baseline[id(u)])
 receipt.write_text(json.dumps(dict(application_sha256=sha(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin'),board_report_sha256=sha(BASE/'board/report.json'),verification_driver_sha256=sha(ROOT/'r1/tools/verify_native_board.py'),lifecycle_driver_sha256=sha(Path(__file__)),comparisons=comparisons,workflows=workflows,overlap_calls_per_implementation=overlap_calls,provider_interception=False,heap_bytes_compared_per_call=51212,scope='Actual CMSIS semaphoreNew/queue creation/send/delete/native heap/scheduler/critical/movement graph; binary/counting/static/dynamic lifetimes, full/overwrite/front/back/overlap paths and heap reclamation',limitations=['Controlled prekernel, nonblocking operations have no waiters. Caller BL targets are authenticated and only allocated-header caller LR is normalized. Full blocking task scheduling, mutex ownership, physical concurrency and whole-image byte equality remain gates.']),indent=2)+'\n');print(comparisons,'queue lifecycle comparisons;',workflows,'workflows;',overlap_calls,'overlap sends; no provider interception')
