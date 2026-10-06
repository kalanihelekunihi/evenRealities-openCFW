#!/usr/bin/env python3
"""Instruction-linked timer->manager->event bridge with explicit exception adapter.
No hardware interrupt entry/return is claimed: Python models basic stacking,
EXC_RETURN unstacking and eligible PendSV delivery while stock/source handlers,
selectors, task creation, priority changes and task bodies execute instructions.
"""
import argparse,hashlib,importlib.util,json,struct
from pathlib import Path
from capstone import Cs,CS_ARCH_ARM,CS_MODE_THUMB,CS_MODE_MCLASS
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
spec=importlib.util.spec_from_file_location('startup',HERE/'verify_nor_commands_integrated.py');s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s);v=s.v;c=s.c
REGS=[v.a.UC_ARM_REG_R0,v.a.UC_ARM_REG_R1,v.a.UC_ARM_REG_R2,v.a.UC_ARM_REG_R3,v.a.UC_ARM_REG_R12,v.a.UC_ARM_REG_LR,v.a.UC_ARM_REG_PC,v.a.UC_ARM_REG_XPSR]
class Machine(s.Machine):
 def __init__(self,*args,**kwargs):
  super().__init__(*args,**kwargs);self.phase='startup';self.reason=None;self.task_events=[];self.switches=[]
  self.svc_entry=0x41b374;self.pendsv_entry=0x41b31c;self.svc_return=0x41b2d0;self.pendsv_return=0x41b372
  if self.source:
   dis=Cs(CS_ARCH_ARM,CS_MODE_THUMB|CS_MODE_MCLASS)
   self.svc_entry=self.symbols['opencfw_boot_svc_entry']&~1;self.pendsv_entry=self.symbols['opencfw_boot_pendsv_entry']&~1
   st=self.symbols['opencfw_boot_first_task_restore']&~1
   self.svc_return=next(i.address for i in dis.disasm(bytes(self.cpu.mem_read(st,96)),st) if i.mnemonic=='bx' and i.op_str=='r2')
   self.pendsv_return=next(i.address for i in dis.disasm(bytes(self.cpu.mem_read(self.pendsv_entry,160)),self.pendsv_entry) if i.mnemonic=='bx' and i.op_str=='r3')
  self.new_thread_entry=(self.symbols['opencfw_boot_thread_new']&~1) if self.source else 0x4160fe
  self.queue_new_entry=(self.symbols['opencfw_bl_queue_create']&~1) if self.source else 0x416816
  self.queue_get_entry=(self.symbols['opencfw_bl_queue_get']&~1) if self.source else 0x416920
  self.queue_put_entry=(self.symbols['opencfw_bl_queue_put']&~1) if self.source else 0x4168a2
  self.dfu_task_entry=(self.symbols.get('opencfw_boot_dfu_task',0x42de59)&~1) if self.source else 0x42de58
  self.timer_new_entry=(self.symbols['opencfw_provider_4163b2']&~1) if self.source else 0x4163b2
  self.mutex_new_entry=(self.symbols['opencfw_provider_416610']&~1) if self.source else 0x416610
 def svc(self,uc,number,user):
  assert self.phase=='startup';self.interrupt=number;self.reason='svc';uc.emu_stop()
 def stop(self,why):self.reason=why;self.cpu.emu_stop()
 def code(self,uc,pc,size,user):
  if self.phase in ('svc','pendsv') and pc==(self.svc_return if self.phase=='svc' else self.pendsv_return):self.stop('exception-return');return
  if self.phase=='thread' and self.u(0xe000ed04)&0x10000000 and not uc.reg_read(v.a.UC_ARM_REG_BASEPRI) and not uc.reg_read(v.a.UC_ARM_REG_PRIMASK) and not self.u(0x200004c4) and not self.u(0x2002716c):self.stop('pendsv');return
  if pc==self.new_thread_entry and self.phase!='startup':
   entry,arg,attr,_=self.args();self.task_events.append(['thread-new',hex(entry),arg,bytes(uc.mem_read(attr,36)).hex()])
  if pc==0x4164da and not self.source:
   pass # Actual event allocation executes below.
  if pc==self.queue_new_entry:
   r0,r1,r2,_=self.args();self.task_events.append(['queue-new-call',r0,r1,bytes(uc.mem_read(r2,24)).hex() if r2 else None])
  if pc==self.queue_get_entry:
   self.task_events.append(['event-queue-get-call',self.args()[0],self.args()[2],self.args()[3]])
  if pc==self.timer_new_entry:
   r0,r1,r2,r3=self.args();self.task_events.append(['timer-new',r0,r1,r2,bytes(uc.mem_read(r3,16)).hex()])
  if pc==self.mutex_new_entry:
   self.task_events.append(['mutex-new',bytes(uc.mem_read(self.args()[0],16)).hex()])
  if pc==self.queue_put_entry:
   self.task_events.append(['dfu-publish',self.args()[0],bytes(uc.mem_read(self.args()[1],40)).hex()])
  if pc==self.dfu_task_entry and self.dispatch:
   self.task_events.append(['dfu-task-enter'])
  if self.dispatch and pc in ((() if getattr(self,'storage',False) else (0x4153a4,)) if getattr(self,'runtime',False) else (0x42ddf2,0x4153a4)):
   self.task_events.append(['dfu-external-boundary',hex(pc),self.args()[:2] if pc==0x4153a4 else []]);self.stop('dfu-dispatch-boundary');return
  if not self.dispatch and pc in (0x42de58,0x42e1da):
   self.task_events.append(['dfu-dispatch-boundary',hex(pc)]);self.stop('dfu-dispatch-boundary');return
  if pc==0x08002120 or (pc==0x4176ce and self.cstr(self.args()[1])=='task.dfu'):
   self.task_events.append(['dfu-log',self.args()[0],self.args()[1] if pc==0x08002120 else self.u(uc.reg_read(v.a.UC_ARM_REG_SP))]);self.ret();return
  if pc==0x4176ce and self.cstr(self.args()[1]) in ('task.manager','evtloop'):
   sp=uc.reg_read(v.a.UC_ARM_REG_SP);self.task_events.append(['log',self.args()[0],self.cstr(self.args()[1]),self.u(sp),self.cstr(self.u(sp+4))]);self.ret();return
  super().code(uc,pc,size,user)
 def stack_basic(self,stack):
  pad=stack&4;frame=stack-32-pad
  values=[self.cpu.reg_read(reg) for reg in REGS]
  values[7]=(values[7]&~0x1ff)|0x01000000|(0x200 if pad else 0)
  self.cpu.mem_write(frame,struct.pack('<8I',*values));return frame
 def unstack_basic(self):
  frame=self.cpu.reg_read(v.a.UC_ARM_REG_PSP);values=struct.unpack('<8I',bytes(self.cpu.mem_read(frame,32)))
  assert values[7]&0x01000000
  for reg,val in zip(REGS,values):
   if reg not in (v.a.UC_ARM_REG_PC,v.a.UC_ARM_REG_XPSR):self.cpu.reg_write(reg,val)
  self.cpu.reg_write(v.a.UC_ARM_REG_CONTROL,2)
  self.cpu.reg_write(v.a.UC_ARM_REG_XPSR,(values[7]&~0x3ff)|0x01000000)
  self.cpu.reg_write(v.a.UC_ARM_REG_PSP,frame+32+(4 if values[7]&0x200 else 0))
  self.cpu.reg_write(v.a.UC_ARM_REG_PC,values[6]|1)
  current=self.u(0x20027134);priority=self.u(current+0x2c)
  self.switches.append(dict(tcb=hex(current),priority=priority,entry_pc=hex(values[6])))
 def drive(self):
  start=(self.symbols['opencfw_boot_reset_entry' if self.reset else 'opencfw_boot_system_entry']&~1) if self.source else (0x43291a if self.reset else 0x43297c)
  self.cpu.reg_write(v.a.UC_ARM_REG_SP,0x2007fb00 if self.reset else v.SP);self.cpu.reg_write(v.a.UC_ARM_REG_LR,v.STOP|1)
  self.cpu.emu_start(start|1,v.STOP+2,count=20000000 if getattr(self,'storage',False) else 2000000);assert self.reason=='svc'
  # Explicit synthetic exception adapter. No interrupts precede SVC in this fixture.
  msp=self.cpu.reg_read(v.a.UC_ARM_REG_MSP);msp_frame=self.stack_basic(msp)
  self.cpu.reg_write(v.a.UC_ARM_REG_CONTROL,0);self.cpu.reg_write(v.a.UC_ARM_REG_MSP,msp_frame);self.cpu.reg_write(v.a.UC_ARM_REG_LR,0xfffffff9)
  self.phase='svc';self.reason=None;self.cpu.emu_start(self.svc_entry|1,v.STOP+2,count=1000);assert self.reason=='exception-return'
  self.cpu.reg_write(v.a.UC_ARM_REG_MSP,msp);self.unstack_basic()
  for _ in range(20):
   self.phase='thread';self.reason=None;self.cpu.emu_start(self.cpu.reg_read(v.a.UC_ARM_REG_PC)|1,v.STOP+2,count=10000000 if getattr(self,'storage',False) else 100000)
   if self.reason=='dfu-dispatch-boundary':return
   assert self.reason=='pendsv',self.reason
   psp=self.cpu.reg_read(v.a.UC_ARM_REG_PSP);frame=self.stack_basic(psp)
   self.cpu.reg_write(v.a.UC_ARM_REG_PSP,frame);self.cpu.reg_write(v.a.UC_ARM_REG_CONTROL,0);self.cpu.reg_write(v.a.UC_ARM_REG_MSP,msp);self.cpu.reg_write(v.a.UC_ARM_REG_LR,0xfffffffd)
   self.w(0xe000ed04,0);self.phase='pendsv';self.reason=None
   self.cpu.emu_start(self.pendsv_entry|1,v.STOP+2,count=10000);assert self.reason=='exception-return'
   self.unstack_basic()
  raise AssertionError('too many scheduler transitions')
def state(m):
 return dict(task_events=m.task_events,task_order=[(x['tcb'],x['priority']) for x in m.switches],ready_counts=[m.u(0x20024870+20*p) for p in range(56)],current=hex(m.u(0x20027134)),suspended_count=m.u(0x20026f84),timer_queue_waiters=m.u(0x20026da0+36),event_thread=hex(m.u(0x200270f0)),manager_priority=m.u(0x20026ac0+0x2c),dfu_handle=m.u(0x200004d4),dfu_queue=m.u(0x200004d8),image_header=bytes(m.cpu.mem_read(0x20026ef8,32)).hex(),event_handle=hex(m.u(0x20000510)),resource_storage=bytes(m.cpu.mem_read(0x20026eac,44)).hex()+bytes(m.cpu.mem_read(0x20026d50,80)).hex(),basepri=m.cpu.reg_read(v.a.UC_ARM_REG_BASEPRI),nesting=m.u(0x200004c4))
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--reset',action='store_true');ap.add_argument('--dispatch',action='store_true');ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();assert v.sha(v.BLOB)==v.SHA
 _,segs,syms=v.elf.elf_info(a.elf);blob=v.BLOB.read_bytes();app=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';assert v.sha(app)=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863';app_vector=app.read_bytes()[32:40];trace={};cases=[]
 for mode,ota_flag in [(0,0),(7,0),(0,0x55555555),(7,0x55555555)]:
  pair=[Machine(),Machine(True,segs,syms)]
  for m in pair:
   if m.source:m.cpu.mem_write(v.BASE,blob[:4])
   m.cpu.mem_map(0x7fe000,0x1000);
   if a.dispatch:m.cpu.mem_map(0x438000,0x1000);m.cpu.mem_write(0x438000,app_vector)
   m.w(0x7fe000,ota_flag);m.reset=a.reset;m.dispatch=a.dispatch;m.stage_status={};m.init_status=0;m.read_status=0;m.mode_result=mode;m.created_handle=0x20026ac0;m.w(c.SLOT,c.SLOT_SENTINEL)
   for addr,n in c.INIT_REGIONS:m.cpu.mem_write(addr,b'\xcc'*n)
   m.cpu.reg_write(v.a.UC_ARM_REG_R9,0);c.seed_source_inputs(m,blob);m.drive()
  results=[state(m) for m in pair];assert results[0]==results[1],results
  assert results[0]['task_order'][:5]==[('0x200269e0',54),('0x20026ac0',48),('0x20026a50',38),('0x20026ac0',8),('0x20026b30',46)]
  assert results[0]['manager_priority']==48 and results[0]['dfu_handle']==0x20026b30 and results[0]['dfu_queue']!=0
  message=bytes.fromhex(next(e[2] for e in results[0]['task_events'] if e[0]=='dfu-publish'));assert struct.unpack('<I',message[:4])[0]==(1 if ota_flag==0x55555555 else 0) and message[4:]==bytes(36)
  queue=results[0]['dfu_queue'];assert pair[0].u(queue+56)==pair[1].u(queue+56)==(0 if a.dispatch else 1)
  assert bytes(pair[0].cpu.mem_read(pair[0].u(queue),40))==bytes(pair[1].cpu.mem_read(pair[1].u(queue),40))==message
  assert results[0]['current']=='0x20026b30'
  assert bytes(pair[0].cpu.mem_read(queue,80))==bytes(pair[1].cpu.mem_read(queue,80))
  if a.dispatch:
   assert results[0]['task_events'][-1][1]==('0x4153a4' if ota_flag==0x55555555 else '0x42ddf2')
   if not ota_flag:assert pair[0].u(0x20026ef8+20)==pair[1].u(0x20026ef8+20)==0x438000
  if a.reset:
   assert pair[0].cpu.reg_read(v.a.UC_ARM_REG_FPSCR)==pair[1].cpu.reg_read(v.a.UC_ARM_REG_FPSCR), [hex(m.cpu.reg_read(v.a.UC_ARM_REG_FPSCR)) for m in pair]
   assert pair[0].u(0xe000ed88)==pair[1].u(0xe000ed88)
  trace.update(pair[0].trace);cases.append(dict(mode=mode,ota_flag=hex(ota_flag),reset_entry=a.reset,result=results[0]))
 used={int(pc,0)+i for pc,b in trace.items() for i in range(len(bytes.fromhex(b)))}
 report=dict(status='PASS',cases=len(cases),distinct_original_trace_bytes=len(used),reset_entry=a.reset,dfu_dispatch=a.dispatch,application_sha256=v.sha(app),app_vector_hex=app_vector.hex(),original_sha256=v.SHA,elf_sha256=v.sha(a.elf),source_sha256={str(p.relative_to(ROOT)):v.sha(p) for folder in ['startup','thread_creation','manager_task','flags_runtime','clock_manager','dfu_task','update_core','filesystem'] for p in (ROOT/'g2/components/bootloader'/folder).iterdir() if p.is_file()},original_trace=trace,comparisons=cases,limits=['Python explicitly models basic exception stacking/alignment/unstacking and eligible PendSV delivery. Actual SVC/PendSV/first restore/selector, timer blocking, manager setup/priority and event task instructions execute. No hardware exception controller, automatic architectural EXC_RETURN, FP/lazy stacking or interrupt deadlines are established.','Default fixture begins system entry43297c; --reset begins pinned reset handler43291a with initial SP2007fb00 and executes reset/stack/FPU setup. Initial vector selection is modeled; physical reset/vector fetch is not proved. No interrupts precede SVC. Peripheral/provider cuts from prior startup remain. Timer/mutex/event construction and allocation now execute actual reconstructed source, including timer callback-record allocation, fresh timer/static mutex object initialization and null-owner mutex release. Timer callback address41639b and event callback42e6f5 are retained serialized stock addresses; deferred callback delivery is not exercised. Actual source CMSIS queue creation/get and fresh static queue/list initialization execute. Event thread blocks on its empty queue, manager resumes at8 and creates DFU46 through actual callback/thread initializer. Actual notification wait/wake, event wait/set/unblock and manager/DFU synchronization execute. DFU blocks before its creator publishes its handle; manager resumes, publishes that handle, signals startup and waits for event bit2; DFU creates its dynamic queue and signals completion, waking manager48. Actual queue-put4168a2/kernel419ec0/copy41a4a6 enqueue the 40-byte message; actual notify bit22 and manager finite wait deliver DFU46. Default stops at DFU task42de58. With --dispatch actual task queue consumption/control flow executes: command0 sets destination438000 and checks the authenticated application vector, then stops before runtime-enable42ddf2; command1 stops before file-open4153a4. Update core stream-mode and reconstructed string resources are linked. Application vector8 bytes are authenticated data inputs; application executable code is not loaded or run. No actual filesystem contents, physical runtime enable or handoff is proved. DFU wrapper42dd68 and literal getter42d88a execute from source; this closure has no context setup side effects.','Stock task-entry pointers branch to source-built test adapters; compiled stack layouts differ, so raw frames/TCB stack pointers are not compared. Actual task selection/order, priorities, list counts and resource/provider interfaces are compared. These adapters are not a byte-identical firmware layout.'])
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['status','cases','distinct_original_trace_bytes']}))
if __name__=='__main__':main()
