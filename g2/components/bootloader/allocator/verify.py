#!/usr/bin/env python3
"""Full allocator-memory original/source comparisons; only mutex/log stubs."""
import argparse,importlib.util,json,hashlib,random
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
s=importlib.util.spec_from_file_location('bootv',ROOT/'g2/components/bootloader/update_core/verify.py');v=importlib.util.module_from_spec(s);s.loader.exec_module(v)
v.ENTRIES.update(allocator_init=0x41fd70,fs_alloc=0x41552c,fs_free=0x415558)
BASE=0x20081000;SIZE=0x70800;LOG=0x08002100;PRINTF=0x08002110
class Machine(v.Machine):
 def __init__(self,*args,**kw):
  super().__init__(*args,**kw);self.cpu.mem_map(0x20040000,0xc0000);self.cpu.mem_write(BASE,b'\xcc'*SIZE);self.w(0x20027130,0x61);self.lock_failure=0
 def code(self,uc,pc,size,_):
  if pc==0x4166aa:
   r0,r1,_,_=self.args();assert r0==0x61 and r1==1000;self.events.append(['lock',r0,r1,self.lock_failure]);self.ret(self.lock_failure);return
  if pc==0x416710:self.events.append(['unlock',self.args()[0]]);self.ret();return
  if pc==LOG:self.events.append(['log',4,self.args()[0]]);self.ret();return
  if pc==PRINTF:raise AssertionError('Unexpected TLSF diagnostic provider')
  super().code(uc,pc,size,_)
 def invoke(self,name,args):
  r=self.run(name,args)
  if name=='fs_free':r.pop('return')
  r['arena_sha256']=hashlib.sha256(self.cpu.mem_read(BASE,SIZE)).hexdigest();r['core']=self.u(0x2002718c)
  return r

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();_,seg,sym=v.elf.elf_info(a.elf);ms=[Machine(),Machine(True,seg,sym)];trace={};cases=[]
 def check(name,args,fixture):
  d=[m.invoke(name,args) for m in ms];assert d[0]==d[1],(name,args,fixture,{k:[x[k] for x in d] for k in d[0] if d[0][k]!=d[1][k]});trace.update(ms[0].trace);cases.append({'function':name,'arguments':args,'fixture':fixture,'result':d[0]});return d[0].get('return')
 assert check('allocator_init',[],{})==0
 held=[]
 for n in [0,1,3,4,5,12,16,31,96,256,4096,65536,SIZE,SIZE+1]:
  p=check('fs_alloc',[n],{'size':n})
  if p:
   held.append(p)
   for m in ms:m.cpu.mem_write(p,bytes([n&255])*max(1,min(n,4096)))
 for p in held[::2]:check('fs_free',[p],{'coalescing':'alternating'})
 for p in held[1::2]:check('fs_free',[p],{'coalescing':'remaining'})
 check('fs_free',[0],{'null':True})
 for m in ms:m.lock_failure=1
 assert check('fs_alloc',[96],{'lock_failure':True})==0
 for m in ms:m.lock_failure=0
 p=check('fs_alloc',[96],{})
 for m in ms:m.lock_failure=1
 check('fs_free',[p],{'lock_failure_leaves_live':True})
 for m in ms:m.lock_failure=0
 check('fs_free',[p],{'release_after_failure':True})
 rng=random.Random(61006);live=[]
 for step in range(180):
  if live and rng.randrange(3)==0:
   p=live.pop(rng.randrange(len(live)));check('fs_free',[p],{'step':step})
  else:
   n=rng.choice([1,4,8,24,96,128,256,1024,4096,8192]);p=check('fs_alloc',[n],{'step':step})
   if p:
    live.append(p)
    for m in ms:m.cpu.mem_write(p,bytes([step&255])*n)
 for p in live:check('fs_free',[p],{'final_drain':True})
 used={int(pc,0)+i for pc,raw in trace.items() for i in range(len(bytes.fromhex(raw)))}
 sources=[p for p in Path(__file__).parent.rglob('*') if p.suffix in ['.c','.h','.py','.ld']]+[ROOT/'g2/components/bootloader/filesystem/runtime_memory.c']
 d={'status':'PASS','cases':len(cases),'comparisons':cases,'original_sha256':v.SHA,'elf_sha256':v.sha(a.elf),'source_sha256':{str(p.relative_to(ROOT)):v.sha(p) for p in sources},'original_trace':trace,'distinct_original_trace_bytes':len(used),'limits':['Full real original and pinned source TLSF allocation/free instructions and full arena bytes compared after every operation.','Mutex acquire/release and init logger are synthetic; scheduling/concurrency/error diagnostics not implemented or proven.','Valid geometry and bounded requests only; corrupt/free-invalid/double-free/overflow are not tested-safe.','Source assertion macros disabled for this candidate build; stock failure-observable behavior remains unproven.','Compatible Cortex-M4 source profile, not byte-identical IAR or full bootloader.']};a.output.write_text(json.dumps(d,indent=2)+'\n');print(json.dumps({'status':'PASS','cases':len(cases),'original_bytes':len(used)},indent=2))
if __name__=='__main__':main()
