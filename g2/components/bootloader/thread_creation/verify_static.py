#!/usr/bin/env python3
"""Wrapper/static TCB/frame comparison. Registration remains synthetic."""
import argparse,importlib.util,json,struct,hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
spec=importlib.util.spec_from_file_location('creator',HERE/'verify.py');t=importlib.util.module_from_spec(spec);spec.loader.exec_module(t);v=t.v
CB=0x20030080;STACK=0x20010000;NAME=0x20030100
class Machine(t.Machine):
 def code(self,uc,pc,size,user):
  if pc==0x41560c:
   dest,n,fill,_=self.args();uc.mem_write(dest,bytes([fill&255])*n);self.ret(dest);return
  if pc==0x417e58:
   self.events.append(['register',self.args()[0]]);self.ret();return
  if pc==0x41b2f8:raise AssertionError('unexpected fatal path')
  if pc==0x417c7c:
   v.Machine.code(self,uc,pc,size,user);return
  super().code(uc,pc,size,user)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();assert v.sha(v.BLOB)==v.SHA
 _,segments,symbols=v.elf.elf_info(a.elf);trace={};cases=[]
 for priority in [1,24,48,55]:
  for n in [128,257,4096]:
   for name in [b'',b'manager\0',b'x'*40+b'\0']:
    pair=[Machine(),Machine(True,segments,symbols)];results=[]
    for m in pair:
     attr=[NAME,0,CB,112,STACK,n*4,priority,1,0];m.cpu.mem_write(t.ATTR,struct.pack('<9I',*attr));m.cpu.mem_write(NAME,name or b'\0');m.cpu.mem_write(CB,b'\xcc'*112);m.cpu.mem_write(STACK,b'\xcc'*(n*4))
     r=m.run('thread_new',[0x42e2f9,0x1234,t.ATTR]);results.append(dict(ret=r['return'],events=r['events'],tcb=bytes(m.cpu.mem_read(CB,112)).hex(),stack_sha=hashlib.sha256(m.cpu.mem_read(STACK,n*4)).hexdigest()))
    assert results[0]==results[1],(priority,n,name,results)
    assert results[0]['ret']==CB;trace.update(pair[0].trace);cases.append(dict(priority=priority,words=n,name=name.hex(),result=results[0]))
 used={int(pc,0)+i for pc,b in trace.items() for i in range(len(bytes.fromhex(b)))}
 report=dict(status='PASS',cases=len(cases),distinct_original_trace_bytes=len(used),original_sha256=v.SHA,elf_sha256=v.sha(a.elf),source_sha256={str(p.relative_to(ROOT)):v.sha(p) for p in HERE.iterdir() if p.is_file()},original_trace=trace,comparisons=cases,limits=['Context guard, dynamic creator, and registration synthetic. Original 41560c fill intercepted; source byte loops execute. TCB and complete stack byte hashes compared.','Only valid static attributes; fatal priority/null stack assertions not covered here.','M4-compatible offline execution; no task scheduling, hardware, exact-build or source completeness claim.'])
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['status','cases','distinct_original_trace_bytes']}))
if __name__=='__main__':main()
