#!/usr/bin/env python3
"""Actual blocking-send timeout graph with controlled tick/context transfer."""
import hashlib,itertools,json,struct
from pathlib import Path
from unicorn import UcError,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ENTRIES={'xQueueGenericCreate':0x97b0e,'xQueueGenericSend':0x97c50,'vQueueDelete':0x95f70,'xTaskIncrementTick':0x987e0}
def verify(stock,candidate,syms,baseline):
 receipt=BASE/'board/queue-timeout-verification.json';receipt.unlink(missing_ok=True);states={};hooks=[];comparisons=0;workflows=0;tick_calls=0;pauses=0
 for u in (stock,candidate):
  try:u.mem_map(0xe000e000,0x1000)
  except UcError:pass
 def put(u,a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
 def word(u,a):return struct.unpack('<I',bytes(u.mem_read(a,4)))[0]
 def init_list(u,a):u.mem_write(a,struct.pack('<5I',0,a+8,0xffffffff,a+8,a+8))
 def target(u,lr):
  first,second=struct.unpack('<2H',bytes(u.mem_read((lr&~1)-4,4)));assert first&0xf800==0xf000 and second&0xd000==0xd000;sign=(first>>10)&1;offset=(sign<<24)|((1^((second>>13)&1)^sign)<<23)|((1^((second>>11)&1)^sign)<<22)|((first&0x3ff)<<12)|((second&0x7ff)<<1)
  return ((lr&~1)+offset-(1<<25 if sign else 0))&0xffffffff
 def snapshot(u):
  heap=bytearray(u.mem_read(0x2001e588,51212))
  if word(u,0x200077fc) and struct.unpack_from('<I',heap,4)[0]&0x80000000:
   lr=struct.unpack_from('<I',heap,8)[0];assert target(u,lr)==(0x855a0 if u is stock else syms['pvPortMalloc']&~1)
   if u is stock:assert lr==0x97b39
   else:struct.pack_into('<I',heap,8,0x97b39)
  return (bytes(heap),bytes(u.mem_read(0x200077fc,20)),bytes(u.mem_read(0x20001000,128)),bytes(u.mem_read(0x20004000,256)),bytes(u.mem_read(0x20007810,76)),bytes(u.mem_read(0x2002ad94,1220)),bytes(u.mem_read(0xe000ed04,4)),u.reg_read(UC_ARM_REG_PRIMASK),u.reg_read(UC_ARM_REG_BASEPRI))
 def write(u,access,a,size,value,user):
  f=states[id(u)]
  if f['armed'] and a==0xe000ed04 and value&0x10000000:f['pending']=True
 def code(u,a,size,user):
  f=states[id(u)]
  if f['pending']:f['pending']=False;f['armed']=False;f['paused']=True;u.emu_stop()
 for u in (stock,candidate):hooks.extend(((u,u.hook_add(UC_HOOK_MEM_WRITE,write,begin=0xe000ed04,end=0xe000ed07)),(u,u.hook_add(UC_HOOK_CODE,code))))
 saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
 def start(u,name,args,sp=0x2003f000):
  u.reg_write(UC_ARM_REG_SP,sp);u.reg_write(UC_ARM_REG_LR,0x20000101)
  for reg,value in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),args):u.reg_write(reg,value)
  for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
  u.emu_start((ENTRIES[name] if u is stock else syms[name])|1,0x20000100,count=2000000)
 def call(name,args,sp=0x2003f000):
  nonlocal comparisons,tick_calls
  results=[]
  for u in (stock,candidate):
   start(u,name,args,sp);assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==sp and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)];results.append((None if name=='vQueueDelete' else u.reg_read(UC_ARM_REG_R0),snapshot(u)))
  assert results[0]==results[1],(name,args,[(k,[(i,a,b) for i,(a,b) in enumerate(zip(results[0][1][k],results[1][1][k])) if a!=b][:12]) for k in range(7) if results[0][1][k]!=results[1][1][k]]);comparisons+=1;tick_calls+=name=='xTaskIncrementTick';return results[0][0]
 try:
  for tick,wait,priority,length,item,pattern in itertools.product((0,100,0xfffffffe),(1,2,7),(0,15,55),(1,3),(0,4),(0,0xa5)):
   for u in (stock,candidate):
    states[id(u)]={'armed':False,'pending':False,'paused':False};u.mem_write(0x20000000,baseline[id(u)]);u.mem_write(0x2001e588,bytes([pattern])*51200);u.mem_write(0x20001000,bytes([0xa5])*128);u.mem_write(0x20004000,bytes([0x79])*256);u.mem_write(0x2002ad94,bytes(1220));u.mem_write(0xe000ed04,bytes(4));u.reg_write(UC_ARM_REG_IPSR,0);u.reg_write(UC_ARM_REG_PRIMASK,0);u.reg_write(UC_ARM_REG_BASEPRI,0)
    for i in range(56):init_list(u,0x2002ad94+i*20)
    for a in (0x2002b1f4,0x2002b208,0x2002b21c,0x2002b244):init_list(u,a)
    for a,v in ((0x2000781c,0x20001000),(0x20007824,1),(0x20007828,tick),(0x2000782c,priority),(0x20007830,1),(0x2000783c,0x7fffffff),(0x20007844,0xffffffff),(0x20007850,0),(0x20007854,0x2002b1f4),(0x20007858,0x2002b208),(0x2000102c,priority),(0x20001060,priority),(0x20001064,0)):put(u,a,v)
    ready=0x2002ad94+priority*20;sentinel=ready+8;u.mem_write(0x20001004,struct.pack('<5I',0,sentinel,sentinel,0x20001000,ready));put(u,ready,1);put(u,sentinel+4,0x20001004);put(u,sentinel+8,0x20001004);put(u,0x20001018,56-priority);put(u,0x20001024,0x20001000);put(u,0x20001028,0)
   handle=call('xQueueGenericCreate',(length,item,0));assert handle==0x2001e598
   for i in range(length):assert call('xQueueGenericSend',(handle,0x20004000 if item else 0,0,0))==1
   contexts={}
   for u in (stock,candidate):
    states[id(u)].update(armed=True,pending=False,paused=False);start(u,'xQueueGenericSend',(handle,0x20004000 if item else 0,wait,0));assert states[id(u)]['paused'] and u.reg_read(UC_ARM_REG_PC)!=0x20000100;contexts[id(u)]=u.context_save();assert word(u,handle+16)==1 and word(u,0x20001028)==handle+16
   assert snapshot(stock)==snapshot(candidate),'blocked state';comparisons+=1;pauses+=1
   for i in range(wait):
    call('xTaskIncrementTick',(),0x2003c000)
    for u in (stock,candidate):u.context_restore(contexts[id(u)])
   results=[]
   for u in (stock,candidate):
    assert word(u,handle+16)==0 and word(u,0x20001028)==0 and word(u,0x20001014)==0x2002ad94+priority*20;u.emu_start(u.reg_read(UC_ARM_REG_PC)|1,0x20000100,count=2000000);assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)];results.append((u.reg_read(UC_ARM_REG_R0),snapshot(u)));assert word(u,handle+56)==length and word(u,0x20007828)==(tick+wait)&0xffffffff
   assert results[0]==results[1] and results[0][0]==0,'timeout return';comparisons+=1;call('vQueueDelete',(handle,));workflows+=1
 finally:
  for u,h in hooks:u.hook_del(h)
  for u in (stock,candidate):u.mem_write(0x20000000,baseline[id(u)])
 receipt.write_text(json.dumps(dict(application_sha256=sha(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin'),board_report_sha256=sha(BASE/'board/report.json'),verification_driver_sha256=sha(ROOT/'r1/tools/verify_native_board.py'),timeout_driver_sha256=sha(Path(__file__)),comparisons=comparisons,workflows=workflows,pend_sv_pauses_per_implementation=pauses,tick_calls_per_implementation=tick_calls,provider_interception=False,scope='Actual blocking queue-send timeout graph through heap, ordered wait/list placement, suspend/resume, critical and tick providers, including tick/overflow-list wrap and mutex-layout task canaries',limitations=['PendSV is observed and execution paused; tick calls run on a controlled separate stack and saved task CPU context is restored. This models scheduling transfer, not the native PendSV/context-switch implementation. Task state is a controlled104-byte prefix with preserved tail; full task construction, event-driven producer/consumer wakeups, physical concurrency and whole-image identity remain gates.']),indent=2)+'\n');print(comparisons,'queue timeout comparisons;',workflows,'workflows;',tick_calls,'actual tick calls; no provider interception')
