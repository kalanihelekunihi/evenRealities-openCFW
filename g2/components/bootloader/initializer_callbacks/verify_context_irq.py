#!/usr/bin/env python3
"""IRQ status/clear/dispatch stock/source; optional explicit synthetic W1C."""
import argparse,hashlib,importlib.util,itertools,json
from pathlib import Path
spec=importlib.util.spec_from_file_location('events',Path(__file__).with_name('verify_context_events.py'));v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
v.v.v.ENTRIES.update(irqget=('opencfw_boot_iom_interrupt_status',0x42c672),irqclear=('opencfw_boot_iom_interrupt_clear',0x42c6b6),irqdispatch=('opencfw_boot_iom4_irq_dispatch',0x430610))
class Machine(v.Machine):
 def __init__(self,source,segments,symbols):super().__init__(source,segments,symbols);self.ack=False
 def memread(self,uc,access,address,size,value,user):
  if address in [v.IOM+0x200,v.IOM+0x204]:self.events.append(['register-read',address,size])
  super().memread(uc,access,address,size,value,user)
 def memwrite(self,uc,access,address,size,value,user):
  super().memwrite(uc,access,address,size,value,user)
  if address==v.IOM+0x208:
   self.events.append(['register-clear-write',address,value&0xffffffff])
   if self.ack:uc.mem_write(v.IOM+0x204,(self.r(v.IOM+0x204)&~value&0xffffffff).to_bytes(4,'little'))
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args();blob=v.v.v.v.BLOB.read_bytes();assert hashlib.sha256(blob).hexdigest()==v.v.v.v.LOCKED_SHA;_,segs,syms=v.v.v.v.elf.elf_info(args.elf);rows=[];trace={}
 def compare(kind,params,prepare,entry,values):
  results=[]
  for source in [False,True]:
   m=Machine(source,segs,syms);m.setup();prepare(m);status=m.call(entry,values);results.append(m.observation([] if entry=='irqdispatch' else [status]));
   if not source:trace.update(m.trace)
  assert results[0]==results[1],(kind,params,results);rows.append(dict(kind=kind,parameters=params,observation=results[0]))
 for enabled,status,mask in itertools.product([0,1,255,256,257],[0,1,4,0x801,0x4a7c,0xffffffff],[0,1,0xff,0xffffffff]):
  def prep(m):m.w(v.IOM+0x204,status);m.w(v.IOM+0x200,mask)
  compare('status',[enabled,status,mask],prep,'irqget',[v.H,enabled,v.v.CFG])
 for handle,output,flags in [(0,v.v.CFG,0),(v.H,v.v.CFG,0),(v.H,0,0x01123456),(v.H,v.v.CFG,0xff123456)]:
  compare('get-guard',[handle,output,flags],lambda m:m.w(v.H,flags),'irqget',[handle,1,output])
 for handle,flags,ack,status in itertools.product([0,v.H],[0,0x01123456],[False,True],[0,4,0xffffffff]):
  def prep(m):m.w(v.H,flags);m.w(v.IOM+0x204,0xffffffff);m.ack=ack
  compare('clear',[handle,flags,ack,status],prep,'irqclear',[handle,status])
 for handle,events,mask,ack,mode in itertools.product([0,v.H],[0,1,4,0x800],[0,1,0xffffffff],[False,True],['idle','descriptor','cq']):
  def prep(m):
   m.w(0x200003b8,handle);m.w(v.IOM+0x204,events);m.w(v.IOM+0x200,mask);m.ack=ack
   if mode=='descriptor':m.cpu.mem_write(v.H+0x83c,b'\1');m.w(v.H+0x840,1)
   if mode=='cq':m.queue(1,1);m.w(v.IOM+0x204,events);m.w(v.IOM+0x200,mask)
  compare('dispatch',[handle,events,mask,ack,mode],prep,'irqdispatch',[])
 report=dict(status='PASS',cases=len(rows),elf_sha256=hashlib.sha256(args.elf.read_bytes()).hexdigest(),original_sha256=hashlib.sha256(blob).hexdigest(),original_trace={hex(pc):raw for pc,raw in trace.items()},comparisons=rows,limits=['Wrapper called as a function; no exception entry/return stack, NVIC delivery or vector resolution proof.','RAM and explicitly synthetic W1C variants; ordered status/enable reads, clear writes and readback compared. Callback/delay/FIFO boundaries inherit the asynchronous test model.','Only module4 dispatch route tested; helper module bounds are absent in stock and not invented. Clear/service return statuses are ignored by original wrapper.'])
 args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['status','cases']}))
if __name__=='__main__':main()
