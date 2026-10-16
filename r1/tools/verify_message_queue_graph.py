#!/usr/bin/env python3
"""CMSIS message queues with actual queue/heap/IRQ/query/movement providers."""
import hashlib,itertools,json,struct
from pathlib import Path
from unicorn import UcError
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ENTRIES={'osMessageQueueNew':0x7d3b4,'osMessageQueuePut':0x7d40c,'osMessageQueueGet':0x7d310,'osMessageQueueGetCount':0x7d390,'osMessageQueueGetCapacity':0x7d388,'vQueueDelete':0x95f70}
def verify(stock,candidate,syms,baseline):
 receipt=BASE/'board/message-queue-verification.json';receipt.unlink(missing_ok=True);comparisons=0;workflows=0;messages=0
 for u in (stock,candidate):
  try:u.mem_map(0xe000e000,4096)
  except UcError:pass
 def word(u,a):return struct.unpack('<I',bytes(u.mem_read(a,4)))[0]
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
  return (bytes(heap),bytes(u.mem_read(0x200077fc,20)),bytes(u.mem_read(0x20002f00,0x1300)),bytes(u.mem_read(0x20007810,96)),bytes(u.mem_read(0xe000ed04,4)),u.reg_read(UC_ARM_REG_PRIMASK),u.reg_read(UC_ARM_REG_BASEPRI))
 saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
 def call(name,args=(),ipsr=0):
  nonlocal comparisons
  outcomes=[]
  for u in (stock,candidate):
   u.reg_write(UC_ARM_REG_IPSR,ipsr);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
   for reg,value in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),args):u.reg_write(reg,value)
   for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
   u.emu_start((ENTRIES[name] if u is stock else syms[name])|1,0x20000100,count=2000000);assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)];outcomes.append((None if name=='vQueueDelete' else u.reg_read(UC_ARM_REG_R0),snapshot(u)))
  assert outcomes[0]==outcomes[1],(name,args,ipsr,[(i,str(a)[:200],str(b)[:200]) for i,(a,b) in enumerate(zip(outcomes[0],outcomes[1])) if a!=b]);comparisons+=1;return outcomes[0][0]
 try:
  for pattern,mask,length,item,static,send_irq,get_irq in itertools.product((0,0xa5),(0,1),(1,3),(1,4,17),(0,1),(0,33),(0,33)):
   for u in (stock,candidate):
    u.mem_write(0x20000000,baseline[id(u)]);u.mem_write(0x2001e588,bytes([pattern])*51200);u.mem_write(0x20002f00,bytes([0x93])*0x1300);u.mem_write(0x20002f00,struct.pack('<6I',0xfffffff0,0xffffffff,0x20003000,80,0x20003400,length*item));u.mem_write(0xe000ed04,bytes(4));u.mem_write(0xe000ed0c,bytes(4));u.reg_write(UC_ARM_REG_PRIMASK,mask);u.reg_write(UC_ARM_REG_BASEPRI,0)
   handle=call('osMessageQueueNew',(length,item,0x20002f00 if static else 0));assert handle==(0x20003000 if static else 0x2001e598)
   assert call('osMessageQueueGetCapacity',(handle,),get_irq)==length
   for round_index in range(2):
    assert call('osMessageQueueGetCount',(handle,),get_irq)==0
    for index in range(length):
     data=bytes((round_index*73+index*13+i)&255 for i in range(item))
     for u in (stock,candidate):u.mem_write(0x20004000,data)
     assert call('osMessageQueuePut',(handle,0x20004000,255,0),send_irq)==0
     assert call('osMessageQueueGetCount',(handle,),get_irq)==index+1
    assert call('osMessageQueuePut',(handle,0x20004000,0,0),send_irq)==0xfffffffd
    for index in range(length):
     assert call('osMessageQueueGet',(handle,0x20004100,0xfffffff0,0),get_irq)==0
     expected=bytes((round_index*73+index*13+i)&255 for i in range(item))
     for u in (stock,candidate):assert bytes(u.mem_read(0x20004100,item))==expected
     assert call('osMessageQueueGetCount',(handle,),get_irq)==length-index-1;messages+=1
    assert call('osMessageQueueGet',(handle,0x20004100,0,0),get_irq)==0xfffffffd
   call('vQueueDelete',(handle,));workflows+=1
   for u in (stock,candidate):assert word(u,0x20007800)==(0 if static else 51184)
 finally:
  for u in (stock,candidate):u.mem_write(0x20000000,baseline[id(u)]);u.reg_write(UC_ARM_REG_IPSR,0);u.reg_write(UC_ARM_REG_PRIMASK,0);u.reg_write(UC_ARM_REG_BASEPRI,0)
 receipt.write_text(json.dumps(dict(application_sha256=sha(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin'),board_report_sha256=sha(BASE/'board/report.json'),verification_driver_sha256=sha(ROOT/'r1/tools/verify_native_board.py'),queue_driver_sha256=sha(Path(__file__)),wrapper_report_sha256=sha(BASE/'rtos-message-queue/report.json'),receive_isr_report_sha256=sha(BASE/'rtos-queue-receive-isr/report.json'),comparisons=comparisons,workflows=workflows,messages_roundtripped_per_implementation=messages,provider_interception=False,heap_bytes_compared_per_call=51212,scope='Actual CMSIS queue creation/send/get/count/capacity, static/dynamic native queues, task/ISR send/receive, kernel query/critical, priority validator, native heap and movement; fill/full/empty/two-ring-round lifetimes and reclamation',limitations=['Controlled prekernel nonblocking queues have no waiters. IRQ/mask/MMIO values are fixtures; actual interrupt dispatch and blocking scheduling do not execute. Only authenticated heap caller LR is normalized. No hardware or image instruction equality proof.']),indent=2)+'\n');print(comparisons,'CMSIS queue graph comparisons;',workflows,'workflows;',messages,'messages per implementation')
if __name__=='__main__':raise SystemExit('Use verify_native_board.py --message-queue')
