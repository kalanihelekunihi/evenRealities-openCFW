#!/usr/bin/env python3
"""Pinned CMSIS message queues versus native, explicit kernel queue boundaries."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ENTRIES={'osMutexAcquire':0x7d488,'osMutexNew':0x7d4d6,'osMutexRelease':0x7d536,'osSemaphoreAcquire':0x7d57c,'osSemaphoreGetCount':0x7d5e8,'osSemaphoreRelease':0x7d698}
BACKENDS={'xTaskGetSchedulerState':0x987a8,'xQueueCreateMutex':0x97ade,'xQueueCreateMutexStatic':0x97af4,'xQueueTakeMutexRecursive':0x98284,'xQueueGiveMutexRecursive':0x97f14,'xQueueSemaphoreTake':0x98120,'xQueueGenericSend':0x97c50,'xQueueGiveFromISR':0x97e6c,'xQueueReceiveFromISR':0x9807c,'uxQueueMessagesWaiting':0x95634,'uxQueueMessagesWaitingFromISR':0x95656}

def main():
 out=BASE/'rtos-synchronization';receipt=out/'verification.json';receipt.unlink(missing_ok=True);rp=out/'report.json';r=json.loads(rp.read_text());obj=out/'synchronization.o';assert sha(obj)==r['selected_object_sha256']
 for p,d in r['inputs'].items():assert sha(ROOT/p)==d,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';states={};comparisons=0;calls=0;counts={n:0 for n in ENTRIES}
 with tempfile.TemporaryDirectory() as directory:
  t=Path(directory);ld=t/'layout.ld';elf=t/'test.elf';binary=t/'text.bin';ld.write_text('SECTIONS { .text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } /DISCARD/ : { *(.comment) *(.note*) } }');bindings={n:0x100ef01+i*16 for i,n in enumerate(BACKENDS)};subprocess.run(['arm-none-eabi-ld','-T',str(ld),*['--defsym='+n+'='+hex(a) for n,a in bindings.items()],str(obj),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True);syms={x.split()[-1]:int(x.split()[0],16) for x in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x.split())==3};stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
  for u in (stock,candidate):u.mem_map(0x20000,0xc0000);u.mem_map(0x1000000,0x10000);u.mem_map(0x20000000,0x40000);u.mem_map(0xe000e000,4096)
  stock.mem_write(0x27000,app.read_bytes());candidate.mem_write(0x1000000,binary.read_bytes());kinds={a:n for n,a in BACKENDS.items()};kinds.update({a&~1:n for n,a in bindings.items()})
  def hook(u,a,size,user):
   nonlocal calls
   if a not in kinds:return
   f=states[id(u)];name=kinds[a];args=[u.reg_read(reg) for reg in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)];value=f['result'];calls+=1
   if name=='xTaskGetSchedulerState':trace=(name,);value=f['scheduler']
   elif name=='xQueueCreateMutex':trace=(name,args[0])
   elif name=='xQueueCreateMutexStatic':trace=(name,*args[:2])
   elif name in ('uxQueueMessagesWaiting','uxQueueMessagesWaitingFromISR','xQueueGiveMutexRecursive'):trace=(name,args[0])
   elif name in ('xQueueReceiveFromISR','xQueueGiveFromISR'):
    ptr=args[2] if name=='xQueueReceiveFromISR' else args[1];assert struct.unpack('<I',bytes(u.mem_read(ptr,4)))[0]==0;u.mem_write(ptr,struct.pack('<I',f['yield']));trace=(name,args[0],args[1] if name=='xQueueReceiveFromISR' else None)
   elif name=='xQueueGenericSend':trace=(name,*args)
   else:trace=(name,*args[:2])
   f['trace'].append(trace);u.reg_write(UC_ARM_REG_R0,value&0xffffffff);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  for u in (stock,candidate):u.hook_add(UC_HOOK_CODE,hook)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  def case(name,args,attr=None,ipsr=0,primask=0,basepri=0,scheduler=1,result=1,yielding=0,capacity=7):
   nonlocal comparisons
   outcomes=[]
   for u in (stock,candidate):
    states[id(u)]={'trace':[],'scheduler':scheduler,'result':result,'yield':yielding};u.mem_write(0x20002000,bytes([0x95])*128);u.mem_write(0x2000203c,struct.pack('<I',capacity));u.mem_write(0x20003000,struct.pack('<4I',*attr) if attr is not None else bytes(16));u.mem_write(0x20004000,bytes([0xa5])*256);u.mem_write(0xe000ed04,bytes(4));u.reg_write(UC_ARM_REG_IPSR,ipsr);u.reg_write(UC_ARM_REG_PRIMASK,primask);u.reg_write(UC_ARM_REG_BASEPRI,basepri);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
    for reg,value in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),args):u.reg_write(reg,value)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    u.emu_start((ENTRIES[name] if u is stock else syms[name])|1,0x20000100,count=100000);assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)];outcomes.append((u.reg_read(UC_ARM_REG_R0),states[id(u)]['trace'],bytes(u.mem_read(0x20003000,16)),bytes(u.mem_read(0x20002000,128)),bytes(u.mem_read(0x20004000,256)),bytes(u.mem_read(0xe000ed04,4)),u.reg_read(UC_ARM_REG_BASEPRI),u.reg_read(UC_ARM_REG_PRIMASK)))
   assert outcomes[0]==outcomes[1],(name,args,attr,ipsr,primask,basepri,scheduler,result,yielding,outcomes);comparisons+=1;counts[name]+=1
  contexts=list(itertools.product((0,16),(0,1),(0,128),(0,1,2)))
  for bits,cb,cbsize,result,ctx in itertools.product((0,1,2,4,8,16,0x80000000,0xffffffff),(0,0x20002000,0x20002001),(0,1,79,80,81,0xffffffff),(0,0x20002000,0x20002001),contexts):
   attr=(0xfffffff0,bits,cb,cbsize);case('osMutexNew',(0x20003000,),attr,ipsr=ctx[0],primask=ctx[1],basepri=ctx[2],scheduler=ctx[3],result=result)
  for ctx,result in itertools.product(contexts,(0,0x20002000)):case('osMutexNew',(0,),ipsr=ctx[0],primask=ctx[1],basepri=ctx[2],scheduler=ctx[3],result=result)
  for name,handle,timeout,result,yielding,ctx in itertools.product(('osMutexAcquire','osSemaphoreAcquire'),(0,1,0x20002000,0x20002001),(0,1,0xffffffff),(0,1,0xffffffff),(0,1,0xffffffff),contexts):
   case(name,(handle,timeout),ipsr=ctx[0],primask=ctx[1],basepri=ctx[2],scheduler=ctx[3],result=result,yielding=yielding)
  for name,handle,result,yielding,ctx in itertools.product(('osMutexRelease','osSemaphoreRelease','osSemaphoreGetCount'),(0,1,0x20002000,0x20002001),(0,1,0xffffffff),(0,1,0xffffffff),contexts):
   case(name,(handle,),ipsr=ctx[0],primask=ctx[1],basepri=ctx[2],scheduler=ctx[3],result=result,yielding=yielding)
 receipt.write_text(json.dumps(dict(application_sha256=sha(app),report_sha256=sha(rp),driver_sha256=sha(Path(__file__)),comparisons=comparisons,comparisons_by_function=counts,backend_calls_per_implementation=calls//2,scope='Actual unchanged CMSIS mutex/semaphore wrappers/IRQ predicate;16-byte mutex attributes,80-byte static threshold, robust rejection, recursive LSB tag/untag, task/ISR routing, timeout/status, wake-yield, counts and NULLs',limitations=['Kernel mutex/queue constructors, take/give/query and scheduler-state boundaries are fixtures. IRQ/mask registers and ICSR are emulator inputs. No composed queue/scheduler graph, physical interrupts or image instruction identity proof.']),indent=2)+'\n');print(comparisons,'CMSIS synchronization comparisons;',counts)
if __name__=='__main__':main()
