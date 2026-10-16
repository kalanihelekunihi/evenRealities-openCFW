#!/usr/bin/env python3
"""Native startup bodies and static callbacks; bounded constructors/port fixtures."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_INVALID
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
FIELDS={'xIdleTaskHandle':(0x20007848,4),'xTimerQueue':(0x2000785c,4),'xTimerTaskHandle':(0x20007860,4),'pxCurrentTimerList':(0x20007868,4),'pxOverflowTimerList':(0x2000786c,4),'xActiveTimerList1':(0x2002b4a8,20),'xActiveTimerList2':(0x2002b4bc,20),'prvCheckForValidListAndQueue.xStaticTimerQueue':(0x2002b258,80),'prvCheckForValidListAndQueue.ucStaticTimerQueueStorage':(0x2002b2a8,512)}
SECTIONS={'.bss.'+n:a for n,(a,z) in FIELDS.items()};SECTIONS.update({'.r1.idle_task_memory':0x2002b4d0,'.r1.timer_task_memory':0x2002b940})
ENTRIES={'vTaskStartScheduler':0x964c8,'xTimerCreateTimerTask':0x98ca8,'r1_native_timer_infrastructure':0x84e58,'vApplicationGetIdleTaskMemory':0x95bb8,'vApplicationGetTimerTaskMemory':0x95bd0}
BACKENDS={'r1_native_task_create_static':0x98418,'xQueueGenericCreateStatic':0x97b62,'vListInitialise':0x95c90,'vPortEnterCritical':0x95cf4,'vPortExitCritical':0x95d24,'xPortStartScheduler':0x979dc}
def main():
 out=BASE/'rtos-scheduler-start';receipt=out/'verification.json';receipt.unlink(missing_ok=True);rp=out/'report.json';r=json.loads(rp.read_text());obj=out/'scheduler-start.o';assert sha(obj)==r['selected_object_sha256']
 for p,d in r['inputs'].items():assert sha(ROOT/p)==d,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';states={};comparisons=0;faults=0;counts={n:0 for n in ENTRIES}
 with tempfile.TemporaryDirectory() as directory:
  t=Path(directory);ld=t/'layout.ld';elf=t/'test.elf';binary=t/'text.bin';ld.write_text('SECTIONS { '+''.join(n+' '+hex(a)+' (NOLOAD) : { *('+n+') } ' for n,a in SECTIONS.items())+'.text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } /DISCARD/ : { *(.comment) *(.note*) } }');bindings={n:0x100ef01+i*16 for i,n in enumerate(BACKENDS)};bindings.update(r1_native_idle_task=0x100ee01,r1_native_timer_task=0x100ee11,uxTopUsedPriority=0x2000784c,xNextTaskUnblockTime=0x20007844);subprocess.run(['arm-none-eabi-ld','-T',str(ld),*['--defsym='+n+'='+hex(a) for n,a in bindings.items()],str(obj),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True);syms={x.split()[-1]:int(x.split()[0],16) for x in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x.split())==3}
  stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
  for u in (stock,candidate):u.mem_map(0x20000,0xc0000);u.mem_map(0x1000000,0x10000);u.mem_map(0x20000000,0x40000)
  stock.mem_write(0x27000,app.read_bytes());candidate.mem_write(0x1000000,binary.read_bytes());kinds={a:n for n,a in BACKENDS.items()};kinds.update({a&~1:n for n,a in bindings.items() if n in BACKENDS})
  def put(u,a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
  def word(u,a):return struct.unpack('<I',bytes(u.mem_read(a,4)))[0]
  def hook(u,a,size,user):
   if a not in kinds:return
   f=states[id(u)];name=kinds[a];args=[u.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)];value=0xdeadbeef;trace=(name,)
   if name=='r1_native_task_create_static':
    expected=0x84fe9 if u is stock else bindings['r1_native_idle_task'];idle=args[0]==expected;assert args[0]==(0x84fe9 if idle else 0x85511) if u is stock else args[0]==bindings['r1_native_idle_task' if idle else 'r1_native_timer_task'];name_data=bytes(u.mem_read(args[1],8 if not idle else 5));extra=struct.unpack('<3I',bytes(u.mem_read(u.reg_read(UC_ARM_REG_SP),12)));trace=(name,'idle' if idle else 'timer',name_data,args[2],args[3],*extra);value=f['idle_result'] if idle else f['timer_result']
   elif name=='xQueueGenericCreateStatic':trace=(name,*args,word(u,u.reg_read(UC_ARM_REG_SP)));value=f['queue_result']
   elif name=='vListInitialise':trace=(name,args[0]);u.mem_write(args[0],struct.pack('<5I',0,args[0]+8,0xffffffff,args[0]+8,args[0]+8))
   elif name=='xPortStartScheduler':trace=(name,word(u,0x20007828),word(u,0x20007830),word(u,0x20007844),u.reg_read(UC_ARM_REG_BASEPRI));value=f['port_result']
   f['trace'].append(trace);u.reg_write(UC_ARM_REG_R0,value&0xffffffff);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  def invalid(u,access,address,size,value,user):states[id(u)]['fault']=(access,address,value);return False
  for u in (stock,candidate):u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_INVALID,invalid)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  def case(name,args=(),queue=0,idle_result=0x2002b4d0,timer_result=0x2002b940,queue_result=0x2002b258,port_result=0,pattern=0):
   nonlocal comparisons,faults
   results=[]
   for u in (stock,candidate):
    f={'trace':[],'fault':None,'idle_result':idle_result,'timer_result':timer_result,'queue_result':queue_result,'port_result':port_result};states[id(u)]=f;u.mem_write(0x2000781c,bytes([0x93])*84);u.mem_write(0x2002b258,bytes([pattern])*3416);u.mem_write(0x20003000,bytes([0xa5])*256);put(u,0x2000785c,queue);put(u,0x2000784c,55);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101);u.reg_write(UC_ARM_REG_BASEPRI,0);u.reg_write(UC_ARM_REG_PRIMASK,0)
    for reg,value in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2),args):u.reg_write(reg,value)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    try:u.emu_start((ENTRIES[name] if u is stock else syms[name])|1,0x20000100,count=100000)
    except UcError:assert f['fault'],(name,u is stock,hex(u.reg_read(UC_ARM_REG_PC)))
    if not f['fault']:assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
    results.append((f['fault'],u.reg_read(UC_ARM_REG_R0) if name=='xTimerCreateTimerTask' and not f['fault'] else None,f['trace'],bytes(u.mem_read(0x2000781c,84)),bytes(u.mem_read(0x2002b258,3416)),bytes(u.mem_read(0x20003000,256)),u.reg_read(UC_ARM_REG_BASEPRI),u.reg_read(UC_ARM_REG_PRIMASK)))
   assert results[0]==results[1],(name,args,queue,idle_result,timer_result,queue_result,[x[:3] for x in results]);comparisons+=1;faults+=bool(results[0][0]);counts[name]+=1
  for name,layout,pattern in itertools.product(('vApplicationGetIdleTaskMemory','vApplicationGetTimerTaskMemory'),((0x20003004,0x20003014,0x20003024),(0x20003004,)*3,(0x20003004,0x20003004,0x20003024),(0,0x20003014,0x20003024),(0x20003004,0,0x20003024),(0x20003004,0x20003014,0)),(0,0xa5)):case(name,layout,pattern=pattern)
  for name,queue,idle_result,timer_result,queue_result,port_result,pattern in itertools.product(('vTaskStartScheduler','xTimerCreateTimerTask','r1_native_timer_infrastructure'),(0,0x20003080),(0,0x2002b4d0),(0,0x2002b940),(0,0x2002b258),(0,1,0xffffffff),(0,0xa5)):case(name,queue=queue,idle_result=idle_result,timer_result=timer_result,queue_result=queue_result,port_result=port_result,pattern=pattern)
 receipt.write_text(json.dumps(dict(application_sha256=sha(app),report_sha256=sha(rp),driver_sha256=sha(Path(__file__)),comparisons=comparisons,fault_comparisons=faults,comparisons_by_function=counts,scope='Actual pinned scheduler/timer startup and infrastructure plus112-byte static memory callbacks; ordered constructor/callback/list/queue/port traces, static extents, state and failure paths',limitations=['Task/queue constructors, list initialization, critical entry/exit and port start use explicit fixtures. Timer task code pointer remains an unexecuted provider. No scheduler/context transfer or physical boot proof.']),indent=2)+'\n');print(comparisons,'startup comparisons;',faults,'faults;',counts)
if __name__=='__main__':main()
