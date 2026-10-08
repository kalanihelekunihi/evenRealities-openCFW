#!/usr/bin/env python3
"""Original/source ISR queues, notification deferral and callback delivery."""
import argparse,importlib.util,itertools,json,struct
from pathlib import Path
s=importlib.util.spec_from_file_location('mutex_fixture',Path(__file__).with_name('verify_mutex_kernel.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);v=m.v
Q=m.Q;T=m.T;W=m.O;BUF=0x20010000;MSG=0x20002000;OUT=0x20002100;FLAG=OUT+12;EVENT=0x20012000;BLOCK=0x20009000
ENTRIES={'opencfw_bl_kernel_queue_put_from_isr':0x41a024,'opencfw_bl_kernel_queue_get_from_isr':0x41a3b0,'opencfw_boot_isr_thread_notify':0x418fe8,'opencfw_boot_pend_callback_isr':0x4196e6,'opencfw_bl_event_flags_set_isr':0x419bd2,'opencfw_boot_event_flags_deferred':0x419bae,'opencfw_boot_kernel_queue_reset':0x419be8,'opencfw_bl_timer_process_commands':0x419546,'opencfw_bl_scheduler_resume':0x418228,'opencfw_boot_timer_queue_unlock':0x41a556}
class Machine(m.Machine):
 def seed_queue(self,count=0,size=4,capacity=3,lock=-1,priority=6,suspended=0,wait=None,flag=17):
  self.seed(priority=priority,ready=False,current_priority=3);self.w(Q,BUF);self.w(Q+4,BUF);self.w(Q+8,BUF+capacity*size);self.w(Q+12,BUF+(capacity-1)*size);self.w(Q+56,count);self.w(Q+60,capacity);self.w(Q+64,size);self.cpu.mem_write(Q+68,bytes([lock&255,lock&255]));self.cpu.mem_write(BUF,bytes(range(64)));self.cpu.mem_write(MSG,bytes(range(64,128)));self.cpu.mem_write(OUT,bytes([0xaa])*16);self.w(FLAG,flag);self.w(0x20027144,4);self.w(0x2002716c,suspended);self.w(0x20027158,0);self.w(0x200004c4,0);self.w(0x20027150,0);self.w(0x20027180,Q)
  for addr in [Q+16,Q+36,0x20026f5c,BLOCK,BLOCK+32,EVENT+4]:self.list_init(addr)
  self.w(0x20027138,BLOCK);self.w(0x2002713c,BLOCK+32);self.w(0x20027164,0xffffffff);self.w(EVENT,0x10);self.w(W+40,0);self.w(W+36,W);self.w(T+36,T)
  if wait:self.block_target();self.append(Q+(36 if wait=='receive' else 16),W+24,56-priority)
 def list_init(self,addr):
  for off,val in [(0,0),(4,addr+8),(8,0xffffffff),(12,addr+8),(16,addr+8)]:self.w(addr+off,val)
 def append(self,addr,item,key):
  anchor=self.u(addr+4);previous=self.u(anchor+8);self.w(item,key);self.w(item+4,anchor);self.w(item+8,previous);self.w(item+12,W);self.w(item+16,addr);self.w(previous+4,item);self.w(anchor+8,item);self.w(addr,self.u(addr)+1)
 def block_target(self):self.append(BLOCK,W+4,77)
 def callback(self):return self.symbols['opencfw_boot_event_flags_deferred'] if self.source else 0x419baf
 def call(self,name,args):
  self.finished=False;self.fatal=False;self.cpu.reg_write(v.a.UC_ARM_REG_XPSR,0x01000000);self.cpu.reg_write(v.a.UC_ARM_REG_SP,v.SP);self.cpu.reg_write(v.a.UC_ARM_REG_LR,v.STOP|1)
  for reg,value in zip([v.a.UC_ARM_REG_R0,v.a.UC_ARM_REG_R1,v.a.UC_ARM_REG_R2,v.a.UC_ARM_REG_R3],args+[0]*4):self.cpu.reg_write(reg,value)
  for index,value in enumerate(args[4:]):self.w(v.SP+4*index,value)
  pc=(self.symbols[name]&~1) if self.source else ENTRIES[name]
  try:self.cpu.emu_start(pc|1,v.STOP+2,count=400000)
  except Exception:
   if not self.fatal:raise
  assert self.finished,(name,self.source,hex(self.cpu.reg_read(v.a.UC_ARM_REG_PC)))
  return None if self.fatal or name in ['opencfw_boot_event_flags_deferred','opencfw_bl_timer_process_commands','opencfw_boot_timer_queue_unlock'] else self.cpu.reg_read(v.a.UC_ARM_REG_R0)
 def snapshot(self,returns):
  buffer=bytearray(self.cpu.mem_read(BUF,64))
  # Normalize only authenticated callback relocation fields of deferred records.
  for off in range(0,64,16):
   if struct.unpack_from('<I',buffer,off)[0]==0xfffffffe and struct.unpack_from('<I',buffer,off+4)[0]==self.callback():struct.pack_into('<I',buffer,off+4,0x419baf)
  return dict(returns=returns,fatal=self.fatal,queue=bytes(self.cpu.mem_read(Q,80)).hex(),buffer=buffer.hex(),output=bytes(self.cpu.mem_read(OUT,16)).hex(),event=bytes(self.cpu.mem_read(EVENT,32)).hex(),current=bytes(self.cpu.mem_read(T,128)).hex(),target=bytes(self.cpu.mem_read(W,128)).hex(),ready=bytes(self.cpu.mem_read(m.READY,160)).hex(),blocked=bytes(self.cpu.mem_read(BLOCK,20)).hex(),pending=bytes(self.cpu.mem_read(0x20026f5c,20)).hex(),highest=self.u(0x2002714c),yield_word=self.u(0x20027158),suspended=self.u(0x2002716c),basepri=self.cpu.reg_read(v.a.UC_ARM_REG_BASEPRI),primask=self.cpu.reg_read(v.a.UC_ARM_REG_PRIMASK),nesting=self.u(0x200004c4),icsr=self.u(0xe000ed04))
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();assert v.sha(v.BLOB)==v.SHA;_,segs,syms=v.elf.elf_info(a.elf);cases=[];trace={}
 def compare(label,fixture,steps,prepare=None):
  outputs=[]
  for source in [False,True]:
   x=Machine(source,segs,syms);x.seed_queue(**fixture)
   if prepare:prepare(x)
   results=[]
   for name,params in steps:
    if callable(params):params=params(x)
    try:results.append(x.call(name,params))
    except Exception:
     print("FAILURE",label,source,hex(x.cpu.reg_read(v.a.UC_ARM_REG_PC)),x.invalid if hasattr(x,"invalid") else "",x.args(),list(x.trace)[-12:]);raise
    if x.fatal:break
   outputs.append(x.snapshot(results))
   if not source:trace.update(x.trace)
  assert outputs[0]==outputs[1],(label,fixture,{k:[o[k] for o in outputs] for k in outputs[0] if outputs[0][k]!=outputs[1][k]})
  cases.append(dict(label=label,fixture=fixture,observed=outputs[0]));return outputs[0]
 for op,count,size,lock,wake,suspended,priority in itertools.product(['put','get'],[0,1,3],[0,1,4,8],[-2,-1,0,3,4,127],[False,True],[0,1],[2,6]):
  name='opencfw_bl_kernel_queue_'+op+'_from_isr';fixture=dict(count=count,size=size,lock=lock,priority=priority,suspended=suspended,wait=('receive' if op=='put' else 'send') if wake else None)
  compare(str((op,count,size,lock,wake,suspended,priority)),fixture,[(name,[Q,MSG,FLAG,0] if op=='put' else [Q,OUT,FLAG])])
 for mode,count in itertools.product([0,1,2,256],[0,1]):compare('overwrite-'+str((mode,count)),dict(count=count,capacity=1),[('opencfw_bl_kernel_queue_put_from_isr',[Q,MSG,FLAG,mode])])
 for op in ['put','get']:
  for ptr,message in [(0,MSG),(Q,0)]:compare('assert-'+op+str((ptr,message)),{},[('opencfw_bl_kernel_queue_'+op+'_from_isr',[ptr,message,FLAG,0] if op=='put' else [ptr,message,FLAG])])
 for old,action,suspended,priority,flagptr in itertools.product([0,1,2,255],[0,1,2,3,4,5,256,260],[0,1],[2,6],[0,FLAG]):
  def prep(x):x.w(W+104,0xffffffff);x.cpu.mem_write(W+108,bytes([old]));x.w(OUT,0xcccccccc);x.block_target() if old==1 else None
  compare('notify-'+str((old,action,suspended,priority,flagptr)),dict(suspended=suspended,priority=priority),[('opencfw_boot_isr_thread_notify',[W,0,5,action,OUT,flagptr])],prep)
 for target,index,now,old,event_container in [(0,0,0,0,0),(W,1,0,0,0),(W,0,1,0,0),(W,0,0,1,1)]:
  def prep(x):x.w(0x20027148,now);x.cpu.mem_write(W+108,bytes([old]));x.w(W+40,event_container)
  compare('notify-fatal-'+str((target,index,now,old,event_container)),{},[('opencfw_boot_isr_thread_notify',[target,index,1,5,OUT,FLAG])],prep)
 for op,lock,tasks in itertools.product(['put','get'],[3,127,-2],[4,128,0xffffffff]):
  def prep(x):x.w(0x20027144,tasks)
  compare('lock-cap-'+str((op,lock,tasks)),dict(count=1,lock=lock),[('opencfw_bl_kernel_queue_'+op+'_from_isr',[Q,MSG,FLAG,0] if op=='put' else [Q,OUT,FLAG])],prep)
 for op in ['put','get']:
  compare('null-wake-'+op,dict(count=1,wait='receive' if op=='put' else 'send'),[('opencfw_bl_kernel_queue_'+op+'_from_isr',[Q,MSG,0,0] if op=='put' else [Q,OUT,0])])
 for op in ['put','get']:
  compare('pending-ready-resume-'+op,dict(count=1,suspended=1,wait='receive' if op=='put' else 'send'),[('opencfw_bl_kernel_queue_'+op+'_from_isr',[Q,MSG,FLAG,0] if op=='put' else [Q,OUT,FLAG]),('opencfw_bl_scheduler_resume',[])])
 def prep_notify(x):x.cpu.mem_write(W+108,b'\x01');x.block_target()
 compare('notify-pending-resume',dict(suspended=1),[('opencfw_boot_isr_thread_notify',[W,0,7,3,OUT,FLAG]),('opencfw_bl_scheduler_resume',[])],prep_notify)
 for op in ['put','get']:
  compare('locked-unlock-delivers-'+op,dict(count=1,lock=0,suspended=1,wait='receive' if op=='put' else 'send'),[('opencfw_bl_kernel_queue_'+op+'_from_isr',[Q,MSG,FLAG,0] if op=='put' else [Q,OUT,FLAG]),('opencfw_boot_timer_queue_unlock',[Q]),('opencfw_bl_scheduler_resume',[])])
 for count,wait,suspended in itertools.product([0,2,3],[False,True],[0,1]):
  f=dict(count=count,size=16,suspended=suspended,wait='receive' if wait else None)
  def prep(x):x.cpu.mem_write(BUF,bytes(64))
  r=compare('defer-enqueue-'+str((count,wait,suspended)),f,[('opencfw_bl_event_flags_set_isr',[EVENT,3,FLAG])],prep);assert r['returns']==[0 if count==3 else 1];assert int.from_bytes(bytes.fromhex(r['event'])[:4],'little')==0x10
 for clear,all_bits in itertools.product([False,True],[False,True]):
  def prep(x):
   x.cpu.mem_write(BUF,bytes(64));x.block_target();x.append(EVENT+4,W+24,3|(0x01000000 if clear else 0)|(0x04000000 if all_bits else 0))
  r=compare('defer-delivery-'+str((clear,all_bits)),dict(size=16),[('opencfw_bl_event_flags_set_isr',[EVENT,3,FLAG]),('opencfw_bl_timer_process_commands',[])],prep);assert r['returns'][0]==1;assert int.from_bytes(bytes.fromhex(r['queue'])[56:60],'little')==0
 def prep(x):x.cpu.mem_write(BUF,bytes(64))
 r=compare('reset-discards-deferred',dict(size=16),[('opencfw_bl_event_flags_set_isr',[EVENT,3,FLAG]),('opencfw_boot_kernel_queue_reset',[Q,0]),('opencfw_bl_timer_process_commands',[])],prep);assert int.from_bytes(bytes.fromhex(r['event'])[:4],'little')==0x10
 for is_new,count,wake in itertools.product([0,1],[0,1,3],[False,True]):compare('reset-'+str((is_new,count,wake)),dict(count=count,wait='send' if wake else None),[('opencfw_boot_kernel_queue_reset',[Q,is_new])])
 for capacity,size in [(0,4),(0x80000000,4)]:compare('reset-fatal-'+str((capacity,size)),dict(capacity=capacity,size=size),[('opencfw_boot_kernel_queue_reset',[Q,0])])
 blob=v.BLOB.read_bytes();assert all(bytes.fromhex(raw)==blob[int(pc,16)-v.BASE:int(pc,16)-v.BASE+len(bytes.fromhex(raw))] for pc,raw in trace.items())
 ranges={n:[lo,hi] for n,lo,hi in [('opencfw_bl_kernel_queue_put_from_isr',0x41a024,0x41a114),('opencfw_bl_kernel_queue_get_from_isr',0x41a3b0,0x41a470),('opencfw_boot_isr_thread_notify',0x418fe8,0x419184),('opencfw_boot_pend_callback_isr',0x4196e6,0x419708),('opencfw_boot_event_flags_deferred',0x419bae,0x419bb6),('opencfw_bl_event_flags_set_isr',0x419bd2,0x419be2),('opencfw_boot_kernel_queue_reset',0x419be8,0x419c9c),('opencfw_boot_queue_isr_task_count',0x41836c,0x418372)]}
 used={int(pc,16)+i for pc,raw in trace.items() for i in range(len(bytes.fromhex(raw)))}
 r=dict(status='PASS',cases=len(cases),elf_sha256=v.sha(a.elf),original_sha256=v.SHA,runner_sha256=v.sha(Path(__file__)),original_trace=trace,body_ranges=ranges,visited_body_bytes={n:len(used&set(range(lo,hi))) for n,(lo,hi) in ranges.items()},comparisons=cases,limits=['Original/source ISR queue copy/wake/lock counters, notification state/list moves, defer enqueue, native timer drain and native flags callback execute. ELF-only source execution; callback word normalized only at recognized16-byte deferred records.','Synthetic coherent SRAM/list/TCB and masks; calls are entered in thread mode, not actual asynchronous exception delivery. BASEPRI/PRIMASK restoration compares; no IRQ priority nesting/timing proof.','Deferred enqueue success does not mean callback already ran. Queue records copy16 bytes; event pointer borrowed with no lifetime extension. Native queue reset discards pending records without callbacks/free; no whole-system cancellation/delete/drain guarantee.','Fatal assertions stop at invalid store. Lock127 saturation is tested at synthetic task count128; default4-task fixtures cap without increment. Pending-ready resume and lock-unlock delivery use native scheduler helpers, but no task instructions or asynchronous IRQ delivery execute.'])
 a.output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(dict(status='PASS',cases=len(cases),visited_body_bytes=r['visited_body_bytes'],elf_sha256=r['elf_sha256'])))
if __name__=='__main__':main()
