#!/usr/bin/env python3
"""Native mutex ownership sequences; current-task selection is synthetic."""
import argparse,importlib.util,json
from pathlib import Path
s=importlib.util.spec_from_file_location('mutex_cases',Path(__file__).with_name('verify_mutex_kernel.py'));v=importlib.util.module_from_spec(s);s.loader.exec_module(v)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();_,segs,syms=v.v.elf.elf_info(a.elf);cases=[];trace={}
 for kind in ['recursive-ownership','final-priority-release']:
  outputs=[]
  for source in [False,True]:
   m=v.Machine(source,segs,syms);observations=[]
   if kind=='recursive-ownership':
    m.seed(owner=0,token=1,depth=0)
    steps=[(v.T,'acquire',v.Q|1),(v.T,'acquire',v.Q|1),(v.O,'release',v.Q|1),(v.O,'acquire',v.Q),(v.T,'release',v.Q|1),(v.T,'release',v.Q|1),(v.O,'acquire',v.Q),(v.O,'release',v.Q)]
   else:
    m.seed(owner=v.O,token=0,depth=1,priority=6,base=2,held=1,current=v.O)
    steps=[(v.O,'release',v.Q)]
   for task,op,handle in steps:
    m.w(0x20027134,task);o=m.run_entry('opencfw_boot_mutex_'+op,[handle,0]);assert not o['fatal'];observations.append(o)
   if kind=='recursive-ownership':
    assert [o['return_value'] for o in observations]==[0,0,0xfffffffd,0xfffffffd,0,0,0,0]
    assert m.u(v.Q+56)==1 and m.u(v.Q+8)==0 and m.u(v.Q+12)==0 and m.u(v.T+100)==0 and m.u(v.O+100)==1
   else:assert m.u(v.O+100)==0 and m.u(v.O+44)==2 and m.u(v.O+24)==54 and m.u(v.O+20)==v.READY+40
   outputs.append(observations)
   if not source:trace.update(m.trace)
  assert outputs[0]==outputs[1],kind;cases.append(dict(sequence=kind,observations=outputs[0]))
 r=dict(status='PASS',cases=len(cases),elf_sha256=v.v.sha(a.elf),original_sha256=v.v.SHA,runner_sha256=v.v.sha(Path(__file__)),original_trace=trace,comparisons=cases,limits=['Native acquire/release, token/recursive/owner count, queue-put and final priority restoration execute on persistent original/source state. Changing CURRENT is an explicit synthetic task-selection operation; no real task switch, asynchronous race, blocking wake, cancellation or drain proof.'])
 a.output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:r[k] for k in ['status','cases','elf_sha256']}))
if __name__=='__main__':main()
