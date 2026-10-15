#!/usr/bin/env python3
"""Compare native watchdog port/client/adapters, optionally executing pinned nrfx."""
import hashlib,json,struct,subprocess,tempfile,itertools,sys
from pathlib import Path
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_WRITE,UC_HOOK_MEM_WRITE_UNMAPPED,UC_HOOK_MEM_READ_UNMAPPED
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_PRIMASK,UC_ARM_REG_BASEPRI,UC_ARM_REG_IPSR
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();STATE=0x20007630;CACHE=0x20007694;RECORD=STATE+20;HEAD=0x20007680;ALT=0x2001c000
ROOTS={'r1_native_watchdog_hw_feed_thunk':0x95be8,'r1_native_watchdog_hw_close':0x500c8,'r1_native_watchdog_hw_handle_init':0x500d4,'r1_native_watchdog_hw_feed':0x500fc,'r1_native_watchdog_hw_open_feed':0x5010c,'r1_native_watchdog_port_stop':0x66234,'r1_native_watchdog_port_sample':0x6623e,'r1_native_watchdog_port_get':0x6625c,'r1_native_watchdog_port_start':0x66264,'r1_native_named_wdt_open':0x56658,'r1_native_named_wdt_feed':0x56638,'r1_native_named_wdt_register':0x56694,'r1_native_wdt_timeout':0x96a1e}
def main():
 native_logging='--native-sdk-logging' in sys.argv;real_ticks='--real-ticks' in sys.argv or native_logging;assert not real_ticks or '--real-critical' in sys.argv or native_logging;real_critical='--real-critical' in sys.argv or native_logging;real_division='--real-division' in sys.argv or native_logging;assert not real_critical or real_division;actual_sdk='--sdk' in sys.argv or native_logging;assert not real_division or actual_sdk;receipt=BASE/('watchdog-logging/verification.json' if native_logging else 'watchdog-startup/sdk-ticks-integration.json' if real_ticks else 'watchdog-startup/sdk-critical-integration.json' if real_critical else 'watchdog-startup/sdk-division-integration.json' if real_division else 'watchdog-startup/sdk-execution.json' if actual_sdk else 'watchdog-startup/device-verification.json');receipt.unlink(missing_ok=True);app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';report=BASE/('watchdog-logging/report.json' if native_logging else 'watchdog-startup/report.json');data=json.loads(report.read_text());obj=BASE/('watchdog-logging/native-watchdog-logging.o' if native_logging else 'watchdog-startup/native-watchdog-startup.o');assert sha(obj)==data['relocatable_sha256']
 if native_logging:assert sha(BASE/'watchdog-logging/mode-getter-only.o')==data['selected_getter_sha256']
 for path,digest in data['inputs'].items():assert sha(ROOT/path)==digest,path
 registry_report=BASE/'i2c5/report.json';registry=json.loads(registry_report.read_text());r=next(r for r in registry['units'] if r['source'].endswith('/registry/stock_registry.c'));registry_obj=Path(r['command'][-1]);assert sha(registry_obj)==r['object_sha256'];runtime_report=BASE/'runtime/report.json';runtime=BASE/'runtime/memory-runtime.o';assert sha(runtime)==json.loads(runtime_report.read_text())['relocatable_sha256']
 providers={'r1_adc_error':0x4e5bc,'osKernelGetTickCount':0x7d28c}
 if native_logging:providers['r1_structured_log_format']=0x91638
 if actual_sdk:providers.update({'__aeabi_uldivmod':0x274e8,'app_util_critical_region_enter':0x4ebec,'app_util_critical_region_exit':0x4ec34})
 if real_division:
  providers.pop('__aeabi_uldivmod');integer_report=BASE/'integer-runtime/report.json';integer=BASE/'integer-runtime/integer-runtime.o';assert sha(integer)==json.loads(integer_report.read_text())['relocatable_sha256']
 if real_critical:
  providers.pop('app_util_critical_region_enter');providers.pop('app_util_critical_region_exit');critical_report=BASE/'sdk-critical/report.json';critical=BASE/'sdk-critical/critical-only.o';assert sha(critical)==json.loads(critical_report.read_text())['selected_object_sha256']
 if real_ticks:
  providers.pop('osKernelGetTickCount');ticks_report=BASE/'rtos-ticks/report.json';ticks=BASE/'rtos-ticks/ticks-only.o';assert sha(ticks)==json.loads(ticks_report.read_text())['selected_object_sha256']
 if not actual_sdk:providers.update({'nrfx_wdt_init':0x7b570,'nrfx_wdt_channel_alloc':0x7b470,'nrfx_wdt_enable':0x7b520,'nrfx_wdt_channel_feed':0x7b508})
 with tempfile.TemporaryDirectory() as directory:
  tmp=Path(directory);ld=tmp/'layout.ld';elf=tmp/'test.elf';binary=tmp/'test.bin';state_file=tmp/'state.bin';port_file=tmp/'port.bin';ld.write_text('SECTIONS { .wdt.log.init 0x7b5f8 : { *(.rodata.nrfx_wdt_init.r1_log_format) } .wdt.log.alloc 0x7b4e4 : { *(.rodata.nrfx_wdt_channel_alloc.r1_log_format) } .wdt.log.enable 0x7b560 : { *(.rodata.nrfx_wdt_enable.r1_log_format) } .r1.log.mode 0x200068ec : { *(.r1.log.mode) } .text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } .r1.watchdog.port 0x993d0 : { *(.r1.watchdog.port) } .r1.wdt.state 0x20007630 : { *(.r1.wdt.state) } .r1.watchdog.device 0x20007694 (NOLOAD) : { *(.r1.watchdog.device) } .r1.registry.head 0x20007680 (NOLOAD) : { *(.r1.registry.head) } .bss.ucMaxSysCallPriority 0x20007810 (NOLOAD) : { *(.bss.ucMaxSysCallPriority) } .bss.ulMaxPRIGROUPValue 0x20007818 (NOLOAD) : { *(.bss.ulMaxPRIGROUPValue) } .bss.xTickCount 0x20007828 (NOLOAD) : { *(.bss.xTickCount) } .bss.xSchedulerRunning 0x20007830 (NOLOAD) : { *(.bss.xSchedulerRunning) } .bss.uxSchedulerSuspended 0x20007850 (NOLOAD) : { *(.bss.uxSchedulerSuspended) } .bss.nrf_nvic_state 0x2002c2fc (NOLOAD) : { *(.bss.nrf_nvic_state) } .bss.m_state 0x20007948 (NOLOAD) : { *(.bss.m_state) } .bss.m_alloc_index 0x20007949 (NOLOAD) : { *(.bss.m_alloc_index) } .bss.m_wdt_event_handler 0x2000794c (NOLOAD) : { *(.bss.m_wdt_event_handler) } /DISCARD/ : { *(.comment) *(.note*) } }')
  roots=list(ROOTS)+(['WDT_IRQHandler'] if actual_sdk else []);subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--gc-sections','--entry='+roots[0],*['--undefined='+n for n in roots],*['--defsym='+n+'='+hex(0x100e001+i*16) for i,n in enumerate(providers)],str(obj),str(registry_obj),str(runtime),*([str(integer)] if real_division else []),*([str(critical)] if real_critical else []),*([str(ticks)] if real_ticks else []),*([str(BASE/'watchdog-logging/mode-getter-only.o')] if native_logging else []),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True)
  for section,path in (('.r1.wdt.state',state_file),('.r1.watchdog.port',port_file)):subprocess.run(['arm-none-eabi-objcopy','--dump-section',section+'='+str(path),str(elf)],check=True)
  syms={x.split()[-1]:int(x.split()[0],16) for x in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x.split())==3};assert syms['r1_native_named_wdt']==STATE and syms['r1_native_watchdog_device']==CACHE
  if real_ticks:
   for name,address in {'ucMaxSysCallPriority':0x20007810,'ulMaxPRIGROUPValue':0x20007818,'xTickCount':0x20007828,'xSchedulerRunning':0x20007830,'uxSchedulerSuspended':0x20007850}.items():assert syms[name]==address
  if real_critical:assert syms['nrf_nvic_state']==0x2002c2fc
  if actual_sdk:assert (syms['m_state'],syms['m_alloc_index'],syms['m_wdt_event_handler'])==(0x20007948,0x20007949,0x2000794c)
  stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);stock.mem_map(0x20000,0xc0000);stock.mem_write(0x27000,app.read_bytes());candidate.mem_map(0x90000,0x10000);candidate.mem_map(0x70000,0x10000)
  for uc in (stock,candidate):uc.mem_map(0x1000000,0x10000);uc.mem_map(0x20000000,0x40000);uc.mem_map(0x40010000,0x1000);uc.mem_map(0xe000e000,0x1000)
  if native_logging:
   for section,address in (('.wdt.log.init',0x7b5f8),('.wdt.log.alloc',0x7b4e4),('.wdt.log.enable',0x7b560)):
    path=tmp/(section+'.bin');subprocess.run(['arm-none-eabi-objcopy','--dump-section',section+'='+str(path),str(elf)],check=True);raw=path.read_bytes();assert raw==app.read_bytes()[address-0x27000:address-0x27000+len(raw)];candidate.mem_write(address,raw)
   assert syms['r1_structured_log_mode']==0x200068ec
  candidate.mem_write(0x1000000,binary.read_bytes());candidate.mem_write(0x993d0,port_file.read_bytes());stock.reg_write(UC_ARM_REG_SP,0x2003f000);stock.emu_start(0x283a1,0x27208,count=2000000);assert stock.reg_read(UC_ARM_REG_PC)==0x27208;initial={id(stock):bytes(stock.mem_read(STATE,80)),id(candidate):state_file.read_bytes()};states={};writes={id(stock):[],id(candidate):[]};faults={id(stock):[],id(candidate):[]}
  def string(uc,address):
   out=bytearray()
   while True:
    value=uc.mem_read(address+len(out),1)[0]
    if not value:return out.decode()
    out.append(value);assert len(out)<256
  assert string(stock,struct.unpack_from('<I',initial[id(stock)])[0])==string(candidate,struct.unpack_from('<I',initial[id(candidate)])[0])=='watchdog'
  def normalized_state(uc):
   value=bytearray(uc.mem_read(STATE,80))
   for offset,entry,name in ((44,0x56659,'r1_native_named_wdt_open'),(68,0x56639,'r1_native_named_wdt_feed')):assert struct.unpack_from('<I',value,offset)[0]==(entry if uc is stock else syms[name]|1)
   for offset in (0,20,44,68):value[offset:offset+4]=bytes(4)
   return bytes(value)
  candidate.mem_write(STATE,initial[id(candidate)]);assert normalized_state(stock)==normalized_state(candidate)
  port_fields=struct.unpack('<3I',port_file.read_bytes());assert port_fields==tuple(syms[name]|1 for name in ('r1_native_watchdog_port_start','r1_native_watchdog_port_stop','r1_native_watchdog_port_sample'));assert struct.unpack('<3I',bytes(stock.mem_read(0x993d0,12)))==(0x66265,0x66235,0x6623f)
  seams={a:n for n,a in providers.items()};seams.update({0x100e000+i*16:n for i,n in enumerate(providers)})
  def hook(uc,address,size,user):
   if native_logging and address in (0x914ec,syms['r1_structured_log_mode_get']):
    f=states[id(uc)];index=f['getter_reads'];f['getter_reads']+=1;sequence=f['mode_sequence']
    if sequence:uc.mem_write(0x200068ec,bytes([sequence[min(index,len(sequence)-1)]]))
    f['events'].append(('mode',uc.mem_read(0x200068ec,1)[0]));return
   if address not in seams and address not in (0x100e400,0x100e410,0x100e420):return
   f=states[id(uc)];r=[uc.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)];name=seams.get(address);value=0
   if name=='nrfx_wdt_init':
    assert r[1]==(0x96a1f if uc is stock else syms['r1_native_wdt_timeout']|1);event=(name,bytes(uc.mem_read(r[0],12)),'empty_timeout');value=f['init_status']
    if f['mutate']:uc.mem_write(CACHE,struct.pack('<I',ALT))
   elif name=='nrfx_wdt_channel_alloc':
    event=(name,r[0]);value=f['alloc_status']
    if not value:uc.mem_write(r[0],bytes([f['allocated']]))
   elif name=='nrfx_wdt_enable':event=(name,)
   elif name=='nrfx_wdt_channel_feed':event=(name,r[0])
   elif name=='r1_structured_log_format':
    descriptor=string(uc,r[1]);assert r[1]==r[2] and r[1] in (0x7b5f8,0x7b4e4,0x7b560)
    args=() if r[0]==0x0c000000 else (string(uc,r[3]),string(uc,struct.unpack('<I',bytes(uc.mem_read(uc.reg_read(UC_ARM_REG_SP),4)))[0]))
    event=(name,r[0],r[1],descriptor,args)
   elif name=='r1_adc_error':event=(name,r[0])
   elif name=='osKernelGetTickCount':event=(name,);value=f['tick']
   elif name=='__aeabi_uldivmod':
    numerator=r[0]|(r[1]<<32);denominator=r[2]|(r[3]<<32);q,rem=divmod(numerator,denominator);f['events'].append((name,numerator,denominator));uc.reg_write(UC_ARM_REG_R0,q&0xffffffff);uc.reg_write(UC_ARM_REG_R1,q>>32);uc.reg_write(UC_ARM_REG_R2,rem&0xffffffff);uc.reg_write(UC_ARM_REG_R3,rem>>32);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
   elif name=='app_util_critical_region_enter':event=(name,uc.mem_read(r[0],1)[0]);uc.mem_write(r[0],b'\x01')
   elif name=='app_util_critical_region_exit':event=(name,r[0]);value=0x12345678
   else:event=('other_device',address,r[0],r[1] if address==0x100e410 else None,r[2] if address==0x100e410 else None);value=0x12345678
   f['events'].append(event);uc.reg_write(UC_ARM_REG_R0,value&0xffffffff);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  def write(uc,access,address,size,value,user):writes[id(uc)].append((address,size,value))
  def fault(uc,access,address,size,value,user):faults[id(uc)].append((address,size,value));return False
  for uc in (stock,candidate):
   uc.hook_add(UC_HOOK_CODE,hook);uc.hook_add(UC_HOOK_MEM_WRITE,write,begin=0x40010000,end=0x40010fff);uc.hook_add(UC_HOOK_MEM_WRITE,write,begin=0xe000e000,end=0xe000efff);uc.hook_add(UC_HOOK_MEM_WRITE_UNMAPPED,fault);uc.hook_add(UC_HOOK_MEM_READ_UNMAPPED,fault)
  def setup(uc,opened=0,channel=0,registered=True,cached=0,init_status=0,alloc_status=0,allocated=0,mutate=False,driver_state=0,alloc_index=0,mode=0,mode_sequence=()):
   states[id(uc)]={'events':[],'init_status':init_status,'alloc_status':alloc_status,'allocated':allocated,'mutate':mutate,'tick':0xfedcba98,'getter_reads':0,'mode_sequence':mode_sequence};writes[id(uc)].clear();faults[id(uc)].clear();uc.mem_write(STATE,initial[id(uc)]);uc.mem_write(STATE+4,bytes([opened,channel]));uc.mem_write(CACHE,struct.pack('<I',cached));uc.mem_write(HEAD,bytes(4));uc.mem_write(0x200068ec,bytes([mode]));uc.mem_write(0x40010000,bytes(4096));uc.mem_write(0xe000e000,bytes(4096));uc.mem_write(0x2002c2fc,bytes(12));uc.reg_write(UC_ARM_REG_PRIMASK,0);
   if real_critical:uc.mem_write(0xe000e180,struct.pack('<2I',0x12345678,0x87654321))
   uc.mem_write(0x20003000,bytes([0xa5])*4);uc.mem_write(0x20007828,struct.pack('<I',0xfedcba98));uc.mem_write(0x20007830,struct.pack('<I',1));uc.mem_write(0x20007850,bytes(4));uc.mem_write(0x20007810,b'\x40');uc.mem_write(0x20007818,bytes(4));uc.mem_write(0xe000e400,bytes([192])*240);uc.reg_write(UC_ARM_REG_IPSR,0);uc.reg_write(UC_ARM_REG_BASEPRI,0)
   handler=0x96a1f if uc is stock else syms['r1_native_wdt_timeout']|1;uc.mem_write(0x20007948,bytes([driver_state,alloc_index,0,0])+struct.pack('<I',handler));uc.mem_write(0x20002000,b'other\0');uc.mem_write(ALT,struct.pack('<6I',0x20002000,ALT+32,0,0,0,0));uc.mem_write(ALT+32,struct.pack('<9I',0x100e401,0,0,0x100e421,0,0,0x100e411,0,0))
   if registered:
    entry=0x56694 if uc is stock else syms['r1_native_named_wdt_register'];uc.reg_write(UC_ARM_REG_SP,0x2003f000);uc.reg_write(UC_ARM_REG_LR,0x20000101);uc.emu_start(entry|1,0x20000100,count=10000);assert uc.reg_read(UC_ARM_REG_R0)==1
  def run(uc,entry,args,void=False):
   for reg,value in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2),args):uc.reg_write(reg,value)
   uc.reg_write(UC_ARM_REG_SP,0x2003f000);uc.reg_write(UC_ARM_REG_LR,0x20000101)
   try:uc.emu_start(entry|1,0x20000100,count=100000)
   except UcError:assert faults[id(uc)],hex(uc.reg_read(UC_ARM_REG_PC))
   else:assert uc.reg_read(UC_ARM_REG_PC)==0x20000100
   control=bytearray(uc.mem_read(0x20007948,8));handler=struct.unpack_from('<I',control,4)[0];assert handler in (0,0x96a1f if uc is stock else syms['r1_native_wdt_timeout']|1);control[4:8]=bytes(4)
   return None if void or faults[id(uc)] else uc.reg_read(UC_ARM_REG_R0),list(states[id(uc)]['events']),list(faults[id(uc)]),normalized_state(uc),bytes(uc.mem_read(CACHE,4)),bytes(uc.mem_read(HEAD,4)),list(writes[id(uc)]),bytes(control),bytes(uc.mem_read(0x2002c2fc,12)),uc.reg_read(UC_ARM_REG_PRIMASK),uc.reg_read(UC_ARM_REG_BASEPRI),bytes(uc.mem_read(0x20003000,4))
  def compare(name,args,void=False):
   a=run(stock,ROOTS[name],args,void);b=run(candidate,syms[name],args,void);assert a==b,(name,args,a,b);return a
  comparisons=0
  if not actual_sdk:
   for opened,registered,cached,init_status,alloc_status,allocated,mutate in itertools.product((0,1,128),(False,True),(0,RECORD,ALT),(0,8),(0,4),(0,7),(False,True)):
    for uc in (stock,candidate):setup(uc,opened,3,registered,cached,init_status,alloc_status,allocated,mutate)
    compare('r1_native_watchdog_port_start',(10000,0,0));comparisons+=1
   for name in ROOTS:
    for opened,channel,arg0,command in itertools.product((0,1,128),(0,7,255),(0,1,0xffffffff),(0,1,2,0xffffffff)):
     for uc in (stock,candidate):setup(uc,opened,channel,cached=RECORD)
     args=(arg0,command,0x89abcdef) if name in ('r1_native_watchdog_port_start','r1_native_named_wdt_feed') else (command,0x20003000,0x89abcdef) if name=='r1_native_watchdog_port_sample' else (RECORD,0,0)
     compare(name,args,name=='r1_native_wdt_timeout');comparisons+=1
   for uc in (stock,candidate):setup(uc,cached=RECORD)
   compare('r1_native_watchdog_port_sample',(1,0,0));comparisons+=1
  else:
   for opened,channel,driver_state,alloc_index in itertools.product((0,1),(0,7,255),(0,1,2),(0,7,8,255)):
    for uc in (stock,candidate):setup(uc,opened,channel,cached=RECORD,driver_state=driver_state,alloc_index=alloc_index)
    compare('r1_native_watchdog_port_start',(10000,0,0));compare('r1_native_named_wdt_feed',(RECORD,0,0));comparisons+=2
   for reload,behaviour,priority in itertools.product((0,1,10000,0xffffffff),(0,1,8,9),(0,6,7,255)):
    for uc in (stock,candidate):setup(uc,cached=RECORD);uc.mem_write(STATE+8,bytes([behaviour,0,0,0])+struct.pack('<I',reload)+bytes([priority,0,0,0]))
    compare('r1_native_named_wdt_open',(RECORD,0,0));comparisons+=1
   for event in (0,1,0xffffffff):
    for uc in (stock,candidate):setup(uc,cached=RECORD);uc.mem_write(0x40010100,struct.pack('<I',event))
    a=run(stock,0x34a7c,(0,0,0),True);b=run(candidate,syms['WDT_IRQHandler'],(0,0,0),True);assert a==b,(event,a,b);comparisons+=1
  if real_ticks:
   for tick,ipsr,primask,basepri in itertools.product((0,1,0x7fffffff,0x80000000,0xfedcba98,0xffffffff),(0,15,16),(0,1),(0,32,128)):
    for uc in (stock,candidate):
     setup(uc,cached=RECORD);uc.mem_write(0x20007828,struct.pack('<I',tick));uc.reg_write(UC_ARM_REG_IPSR,ipsr);uc.reg_write(UC_ARM_REG_PRIMASK,primask);uc.reg_write(UC_ARM_REG_BASEPRI,basepri)
    compare('r1_native_watchdog_port_sample',(1,0x20003000,0));assert bytes(candidate.mem_read(0x20003000,4))==struct.pack('<I',tick);comparisons+=1
  if native_logging:
   for mode,driver_state,alloc_index in itertools.product(range(256),(0,1,2),(0,7,8,255)):
    for uc in (stock,candidate):setup(uc,cached=RECORD,driver_state=driver_state,alloc_index=alloc_index,mode=mode)
    compare('r1_native_watchdog_port_start',(10000,0,0));comparisons+=1
   for sequence in itertools.product(range(8),repeat=3):
    for uc in (stock,candidate):setup(uc,cached=RECORD,mode_sequence=sequence)
    compare('r1_native_watchdog_port_start',(10000,0,0));comparisons+=1
 receipt.write_text(json.dumps(dict(application_sha256=sha(app),report_sha256=sha(report),relocatable_sha256=sha(obj),registry_report_sha256=sha(registry_report),runtime_report_sha256=sha(runtime_report),comparisons=comparisons,actual_sdk_executed=actual_sdk,actual_integer_runtime_executed=real_division,actual_critical_regions_executed=real_critical,actual_tick_getter_executed=real_ticks,native_sdk_logging_executed=native_logging,mode_values_tested=256 if native_logging else 1,mode_transition_sequences_tested=512 if native_logging else 0,descriptor_initial_bytes_compared=87 if native_logging else 0,ticks_report_sha256=sha(ticks_report) if real_ticks else None,critical_report_sha256=sha(critical_report) if real_critical else None,integer_runtime_report_sha256=sha(integer_report) if real_division else None,state_initializer_bytes_compared=80,port_table_bytes_compared=12,scope='Native port and cached device clients, actual registry/memory, repeated start/open/feed, typed 10-second priority-6 config and SDK adapter error handling'+('; actual Nordic WDT state and MMIO/core writes execute' if actual_sdk else ''),limitations=[(('ADC error logger is intercepted; Nordic WDT, integer division, critical-region and tick C bodies execute.' if real_ticks else 'Tick getter and ADC error logger are intercepted; Nordic WDT, integer division and critical-region C bodies execute.' if real_critical else 'Critical-region helpers, tick getter and ADC error logger are intercepted; Nordic WDT and integer division C bodies execute.' if real_division else '64-bit division, critical-region helpers, tick getter and ADC error logger are intercepted; Nordic WDT bodies execute.') if actual_sdk else 'Final nrfx WDT calls, tick getter and ADC error logger are intercepted.'),('All 256 R1 mode bytes and 512 short-circuit mode transitions are tested; structured formatter and returning ADC error logger remain intercepted.' if native_logging else 'SDK MMIO cases use R1 logging mode zero; original gated SDK log routing remains outside this contract.'),'Handler pointer relocation is normalized; no original executable providers are linked into the candidate.','Physical watchdog expiry/reset, live timing, whole-image source completeness and original instruction identity remain open.'],instruction_identity_proven=False),indent=2)+'\n');print(f'{comparisons} native watchdog device/port comparisons passed (actual SDK: {actual_sdk})')
if __name__=='__main__':main()
