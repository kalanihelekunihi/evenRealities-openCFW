#!/usr/bin/env python3
"""Recoverable scheduler resume paths with coherent pending/delayed/ready lists."""
import argparse,importlib.util,json,itertools
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
spec=importlib.util.spec_from_file_location('resume_v',HERE/'verify_runtime.py');r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r);v=r.v
v.ENTRIES['scheduler_resume']=0x418228
class Machine(r.Machine):
 def __init__(self,*args,**kwargs):super().__init__(*args,**kwargs);self.tick_calls=0
 def code(self,uc,pc,size,user):
  if pc==0x418408:
   self.tick_calls+=1;value=self.tick_calls&1;self.events.append(['tick-provider',value]);self.ret(value);return
  super().code(uc,pc,size,user)
def attach(m,listaddr,item,owner,at_item):
 end=listaddr+8;m.w(listaddr,1);m.w(listaddr+4,item if at_item else end);m.w(listaddr+12,item);m.w(listaddr+16,item);m.w(item+4,end);m.w(item+8,end);m.w(item+12,owner);m.w(item+16,listaddr)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();assert v.sha(v.BLOB)==v.SHA
 _,segments,symbols=v.elf.elf_info(a.elf);symbols['opencfw_boot_scheduler_resume']=symbols['opencfw_bl_scheduler_resume'];trace={};cases=[]
 for suspended,priority,ticks,yielded,at_item,nesting in itertools.product([1,2],[23,24,48],[0,2],[0,1],[0,1],[0,0xaaaaaaaa]):
  pair=[Machine(),Machine(True,segments,symbols)];results=[]
  for m in pair:
   cb=0x20030000;current=0x20030080;delayed=0x20026f34;pending=0x20026f5c
   m.w(0x2002716c,suspended);m.w(0x20027144,2);m.w(0x20027134,current);m.w(current+44,24);m.w(0x2002714c,24);m.w(0x20027138,delayed);m.w(0x20027164,1000);m.w(0x20027154,ticks);m.w(0x20027158,yielded);m.w(0x200004c4,nesting);m.w(cb+44,priority);m.w(cb+4,1000)
   for p in range(56):
    l=0x20024870+p*20;end=l+8;m.w(l,0);m.w(l+4,end);m.w(l+8,0xffffffff);m.w(l+12,end);m.w(l+16,end)
   attach(m,delayed,cb+4,cb,at_item);attach(m,pending,cb+24,cb,at_item)
   ret=m.run('scheduler_resume',[]);results.append(dict(ret=ret['return'],events=ret['events'],tcb=bytes(m.cpu.mem_read(cb,112)).hex(),ready=bytes(m.cpu.mem_read(0x20024870,1120)).hex(),lists=bytes(m.cpu.mem_read(0x20026f34,100)).hex(),globals=bytes(m.cpu.mem_read(0x20027130,64)).hex(),nesting=m.u(0x200004c4),basepri=m.cpu.reg_read(v.a.UC_ARM_REG_BASEPRI),pendsv=m.u(0xe000ed04)))
  assert results[0]==results[1],(suspended,priority,ticks,yielded,at_item,nesting,results)
  if suspended==1:assert pair[0].u(0x20026f5c)==0 and pair[0].u(0x20027164)==0xffffffff
  trace.update(pair[0].trace);cases.append(dict(suspended=suspended,priority=priority,ticks=ticks,yielded=yielded,at_item=at_item,nesting=nesting,result=results[0]))
 used={int(pc,0)+i for pc,b in trace.items() for i in range(len(bytes.fromhex(b)))}
 report=dict(status='PASS',cases=len(cases),distinct_original_trace_bytes=len(used),original_sha256=v.SHA,elf_sha256=v.sha(a.elf),source_sha256={str(p.relative_to(ROOT)):v.sha(p) for p in HERE.iterdir() if p.is_file()},original_trace=trace,comparisons=cases,limits=['Actual pending/delayed removal, ready insertion, cursor repair, unblock refresh, nesting/BASEPRI and PendSV request execute. Deferred tick418408 synthetic return sequence1/0; real tick effects not modeled.','Coherent one pending task/one current task synthetic lists. Empty-task branch, zero-suspension fatal assertion and concurrent IRQ mutations not covered.','M4-compatible original/source comparison; no actual scheduling/hardware/exact build claim.'])
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['status','cases','distinct_original_trace_bytes']}))
if __name__=='__main__':main()
