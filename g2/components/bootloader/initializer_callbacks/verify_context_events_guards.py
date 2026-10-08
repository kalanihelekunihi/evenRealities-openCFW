#!/usr/bin/env python3
"""Additional independent guard/retention and synthetic busy->idle fixtures."""
import argparse,hashlib,importlib.util,json
from pathlib import Path
spec=importlib.util.spec_from_file_location('events',Path(__file__).with_name('verify_context_events.py'));v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
class Machine(v.Machine):
 def memread(self,uc,access,address,size,value,user):
  if getattr(self,'busy_transition',False) and address==v.IOM+0x248:
   self.busy_reads+=1;state=2 if self.busy_reads==1 else 4;self.w(address,state);self.events.append(['synthetic-busy-state',self.busy_reads,state])
  super().memread(uc,access,address,size,value,user)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args();assert hashlib.sha256(v.v.v.v.BLOB.read_bytes()).hexdigest()==v.v.v.v.LOCKED_SHA;_,segs,syms=v.v.v.v.elf.elf_info(args.elf);rows=[];trace={}
 fixtures=[('cqstatus',[v.Q,v.v.CFG],0),('cqresume',[0],None),('cqresume',[v.Q],0),('cqresume',[v.Q],0x01cdcdcd),('service',[v.H,1],0)]
 fixtures.extend([('descriptor-mode2',[v.H,1],None),('rx-busy',[v.H,0x800],None),('cqstatus-flags',[v.Q,v.v.CFG],None),('cqstatus-wrap',[v.Q,v.v.CFG],None),('cqstatus-partial',[v.Q,v.v.CFG],None)])
 for entry,values,flags in fixtures:
  results=[]
  for source in [False,True]:
   m=Machine(source,segs,syms);m.setup()
   if entry.startswith('cq') or entry=='service':m.queue(0,3)
   if flags is not None:m.w(v.Q,flags)
   if entry=='cqstatus-flags':
    ops=m.r(v.Q+0x24);m.w(m.r(ops+0x18),m.r(ops+0x1c)|m.r(ops+0x20)|m.r(ops+0x24));name='cqstatus'
   elif entry=='cqstatus-partial':m.w(v.Q+0x14,v.v.BUFFER+8);name='cqstatus'
   elif entry=='cqstatus-wrap':
    ops=m.r(v.Q+0x24);m.w(v.Q+0x20,256);m.w(m.r(ops+8),128);name='cqstatus'
   elif entry=='descriptor-mode2':m.cpu.mem_write(v.H+0x83c,b'\1');m.cpu.mem_write(v.H+0x82c,b'\2');m.w(v.H+0x840,1);name='service'
   elif entry=='rx-busy':m.drain=True;m.busy_transition=True;m.busy_reads=0;m.w(v.IOM+0x218,0);m.w(v.IOM+0x100,4<<16);name='apply'
   else:name=entry
   status=m.call(name,values);result=m.observation([] if name=='apply' else [status]);results.append(result)
   if entry=='descriptor-mode2':assert result['event_state']['descriptor_callbacks'][1]==0
   if not source:trace.update(m.trace)
  assert results[0]==results[1],(entry,flags,results);rows.append(dict(entry=entry,flags=flags,observation=results[0]))
 report=dict(status='PASS',cases=len(rows),elf_sha256=hashlib.sha256(args.elf.read_bytes()).hexdigest(),original_trace={hex(pc):raw for pc,raw in trace.items()},comparisons=rows,limits=['Queue invalid/disabled and NULL guards, descriptor callback clearing with mode2 and a synthetic busy->idle FIFO transition.','Busy state is an explicit two-read fixture; not observed peripheral progress, elapsed time or IRQ delivery.'])
 args.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['status','cases']}))
if __name__=='__main__':main()
