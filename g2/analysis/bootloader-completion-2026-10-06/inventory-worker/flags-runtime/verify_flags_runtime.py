#!/usr/bin/env python3
"""Original/source tests of stock event-flag waiter insertion 0x41866a."""
import argparse, importlib.util, json
from pathlib import Path
from unicorn import UC_HOOK_MEM_INVALID

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[4]
spec=importlib.util.spec_from_file_location('bootverify',ROOT/'g2/components/bootloader/update_core/verify.py')
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
ENTRY=0x41866a;v.ENTRIES.update({'event_waiter_link':ENTRY,'flags_wait':0x416590,'flags_wait_core':0x4199dc})
KERNEL_READY=0x2002716c;CURRENT_TCB=0x20027134
EVENT=0x20009000;ANCHOR=0x20009100;EXISTING=0x20009200;TCB=0x20008000;WAIT_COUNT=EVENT+4

class M(v.Machine):
 def __init__(self,source=False,segs=(),syms=None):
  super().__init__(source,segs,syms);self.events=[];self.faults=[]
  self.cpu.hook_add(UC_HOOK_MEM_INVALID,self.invalid_memory)
  if source:
   self.symbols['opencfw_boot_event_waiter_link']=self.symbols['opencfw_provider_41866a']
   self.symbols['opencfw_boot_flags_wait']=self.symbols['opencfw_provider_416590']
   self.symbols['opencfw_boot_flags_wait_core']=self.symbols['opencfw_provider_4199dc']
 def code(self,uc,pc,size,user):
  if pc==0x419186:
   args=self.args();self.events.append(['task_block',args[0],args[1]])
   if isinstance(self.fixture,dict) and self.fixture.get('thread_wait_field') is not None:
    self.w(TCB+24,self.fixture['thread_wait_field'])
   self.ret(0);return
  if pc==0x41b2f8:
   self.events.append(['mask_interrupts']);self.ret(0);return
  if pc==0x41602a:
   value=self.fixture.get('privileged_or_isr',0);self.events.append(['privilege_check',value]);self.ret(value);return
  if pc==0x418b56:
   value=self.fixture.get('runtime_mode',1);self.events.append(['runtime_mode',value]);self.ret(value);return
  if pc==0x4181d8:
   self.events.append(['scheduler_suspend']);self.ret(0);return
  if pc==0x418228:
   value=self.fixture.get('scheduler_resume',1);self.events.append(['scheduler_resume',value]);self.ret(value);return
  if pc==0x41b3d0:
   self.events.append(['kernel_reschedule']);self.ret(0);return
  if pc==0x41b3e4:
   value=self.fixture.get('wake_flags')
   if value is not None:uc.mem_write(self.fixture['event_address'],value.to_bytes(4,'little'))
   self.events.append(['kernel_enter']);self.ret(0);return
  if pc==0x41b3fc:
   self.events.append(['kernel_exit']);self.ret(0);return
  super().code(uc,pc,size,user)
 def invalid_memory(self,uc,access,address,size,value,user):
  self.faults.append([access,address,size,value]);return False
 def setup(self,has_existing,flags,ticks):
  self.events=[];self.w(KERNEL_READY,0x20007000);self.w(CURRENT_TCB,TCB)
  self.w(EVENT,0x0f0f);self.w(WAIT_COUNT,7);self.w(EVENT+8,ANCHOR)
  # Anchor and waiter links use two words at offsets +4/+8. Empty means
  # self-linked; otherwise insert the current waiter between anchor/existing.
  self.w(ANCHOR+4,EXISTING if has_existing else ANCHOR)
  self.w(ANCHOR+8,EXISTING if has_existing else ANCHOR)
  if has_existing:
   self.w(EXISTING+4,ANCHOR);self.w(EXISTING+8,ANCHOR)
  self.w(TCB+24,0);self.w(TCB+28,0);self.w(TCB+32,0);self.w(TCB+40,0);self.w(TCB+44,8)
  self.fixture=(flags,ticks)
 def invoke(self,has_existing,flags,ticks):
  self.setup(has_existing,flags,ticks)
  try:r=self.run('event_waiter_link',[WAIT_COUNT,flags,ticks])
  except Exception:
   print('failure',self.source,hex(self.cpu.reg_read(v.a.UC_ARM_REG_PC)))
   raise
  r['events']=self.events
  r['state']={'wait_count':self.u(WAIT_COUNT),'tcb_flags':self.u(TCB+24),
   'tcb_prev':self.u(TCB+28),'tcb_next':self.u(TCB+32),'tcb_wait_object':self.u(TCB+40),
   'anchor_prev':self.u(ANCHOR+4),'anchor_next':self.u(ANCHOR+8),
   'existing_prev':self.u(EXISTING+4),'existing_next':self.u(EXISTING+8)}
  return r

 def invoke_flags(self,event,mask,options,timeout,fixture):
  self.events=[]
  self.setup(False,0,timeout)
  self.fixture=dict(fixture);self.fixture['event_address']=event
  if event:
   self.w(event,fixture.get('initial_flags',0));self.w(event+4,fixture.get('waiter_count',0));self.w(event+8,ANCHOR)
  self.w(ANCHOR+4,ANCHOR);self.w(ANCHOR+8,ANCHOR)
  r=self.run('flags_wait',[event,mask,options,timeout]);r['providers']=self.events
  if event:
   r['event_flags']=self.u(event);r['waiter_count']=self.u(event+4)
   r['tcb_wait_node']=[self.u(TCB+24),self.u(TCB+28),self.u(TCB+32),self.u(TCB+40)]
  return r

 def invoke_flags_core(self,event,mask,clear,wait_all,timeout,fixture):
  self.events=[]
  self.setup(False,0,timeout)
  self.fixture=dict(fixture);self.fixture['event_address']=event
  self.w(event,fixture.get('initial_flags',0));self.w(event+4,fixture.get('waiter_count',0));self.w(event+8,ANCHOR)
  self.w(ANCHOR+4,ANCHOR);self.w(ANCHOR+8,ANCHOR)
  self.w(v.SP,timeout)
  r=self.run('flags_wait_core',[event,mask,clear,wait_all]);r['providers']=self.events
  r['event_flags']=self.u(event);r['waiter_count']=self.u(event+4)
  r['tcb_wait_node']=[self.u(TCB+24),self.u(TCB+28),self.u(TCB+32),self.u(TCB+40)]
  return r

 def invoke_fatal_core(self,event,mask,timeout,fixture):
  self.events=[];self.faults=[];self.setup(False,0,timeout)
  self.fixture=dict(fixture);self.fixture['event_address']=event
  if event:self.w(event,0);self.w(event+4,0);self.w(event+8,ANCHOR)
  self.w(v.SP,timeout)
  try:self.run('flags_wait_core',[event,mask,0,0])
  except Exception:pass
  return {'providers':self.events,'faults':self.faults}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
 _,segs,syms=v.elf.elf_info(a.elf);cases=[];trace={}
 for has_existing,flags,ticks in [(False,1,0),(False,0x400000,13),(True,0x800000,0),(True,0x100000,0xffffffff)]:
  ms=[M(),M(True,segs,syms)];rs=[m.invoke(has_existing,flags,ticks) for m in ms]
  keys=('events','state');assert all(rs[0][k]==rs[1][k] for k in keys),(has_existing,flags,ticks,rs)
  trace.update(ms[0].trace);cases.append({'existing_waiter':has_existing,'flags':flags,'timeout_argument_raw':ticks,'state':rs[0]['state'],'providers':rs[0]['events']})
 wait_rows=[(EVENT,3,0,50,{'initial_flags':2}),
  (EVENT,3,2,50,{'initial_flags':2}),
  (EVENT,3,0,0,{'initial_flags':0}),
  (EVENT,3,3,20000,{'initial_flags':3}),
  (EVENT,3,1,20000,{'initial_flags':1}),
  (EVENT,0x01000000,0,0,{}),(0,1,0,1,{}),
  (EVENT,1,0,0,{'privileged_or_isr':1}),
  (EVENT,1,0,1,{'privileged_or_isr':1})]
 for event,mask,options,timeout,fixture in wait_rows:
  ms=[M(),M(True,segs,syms)];rs=[m.invoke_flags(event,mask,options,timeout,fixture) for m in ms]
  left=(rs[0]['return'],rs[0]['providers'],rs[0].get('event_flags'),rs[0].get('waiter_count'),rs[0].get('tcb_wait_node'))
  right=(rs[1]['return'],rs[1]['providers'],rs[1].get('event_flags'),rs[1].get('waiter_count'),rs[1].get('tcb_wait_node'))
  assert left==right,(event,mask,options,timeout,fixture,left,right)
  trace.update(ms[0].trace);cases.append({'function':'flags_wait','arguments':[event,mask,options,timeout],'fixture':fixture,'return':left[0],'providers':left[1]})
 core_rows=[(EVENT,1,1,0,0,{'initial_flags':3,'runtime_mode':1}),
  (EVENT,3,1,1,0,{'initial_flags':1,'runtime_mode':1}),
  (EVENT,2,1,0,25,{'initial_flags':0,'wake_flags':2,'runtime_mode':1}),
  (EVENT,2,0,0,25,{'initial_flags':0,'wake_flags':2,'runtime_mode':1}),
  (EVENT,3,1,1,25,{'initial_flags':0,'wake_flags':3,'runtime_mode':1}),
  (EVENT,2,1,0,25,{'initial_flags':0,'wake_flags':2,'runtime_mode':1,'scheduler_resume':0,'thread_wait_field':0x02000002})]
 for event,mask,clear,wait_all,timeout,fixture in core_rows:
  ms=[M(),M(True,segs,syms)];rs=[m.invoke_flags_core(event,mask,clear,wait_all,timeout,fixture) for m in ms]
  left=(rs[0]['return'],rs[0]['providers'],rs[0]['event_flags'],rs[0]['waiter_count'],rs[0]['tcb_wait_node'])
  right=(rs[1]['return'],rs[1]['providers'],rs[1]['event_flags'],rs[1]['waiter_count'],rs[1]['tcb_wait_node'])
  assert left==right,(event,mask,clear,wait_all,timeout,fixture,left,right)
  trace.update(ms[0].trace);cases.append({'function':'flags_wait_core','arguments':[event,mask,clear,wait_all,timeout],'fixture':fixture,'return':left[0],'providers':left[1],'event_flags':left[2],'waiter_count':left[3],'tcb_wait_node':left[4]})
 for event,mask,timeout,fixture in [(0,1,0,{}),(EVENT,1,25,{'runtime_mode':0})]:
  ms=[M(),M(True,segs,syms)];rs=[m.invoke_fatal_core(event,mask,timeout,fixture) for m in ms]
  assert rs[0]==rs[1] and rs[0]['faults'] and rs[0]['faults'][0][1]==0xffffffff,(event,mask,timeout,fixture,rs)
  trace.update(ms[0].trace);cases.append({'function':'flags_wait_core_fatal','arguments':[event,mask,timeout],'fixture':fixture,'observation':rs[0]})
 used={int(pc,0)+i for pc,raw in trace.items() for i in range(len(bytes.fromhex(raw)))}
 out={'status':'PASS','cases':len(cases),'original_sha256':v.SHA,'elf_sha256':v.sha(a.elf),'distinct_original_instruction_bytes':len(used),'original_trace':trace,'comparisons':cases,'source_sha256':{p.name:v.sha(p) for p in [HERE/'verify_flags_runtime.py',ROOT/'g2/components/bootloader/flags_runtime/flags_runtime.c',ROOT/'g2/components/bootloader/flags_runtime/cmsis_notifications.c',ROOT/'g2/components/bootloader/flags_runtime/flags_runtime.h',ROOT/'g2/components/bootloader/flags_runtime/module.ld']},'limits':['Original/source execution covers 0x416590 -> 0x4199DC -> 0x41866A plus the actual 0x418d7a TCB wait-result accessor; flags, wait-node, list and fatal writes are checked against original instructions. Event/TCB RAM and task state are synthetic fixtures.','Kernel timeout registration, scheduler handoff/resume and critical-section implementations remain injected providers; tests compare calls and relevant state, not full scheduler/concurrency semantics.','Timeout values are raw; no tick rate is inferred. No device behavior is exercised.']}
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:out[k] for k in ('status','cases','distinct_original_instruction_bytes')},indent=2))
if __name__=='__main__':main()
