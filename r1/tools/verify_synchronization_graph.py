#!/usr/bin/env python3
"""Actual CMSIS/kernel synchronization lifetimes with controlled prekernel task selection."""
import hashlib,itertools,json,struct
from pathlib import Path
from unicorn import UcError
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ENTRIES={'r1_native_task_create_static':0x98418,'osMutexNew':0x7d4d6,'osMutexAcquire':0x7d488,'osMutexRelease':0x7d536,'osSemaphoreNew':0x7d60c,'osSemaphoreAcquire':0x7d57c,'osSemaphoreRelease':0x7d698,'osSemaphoreGetCount':0x7d5e8,'xTaskPriorityInherit':0x989ac,'vQueueDelete':0x95f70}
def verify(stock,candidate,syms,baseline):
 receipt=BASE/'board/synchronization-verification.json';receipt.unlink(missing_ok=True);comparisons=0;workflows=0;inherits=0;messages=0
 for u in (stock,candidate):
  try:u.mem_map(0xe000e000,4096)
  except UcError:pass
 def word(u,a):return struct.unpack('<I',bytes(u.mem_read(a,4)))[0]
 def put(u,a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
 def target(u,lr):
  first,second=struct.unpack('<2H',bytes(u.mem_read((lr&~1)-4,4)));assert first&0xf800==0xf000 and second&0xd000==0xd000;sign=(first>>10)&1;offset=(sign<<24)|((1^((second>>13)&1)^sign)<<23)|((1^((second>>11)&1)^sign)<<22)|((first&0x3ff)<<12)|((second&0x7ff)<<1)
  return ((lr&~1)+offset-(1<<25 if sign else 0))&0xffffffff
 def snapshot(u):
  heap=bytearray(u.mem_read(0x2001e588,51212));end=word(u,0x200077fc)
  if end:
   block=0x2001e588
   while block<end:
    value=word(u,block+4);size=value&0x7fffffff;assert size and not size&7 and block+size<=end
    if value&0x80000000:
     lr=word(u,block+8);assert target(u,lr)==(0x855a0 if u is stock else syms['pvPortMalloc']&~1)
     if u is stock:assert lr==0x97b39
     else:struct.pack_into('<I',heap,block-0x2001e588+8,word(stock,block+8))
    block+=size
  return (bytes(heap),bytes(u.mem_read(0x200077fc,20)),bytes(u.mem_read(0x20001000,112)),bytes(u.mem_read(0x20001100,112)),bytes(u.mem_read(0x20003e00,0x500)),bytes(u.mem_read(0x20007810,96)),bytes(u.mem_read(0x2002ad94,1220)),word(u,0xe000ed04),u.reg_read(UC_ARM_REG_PRIMASK),u.reg_read(UC_ARM_REG_BASEPRI))
 saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
 def call(name,args=(),ipsr=0):
  nonlocal comparisons
  outcomes=[]
  for u in (stock,candidate):
   u.reg_write(UC_ARM_REG_IPSR,ipsr);u.reg_write(UC_ARM_REG_SP,0x2003c000);u.reg_write(UC_ARM_REG_LR,0x20000101)
   for reg,value in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),args):u.reg_write(reg,value)
   u.mem_write(0x2003c000,struct.pack('<3I',*(list(args[4:])+[0,0,0])[:3]))
   for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
   try:u.emu_start((ENTRIES[name] if u is stock else syms[name])|1,0x20000100,count=2000000)
   except UcError as error:raise AssertionError((name,args,u is stock,hex(u.reg_read(UC_ARM_REG_PC)))) from error
   assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003c000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)];outcomes.append((None if name=='vQueueDelete' else u.reg_read(UC_ARM_REG_R0),snapshot(u)))
  assert outcomes[0]==outcomes[1],(name,args,ipsr,[(i,str(a)[:180],str(b)[:180]) for i,(a,b) in enumerate(zip(outcomes[0],outcomes[1])) if a!=b]);comparisons+=1;return outcomes[0][0]
 def select(address):
  for u in (stock,candidate):put(u,0x2000781c,address)
 try:
  for pattern,mask,mutex_static,sem_static,recursive,irq in itertools.product((0,0xa5),(0,1),(0,1),(0,1),(0,1),(0,33)):
   for u in (stock,candidate):
    u.mem_write(0x20000000,baseline[id(u)]);u.mem_write(0x2001e588,bytes([pattern])*51200);u.mem_write(0x20001000,bytes([0x93])*0x200);u.mem_write(0x20003e00,bytes([0x93])*0x500);u.mem_write(0x20003e00,b'Owner\0Requester\0');u.mem_write(0x20003f00,struct.pack('<4I',0xfffffff0,1 if recursive else 0,0x20004000,80));u.mem_write(0x20003f20,struct.pack('<4I',0xfffffff0,0xffffffff,0x20004100,80));u.mem_write(0xe000ed04,bytes(4));u.mem_write(0xe000ed0c,bytes(4));u.reg_write(UC_ARM_REG_PRIMASK,mask);u.reg_write(UC_ARM_REG_BASEPRI,0)
   for cb,stack,priority,name in ((0x20001000,0x20002000,8,0x20003e00),(0x20001100,0x20002800,25,0x20003e06)):
    assert call('r1_native_task_create_static',(0x12345679,name,256,0x87654321,priority,stack,cb))==cb
   select(0x20001000)
   mutex=call('osMutexNew',(0x20003f00 if mutex_static else 0,))
   # Dynamic recursive attributes must preserve the recursive bit with NULL/zero storage.
   if recursive and not mutex_static:
    call('vQueueDelete',(mutex,))
    for u in (stock,candidate):u.mem_write(0x20003f00,struct.pack('<4I',0,1,0,0))
    mutex=call('osMutexNew',(0x20003f00,))
   assert mutex and (mutex&1)==recursive;raw_mutex=mutex&~1
   for index in range(3 if recursive else 1):assert call('osMutexAcquire',(mutex,0))==0
   for u in (stock,candidate):assert word(u,0x20001064)==1 and word(u,raw_mutex+8)==0x20001000
   if recursive:
    select(0x20001100);assert call('osMutexRelease',(mutex,))==0xfffffffd
   select(0x20001100);assert call('xTaskPriorityInherit',(0x20001000,))==1;inherits+=1
   for u in (stock,candidate):assert word(u,0x2000102c)==25
   select(0x20001000)
   for index in range(3 if recursive else 1):assert call('osMutexRelease',(mutex,))==0
   for u in (stock,candidate):assert word(u,0x20001064)==0 and word(u,0x2000102c)==8 and word(u,raw_mutex+8)==0
   sem=call('osSemaphoreNew',(3,1,0x20003f20 if sem_static else 0));assert sem
   assert call('osSemaphoreGetCount',(sem,),irq)==1
   for index in range(2):assert call('osSemaphoreRelease',(sem,),irq)==0;messages+=1
   assert call('osSemaphoreRelease',(sem,),irq)==0xfffffffd
   for index in range(3):assert call('osSemaphoreAcquire',(sem,0),irq)==0;messages+=1
   assert call('osSemaphoreAcquire',(sem,0),irq)==0xfffffffd and call('osSemaphoreGetCount',(sem,),irq)==0
   call('vQueueDelete',(sem,));call('vQueueDelete',(raw_mutex,));workflows+=1
   for u in (stock,candidate):assert word(u,0x20007800)==(0 if mutex_static and sem_static else 51184)
 finally:
  for u in (stock,candidate):u.mem_write(0x20000000,baseline[id(u)]);u.reg_write(UC_ARM_REG_IPSR,0);u.reg_write(UC_ARM_REG_PRIMASK,0);u.reg_write(UC_ARM_REG_BASEPRI,0)
 result=dict(application_sha256=sha(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin'),board_report_sha256=sha(BASE/'board/report.json'),verification_driver_sha256=sha(ROOT/'r1/tools/verify_native_board.py'),synchronization_driver_sha256=sha(Path(__file__)),provider_reports={name:sha(BASE/name/'report.json') for name in ('rtos-synchronization','rtos-mutex-kernel','rtos-mutex-tasks')},comparisons=comparisons,workflows=workflows,inheritance_lifetimes_per_implementation=inherits,semaphore_operations_per_implementation=messages,provider_interception=False,heap_bytes_compared_per_call=51212,scope='Actual static task construction, CMSIS mutex/semaphore wrappers, kernel recursive ownership, inherited/restored priorities, task/ISR semaphore operations, queues/critical/heap/list providers and full reclamation',limitations=['Current task is selected by controlled pointer writes; inheritance is invoked explicitly without blocking/context transfer. Task entry pointers remain unexecuted, and stack frames are outside this comparison. IRQ/mask/MMIO values are fixtures. Only authenticated heap caller LR is normalized. No blocking resumption, hardware concurrency or whole-image identity proof.']);receipt.write_text(json.dumps(result,indent=2)+'\n');print(comparisons,'synchronization graph comparisons;',workflows,'workflows;',inherits,'inheritance lifetimes')
if __name__=='__main__':raise SystemExit('Use verify_native_board.py --synchronization')
