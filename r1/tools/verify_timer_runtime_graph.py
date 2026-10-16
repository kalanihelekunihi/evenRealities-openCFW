#!/usr/bin/env python3
"""Execute staged timer/queue/task/kernel providers against the locked native image."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
from build_source_candidates import undefined_symbols
from verify_rtos_scheduler_tick import FIELDS
from verify_rtos_scheduler_start import SECTIONS
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ENTRIES={'InsertTimerInActiveList':0x851f4,'ProcessExpiredTimer':0x852a0,'ProcessReceivedCommands':0x852e0,'ProcessTimerOrBlockTask':0x853d4,'SampleTimeNow':0x85484}
def main():
 out=BASE/'rtos-timer-runtime';(out/'graph-verification.json').unlink(missing_ok=True);stage=json.loads((out/'stage-verification.json').read_text());obj=out/'timer-stage.o';assert sha(obj)==stage['selected_object_sha256'];app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';states={};comparisons=0;callbacks=0;provider_counts={'native':{},'source':{}}
 for group in ('provider_reports','isolated_receipts'):
  for path,digest in stage[group].items():assert sha(BASE/path)==digest,path
 for path in stage['provider_reports']:
  report=json.loads((BASE/path).read_text())
  for name,digest in report['inputs'].items():assert sha(ROOT/name)==digest,name
 assert sha(BASE/'board/report.json')==stage['board_report_sha256'] and sha(BASE/'board/native-board.o')==stage['board_object_sha256']
 assert sha(ROOT/'r1/tools/check_rtos_timer_stage.py')==stage['driver_sha256']
 sections={**SECTIONS,**{'.bss.'+n:a for n,(a,z) in FIELDS.items()},'.bss.ucMaxSysCallPriority':0x20007810,'.bss.uxCriticalNesting':0x20007814,'.bss.ulMaxPRIGROUPValue':0x20007818,'.bss.xSchedulerRunning':0x20007830,'.bss.xSuspendedTaskList':0x2002b244,'.bss.uxTaskNumber':0x20007840,'.bss.uxDeletedTasksWaitingCleanUp':0x20007820,'.bss.xTasksWaitingTermination':0x2002b230,'.bss.prvSampleTimeNow.xLastTime':0x20007864,'.r1.heap.state':0x200077fc,'.r1.heap.storage':0x2001e588,'.r1.heap.start':0x2002ad88}
 api_report=BASE/'rtos-timer-api/report.json';api=json.loads(api_report.read_text());api_obj=api_report.parent/'timer-api.o';assert sha(api_obj)==api['selected_object_sha256'];api_receipt=api_report.parent/'verification.json';av=json.loads(api_receipt.read_text());assert av['report_sha256']==sha(api_report) and av['driver_sha256']==sha(ROOT/'r1/tools/verify_rtos_timer_api.py')
 for path,digest in api['inputs'].items():assert sha(ROOT/path)==digest,path
 isr_obj=BASE/'rtos-timer-isr-queue/timer-isr-queue.o';priority_obj=BASE/'rtos-interrupt-priority/interrupt-priority.o';extra_reports={}
 for name,objpath in (('rtos-timer-isr-queue',isr_obj),('rtos-interrupt-priority',priority_obj)):
  rp=BASE/name/'report.json';report=json.loads(rp.read_text());assert sha(objpath)==report['selected_object_sha256'];vp=rp.parent/'verification.json';v=json.loads(vp.read_text());assert v['report_sha256']==sha(rp) and v['driver_sha256']==sha(ROOT/'r1/tools'/('verify_'+name.replace('-','_')+'.py'));extra_reports[name]=dict(report_sha256=sha(rp),object_sha256=sha(objpath),receipt_sha256=sha(vp))
  for path,digest in report['inputs'].items():assert sha(ROOT/path)==digest,path
 count_report=BASE/'rtos-task-count/report.json';count=json.loads(count_report.read_text());count_obj=count_report.parent/'task-count.o';assert sha(count_obj)==count['selected_object_sha256']
 for path,digest in count['inputs'].items():assert sha(ROOT/path)==digest,path
 extra_reports['rtos-task-count']=dict(report_sha256=sha(count_report),object_sha256=sha(count_obj),verified_through='rtos-timer-isr-queue/verification.json')
 extra_reports['rtos-interrupt-priority']['role']='Independent revalidation; graph uses existing board-owned rtos-critical validator and shared priority state'
 roots=['uxTaskGetNumberOfTasks','r1_native_timer_task','xTimerCreate','xTimerCreateStatic','xTimerGenericCommand','pvPortMalloc','r1_native_initial_xpsr','uxTopUsedPriority','vTaskStartScheduler','xQueueGenericSend',*['r1_timer_runtime_'+n for n in ENTRIES]];remaining=sorted((set(undefined_symbols(obj)[0])|set(undefined_symbols(api_obj)[0])|set(undefined_symbols(isr_obj)[0])|set(undefined_symbols(priority_obj)[0])|set(undefined_symbols(count_obj)[0]))-(set(undefined_symbols(obj)[1])|set(undefined_symbols(api_obj)[1])|set(undefined_symbols(isr_obj)[1])|set(undefined_symbols(priority_obj)[1])|set(undefined_symbols(count_obj)[1])));bindings={n:0x1100001+i*16 for i,n in enumerate(remaining)}
 with tempfile.TemporaryDirectory() as directory:
  t=Path(directory);ld=t/'layout.ld';elf=t/'graph.elf';binary=t/'text.bin'
  ld.write_text('SECTIONS { '+''.join(n+' '+hex(a)+' (NOLOAD) : { *('+n+') } ' for n,a in sections.items())+'.r1.task.initial_xpsr 0x9c4cc : { *(.r1.task.initial_xpsr) } .r1.scheduler.top_used_priority 0x2000784c : { *(.data.uxTopUsedPriority) *(.rodata.uxTopUsedPriority) } .text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } .bss 0x2003e000 (NOLOAD) : { *(.bss*) *(COMMON) } .unused_data 0x21000000 : { *(.r1.*) *(.wdt.*) *(.nrf*) *(.sdh*) *(.data*) } /DISCARD/ : { *(.comment) *(.note*) } }')
  subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--gc-sections',*['--undefined='+n for n in roots],*['--defsym='+n+'='+hex(a) for n,a in bindings.items()],str(obj),*([str(api_obj),str(isr_obj),str(count_obj)] if not stage.get('canonical_board_includes_timer_objects') else []),'-o',str(elf)],check=True,capture_output=True)
  subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True);syms={x.split()[-1]:int(x.split()[0],16) for x in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x.split())==3};stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
  for u in (stock,candidate):u.mem_map(0x20000,0xc0000);u.mem_map(0x1000000,0x40000);u.mem_map(0x1100000,0x1000);u.mem_map(0x1200000,0x1000);u.mem_map(0x20000000,0x40000);u.mem_map(0xe000e000,0x1000)
  stock.mem_write(0x27000,app.read_bytes());candidate.mem_write(0x1000000,binary.read_bytes());assert len(binary.read_bytes())<0x40000
  for section,address,expected in (('.r1.task.initial_xpsr',0x9c4cc,0x1000000),('.r1.scheduler.top_used_priority',0x2000784c,55)):
   p=t/(section+'.bin');subprocess.run(['arm-none-eabi-objcopy','--dump-section',section+'='+str(p),str(elf)],check=True);assert p.read_bytes()==struct.pack('<I',expected);candidate.mem_write(address,p.read_bytes())
  def word(u,a):return struct.unpack('<I',bytes(u.mem_read(a,4)))[0]
  def put(u,a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
  targets={'uxTaskGetNumberOfTasks':0x9566c,'xQueueGenericSendFromISR':0x97da4,'vPortValidateInterruptPriority':0x95f18,'xQueueReceive':0x97f50,'vQueueWaitForMessageRestricted':0x95f8e,'vTaskPlaceOnEventListRestricted':0x961b8,'vTaskSuspendAll':0x9659c,'xTaskResumeAll':0x98b24,'pvPortMalloc':0x855a0,'vPortFree':0x95d48}
  def hook(u,a,size,user):
   nonlocal callbacks
   f=states[id(u)]
   if f['phase'] in ('runtime','task-loop'):
    counts=provider_counts['native' if u is stock else 'source']
    for name,native in targets.items():
     if a==((native if u is stock else syms[name])&~1):counts[name]=counts.get(name,0)+1
   if f['phase']=='task-loop' and a==(0x85512 if u is stock else syms['prvGetNextExpireTime']&~1):
    if f['loops']==1:f['loop_boundary']=True;u.emu_stop();return
    f['loops']+=1
   if u is candidate:assert not 0x20000<=a<0xe0000 and a not in {v&~1 for v in bindings.values()},hex(a)
   if f['phase']=='startup' and a==((0x979dc if u is stock else syms['xPortStartScheduler'])&~1):f['stopped']=True;u.emu_stop();return
   if a in (0x1200000,0x1200010):
    arg=u.reg_read(UC_ARM_REG_R0);f['trace'].append(('timer',arg,word(u,arg+24),u.mem_read(arg+40,1)[0]) if a==0x1200000 else ('pended',arg,u.reg_read(UC_ARM_REG_R1)));callbacks+=1;u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  for u in (stock,candidate):u.hook_add(UC_HOOK_CODE,hook)
  stock.reg_write(UC_ARM_REG_SP,0x2003f000);states[id(stock)]={'phase':'cold'};stock.emu_start(0x283a1,0x27208,count=2000000);assert stock.reg_read(UC_ARM_REG_PC)==0x27208
  baseline={id(u):bytes(u.mem_read(0x20000000,0x40000)) for u in (stock,candidate)}
  def run(u,entry,args=()):
   u.reg_write(UC_ARM_REG_SP,0x2003c000);u.reg_write(UC_ARM_REG_LR,0x20000101)
   for reg,value in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),args):u.reg_write(reg,value)
   u.mem_write(0x2003c000,struct.pack('<2I',*(list(args[4:])+[0,0])[:2]))
   try:u.emu_start(entry|1,0x20000100,count=2000000)
   except UcError as error:raise AssertionError((u is stock,hex(entry),args,hex(u.reg_read(UC_ARM_REG_PC)),states[id(u)])) from error
   if states[id(u)]['phase']=='task-loop':assert states[id(u)]['loop_boundary']
   elif states[id(u)]['phase']!='startup':assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003c000,(hex(entry),hex(u.reg_read(UC_ARM_REG_PC)))
  def call_target(u,lr):
   first,second=struct.unpack('<2H',bytes(u.mem_read((lr&~1)-4,4)));assert first&0xf800==0xf000 and second&0xd000==0xd000;sign=(first>>10)&1;offset=(sign<<24)|((1^((second>>13)&1)^sign)<<23)|((1^((second>>11)&1)^sign)<<22)|((first&0x3ff)<<12)|((second&0x7ff)<<1)
   return ((lr&~1)+offset-(1<<25 if sign else 0))&0xffffffff
  function_sizes={x.split()[-1]:int(x.split()[1],16) for x in subprocess.check_output(['arm-none-eabi-nm','-S',str(elf)],text=True).splitlines() if len(x.split())==4}
  def snapshot(u):
   queue=bytearray(u.mem_read(0x2002b258,0x278))
   # Generic command writes12 defined bytes in a16-byte daemon message.
   # Compare each defined field; ignore only the four uninitialized padding bytes.
   for offset in range(80+12,80+512,16):queue[offset:offset+4]=bytes(4)
   heap=bytearray(u.mem_read(0x2001e588,51200));end=word(u,0x200077fc)
   if end:
    block=0x2001e588
    while block<end:
     value=word(u,block+4);size=value&0x7fffffff;assert size and not size&7 and block+size<=end
     if value&0x80000000:
      lr=word(u,block+8);assert call_target(u,lr)==(0x855a0 if u is stock else syms['pvPortMalloc']&~1)
      if u is stock:assert lr==0x98c5d
      else:
       assert syms['xTimerCreate']<=(lr&~1)<syms['xTimerCreate']+function_sizes['xTimerCreate'];struct.pack_into('<I',heap,block-0x2001e588+8,word(stock,block+8))
     block+=size
   return (bytes(u.mem_read(0x20001000,0x1000)),bytes(u.mem_read(0x20007810,96)),bytes(u.mem_read(0x2002ad94,1220)),bytes(queue),bytes(u.mem_read(0x200077fc,20)),bytes(heap),word(u,0xe000ed04),u.reg_read(UC_ARM_REG_BASEPRI),states[id(u)]['trace'],bytes(u.mem_read(0x2002b940,112)))
  def compare():
   nonlocal comparisons
   a=snapshot(stock);b=snapshot(candidate);assert a==b,[(i,[(j,x,y) for j,(x,y) in enumerate(zip(av,bv)) if x!=y][:12] if isinstance(av,bytes) else (av,bv)) for i,(av,bv) in enumerate(zip(a,b)) if av!=bv];comparisons+=1
  for now,period,auto,dynamic,isr in itertools.product((0,1,99,0xfffffffe),(1,2,100),(0,1),(0,1),(0,1)):
   for u in (stock,candidate):
    u.mem_write(0x20000000,baseline[id(u)]);u.mem_write(0xe000e000,bytes(4096));u.reg_write(UC_ARM_REG_IPSR,0);u.reg_write(UC_ARM_REG_BASEPRI,0);u.reg_write(UC_ARM_REG_PRIMASK,0);states[id(u)]={'phase':'startup','stopped':False,'trace':[]};run(u,0x964c8 if u is stock else syms['vTaskStartScheduler']);assert states[id(u)]['stopped'];states[id(u)]['phase']='runtime';put(u,0x20007814,0);u.reg_write(UC_ARM_REG_BASEPRI,0)
    run(u,0x9566c if u is stock else syms['uxTaskGetNumberOfTasks']);assert u.reg_read(UC_ARM_REG_R0)==2
    # Create the actual timer through the admitted upstream factory bodies.
    u.mem_write(0x20001000,bytes([0x93])*44)
    args=(0x20001400,period,auto,0x12345678,0x1200001)
    if not dynamic:args+=(0x20001000,)
    run(u,(0x98c48 if dynamic else 0x98c7c) if u is stock else syms['xTimerCreate' if dynamic else 'xTimerCreateStatic'],args);timer=u.reg_read(UC_ARM_REG_R0)
    assert (0x2001e588<timer<0x2002ad88) if dynamic else timer==0x20001000
    states[id(u)]['timer']=timer;put(u,0x20007828,now);put(u,0x20007864,now)
    u.reg_write(UC_ARM_REG_IPSR,33 if isr else 0);run(u,0x98d04 if u is stock else syms['xTimerGenericCommand'],(timer,6 if isr else 1,now,0x20001300 if isr else 0,0));assert u.reg_read(UC_ARM_REG_R0)==1;u.reg_write(UC_ARM_REG_IPSR,0)
    run(u,0x852e0 if u is stock else syms['r1_timer_runtime_ProcessReceivedCommands'])
   compare()
   for u in (stock,candidate):
    expiry=(now+period)&0xffffffff;put(u,0x20007828,expiry);run(u,0x85484 if u is stock else syms['r1_timer_runtime_SampleTimeNow'],(0x20001200,));run(u,0x852a0 if u is stock else syms['r1_timer_runtime_ProcessExpiredTimer'],(expiry,expiry))
   compare()
   for u in (stock,candidate):
    current=word(u,0x20007868);empty=word(u,current)==0;next_expiry=0 if empty else word(u,word(u,current+12))
    run(u,0x853d4 if u is stock else syms['r1_timer_runtime_ProcessTimerOrBlockTask'],(next_expiry,int(empty)))
   compare()
   for u in (stock,candidate):
    # A producer wakes the blocked daemon through the actual queue/event-list graph.
    u.reg_write(UC_ARM_REG_IPSR,33 if isr else 0);run(u,0x98d04 if u is stock else syms['xTimerGenericCommand'],(states[id(u)]['timer'],8 if isr else 3,expiry,0x20001300 if isr else 0,0));assert u.reg_read(UC_ARM_REG_R0)==1;u.reg_write(UC_ARM_REG_IPSR,0);run(u,0x852e0 if u is stock else syms['r1_timer_runtime_ProcessReceivedCommands'])
   compare()
   for u in (stock,candidate):
    run(u,0x98d04 if u is stock else syms['xTimerGenericCommand'],(states[id(u)]['timer'],5,expiry,0,0));assert u.reg_read(UC_ARM_REG_R0)==1
    # Execute a complete daemon iteration while a queued command prevents blocking.
    states[id(u)].update(phase='task-loop',loops=0,loop_boundary=False);run(u,0x85510 if u is stock else syms['r1_native_timer_task'],(0,));states[id(u)]['phase']='runtime'
   compare()
  for counts in provider_counts.values():assert all(counts.get(name,0)>0 for name in targets),counts
  assert provider_counts['native']==provider_counts['source']
  result=dict(application_sha256=sha(app),stage_receipt_sha256=sha(out/'stage-verification.json'),stage_object_sha256=sha(obj),driver_sha256=sha(Path(__file__)),api_report_sha256=sha(api_report),api_object_sha256=sha(api_obj),api_receipt_sha256=sha(api_receipt),comparisons=comparisons,timer_callback_fixture_calls_per_implementation=callbacks//2,provider_interception=False,executed_provider_entry_counts=provider_counts,extra_provider_reports=extra_reports,workflows=96,dynamic_timer_workflows=48,static_timer_workflows=48,isr_command_workflows=48,timer_task_loop_iterations_per_implementation=96,scope='Actual scheduler startup and static timer queue, queue send/receive, runtime command/expiry/restricted wait, task event/delayed placement, suspend/resume and heap allocation/deletion and actual ISR queue send/priority validation; callback and port-start boundaries explicit',limitations=['Timers are created through actual source APIs. Callback returns remain explicit fixtures. Heap caller LR is normalized only after validating the original BL target and constructor call site. Message bytes12..15 are uninitialized padding; only these four bytes per queue slot are normalized. One daemon iteration per workflow executes with a pending delete command preventing task blocking, then stops before the second iteration. Task/exception transfer and physical time do not execute. Not canonical board/frontier admission or instruction identity.']);(out/'graph-verification.json').write_text(json.dumps(result,indent=2)+'\n');print(comparisons,'timer graph comparisons',callbacks//2,'callbacks per implementation')
if __name__=='__main__':main()
