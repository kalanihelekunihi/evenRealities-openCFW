#!/usr/bin/env python3
"""Timer constructors/initializer/commands versus native with explicit backend fixtures."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_INVALID
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ENTRIES={'xTimerCreate':0x98c48,'xTimerCreateStatic':0x98c7c,'r1_timer_initialise_new':0x8515a,'xTimerGenericCommand':0x98d04}
BACKENDS={'pvPortMalloc':0x855a0,'r1_native_timer_infrastructure':0x84e58,'xTaskGetSchedulerState':0x987a8,'xQueueGenericSend':0x97c50,'xQueueGenericSendFromISR':0x97da4}
def main():
 out=BASE/'rtos-timer-api';receipt=out/'verification.json';receipt.unlink(missing_ok=True);rp=out/'report.json';r=json.loads(rp.read_text());obj=out/'timer-api.o';assert sha(obj)==r['selected_object_sha256']
 for p,d in r['inputs'].items():assert sha(ROOT/p)==d,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';states={};comparisons=0;faults=0;counts={n:0 for n in ENTRIES}
 with tempfile.TemporaryDirectory() as directory:
  t=Path(directory);ld=t/'layout.ld';elf=t/'test.elf';binary=t/'text.bin';lists=t/'list.o';lo=BASE/'rtos-task-wait/list.o';lr=json.loads((BASE/'rtos-task-wait/report.json').read_text());assert sha(lo)==lr['list_unit']['object_sha256'];subprocess.run(['arm-none-eabi-ld','-r','--gc-sections','--undefined=vListInitialiseItem',str(lo),'-o',str(lists)],check=True);ld.write_text('SECTIONS { .text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } /DISCARD/ : { *(.comment) *(.note*) } }');bindings={n:0x100ee01+i*16 for i,n in enumerate(BACKENDS)};subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--defsym=xTimerQueue=0x2000785c',*['--defsym='+n+'='+hex(a) for n,a in bindings.items()],str(obj),str(lists),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True);syms={x.split()[-1]:int(x.split()[0],16) for x in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x.split())==3};stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
  for u in (stock,candidate):u.mem_map(0x20000,0xc0000);u.mem_map(0x1000000,0x10000);u.mem_map(0x20000000,0x40000)
  stock.mem_write(0x27000,app.read_bytes());candidate.mem_write(0x1000000,binary.read_bytes());kinds={a:n for n,a in BACKENDS.items()};kinds.update({a&~1:n for n,a in bindings.items()})
  def hook(u,a,size,user):
   if a not in kinds:return
   f=states[id(u)];name=kinds[a];args=[u.reg_read(reg) for reg in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)];value=0;trace=(name,)
   if name=='pvPortMalloc':assert args[0]==44;value=f['allocation'];trace=(name,44)
   elif name=='xTaskGetSchedulerState':value=f['scheduler']
   elif name in ('xQueueGenericSend','xQueueGenericSendFromISR'):
    assert args[0]==0x20002000;message=struct.unpack('<3I',bytes(u.mem_read(args[1],12)));trace=(name,args[0],message,args[2],args[3]);value=f['result']
    if name=='xQueueGenericSendFromISR' and args[2]:u.mem_write(args[2],struct.pack('<I',0x12345678))
   f['trace'].append(trace);u.reg_write(UC_ARM_REG_R0,value);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  def fault(u,access,a,size,value,user):
   if a==0xffffffff and value==0:states[id(u)]['fault']=True
   return False
  for u in (stock,candidate):u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_INVALID,fault)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  def call(name,args,status=0,allocation=0x20001000,queue=0x20002000,scheduler=2,result=1):
   nonlocal comparisons,faults
   outcomes=[]
   for u in (stock,candidate):
    f={'trace':[],'fault':False,'allocation':allocation,'scheduler':scheduler,'result':result};states[id(u)]=f;u.mem_write(0x20001000,bytes([0x93])*0x2000);u.mem_write(0x20001028,bytes([status]));u.mem_write(0x2000785c,struct.pack('<I',queue));u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101);u.reg_write(UC_ARM_REG_BASEPRI,0);u.reg_write(UC_ARM_REG_PRIMASK,0)
    for reg,value in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),args):u.reg_write(reg,value)
    u.mem_write(0x2003f000,struct.pack('<2I',*(list(args[4:])+[0,0])[:2]))
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    try:u.emu_start((ENTRIES[name] if u is stock else syms[name])|1,0x20000100,count=100000)
    except UcError:assert f['fault'],(name,args,u is stock,hex(u.reg_read(UC_ARM_REG_PC)))
    if not f['fault']:assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
    outcomes.append((f['fault'],None if f['fault'] or name=='r1_timer_initialise_new' else u.reg_read(UC_ARM_REG_R0),f['trace'],bytes(u.mem_read(0x20001000,0x2000)),bytes(u.mem_read(0x2000785c,4)),u.reg_read(UC_ARM_REG_BASEPRI)))
   assert outcomes[0]==outcomes[1],(name,args,status,[x[:3] for x in outcomes],[(i,a,b) for i,(a,b) in enumerate(zip(outcomes[0][3],outcomes[1][3])) if a!=b][:12]);comparisons+=1;faults+=outcomes[0][0];counts[name]+=1
  for name,period,auto,ident,callback,success in itertools.product(('xTimerCreate','xTimerCreateStatic'),(0,1,100,0x80000000,0xffffffff),(0,1,0xffffffff),(0,0x12345678),(0,0x100f001),(0,1)):
   args=(0x20002800,period,auto,ident,callback)
   if name=='xTimerCreateStatic':args+=(0x20001000 if success else 0,)
   call(name,args,allocation=0x20001000 if success else 0)
  for period,auto,status in itertools.product((0,1,0xffffffff),(0,1,0xffffffff),range(256)):call('r1_timer_initialise_new',(0x20002800,period,auto,0x12345678,0x100f001,0x20001000),status=status)
  for command,value,queue,scheduler,wait,result,woken in itertools.product((-1,0,1,5,6,9,0x7fffffff),(0,100,0xffffffff),(0,0x20002000),(0,1,2),(0,1,0xffffffff),(0,1,0xffffffff),(0,0x20001200)):
   call('xTimerGenericCommand',(0x20001000,command&0xffffffff,value,woken,wait),queue=queue,scheduler=scheduler,result=result)
  call('xTimerGenericCommand',(0,1,0,0,0))
 receipt.write_text(json.dumps(dict(application_sha256=sha(app),report_sha256=sha(rp),driver_sha256=sha(Path(__file__)),list_report_sha256=sha(BASE/'rtos-task-wait/report.json'),list_object_sha256=sha(lo),comparisons=comparisons,assertion_comparisons=faults,comparisons_by_function=counts,scope='Unchanged pinned dynamic/static timer creation/private initializer/generic-command bodies and actual list-item initialization;44-byte timer fields/status, NULL/failure/zero-period assertions, task/ISR routing, scheduler-dependent wait and return values',limitations=['Heap allocation, timer infrastructure, scheduler-state and task/ISR queue sends are explicit fixtures. Queue message bytes12..15 are uninitialized padding and excluded from the call contract; first12 bytes are checked exactly. No combined timer graph, ISR behavior on hardware or instruction identity proof.']),indent=2)+'\n');print(comparisons,'timer API comparisons;',faults,'assertions;',counts)
if __name__=='__main__':main()
