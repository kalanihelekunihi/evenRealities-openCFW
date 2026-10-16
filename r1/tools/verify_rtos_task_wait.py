#!/usr/bin/env python3
"""Actual pinned timeout/wait/mutex/list bodies versus native; critical fixtures."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_INVALID
from unicorn.arm_const import *
from verify_rtos_scheduler_tick import FIELDS as SHARED
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
FIELDS={**SHARED,'xSuspendedTaskList':(0x2002b244,20),'uxTopUsedPriority':(0x2000784c,4)}
ENTRIES={'vTaskInternalSetTimeOutState':0x96160,'vTaskMissedYield':0x96170,'vTaskPlaceOnEventList':0x96188,'xTaskCheckForTimeOut':0x98340,'xTaskPriorityDisinherit':0x98910,'prvAddCurrentTaskToDelayedList':0x84cf0,'uxListRemove':0x9560e,'vListInsert':0x95cac};BACKENDS={'vPortEnterCritical':0x95cf4,'vPortExitCritical':0x95d24}
def main():
 out=BASE/'rtos-task-wait';receipt=out/'verification.json';receipt.unlink(missing_ok=True);rp=out/'report.json';r=json.loads(rp.read_text());obj=out/'task-wait.o';assert sha(obj)==r['selected_object_sha256']
 for p,d in r['inputs'].items():assert sha(ROOT/p)==d,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';states={};comparisons=0;faults=0;counts={n:0 for n in ENTRIES}
 with tempfile.TemporaryDirectory() as directory:
  t=Path(directory);ld=t/'layout.ld';elf=t/'test.elf';binary=t/'text.bin';ld.write_text('SECTIONS { .r1.scheduler.top_used_priority 0x2000784c : { *(.data.uxTopUsedPriority) *(.rodata.uxTopUsedPriority) } .text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } .bss.xSuspendedTaskList 0x2002b244 (NOLOAD) : { *(.bss.xSuspendedTaskList) } /DISCARD/ : { *(.comment) *(.note*) } }');bindings={n:0x100ef01+i*16 for i,n in enumerate(BACKENDS)};subprocess.run(['arm-none-eabi-ld','-T',str(ld),*['--defsym='+n+'='+hex(a) for n,(a,z) in FIELDS.items() if n not in ('xSuspendedTaskList','uxTopUsedPriority')],*['--defsym='+n+'='+hex(a) for n,a in bindings.items()],str(obj),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True);syms={x.split()[-1]:int(x.split()[0],16) for x in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x.split())==3}
  for n,(a,z) in FIELDS.items():assert syms[n]==a
  stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
  for u in (stock,candidate):u.mem_map(0x20000,0xc0000);u.mem_map(0x1000000,0x10000);u.mem_map(0x20000000,0x40000)
  stock.mem_write(0x27000,app.read_bytes());candidate.mem_write(0x1000000,binary.read_bytes());data=t/'priority.bin';subprocess.run(['arm-none-eabi-objcopy','--dump-section','.r1.scheduler.top_used_priority='+str(data),str(elf)],check=True);assert data.read_bytes()==struct.pack('<I',55);candidate.mem_write(0x2000784c,data.read_bytes());kinds={a:n for n,a in BACKENDS.items()};kinds.update({a&~1:n for n,a in bindings.items()})
  def hook(u,a,size,user):
   if a not in kinds:return
   states[id(u)]['trace'].append(kinds[a]);u.reg_write(UC_ARM_REG_R0,0xdeadbeef);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  def fault(u,access,address,size,value,user):
   if address==0xffffffff and value==0:states[id(u)]['fault']=True
   return False
  for u in (stock,candidate):u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_INVALID,fault)
  def put(u,a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
  def word(u,a):return struct.unpack('<I',bytes(u.mem_read(a,4)))[0]
  def init_list(u,a):u.mem_write(a,struct.pack('<5I',0,a+8,0xffffffff,a+8,a+8))
  def append(u,a,item,owner,value):
   sentinel=a+8;previous=word(u,sentinel+8);u.mem_write(item,struct.pack('<5I',value&0xffffffff,sentinel,previous,owner,a));put(u,previous+4,item);put(u,sentinel+8,item);put(u,a,word(u,a)+1)
  def reset(tick=0,priority=0,other=0,delayed=0,events=0,index=0):
   for u in (stock,candidate):
    u.mem_write(0x20001000,bytes([0xa5])*0x4000);u.mem_write(0x2000781c,bytes(64));u.mem_write(0x2002ad94,bytes(1220))
    for n,v in [('pxCurrentTCB',0x20001000),('uxCurrentNumberOfTasks',1),('uxTopReadyPriority',priority),('uxTopUsedPriority',55),('uxSchedulerSuspended',1),('xTickCount',tick),('xNextTaskUnblockTime',0xffffffff),('pxDelayedTaskList',0x2002b1f4),('pxOverflowDelayedTaskList',0x2002b208)]:put(u,FIELDS[n][0],v)
    for i in range(56):init_list(u,0x2002ad94+i*20)
    for a in (0x2002b1f4,0x2002b208,0x2002b21c,0x2002b244,0x20003000):init_list(u,a)
    put(u,0x2000102c,priority);put(u,0x20001018,56-priority);put(u,0x20001028,0);put(u,0x20001060,priority);put(u,0x20001064,1);append(u,0x2002ad94+priority*20,0x20001004,0x20001000,0)
    if other:put(u,0x2000282c,priority);append(u,0x2002ad94+priority*20,0x20002804,0x20002800,0)
    for i in range(delayed):
     task=0x20002000+i*128;put(u,task+44,i);append(u,0x2002b1f4,task+4,task,(1,100,0xffffffff)[i])
    for i in range(events):
     task=0x20002400+i*128;append(u,0x20003000,task+24,task,(0,56,0xffffffff)[i])
    if index:put(u,0x2002ad94+priority*20+4,0x20001004)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  def call(name,args=()):
   nonlocal comparisons,faults
   results=[]
   for u in (stock,candidate):
    f={'trace':[],'fault':False};states[id(u)]=f;u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101);u.reg_write(UC_ARM_REG_BASEPRI,0)
    for reg,value in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),args):u.reg_write(reg,value)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    try:u.emu_start((ENTRIES[name] if u is stock else syms[name])|1,0x20000100,count=1000000)
    except UcError:assert f['fault'],(name,args,u is stock,hex(u.reg_read(UC_ARM_REG_PC)))
    if not f['fault']:assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
    results.append((f['fault'],u.reg_read(UC_ARM_REG_R0) if name in ('xTaskCheckForTimeOut','xTaskPriorityDisinherit','uxListRemove') and not f['fault'] else None,f['trace'],bytes(u.mem_read(0x20001000,0x4000)),bytes(u.mem_read(0x2000781c,64)),bytes(u.mem_read(0x2002ad94,1220)),u.reg_read(UC_ARM_REG_BASEPRI)))
   assert results[0]==results[1],(name,args,[x[:3] for x in results],[(k,[(i,a,b) for i,(a,b) in enumerate(zip(results[0][k],results[1][k])) if a!=b][:12]) for k in range(3,6)]);comparisons+=1;faults+=results[0][0];counts[name]+=1
  for now,overflow in itertools.product((0,1,99,0xfffffffe,0xffffffff),(0,1,0x7fffffff,0xffffffff)):
   reset(now)
   for u in (stock,candidate):put(u,FIELDS['xNumOfOverflows'][0],overflow)
   call('vTaskInternalSetTimeOutState',(0x20004000,));call('vTaskMissedYield')
  for now,overflow,delta,enter,wait in itertools.product((0,1,99,0xfffffffe,0xffffffff),(0,1,0x7fffffff,0x80000000,0xffffffff),(-1,0,1),(0,1,98,99,0xfffffffe,0xffffffff),(0,1,2,99,100,0xffffffff)):
   reset(now)
   for u in (stock,candidate):put(u,FIELDS['xNumOfOverflows'][0],overflow);u.mem_write(0x20004000,struct.pack('<2I',(overflow+delta)&0xffffffff,enter));put(u,0x20004020,wait)
   call('xTaskCheckForTimeOut',(0x20004000,0x20004020))
  for tick,wait,priority,other,delayed,events,index in itertools.product((0,1,100,0xfffffffe,0xffffffff),(0,1,2,100,0x7fffffff,0xfffffffe,0xffffffff),(0,1,15,55),(0,1),(0,1,3),(0,1,3),(0,1)):
   reset(tick,priority,other,delayed,events,index);call('vTaskPlaceOnEventList',(0x20003000,wait))
   for indefinite in (0,1):reset(tick,priority,other,delayed,events,index);call('prvAddCurrentTaskToDelayedList',(wait,indefinite))
  for priority,base,held,other,index,holder in itertools.product((0,1,15,55),(0,1,15,55),(0,1,2,0xffffffff),(0,1),(0,1),(0,0x20001000,0x20002000)):
   reset(99,priority,other,index=index)
   for u in (stock,candidate):put(u,0x20001060,base);put(u,0x20001064,held)
   call('xTaskPriorityDisinherit',(holder,))
  for priority,other,index in itertools.product((0,55),(0,1),(0,1)):
   reset(99,priority,other,index=index);call('uxListRemove',(0x20001004,))
  for value,events,index in itertools.product((0,1,55,56,0x7fffffff,0xffffffff),(0,1,3),(0,1)):
   reset(99,0,events=events,index=index)
   for u in (stock,candidate):put(u,0x20001018,value)
   call('vListInsert',(0x20003000,0x20001018))
  reset();call('xTaskCheckForTimeOut',(0,0x20004020));reset();call('xTaskCheckForTimeOut',(0x20004000,0));reset();call('vTaskPlaceOnEventList',(0,1))
 receipt.write_text(json.dumps(dict(application_sha256=sha(app),report_sha256=sha(rp),driver_sha256=sha(Path(__file__)),comparisons=comparisons,assertion_comparisons=faults,comparisons_by_function=counts,accessed_tcb_prefix_bytes=104,top_used_priority_bytes_compared=4,scope='Actual pinned timeout snapshots/checks, missed yield, ordered event/delayed/suspended placement, mutex disinherit and list insert/remove; full TCB canaries and shared state/list memory',limitations=['Critical entry/exit are bounded fixtures. The104-byte accessed TCB prefix preserves the native stack-depth word; full112-byte construction/tail fields remain gated. No scheduler startup/context switching, physical concurrency or whole-image identity proof.']),indent=2)+'\n');print(comparisons,'task wait/mutex comparisons;',faults,'assertions;',counts)
if __name__=='__main__':main()
