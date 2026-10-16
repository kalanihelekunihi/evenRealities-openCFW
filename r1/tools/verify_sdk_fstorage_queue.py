#!/usr/bin/env python3
"""Fstorage workflows with actual pinned FIFO/atomic/facade code and controlled SVC/SDH."""
import hashlib,itertools,json,struct,subprocess,tempfile,sys
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_INTR
from unicorn.arm_const import *
from verify_sdk_fstorage_sd import FIELDS,API,OBSERVERS
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();FS=0x20002000;SRC=0x20003000;DST=0x20004000;FLAGS=0x2002c494;FIFO=0x2002c3f8;BUFFER=0x2002c408

def main():
 real_clock='--real-clock' in sys.argv;via_soc='--via-soc' in sys.argv or real_clock;out=BASE/('sdk-clock' if real_clock else 'sdk-soc' if via_soc else 'sdk-atfifo');receipt=out/('fstorage-integration-verification.json');receipt.unlink(missing_ok=True);provider_reports={};objects=[]
 for name,objname,field in [('sdk-atfifo','atfifo-atomic.o','selected_object_sha256'),('sdk-fstorage-sd','fstorage-sd.o',None),('sdk-fstorage','fstorage.o',None),('runtime','memory-runtime.o','relocatable_sha256')]:
  rp=BASE/name/'report.json';r=json.loads(rp.read_text());obj=BASE/name/objname;assert sha(obj)==(r[field] if field else r['units'][0]['object_sha256']);provider_reports[name+'/report.json']=sha(rp);objects.append(obj)
  for p,d in r.get('inputs',{}).items():assert sha(ROOT/p)==d,p
 soc_bindings={};soc_sections={}
 if via_soc:
  from verify_sdk_soc import BOUNDARIES,SECTIONS
  soc_bindings={**BOUNDARIES,'r1_adc_error':0x100ee01,'r1_soc_observer_907fc':0x907fd,'ble_dfu_buttonless_on_sys_evt':0x52279};soc_sections=SECTIONS
  sp=BASE/'sdk-soc/report.json';sr=json.loads(sp.read_text());so=BASE/'sdk-soc/soc.o';assert sha(so)==sr['selected_object_sha256'];objects.append(so);provider_reports['sdk-soc/report.json']=sha(sp)
  for p,d in sr['inputs'].items():assert sha(ROOT/p)==d,p
  ip=BASE/'sdk-ble-dispatch/report.json';ir=json.loads(ip.read_text());io=BASE/'sdk-ble-dispatch/nrf_section_iter.o';assert sha(io)==next(x['object_sha256'] for x in ir['units'] if x['source'].endswith('/nrf_section_iter.c'));objects.append(io);provider_reports['sdk-ble-dispatch/report.json']=sha(ip)
 if real_clock:
  cp=BASE/'sdk-clock/report.json';cr=json.loads(cp.read_text());co=BASE/'sdk-clock/clock.o';assert sha(co)==cr['selected_object_sha256'];objects.append(co);provider_reports['sdk-clock/report.json']=sha(cp);soc_bindings.pop('r1_soc_observer_907fc')
  for p,d in cr['inputs'].items():assert sha(ROOT/p)==d,p
  soc_bindings.update(app_util_critical_region_enter=0x100eb01,app_util_critical_region_exit=0x100eb11,nrfx_clock_init=0x100eb21,nrfx_clock_enable=0x100eb31,nrfx_clock_lfclk_start=0x100eb41,nrfx_clock_lfclk_stop=0x100eb51,r1_structured_log_mode_get=0x100eb61,r1_structured_log_format=0x100eb71,nrf_strerror_get=0x100eb81)
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';states={};workflows=0;actions_count=0;svc_count=0;events=0;soc_svc_count=0
 with tempfile.TemporaryDirectory() as directory:
  t=Path(directory);ld=t/'layout.ld';elf=t/'test.elf';binary=t/'text.bin';ld.write_text('SECTIONS { '+('.bss.r1_sdk_clock_control 0x2002c154 (NOLOAD) : { *(.bss.r1_sdk_clock_control) } ' if real_clock else '')+(''.join(n+' '+hex(a)+' : { *('+n+') } ' for n,a in soc_sections.items())+'.sdh_soc_observers0 0xc45d8 : { *(.sdh_soc_observers0) } ' if via_soc else '')+''.join('.bss.'+n+' '+hex(a)+' (NOLOAD) : { *(.bss.'+n+') } ' for n,(a,z) in FIELDS.items())+'.r1.fstorage_sd.fifo_pointer 0x9c85c : { *(.r1.fstorage_sd.fifo_pointer) } .rodata.r1_sdk_fstorage_sd_flash_info 0x9c860 : { *(.rodata.r1_sdk_fstorage_sd_flash_info) } .rodata.nrf_fstorage_sd 0x9c86c : { *(.rodata.nrf_fstorage_sd) } .text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } /DISCARD/ : { *(.comment) *(.note*) } }')
  subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--entry=nrf_fstorage_init',*['--defsym='+n+'='+hex(a) for n,a in soc_bindings.items()],'--defsym=nrf_sdh_is_enabled=0x100e001','--defsym=nrf_sdh_request_continue=0x100e011','--defsym=__start_fs_data=0x20007dc0','--defsym=__stop_fs_data=0x20007de8',*map(str,objects),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True)
  syms={x.split()[-1]:int(x.split()[0],16) for x in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x.split())==3}
  stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
  for u in (stock,candidate):u.mem_map(0x20000,0xc0000);u.mem_map(0x1000000,0x10000);u.mem_map(0x20000000,0x40000)
  stock.mem_write(0x27000,app.read_bytes());candidate.mem_write(0x1000000,binary.read_bytes())
  for section,address in (('.r1.fstorage_sd.fifo_pointer',0x9c85c),('.rodata.r1_sdk_fstorage_sd_flash_info',0x9c860),('.rodata.nrf_fstorage_sd',0x9c86c))+tuple(soc_sections.items())+((('.sdh_soc_observers0',0xc45d8),) if via_soc else ()):
   p=t/(str(address)+'.bin');subprocess.run(['arm-none-eabi-objcopy','--dump-section',section+'='+str(p),str(elf)],check=True);candidate.mem_write(address,p.read_bytes())
  def ret(u,value):u.reg_write(UC_ARM_REG_R0,value);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  def hook(u,address,size,user):
   nonlocal events
   f=states[id(u)]
   if via_soc and (address==0x52278 or (address==0x907fc and not real_clock)):f['trace'].append(('soc_observer',address,u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1)));ret(u,0);return
   if real_clock and address==0x100eb90:f['trace'].append(('clock_ready',u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(0x2002c154,20))));ret(u,0);return
   if real_clock and address in (0x100eb00,0x100eb10,0x100eb20,0x100eb30,0x100eb40,0x100eb50,0x100eb60,0x100eb70,0x100eb80):raise AssertionError(('unexpected clock hardware/log/critical fixture call',hex(address)))
   if via_soc and address in (0x4e5bc,0x100ee00):raise AssertionError('unexpected SOC error')
   if address in (0x7a4d8,0x100e000):f['trace'].append(('sd_enabled',));ret(u,f['enabled'])
   elif address in (0x7a4e4,0x100e010):f['trace'].append(('continue',bytes(u.mem_read(FLAGS,20))));ret(u,0xffffffff)
   elif address==0x100ef00:events+=1;f['trace'].append(('event',bytes(u.mem_read(u.reg_read(UC_ARM_REG_R0),24)),bytes(u.mem_read(FLAGS,20)),bytes(u.mem_read(FIFO,16))));ret(u,0xffffffff)
  def svc(u,number,user):
   nonlocal svc_count,soc_svc_count
   pc=u.reg_read(UC_ARM_REG_PC);op=bytes(u.mem_read(pc-2,2))
   if via_soc and op==b'\x4b\xdf':
    f=states[id(u)];items=f['soc_items'];status,event=items.pop(0) if items else (5,0);soc_svc_count+=1;f['trace'].append(('svc75',status,event if status==0 else None))
    if status==0:u.mem_write(u.reg_read(UC_ARM_REG_R0),struct.pack('<I',event))
    u.reg_write(UC_ARM_REG_R0,status);return
   assert op[1]==0xdf and op[0] in (40,41);f=states[id(u)];a=[u.reg_read(reg) for reg in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2)];f['trace'].append(('svc',op[0],a if op[0]==41 else a[:1],bytes(u.mem_read(FLAGS,20)),bytes(u.mem_read(FIFO,16))));i=f['svc_index'];f['svc_index']+=1;svc_count+=1;u.reg_write(UC_ARM_REG_R0,f['statuses'][min(i,len(f['statuses'])-1)])
  for u in (stock,candidate):u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_INTR,svc)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  def run(u,actions,enabled,statuses):
   for a,z in FIELDS.values():u.mem_write(a,bytes(z))
   if real_clock:
    u.mem_write(0x2002c154,struct.pack('<3Bx4I',1,0,0,2,0x20006000,0,0))
    for i in range(3):u.mem_write(0x20006000+i*8,struct.pack('<2I',0x20006000+(i+1)*8 if i<2 else 0,0x100eb91))
   u.mem_write(FS,struct.pack('<5I',0,0,0x100ef01,0xd4000,0xf8000));u.mem_write(SRC,bytes((i*37+19)&255 for i in range(1024)));u.mem_write(DST,bytes([0xa7])*1024);f=dict(trace=[],enabled=enabled,statuses=statuses,svc_index=0);states[id(u)]=f;results=[]
   for action in actions:
    name=action[0];n=action[1] if len(action)>1 else 4
    if name=='init':entry=0x78c78;symbol='nrf_fstorage_init';args=(FS,0x9c86c,0)
    elif name=='write':entry=0x78dac;symbol='nrf_fstorage_write';args=(FS,0xd4000,SRC,n)
    elif name=='erase':entry=0x78c4c;symbol='nrf_fstorage_erase';args=(FS,0xd4000,n,0x12345678)
    elif name=='busy':entry=0x78c80;symbol='nrf_fstorage_is_busy';args=(FS,)
    elif name=='event':
     entry=0x7a500 if via_soc else 0x78d08;symbol='r1_sdk_soc_events_poll' if via_soc else 'nrf_fstorage_sys_evt_handler';args=(n,0);f['soc_items']=[(0,n),(5,0)]
    elif name=='req':entry=0x78cd0;symbol='nrf_fstorage_sdh_req_handler';args=(n,0)
    elif name=='state':entry=0x78ce8;symbol='nrf_fstorage_sdh_state_handler';args=(n,0)
    elif name=='uninit':entry=0x93ec4;symbol='r1_sdk_fstorage_sd_uninit';args=(FS,0)
    else:raise AssertionError(name)
    u.reg_write(UC_ARM_REG_SP,0x2003f000);u.mem_write(0x2003f000,struct.pack('<I',0x12345678));u.reg_write(UC_ARM_REG_LR,0x20000101)
    for reg,v in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),args):u.reg_write(reg,v)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    u.emu_start((entry if u is stock else syms[symbol])|1,0x20000100,count=200000)
    assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)],(action,enabled,statuses,hex(u.reg_read(UC_ARM_REG_PC)))
    value=None if name in ('event','state') else u.reg_read(UC_ARM_REG_R0)
    results.append((name,value,bytes(u.mem_read(FLAGS,20)),bytes(u.mem_read(FIFO,16)),bytes(u.mem_read(BUFFER,140)),bytes(u.mem_read(0x200079a8,8)),bytes(u.mem_read(FS,20)),bytes(u.mem_read(0x2002c154,20)) if real_clock else None,bytes(u.mem_read(0x20006000,24)) if real_clock else None))
   return results,f['trace']
  def compare(actions,enabled=1,statuses=(0,)):
   nonlocal workflows,actions_count
   a=run(stock,actions,enabled,statuses);b=run(candidate,actions,enabled,statuses);assert a==b,(actions,enabled,statuses,a,b);workflows+=1;actions_count+=len(actions);return a
  for enabled,opcode,n,statuses in itertools.product((0,1),('write','erase'),(1,4,4097),((0,),(17,0),(3,),(0xffffffff,))):
   if opcode=='erase' and not enabled and 0 in statuses and n>4:continue
   sequence=[('init',),(opcode,n),('busy',)]
   if enabled or statuses[0]==17:sequence += [('event',2)]*5+[('busy',)]
   compare(sequence,enabled=enabled,statuses=statuses)
  for cycles in range(1,10):
   sequence=[('init',)]
   for i in range(cycles):sequence += [('write',4)]*5+[('busy',)]+[('event',2)]*4+[('busy',)]
   result=compare(sequence);writes=[value for name,value,*rest in result[0] if name=='write'];assert writes==[0,0,0,0,4]*cycles
  for n in (1,3,4,4095,4096,4097,8192,8193):compare([('init',),('write',n)]+[('event',2)]*4+[('busy',)])
  compare([('init',),('write',4)]+[('event',3)]*9+[('busy',)])
  for state in (1,3):compare([('init',),('write',4),('req',0),('write',8),('event',2),('busy',),('state',state),('event',2),('busy',)])
  compare([('init',),('req',0),('state',3),('write',4),('busy',)])
  compare([('init',),('write',4),('init',),('event',2),('uninit',),('init',),('write',8),('event',2),('busy',)])
  compare([('init',),('event',0),('event',0xffffffff),('busy',)])
 if real_clock:
  for n in (1,4,4097):compare([('init',),('write',n),('event',0),('busy',),('event',0),('event',2),('busy',)])
 receipt.write_text(json.dumps(dict(application_sha256=sha(app),provider_reports=provider_reports,workflows=workflows,actions=actions_count,svc_calls_per_implementation=svc_count//2,soc_svc_calls_per_implementation=soc_svc_count//2,via_actual_soc_poll=via_soc,via_actual_clock_observer=real_clock,event_callbacks_per_implementation=events//2,scope=('Actual clock SOC observer with queued notification callbacks. ' if real_clock else '')+('Via actual pinned SOC poll and legacy iterator. ' if via_soc else '')+'Actual pinned FIFO/exclusive/atomic/facade/SoftDevice fstorage code, queue-full status, repeated ring wrap/drain, chunking, busy retry, fatal/timeout event results, pause/resume, repeated init/uninit and FIFO state/event order after each action',limitations=[('SDH enable/continue, DFU SOC observer, application callbacks and flash/SOC SVC replies are fixtures; clock SOC code executes, nrfx/critical/log dependencies are fail-on-call boundaries in this harness.' if real_clock else 'SDH enable/continue, clock/DFU SOC observers, application callback and flash/SOC SVC replies are fixtures.' if via_soc else 'Only SDH enable/continue, application callbacks and flash SVC replies are fixtures; no physical persistence or actual interrupt scheduling is proven.'),'Serialized valid bounded workflows; reentrant/multicore behavior and nonterminating huge/zero-page synchronous erases remain gates.','Full image, original compiler/link identity and hardware remain unproven.'],instruction_identity_proven=False),indent=2)+'\n');print(workflows,'real FIFO fstorage workflows passed;',actions_count,'actions;',svc_count//2,'SVC calls')
if __name__=='__main__':main()
