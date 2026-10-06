#!/usr/bin/env python3
"""Dynamic creator executes recovered RTOS heap and suspend/resume wrappers."""
import argparse,importlib.util,json,struct,hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
spec=importlib.util.spec_from_file_location('owned_heap_v',HERE/'verify_runtime.py');r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r);v=r.v
class Machine(r.Machine):
 def code(self,uc,pc,size,user):
  if pc==0x418408:raise AssertionError('unexpected deferred tick')
  if pc==0x41b5f6:self.events.append(['malloc-failed']);self.finished=True;uc.emu_stop();return
  super().code(uc,pc,size,user)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();assert v.sha(v.BLOB)==v.SHA
 _,segments,symbols=v.elf.elf_info(a.elf);pair=[Machine(),Machine(True,segments,symbols)];trace={};cases=[]
 for stack_bytes in [1024,2048,4096]:
  results=[]
  for m in pair:
   m.cpu.mem_write(r.t.ATTR,struct.pack('<9I',0,0,0,0,0,stack_bytes,24,0,0));ret=m.run('thread_new',[0x42e2f9,0x1234,r.t.ATTR]);results.append(dict(ret=ret['return'],events=ret['events'],arena=hashlib.sha256(m.cpu.mem_read(0x2000055c,0x14000)).hexdigest(),ready=bytes(m.cpu.mem_read(0x20024870,1120)).hex(),globals=bytes(m.cpu.mem_read(0x20027108,0x70)).hex(),critical=m.u(0x200004c4),basepri=m.cpu.reg_read(v.a.UC_ARM_REG_BASEPRI)))
  assert results[0]==results[1],(stack_bytes,results);assert results[0]['ret']!=0;trace.update(pair[0].trace);cases.append(dict(stack_bytes=stack_bytes,result=results[0]))
 used={int(pc,0)+i for pc,b in trace.items() for i in range(len(bytes.fromhex(b)))}
 report=dict(status='PASS',cases=len(cases),distinct_original_trace_bytes=len(used),original_sha256=v.SHA,elf_sha256=v.sha(a.elf),source_sha256={str(p.relative_to(ROOT)):v.sha(p) for p in HERE.iterdir() if p.is_file()},original_trace=trace,comparisons=cases,limits=['Actual dynamic allocation, RTOS heap init/allocate/split, suspension/resume, critical nesting, thread init/frame/registration execute. Tick provider not reached; no deferred ticks/pending-ready tasks in this profile.','Original fill41560c intercepted; source loops execute. Manual zeroed initial kernel state, not hardware startup. No scheduling/IRQ/physical memory/byte identity proof.'])
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['status','cases','distinct_original_trace_bytes']}))
if __name__=='__main__':main()
