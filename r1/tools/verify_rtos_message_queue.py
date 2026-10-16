#!/usr/bin/env python3
"""Pinned CMSIS message queues versus native, explicit kernel queue boundaries."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ENTRIES={'osMessageQueueGet':0x7d310,'osMessageQueueGetCapacity':0x7d388,'osMessageQueueGetCount':0x7d390,'osMessageQueueNew':0x7d3b4,'osMessageQueuePut':0x7d40c}
BACKENDS={'xTaskGetSchedulerState':0x987a8,'xQueueGenericCreate':0x97b0e,'xQueueGenericCreateStatic':0x97b62,'xQueueGenericSend':0x97c50,'xQueueGenericSendFromISR':0x97da4,'xQueueReceive':0x97f50,'xQueueReceiveFromISR':0x9807c,'uxQueueMessagesWaiting':0x95634,'uxQueueMessagesWaitingFromISR':0x95656}
def main():
 out=BASE/'rtos-message-queue';receipt=out/'verification.json';receipt.unlink(missing_ok=True);rp=out/'report.json';r=json.loads(rp.read_text());obj=out/'message-queue.o';assert sha(obj)==r['selected_object_sha256']
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
   elif name=='xQueueGenericCreate':trace=(name,*args[:3])
   elif name=='xQueueGenericCreateStatic':trace=(name,*args,struct.unpack('<I',bytes(u.mem_read(u.reg_read(UC_ARM_REG_SP),4)))[0])
   elif name in ('uxQueueMessagesWaiting','uxQueueMessagesWaitingFromISR'):trace=(name,args[0])
   elif name.endswith('FromISR'):
    assert struct.unpack('<I',bytes(u.mem_read(args[2],4)))[0]==0;u.mem_write(args[2],struct.pack('<I',f['yield']));trace=(name,*args[:2],args[3] if name=='xQueueGenericSendFromISR' else None)
   else:trace=(name,*args[:3],args[3] if name=='xQueueGenericSend' else None)
   if name in ('xQueueReceive','xQueueReceiveFromISR') and value==1:u.mem_write(args[1],b'\x12\x34\x56\x78')
   f['trace'].append(trace);u.reg_write(UC_ARM_REG_R0,value&0xffffffff);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  for u in (stock,candidate):u.hook_add(UC_HOOK_CODE,hook)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  def case(name,args,attr=None,ipsr=0,primask=0,basepri=0,scheduler=1,result=1,yielding=0,capacity=7):
   nonlocal comparisons
   outcomes=[]
   for u in (stock,candidate):
    states[id(u)]={'trace':[],'scheduler':scheduler,'result':result,'yield':yielding};u.mem_write(0x20002000,bytes([0x95])*128);u.mem_write(0x2000203c,struct.pack('<I',capacity));u.mem_write(0x20003000,struct.pack('<6I',*attr) if attr is not None else bytes(24));u.mem_write(0x20004000,bytes([0xa5])*256);u.mem_write(0xe000ed04,bytes(4));u.reg_write(UC_ARM_REG_IPSR,ipsr);u.reg_write(UC_ARM_REG_PRIMASK,primask);u.reg_write(UC_ARM_REG_BASEPRI,basepri);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
    for reg,value in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),args):u.reg_write(reg,value)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    u.emu_start((ENTRIES[name] if u is stock else syms[name])|1,0x20000100,count=100000);assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)];outcomes.append((u.reg_read(UC_ARM_REG_R0),states[id(u)]['trace'],bytes(u.mem_read(0x20003000,24)),bytes(u.mem_read(0x20002000,128)),bytes(u.mem_read(0x20004000,256)),bytes(u.mem_read(0xe000ed04,4)),u.reg_read(UC_ARM_REG_BASEPRI),u.reg_read(UC_ARM_REG_PRIMASK)))
   assert outcomes[0]==outcomes[1],(name,args,attr,ipsr,primask,basepri,scheduler,result,yielding,outcomes);comparisons+=1;counts[name]+=1
  for count,size,cb,cbsize,memory,memsize,result in itertools.product((0,1,3,0x10000,0x80000000,0xffffffff),(0,1,4,0x10000,0x80000000,0xffffffff),(0,0x20002000),(0,79,80,81,0xffffffff),(0,0x20004000),(0,1,4,12,0xffffffff),(0,0x20002000)):
   attr=(0xfffffff0,0xffffffff,cb,cbsize,memory,memsize);case('osMessageQueueNew',(count,size,0x20003000),attr,result=result)
  contexts=list(itertools.product((0,16),(0,1),(0,128),(0,1,2)))
  attrs=(None,(0,0,0,0,0,0),(0xfffffff0,0xffffffff,0x20002000,80,0x20004000,12),(0,0,0x20002000,79,0x20004000,12))
  for attr,ctx,count,size in itertools.product(attrs,contexts,(0,3),(0,4)):case('osMessageQueueNew',(count,size,0 if attr is None else 0x20003000),attr,*ctx,result=0x20002000)
  for name,queue,msg,prio,timeout,result,yielding,ctx in itertools.product(('osMessageQueuePut','osMessageQueueGet'),(0,0x20002000),(0,0x20004000),(0,0xfffffff0),(0,1,0xffffffff),(0,1,0xffffffff),(0,1,0xffffffff),contexts):case(name,(queue,msg,prio,timeout),ipsr=ctx[0],primask=ctx[1],basepri=ctx[2],scheduler=ctx[3],result=result,yielding=yielding)
  for queue,value,ctx in itertools.product((0,0x20002000),(0,1,0xffffffff),contexts):
   case('osMessageQueueGetCapacity',(queue,),ipsr=ctx[0],primask=ctx[1],basepri=ctx[2],scheduler=ctx[3],capacity=value)
   case('osMessageQueueGetCount',(queue,),ipsr=ctx[0],primask=ctx[1],basepri=ctx[2],scheduler=ctx[3],result=value)
 receipt.write_text(json.dumps(dict(application_sha256=sha(app),report_sha256=sha(rp),driver_sha256=sha(Path(__file__)),comparisons=comparisons,comparisons_by_function=counts,backend_calls_per_implementation=calls//2,scope='Actual unchanged CMSIS queue wrappers/IRQ predicate;24-byte attributes,80-byte static threshold,32-bit product wrap, ignored names/bits/priority, task/ISR routing, zero/nonzero timeout, status and wake-yield, capacity/count and NULLs',limitations=['Kernel queue constructors/send/receive/query and scheduler-state boundaries are fixtures. IRQ/mask registers and ICSR are emulator inputs. No composed queue/scheduler graph, physical interrupts or image instruction identity proof.']),indent=2)+'\n');print(comparisons,'CMSIS message queue comparisons;',counts)
if __name__=='__main__':main()
