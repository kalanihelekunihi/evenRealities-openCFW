#!/usr/bin/env python3
"""Trace actual task startup and bounded infinite-loop prefixes against stock."""
import hashlib,json,struct,subprocess,tempfile,itertools,sys
from pathlib import Path
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_WRITE_UNMAPPED
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_BASEPRI
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
TASKS={'gtx':(0x920ec,0x200065e0,0x200065b8),'msgtx':(0x9227c,0x200065bc,0x200065b4),'sensor':(0x92580,0x20006608,0x20006604),'service':(0x926dc,0x2000668c,0x20006688),'storage':(0x46954,0x200066d8,0x200066d4)}
PROVIDERS={'r1_native_sync_wait':0x923b4,'osMessageQueueNew':0x7d3b4,'r1_native_sync_signal':0x92440,'r1_native_watchdog_register':0x5db14,'r1_native_watchdog_arm':0x5dbea,'osThreadFlagsWait':0x7d780,'r1_native_watchdog_disarm':0x5dbbc,'r1_native_watchdog_feed':0x5da00,'r1_native_output_worker':0x44f50,'r1_native_worker_park':0x45c20,'r1_native_stream_initialize':0x8a55c,'r1_native_accelerometer_singleton':0x89d88,'r1_native_stream_register':0x89eec,'r1_native_temperature_singleton':0x8a1ac,'r1_native_health_initialize':0x4a21c,'r1_event_publish':0x8d8fc,'r1_native_sensor_timer_poll':0x8a45c,'osMessageQueueGet':0x7d310,'r1_native_event_dispatch':0x8d888,'r1_native_motion_interrupt':0x50294,'r1_native_suspend_signal':0x923a4,'osDelay':0x7d154,'r1_native_service_hardware_initialize':0x45c84,'r1_native_health_database_initialize':0x70030,'r1_native_hr_cache_initialize':0x8d534,'r1_native_spo2_cache_initialize':0x8e54e,'r1_native_temperature_cache_initialize':0x8e69c,'r1_native_stress_cache_initialize':0x8e558,'r1_native_activity_cache_initialize':0x8a7f0,'r1_native_sleep_database_initialize':0x8dd8c,'r1_native_hrv_cache_initialize':0x8d884,'r1_native_proto_port_reset':0x82f78,'r1_native_storage_hardware_initialize':0x45d00,'r1_native_delayed_schedule':0x65b4c}
def main():
 real_sender='--real-sender' in sys.argv;real_output='--real-output' in sys.argv or real_sender;real_watchdog='--real-watchdog' in sys.argv or real_output
 real_sync='--real-sync' in sys.argv or real_watchdog
 receipt=BASE/('native-tasks/sender-integration-verification.json' if real_sender else 'native-tasks/output-integration-verification.json' if real_output else 'native-tasks/watchdog-integration-verification.json' if real_watchdog else 'native-tasks/sync-integration-verification.json' if real_sync else 'native-tasks/verification.json');receipt.unlink(missing_ok=True);app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';report=BASE/'native-tasks/report.json';data=json.loads(report.read_text());obj=BASE/'native-tasks/native_tasks.o';assert sha(obj)==data['units'][0]['object_sha256']
 for path,digest in data['inputs'].items():assert sha(ROOT/path)==digest,path
 providers={};others=[]
 for name,object_name in (('native-events','native_events.o'),('native-tx','native_tx.o')):
  path=BASE/(name+'/report.json');r=json.loads(path.read_text());object_path=BASE/(name+'/'+object_name);assert sha(object_path)==r['units'][0]['object_sha256'];others.append(object_path);providers[name+'/report.json']=sha(path)
 if real_sync:
  for name in ('r1_native_sync_wait','r1_native_sync_signal','r1_native_suspend_signal','r1_native_worker_park'):del PROVIDERS[name]
  PROVIDERS.update({'osEventFlagsSet':0x7d1a0,'r1_structured_log_mode_get':0x914ec})
  path=BASE/'native-sync/report.json';r=json.loads(path.read_text());object_path=BASE/'native-sync/native_sync.o';assert sha(object_path)==r['units'][0]['object_sha256'];others.append(object_path);providers['native-sync/report.json']=sha(path)
  PROVIDERS.update({'r1_structured_log_format':0x91638,'nrf_log_frontend_std_1':0x799c8})
 if real_watchdog:
  for name in ('r1_native_watchdog_register','r1_native_watchdog_arm','r1_native_watchdog_disarm','r1_native_watchdog_feed'):del PROVIDERS[name]
  PROVIDERS.update({'pvPortMalloc':0x855a0,'osMutexAcquire':0x7d488,'osMutexRelease':0x7d536})
  path=BASE/'native-watchdog/report.json';r=json.loads(path.read_text());object_path=BASE/'native-watchdog/native_watchdog.o';selected=BASE/'native-watchdog/current-task-only.o';assert sha(object_path)==r['units'][0]['object_sha256'] and sha(selected)==r['selected_current_task_sha256'];others.extend((object_path,selected));providers['native-watchdog/report.json']=sha(path)
  path=BASE/'runtime/report.json';r=json.loads(path.read_text());object_path=BASE/'runtime/memory-runtime.o';assert sha(object_path)==r['relocatable_sha256'];others.append(object_path);providers['runtime/report.json']=sha(path)
 if real_output:
  del PROVIDERS['r1_native_output_worker'];PROVIDERS.update({'r1_native_ble_message_send':0x3e7a8,'vPortFree':0x95d48,'nrf_log_frontend_std_0':0x799c0})
  for name,filename in (('native-output','native_output.o'),('connection-handle','connection_handle.o')):
   path=BASE/(name+'/report.json');r=json.loads(path.read_text());object_path=BASE/(name+'/'+filename);assert sha(object_path)==r['units'][0]['object_sha256'];others.append(object_path);providers[name+'/report.json']=sha(path)
 if real_sender:
  del PROVIDERS['r1_native_ble_message_send'];PROVIDERS.update({'osSemaphoreAcquire':0x7d57c,'osSemaphoreRelease':0x7d698,'osSemaphoreGetCount':0x7d5e8,'r1_adc_error':0x4e5bc,'r1_native_bae8_send':0x526cc})
  path=BASE/'native-ble-send/report.json';r=json.loads(path.read_text());object_path=BASE/'native-ble-send/native_ble_send.o';assert sha(object_path)==r['units'][0]['object_sha256'];others.append(object_path);providers['native-ble-send/report.json']=sha(path)
 callbacks={'r1_thread_create_a':0x43b8d,'r1_task_stop_668c':0x43b75,'r1_thread_create_f':0x46925,'r1_task_stop_6608':0x4690d,'r1_thread_create_g':0x46a45,'r1_task_stop_66d8':0x46a2d,'r1_thread_create_b':0x44ef1,'r1_task_stop_65e0':0x44ed9,'r1_thread_create_e':0x4509d,'r1_task_stop_65bc':0x45085}
 with tempfile.TemporaryDirectory() as directory:
  tmp=Path(directory);ld=tmp/'layout.ld';elf=tmp/'test.elf';binary=tmp/'test.bin';sections=' .r1.watchdog.enabled 0x20006730 (NOLOAD) : { *(.r1.watchdog.enabled) } .r1.watchdog.mutex 0x20006738 (NOLOAD) : { *(.r1.watchdog.mutex) } .r1.watchdog.registry 0x20015404 (NOLOAD) : { *(.r1.watchdog.registry) } .bss.pxCurrentTCB 0x2000781c (NOLOAD) : { *(.bss.pxCurrentTCB) } .r1.sync.flags 0x2000655c (NOLOAD) : { *(.r1.sync.flags) } .r1.event.sensor 0x2000668c : { *(.r1.event.sensor) } .r1.event.system 0x20006608 : { *(.r1.event.system) } .r1.event.storage 0x200066d8 : { *(.r1.event.storage) } .r1.ble.semaphores 0x200064fc (NOLOAD) : { *(.r1.ble.semaphores) } .r1.connection.field8 0x200064ba : { *(.r1.connection.field8) } .r1.connection.field10 0x200064bc : { *(.r1.connection.field10) } .r1.tx.channel1 0x200065bc : { *(.r1.tx.channel1) } .r1.tx.shared 0x200065e0 : { *(.r1.tx.shared) } '+''.join(' .r1.task.'+name+'.watchdog '+hex(row[2])+' (NOLOAD) : { *(.r1.task.'+name+'.watchdog) } ' for name,row in TASKS.items());ld.write_text('SECTIONS { .r1.output.ring 0x44fec : { *(.r1.output.ring) } .r1.output.sdk 0x4501c : { *(.r1.output.sdk) } .text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } '+sections+'/DISCARD/ : { *(.comment) *(.note*) } }')
  roots=['r1_native_task_'+n for n in TASKS]+['r1_native_storage_delayed_callback'];subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--gc-sections','--entry='+roots[0],*['--undefined='+n for n in roots],*['--defsym='+n+'='+hex(0x100e001+i*16) for i,n in enumerate(PROVIDERS)],*['--defsym='+n+'='+hex(a) for n,a in callbacks.items()],str(obj),*map(str,others),*(['--defsym=r1_native_bae8_service=0x20006504'] if real_sender else []),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True)
  syms={x.split()[-1]:int(x.split()[0],16) for x in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x.split())==3};stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);stock.mem_map(0x20000,0xc0000);stock.mem_write(0x27000,app.read_bytes())
  for uc in (stock,candidate):uc.mem_map(0x1000000,0x10000);uc.mem_map(0x20000000,0x40000)
  if real_output:
   candidate.mem_map(0x40000,0x10000)
   for section,address in (('.r1.output.ring',0x44fec),('.r1.output.sdk',0x4501c)):
    path=tmp/(section+'.bin');subprocess.run(['arm-none-eabi-objcopy','--dump-section',section+'='+str(path),str(elf)],check=True);candidate.mem_write(address,path.read_bytes())
  candidate.mem_write(0x1000000,binary.read_bytes());stock.reg_write(UC_ARM_REG_SP,0x2003f000);stock.emu_start(0x283a1,0x27208,count=2000000);assert stock.reg_read(UC_ARM_REG_PC)==0x27208
  for name,row in TASKS.items():assert syms['r1_task_'+name+'_watchdog']==row[2];assert bytes(stock.mem_read(row[2],4))==bytes(candidate.mem_read(row[2],4))==bytes(4)
  seams={a:n for n,a in PROVIDERS.items()};seams.update({0x100e000+i*16:n for i,n in enumerate(PROVIDERS)});state={};faults={id(stock):[],id(candidate):[]};execution_counts={id(uc):dict(worker_entries=0,sends=0,frees=0) for uc in (stock,candidate)}
  def string(uc,address):
   out=bytearray()
   while True:
    b=uc.mem_read(address+len(out),1)[0]
    if not b:return out.decode()
    out.append(b);assert len(out)<32
  def hook(uc,address,size,user):
   if real_output and address in (0x44f50,syms['r1_native_output_worker']):execution_counts[id(uc)]['worker_entries']+=1
   if real_sender and address in (0x3e7a8,syms['r1_native_ble_message_send']):
    r=[uc.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)];state[id(uc)]['events'].append(('r1_native_ble_message_send',*r,struct.unpack('<I',bytes(uc.mem_read(uc.reg_read(UC_ARM_REG_SP),4)))[0]));execution_counts[id(uc)]['sends']+=1;return
   if address not in seams and not (real_watchdog and address==0x100e500):return
   name='watchdog_sample' if address==0x100e500 else seams[address];f=state[id(uc)];r=[uc.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)];value=0
   if name=='osMessageQueueNew':event=(name,tuple(r[:3]));value=f['queue']
   elif name=='r1_native_watchdog_register':event=(name,string(uc,r[0]),r[1]);value=0x20016000
   elif name=='osThreadFlagsWait':
    event=(name,tuple(r[:3]));f['events'].append(event)
    if real_sync and r[1]==1:
     uc.reg_write(UC_ARM_REG_R0,0x800000);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
    if f['waits']>=len(f['flags']):f['reason']='wait_limit';uc.emu_stop();return
    value=f['flags'][f['waits']];f['waits']+=1;f['received']=0
    if f['mutate'] and not real_watchdog:uc.mem_write(f['watchdog'],struct.pack('<I',0x20016000+f['waits']*16))
    uc.reg_write(UC_ARM_REG_R0,value);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
   elif name=='pvPortMalloc':event=(name,r[0]);value=0x20018000
   elif name=='osMutexAcquire':event=(name,r[0],r[1]);value=0xfffffffc
   elif name=='osMutexRelease':event=(name,r[0]);value=0xfffffffc
   elif name=='watchdog_sample':
    event=(name,r[0],r[1],struct.unpack('<I',bytes(uc.mem_read(r[1],4)))[0] if r[1] else None)
    if r[0] and r[1]:uc.mem_write(r[1],struct.pack('<I',0x76543210))
   elif name=='osEventFlagsSet':event=(name,r[0],r[1]);value=0xfffffffc
   elif name=='r1_structured_log_mode_get':event=(name,);value=0
   elif name in ('r1_structured_log_format','nrf_log_frontend_std_1'):raise AssertionError('Mode zero should not log')
   elif name=='r1_native_sensor_timer_poll':event=(name,);value=f['timeout']
   elif name=='osSemaphoreAcquire':event=(name,r[0],r[1]);value=0
   elif name=='osSemaphoreGetCount':event=(name,r[0]);value=0
   elif name=='osSemaphoreRelease':event=(name,r[0]);value=0xfffffffc
   elif name=='r1_adc_error':event=(name,r[0]);value=0x76543210
   elif name=='r1_native_bae8_send':
    assert r[0]==0x20006504;event=(name,r[0],r[1],struct.unpack('<I',bytes(uc.mem_read(r[2],4)))[0],r[3],struct.unpack('<I',bytes(uc.mem_read(uc.reg_read(UC_ARM_REG_SP),4)))[0]);value=0xfffffffc
   elif name=='osMessageQueueGet' and real_output and f['task'] in ('gtx','msgtx'):
    event=(name,r[0],r[2],r[3],bytes(uc.mem_read(r[1],4)));assert bytes(uc.mem_read(r[1],4))==bytes(4)
    if f['received']<f['records']:
     index=f['received'];f['received']+=1;pointer=0x2001a000+index*64
     if f['write_bytes']:uc.mem_write(r[1],struct.pack('<I',pointer))
     value=0
     if f['mutate']:uc.mem_write(f['context']+12,struct.pack('<I',0x20012000+index*32))
    else:value=0xfffffffd
   elif name=='r1_native_ble_message_send':
    execution_counts[id(uc)]['sends']+=1
    event=(name,*r,struct.unpack('<I',bytes(uc.mem_read(uc.reg_read(UC_ARM_REG_SP),4)))[0]);value=0xfffffffc
   elif name=='vPortFree':
    event=(name,r[0]);execution_counts[id(uc)]['frees']+=1
   elif name=='nrf_log_frontend_std_0':raise AssertionError('Valid connection should not log')
   elif name=='osMessageQueueGet':
    event=(name,r[0],r[2],r[3],bytes(uc.mem_read(r[1],16)))
    if f['received']<f['records']:
     index=f['received'];record=struct.pack('<4I',0x12340000+index,0x2003+index,4,0x89abcdef+index);uc.mem_write(r[1],record[:f['write_bytes']]);f['received']+=1;value=0
     if f['mutate']:uc.mem_write(f['context']+12,struct.pack('<I',0x20012000+index*32))
    else:value=0xfffffffd
   elif name=='r1_native_event_dispatch':event=(name,bytes(uc.mem_read(r[0],16)))
   elif name=='r1_event_publish':event=(name,tuple(r[:3]));value=0xfffffffc
   elif name=='r1_native_delayed_schedule':
    assert r[0]==(0x7ca71 if uc is stock else syms['r1_native_storage_delayed_callback']|1);event=(name,'storage_callback',r[1],r[2])
   elif name=='osDelay':
    event=(name,r[0]);f['delays']+=1
    if f['delays']>=3:f['events'].append(event);f['reason']='delay_limit';uc.emu_stop();return
    value=0xfffffffc
   elif name=='r1_native_worker_park':
    event=(name,r[0],r[1])
    if not f['park_returns']:f['events'].append(event);f['reason']='park_stop';uc.emu_stop();return
   elif name in ('r1_native_sync_wait','r1_native_sync_signal','r1_native_suspend_signal','r1_native_output_worker','r1_native_watchdog_arm','r1_native_watchdog_disarm','r1_native_watchdog_feed'):event=(name,r[0])
   else:event=(name,)
   f['events'].append(event)
   if f['mutate'] and name in ('r1_native_watchdog_arm','r1_native_watchdog_disarm','r1_native_watchdog_feed'):
    old=struct.unpack('<I',bytes(uc.mem_read(f['watchdog'],4)))[0];uc.mem_write(f['watchdog'],struct.pack('<I',(old+4)&0xffffffff))
   uc.reg_write(UC_ARM_REG_R0,value);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  def fault(uc,access,address,size,value,user):faults[id(uc)].append((address,size,value));return False
  for uc in (stock,candidate):uc.hook_add(UC_HOOK_CODE,hook);uc.hook_add(UC_HOOK_MEM_WRITE_UNMAPPED,fault)
  def run(uc,entry,task,flags,records,timeout,write_bytes,mutate,queue,park_returns,basepri):
   _,context,watchdog=TASKS[task];f=dict(events=[],reason=None,task=task,context=context,watchdog=watchdog,flags=flags,records=records,timeout=timeout,write_bytes=write_bytes,mutate=mutate,queue=queue,park_returns=park_returns,waits=0,received=0,delays=0);state[id(uc)]=f;faults[id(uc)].clear()
   if real_sender:uc.mem_write(0x200064fc,struct.pack('<2I',0x2000c000,0x2000c100));uc.mem_write(0x200064ba,struct.pack('<H',1))
   if real_output:
    uc.mem_write(0x200064bc,b'\0\0')
    for index in range(3):uc.mem_write(0x2001a000+index*64,struct.pack('<3I',0x12340000+index,index,0x98760004)+bytes([0x61+index])*4)
   uc.mem_write(0x2000655c,struct.pack('<I',0x20017000))
   if real_watchdog:
    uc.mem_write(0x20006730,b'\x01');uc.mem_write(0x20006738,struct.pack('<I',0x20019000));uc.mem_write(0x2000781c,struct.pack('<I',0x20012340));uc.mem_write(0x20015404,struct.pack('<4I',0x20019100,28,0,0));uc.mem_write(0x20019100,struct.pack('<3I',0,0,0x100e501));uc.mem_write(0x20018000,bytes([0xa5])*64)
   for row in TASKS.values():uc.mem_write(row[1]+12,struct.pack('<I',0xdeadbeef));uc.mem_write(row[2],struct.pack('<I',0xa5a5a5a5))
   uc.reg_write(UC_ARM_REG_BASEPRI,basepri);uc.reg_write(UC_ARM_REG_R0,0x12345678);uc.reg_write(UC_ARM_REG_SP,0x2003f000);uc.reg_write(UC_ARM_REG_LR,0x20000101)
   try:uc.emu_start(entry|1,0x20000100,count=100000)
   except UcError:assert faults[id(uc)],(task,hex(uc.reg_read(UC_ARM_REG_PC)));f['reason']='assertion'
   assert f['reason'] is not None,(task,hex(uc.reg_read(UC_ARM_REG_PC)),f['events'])
   return f['events'],f['reason'],list(faults[id(uc)]),uc.reg_read(UC_ARM_REG_BASEPRI),[(bytes(uc.mem_read(row[1]+12,4)),bytes(uc.mem_read(row[2],4))) for row in TASKS.values()],(bytes(uc.mem_read(0x20015404,16)),bytes(uc.mem_read(0x20018000,64))) if real_watchdog else None
  comparisons=0;assertions=0
  flags_cases=(0,1,2,3,0x400000,0x400002,0x800000,0x800001,0x800002,0xc00000,0xc00003,0xffffff,0x1000000,0x7fffffff,0x80000000,0x80000001,0xffffffff)
  for task,flag,records,timeout,write_bytes,mutate in itertools.product(TASKS,flags_cases,(0,1,3),(0,123,0xffffffff),(4,16),(False,True)):
   case=(task,(flag,0),records,timeout,write_bytes,mutate,0x20011000,False,32);a=run(stock,TASKS[task][0],*case);b=run(candidate,syms['r1_native_task_'+task],*case);assert a==b,(case,a,b);comparisons+=1
  for task,queue,park_returns,basepri in itertools.product(TASKS,(0,0x20011000),(False,True),(0,32,128)):
   case=(task,(0x800001,),1,123,16,True,queue,park_returns,basepri);a=run(stock,TASKS[task][0],*case);b=run(candidate,syms['r1_native_task_'+task],*case);assert a==b,(case,a,b);comparisons+=1
   if a[1]=='assertion':assert a[2]==[(0xffffffff,4,0)] and a[3]==64;assertions+=1
  callback_comparisons=0
  for argument in (0,1,0x12345678,0xffffffff):
   outcomes=[]
   for uc,entry in ((stock,0x7ca70),(candidate,syms['r1_native_storage_delayed_callback'])):
    state[id(uc)]={'events':[],'mutate':False};uc.reg_write(UC_ARM_REG_R0,argument);uc.reg_write(UC_ARM_REG_SP,0x2003f000);uc.reg_write(UC_ARM_REG_LR,0x20000101);uc.emu_start(entry|1,0x20000100,count=10000);assert uc.reg_read(UC_ARM_REG_PC)==0x20000100;outcomes.append(state[id(uc)]['events'])
   assert outcomes[0]==outcomes[1]==[('r1_event_publish',(0x2005,0,0))];callback_comparisons+=1
 if real_output:assert execution_counts[id(stock)]==execution_counts[id(candidate)] and all(execution_counts[id(candidate)].values())
 receipt.write_text(json.dumps(dict(application_sha256=sha(app),report_sha256=sha(report),object_sha256=sha(obj),provider_reports=providers,actual_sync_bodies=real_sync,actual_watchdog_bodies=real_watchdog,actual_output_bodies=real_output,actual_sender_executed=real_sender,output_execution_counts=execution_counts[id(candidate)] if real_output else None,comparisons=comparisons,assertion_fault_comparisons=assertions,callback_comparisons=callback_comparisons,initial_watchdog_bytes_compared=20,scope='Five actual task entries: ordered startup, queue creation, watchdog state, bounded repeated loop traces, signed-range flag selection, queue drain/record zeroing, motion, suspend, failure faults and storage callback',limitations=[('Actual output worker, serialized sender/helpers, connection getters, synchronization/watchdog/current-task/memory execute; queue/allocator, semaphore APIs, BAE8 send, logger and other RTOS/startup/dispatch boundaries remain intercepted.' if real_sender else 'Actual output worker/veneers/connection getter, synchronization, watchdog/list, current-task getter and memory execute; queue, allocator, generic BLE sender, mutex, sample and startup/dispatch providers remain intercepted.' if real_output else 'Actual synchronization, watchdog/list, current-task getter and source memory bodies execute; heap, mutex, final sample, RTOS, startup and dispatch providers are intercepted.' if real_watchdog else 'Actual synchronization bodies execute; RTOS, watchdog, startup hardware/database and dispatch providers are intercepted.' if real_sync else 'RTOS, watchdog, synchronization, startup hardware/database and dispatch providers are intercepted.'),'Loops are observed for two waits, up to three queued records or three indefinite-delay attempts; this does not prove scheduler concurrency or actual hardware.','Actual creators/stoppers are not executed in this oracle; their context references are test-only initial-data bindings.','Original instruction identity and whole-image source completeness remain open.'],instruction_identity_proven=False),indent=2)+'\n');print(f'{comparisons} task trace comparisons and {callback_comparisons} callback cases passed, including {assertions} assertion faults')
if __name__=='__main__':main()
