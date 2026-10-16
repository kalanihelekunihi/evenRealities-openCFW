#!/usr/bin/env python3
"""Actual pinned timeout/wait/mutex/list bodies versus native; critical fixtures."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_INVALID
from unicorn.arm_const import *
from verify_native_task_construction import FIELDS as SHARED
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
FIELDS={**SHARED,'uxDeletedTasksWaitingCleanUp':(0x20007820,4)}
ENTRIES={'vTaskDelete':0x96020,'eTaskGetState':0x5cfac,'r1_native_task_reclaim':0x84f36,'osThreadTerminate':0x7d8d6,'vListInsertEnd':0x95cdc,'r1_native_task_idle_cleanup':0x84fe8,'r1_native_expected_idle_time':0x84f68};BACKENDS={'vPortEnterCritical':0x95cf4,'vPortExitCritical':0x95d24,'vPortFree':0x95d48,'xTaskGetSchedulerState':0x987a8}
def main():
 out=BASE/'rtos-task-termination';receipt=out/'verification.json';receipt.unlink(missing_ok=True);rp=out/'report.json';r=json.loads(rp.read_text());obj=out/'task-termination.o';assert sha(obj)==r['selected_object_sha256']
 for p,d in r['inputs'].items():assert sha(ROOT/p)==d,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';states={};scheduler_state=1;comparisons=0;faults=0;counts={n:0 for n in ENTRIES}
 with tempfile.TemporaryDirectory() as directory:
  t=Path(directory);ld=t/'layout.ld';elf=t/'test.elf';binary=t/'text.bin';ld.write_text('SECTIONS { .text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } .bss.uxDeletedTasksWaitingCleanUp 0x20007820 (NOLOAD) : { *(.bss.uxDeletedTasksWaitingCleanUp) } /DISCARD/ : { *(.comment) *(.note*) } }');rem=t/'remove.o';subprocess.run(['arm-none-eabi-ld','-r','--gc-sections','--undefined=uxListRemove',str(BASE/'rtos-task-wait/list.o'),'-o',str(rem)],check=True);bindings={n:0x100ef01+i*16 for i,n in enumerate(BACKENDS)};subprocess.run(['arm-none-eabi-ld','-T',str(ld),*['--defsym='+n+'='+hex(a) for n,(a,z) in FIELDS.items() if n != 'uxDeletedTasksWaitingCleanUp'],*['--defsym='+n+'='+hex(a) for n,a in bindings.items()],str(obj),str(rem),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True);syms={x.split()[-1]:int(x.split()[0],16) for x in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x.split())==3}
  for n,(a,z) in FIELDS.items():assert syms[n]==a
  stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
  for u in (stock,candidate):u.mem_map(0x20000,0xc0000);u.mem_map(0x1000000,0x10000);u.mem_map(0x20000000,0x40000);u.mem_map(0xe000e000,0x2000)
  stock.mem_write(0x27000,app.read_bytes());candidate.mem_write(0x1000000,binary.read_bytes());kinds={a:n for n,a in BACKENDS.items()};kinds.update({a&~1:n for n,a in bindings.items()})
  def hook(u,a,size,user):
   if a not in kinds:return
   name=kinds[a];states[id(u)]['trace'].append((name,u.reg_read(UC_ARM_REG_R0)) if name=='vPortFree' else (name,));u.reg_write(UC_ARM_REG_R0,scheduler_state if name=='xTaskGetSchedulerState' else 0xdeadbeef);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
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
    u.reg_write(UC_ARM_REG_IPSR,0);u.reg_write(UC_ARM_REG_PRIMASK,0);u.reg_write(UC_ARM_REG_BASEPRI,0);u.mem_write(0x20001000,bytes([0xa5])*0x4000);u.mem_write(0x2000781c,bytes(64));put(u,0xe000ed04,0);u.mem_write(0x2002ad94,bytes(1220))
    for n,v in [('pxCurrentTCB',0x20001000),('uxCurrentNumberOfTasks',1),('uxTopReadyPriority',priority),('uxSchedulerSuspended',1),('xTickCount',tick),('xNextTaskUnblockTime',0xffffffff),('pxDelayedTaskList',0x2002b1f4),('pxOverflowDelayedTaskList',0x2002b208)]:put(u,FIELDS[n][0],v)
    for i in range(56):init_list(u,0x2002ad94+i*20)
    for a in (0x2002b1f4,0x2002b208,0x2002b21c,0x2002b230,0x2002b244,0x20003000):init_list(u,a)
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
    f={'trace':[],'fault':False};states[id(u)]=f;u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101);
    for reg,value in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),args):u.reg_write(reg,value)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    try:u.emu_start((ENTRIES[name] if u is stock else syms[name])|1,(0x8501a if name=='r1_native_task_idle_cleanup' and u is stock else 0x20000100),count=1000000)
    except UcError:assert f['fault'],(name,args,u is stock,hex(u.reg_read(UC_ARM_REG_PC)))
    if not f['fault'] and name=='r1_native_task_idle_cleanup' and u is stock:assert u.reg_read(UC_ARM_REG_PC)==0x8501a and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and u.reg_read(UC_ARM_REG_R4)==0x2000781c and u.reg_read(UC_ARM_REG_R6)==0x2002b230
    elif not f['fault']:assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
    results.append((f['fault'],u.reg_read(UC_ARM_REG_R0) if name in ('eTaskGetState','osThreadTerminate','r1_native_expected_idle_time') and not f['fault'] else None,f['trace'],bytes(u.mem_read(0x20001000,0x4000)),bytes(u.mem_read(0x2000781c,64)),bytes(u.mem_read(0x2002ad94,1220)),u.reg_read(UC_ARM_REG_BASEPRI),word(u,0xe000ed04)))
   assert results[0]==results[1],(name,args,[x[:3] for x in results],[(k,[(i,a,b) for i,(a,b) in enumerate(zip(results[0][k],results[1][k])) if a!=b][:12]) for k in range(3,6)]);comparisons+=1;faults+=results[0][0];counts[name]+=1
  for mode in range(256):
   reset()
   for u in (stock,candidate):u.mem_write(0x2000106d,bytes([mode]));put(u,0x20001030,0x20004000)
   call('r1_native_task_reclaim',(0x20001000,))
  for current,container,event,notify in itertools.product((0,1),(0,0x2002ad94,0x2002b1f4,0x2002b208,0x2002b21c,0x2002b230,0x2002b244,0x20003000),(0,0x20003000),(0,1,2,255)):
   reset()
   for u in (stock,candidate):put(u,0x20001014,container);put(u,0x20001028,event);u.mem_write(0x2000106c,bytes([notify]));put(u,FIELDS['pxCurrentTCB'][0],0x20001000 if current else 0x20002800)
   call('eTaskGetState',(0x20001000,))
  reset();call('eTaskGetState',(0,))
  for current,asnull,mode,events,other,index,running,suspended,delayed in itertools.product((0,1),(0,1),(0,1,2,3),(0,1),(0,1),(0,1),(0,1),(0,1),(0,1,3)):
   if asnull and not current:continue
   reset(priority=15,other=other,delayed=delayed,events=events,index=index)
   for u in (stock,candidate):
    if not current:put(u,FIELDS['pxCurrentTCB'][0],0x20002800)
    put(u,FIELDS['xSchedulerRunning'][0],running);put(u,FIELDS['uxSchedulerSuspended'][0],suspended);put(u,0x20001030,0x20004000);u.mem_write(0x2000106d,bytes([mode]))
    if events:append(u,0x20003000,0x20001018,0x20001000,41)
   call('vTaskDelete',(0 if asnull else 0x20001000,))
  for container,mode,event,index,other in itertools.product((0x2002b1f4,0x2002b208,0x2002b244),(0,1,2),(0,1),(0,1),(0,1,3)):
   reset(priority=15)
   for u in (stock,candidate):
    task=0x20002000;put(u,task+44,55);put(u,task+48,0x20004000);u.mem_write(task+109,bytes([mode]));put(u,task+40,0)
    append(u,container,task+4,task,100)
    for j in range(other):append(u,container,0x20002404+j*128,0x20002400+j*128,101+j)
    if index:put(u,container+4,task+4)
    if event:append(u,0x20003000,task+24,task,1)
   call('vTaskDelete',(task,))
  for ipsr,primask,basepri,handle,current,container,scheduler_state in itertools.product((0,16),(0,1),(0,64),(0,0x20001000),(0,1),(0,0x2002ad94,0x2002b230,0x2002b244),(0,1,2)):
   if current and container!=0x2002ad94:continue
   reset(priority=0)
   for u in (stock,candidate):
    put(u,0x20001014,container);put(u,FIELDS['pxCurrentTCB'][0],0x20001000 if current else 0x20002800);u.mem_write(0x2000106d,b'\x02');u.mem_write(0x2000106c,b'\x00');put(u,0x20001028,0);u.reg_write(UC_ARM_REG_IPSR,ipsr);u.reg_write(UC_ARM_REG_PRIMASK,primask);u.reg_write(UC_ARM_REG_BASEPRI,basepri)
   # Ready/suspended lists must be consistent when deletion follows the state query.
   if container==0x2002b244:
    for u in (stock,candidate):append(u,container,0x20001004,0x20001000,0)
   call('osThreadTerminate',(handle,))
  for events,index,value in itertools.product((0,1,3),(0,1),(0,1,0xffffffff)):
   reset(events=events)
   for u in (stock,candidate):
    put(u,0x20001018,value)
    if index and events:put(u,0x20003004,0x20002418)
   call('vListInsertEnd',(0x20003000,0x20001018))
  for number,pattern,index,counter in itertools.product((0,1,2,3,8),((0,1,2),(2,0,1),(1,2,0),(3,0,2),(0,255,2)),(0,1),(0,100,0xffffffff)):
   reset()
   for u in (stock,candidate):
    put(u,FIELDS['uxDeletedTasksWaitingCleanUp'][0],number);put(u,FIELDS['uxCurrentNumberOfTasks'][0],counter)
    for j in range(number):
     task=0x20002000+j*128;put(u,task+48,0x20004000+j*128);u.mem_write(task+109,bytes([pattern[j%3]]));append(u,0x2002b230,task+4,task,j)
    if number and index:put(u,0x2002b234,0x20002004+(number-1)*128)
   call('r1_native_task_idle_cleanup')
  for tick,next_unblock,priority,top,ready in itertools.product((0,1,100,0xfffffffe,0xffffffff),(0,1,100,0xfffffffe,0xffffffff),(0,1,55),(0,1,55),(0,1,2,0xffffffff)):
   reset(priority=priority)
   for u in (stock,candidate):put(u,0x20007828,tick);put(u,0x20007844,next_unblock);put(u,0x2000782c,top);put(u,0x2002ad94,ready)
   call('r1_native_expected_idle_time')
  receipt.write_text(json.dumps(dict(application_sha256=sha(app),report_sha256=sha(rp),driver_sha256=sha(Path(__file__)),comparisons=comparisons,assertion_comparisons=faults,comparisons_by_function=counts,tcb_bytes_compared=112,scope='Actual pinned termination/state/reclamation/list bodies; complete fixture TCB, shared scheduler words, ready/delayed/termination/event lists and PendSV write compared',idle_cleanup_native_region=['0x84fe8','0x8501a'],idle_cleanup_native_function_abi_claimed=False,limitations=['Critical entry/exit, vPortFree and scheduler-state reads are bounded fixtures. Idle cleanup is a bounded inlined region, not a standalone native function. Complete idle loop and native PendSV transfer remain separate gates. No physical concurrency or image byte equality proof.']),indent=2)+'\n');print(comparisons,'task termination comparisons;',faults,'assertions;',counts)
if __name__=='__main__':main()
