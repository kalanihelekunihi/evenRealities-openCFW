#!/usr/bin/env python3
"""Original/source mutex state comparisons; explicit scheduling fixtures."""
import argparse,importlib.util,itertools,json,struct
from pathlib import Path
from unicorn import UC_HOOK_MEM_INVALID
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
spec=importlib.util.spec_from_file_location('mutex_base',ROOT/'g2/components/bootloader/update_core/verify.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
ENTRIES={'opencfw_boot_mutex_acquire':0x4166aa,'opencfw_boot_mutex_release':0x416710,'opencfw_bl_kernel_mutex_take_plain':0x41a24e,'opencfw_bl_kernel_mutex_take_tagged':0x419e22,'opencfw_bl_kernel_mutex_give_tagged':0x419de2,'opencfw_boot_current_task':0x418b4e,'opencfw_boot_mutex_claim_current':0x418d90,'opencfw_boot_mutex_inherit':0x418b7c,'opencfw_boot_mutex_disinherit_timeout':0x418ccc,'opencfw_boot_mutex_waiter_priority':0x41a492}
Q=0x20003000;T=0x20006000;O=0x20006400;READY=0x20024870
class Machine(v.Machine):
 def __init__(self,*args,**kw):
  super().__init__(*args,**kw);self.cpu.hook_add(UC_HOOK_MEM_INVALID,self.invalid);self.fatal=False;self.script=None;self.timeout_checks=0;self.events=[]
 def invalid(self,uc,access,address,size,value,user):
  if address==0xffffffff:self.fatal=True;self.finished=True;uc.emu_stop();return False
  return False
 def code(self,uc,pc,size,user):
  # The scheduling fixture only intercepts documented helper calls, never
  # mutex/priority bodies, queue release, or critical-section helpers.
  boundaries={'opencfw_boot_timeout_check':0x418922,'opencfw_boot_wait_list_sorted':0x41863e,'opencfw_bl_scheduler_suspend':0x4181d8,'opencfw_bl_scheduler_resume':0x418228,'opencfw_boot_timer_queue_unlock':0x41a556}
  if self.script:
   for name,stock in boundaries.items():
    entry=(self.symbols[name]&~1) if self.source else stock
    if pc!=entry:continue
    r0,r1,_,_=self.args()
    if name=='opencfw_boot_timeout_check':
     self.timeout_checks+=1;expired=self.timeout_checks>=2 or self.script in ['expire','expire_race'];
     if self.script in ['race','expire_race']:self.w(Q+56,1)
     self.events.append(['timeout_check',expired]);self.ret(int(expired))
    elif name=='opencfw_boot_wait_list_sorted':
     self.events.append(['wait',r0,r1])
     if self.script=='wake':self.w(Q+56,1)
     self.ret()
    else:self.events.append([name]);self.ret(1 if name=='opencfw_bl_scheduler_resume' else 0)
    return
  super().code(uc,pc,size,user)
 def seed(self,owner=O,token=1,depth=0,priority=2,current_priority=5,base=2,held=1,ready=True,event_high=False,current=T,item_size=0,queue_kind=0,current_held=0,waiter=False):
  self.cpu.mem_write(Q,bytes(80));self.w(Q+8,owner);self.w(Q+12,depth);self.w(Q+56,token);self.w(Q+60,1);self.w(Q+64,item_size);self.w(Q,queue_kind);self.cpu.mem_write(Q+68,b'\xff\xff');self.w(0x20027134,current);self.w(0x20027150,0);self.w(0x2002716c,1);self.w(0x2002714c,0);self.w(0x20027144,0)
  for task,p,b,n in [(T,current_priority,current_priority,current_held),(O,priority,base,held)]:
   self.cpu.mem_write(task,bytes(128));self.w(task+44,p);self.w(task+96,b);self.w(task+100,n);self.w(task+24,(0x80000000 if event_high else 56-p))
  for p in range(8):
   l=READY+20*p;anchor=l+8;self.w(l,0);self.w(l+4,anchor);self.w(anchor,0xffffffff);self.w(anchor+4,anchor);self.w(anchor+8,anchor)
  if ready:
   l=READY+20*priority;anchor=l+8;self.w(l,1);self.w(anchor+4,O+4);self.w(anchor+8,O+4);self.w(O+8,anchor);self.w(O+12,anchor);self.w(O+20,l)
  else:self.w(O+20,0x20009000)
  if waiter:self.w(Q+36,1);self.w(Q+48,O+24)
 def run_entry(self,name,args):
  self.finished=False;self.fatal=False;self.cpu.reg_write(v.a.UC_ARM_REG_XPSR,0x01000000);self.cpu.reg_write(v.a.UC_ARM_REG_SP,v.SP);self.cpu.reg_write(v.a.UC_ARM_REG_LR,v.STOP|1)
  for r,x in zip([v.a.UC_ARM_REG_R0,v.a.UC_ARM_REG_R1,v.a.UC_ARM_REG_R2,v.a.UC_ARM_REG_R3],args+[0]*4):self.cpu.reg_write(r,x)
  entry=(self.symbols[name]&~1) if self.source else ENTRIES[name]
  try:self.cpu.emu_start(entry|1,v.STOP+2,count=200000)
  except Exception:
   if not self.fatal:raise
  assert self.finished,(name,self.source,hex(self.cpu.reg_read(v.a.UC_ARM_REG_PC)))
  return dict(return_value=None if self.fatal or name=='opencfw_boot_mutex_disinherit_timeout' else self.cpu.reg_read(v.a.UC_ARM_REG_R0),fatal=self.fatal,queue=bytes(self.cpu.mem_read(Q,80)).hex(),tasks=bytes(self.cpu.mem_read(T,128)).hex()+bytes(self.cpu.mem_read(O,128)).hex(),ready=bytes(self.cpu.mem_read(READY,160)).hex(),highest=self.u(0x2002714c),events=self.events,primask=self.cpu.reg_read(v.a.UC_ARM_REG_PRIMASK),basepri=self.cpu.reg_read(v.a.UC_ARM_REG_BASEPRI))
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args();assert v.sha(v.BLOB)==v.SHA;_,segments,symbols=v.elf.elf_info(args.elf);cases=[];trace={}
 def check(name,params,fixture=None,script=None,context=None):
  ms=[Machine(),Machine(True,segments,symbols)];out=[]
  for m in ms:
   m.seed(**(fixture or {}));m.script=script
   if context:
    mode,pm,bp=context;m.w(0x20027150,0 if mode==1 else 1);m.w(0x2002716c,0 if mode==2 else 1);m.cpu.reg_write(v.a.UC_ARM_REG_PRIMASK,pm);m.cpu.reg_write(v.a.UC_ARM_REG_BASEPRI,bp)
   out.append(m.run_entry(name,params))
  assert out[0]==out[1],(name,params,fixture,script,{k:[o[k] for o in out] for k in out[0] if out[0][k]!=out[1][k]})
  trace.update(ms[0].trace);cases.append(dict(function=name,args=params,fixture=fixture,script=script,context=context,observed=out[0]))
 for name in ['opencfw_boot_mutex_acquire','opencfw_boot_mutex_release']:
  for tagged,token,owner,depth,context in itertools.product([0,1],[0,1],[T,O],[0,1,2,0xffffffff],[(1,0,0),(0,1,0),(2,0,32)]):
   check(name,[Q|tagged,0],dict(token=token,owner=owner,depth=depth),context=context)
  for handle in [0,1]:check(name,[handle,0])
 for name in ['opencfw_bl_kernel_mutex_take_plain','opencfw_bl_kernel_mutex_take_tagged','opencfw_bl_kernel_mutex_give_tagged']:
  for token,owner,depth in itertools.product([0,1,2],[T,O],[0,1,2,0xffffffff]):check(name,[Q,0],dict(token=token,owner=owner,depth=depth))
  check(name,[0,0])
 for name in ['opencfw_boot_mutex_inherit','opencfw_boot_mutex_disinherit_timeout']:
  for p,current,base,held,ready,high in itertools.product([1,3,6],[2,5],[1,4],[1,2],[False,True],[False,True]):check(name,[O,3],dict(priority=p,current_priority=current,base=base,held=held,ready=ready,event_high=high))
  check(name,[0,3]);check(name,[O,3],dict(held=0));check(name,[T,0],dict(held=1,base=1,current_priority=5))
 for current in [0,T]:check('opencfw_boot_mutex_claim_current',[],dict(current=current))
 check('opencfw_bl_kernel_mutex_take_plain',[Q,0],dict(item_size=1))
 check('opencfw_bl_kernel_mutex_take_plain',[Q,1],context=(0,0,0))
 check('opencfw_boot_mutex_disinherit_timeout',[T,0],dict(current_held=1,current_priority=5))
 for script in ['expire','wake','timeout','race','expire_race']:
  for tagged,ready,held in itertools.product([0,1],[False,True],[1,2]):check('opencfw_boot_mutex_acquire',[Q|tagged,1000],dict(token=0,owner=O,ready=ready,held=held,waiter=True),script=script,context=(1,0,0))
 for kind in [0,1]:check('opencfw_bl_kernel_mutex_take_plain',[Q,0],dict(queue_kind=kind))
 used={int(pc,0)+i for pc,raw in trace.items() for i in range(len(bytes.fromhex(raw)))}
 ranges={n:[ENTRIES[n],hi] for n,hi in [('opencfw_boot_mutex_acquire',0x416710),('opencfw_boot_mutex_release',0x416762),('opencfw_bl_kernel_mutex_take_plain',0x41a3b0),('opencfw_bl_kernel_mutex_take_tagged',0x419e62),('opencfw_bl_kernel_mutex_give_tagged',0x419e22),('opencfw_boot_current_task',0x418b56),('opencfw_boot_mutex_claim_current',0x418da6),('opencfw_boot_mutex_inherit',0x418c1e),('opencfw_boot_mutex_disinherit_timeout',0x418d7a),('opencfw_boot_mutex_waiter_priority',0x41a4a6)]}
 r=dict(status='PASS',cases=len(cases),elf_sha256=v.sha(args.elf),original_sha256=v.SHA,runner_sha256=v.sha(Path(__file__)),original_trace=trace,body_ranges=ranges,visited_body_bytes={n:len(used&set(range(lo,hi))) for n,(lo,hi) in ranges.items()},comparisons=cases,limits=['Original/source mutex wrappers, plain/recursive take/give, owner counters, inheritance/disinheritance and native critical/list/queue-put helpers execute. Source instruction execution restricted to executable ELF segments; no original executable bytes loaded in source machine.','Blocking suites explicitly stub timeout check, wait-list enqueue, suspend/resume and queue unlock. Queue availability is injected at wait enqueue; no real task switch, tick delivery, cancellation, deletion or drain claim.','Fatal null/storage/assert paths stop at invalid store after interrupt mask; this is not recoverable-error behavior. Priority/list updates compare bytes under valid bounded ready-list fixtures; no global scheduler correctness claim.','Timeout1000 is a raw API tick argument; no milliseconds conversion proof. Recursive counters wrap modulo32 bits.'])
 args.output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(dict(status='PASS',cases=len(cases),visited_body_bytes=r['visited_body_bytes'],elf_sha256=r['elf_sha256'])))
if __name__=='__main__':main()
