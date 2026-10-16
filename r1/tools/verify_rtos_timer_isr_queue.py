#!/usr/bin/env python3
"""Pinned queue send/delete/copy/unlock versus native, explicit task fixtures."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_INVALID
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
BACKENDS={'vPortEnterCritical':0x95cf4,'vPortExitCritical':0x95d24,'vPortFree':0x95d48,'vTaskInternalSetTimeOutState':0x96160,'vTaskMissedYield':0x96170,'vTaskPlaceOnEventList':0x96188,'vTaskSuspendAll':0x9659c,'xTaskCheckForTimeOut':0x98340,'xTaskGetSchedulerState':0x987a8,'xTaskPriorityDisinherit':0x98910,'xTaskRemoveFromEventList':0x98a4c,'xTaskResumeAll':0x98b24}
# Task-count query executes its actual source body.
ENTRIES={'xQueueGenericSendFromISR':0x97da4};Q=0x20004000

def main():
 out=BASE/'rtos-timer-isr-queue';receipt=out/'verification.json';receipt.unlink(missing_ok=True);rp=out/'report.json';r=json.loads(rp.read_text());obj=out/'timer-isr-queue.o';assert sha(obj)==r['selected_object_sha256']
 for p,d in r['inputs'].items():assert sha(ROOT/p)==d,p
 mp=BASE/'runtime/report.json';mr=json.loads(mp.read_text());memory=BASE/'runtime/memory-runtime.o';assert sha(memory)==mr['relocatable_sha256']
 move_report=BASE/'runtime-memmove/report.json';move=json.loads(move_report.read_text());move_obj=move_report.parent/'memmove.o';assert sha(move_obj)==move['units'][0]['object_sha256'];wrapper_report=BASE/'native-rtc-device/report.json';wrapper=json.loads(wrapper_report.read_text());wrapper_obj=wrapper_report.parent/'native_memory_move-selected.o';assert sha(wrapper_obj)==wrapper['units'][1]['object_sha256']
 count_report=BASE/'rtos-task-count/report.json';count=json.loads(count_report.read_text());count_obj=count_report.parent/'task-count.o';assert sha(count_obj)==count['selected_object_sha256']
 for path,digest in count['inputs'].items():assert sha(ROOT/path)==digest,path
 priority_report=BASE/'rtos-interrupt-priority/report.json';priority=json.loads(priority_report.read_text());assert sha(priority_report.parent/'interrupt-priority.o')==priority['selected_object_sha256']
 for path,digest in priority['inputs'].items():assert sha(ROOT/path)==digest,path
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';states={};comparisons=0;faults=0;calls=0;counts={n:0 for n in ENTRIES}
 with tempfile.TemporaryDirectory() as directory:
  t=Path(directory);ld=t/'layout.ld';elf=t/'test.elf';binary=t/'text.bin';ld.write_text('SECTIONS { .text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } /DISCARD/ : { *(.comment) *(.note*) } }');bindings={n:0x100ef01+i*16 for i,n in enumerate(BACKENDS)};subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--defsym=uxCurrentNumberOfTasks=0x20007824',*['--defsym='+n+'='+hex(a) for n,a in bindings.items()],str(obj),str(memory),str(move_obj),str(wrapper_obj),str(BASE/'rtos-interrupt-priority/interrupt-priority.o'),str(count_obj),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True);syms={x.split()[-1]:int(x.split()[0],16) for x in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x.split())==3}
  stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
  for u in (stock,candidate):u.mem_map(0x20000,0xc0000);u.mem_map(0x1000000,0x10000);u.mem_map(0x20000000,0x40000);u.mem_map(0xe000e000,0x1000)
  stock.mem_write(0x27000,app.read_bytes());candidate.mem_write(0x1000000,binary.read_bytes());kinds={a:n for n,a in BACKENDS.items()};kinds.update({a&~1:n for n,a in bindings.items()})
  def put(u,a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
  def word(u,a):return struct.unpack('<I',bytes(u.mem_read(a,4)))[0]
  def hook(u,a,size,user):
   nonlocal calls
   if a not in kinds:return
   f=states[id(u)];name=kinds[a];args=[u.reg_read(reg) for reg in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)];calls+=1;value=0xdeadbeef;trace=(name,)
   if name=='xTaskGetSchedulerState':value=f['scheduler']
   elif name=='vPortFree':trace=(name,args[0])
   elif name=='vTaskInternalSetTimeOutState':u.mem_write(args[0],struct.pack('<2I',7,1234))
   elif name=='xTaskCheckForTimeOut':
    trace=(name,bytes(u.mem_read(args[0],8)).hex(),word(u,args[1]));f['checks']+=1;value=1 if f['mode']=='expire' or (f['mode']=='twice' and f['checks']>1) else 0;put(u,args[1],0 if value else max(0,word(u,args[1])-1));u.mem_write(args[0],struct.pack('<2I',8,1235))
    if f['mode']=='space':put(u,Q+56,word(u,Q+60)-1)
   elif name=='vTaskPlaceOnEventList':
    trace=(name,*args[:2]);assert args[0]==Q+16
    if f['mode']=='irq':u.mem_write(Q+68,bytes((2,2)));put(u,Q+16,2);put(u,Q+36,2)
   elif name=='xTaskResumeAll':
    f['resumes']+=1;value=f['resume']
    if f['mode'] in ('wake','irq') or (f['mode']=='twice' and f['resumes']>1):put(u,Q+56,word(u,Q+60)-1)
   elif name=='xTaskPriorityDisinherit':trace=(name,args[0]);value=f['yield']
   elif name=='xTaskRemoveFromEventList':
    trace=(name,args[0]);value=f['yield'];assert args[0] in (Q+16,Q+36);assert word(u,args[0])>0;put(u,args[0],word(u,args[0])-1)
   f['trace'].append(trace);u.reg_write(UC_ARM_REG_R0,value);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  def fault(u,access,address,size,value,user):
   if address==0xffffffff and value==0:states[id(u)]['fault']=True
   return False
  for u in (stock,candidate):u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_INVALID,fault)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  def reset(length,item,count,index=0,mutex=False):
   for u in (stock,candidate):
    u.mem_write(Q,bytes((i*37+0xa5)&255 for i in range(0x1200)));u.mem_write(0x20006000,bytes((i*13+7)&255 for i in range(256)));u.mem_write(0xe000ed04,bytes(4));head=0 if mutex else 0x20005000 if item else Q
    for off,value in ((0,head),(4,head+index*item),(8,0x20006100 if mutex else head+length*item),(12,head+(length-1-index)*item),(16,0),(36,0),(56,count),(60,length),(64,item)):put(u,Q+off,value)
    u.mem_write(Q+68,b'\xff\xff\x01')
  def call(name,args,mode='expire',scheduler=2,yielding=0,resume=0):
   nonlocal comparisons,faults
   results=[]
   for u in (stock,candidate):
    f={'trace':[],'fault':False,'checks':0,'resumes':0,'mode':mode,'scheduler':scheduler,'yield':yielding,'resume':resume};states[id(u)]=f;u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101);u.reg_write(UC_ARM_REG_BASEPRI,0);u.reg_write(UC_ARM_REG_IPSR,33);u.mem_write(0x20007810,struct.pack('<3I',0,0,7));u.mem_write(0xe000ed0c,bytes(4));u.mem_write(0x20007824,struct.pack('<I',scheduler))
    for reg,value in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),(*args,0,0,0,0)):u.reg_write(reg,value)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    try:u.emu_start((ENTRIES[name] if u is stock else syms[name])|1,0x20000100,count=1000000)
    except UcError:assert f['fault'],(name,args,u is stock,hex(u.reg_read(UC_ARM_REG_PC)),f)
    if not f['fault']:assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
    results.append((f['fault'],None if f['fault'] or name in ('vQueueDelete','prvUnlockQueue') else u.reg_read(UC_ARM_REG_R0),f['trace'],bytes(u.mem_read(Q,0x1200)),bytes(u.mem_read(0x20006000,256)),bytes(u.mem_read(0xe000ed04,4)),u.reg_read(UC_ARM_REG_BASEPRI)))
   assert results[0]==results[1],(name,args,mode,scheduler,yielding,resume,[x[:3] for x in results],[(i,a,b) for i,(a,b) in enumerate(zip(results[0][3],results[1][3])) if a!=b][:20],results[0][5:],results[1][5:]);comparisons+=1;faults+=results[0][0];counts[name]+=1
  for length,item,count,position,index,waiting,yielding,woken,lock,tasks in itertools.product((1,3),(0,1,4,17),(0,1,3),(0,1,2),(0,1),(0,1),(0,1),(0,0x20006080),(-1,0,2,127),(0,1,2,126,127,128,0x7fffffff,0x80000000,0xffffffff)):
   if count>length or index>=length:continue
   reset(length,item,count,index)
   for u in (stock,candidate):put(u,Q+36,waiting);u.mem_write(Q+69,bytes([lock&255]))
   call('xQueueGenericSendFromISR',(Q,0x20006000 if item else 0,woken,position),scheduler=tasks,yielding=yielding)
  for delta in (-17,-4,-1,0,1,4,17):
   reset(3,17,0);call('xQueueGenericSendFromISR',(Q,0x20005000+delta,0x20006080,0),scheduler=2)
  reset(1,1,0);call('xQueueGenericSendFromISR',(Q,0,0,0));reset(1,1,0);call('xQueueGenericSendFromISR',(0,0x20006000,0,0))
 receipt.write_text(json.dumps(dict(application_sha256=sha(app),report_sha256=sha(rp),driver_sha256=sha(Path(__file__)),memory_report_sha256=sha(mp),memory_object_sha256=sha(memory),memory_provider_reports={'runtime-memmove/report.json':sha(move_report),'native-rtc-device/report.json':sha(wrapper_report)},memory_provider_objects={'runtime-memmove/memmove.o':sha(move_obj),'native-rtc-device/native_memory_move-selected.o':sha(wrapper_obj)},task_count_report_sha256=sha(count_report),task_count_object_sha256=sha(count_obj),priority_report_sha256=sha(BASE/'rtos-interrupt-priority/report.json'),priority_object_sha256=sha(BASE/'rtos-interrupt-priority/interrupt-priority.o'),comparisons=comparisons,assertion_comparisons=faults,backend_calls_per_implementation=calls//2,comparisons_by_function=counts,scope='Actual pinned ISR queue send/copy and SDK priority validator, native-return-ABI movement adapter and musl memmove; ring/front/overwrite/full, receive waiter/woken pointer, lock/task-count saturation, overlap and assertions',limitations=['Event removal and mutex disinherit are fixtures. Actual task-count query, SDK priority validator and BASEPRI mask/restore bodies execute. No physical ISR concurrency or instruction identity proof.']),indent=2)+'\n');print(comparisons,'queue operation comparisons;',faults,'assertions;',counts)
if __name__=='__main__':main()
