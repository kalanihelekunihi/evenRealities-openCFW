#!/usr/bin/env python3
"""Actual wrapper/dynamic creation, first/second allocation failure cleanup."""
import argparse,importlib.util,json,struct,hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
spec=importlib.util.spec_from_file_location('dynamic_v',HERE/'verify_runtime.py');r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r);v=r.v
class Machine(r.Machine):
 def __init__(self,*args,**kwargs):super().__init__(*args,**kwargs);self.allocation_mode='success';self.calls=0
 def code(self,uc,pc,size,user):
  if pc==0x419730:
   self.calls+=1;size=self.args()[0];ret=(r.s.STACK if self.calls==1 else r.s.CB)
   if (self.allocation_mode=='fail-stack' and self.calls==1) or (self.allocation_mode=='fail-tcb' and self.calls==2):ret=0
   self.events.append(['allocate',size,ret]);self.ret(ret);return
  if pc==0x419830:self.events.append(['free',self.args()[0]]);self.ret();return
  super().code(uc,pc,size,user)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();assert v.sha(v.BLOB)==v.SHA
 _,segments,symbols=v.elf.elf_info(a.elf);trace={};cases=[]
 for mode in ['success','fail-stack','fail-tcb']:
  for stack_bytes in [1024,1027,0x40100]:
   for name in [0,r.s.NAME]:
    pair=[Machine(),Machine(True,segments,symbols)];results=[]
    for m in pair:
     m.allocation_mode=mode;m.w(0x20027150,0);m.w(0x20027144,0);m.w(0x20027134,0);m.w(0x200004c4,0);m.cpu.mem_write(r.t.ATTR,struct.pack('<9I',name,0,0,0,0,stack_bytes,24,0,0));m.cpu.mem_write(r.s.NAME,b'a'*40+b'\0');m.cpu.mem_write(r.s.CB,b'\xcc'*112);m.cpu.mem_write(r.s.STACK,b'\xcc'*1024)
     ret=m.run('thread_new',[0x42e2f9,0x1234,r.t.ATTR]);results.append(dict(ret=ret['return'],events=ret['events'],tcb=bytes(m.cpu.mem_read(r.s.CB,112)).hex(),stack_sha=hashlib.sha256(m.cpu.mem_read(r.s.STACK,1024)).hexdigest(),ready=bytes(m.cpu.mem_read(0x20024870,1120)).hex(),globals=bytes(m.cpu.mem_read(0x20027130,64)).hex()))
    assert results[0]==results[1],(mode,stack_bytes,name,results)
    assert results[0]['ret']==(r.s.CB if mode=='success' else 0)
    if mode=='fail-tcb':assert results[0]['events'][-1]==['free',r.s.STACK]
    if mode=='success' and name:assert bytes.fromhex(results[0]['tcb'])[0x34:0x54]==b'a'*31+b'\0'
    trace.update(pair[0].trace);cases.append(dict(mode=mode,stack_bytes=stack_bytes,name=name,result=results[0]))
 used={int(pc,0)+i for pc,b in trace.items() for i in range(len(bytes.fromhex(b)))}
 report=dict(status='PASS',cases=len(cases),distinct_original_trace_bytes=len(used),original_sha256=v.SHA,elf_sha256=v.sha(a.elf),source_sha256={str(p.relative_to(ROOT)):v.sha(p) for p in HERE.iterdir() if p.is_file()},original_trace=trace,comparisons=cases,limits=['RTOS heap allocate419730/free419830 synthetic. Actual dynamic creation/failure cleanup/initializer/frame/ready lists/registration/critical state execute.','Original fill41560c intercepted; source loops execute. No real heap exhaustion, task execution, IRQ or hardware behavior. M4 compatibility.'])
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['status','cases','distinct_original_trace_bytes']}))
if __name__=='__main__':main()
