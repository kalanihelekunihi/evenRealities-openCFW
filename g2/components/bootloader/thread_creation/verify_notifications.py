#!/usr/bin/env python3
"""Single-slot notification state and actual blocked-task ready-list wake."""
import argparse,importlib.util,itertools,json
from pathlib import Path
from unicorn import UcError
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
spec=importlib.util.spec_from_file_location('timer',HERE/'verify_timer_wait.py');t=importlib.util.module_from_spec(spec);spec.loader.exec_module(t);v=t.v;p=t.p
v.ENTRIES.update(thread_notify_wait=0x418dac,thread_notify=0x418e70,thread_wait_result_take=0x418d7a)
OUT=0x20030300
class Machine(t.Machine):
 def __init__(self,*args,**kwargs):
  super().__init__(*args,**kwargs);self.stop_yield=False;self.yield_entry=(self.symbols['opencfw_bl_kernel_reschedule']&~1) if self.source else 0x41b3d0
 def code(self,uc,pc,size,user):
  if pc==self.yield_entry and self.stop_yield:self.events.append(['yield-boundary']);self.finished=True;uc.emu_stop();return
  super().code(uc,pc,size,user)
def snapshot(m):
 return dict(events=m.events,regions={hex(a):bytes(m.cpu.mem_read(a,n)).hex() for a,n in [(0x20030000,224),(0x20024870,1120),(0x20026f34,100),(0x20027130,100),(OUT,4)]},basepri=m.cpu.reg_read(v.a.UC_ARM_REG_BASEPRI),nesting=m.u(0x200004c4),icsr=m.u(0xe000ed04),fault=m.invalid)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();assert v.sha(v.BLOB)==v.SHA
 _,segs,syms=v.elf.elf_info(a.elf);trace={};cases=[];fixtures=[]
 for state,inherited,action,value,previous in itertools.product([0,1,2],[False,True],[0,1,2,3,4,256],[0,0x800000,0xffffffff],[0,OUT]):fixtures.append(('thread_notify',[0x20030000,0,value,action,previous],dict(state=state,inherited=inherited)))
 for state,ticks,entryclear,exitclear,output in itertools.product([0,1,2],[0,13,0xffffffff],[0,0x800000],[0,0x800000],[0,OUT]):fixtures.append(('thread_notify_wait',[0,entryclear,exitclear,output,ticks],dict(state=state,stop_yield=state!=2 and ticks!=0)))
 for val in [0,32,0x02000002,0xffffffff]:fixtures.append(('thread_wait_result_take',[],dict(eventword=val)))
 fixtures += [('thread_notify',[0x20030000,0,1,5,OUT],dict(state=0,now=17,fatal=True)),('thread_notify',[0x20030000,1,1,0,OUT],dict(state=0,fatal=True)),('thread_notify_wait',[1,0,0,OUT,0],dict(state=0,fatal=True))]
 for entry,args,f in fixtures:
  pair=[Machine(),Machine(True,segs,syms)];results=[];returns=[]
  for m in pair:
   t.init(m,f.get('now',0));target=0x20030000
   if entry=='thread_notify':p.initialize(m,False,f.get('inherited',False),f['state']!=1,False,False,0);m.w(0x20027138,0x20026f34);m.w(0x2002713c,0x20026f48);m.w(0x20027164,0xffffffff);m.w(0x20027148,f.get('now',0))
   m.w(target+0x68,0x800123);m.cpu.mem_write(target+0x6c,bytes([f.get('state',0)]));m.w(target+0x28,0);m.w(OUT,0xcccccccc)
   if 'eventword' in f:m.w(target+0x18,f['eventword'])
   m.stop_yield=f.get('stop_yield',False)
   if len(args)>4:m.w(v.SP,args[4])
   try:ret=m.run(entry,args)['return'];assert not f.get('fatal');returns.append(None if m.stop_yield else ret)
   except UcError:assert f.get('fatal') and m.invalid['address']==0xffffffff;returns.append('invalid-store')
   results.append(snapshot(m))
  assert results[0]==results[1] and returns[0]==returns[1],(entry,args,f,returns,results)
  trace.update(pair[0].trace);cases.append(dict(entry=entry,args=args,fixture=f,return_value=returns[0],result=results[0]))
 used={int(pc,0)+i for pc,b in trace.items() for i in range(len(bytes.fromhex(b)))}
 report=dict(status='PASS',cases=len(cases),distinct_original_trace_bytes=len(used),original_sha256=v.SHA,elf_sha256=v.sha(a.elf),source_sha256={str(HERE.joinpath(n).relative_to(ROOT)):v.sha(HERE/n) for n in ['thread_notifications.c','thread_notifications.h','timer_wait.c','timer_wait.h','kernel_runtime.c','scheduler_resume.c','notifications_module.ld','verify_notifications.py']},original_trace=trace,comparisons=cases,limits=['Actual notification state0/1/2, actions0..4 and low-byte alias256, previous/current flag values, finite/indefinite wait list moves, blocked noncurrent target ready insertion, highest priority and PendSV-request store execute. No provider cuts on these notification paths.','Blocked wait fixtures stop at PendSV-request entry; no post-wake retry or real context switching in this direct fixture. Other sender wake paths run to completion with synthetic coherent TCB/lists. Fatal invalid index/action observes invalid-address store, not hardware HardFault delivery.','ISR418fe8 is not reconstructed or invoked. No automatic interrupts, scheduling/timing/hardware/byte identity is claimed.'])
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['status','cases','distinct_original_trace_bytes']}))
if __name__=='__main__':main()
