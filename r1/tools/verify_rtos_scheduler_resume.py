#!/usr/bin/env python3
"""Pinned scheduler suspend/resume against native, including real pending lists."""
import hashlib,itertools,json,struct,subprocess,tempfile,sys
from pathlib import Path
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_INVALID
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
FIELDS={'pxCurrentTCB':(0x2000781c,4),'uxCurrentNumberOfTasks':(0x20007824,4),'uxTopReadyPriority':(0x2000782c,4),'xPendedTicks':(0x20007834,4),'xYieldPending':(0x20007838,4),'xNextTaskUnblockTime':(0x20007844,4),'uxSchedulerSuspended':(0x20007850,4),'pxDelayedTaskList':(0x20007854,4),'pxReadyTasksLists':(0x2002ad94,1120),'xPendingReadyList':(0x2002b21c,20)}
ENTRIES={'vTaskSuspendAll':0x9659c,'xTaskResumeAll':0x98b24,'prvResetNextTaskUnblockTime':0x85468};BACKENDS={'vPortEnterCritical':0x95cf4,'vPortExitCritical':0x95d24,'xTaskIncrementTick':0x987e0}
def main():
 real_tick='--real-tick' in sys.argv
 out=BASE/'rtos-scheduler-resume';receipt=out/('tick-integration-verification.json' if real_tick else 'verification.json');receipt.unlink(missing_ok=True);rp=out/'report.json';r=json.loads(rp.read_text());obj=out/'scheduler.o';assert sha(obj)==r['selected_object_sha256']
 for p,d in r['inputs'].items():assert sha(ROOT/p)==d,p
 backends={n:a for n,a in BACKENDS.items() if not real_tick or n!='xTaskIncrementTick'};extra=[];fields=dict(FIELDS)
 if real_tick:
  tick_report=BASE/'rtos-scheduler-tick/report.json';tr=json.loads(tick_report.read_text());tick_object=tick_report.parent/'scheduler-tick.o';assert sha(tick_object)==tr['selected_object_sha256'];extra=[str(tick_object)];fields.update({'xNumOfOverflows':(0x2000783c,4),'pxOverflowDelayedTaskList':(0x20007858,4),'xDelayedTaskList1':(0x2002b1f4,20),'xDelayedTaskList2':(0x2002b208,20)})
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';states={};comparisons=0;faults=0;ticks=0
 with tempfile.TemporaryDirectory() as directory:
  t=Path(directory);ld=t/'layout.ld';elf=t/'test.elf';binary=t/'text.bin';ld.write_text('SECTIONS { .text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } '+''.join('.bss.'+n+' '+hex(a)+' (NOLOAD) : { *(.bss.'+n+') } ' for n,(a,z) in fields.items() if n not in ('uxSchedulerSuspended','pxCurrentTCB'))+'/DISCARD/ : { *(.comment) *(.note*) } }');bindings={n:0x100ef01+i*16 for i,n in enumerate(backends)};subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--defsym=uxSchedulerSuspended=0x20007850','--defsym=pxCurrentTCB=0x2000781c',*['--defsym='+n+'='+hex(a) for n,a in bindings.items()],str(obj),*extra,'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True);syms={x.split()[-1]:int(x.split()[0],16) for x in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x.split())==3}
  for n,(a,z) in fields.items():assert syms[n]==a
  stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
  for u in (stock,candidate):u.mem_map(0x20000,0xc0000);u.mem_map(0x1000000,0x10000);u.mem_map(0x20000000,0x40000);u.mem_map(0xe000e000,0x1000)
  stock.mem_write(0x27000,app.read_bytes());candidate.mem_write(0x1000000,binary.read_bytes());kinds={a:n for n,a in backends.items()};kinds.update({a&~1:n for n,a in bindings.items()})
  def hook(u,a,size,user):
   nonlocal ticks
   if real_tick and a in (0x987e0,syms['xTaskIncrementTick']&~1):
    states[id(u)]['trace'].append('xTaskIncrementTick');states[id(u)]['ticks']+=1;ticks+=1;return
   if a not in kinds:return
   f=states[id(u)];name=kinds[a];f['trace'].append(name);value=0xdeadbeef
   if name=='xTaskIncrementTick':value=(f['pattern']>>(f['ticks']%8))&1;f['ticks']+=1;ticks+=1
   u.reg_write(UC_ARM_REG_R0,value);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  def fault(u,access,address,size,value,user):
   if address==0xffffffff and value==0:states[id(u)]['fault']=True
   return False
  for u in (stock,candidate):u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_INVALID,fault)
  def put(u,a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
  def word(u,a):return struct.unpack('<I',bytes(u.mem_read(a,4)))[0]
  def init_list(u,a):u.mem_write(a,struct.pack('<5I',0,a+8,0xffffffff,a+8,a+8))
  def append(u,a,item,owner,value):
   sentinel=a+8;previous=word(u,sentinel+8);u.mem_write(item,struct.pack('<5I',value,sentinel,previous,owner,a));put(u,previous+4,item);put(u,sentinel+8,item);put(u,a,word(u,a)+1)
  def reset(suspended,number,priorities,current,yielding,pended,index_mode):
   for u in (stock,candidate):
    u.mem_write(0x20001000,bytes([0xa5])*8192);u.mem_write(0x2000781c,bytes(64));u.mem_write(0x2002ad94,bytes(1180));u.mem_write(0xe000ed04,bytes(4));put(u,0x2000781c,0x20001000);put(u,0x2000102c,current)
    for name,value in [('uxSchedulerSuspended',suspended),('uxCurrentNumberOfTasks',number),('uxTopReadyPriority',0),('xYieldPending',yielding),('xPendedTicks',pended),('xNextTaskUnblockTime',0xdeadbeef),('pxDelayedTaskList',0x2002b1f4)]:put(u,FIELDS[name][0],value)
    for i in range(56):init_list(u,0x2002ad94+i*20)
    init_list(u,0x2002b21c);init_list(u,0x2002b1f4)
    for i,priority in enumerate(priorities):
     task=0x20002000+i*128;put(u,task+44,priority);append(u,0x2002b21c,task+24,task,0x11110000+i);append(u,0x2002b1f4,task+4,task,500+i)
    # An optional remaining delayed task exercises the non-empty next-unblock path.
    if index_mode&2:append(u,0x2002b1f4,0x20002804,0x20002800,0x12345678)
    if real_tick:
     put(u,0x20007828,499);put(u,0x20007858,0x2002b208);init_list(u,0x2002b208);task=0x20002880;put(u,task+44,min(current+1,55));put(u,task+40,0);append(u,0x2002b1f4,task+4,task,501)
    if index_mode&1 and priorities:
     put(u,0x2002b21c+4,0x20002018);put(u,0x2002b1f4+4,0x20002004)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  def call(name,pattern=0):
   nonlocal comparisons,faults
   results=[]
   for u in (stock,candidate):
    f={'trace':[],'fault':False,'pattern':pattern,'ticks':0};states[id(u)]=f;u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101);u.reg_write(UC_ARM_REG_BASEPRI,0)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    try:u.emu_start((ENTRIES[name] if u is stock else syms[name])|1,0x20000100,count=1000000)
    except UcError:assert f['fault'],(name,u is stock,hex(u.reg_read(UC_ARM_REG_PC)))
    if not f['fault']:assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
    results.append((f['fault'],u.reg_read(UC_ARM_REG_R0) if name=='xTaskResumeAll' and not f['fault'] else None,f['trace'],bytes(u.mem_read(0x20001000,8192)),bytes(u.mem_read(0x2000781c,64)),bytes(u.mem_read(0x2002ad94,1180)),bytes(u.mem_read(0xe000ed04,4)),u.reg_read(UC_ARM_REG_BASEPRI)))
   assert results[0]==results[1],(name,pattern,[x[:3] for x in results],[(k,[(i,a,b) for i,(a,b) in enumerate(zip(results[0][k],results[1][k])) if a!=b][:12]) for k in range(3,7)]);comparisons+=1;faults+=results[0][0]
  for value in (0,1,2,0x7fffffff,0xfffffffe,0xffffffff):reset(value,0,(),0,0,0,0);call('vTaskSuspendAll')
  for suspended,number,priorities,current,yielding,pended,pattern,index_mode in itertools.product((0,1,2,0xffffffff),(0,1),((),(0,),(1,),(55,),(0,55),(55,0),(15,1,55)),(0,1,15,55),(0,1,0xffffffff),(0,1,2,7),((0,) if real_tick else (0,1,0xaa)),range(4)):
   reset(suspended,number,priorities,current,yielding,pended,index_mode);call('xTaskResumeAll',pattern)
  for priorities,index_mode in itertools.product(((),(0,),(1,55)),range(4)):reset(1,1,priorities,0,0,0,index_mode);call('prvResetNextTaskUnblockTime')
 result=dict(application_sha256=sha(app),report_sha256=sha(rp),driver_sha256=sha(Path(__file__)),comparisons=comparisons,assertion_comparisons=faults,tick_calls_per_implementation=ticks//2,scope='Unchanged pinned suspend/resume/reset-unblock bodies, actual inline pending/state/ready-list transfers,48-byte TCB prefix,priority/yield/pended tick decisions, nested suspend/overflow and assertion path',limitations=['Critical entry/exit and xTaskIncrementTick are bounded fixtures. Full TCB size/allocation, actual tick side effects, scheduler startup/context switching, physical interrupts and whole-image identity remain gates.'])
 if real_tick:
  result.update(tick_report_sha256=sha(tick_report),tick_object_sha256=sha(tick_object),actual_tick_executed=True,scope='Actual pinned suspend/resume, pending-ready transfers and tick replay with a real delayed timeout; full TCB/state/list comparisons',limitations=['Critical entry/exit remain bounded fixtures. Full TCB allocation, scheduler startup/context switching, physical concurrency and whole-image equality remain gates.'])
 receipt.write_text(json.dumps(result,indent=2)+'\n');print(comparisons,'scheduler comparisons;',faults,'assertions;',ticks//2,'tick calls; actual tick:',real_tick)
if __name__=='__main__':main()
