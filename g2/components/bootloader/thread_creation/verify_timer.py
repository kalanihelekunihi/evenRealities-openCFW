#!/usr/bin/env python3
"""Stock static idle creation and scheduler setup, timer/SVC boundary explicit."""
import argparse,importlib.util,json,hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
spec=importlib.util.spec_from_file_location('runtime_v',HERE/'verify_runtime.py');r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r);v=r.v
v.ENTRIES['scheduler_bootstrap']=0x418148
class Machine(r.Machine):
 def __init__(self,*args,**kwargs):super().__init__(*args,**kwargs);self.timer_status=1
 def code(self,uc,pc,size,user):
  if pc==0x41b4f6:self.events.append(['port-start',self.u(0x20027150),self.u(0x20027164),self.u(0x20027148)]);self.ret();return
  super().code(uc,pc,size,user)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();assert v.sha(v.BLOB)==v.SHA
 _,segments,symbols=v.elf.elf_info(a.elf);trace={};cases=[]
 for timer in [0,0x20026da0]:
  for current in [0,0x20026ac0]:
   pair=[Machine(),Machine(True,segments,symbols)];results=[]
   for m in pair:
    m.w(0x20027180,timer);m.cpu.mem_write(0x200269e0,b"\xcc"*112);m.cpu.mem_write(0x200254d0,b"\xcc"*1024);m.cpu.mem_write(0x20026da0,b"\xcc"*80);m.w(0x200004c4,0xaaaaaaaa);m.w(0x200004c8,0x12345678);m.w(0x20027134,current);m.w(0x20027144,1 if current else 0);m.w(0x20027150,0);m.w(0x20027160,1);m.w(0x2002714c,48 if current else 0);m.w(0x20027164,123);m.w(0x20027148,456)
    if current:m.w(current+0x2c,48)
    for p in range(56):
     l=0x20024870+20*p;node=l+8;m.w(l,0);m.w(l+4,node);m.w(node,0xffffffff);m.w(node+4,node);m.w(node+8,node)
    m.cpu.mem_write(0x20026970,b'\xcc'*112);m.cpu.mem_write(0x200250d0,b'\xcc'*1024)
    ret=m.run('scheduler_bootstrap',[]);results.append(dict(ret=ret['return'],events=ret['events'],tcb=bytes(m.cpu.mem_read(0x20026970,112)).hex(),stack_sha=hashlib.sha256(m.cpu.mem_read(0x200250d0,1024)).hexdigest(),ready=bytes(m.cpu.mem_read(0x20024870,1120)).hex(),globals=bytes(m.cpu.mem_read(0x20027130,64)).hex(),timer_tcb=bytes(m.cpu.mem_read(0x200269e0,112)).hex(),timer_stack_sha=hashlib.sha256(m.cpu.mem_read(0x200254d0,1024)).hexdigest(),timer_queue=bytes(m.cpu.mem_read(0x20026da0,80)).hex(),timer_lists=bytes(m.cpu.mem_read(0x20026f98,40)).hex(),nesting=m.u(0x200004c4),basepri=m.cpu.reg_read(v.a.UC_ARM_REG_BASEPRI)))
   assert results[0]==results[1],(timer,current,results)
   assert results[0]['ret']==0x12345678;trace.update(pair[0].trace);cases.append(dict(timer_status=timer,current=current,result=results[0]))
 used={int(pc,0)+i for pc,b in trace.items() for i in range(len(bytes.fromhex(b)))}
 report=dict(status='PASS',cases=len(cases),distinct_original_trace_bytes=len(used),original_sha256=v.SHA,elf_sha256=v.sha(a.elf),source_sha256={str(p.relative_to(ROOT)):v.sha(p) for p in HERE.iterdir() if p.is_file()},original_trace=trace,comparisons=cases,limits=['Timer service creation, fresh static queue and nested critical paths execute. Port startup41b4f6 synthetic; no SVC/context transfer. Original fill41560c intercepted; source fills execute.','Actual static idle memory selection, idle thread creation/registration and scheduler state writes execute. Full idle TCB/stack/ready arrays/globals compared.','M4-compatible offline execution; not hardware, full scheduler, or byte-identical build. Fresh-queue specialization covers startup only; queue reuse/reset-wakeup and fatal malformed inputs not exercised.'])
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['status','cases','distinct_original_trace_bytes']}))
if __name__=='__main__':main()
