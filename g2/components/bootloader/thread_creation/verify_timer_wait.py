#!/usr/bin/env python3
"""Compare actual initial timer blocking/list moves, preserving synthetic clocks."""
import argparse,importlib.util,itertools,json
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
spec=importlib.util.spec_from_file_location('priority',HERE/'verify_priority.py');p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p);v=p.v
v.ENTRIES.update(task_block=0x419186,wait_list_append=0x4186dc,timer_queue_wait=0x41a5fe,timer_queue_unlock=0x41a556,timer_next_expiry=0x4194be,timer_sample_time=0x4194e2,timer_wait_expiry=0x419458)
QUEUE=0x20026da0;OUT=0x20030180
class Machine(p.Machine):
 def code(self,uc,pc,size,user):
  if pc in (0x419406,0x41965c,0x4189a2):
   self.events.append([hex(pc),self.args()[:2] if pc==0x419406 else []]);self.ret();return
  if pc==0x41872c:
   self.events.append(['event-remove-provider',self.args()[0]]);self.w(self.args()[0],0);self.ret(1);return
  super().code(uc,pc,size,user)
def init(m,now,cursor=False):
 cb=p.initialize(m,True,False,True,cursor,False,0)
 for addr in [0x20026f48,0x20026f5c,0x20026f70,0x20026f84,0x20026f98,0x20026fac,QUEUE+16,QUEUE+36]:
  for off,val in [(0,0),(4,addr+8),(8,0xffffffff),(12,addr+8),(16,addr+8)]:m.w(addr+off,val)
 m.w(0x20027138,0x20026f34);m.w(0x2002713c,0x20026f48);m.w(0x20027148,now);m.w(0x20027164,0xffffffff);m.w(0x20027144,1)
 m.w(0x20027178,0x20026f98);m.w(0x2002717c,0x20026fac);m.w(0x20027180,QUEUE);m.w(0x20027188,now)
 m.cpu.mem_write(QUEUE+0x44,b'\xff\xff');m.w(QUEUE+0x38,0);return cb
def state(m):
 return dict(events=m.events,regions={hex(a):bytes(m.cpu.mem_read(a,n)).hex() for a,n in [(0x20024870,1120),(0x20026f34,120),(QUEUE,80),(0x20027130,100),(0x20030000,112),(OUT,4)]},basepri=m.cpu.reg_read(v.a.UC_ARM_REG_BASEPRI),nesting=m.u(0x200004c4),icsr=m.u(0xe000ed04))
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();assert v.sha(v.BLOB)==v.SHA
 _,segs,syms=v.elf.elf_info(a.elf);trace={};cases=[];fixtures=[]
 for now,ticks,indef,cursor in itertools.product([0,17,0xfffffff0],[0,1,32,0xffffffff],[0,1],[False,True]):
  for entry,args in [('task_block',[ticks,indef]),('wait_list_append',[QUEUE+36,ticks,indef]),('timer_queue_wait',[QUEUE,ticks,indef])]:fixtures.append((entry,args,dict(now=now,cursor=cursor)))
 for now,expiry,empty,wrapped in itertools.product([0,17,0xfffffff0],[0,16,32,0xffffffff],[0,1],[False,True]):fixtures.append(('timer_wait_expiry',[expiry,empty],dict(now=now,wrapped=wrapped)))
 for locks,counts in itertools.product([(-1,-1),(0,0),(1,1),(2,3)],[(0,0),(1,1)]):fixtures.append(('timer_queue_unlock',[QUEUE],dict(now=0,locks=locks,counts=counts)))
 for entry,args,f in fixtures:
  pair=[Machine(),Machine(True,segs,syms)];states=[]
  for m in pair:
   init(m,f['now'],f.get('cursor',False))
   if f.get('wrapped'):m.w(0x20027188,0xffffffff)
   if 'locks' in f:m.cpu.mem_write(QUEUE+0x44,bytes(x&255 for x in f['locks']))
   if 'counts' in f:m.w(QUEUE+16,f['counts'][0]);m.w(QUEUE+36,f['counts'][1])
   m.run(entry,args);states.append(state(m))
  assert states[0]==states[1],(entry,args,f,states)
  trace.update(pair[0].trace);cases.append(dict(entry=entry,args=args,fixture=f,result=states[0]))
 used={int(pc,0)+i for pc,b in trace.items() for i in range(len(bytes.fromhex(b)))}
 report=dict(status='PASS',cases=len(cases),distinct_original_trace_bytes=len(used),original_sha256=v.SHA,elf_sha256=v.sha(a.elf),source_sha256={str(HERE.joinpath(n).relative_to(ROOT)):v.sha(HERE/n) for n in ['timer_wait.c','timer_wait.h','timer_wait_module.ld','verify_timer_wait.py','kernel_runtime.c','scheduler_resume.c']},original_trace=trace,comparisons=cases,limits=['Actual list unlink/sorted insert, timeout vs indefinite suspend, timer initial block, critical section, scheduler suspend/resume and PendSV-request store execute. Coherent synthetic lists/TCB and tick values; no automatic exception delivery.','Timer expiration/rollover/event-wake/missed-yield are intercepted providers. Queue unlock wake cases clear synthetic count and return1; no real event delivery asserted. Timer command processing is not executed in these direct helper fixtures.','Both finite wrapped/nonwrapped timeout lists and indefinite suspend tested. No physical timer or hardware boot/byte identity claim.'])
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['status','cases','distinct_original_trace_bytes']}))
if __name__=='__main__':main()
