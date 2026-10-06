#!/usr/bin/env python3
"""Static create/init/registration in original and source with synthetic state."""
import argparse,importlib.util,json,struct,hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
spec=importlib.util.spec_from_file_location('static_v',HERE/'verify_static.py');s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s);t=s.t;v=s.v
class Machine(s.Machine):
 def code(self,uc,pc,size,user):
  providers={0x41b3e4:'enter',0x41b3fc:'exit',0x418a44:'lists-init',0x41b3d0:'reschedule'}
  if pc in providers:
   v.Machine.code(self,uc,pc,size,user);return
  if pc==0x417e58:
   v.Machine.code(self,uc,pc,size,user);return
  if pc==0x41602a:
   v.Machine.code(self,uc,pc,size,user);return
  if pc==0x41560c:
   dest,n,fill,_=self.args();uc.mem_write(dest,bytes([fill&255])*n);self.ret(dest);return
  v.Machine.code(self,uc,pc,size,user)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();assert v.sha(v.BLOB)==v.SHA
 _,segments,symbols=v.elf.elf_info(a.elf);trace={};cases=[]
 for priority in [1,24,48,55]:
  for running in [0,1]:
   for current in [0,0x20030300]:
    for count in [0,2]:
     pair=[Machine(),Machine(True,segments,symbols)];results=[]
     for m in pair:
      m.cpu.mem_write(t.ATTR,struct.pack('<9I',s.NAME,0,s.CB,112,s.STACK,1024,priority,1,0));m.cpu.mem_write(s.NAME,b'manager\0');m.cpu.mem_write(s.CB,b'\xcc'*112);m.cpu.mem_write(s.STACK,b'\xcc'*1024)
      m.w(0x200004c4,0);m.cpu.reg_write(v.a.UC_ARM_REG_BASEPRI,0);m.cpu.reg_write(v.a.UC_ARM_REG_PRIMASK,0);m.w(0x2002716c,0);m.w(0x20027134,current);m.w(0x20027144,count);m.w(0x20027150,running);m.w(0x20027160,0xffffffff);m.w(0x2002714c,24)
      if current:m.w(current+0x2c,24)
      for p in range(56):
       l=0x20024870+20*p;node=l+8;m.w(l,0);m.w(l+4,node);m.w(node,0xffffffff);m.w(node+4,node);m.w(node+8,node)
      r=m.run('thread_new',[0x42e2f9,0x1234,t.ATTR]);results.append(dict(ret=r['return'],events=r['events'],tcb=bytes(m.cpu.mem_read(s.CB,112)).hex(),stack_sha=hashlib.sha256(m.cpu.mem_read(s.STACK,1024)).hexdigest(),ready=bytes(m.cpu.mem_read(0x20024870,1120)).hex(),globals=bytes(m.cpu.mem_read(0x20027130,64)).hex(),delayed_lists=bytes(m.cpu.mem_read(0x20026f34,100)).hex(),nesting=m.u(0x200004c4),basepri=m.cpu.reg_read(v.a.UC_ARM_REG_BASEPRI),pendsv=m.u(0xe000ed04)))
     assert results[0]==results[1],(priority,running,current,count,results)
     trace.update(pair[0].trace);cases.append(dict(priority=priority,running=running,current=current,count=count,result=results[0]))
 used={int(pc,0)+i for pc,b in trace.items() for i in range(len(bytes.fromhex(b)))}
 report=dict(status='PASS',cases=len(cases),distinct_original_trace_bytes=len(used),original_sha256=v.SHA,elf_sha256=v.sha(a.elf),source_sha256={str(p.relative_to(ROOT)):v.sha(p) for p in HERE.iterdir() if p.is_file()},original_trace=trace,comparisons=cases,limits=['Context guard, critical nesting, BASEPRI writes, ready-list initialization and PendSV request execute in source and original; dynamic creation remains synthetic and is not reached. No actual scheduler switch/interrupt delivery.','Original fill41560c intercepted; source byte loops execute; full TCB/stack/ready arrays/globals compared.','M4-compatible offline execution, not hardware or byte identity.'])
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['status','cases','distinct_original_trace_bytes']}))
if __name__=='__main__':main()
