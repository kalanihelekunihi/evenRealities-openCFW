#!/usr/bin/env python3
"""Pinned timer helpers/task loop versus native; actual C list primitives."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_INVALID
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ENTRIES={'InsertTimerInActiveList':0x851f4,'ReloadTimer':0x85440,'ProcessExpiredTimer':0x852a0,'SampleTimeNow':0x85484,'ProcessTimerOrBlockTask':0x853d4,'ProcessReceivedCommands':0x852e0,'task':0x85510}
BACKENDS={'xTaskGetTickCount':0x987c4,'vTaskSuspendAll':0x9659c,'xTaskResumeAll':0x98b24,'vQueueWaitForMessageRestricted':0x95f8e,'xQueueReceive':0x97f50,'vPortFree':0x95d48}
FIELDS={'xTimerQueue':0x2000785c,'pxCurrentTimerList':0x20007868,'pxOverflowTimerList':0x2000786c}
def main():
 out=BASE/'rtos-timer-runtime';receipt=out/'verification.json';receipt.unlink(missing_ok=True);rp=out/'report.json';r=json.loads(rp.read_text());obj=out/'timer-runtime.o';assert sha(obj)==r['selected_object_sha256']
 for p,d in r['inputs'].items():assert sha(ROOT/p)==d,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';states={};comparisons=0;faults=0;counts={n:0 for n in ENTRIES};callback_calls=0
 with tempfile.TemporaryDirectory() as directory:
  t=Path(directory);ld=t/'layout.ld';elf=t/'test.elf';binary=t/'text.bin';lists=t/'lists.o';lo=BASE/'rtos-task-wait/list.o';lr=json.loads((BASE/'rtos-task-wait/report.json').read_text());assert sha(lo)==lr['list_unit']['object_sha256'];subprocess.run(['arm-none-eabi-ld','-r','--gc-sections','--undefined=vListInsert','--undefined=uxListRemove',str(lo),'-o',str(lists)],check=True)
  ld.write_text('SECTIONS { .bss.prvSampleTimeNow.xLastTime 0x20007864 (NOLOAD) : { *(.bss.prvSampleTimeNow.xLastTime) } .text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } /DISCARD/ : { *(.comment) *(.note*) } }');bindings={n:0x100ee01+i*16 for i,n in enumerate(BACKENDS)};subprocess.run(['arm-none-eabi-ld','-T',str(ld),*['--defsym='+n+'='+hex(a) for n,a in {**FIELDS,**bindings}.items()],str(obj),str(lists),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True);syms={x.split()[-1]:int(x.split()[0],16) for x in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x.split())==3};assert syms['prvSampleTimeNow.xLastTime']==0x20007864
  stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
  for u in (stock,candidate):u.mem_map(0x20000,0xc0000);u.mem_map(0x1000000,0x10000);u.mem_map(0x20000000,0x40000);u.mem_map(0xe000e000,0x1000)
  stock.mem_write(0x27000,app.read_bytes());candidate.mem_write(0x1000000,binary.read_bytes());kinds={a:n for n,a in BACKENDS.items()};kinds.update({a&~1:n for n,a in bindings.items()})
  def put(u,a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
  def word(u,a):return struct.unpack('<I',bytes(u.mem_read(a,4)))[0]
  def hook(u,a,size,user):
   nonlocal callback_calls
   f=states[id(u)]
   if f['name']=='task' and a==(0x85512 if u is stock else syms['prvGetNextExpireTime']&~1):
    if f['loops']==3:f['boundary']=True;u.emu_stop();return
    f['loops']+=1
   if a in (0x100f000,0x100f010):
    args=(u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1));f['trace'].append(('timer-callback',args[0],word(u,args[0]+24),u.mem_read(args[0]+40,1)[0],word(u,args[0]+20)) if a==0x100f000 else ('pended-callback',*args));callback_calls+=1;u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR));return
   if a not in kinds:return
   name=kinds[a];args=[u.reg_read(reg) for reg in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2)];value=0
   if name=='xTaskGetTickCount':value=f['now'];trace=('tick',value)
   elif name=='xTaskResumeAll':value=f['resume'];trace=(name,value)
   elif name=='xQueueReceive':
    assert args[0]==0x20002000 and args[2]==0
    if f['messages']:u.mem_write(args[1],struct.pack('<4I',*f['messages'].pop(0)));value=1
    trace=(name,value)
   elif name=='vQueueWaitForMessageRestricted':trace=(name,*args)
   elif name=='vPortFree':trace=(name,args[0])
   else:trace=(name,)
   f['trace'].append(trace);u.reg_write(UC_ARM_REG_R0,value);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  def invalid(u,access,a,size,value,user):states[id(u)]['fault']=(access,a,value);return False
  for u in (stock,candidate):u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_INVALID,invalid)
  def init_list(u,a):u.mem_write(a,struct.pack('<5I',0,a+8,0xffffffff,a+8,a+8))
  def append(u,a,item,owner,expiry):
   prev=word(u,a+16);u.mem_write(item,struct.pack('<5I',expiry&0xffffffff,a+8,prev,owner,a));put(u,prev+4,item);put(u,a+16,item);put(u,a,word(u,a)+1)
  def prepare(name,now=0,last=0,period=1,status=1,onlist=0,expiry=0,other=False,resume=0,messages=()):
   for u in (stock,candidate):
    states[id(u)]={'name':name,'now':now,'trace':[],'resume':resume,'messages':list(messages),'fault':None,'boundary':False,'loops':0};u.mem_write(0x20001000,bytes([0x93])*0x3000);u.mem_write(0x2000785c,struct.pack('<5I',0x20002000,0,last,0x2002b4a8,0x2002b4bc));init_list(u,0x2002b4a8);init_list(u,0x2002b4bc);u.mem_write(0x20001004,bytes(20));put(u,0x20001000,0x20003300);put(u,0x20001018,period);put(u,0x2000101c,0x12345678);put(u,0x20001020,0x100f001);put(u,0x20001024,99);u.mem_write(0x20001028,bytes([status]));put(u,0xe000ed04,0)
    if onlist:append(u,0x2002b4a8 if onlist==1 else 0x2002b4bc,0x20001004,0x20001000,expiry)
    if other:
     u.mem_write(0x20001104,bytes(20));put(u,0x20001118,100);put(u,0x20001120,0x100f001);u.mem_write(0x20001128,b'\x03');append(u,0x2002b4bc,0x20001104,0x20001100,100)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  def call(name,args=()):
   nonlocal comparisons,faults
   results=[]
   for u in (stock,candidate):
    f=states[id(u)];u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101);u.reg_write(UC_ARM_REG_BASEPRI,0);u.reg_write(UC_ARM_REG_PRIMASK,0)
    for reg,value in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),args):u.reg_write(reg,value)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    try:u.emu_start((ENTRIES[name] if u is stock else syms['r1_native_timer_task' if name=='task' else 'r1_timer_runtime_'+name])|1,0x20000100,count=1000000)
    except UcError:assert f['fault'],(name,u is stock,hex(u.reg_read(UC_ARM_REG_PC)))
    if name=='task':assert f['boundary'] or f['fault']
    elif not f['fault']:assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
    results.append((f['fault'],f['boundary'],f['trace'],u.reg_read(UC_ARM_REG_R0) if name in ('InsertTimerInActiveList','SampleTimeNow') and not f['fault'] else None,bytes(u.mem_read(0x20001000,0x3000)),bytes(u.mem_read(0x2000785c,20)),bytes(u.mem_read(0x2002b4a8,40)),word(u,0xe000ed04),u.reg_read(UC_ARM_REG_BASEPRI)))
   assert results[0]==results[1],(name,args,[x[:4] for x in results],[(i,len(a)) for i,(a,b) in enumerate(zip(results[0][4:7],results[1][4:7]),4) if a!=b]);comparisons+=1;faults+=bool(results[0][0]);counts[name]+=1
  edge=(0,1,2,100,0xfffffffe,0xffffffff)
  for expiry,now,command,period in itertools.product(edge,edge,edge,(1,2,100)):
   prepare('InsertTimerInActiveList',period=period);call('InsertTimerInActiveList',(0x20001000,expiry,now,command))
  for name,expiry,delta,period,status in itertools.product(('ReloadTimer','ProcessExpiredTimer'),(0,1,99,0xfffffffe,0xffffffff),(0,1,2,3),(1,2,100),(0,1,2,3,4,5,6,7,0x85)):
   now=(expiry+delta)&0xffffffff;prepare(name,period=period,status=status,onlist=1 if name=='ProcessExpiredTimer' else 0,expiry=expiry);call(name,(0x20001000,expiry,now) if name=='ReloadTimer' else (expiry,now))
  for now,last,status,shape in itertools.product(edge,edge,(1,5),(0,1)):
   prepare('SampleTimeNow',now,last,1,status,shape,0xfffffffe,True);call('SampleTimeNow',(0x20003500,))
  for now,empty,shape,other,resume in itertools.product((0,1,100),(0,1,0xffffffff),(0,1),(0,1),(0,1,0xffffffff)):
   if not empty and not shape:continue
   prepare('ProcessTimerOrBlockTask',now,0,100,1,shape,100,other,resume);call('ProcessTimerOrBlockTask',(100 if shape else 0,empty))
  for command,now,delta,period,status,onlist in itertools.product((-3,-2,-1,*range(12),0x7fffffff),(0,1,100,0xfffffffe),(0,1,3),(1,2,100),(0,1,2,4,7,0x85),(0,1,2)):
   msg=(command&0xffffffff,0x100f011,0x12345678,0x87654321) if command<0 else (command,(now-delta)&0xffffffff,0x20001000,0)
   prepare('ProcessReceivedCommands',now,now,period,status,onlist,(now+100)&0xffffffff,messages=(msg,));call('ProcessReceivedCommands')
  for value in (0,1,0xffffffff):prepare('ProcessReceivedCommands',messages=((4,value,0x20001000,0),));call('ProcessReceivedCommands')
  for now,shape,status,resume in itertools.product((0,7),(0,1),(1,5),(0,1)):
   prepare('task',now,now,100,status,shape,5,resume=resume);call('task',(0,))
 receipt.write_text(json.dumps(dict(application_sha256=sha(app),report_sha256=sha(rp),driver_sha256=sha(Path(__file__)),comparisons=comparisons,fault_comparisons=faults,comparisons_by_function=counts,timer_callback_fixture_calls_per_implementation=callback_calls//2,list_report_sha256=sha(BASE/'rtos-task-wait/report.json'),list_input_object_sha256=sha(lo),scope='Actual pinned timer helper/task bodies and actual list insert/remove:44-byte timer,16-byte commands, current/overflow placement, expiry/autoreload backlog, rollover, stop/change/delete/pended commands and loop iterations',limitations=['Queue receive/restricted wait, kernel tick/suspend/resume, free and timer/pended callbacks are explicit fixtures. Runtime has no physical time progression or task execution. Native inlined next-expiry and switch-list paths are exercised through owning bodies, not promoted as separate functions.']),indent=2)+'\n');print(comparisons,'timer runtime comparisons;',faults,'faults;',counts)
if __name__=='__main__':main()
