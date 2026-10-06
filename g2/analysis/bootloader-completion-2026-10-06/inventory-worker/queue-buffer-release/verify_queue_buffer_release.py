#!/usr/bin/env python3
"""Original/source comparison for queue reference release 0x418c1e."""
import argparse,importlib.util,json
from pathlib import Path
from unicorn import UcError,UC_HOOK_MEM_INVALID
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[4]
spec=importlib.util.spec_from_file_location('bootverify',ROOT/'g2/components/bootloader/update_core/verify.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
ENTRY=0x418c1e;TCB=0x20030000;OTHER=0x20030100;CURRENT=0x20027134;HIGHEST=0x2002714c;READY=0x20024870
v.ENTRIES['queue_buffer_release']=ENTRY
class Machine(v.Machine):
 def __init__(self,source=False,segs=(),syms=None):
  super().__init__(source,segs,syms);self.events=[];self.invalid=None
  self.cpu.hook_add(UC_HOOK_MEM_INVALID,self.bad)
  if source:self.symbols['opencfw_boot_queue_buffer_release']=self.symbols['opencfw_boot_queue_buffer_release']
 def bad(self,uc,access,address,size,value,user):self.invalid={'access':access,'address':address,'size':size,'value':value};return False
 def code(self,uc,pc,size,user):
  if pc==0x41b2f8:self.events.append(['mask_interrupts']);self.ret(0);return
  if pc==0x41b5a8:
   node=self.args()[0];listing=self.u(node+16);following=self.u(node+4);previous=self.u(node+8)
   self.w(following+8,previous);self.w(previous+4,following)
   if self.u(listing+4)==node:self.w(listing+4,previous)
   self.w(node+16,0);self.w(listing,self.u(listing)-1)
   self.events.append(['list_unlink',node,listing]);self.ret(self.u(listing));return
  super().code(uc,pc,size,user)
def list_empty(m,base):
 end=base+8;m.w(base,0);m.w(base+4,end);m.w(base+8,0xffffffff);m.w(base+12,end);m.w(base+16,end)
def list_insert_single(m,base,node):
 end=base+8;m.w(base,1);m.w(base+4,end);m.w(base+12,node);m.w(base+16,node)
 m.w(node+4,end);m.w(node+8,end);m.w(node+16,base)
def initialize(m,f):
 m.cpu.mem_write(TCB,b'\0'*112);m.cpu.mem_write(OTHER,b'\0'*112)
 for p in range(56):list_empty(m,READY+20*p)
 effective=f.get('effective',48);base=f.get('base',24);references=f.get('references',1)
 m.w(CURRENT,f.get('current',TCB));m.w(HIGHEST,f.get('highest',48))
 m.w(TCB+6*4,f.get('wait_field',8));m.w(TCB+11*4,effective);m.w(TCB+24*4,base);m.w(TCB+25*4,references)
 list_insert_single(m,READY+20*effective,TCB+4)
 if effective!=base:list_insert_single(m,READY+20*base,OTHER+4)
 m.w(OTHER+11*4,base);m.w(OTHER+24*4,base);m.w(OTHER+25*4,1)
def observe(m,result):
 return {'result':result,'fault':m.invalid,'events':m.events,'tcb':bytes(m.cpu.mem_read(TCB,112)).hex(),'other':bytes(m.cpu.mem_read(OTHER,112)).hex(),'ready':bytes(m.cpu.mem_read(READY,1120)).hex(),'highest':m.u(HIGHEST),'current':m.u(CURRENT)}
def execute(m,source,segs,syms,arg,f):
 initialize(m,f)
 if source:
  entry='queue_buffer_release';args=[arg]
 else:entry='queue_buffer_release';args=[arg]
 try:ret=m.run(entry,args)['return'];assert not f.get('fatal'),(arg,f,ret)
 except UcError:assert f.get('fatal') and m.invalid and m.invalid['address']==0xffffffff,(arg,f,m.invalid);ret='fatal-store'
 return observe(m,ret)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();assert v.sha(v.BLOB)==v.SHA
 _,segs,syms=v.elf.elf_info(a.elf);rows=[
  (TCB,dict(effective=24,base=24,references=1,highest=24)),
  (TCB,dict(effective=48,base=24,references=2,highest=48)),
  (TCB,dict(effective=48,base=24,references=1,highest=48)),
  (TCB,dict(effective=48,base=8,references=1,highest=4)),
  (0,dict(effective=24,base=24,references=0)),(TCB+0x1000,dict(fatal=True)),(TCB,dict(references=0,fatal=True))]
 cases=[];trace={}
 for arg,f in rows:
  pair=[Machine(),Machine(True,segs,syms)];results=[execute(m,m.source,segs,syms,arg,f) for m in pair]
  assert results[0]==results[1],(arg,f,results)
  trace.update(pair[0].trace);cases.append({'argument':arg,'fixture':f,'observation':results[0]})
 used={int(pc,0)+i for pc,raw in trace.items() for i in range(len(bytes.fromhex(raw)))}
 out={'status':'PASS','cases':len(cases),'distinct_original_trace_bytes':len(used),'original_sha256':v.SHA,'elf_sha256':v.sha(a.elf),'source_sha256':{str(p.relative_to(ROOT)):v.sha(p) for p in [HERE/'verify_queue_buffer_release.py',HERE/'queue_buffer_release_module.ld',ROOT/'g2/components/bootloader/thread_creation/queue_buffer_release.c',ROOT/'g2/components/bootloader/thread_creation/queue_buffer_release.h']},'original_trace':trace,'comparisons':cases,'limits':['The stock intrusive-list unlink routine at 0x41b5a8 executes as the direct dependency in both runs; list memory is synthetic but coherent. The source component resolves this ABI to the separately recovered opencfw_boot_list_unlink provider.','These fixtures verify current-thread ownership, reference decrement, inherited-priority retention until the final reference, effective-priority restoration, ready-list movement, wait-state recomputation, highest-priority refresh and fatal guards. Mutex acquisition and real blocking/preemption are outside this helper. No hardware or byte-identity claim.']}
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'status':out['status'],'cases':out['cases'],'distinct_original_trace_bytes':len(used)}))
if __name__=='__main__':main()
