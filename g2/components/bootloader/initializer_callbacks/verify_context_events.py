#!/usr/bin/env python3
"""Original/source asynchronous IOM paths with explicit synthetic MMIO/callbacks."""
import argparse,hashlib,importlib.util,itertools,json,struct
from pathlib import Path
from unicorn import arm_const as a
from unicorn import UC_HOOK_MEM_READ
spec=importlib.util.spec_from_file_location('children',Path(__file__).with_name('verify_context_children.py'));v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
H=v.v.POOL+4*v.v.STRIDE;IOM=0x40054000;Q=v.QUEUE+4*44;CALLBACK=0x08000100
EXTRA={'publish':('opencfw_boot_iom_descriptor_publish',0x42c45a),'classify':('opencfw_boot_iom_error_classify',0x42c076),'apply':('opencfw_boot_iom_event_apply',0x42c0b2),'service':('opencfw_boot_iom_event_service',0x42c6f8),'cqstatus':('opencfw_boot_iom_cq_status',0x427a56),'cqresume':('opencfw_boot_iom_cq_resume',0x427b38)}
v.v.ENTRIES.update(EXTRA)
class Machine(v.Machine):
 def __init__(self,source,segments,symbols):
  super().__init__(source,segments,symbols);self.callback_effect='none';self.debug_count=0;self.cpu.mem_write(CALLBACK,b'\x70\x47');self.cpu.hook_add(UC_HOOK_MEM_READ,self.memread,begin=IOM,end=IOM+0xfff);self.drain=False
  self.cuts[(symbols['opencfw_boot_delay_us_math']&~1) if source else 0x41d1c0]=('delay-math',1)
 def code(self,uc,pc,size,user):
  if pc==CALLBACK+2 and self.callback_effect=="reenter":
   self.events.append(["synthetic-reentry",H,self.reentry_event]);uc.reg_write(a.UC_ARM_REG_R0,H);uc.reg_write(a.UC_ARM_REG_R1,self.reentry_event);return
  if pc==CALLBACK:
   self.events.append(['callback',uc.reg_read(a.UC_ARM_REG_R0),uc.reg_read(a.UC_ARM_REG_R1)])
   if self.callback_effect=='stop':uc.mem_write(H+0x834,b'\1')
   if self.callback_effect=='mode2':uc.mem_write(H+0x82c,b'\2')
   if self.callback_effect=='replace':uc.mem_write(H+0x28+4,struct.pack('<I',CALLBACK+0x101))
   uc.reg_write(a.UC_ARM_REG_R0,0);return
  if CALLBACK<=pc<CALLBACK+12:return # synthetic callback instructions excluded from stock trace
  super().code(uc,pc,size,user)
 def memread(self,uc,access,address,size,value,user):
  if self.drain and address==IOM+0x108:
   level=(self.r(IOM+0x100)>>16)&255;self.events.append(["fifo-pop",level]);self.w(IOM+0x100,max(0,level-4)<<16)
 def observation(self,status):
  result=super().observation(status);result["status_buffer"]=bytes(self.cpu.mem_read(v.CFG,16)).hex();result["event_state"]={"cq_head":self.r(H+0x1c),"cq_pending":self.r(H+0x24),"descriptor_head":self.r(H+0x850),"descriptor_pending":self.r(H+0x840),"descriptor_active":self.cpu.mem_read(H+0x83c,1)[0],"callback_mode":self.cpu.mem_read(H+0x82c,1)[0],"stop_flag":self.cpu.mem_read(H+0x834,1)[0],"descriptor_callbacks":[self.r(v.BUFFER+i*32+24) for i in range(4)],"cq_callbacks":[self.r(H+0x28+i*4) for i in [0,1,2,3,255]],"primask":self.cpu.reg_read(a.UC_ARM_REG_PRIMASK)};return result
 def call(self,entry,args):
  self.cpu.reg_write(a.UC_ARM_REG_XPSR,0x01000000);return super().call(entry,args)
 def w(self,p,n):self.cpu.mem_write(p,struct.pack('<I',n&0xffffffff))
 def r(self,p):return struct.unpack('<I',self.cpu.mem_read(p,4))[0]
 def setup(self):
  self.reset();self.callback_effect='none';self.cpu.mem_write(v.CFG,b'\xcc'*16);self.debug_count=0;self.cpu.mem_write(H,b'\0'*v.v.STRIDE);self.handle(4)
  self.cpu.mem_write(IOM,b'\0'*0x1000);self.w(IOM+0x248,4);self.w(IOM+0x100,4<<8);self.w(IOM+0x200,0x12345678)
  self.w(H+0x14,0x11223344);self.w(H+0x848,4);self.w(H+0x854,v.BUFFER)
  for i in range(4):
   for word in range(6):self.w(v.BUFFER+i*32+word*4,0x81000000+i*0x100+word)
   self.w(v.BUFFER+i*32+24,CALLBACK|1);self.w(v.BUFFER+i*32+28,0xcafe0000+i)
  self.events.clear();self.state_writes.clear();self.writes.clear()
 def queue(self,completed,pending=3,head=0):
  self.call('cqinit',[H,16,v.BUFFER]);self.w(IOM+0x22c,v.BUFFER);self.w(H+0x24,pending);self.call('cqon',[H]);ops=self.r(Q+0x24)
  self.w(Q+0x20,completed+3);self.w(self.r(ops+8),completed);self.w(self.r(ops+4),v.BUFFER);self.w(v.BUFFER,self.r(ops+8)|1)
  self.w(H+0x1c,head)
  for slot in range(256):self.w(H+0x28+slot*4,CALLBACK|1);self.w(H+0x428+slot*4,0xbabe0000+slot)
  self.events.clear();self.state_writes.clear();self.writes.clear()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args();assert hashlib.sha256(v.v.v.BLOB.read_bytes()).hexdigest()==v.v.v.LOCKED_SHA;_,segments,symbols=v.v.v.elf.elf_info(args.elf);machines=[Machine(False,segments,symbols),Machine(True,segments,symbols)];cases=[];all_trace={}
 def compare(label,params,prepare,entry,values):
  results=[]
  for m in [Machine(False,segments,symbols),Machine(True,segments,symbols)]:
   m.setup();prepare(m)
   try:status=m.call(entry,values)
   except Exception as error:raise AssertionError((label,params,m.source,hex(m.cpu.reg_read(a.UC_ARM_REG_PC)),hex(m.r(Q+0x24)),bytes(m.cpu.mem_read(v.BUFFER,32)).hex(),m.events[-4:])) from error
   results.append(m.observation([status] if entry not in ['publish','apply'] else []))
   if not m.source:all_trace.update(m.trace)
  assert results[0]==results[1],(label,params,results);cases.append(dict(kind=label,parameters=params,observation=results[0]))
 for capacity,head in itertools.product([0,1,4],[0,1,3,0xffffffff]):
  def prep(m):m.w(H+0x848,capacity);m.w(H+0x850,head)
  compare('publisher',[capacity,head],prep,'publish',[H])
 for events,registered in itertools.product([0,1,4,8,0x10,0x20,0x40,0x200,0x800,0x4000,0x4800,0x4a7c],[0,4,0x10,0x200,0x4000]):
  compare('classify',[events,registered],lambda m:m.w(IOM+0x204,registered),'classify',[4,events])
 for event,remaining in itertools.product([0,0x10,0x200,0x800,0xa10],[0,1,4,5,9]):
  def prep(m):m.w(IOM+0x218,2);m.w(IOM+0x21c,remaining);m.w(H+0x864,7)
  compare('event-apply-tx',[event,remaining],prep,'apply',[H,event])
 for active,pending,event,dma in itertools.product([0,1],[1,2],[0,1,0x800,0x801,4,0x10,0x200,0x4000],[0,1]):
  def prep(m):m.cpu.mem_write(H+0x83c,bytes([active]));m.w(H+0x840,pending);m.w(IOM+0x218,dma)
  compare('descriptor-service',[active,pending,event,dma],prep,'service',[H,event])
 for completed,pending,event,mode,effect in itertools.product([0,1,3],[1,3,256],[0,4,0x10,0x200,0x4000],[0,2],['none','stop','mode2','replace']):
  if completed>pending:continue
  def prep(m):m.queue(completed,pending);m.cpu.mem_write(H+0x82c,bytes([mode]));m.callback_effect=effect
  compare('cq-service',[completed,pending,event,mode,effect],prep,'service',[H,event])
 for completed,head,pending,mode in itertools.product([256,257],[255],[1,3],[0,2]):
  def prep(m):m.queue(completed,pending,head);m.cpu.mem_write(H+0x82c,bytes([mode]))
  compare('cq-counter-wrap',[completed,head,pending,mode],prep,'service',[H,0])
 for kind in ['direct','linear','jump']:
  def prep(m):
   m.queue(0,3);ops=m.r(Q+0x24)
   if kind=='linear':m.w(v.BUFFER,0x40050000);m.w(v.BUFFER+8,m.r(ops+8)|1)
   if kind=='jump':m.w(v.BUFFER,m.r(ops+4));m.w(v.BUFFER+4,v.BUFFER+64);m.w(v.BUFFER+64,m.r(ops+8)|1)
  compare('cq-resume-chain',[kind],prep,'cqresume',[Q])
 for queue,out in [(0,v.CFG),(Q,0),(Q,v.CFG)]:
  def prep(m):m.queue(1,3)
  compare('cq-status-guards',[queue,out],prep,'cqstatus',[queue,out])
 for level in [0,4,8,12]:
  def prep(m):m.drain=True;m.w(IOM+0x218,0);m.w(IOM+0x100,level<<16)
  compare('event-apply-rx',[level],prep,'apply',[H,0x800])
 for kind in ['descriptor','cq']:
  def prep(m):
   m.callback_effect='reenter';m.reentry_event=1 if kind=='descriptor' else 0
   entry=m.symbols['opencfw_boot_iom_event_service'] if m.source else 0x42c6f9
   m.cpu.mem_write(CALLBACK,bytes.fromhex('10b500bf014b984710bd00bf')+struct.pack('<I',entry|1))
   if kind=='descriptor':
    m.cpu.mem_write(H+0x83c,b'\1');m.w(H+0x840,1);m.w(v.BUFFER+2*32+24,0)
   else:m.queue(3,3)
  compare('synthetic-callback-reentry',[kind],prep,'service',[H,1 if kind=='descriptor' else 0])
 for handle,flags,pending in [(0,0,0),(H,0,1),(H,0x01123456,0),(H,0x01123456,1)]:
  def prep(m):m.w(H,flags);m.w(H+0x24,pending)
  compare('service-guard',[handle,flags,pending],prep,'service',[handle,1])
 trace={hex(pc):raw for pc,raw in all_trace.items()};report=dict(status='PASS',cases=len(cases),elf_sha256=hashlib.sha256(args.elf.read_bytes()).hexdigest(),original_sha256=v.v.v.LOCKED_SHA,original_trace=trace,comparisons=cases,limits=['Fresh emulator for each fixture; MMIO is RAM and FIFO RX levels are explicitly synthetic. Callbacks are controlled ABI stubs; nested callback executes a synthetic call stub into actual stock/source service. Delay helper is cut; no hardware delivery or real callback body proof.','Native CQ status/resume, publisher, event/classifier and service bodies execute; ordinary CQ enable/disable also execute.','No heap allocation/free in this function family. Queue-full/allocation rejection belong to untested submission paths. Unbounded polls/command scans require stated finite fixtures.'])
 args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['status','cases']}))
if __name__=='__main__':main()
