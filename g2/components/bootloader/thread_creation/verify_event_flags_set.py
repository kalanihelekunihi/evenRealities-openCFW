#!/usr/bin/env python3
"""Actual event flag matching, clear masks, list removal and priority wake."""
import argparse,importlib.util,itertools,json
from pathlib import Path
from unicorn import UcError
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
spec=importlib.util.spec_from_file_location('timer',HERE/'verify_timer_wait.py');t=importlib.util.module_from_spec(spec);spec.loader.exec_module(t);v=t.v;p=t.p
v.ENTRIES.update(event_new=0x4164da,event_flags_set=0x419b06,event_set_api=0x41652e,event_flags_read=0x419af4)
EVENT=0x20031000;ATTR=0x20031200
class Machine(t.Machine):
 def __init__(self,*args,**kwargs):super().__init__(*args,**kwargs);self.alloc_success=True;self.isr_status=1;self.isr_woken=0
 def code(self,uc,pc,size,user):
  if pc==0x419730:self.events.append(['allocate',self.args()[0]]);self.ret(EVENT if self.alloc_success else 0);return
  if pc==0x419bd2:
   event,mask,out,_=self.args();self.events.append(['isr-provider',event,mask]);self.w(out,self.isr_woken);self.ret(self.isr_status);return
  super().code(uc,pc,size,user)
def snapshot(m):
 return dict(events=m.events,regions={hex(a):bytes(m.cpu.mem_read(a,n)).hex() for a,n in [(EVENT,32),(0x20030000,224),(0x20024870,1120),(0x20026f34,100),(0x20027130,100)]},basepri=m.cpu.reg_read(v.a.UC_ARM_REG_BASEPRI),nesting=m.u(0x200004c4),icsr=m.u(0xe000ed04),fault=m.invalid)
def init(m,f):
 t.init(m,0);target=p.initialize(m,False,f.get('priority',24)==48,not f.get('waiter'),False,False,0)
 m.w(0x20027138,0x20026f34);m.w(0x2002713c,0x20026f48);m.w(0x20027164,0xffffffff);m.w(0x20027144,2)
 m.cpu.mem_write(EVENT,b'\xcc'*32)
 m.w(EVENT,f.get('initial',0));lst=EVENT+4;end=lst+8
 for off,val in [(0,0),(4,end),(8,0xffffffff),(12,end),(16,end)]:m.w(lst+off,val)
 if f.get('waiter'):
  node=target+24
  for off,val in [(0,f['mask']|f['control']|0x80000000),(4,end),(8,end),(12,target),(16,lst)]:m.w(node+off,val)
  m.w(lst,1);m.w(lst+12,node);m.w(lst+16,node)
 m.cpu.reg_write(v.a.UC_ARM_REG_IPSR,f.get('ipsr',0));m.alloc_success=f.get('alloc_success',True);m.isr_status=f.get('isr_status',1);m.isr_woken=f.get('isr_woken',0)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();assert v.sha(v.BLOB)==v.SHA
 _,segs,syms=v.elf.elf_info(a.elf);trace={};cases=[];fixtures=[]
 for initial,flags,mask,control,priority in itertools.product([0,1,3],[0,1,2,3],[1,3,4],[0,0x01000000,0x04000000,0x05000000],[24,48]):fixtures.append(('event_flags_set',[EVENT,flags],dict(initial=initial,waiter=True,mask=mask,control=control,priority=priority)))
 for initial,flags,ipsr,status,woken in itertools.product([0,3],[0,2],[0,3],[0,1],[0,1]):fixtures.append(('event_set_api',[EVENT,flags],dict(initial=initial,ipsr=ipsr,isr_status=status,isr_woken=woken)))
 for cb,size,success,ipsr in itertools.product([0,EVENT],[0,31,32,64],[False,True],[0,3]):fixtures.append(('event_new',[ATTR],dict(cb=cb,size=size,alloc_success=success,ipsr=ipsr)))
 fixtures += [('event_new',[0],dict(alloc_success=True)),('event_new',[0],dict(alloc_success=False)),('event_flags_set',[EVENT,0xff000000],dict(fatal=True)),('event_flags_set',[0,1],dict(fatal=True))]
 for entry,args,f in fixtures:
  pair=[Machine(),Machine(True,segs,syms)];results=[];returns=[]
  for m in pair:
   init(m,f)
   if entry=='event_new':
    for i,val in enumerate([0,0,f.get('cb',0),f.get('size',0)]):m.w(ATTR+4*i,val)
   try:ret=m.run(entry,args)['return'];assert not f.get('fatal');returns.append(ret)
   except UcError:assert f.get('fatal') and m.invalid['address']==0xffffffff;returns.append('invalid-store')
   results.append(snapshot(m))
  assert results[0]==results[1] and returns[0]==returns[1],(entry,args,f,returns,results)
  trace.update(pair[0].trace);cases.append(dict(entry=entry,args=args,fixture=f,return_value=returns[0],result=results[0]))
 used={int(pc,0)+i for pc,b in trace.items() for i in range(len(bytes.fromhex(b)))}
 report=dict(status='PASS',cases=len(cases),distinct_original_trace_bytes=len(used),original_sha256=v.SHA,elf_sha256=v.sha(a.elf),source_sha256={str(HERE.joinpath(n).relative_to(ROOT)):v.sha(HERE/n) for n in ['event_flags_set.c','event_flags_set.h','timer_wait.c','kernel_runtime.c','scheduler_resume.c','event_flags_set_module.ld','verify_event_flags_set.py']},original_trace=trace,comparisons=cases,limits=['Actual event create/set/read, flag matching/clear mask, blocked waiter and delay-list removal, ready insertion, highest-priority/yield-pending and scheduler resume execute. Synthetic coherent one-waiter event fixture.','ISR defer provider and allocation return controlled; no actual ISR queue or allocator in direct profile. PendSV requests are not delivered here; no automatic scheduler or hardware timing claim.','Fatal inputs observe invalid store rather than HardFault delivery; no firmware byte identity or full source completion.'])
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['status','cases','distinct_original_trace_bytes']}))
if __name__=='__main__':main()
