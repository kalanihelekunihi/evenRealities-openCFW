#!/usr/bin/env python3
"""Semaphore->native queue factory/heap/destroy, with scheduler and put cuts."""
import argparse,hashlib,importlib.util,json,struct
from pathlib import Path
spec=importlib.util.spec_from_file_location('sem',Path(__file__).with_name('verify_semaphore_create.py'));v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
class Machine(v.Machine):
 def __init__(self,source,segments,symbols):
  super().__init__(source,segments,symbols)
  self.cuts={pc:label for pc,label in self.cuts.items() if label not in ['dynamic','static','free']}
  self.scheduler={(symbols[n]&~1 if source else pc):label for n,pc,label in [('opencfw_bl_scheduler_suspend',0x4181d8,'suspend'),('opencfw_bl_scheduler_resume',0x418228,'resume')]}
 def code(self,uc,pc,size,user):
  if pc in self.scheduler:self.events.append([self.scheduler[pc]]);uc.reg_write(v.a.UC_ARM_REG_R0,0);uc.reg_write(v.a.UC_ARM_REG_PC,uc.reg_read(v.a.UC_ARM_REG_LR));return
  super().code(uc,pc,size,user)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args();_,segments,symbols=v.v.elf.elf_info(args.elf);cases=[];trace={}
 for maximum,initial,static,put in [(1,0,False,0),(1,1,False,0),(1,1,False,1),(1,1,False,2),(1,0,True,0),(1,1,True,0),(1,1,True,1),(1,1,True,2),(3,0,False,0),(3,2,False,0),(3,0,True,0),(3,2,True,0)]:
  observations=[]
  for source in [False,True]:
   m=Machine(source,segments,symbols)
   # Explicit cold RTOS heap globals, shared by source and original fixtures.
   m.cpu.mem_write(0x20027020,b'\0'*8);m.cpu.mem_write(0x20027108,b'\0'*20)
   row=m.run(maximum,initial,static,v.CB if static else 0,80 if static else 0,0,True,put)
   row.update(arena_sha256=hashlib.sha256(m.cpu.mem_read(0x2000055c,0x14000)).hexdigest(),heap_head=bytes(m.cpu.mem_read(0x20027020,8)).hex(),heap_globals=bytes(m.cpu.mem_read(0x20027108,20)).hex());observations.append(row)
   if not source:trace.update(m.trace)
  assert observations[0]==observations[1],(maximum,initial,static,put,observations);cases.append(dict(maximum=maximum,initial=initial,static=static,put_status=put,observation=observations[0]))
 report=dict(status='PASS',cases=len(cases),elf_sha256=hashlib.sha256(args.elf.read_bytes()).hexdigest(),original_sha256=v.v.LOCKED_SHA,original_trace={hex(pc):raw for pc,raw in trace.items()},comparisons=cases,limits=['Native queue initialization, heap allocate/free/coalescing and recovered semaphore paths execute. Scheduler suspend/resume and queue-put outcomes are controlled; guard returns0.','Cold synthetic heap; full81920-byte arena and heap globals compared. No live scheduler, waiter cancellation or IRQ delivery proof.','Binary initial-token failure frees dynamic allocation and preserves static storage as dictated by flag+0x46. No release behavior is added beyond recovered stock destroy.'])
 args.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['status','cases']}))
if __name__=='__main__':main()
