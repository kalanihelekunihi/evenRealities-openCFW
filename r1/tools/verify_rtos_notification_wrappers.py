#!/usr/bin/env python3
"""Native CMSIS flags/delay contracts with explicit notification/event/tick fixtures."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ENTRIES={'osDelay':0x7d154,'osEventFlagsSet':0x7d1a0,'osThreadFlagsSet':0x7d6f4,'osThreadFlagsWait':0x7d780}
BACKENDS={'vTaskDelay':0x95fd4,'xEventGroupGetBitsFromISR':0x977de,'xEventGroupSetBits':0x977f4,'xEventGroupSetBitsFromISR':0x9787c,'xTaskGenericNotify':0x98484,'xTaskGenericNotifyFromISR':0x985ac,'xTaskGenericNotifyWait':0x98700,'xTaskGetSchedulerState':0x987a8,'xTaskGetTickCount':0x987c4}
def main():
 out=BASE/'rtos-notification-wrappers';vp=out/'verification.json';vp.unlink(missing_ok=True);rp=out/'report.json';r=json.loads(rp.read_text());obj=out/'notification-wrappers.o';assert sha(obj)==r['selected_object_sha256']
 for p,d in r['inputs'].items():assert sha(ROOT/p)==d,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';states={};comparisons=0;counts={n:0 for n in ENTRIES}
 with tempfile.TemporaryDirectory() as directory:
  t=Path(directory);ld=t/'layout.ld';elf=t/'test.elf';binary=t/'text.bin';ld.write_text('SECTIONS { .text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } /DISCARD/ : { *(.comment) *(.note*) } }');bindings={n:0x100ee01+i*16 for i,n in enumerate(BACKENDS)};subprocess.run(['arm-none-eabi-ld','-T',str(ld),*['--defsym='+n+'='+hex(a) for n,a in bindings.items()],str(obj),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True);syms={x.split()[-1]:int(x.split()[0],16) for x in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x.split())==3};stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
  for u in (stock,candidate):u.mem_map(0x20000,0xc0000);u.mem_map(0x1000000,0x10000);u.mem_map(0x20000000,0x40000);u.mem_map(0xe000e000,4096)
  stock.mem_write(0x27000,app.read_bytes());candidate.mem_write(0x1000000,binary.read_bytes());kinds={a:n for n,a in BACKENDS.items()};kinds.update({a&~1:n for n,a in bindings.items()})
  def word(u,a):return struct.unpack('<I',bytes(u.mem_read(a,4)))[0]
  def put(u,a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
  def hook(u,a,size,user):
   if a not in kinds:return
   f=states[id(u)];name=kinds[a];args=[u.reg_read(reg) for reg in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)];value=f['status'];trace=(name,)
   if name=='xTaskGetSchedulerState':value=f['scheduler']
   elif name=='xTaskGetTickCount':value=(f['start']+f['ticks']*f['step'])&0xffffffff;f['ticks']+=1;trace=(name,value)
   elif name=='vTaskDelay':trace=(name,args[0])
   elif name in ('xTaskGenericNotify','xTaskGenericNotifyFromISR'):
    sp=u.reg_read(UC_ARM_REG_SP);previous=word(u,sp);woken=word(u,sp+4) if name.endswith('FromISR') else 0;assert args[1]==0;trace=(name,*args,bool(previous),bool(woken))
    if previous:put(u,previous,f['notified'])
    if args[3]==1:f['notified']|=args[2]
    else:assert args[3]==0
    if woken:assert word(u,woken)==0;put(u,woken,f['yield'])
   elif name=='xTaskGenericNotifyWait':
    assert args[0]==args[1]==0;timeout=word(u,u.reg_read(UC_ARM_REG_SP));trace=(name,*args[:3],timeout);value,nval=f['sequence'].pop(0) if f['sequence'] else (0,0);put(u,args[3],nval)
   elif name=='xEventGroupSetBitsFromISR':
    assert word(u,args[2])==0;put(u,args[2],f['yield']);trace=(name,*args[:2])
   elif name=='xEventGroupGetBitsFromISR':value=f['event'];trace=(name,args[0])
   elif name=='xEventGroupSetBits':value=f['event']|args[1];trace=(name,*args[:2])
   f['trace'].append(trace);u.reg_write(UC_ARM_REG_R0,value&0xffffffff);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  for u in (stock,candidate):u.hook_add(UC_HOOK_CODE,hook)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  def case(name,args,ctx=(0,0,0,1),notified=0,event=0,status=1,yielding=0,start=0,step=0,sequence=((1,3),)):
   nonlocal comparisons
   results=[]
   for u in (stock,candidate):
    f=dict(trace=[],scheduler=ctx[3],notified=notified,event=event,status=status,yielding=yielding,start=start,step=step,ticks=0,sequence=list(sequence));f['yield']=yielding;states[id(u)]=f;u.mem_write(0xe000ed04,bytes(4));u.reg_write(UC_ARM_REG_IPSR,ctx[0]);u.reg_write(UC_ARM_REG_PRIMASK,ctx[1]);u.reg_write(UC_ARM_REG_BASEPRI,ctx[2]);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
    for reg,value in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),args):u.reg_write(reg,value)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    u.emu_start((ENTRIES[name] if u is stock else syms[name])|1,0x20000100,count=100000);assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)];results.append((u.reg_read(UC_ARM_REG_R0),f['trace'],f['notified'],word(u,0xe000ed04),u.reg_read(UC_ARM_REG_BASEPRI),u.reg_read(UC_ARM_REG_PRIMASK)))
   assert results[0]==results[1],(name,args,ctx,notified,event,status,yielding,start,step,sequence,results);comparisons+=1;counts[name]+=1
  contexts=list(itertools.product((0,16),(0,1),(0,128),(0,1,2)))
  for handle,flags,nval,status,yielding,ctx in itertools.product((0,0x20002000),(0,1,3,0x7fffffff,0x80000000,0xffffffff),(0,1,0x12345678,0xffffffff),(0,1,0xffffffff),(0,1,0xffffffff),contexts):case('osThreadFlagsSet',(handle,flags),ctx,notified=nval,status=status,yielding=yielding)
  for handle,flags,event,status,yielding,ctx in itertools.product((0,0x20002000),(0,1,0xffffff,0x1000000,0x80000000,0xffffffff),(0,1,0x12345678,0xffffffff),(0,1,0xffffffff),(0,1,0xffffffff),contexts):case('osEventFlagsSet',(handle,flags),ctx,event=event,status=status,yielding=yielding)
  sequences=(((0,0),),((1,0),),((1,1),),((1,3),),((1,1),(1,2),(0,0)),((1,4),(1,8),(0,0)),((1,0x7fffffff),(0,0)))
  for flags,options,timeout,start,step,sequence in itertools.product((0,1,3,0x7fffffff,0x80000000),(0,1,2,3,0xffffffff),(0,1,5,0xffffffff),(0,0xfffffffe),(0,1,6),sequences):case('osThreadFlagsWait',(flags,options,timeout),start=start,step=step,sequence=sequence)
  for ctx,flags in itertools.product(contexts,(0,3,0x80000000)):case('osThreadFlagsWait',(flags,1,1),ctx,sequence=((1,1),(1,2),(0,0)))
  for ctx,ticks in itertools.product(contexts,(0,1,100,0x80000000,0xffffffff)):case('osDelay',(ticks,),ctx)
 vp.write_text(json.dumps(dict(application_sha256=sha(app),report_sha256=sha(rp),driver_sha256=sha(Path(__file__)),comparisons=comparisons,comparisons_by_function=counts,scope='Actual unchanged CMSIS flag/delay wrappers,31/24-bit validation, task/ISR/mask predicates, notify set/query sequencing, any/all/no-clear wait accumulation and tick wrap/timeout, deferred event return/yield and zero delay',limitations=['Notification/event/delay/scheduler/tick calls are explicit fixtures. Task fields, real waits/deferred timer callbacks and physical interrupt/scheduling behavior are not established. No canonical graph/frontier or instruction identity proof.']),indent=2)+'\n');print(comparisons,'notification wrapper comparisons;',counts)
if __name__=='__main__':main()
