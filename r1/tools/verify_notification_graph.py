#!/usr/bin/env python3
"""Real notification, delay, event, ISR timer queue and callback composition."""
import hashlib,itertools,json,struct
from pathlib import Path
from unicorn import UcError,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();LOW=0x20001000;HIGH=0x20001100;E=0x20004000
ENTRIES={'r1_native_task_create_static':0x98418,'xTimerCreateTimerTask':0x98ca8,'osDelay':0x7d154,'osThreadFlagsSet':0x7d6f4,'osThreadFlagsWait':0x7d780,'osEventFlagsSet':0x7d1a0,'r1_native_timer_task':0x85510}
TARGETS={'xTaskGenericNotify':0x98484,'xTaskGenericNotifyFromISR':0x985ac,'xTaskGenericNotifyWait':0x98700,'vTaskDelay':0x95fd4,'xEventGroupSetBits':0x977f4,'xTimerPendFunctionCallFromISR':0x98d98,'vEventGroupSetBitsCallback':0x95c8c,'vTaskRemoveFromUnorderedEventList':0x963e8,'xQueueGenericSendFromISR':0x97da4}
def verify(stock,candidate,syms,baseline):
 receipt=BASE/'board/notification-verification.json';receipt.unlink(missing_ok=True);comparisons=0;workflows=0;states={};handles=[];provider_counts={'native':{},'source':{}}
 for u in (stock,candidate):
  try:u.mem_map(0xe000e000,4096)
  except UcError:pass
 def word(u,a):return struct.unpack('<I',bytes(u.mem_read(a,4)))[0]
 def put(u,a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
 def code(u,a,size,user):
  f=states[id(u)];counts=provider_counts['native' if u is stock else 'source']
  for name,native in TARGETS.items():
   if a==((native if u is stock else syms[name])&~1):counts[name]=counts.get(name,0)+1
  if f['loop'] and a==(0x85512 if u is stock else syms['prvGetNextExpireTime']&~1):
   if f['iterations']==1:f['boundary']=True;u.emu_stop();return
   f['iterations']+=1
 for u in (stock,candidate):handles.append((u,u.hook_add(UC_HOOK_CODE,code)))
 def snapshot(u):
  queue=bytearray(u.mem_read(0x2002b258,632))
  for slot,flags in states[id(u)]['slots']:
   assert struct.unpack_from('<I',queue,slot-0x2002b258)[0]==0xfffffffe
   callback=word(u,slot+4);assert callback==(0x95c8d if u is stock else syms['vEventGroupSetBitsCallback']|1) and word(u,slot+8)==E and word(u,slot+12)==flags
   if u is candidate:struct.pack_into('<I',queue,slot+4-0x2002b258,0x95c8d)
  return (bytes(u.mem_read(LOW,112)),bytes(u.mem_read(HIGH,112)),bytes(u.mem_read(0x2002b940,112)),bytes(u.mem_read(0x20003e00,0x300)),bytes(u.mem_read(0x20007810,96)),bytes(u.mem_read(0x2002ad94,1220)),bytes(queue),bytes(u.mem_read(0x200077fc,20)),word(u,0xe000ed04),u.reg_read(UC_ARM_REG_PRIMASK),u.reg_read(UC_ARM_REG_BASEPRI))
 saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
 def call(name,args=(),ipsr=0):
  nonlocal comparisons
  outcomes=[]
  for u in (stock,candidate):
   f=states[id(u)];u.reg_write(UC_ARM_REG_IPSR,ipsr);u.reg_write(UC_ARM_REG_SP,0x2003c000);u.reg_write(UC_ARM_REG_LR,0x20000101)
   for reg,value in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),args):u.reg_write(reg,value)
   u.mem_write(0x2003c000,struct.pack('<3I',*(list(args[4:])+[0,0,0])[:3]))
   for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
   try:u.emu_start((ENTRIES[name] if u is stock else syms[name])|1,0x20000100,count=2000000)
   except UcError as error:raise AssertionError((name,args,u is stock,hex(u.reg_read(UC_ARM_REG_PC)))) from error
   if f['loop']:assert f['boundary'] and f['iterations']==1
   else:assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003c000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
   outcomes.append((None if f['loop'] else u.reg_read(UC_ARM_REG_R0),snapshot(u)))
  assert outcomes[0]==outcomes[1],(name,args,ipsr,[(i,str(a)[:220],str(b)[:220]) for i,(a,b) in enumerate(zip(outcomes[0],outcomes[1])) if a!=b]);comparisons+=1;return outcomes[0][0]
 def select(address):
  for u in (stock,candidate):put(u,0x2000781c,address)
 try:
  for pattern,notify_irq,event_irq,no_clear,mask,clear_event in itertools.product((0,0xa5),(0,33),(0,33),(0,1),(1,3),(0,1)):
   for u in (stock,candidate):
    states[id(u)]={'loop':False,'iterations':0,'boundary':False,'slots':[]};u.mem_write(0x20000000,baseline[id(u)]);u.mem_write(LOW,bytes([pattern])*0x200);u.mem_write(0x20003e00,bytes([pattern])*0x300);u.mem_write(0x20003e00,b'Low\0High\0');u.mem_write(E,bytes([pattern])*32);put(u,E,0x10);u.mem_write(E+4,struct.pack('<5I',0,E+12,0xffffffff,E+12,E+12));u.mem_write(0xe000ed04,bytes(4));u.mem_write(0xe000ed0c,bytes(4));u.reg_write(UC_ARM_REG_BASEPRI,0);u.reg_write(UC_ARM_REG_PRIMASK,0)
   for cb,stack,priority,name in ((LOW,0x20002000,8,0x20003e00),(HIGH,0x20002800,25,0x20003e04)):assert call('r1_native_task_create_static',(0x12345679,name,256,0,priority,stack,cb))==cb
   assert call('xTimerCreateTimerTask')==1
   select(HIGH);assert call('osDelay',(5,))==0
   for u in (stock,candidate):assert word(u,HIGH+20)==word(u,0x20007854);put(u,HIGH+104,0x10);u.mem_write(HIGH+108,b'\x01')
   select(LOW);assert call('osThreadFlagsSet',(HIGH,mask),notify_irq)==(0x10|mask)
   for u in (stock,candidate):assert word(u,HIGH+20)==0x2002ad94+25*20 and u.mem_read(HIGH+108,1)[0]==2
   select(HIGH);assert call('osThreadFlagsWait',(mask,2 if no_clear else 0,0))==(0x10|mask)
   for u in (stock,candidate):assert word(u,HIGH+104)==(0x10|mask if no_clear else 0x10) and u.mem_read(HIGH+108,1)[0]==0
   assert call('osDelay',(0,))==0;assert call('osDelay',(5,))==0
   for u in (stock,candidate):
    item=HIGH+24;value=mask|(0x04000000 if mask==3 else 0)|(0x01000000 if clear_event else 0);u.mem_write(item,struct.pack('<5I',value,E+12,E+12,HIGH,E+4));put(u,E+4,1);put(u,E+16,item);put(u,E+20,item)
   select(LOW)
   if event_irq:
    for u in (stock,candidate):states[id(u)]['slots'].append((word(u,0x2002b258+4),mask))
   expected=0x10|mask if event_irq or not clear_event else 0x10
   assert call('osEventFlagsSet',(E,mask),event_irq)==expected
   if event_irq:
    for u in (stock,candidate):assert word(u,E)==0x10 and word(u,HIGH+20)==word(u,0x20007854) and word(u,0x2002b258+56)==1
   else:
    for u in (stock,candidate):assert word(u,HIGH+20)==0x2002ad94+25*20;states[id(u)]['slots'].append((word(u,0x2002b258+4),0))
    assert call('osEventFlagsSet',(E,0),33)==expected
   select(0x2002b940)
   for u in (stock,candidate):states[id(u)]['loop']=True
   call('r1_native_timer_task',(0,))
   for u in (stock,candidate):
    states[id(u)]['loop']=False;assert word(u,E)==(0x10 if clear_event else 0x10|mask) and word(u,E+4)==0 and word(u,HIGH+20)==0x2002ad94+25*20 and word(u,HIGH+24)==(0x82000000|0x10|mask) and word(u,HIGH+40)==0 and word(u,0x2002b258+56)==0
   workflows+=1
 finally:
  for u,h in handles:u.hook_del(h)
  for u in (stock,candidate):u.mem_write(0x20000000,baseline[id(u)]);u.reg_write(UC_ARM_REG_IPSR,0);u.reg_write(UC_ARM_REG_PRIMASK,0);u.reg_write(UC_ARM_REG_BASEPRI,0)
 assert provider_counts['native']==provider_counts['source'] and all(provider_counts['source'].get(n,0)>0 for n in TARGETS),provider_counts
 result=dict(application_sha256=sha(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin'),board_report_sha256=sha(BASE/'board/report.json'),verification_driver_sha256=sha(ROOT/'r1/tools/verify_native_board.py'),notification_driver_sha256=sha(Path(__file__)),provider_reports={n:sha(BASE/n/'report.json') for n in ('rtos-notification-wrappers','rtos-notification-tasks','rtos-event-groups','rtos-timer-pend','rtos-unordered-event')},comparisons=comparisons,workflows=workflows,notification_wakes_per_implementation=workflows,event_wakes_per_implementation=workflows,daemon_iterations_per_implementation=workflows,provider_interception=False,executed_provider_entry_counts=provider_counts,scope='Actual static task/timer construction, notification set/wait/delay, event task/ISR set, exact negative callback command, real queue/daemon/callback/event/unordered wake graph; one nonblocking daemon iteration per workflow',limitations=['Current-task selection, initial notification-wait state and event wait-list attachment are controlled fixtures. Delay/wait instructions execute without physical exception dispatch or real blocking resumption. Event32-byte storage is fixture-initialized; event creation is not claimed. Callback pointer is normalized only after exact identity/payload checks. Task stacks/exception return and whole-image instruction equality remain gates.']);receipt.write_text(json.dumps(result,indent=2)+'\n');print(comparisons,'notification/event graph comparisons;',workflows,'workflows; actual daemon callbacks and unordered wakes')
if __name__=='__main__':raise SystemExit('Use verify_native_board.py --notification-graph')
