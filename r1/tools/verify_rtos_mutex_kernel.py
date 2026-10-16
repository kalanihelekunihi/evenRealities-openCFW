#!/usr/bin/env python3
"""Pinned kernel mutex/semaphore bodies versus native with explicit task/queue fixtures."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_INVALID
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();Q=0x20004000
ENTRIES={'prvInitialiseMutex':0x8507c,'xQueueCreateMutex':0x97ade,'xQueueCreateMutexStatic':0x97af4,'xQueueGiveFromISR':0x97e6c,'xQueueGiveMutexRecursive':0x97f14,'xQueueSemaphoreTake':0x98120,'xQueueTakeMutexRecursive':0x98284}
BACKENDS={'pvTaskIncrementMutexHeldCount':0x85684,'vPortEnterCritical':0x95cf4,'vPortExitCritical':0x95d24,'vTaskInternalSetTimeOutState':0x96160,'vTaskMissedYield':0x96170,'vTaskPlaceOnEventList':0x96188,'vTaskPriorityDisinheritAfterTimeout':0x9626c,'vTaskSuspendAll':0x9659c,'xQueueGenericCreate':0x97b0e,'xQueueGenericCreateStatic':0x97b62,'xQueueGenericSend':0x97c50,'xTaskCheckForTimeOut':0x98340,'xTaskGetCurrentTaskHandle':0x9879c,'xTaskGetSchedulerState':0x987a8,'xTaskPriorityInherit':0x989ac,'xTaskRemoveFromEventList':0x98a4c,'xTaskResumeAll':0x98b24}
def main():
 out=BASE/'rtos-mutex-kernel';vp=out/'verification.json';vp.unlink(missing_ok=True);rp=out/'report.json';r=json.loads(rp.read_text());obj=out/'mutex-kernel.o';assert sha(obj)==r['selected_object_sha256']
 for p,d in r['inputs'].items():assert sha(ROOT/p)==d,p
 actual={}
 for name,filename in [('rtos-task-count','task-count.o'),('rtos-interrupt-priority','interrupt-priority.o')]:
  p=BASE/name/'report.json';rr=json.loads(p.read_text());o=p.parent/filename;assert sha(o)==rr['selected_object_sha256'];actual[name]={'report_sha256':sha(p),'object_sha256':sha(o)}
  for path,digest in rr['inputs'].items():assert sha(ROOT/path)==digest,path
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';states={};comparisons=0;faults=0;counts={n:0 for n in ENTRIES}
 with tempfile.TemporaryDirectory() as directory:
  t=Path(directory);ld=t/'layout.ld';elf=t/'test.elf';binary=t/'text.bin';ld.write_text('SECTIONS { .text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } /DISCARD/ : { *(.comment) *(.note*) } }');bindings={n:0x100ee01+i*16 for i,n in enumerate(BACKENDS)};subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--defsym=uxCurrentNumberOfTasks=0x20007824',*['--defsym='+n+'='+hex(a) for n,a in bindings.items()],str(obj),str(BASE/'rtos-task-count/task-count.o'),str(BASE/'rtos-interrupt-priority/interrupt-priority.o'),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True);syms={x.split()[-1]:int(x.split()[0],16) for x in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x.split())==3};stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
  for u in (stock,candidate):u.mem_map(0x20000,0xc0000);u.mem_map(0x1000000,0x10000);u.mem_map(0x20000000,0x40000);u.mem_map(0xe000e000,4096)
  stock.mem_write(0x27000,app.read_bytes());candidate.mem_write(0x1000000,binary.read_bytes());kinds={a:n for n,a in BACKENDS.items()};kinds.update({a&~1:n for n,a in bindings.items()})
  def word(u,a):return struct.unpack('<I',bytes(u.mem_read(a,4)))[0]
  def put(u,a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
  def hook(u,a,size,user):
   if a not in kinds:return
   f=states[id(u)];name=kinds[a];args=[u.reg_read(reg) for reg in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)];value=0;trace=(name,)
   if name=='xTaskGetSchedulerState':value=f['scheduler']
   elif name=='xTaskGetCurrentTaskHandle':value=0x20001000
   elif name=='pvTaskIncrementMutexHeldCount':put(u,0x20001064,word(u,0x20001064)+1);value=0x20001000
   elif name=='xQueueGenericCreate':trace=(name,*args[:3]);value=f['allocation']
   elif name=='xQueueGenericCreateStatic':trace=(name,*args,word(u,u.reg_read(UC_ARM_REG_SP)));value=f['allocation']
   elif name=='xQueueGenericSend':trace=(name,*args);value=f['send'];assert args[1:]==[0,0,0]
   elif name=='vTaskInternalSetTimeOutState':u.mem_write(args[0],struct.pack('<2I',0,100))
   elif name=='xTaskCheckForTimeOut':
    f['checks']+=1;value=int(f['mode']=='expire' or (f['mode']=='twice' and f['checks']>1));trace=(name,value,word(u,args[1]));put(u,args[1],0 if value else 1)
   elif name=='vTaskPlaceOnEventList':
    trace=(name,*args[:2]);assert args[0]==Q+36
    if f['mode']=='wake':put(u,Q+56,1)
   elif name=='xTaskPriorityInherit':trace=(name,args[0]);value=f['inherit']
   elif name=='vTaskPriorityDisinheritAfterTimeout':trace=(name,*args[:2])
   elif name=='xTaskRemoveFromEventList':
    trace=(name,args[0]);value=f['yield'];assert args[0] in (Q+16,Q+36);put(u,args[0],max(0,word(u,args[0])-1))
   elif name=='xTaskResumeAll':value=f['resume']
   f['trace'].append(trace);u.reg_write(UC_ARM_REG_R0,value&0xffffffff);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  def fault(u,access,a,size,value,user):
   if a==0xffffffff and value==0:states[id(u)]['fault']=True
   return False
  for u in (stock,candidate):u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_INVALID,fault)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  def reset(count=0,mutex=False,holder=0,recursive=0,waiting=0,lock=-1,tasks=2,item=0,length=3):
   for u in (stock,candidate):
    u.mem_write(Q,bytes([0x93])*256);u.mem_write(0x20001000,bytes(128));put(u,Q,0 if mutex else Q);put(u,Q+8,holder);put(u,Q+12,recursive);put(u,Q+56,count);put(u,Q+60,length);put(u,Q+64,item);u.mem_write(Q+68,bytes([lock&255,lock&255]));put(u,0x20007824,tasks);u.mem_write(0x20007810,struct.pack('<3I',0,0,7));u.mem_write(0xe000e000,bytes(4096));u.reg_write(UC_ARM_REG_BASEPRI,0);u.reg_write(UC_ARM_REG_PRIMASK,0);u.reg_write(UC_ARM_REG_IPSR,33)
    for a in (Q+16,Q+36):u.mem_write(a,struct.pack('<5I',waiting,a+8,0xffffffff,a+8,a+8))
  def call(name,args=(),mode='expire',scheduler=2,allocation=Q,inherit=1,resume=0,yielding=0,send=1):
   nonlocal comparisons,faults
   results=[]
   for u in (stock,candidate):
    f={'trace':[],'fault':False,'checks':0,'mode':mode,'scheduler':scheduler,'allocation':allocation,'inherit':inherit,'resume':resume,'yield':yielding,'send':send};states[id(u)]=f;u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
    for reg,value in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),(*args,0,0,0,0)):u.reg_write(reg,value)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    try:u.emu_start((ENTRIES[name] if u is stock else syms[name])|1,0x20000100,count=100000)
    except UcError:assert f['fault'],(name,args,u is stock,hex(u.reg_read(UC_ARM_REG_PC)),f)
    if not f['fault']:assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
    results.append((f['fault'],None if f['fault'] or name=='prvInitialiseMutex' else u.reg_read(UC_ARM_REG_R0),f['trace'],bytes(u.mem_read(Q,256)),bytes(u.mem_read(0x20001000,128)),bytes(u.mem_read(0xe000ed04,4)),u.reg_read(UC_ARM_REG_BASEPRI)))
   assert results[0]==results[1],(name,args,mode,scheduler,inherit,resume,yielding,results[0][:3],results[1][:3],[(i,a,b) for i,(a,b) in enumerate(zip(results[0][3],results[1][3])) if a!=b][:12]);comparisons+=1;faults+=results[0][0];counts[name]+=1
  for name,kind,allocation,send in itertools.product(('xQueueCreateMutex','xQueueCreateMutexStatic'),(0,1,4,255),(0,Q),(0,1)):
   reset();call(name,(kind,Q) if name.endswith('Static') else (kind,),allocation=allocation,send=send)
  for ptr in (0,Q):reset();call('prvInitialiseMutex',(ptr,))
  for name,holder,recursive,count,wait,scheduler,send in itertools.product(('xQueueTakeMutexRecursive','xQueueGiveMutexRecursive'),(0,0x20001000,0x20002000),(0,1,2,0xfffffffe,0xffffffff),(0,1),(0,1),(0,1,2),(0,1)):
   reset(count,True,holder,recursive);call(name,(Q,wait),scheduler=scheduler,send=send)
  for mutex,holder,count,wait,mode,scheduler,inherit,resume,yielding in itertools.product((0,1),(0,0x20002000),(0,1),(0,1,0xffffffff),('expire','wake','twice'),(0,1,2),(0,1),(0,1),(0,1)):
   reset(count,mutex,holder,waiting=0);call('xQueueSemaphoreTake',(Q,wait),mode=mode,scheduler=scheduler,inherit=inherit,resume=resume,yielding=yielding)
  for mutex,holder,count,item,lock,tasks,woken,waiting,yielding in itertools.product((0,1),(0,0x20001000),(0,1,3),(0,1),(-1,0,2,127),(0,2,128,0xffffffff),(0,0x20001040),(0,1),(0,1)):
   reset(count,mutex,holder,waiting=waiting,lock=lock,tasks=tasks,item=item);call('xQueueGiveFromISR',(Q,woken),yielding=yielding)
  for priority in (0,1,15,55):
   reset(0,True,0x20002000)
   for u in (stock,candidate):put(u,Q+36,1);put(u,Q+48,0x20002018);u.mem_write(0x20002018,struct.pack('<5I',56-priority,Q+44,Q+44,0x20002000,Q+36))
   call('xQueueSemaphoreTake',(Q,1),mode='twice',inherit=1)
  for name in ('xQueueTakeMutexRecursive','xQueueGiveMutexRecursive','xQueueSemaphoreTake','xQueueGiveFromISR'):reset();call(name,(0,0))
 vp.write_text(json.dumps(dict(application_sha256=sha(app),report_sha256=sha(rp),driver_sha256=sha(Path(__file__)),actual_providers=actual,comparisons=comparisons,assertion_comparisons=faults,comparisons_by_function=counts,scope='Actual pinned mutex creation/private init, recursive ownership/count wrap, semaphore take timeout/retry/inheritance paths, ISR give/locks/assertions; actual priority validator and task-count query',limitations=['Queue constructors/send, current-task/held-count, event operations, timeout/scheduler/inheritance boundaries are explicit fixtures. No combined synchronization graph, actual blocking resumption or physical concurrency/instruction identity proof.']),indent=2)+'\n');print(comparisons,'mutex kernel comparisons;',faults,'assertions;',counts)
if __name__=='__main__':main()
