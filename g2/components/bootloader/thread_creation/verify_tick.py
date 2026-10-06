#!/usr/bin/env python3
"""Tick expiration, optional event removal, overflow-list swap, timeslicing."""
import argparse,importlib.util,json,itertools
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
spec=importlib.util.spec_from_file_location('tick_v',HERE/'verify_resume.py');r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r);v=r.v;v.ENTRIES['tick_increment']=0x418408
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();assert v.sha(v.BLOB)==v.SHA
 _,segments,symbols=v.elf.elf_info(a.elf);symbols['opencfw_boot_tick_increment']=symbols['opencfw_bl_tick_increment'];trace={};cases=[]
 for suspended,priority,tick,deadline,event,ready_count,yielded in itertools.product([0,1],[23,24,48],[9,0xffffffff],[0,10,11],[0,1],[1,2],[0,1]):
  pair=[v.Machine(),v.Machine(True,segments,symbols)];results=[]
  for m in pair:
   current=0x20030080;cb=0x20030000;delayed=0x20026f34;overflow=0x20026f48;wait=0x20026f70
   m.w(0x2002716c,suspended);m.w(0x20027148,tick);m.w(0x20027138,delayed);m.w(0x2002713c,overflow);m.w(0x20027164,deadline if tick!=0xffffffff else 0xffffffff);m.w(0x20027154,7);m.w(0x2002715c,0);m.w(0x20027158,yielded);m.w(0x20027134,current);m.w(current+44,24);m.w(cb+44,priority);m.w(cb+4,deadline);m.w(0x2002714c,24)
   for l in [delayed,overflow,wait]+[0x20024870+p*20 for p in range(56)]:
    end=l+8;m.w(l,0);m.w(l+4,end);m.w(l+8,0xffffffff);m.w(l+12,end);m.w(l+16,end)
   active=overflow if tick==0xffffffff else delayed;r.attach(m,active,cb+4,cb,1)
   if event:r.attach(m,wait,cb+24,cb,1)
   else:m.w(cb+40,0)
   ready=0x20024870+24*20;r.attach(m,ready,current+4,current,0)
   if ready_count==2:
    extra=0x20030200;node=extra+4;end=ready+8
    m.w(ready,2);m.w(end+8,node);m.w(current+8,node)
    m.w(node+4,end);m.w(node+8,current+4);m.w(node+12,extra);m.w(node+16,ready)
   ret=m.run('tick_increment',[]);results.append(dict(ret=ret['return'],tcb=bytes(m.cpu.mem_read(cb,112)).hex(),current=bytes(m.cpu.mem_read(current,112)).hex(),ready=bytes(m.cpu.mem_read(0x20024870,1120)).hex(),lists=bytes(m.cpu.mem_read(0x20026f34,100)).hex(),globals=bytes(m.cpu.mem_read(0x20027130,64)).hex()))
  assert results[0]==results[1],(suspended,priority,tick,deadline,event,ready_count,yielded,results)
  trace.update(pair[0].trace);cases.append(dict(suspended=suspended,priority=priority,tick=tick,deadline=deadline,event=event,ready_count=ready_count,yielded=yielded,result=results[0]))
 used={int(pc,0)+i for pc,b in trace.items() for i in range(len(bytes.fromhex(b)))}
 report=dict(status='PASS',cases=len(cases),distinct_original_trace_bytes=len(used),original_sha256=v.SHA,elf_sha256=v.sha(a.elf),source_sha256={str(p.relative_to(ROOT)):v.sha(p) for p in HERE.iterdir() if p.is_file()},original_trace=trace,comparisons=cases,limits=['Synthetic coherent delayed/event/current/second-ready task lists. No providers on valid tested paths.','Actual tick, overflow swap/unblock refresh, removal/cursor repair, ready insertion, deferred tick accumulation and yield decision execute. Multiple simultaneous wake tasks and malformed wrap/fatal paths not covered.','Values are ticks, not milliseconds; no hardware clock/IRQ/actual scheduler delivery or byte identity.'])
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['status','cases','distinct_original_trace_bytes']}))
if __name__=='__main__':main()
