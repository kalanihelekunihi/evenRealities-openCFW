#!/usr/bin/env python3
"""Pinned CMSIS semaphore creation versus native, actual IRQ-context predicate."""
import hashlib,itertools,json,struct,subprocess,tempfile,sys
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
BACKENDS={'xTaskGetSchedulerState':0x987a8,'xQueueGenericCreate':0x97b0e,'xQueueGenericCreateStatic':0x97b62,'xQueueCreateCountingSemaphore':0x97a88,'xQueueCreateCountingSemaphoreStatic':0x97ab0,'xQueueGenericSend':0x97c50,'vQueueDelete':0x95f70}
def main():
 real_queue='--real-queue' in sys.argv
 out=BASE/'rtos-semaphore-new';rp=out/'report.json';r=json.loads(rp.read_text());obj=out/'semaphore-new.o';assert sha(obj)==r['selected_object_sha256']
 for p,d in r['inputs'].items():assert sha(ROOT/p)==d,p
 queue_report=BASE/'rtos-queue-create/report.json';queue_object=queue_report.parent/'queue-create.o';extra=[];backends=dict(BACKENDS)
 if real_queue:
  qr=json.loads(queue_report.read_text());assert sha(queue_object)==qr['selected_object_sha256'];extra=[str(queue_object)];backends={n:a for n,a in backends.items() if n not in ('xQueueGenericCreate','xQueueGenericCreateStatic','xQueueCreateCountingSemaphore','xQueueCreateCountingSemaphoreStatic')};backends.update({'pvPortMalloc':0x855a0,'vPortEnterCritical':0x95cf4,'vPortExitCritical':0x95d24,'xTaskRemoveFromEventList':0x98a4c})
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';states={};count=0;backend_calls=0
 with tempfile.TemporaryDirectory() as directory:
  t=Path(directory);ld=t/'layout.ld';elf=t/'test.elf';binary=t/'text.bin';ld.write_text('SECTIONS { .text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } /DISCARD/ : { *(.comment) *(.note*) } }');bindings={n:0x100ef01+i*16 for i,n in enumerate(backends)};subprocess.run(['arm-none-eabi-ld','-T',str(ld),*['--defsym='+n+'='+hex(a) for n,a in bindings.items()],str(obj),*extra,'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True);syms={x.split()[-1]:int(x.split()[0],16) for x in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x.split())==3}
  stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
  for u in (stock,candidate):u.mem_map(0x20000,0xc0000);u.mem_map(0x1000000,0x10000);u.mem_map(0x20000000,0x40000)
  stock.mem_write(0x27000,app.read_bytes());candidate.mem_write(0x1000000,binary.read_bytes());kinds={a:n for n,a in backends.items()};kinds.update({a&~1:n for n,a in bindings.items()})
  def hook(u,a,size,user):
   nonlocal backend_calls
   name=kinds.get(a)
   if not name:return
   f=states[id(u)];args=[u.reg_read(reg) for reg in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)];backend_calls+=1
   if name=='pvPortMalloc':trace=(name,args[0]);value=f['handle']
   elif name in ('vPortEnterCritical','vPortExitCritical'):trace=(name,);value=0xdeadbeef
   elif name=='xTaskRemoveFromEventList':raise AssertionError('New queues cannot remove existing waiters')
   elif name=='xTaskGetSchedulerState':trace=(name,);value=f['scheduler']
   elif name=='xQueueGenericCreate':trace=(name,*args[:3]);value=f['handle']
   elif name=='xQueueGenericCreateStatic':trace=(name,*args,struct.unpack('<I',bytes(u.mem_read(u.reg_read(UC_ARM_REG_SP),4)))[0]);value=f['handle']
   elif name=='xQueueCreateCountingSemaphore':trace=(name,*args[:2]);value=f['handle']
   elif name=='xQueueCreateCountingSemaphoreStatic':trace=(name,*args[:3]);value=f['handle']
   elif name=='xQueueGenericSend':trace=(name,*args);value=f['send']
   else:trace=(name,args[0]);value=0xdeadbeef
   f['trace'].append(trace);u.reg_write(UC_ARM_REG_R0,value);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  for u in (stock,candidate):u.hook_add(UC_HOOK_CODE,hook)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11];attrs=[None,*itertools.product((0,0x20003300),(0,79,80,81),(0,0x20003200,0xfffffff0))]
  for maximum,initial,attr,ipsr,primask,basepri,scheduler,handle,send in itertools.product((0,1,2,0xffffffff),(0,1,2,0xffffffff),attrs,(0,16),(0,1),(0,128),(0,1,2),(0,0x20003400),(0,1)):
   results=[]
   for u in (stock,candidate):
    states[id(u)]={'trace':[],'scheduler':scheduler,'handle':handle,'send':send};u.mem_write(0x20003000,struct.pack('<4I',attr[2],0xffffffff,attr[0],attr[1]) if attr else bytes(16));u.mem_write(0x20003200,b'sem\0');u.mem_write(0x20003300,bytes([0x95])*96);u.mem_write(0x20003400,bytes([0xa5])*256);u.reg_write(UC_ARM_REG_IPSR,ipsr);u.reg_write(UC_ARM_REG_PRIMASK,primask);u.reg_write(UC_ARM_REG_BASEPRI,basepri);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
    for reg,value in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2),(maximum,initial,0x20003000 if attr else 0)):u.reg_write(reg,value)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    u.emu_start((0x7d60c if u is stock else syms['osSemaphoreNew'])|1,0x20000100,count=100000);assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
    results.append((u.reg_read(UC_ARM_REG_R0),states[id(u)]['trace'],bytes(u.mem_read(0x20003000,16)),bytes(u.mem_read(0x20003300,96)),bytes(u.mem_read(0x20003400,256)),u.reg_read(UC_ARM_REG_IPSR),u.reg_read(UC_ARM_REG_PRIMASK),u.reg_read(UC_ARM_REG_BASEPRI)))
   assert results[0]==results[1],(maximum,initial,attr,ipsr,primask,basepri,scheduler,handle,send,results);count+=1
 receipt=dict(application_sha256=sha(app),report_sha256=sha(rp),comparisons=count,backend_calls_per_implementation=backend_calls//2,scope='Actual pinned CMSIS osSemaphoreNew/IRQ context; static/dynamic binary/counting routes,80-byte bounds, attributes/name ignored, failed initial give deletion, ISR and scheduler/mask contexts',limitations=['FreeRTOS queue allocation/send/delete and scheduler state are bounded fixtures. Real allocator, queue layout/scheduler integration, physical exceptions and whole-image identity remain gates.'])
 if real_queue:
  receipt.update(queue_report_sha256=sha(queue_report),queue_object_sha256=sha(queue_object),driver_sha256=sha(Path(__file__)),actual_queue_constructors_executed=True,scope='Actual pinned CMSIS osSemaphoreNew plus FreeRTOS queue constructors/reset/list; full queue bytes and attribute canaries compared',limitations=['Allocator, scheduler state, critical entry/exit and queue send/delete remain bounded fixtures. Full scheduler, real heap, physical behavior and whole-image identity remain gates.'])
 (out/('queue-integration-verification.json' if real_queue else 'verification.json')).write_text(json.dumps(receipt,indent=2)+'\n');print(count,'CMSIS semaphore creation comparisons;',backend_calls//2,'backend calls; actual queue:',real_queue)
if __name__=='__main__':main()
