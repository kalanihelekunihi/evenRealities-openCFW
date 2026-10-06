#!/usr/bin/env python3
"""Recovered previously failed context helpers and notification control flow."""
import argparse,importlib.util,json,struct,itertools
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
s=importlib.util.spec_from_file_location('bootv',ROOT/'g2/components/bootloader/update_core/verify.py');v=importlib.util.module_from_spec(s);s.loader.exec_module(v)
v.ENTRIES.update(dfu_queue_init=0x42dd70,dfu_thread_init=0x42ddae,dfu_thread_deinit=0x42ddda,dfu_send=0x42dca2,dfu_dispatch=0x42e1c4,dfu_orchestrator=0x42dd14)
THREAD=0x200004d4;QUEUE=0x200004d8;MSG=0x20032000;LOG=0x08002120
class Machine(v.Machine):
 def __init__(self,*args,**kw):
  super().__init__(*args,**kw);self.new_queue=0x62;self.new_thread=0x63;self.put_status=0;self.flags=[];self.panic=False
 def code(self,uc,pc,size,user):
  r0,r1,r2,r3=self.args()
  if pc==0x416816:self.events.append(['queue_new',r0,r1,r2]);assert [r0,r1,r2]==[50,40,0];self.ret(self.new_queue);return
  if pc==0x4160fe:
   expected=(self.symbols['opencfw_boot_dfu_orchestrator'] if self.source else 0x42dd15);assert r0==expected and r1==0
   attrs=list(struct.unpack('<9I',self.cpu.mem_read(r2,36)));assert attrs==[0x4341a4,0,0x20026b30,0x70,0x20020e00,0x2000,0x2e,1,0]
   assert bytes(self.cpu.mem_read(attrs[0],4))==b'dfu\0';self.events.append(['thread_new','orchestrator',r1,attrs]);self.ret(self.new_thread);return
  if pc==0x416200:self.events.append(['thread_terminate',r0]);self.ret();return
  if pc==0x4168a2:self.events.append(['queue_put',r0,bytes(self.cpu.mem_read(r1,40)).hex(),r2,r3,self.put_status]);assert r2==r3==0;self.ret(self.put_status);return
  if pc==0x41623a:self.events.append(['flags_set',r0,r1]);self.ret(0x55);return
  if pc==0x4162c4:
   assert [r0,r1,r2]==[0xffffff,0,0xffffffff]
   if self.flags:flags=self.flags.pop(0);self.events.append(['flags_wait',flags]);self.ret(flags)
   else:self.events.append(['flags_wait','synthetic_stop']);self.finished=True;uc.emu_stop()
   return
  if pc==0x41b2f8:self.events.append(['panic_boundary']);self.panic=True;self.finished=True;uc.emu_stop();return
  names={0x42de58:'drain_task_boundary',0x42e1da:'terminal_boundary',0x42dd9a:'control_one',0x42dda4:'control_two',0x42dd68:'runtime_context'}
  if pc in names:self.events.append([names[pc]]);self.ret();return
  if pc==LOG:self.events.append(['log',r0,r1]);self.ret();return
  super().code(uc,pc,size,user)
 def invoke(self,name,args):
  d=self.run(name,args)
  if name!='dfu_send':d.pop('return')
  d['context']=[self.u(THREAD),self.u(QUEUE)];d['panic']=self.panic;return d

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();_,seg,sym=v.elf.elf_info(a.elf);cases=[];trace={}
 def check(name,args,fixture):
  ms=[Machine(),Machine(True,seg,sym)]
  for m in ms:
   m.w(THREAD,fixture.get('thread',0x63));m.w(QUEUE,fixture.get('queue',0x62));m.new_queue=fixture.get('new_queue',0x62);m.new_thread=fixture.get('new_thread',0x63);m.put_status=fixture.get('put_status',0);m.flags=list(fixture.get('flags',[]));m.cpu.mem_write(MSG,bytes(range(40)))
  d=[m.invoke(name,args) for m in ms];assert d[0]==d[1],(name,fixture,{k:[x[k] for x in d] for k in d[0] if d[0][k]!=d[1][k]});trace.update(ms[0].trace);cases.append({'function':name,'fixture':fixture,'result':d[0]})
 for q in [0,0x62,0xffffffff]:check('dfu_queue_init',[],{'new_queue':q})
 for t in [0,0x63,0xffffffff]:check('dfu_thread_init',[],{'new_thread':t})
 for t in [0,0x63,0xffffffff]:check('dfu_thread_deinit',[],{'thread':t})
 for q,t,status in itertools.product([0,0x62],[0,0x63],[0,1,0xfffffffd,0xfffffffc]):check('dfu_send',[MSG],{'queue':q,'thread':t,'put_status':status})
 for flags in [0,1,0x400000,0x800000,0xc00000,0xffffffff,0x80000000,0xffffff]:check('dfu_dispatch',[flags],{'flags_value':flags})
 for flags in [[],[0],[0xffffffff],[1,0x400000,0x800000,0xc00000,0,0x80000000]]:check('dfu_orchestrator',[],{'flags':flags})
 used={int(pc,0)+i for pc,raw in trace.items() for i in range(len(bytes.fromhex(raw)))}
 d={'status':'PASS','cases':len(cases),'comparisons':cases,'original_trace':trace,'distinct_original_trace_bytes':len(used),'original_sha256':v.SHA,'elf_sha256':v.sha(a.elf),'source_sha256':{p.name:v.sha(p) for p in Path(__file__).parent.iterdir() if p.suffix in ['.c','.h','.py','.ld']},'limits':['Real original/source context, queue/thread initialization, publisher/dispatcher and orchestrator instructions execute.','CMSIS queue/thread/flags/control callbacks are synthetic; no kernel scheduling, live ISR or concurrency proof.','Allocation failure stops at panic call boundary; the subsequent original/source intentional invalid-address store/infinite loop is statically recovered but not executed.','DFU/terminal callbacks are observed at entry and return synthetically; terminal is not demonstrated to return on hardware.','Only low-word publisher result and void helper semantics compared; incidental original return registers not public contracts here.','Attributes equal raw36byte words; exact CMSIS/kernel revision and semantic security configuration not established.','No physical reset/startup, complete platform initialization or byte-identical build.']};a.output.write_text(json.dumps(d,indent=2)+'\n');print(json.dumps({'status':'PASS','cases':len(cases),'original_bytes':len(used)},indent=2))
if __name__=='__main__':main()
