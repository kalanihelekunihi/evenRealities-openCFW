#!/usr/bin/env python3
"""Actual initializer, heap, CMSIS lifecycle, product callback and queue-worker graph."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
from build_source_candidates import undefined_symbols
from verify_rtos_scheduler_tick import FIELDS
from verify_rtos_scheduler_start import SECTIONS
from verify_native_delayed_schedule import A
from verify_native_delayed_initialize import RAM
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-delayed-reschedule';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ENTRIES={'r1_native_delayed_cancel':0x65d64,'r1_native_delayed_initialize':0x65740,'r1_native_delayed_worker':0x65ea8,'vTaskStartScheduler':0x964c8,'xQueueGenericCreateStatic':0x97b62,'xQueueCreateMutexStatic':0x97af4,'xTimerCreateStatic':0x98c7c,'r1_native_delayed_schedule':0x65b4c,'r1_timer_runtime_ProcessReceivedCommands':0x852e0,'r1_timer_runtime_ProcessExpiredTimer':0x852a0,'osMessageQueueGet':0x7d310}
TARGETS={'r1_native_delayed_cancel':0x65d64,'r1_native_delayed_initialize':0x65740,'osMessageQueueNew':0x7d3b4,'osMutexNew':0x7d4d6,'osThreadNew':0x7d818,'osThreadTerminate':0x7d8d6,'osTimerNew':0x7d90c,'pvPortMalloc':0x855a0,'pvTimerGetTimerID':0x8569c,'TimerCallback':0x34088,'r1_native_delayed_worker':0x65ea8,'osMessageQueueGet':0x7d310,'r1_native_delayed_schedule':0x65b4c,'r1_native_delayed_reschedule':0x65f84,'r1_native_delayed_push':0x659e8,'osMutexAcquire':0x7d488,'osMutexRelease':0x7d536,'osTimerStop':0x7d9ea,'osTimerStart':0x7d9b0,'xTimerIsTimerActive':0x98d68,'xTimerGenericCommand':0x98d04,'osMessageQueuePut':0x7d40c,'xQueueGenericSend':0x97c50,'xQueueReceive':0x97f50,'vPortEnterCritical':0x95cf4,'vPortExitCritical':0x95d24}
def main():
 vp=OUT/'initialization-graph-verification.json';vp.unlink(missing_ok=True);sp=OUT/'stage-verification.json';stage=json.loads(sp.read_text());obj=OUT/'delayed-stage.o';assert sha(obj)==stage['selected_object_sha256']
 assert sha(BASE/'board/report.json')==stage['board_report_sha256'] and sha(ROOT/'r1/tools/check_native_delayed_stage.py')==stage['driver_sha256']
 for group in ('provider_reports','provider_receipts'):
  for p,h in stage[group].items():assert sha(BASE/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 sections={**SECTIONS,**{'.bss.'+n:a for n,(a,z) in FIELDS.items()},'.bss.ucMaxSysCallPriority':0x20007810,'.bss.uxCriticalNesting':0x20007814,'.bss.ulMaxPRIGROUPValue':0x20007818,'.bss.xSchedulerRunning':0x20007830,'.bss.xSuspendedTaskList':0x2002b244,'.bss.uxTaskNumber':0x20007840,'.bss.uxDeletedTasksWaitingCleanUp':0x20007820,'.bss.xTasksWaitingTermination':0x2002b230,'.bss.prvSampleTimeNow.xLastTime':0x20007864,'.r1.heap.state':0x200077fc,'.r1.heap.storage':0x2001e588,'.r1.heap.start':0x2002ad88}
 sections.update({'.r1.delayed.'+n:a for n,(a,z) in RAM.items()})
 remaining=set(undefined_symbols(obj)[0]);bindings={n:0x1100001+i*16 for i,n in enumerate(sorted(remaining))};counts={'native':{},'source':{}};states={};comparisons=0;workflows=0
 with tempfile.TemporaryDirectory() as directory:
  t=Path(directory);ld=t/'layout.ld';elf=t/'graph.elf';binary=t/'text.bin'
  ld.write_text('SECTIONS { '+''.join(n+' '+hex(a)+' (NOLOAD) : { *('+n+') } ' for n,a in sections.items())+'.r1.task.initial_xpsr 0x9c4cc : { *(.r1.task.initial_xpsr) } .r1.scheduler.top_used_priority 0x2000784c : { *(.data.uxTopUsedPriority) *(.rodata.uxTopUsedPriority) } .text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } .bss 0x2003e000 (NOLOAD) : { *(.bss*) *(COMMON) } .unused_data 0x21000000 : { *(.r1.*) *(.wdt.*) *(.nrf*) *(.sdh*) *(.data*) } /DISCARD/ : { *(.comment) *(.note*) } }')
  roots=[*ENTRIES,*TARGETS,'r1_native_initial_xpsr','uxTopUsedPriority']
  subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--gc-sections',*['--undefined='+n for n in roots],*['--defsym='+n+'='+hex(a) for n,a in bindings.items()],str(obj),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True);syms={v[2]:int(v[0],16) for l in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=l.split())==3};image=binary.read_bytes();assert len(image)<0x40000
  function_sizes={v[3]:int(v[1],16) for l in subprocess.check_output(['arm-none-eabi-nm','-S','--defined-only',str(elf)],text=True).splitlines() if len(v:=l.split())==4}
  stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);source=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
  for u in (stock,source):u.mem_map(0x20000,0xc0000);u.mem_map(0x1000000,0x40000);u.mem_map(0x1100000,0x1000);u.mem_map(0x1200000,0x1000);u.mem_map(0x20000000,0x40000);u.mem_map(0xe000e000,4096)
  stock.mem_write(0x27000,app.read_bytes());source.mem_write(0x1000000,image)
  def word(u,a):return struct.unpack('<I',bytes(u.mem_read(a,4)))[0]
  def put(u,a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
  def hook(u,a,size,_):
   f=states[id(u)]
   if u is source:assert not 0x20000<=a<0xe0000 and not 0x1100000<=a<0x1101000,('unexpected source provider',hex(a))
   if f['phase']=='startup' and a==((0x979dc if u is stock else syms['xPortStartScheduler'])&~1):f['stopped']=True;u.emu_stop();return
   if a==0x1200000:
    assert f.get('worker') and u.reg_read(UC_ARM_REG_R0)==0x89abcdef
    f['callbacks'].append(u.reg_read(UC_ARM_REG_R0));u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR));return
   if f['phase']=='runtime':
    c=counts['native' if u is stock else 'source']
    for n,native in TARGETS.items():
     if a==((native if u is stock else syms[n])&~1):c[n]=c.get(n,0)+1
    if f.get('worker') and a==((0x7d310 if u is stock else syms['osMessageQueueGet'])&~1) and word(u,0x20014350+56)==0:
     f['worker_boundary']=True;u.emu_stop();return
  for u in (stock,source):states[id(u)]={'phase':'cold'};u.hook_add(UC_HOOK_CODE,hook)
  stock.reg_write(UC_ARM_REG_SP,0x2003f000);stock.emu_start(0x283a1,0x27208,count=2000000);assert stock.reg_read(UC_ARM_REG_PC)==0x27208
  # Shared authenticated cold RAM is a controlled fixture, not source init proof.
  cold=bytes(stock.mem_read(0x20000000,0x40000));source.mem_write(0x9c4cc,struct.pack('<I',0x01000000));source.mem_write(0x2000784c,struct.pack('<I',55))
  def run(u,name,args=()):
   u.reg_write(UC_ARM_REG_SP,0x2003c000);u.reg_write(UC_ARM_REG_LR,0x20000101)
   for reg,value in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),args):u.reg_write(reg,value)
   u.mem_write(0x2003c000,struct.pack('<3I',*(list(args[4:])+[0,0,0])[:3]))
   try:u.emu_start(((ENTRIES[name] if u is stock else syms[name])|1),0x20000100,count=2000000)
   except UcError as e:raise AssertionError((name,u is stock,hex(u.reg_read(UC_ARM_REG_PC)))) from e
   if states[id(u)]['phase']=='startup':assert states[id(u)]['stopped']
   elif states[id(u)].get('worker'):assert states[id(u)]['worker_boundary']
   else:assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003c000
   return u.reg_read(UC_ARM_REG_R0)
  def snapshot(u):
   timer=bytearray(u.mem_read(0x200150d8,44));callback=word(u,0x200150f8)
   assert callback==(0x34089 if u is stock else syms['TimerCallback']|1)
   struct.pack_into('<I',timer,32,0x34089)
   name=word(u,0x200150d8);assert bytes(u.mem_read(name,18)).split(b'\0')[0]==b'fw_evt_loop_mutex'
   struct.pack_into('<I',timer,0,0xbf5b0)
   tagged=word(u,0x200150f4);assert tagged&1 and (tagged&~1)==0x2001e598
   metadata=tagged&~1;assert word(u,metadata)==(0x65f85 if u is stock else syms['r1_native_delayed_reschedule']|1) and word(u,metadata+4)==0
   heap=bytearray(u.mem_read(0x2001e588,51200));lr=word(u,0x2001e590)
   if u is stock:assert lr==0x7d93b
   else:
    assert syms['osTimerNew']<=(lr&~1)<syms['osTimerNew']+function_sizes['osTimerNew']
    # Validate the recorded return site's BL target before normalizing it.
    insn=bytes(u.mem_read((lr&~1)-4,4));h1,h2=struct.unpack('<2H',insn)
    assert h1&0xf800==0xf000 and h2&0xd000==0xd000
    sign=(h1>>10)&1;j1=(h2>>13)&1;j2=(h2>>11)&1
    offset=(sign<<24)|((1^(j1^sign))<<23)|((1^(j2^sign))<<22)|((h1&0x3ff)<<12)|((h2&0x7ff)<<1)
    if offset&(1<<24):offset-=1<<25
    assert ((lr&~1)+offset)==(syms['pvPortMalloc']&~1)
    struct.pack_into('<I',heap,8,0x7d93b)
   struct.pack_into('<I',heap,metadata-0x2001e588,0x65f85)
   stack=bytearray(u.mem_read(0x20014488,3072));sp=word(u,0x20014418)
   assert 0x20014488<=sp and sp+68<=0x20015088
   assert word(u,sp+56)==(0x854e1 if u is stock else syms['prvTaskExitError']|1)
   assert word(u,sp+60)==(0x65ea9 if u is stock else syms['r1_native_delayed_worker']|1)
   struct.pack_into('<I',stack,sp+56-0x20014488,0x854e1)
   struct.pack_into('<I',stack,sp+60-0x20014488,0x65ea9)
   daemon=bytearray(u.mem_read(0x2002b258,592))
   for off in range(92,592,16):daemon[off:off+4]=bytes(4)
   return bytes(u.mem_read(A['r1_delayed_context'],24)),bytes(u.mem_read(A['r1_delayed_callbacks'],768)),bytes(u.mem_read(0x20014350,200)),bytes(u.mem_read(0x20014418,112)),bytes(stack),bytes(u.mem_read(0x20015088,80)),bytes(timer),bytes(heap),bytes(u.mem_read(0x200077fc,20)),bytes(daemon),bytes(u.mem_read(0x2002b4a8,40)),bytes(u.mem_read(0x20007810,96)),bytes(u.mem_read(0x2002ad94,1220)),u.reg_read(UC_ARM_REG_BASEPRI),u.reg_read(UC_ARM_REG_PRIMASK),tuple(states[id(u)].get('callbacks',[]))
  def compare():
   nonlocal comparisons
   a=snapshot(stock);b=snapshot(source);assert a==b,[(i,[(j,x,y) for j,(x,y) in enumerate(zip(av,bv)) if x!=y][:16] if isinstance(av,bytes) else (av,bv)) for i,(av,bv) in enumerate(zip(a,b)) if av!=bv];comparisons+=1
  for delay,second,now,repeat_init in itertools.product((2,3,3072),(False,True),(0,1024),(False,True)):
   for u in (stock,source):
    u.mem_write(0x20000000,cold);u.mem_write(0xe000e000,bytes(4096));u.reg_write(UC_ARM_REG_IPSR,0);u.reg_write(UC_ARM_REG_BASEPRI,0);u.reg_write(UC_ARM_REG_PRIMASK,0);states[id(u)]={'phase':'startup','stopped':False,'callbacks':[]};run(u,'vTaskStartScheduler');states[id(u)]['phase']='runtime';put(u,0x20007814,0);u.reg_write(UC_ARM_REG_BASEPRI,0)
    for n,(address,size) in RAM.items():u.mem_write(address,bytes(size))
    put(u,0x20007828,now)
    run(u,'r1_native_delayed_initialize')
    if repeat_init:run(u,'r1_native_delayed_initialize')
    assert tuple(word(u,0x20006718+i*4) for i in range(4))==(0x20014350,0x20014418,0x20015088,0x200150d8)
    run(u,'r1_native_delayed_schedule',(0x1200001,0x89abcdef,delay));run(u,'r1_timer_runtime_ProcessReceivedCommands')
   compare()
   if second:
    for u in (stock,source):
     run(u,'r1_native_delayed_schedule',(0x23456789,0xabcdef01,delay+1));run(u,'r1_timer_runtime_ProcessReceivedCommands')
     assert run(u,'r1_native_delayed_cancel',(0x23456789,0))==1
     run(u,'r1_timer_runtime_ProcessReceivedCommands')
     assert word(u,A['r1_delayed_callbacks']+4)==0
    compare()
   for u in (stock,source):
    expiry=word(u,0x200150dc);put(u,0x20007828,expiry);run(u,'r1_timer_runtime_ProcessExpiredTimer',(expiry,expiry));run(u,'r1_timer_runtime_ProcessReceivedCommands')
    states[id(u)]['worker']=True;states[id(u)]['worker_boundary']=False
    run(u,'r1_native_delayed_worker',(0,));states[id(u)]['worker']=False
    assert states[id(u)]['callbacks']==[0x89abcdef]
   compare();workflows+=1
 assert counts['native']==counts['source'] and all(counts['source'].get(n,0)>0 for n in TARGETS),counts
 vp.write_text(json.dumps(dict(stage_sha256=sha(sp),driver_sha256=sha(Path(__file__)),input_helpers={n:sha(ROOT/'r1/tools'/n) for n in ('verify_rtos_scheduler_tick.py','verify_rtos_scheduler_start.py','verify_native_delayed_schedule.py','build_source_candidates.py','verify_native_delayed_initialize.py')},application_sha256=sha(app),comparisons=comparisons,workflows=workflows,worker_dispatches_per_implementation=workflows,provider_counts=counts,provider_interception=False,source_text_bytes=len(image),actual_product_initializer=True,actual_heap=True,reinitialized_workflows=12,cancellation_workflows=12,canonical_board_integrated=stage['canonical_board_integrated'],instruction_identity=False,limitations=['Shared authenticated cold RAM and scheduler startup are fixtures; actual product initialization and lifecycle bodies execute','Startup stops at actual port-start boundary; no physical scheduling or blocked-task resumption','Timer name/callback, heap callback metadata, exact allocator BL return, initial task PC/LR normalized after checks; only4 padding bytes per daemon command excluded','Source graph forbids stock instruction execution and unresolved-call guards','Worker stops at its next empty-queue receive boundary, before actual blocking; dispatched user callback is a controlled fixture']),indent=2)+'\n');print('Actual initializer source graph:',comparisons,'comparisons;',workflows,'workflows; actual timer/queue/mutex/critical providers')
if __name__=='__main__':main()
