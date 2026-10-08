#!/usr/bin/env python3
"""Native public ISR wrappers; no kernel operation return stubs."""
import argparse,importlib.util,itertools,json
from pathlib import Path
s=importlib.util.spec_from_file_location('isr_cases',Path(__file__).with_name('verify_isr_delivery.py'));v=importlib.util.module_from_spec(s);s.loader.exec_module(v)
v.ENTRIES.update(opencfw_bl_queue_put=0x4168a2,opencfw_bl_queue_get=0x416920,opencfw_provider_41652e=0x41652e)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();_,segs,syms=v.v.elf.elf_info(a.elf);cases=[];trace={}
 def check(name,params,fixture,expected):
  out=[]
  for source in [False,True]:
   m=v.Machine(source,segs,syms);m.seed_queue(**fixture);m.w(0x20027150,1);m.cpu.reg_write(v.v.a.UC_ARM_REG_PRIMASK,1);r=m.call(name,params);assert not m.fatal and r==(expected&0xffffffff),(name,r,expected);out.append(m.snapshot([r]))
   if not source:trace.update(m.trace)
  assert out[0]==out[1],(name,params,fixture,{k:[o[k] for o in out] for k in out[0] if out[0][k]!=out[1][k]});cases.append(dict(function=name,args=params,fixture=fixture,observed=out[0]))
 for op,count,wake,timeout in itertools.product(['put','get'],[0,1,3],[False,True],[0,1,0xffffffff]):
  f=dict(count=count,wait=('receive' if op=='put' else 'send') if wake else None);expected=-4 if timeout else -3 if (count==3 if op=='put' else count==0) else 0
  check('opencfw_bl_queue_'+op,[v.Q,v.MSG if op=='put' else v.OUT,v.OUT+8,timeout],f,expected)
 for op,queue,message in itertools.product(['put','get'],[0,v.Q],[0,v.MSG]):
  if queue and message:continue
  check('opencfw_bl_queue_'+op,[queue,message,v.OUT+8,0],{},-4)
 for count,event,flags in itertools.product([0,3],[0,v.EVENT],[0,1,0x00ffffff,0x01000000,0x80000000]):
  expected=-4 if not event or flags&0xff000000 else -3 if count==3 else 0x10|flags
  check('opencfw_provider_41652e',[event,flags],dict(count=count,size=16),expected)
 r=dict(status='PASS',cases=len(cases),elf_sha256=v.v.sha(a.elf),original_sha256=v.v.SHA,runner_sha256=v.v.sha(Path(__file__)),original_trace=trace,comparisons=cases,limits=['Public queue put/get and event-flags wrappers execute native ISR kernel paths under controlled PRIMASK/kernel-state fixtures. No provider result stubs. Reserved flag bits and ISR nonzero timeout reject-4; full/empty gives-3; wake requests store PendSVSET without task restoration.','Event-flags wrapper returns current_flags|requested_flags after successful deferred enqueue; actual callback/clear-on-exit may produce a different later flags value. Enqueue is not completion. Synthetic coherent SRAM/masks, no asynchronous exception delivery or scheduling/timing proof.'])
 a.output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:r[k] for k in ['status','cases','elf_sha256']}))
if __name__=='__main__':main()
