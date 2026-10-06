#!/usr/bin/env python3
"""Differential stock/source fixtures for queue put 0x419ec0 / ring copy 0x41a4a6."""
import argparse,importlib.util,itertools,json
from pathlib import Path
from unicorn import UcError,UC_HOOK_MEM_INVALID
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[4]
spec=importlib.util.spec_from_file_location('timer_verify',ROOT/'g2/components/bootloader/thread_creation/verify_timer_wait.py');t=importlib.util.module_from_spec(spec);spec.loader.exec_module(t);v=t.v
PUT=0x419ec0;COPY=0x41a4a6;QUEUE=0x20031000;STORAGE=0x20032000;MESSAGE=0x20033000
v.ENTRIES.update(queue_put=PUT,queue_copy_in=COPY)
class Machine(v.Machine):
 def __init__(self,source=False,segs=(),syms=None):
  super().__init__(source,segs,syms);self.events=[];self.fixture={};self.invalid=None;self.stopped=False
  self.cpu.hook_add(UC_HOOK_MEM_INVALID,self.bad)
  if source:
   self.symbols['opencfw_boot_queue_put']=self.symbols['opencfw_bl_kernel_queue_put_blocking']
   self.symbols['opencfw_boot_queue_copy_in']=self.symbols['opencfw_boot_queue_copy_in']
 def bad(self,uc,access,address,size,value,user):self.invalid=dict(access=access,address=address,size=size,value=value);return False
 def code(self,uc,pc,size,user):
  if pc==0x41b2f8:self.events.append(['mask']);self.ret(0);return
  if pc==0x418b56:
   x=self.fixture.get('runtime',1);self.events.append(['runtime',x]);self.ret(x);return
  if pc in (0x41b3e4,0x41b3fc):
   self.events.append(['kernel_enter' if pc==0x41b3e4 else 'kernel_exit']);self.ret(0);return
  if pc==0x4181d8:self.events.append(['scheduler_suspend']);self.ret();return
  if pc==0x418228:
   x=self.fixture.get('resume',1);self.events.append(['scheduler_resume',x]);self.ret(x);return
  if pc==0x41b3d0:
   self.events.append(['reschedule'])
   if self.fixture.get('stop_reschedule'):
    self.stopped=True;self.finished=True;uc.emu_stop();return
   self.ret();return
  if pc==0x418912:
   ptr=self.args()[0];self.w(ptr,self.fixture.get('over',0));self.w(ptr+4,self.fixture.get('start',0));self.events.append(['timeout_capture',ptr]);self.ret();return
  if pc==0x418922:
   state,left=self.args()[:2];x=self.fixture.get('expired',0);self.w(left,self.fixture.get('remaining',max(0,self.u(left)-1)));self.events.append(['timeout_check',state,left,x]);self.ret(x);return
  if pc==0x41863e:
   q,ticks=self.args()[:2];self.events.append(['wait_list',q,ticks]);self.ret();return
  if pc==0x41a556:
   q=self.args()[0];self.events.append(['queue_unlock',q]);self.ret();return
  if pc==0x41872c:
   anchor=self.args()[0];x=self.fixture.get('remove_waiter',0);self.events.append(['remove_event_waiter',anchor,x]);self.ret(x);return
  if pc==0x418c1e:
   ptr=self.args()[0];self.events.append(['buffer_release',ptr]);self.ret(self.fixture.get('release_result',0));return
  super().code(uc,pc,size,user)
def init(m,fixture):
 m.events=[];m.invalid=None;m.stopped=False;m.fixture=fixture
 m.cpu.mem_write(QUEUE,b'\0'*80);m.cpu.mem_write(STORAGE,b'\xa5'*24);m.cpu.mem_write(MESSAGE,bytes(range(1,33)))
 q=QUEUE;s=STORAGE
 m.w(q,s);m.w(q+4,fixture.get('write',s));m.w(q+8,s+24);m.w(q+12,fixture.get('reverse',s+16))
 m.w(q+0x24,fixture.get('event_anchor',0));m.w(q+0x38,fixture.get('count',0));m.w(q+0x3c,fixture.get('capacity',3));m.w(q+0x40,fixture.get('item_size',8))
 m.cpu.mem_write(q+0x44,b'\xff\xff');m.w(0x20027148,fixture.get('now',0));m.w(0x2002715c,fixture.get('over',0))
def observe(m,ret):
 events=[]
 for event in m.events:
  event=list(event)
  if event[0]=='timeout_capture':event[1]='stack-local'
  if event[0]=='timeout_check':event[1:3]=['stack-local','stack-local']
  events.append(event)
 return {'return':ret,'stopped':m.stopped,'invalid':m.invalid,'events':events,'queue':bytes(m.cpu.mem_read(QUEUE,80)).hex(),'storage':bytes(m.cpu.mem_read(STORAGE,24)).hex()}
def run(m,name,args,f):
 init(m,f)
 try:r=m.run(name,args)['return'];assert not f.get('fatal'),(name,args,f,m.events)
 except UcError:assert f.get('fatal') and m.invalid and m.invalid['address']==0xffffffff,(name,args,f,m.invalid,m.events);r='fatal-store'
 if m.stopped:r='reschedule-boundary'
 return observe(m,r)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();assert v.sha(v.BLOB)==v.SHA
 _,segs,syms=v.elf.elf_info(a.elf);cases=[];trace={}
 fixtures=[('queue_put',[QUEUE,MESSAGE,0,0],dict(count=0,capacity=1,item_size=8,write=STORAGE,reverse=STORAGE+16)),
  ('queue_put',[QUEUE,MESSAGE,0,0],dict(count=0,capacity=50,item_size=8,write=STORAGE,reverse=STORAGE+16)),
  ('queue_put',[QUEUE,MESSAGE,0,1],dict(count=0,capacity=50,item_size=8,write=STORAGE,reverse=STORAGE+16)),
  ('queue_put',[QUEUE,MESSAGE,0,0],dict(count=0,capacity=1,item_size=8,event_anchor=0x20031100,remove_waiter=1,write=STORAGE,reverse=STORAGE+16)),
  ('queue_put',[QUEUE,MESSAGE,0,0],dict(count=1,capacity=1,item_size=8,write=STORAGE,reverse=STORAGE+16)),
  ('queue_put',[QUEUE,MESSAGE,0,2],dict(count=1,capacity=1,item_size=8,write=STORAGE,reverse=STORAGE+16)),
  ('queue_put',[QUEUE,MESSAGE,9,0],dict(count=1,capacity=1,item_size=8,runtime=1,start=100,over=0,expired=0,remaining=8,write=STORAGE,reverse=STORAGE+16,stop_reschedule=True,resume=0)),
  ('queue_put',[QUEUE,MESSAGE,9,0],dict(count=1,capacity=1,item_size=8,runtime=1,start=100,over=0,expired=1,remaining=0,write=STORAGE,reverse=STORAGE+16)),
  ('queue_put',[0,MESSAGE,0,0],dict(fatal=True)),
  ('queue_put',[QUEUE,0,0,0],dict(fatal=True)),
  ('queue_put',[QUEUE,MESSAGE,0,2],dict(capacity=3,fatal=True)),
  ('queue_put',[QUEUE,MESSAGE,9,0],dict(runtime=0,fatal=True)),
 ]
 for f in [{'count':0,'item_size':8,'write':STORAGE,'reverse':STORAGE+16},
           {'count':1,'item_size':8,'write':STORAGE+16,'reverse':STORAGE+16},
           {'count':3,'item_size':8,'write':STORAGE,'reverse':STORAGE,'capacity':3},
           {'count':3,'item_size':8,'write':STORAGE,'reverse':STORAGE+16,'capacity':3}]:
  fixtures.append(('queue_copy_in',[QUEUE,MESSAGE,2 if f['count']==3 else 0],f))
 for name,args,f in fixtures:
  pair=[Machine(),Machine(True,segs,syms)];rs=[run(m,name,args,f) for m in pair]
  assert rs[0]==rs[1],(name,args,f,rs)
  trace.update(pair[0].trace);cases.append({'entry':name,'arguments':args,'fixture':f,'observation':rs[0]})
 used={int(pc,0)+i for pc,raw in trace.items() for i in range(len(bytes.fromhex(raw)))}
 report={'status':'PASS','cases':len(cases),'distinct_original_trace_bytes':len(used),'original_sha256':v.SHA,'elf_sha256':v.sha(a.elf),'source_sha256':{str(p.relative_to(ROOT)):v.sha(p) for p in [HERE/'verify_queue_send.py',HERE/'queue_send_module.ld',ROOT/'g2/components/bootloader/thread_creation/queue_send.c',ROOT/'g2/components/bootloader/thread_creation/queue_send.h']},'original_trace':trace,'comparisons':cases,'limits':['Queue timeout capture/check, scheduler suspend/resume, wait-list insertion, lock wake/unlock and event-waiter removal are explicit provider cuts in these standalone fixtures; their call ABI and surrounding state path are compared.','The original 0x41a4a6 helper and its actual memcpy41568c run as instructions; source uses a forward byte loop. Item size, pointers, queue state and timeout values are synthetic. No tick unit or hardware queue behavior is inferred.']}
 a.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['status','cases','distinct_original_trace_bytes']}))
if __name__=='__main__':main()
