#!/usr/bin/env python3
"""Bounded ready-list selection, sentinel skip and circular history."""
import argparse,importlib.util,json
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
spec=importlib.util.spec_from_file_location('select_v',ROOT/'g2/components/bootloader/update_core/verify.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v);v.ENTRIES['thread_select']=0x418570
class Machine(v.Machine):
 def code(self,uc,pc,size,user):
  if pc==0x41b600:raise AssertionError('unmodeled overflow path')
  super().code(uc,pc,size,user)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();assert v.sha(v.BLOB)==v.SHA
 _,segments,symbols=v.elf.elf_info(a.elf);trace={};cases=[]
 for suspended in [0,1]:
  for index in [0,63]:
   for cursor in ['sentinel','first','second']:
    for max_priority in [24,55]:
     pair=[Machine(),Machine(True,segments,symbols)];results=[]
     for m in pair:
      cbs=[0x20030000,0x20030080];nodes=[p+4 for p in cbs];listaddr=0x20024870+24*20;end=listaddr+8
      m.w(0x20027134,cbs[0]);m.w(0x2002716c,suspended);m.w(0x20027158,0xcc);m.w(0x20027170,index);m.w(0x2002714c,max_priority);m.cpu.mem_write(0x20026500,b'\xcc'*512)
      for p in range(56):m.w(0x20024870+20*p,0)
      m.w(listaddr,2);m.w(listaddr+4,dict(sentinel=end,first=nodes[0],second=nodes[1])[cursor]);m.w(end+4,nodes[0]);m.w(end+8,nodes[1])
      for i,cb in enumerate(cbs):
       m.w(cb+0x30,0x20031000+i*0x100);m.cpu.mem_write(0x20031000+i*0x100,b'\xa5'*16);m.w(cb+0x58,10+i);m.w(cb+0x10,cb)
       m.w(nodes[i]+4,nodes[1] if i==0 else end);m.w(nodes[i]+8,end if i==0 else nodes[0])
      m.run('thread_select',[]);results.append(dict(current=m.u(0x20027134),pending=m.u(0x20027158),priority=m.u(0x2002714c),index=m.u(0x20027170),history=bytes(m.cpu.mem_read(0x20026500,512)).hex(),list=bytes(m.cpu.mem_read(listaddr,20)).hex()))
     assert results[0]==results[1],(suspended,index,cursor,max_priority,results)
     trace.update(pair[0].trace);cases.append(dict(suspended=suspended,index=index,cursor=cursor,max_priority=max_priority,result=results[0]))
 used={int(pc,0)+i for pc,b in trace.items() for i in range(len(bytes.fromhex(b)))}
 report=dict(status='PASS',cases=len(cases),distinct_original_trace_bytes=len(used),original_sha256=v.SHA,elf_sha256=v.sha(a.elf),source_sha256={str(p.relative_to(ROOT)):v.sha(p) for p in HERE.iterdir() if p.is_file()},original_trace=trace,comparisons=cases,limits=['Synthetic coherent circular ready lists with two tasks and intact A5 stack guard. Stack-overflow/nonreturn path and empty-all-lists fatal path not covered.','No providers reached on valid paths; actual instruction selection/history logic compared. No context restoration, SVC/PendSV dispatch, hardware or byte identity.'])
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['status','cases','distinct_original_trace_bytes']}))
if __name__=='__main__':main()
