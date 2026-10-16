#!/usr/bin/env python3
"""Power shutdown/continuation contracts with real iterator and exclusive swap."""
import hashlib,itertools,json,struct,subprocess,tempfile,sys,re
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
FIELDS={'r1_sdk_power_pwr_mgmt_evt':(0x200079b0,1),'r1_sdk_power_shutdown_started':(0x200079b1,1),'r1_sdk_power_sysoff_mtx':(0x200079b4,4),'r1_sdk_power_handlers_iter':(0x2002c4a8,12)}
EVENT=0x200079b0;STARTED=EVENT+1;LOCK=EVENT+4;ITER=0x2002c4a8;SET=0x20004000;RANGES=0x20004100;HANDLERS=0x20004200

def main():
 real_panic='--real-panic' in sys.argv;real_dfu='--real-dfu' in sys.argv or real_panic;out=BASE/'sdk-power-management';rp=out/'report.json';r=json.loads(rp.read_text());obj=out/'power-management.o';receipt=(BASE/'sdk-logger-frontend/power-integration-verification.json') if real_panic else (BASE/'sdk-dfu-state/power-integration-verification.json') if real_dfu else out/'verification.json';receipt.unlink(missing_ok=True);assert sha(obj)==r['selected_object_sha256']
 for p,d in r['inputs'].items():assert sha(ROOT/p)==d,p
 ip=BASE/'sdk-ble-dispatch/report.json';ir=json.loads(ip.read_text());io=BASE/'sdk-ble-dispatch/nrf_section_iter.o';assert sha(io)==next(x['object_sha256'] for x in ir['units'] if x['source'].endswith('/nrf_section_iter.c'))
 dp=BASE/'sdk-dfu-state/report.json';do=BASE/'sdk-dfu-state/dfu-state.o'
 if real_dfu:
  dr=json.loads(dp.read_text());assert sha(do)==dr['selected_object_sha256']
  for p,d in dr['inputs'].items():assert sha(ROOT/p)==d,p
 logger_report=BASE/'sdk-logger-frontend/report.json';logger_object=BASE/'sdk-logger-frontend/logger.o'
 if real_panic:
  logger=json.loads(logger_report.read_text());assert sha(logger_object)==logger['selected_object_sha256']
  for p,d in logger['inputs'].items():assert sha(ROOT/p)==d,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';ep=out/'evidence.json';e=json.loads(ep.read_text());assert e['application_sha256']==sha(app)
 for row in e['functions']:
  p=out/row['ghidra_file'];assert sha(p)==row['ghidra_sha256'];a=int(row['entry'],16);assert bytes(json.loads(p.read_text())['data'])==app.read_bytes()[a-0x27000:a-0x27000+row['body_bytes']]
 states={};comparisons=0;callback_calls=0;terminals={};svcs=0;forced=0;dfu_cases=0;panic_backend_calls=0
 with tempfile.TemporaryDirectory() as directory:
  t=Path(directory);ld=t/'layout.ld';elf=t/'test.elf';binary=t/'text.bin';ld.write_text('SECTIONS { '+('.bss.r1_sdk_logger_data 0x2002d60c (NOLOAD) : { *(.bss.r1_sdk_logger_data) } ' if real_panic else '')+''.join('.bss.'+n+' '+hex(a)+' (NOLOAD) : { *(.bss.'+n+') } ' for n,(a,z) in FIELDS.items())+'.text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } /DISCARD/ : { *(.comment) *(.note*) } }')
  bindings={'nrf_log_panic':0x100ee01,'nrf_log_frontend_dequeue':0x100ee11,'nrf_sdh_is_enabled':0x100ee21,'r1_reset_trace_capture_site_adapter':0x100ee31,'r1_structured_log_mode_get':0x100ee41,'r1_structured_log_format':0x100ee51}
  if real_panic:bindings.pop('nrf_log_panic')
  subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--entry=nrf_pwr_mgmt_shutdown','--gc-sections','--undefined=r1_sdk_power_shutdown_process','--undefined=nrf_section_iter_init',*(['--undefined=r1_sdh_state_observer_567ac'] if real_dfu else []),*['--defsym='+n+'='+hex(a) for n,a in bindings.items()],str(obj),str(io),*([str(do)] if real_dfu else []),*([str(logger_object)] if real_panic else []),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True);syms={x.split()[-1]:int(x.split()[0],16) for x in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x.split())==3}
  from verify_sdk_atfifo import REGS
  def stores(path,extra=()):
   result={}
   for line in subprocess.check_output(['arm-none-eabi-objdump','-d',*extra,str(path)],text=True).splitlines():
    m=re.search(r'^\s*([0-9a-f]+):.*\bstrex\s+(r\d+|ip|lr),',line)
    if m:result[int(m[1],16)]=REGS[m[2]]
   return result
  candidate_stores=stores(elf);native_stores=stores(BASE/'i2c5/stock-analysis-exec.elf',('--start-address=0x27380','--stop-address=0x27398'));assert candidate_stores and native_stores
  stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
  for u in (stock,candidate):u.mem_map(0x20000,0xc0000);u.mem_map(0x1000000,0x10000);u.mem_map(0x20000000,0x40000);u.mem_map(0x40000000,4096);u.mem_map(0xe000e000,4096)
  stock.mem_write(0x27000,app.read_bytes());candidate.mem_write(0x1000000,binary.read_bytes());stock.reg_write(UC_ARM_REG_SP,0x2003f000);stock.emu_start(0x283a1,0x27208,count=2000000);assert stock.reg_read(UC_ARM_REG_PC)==0x27208
  for n,(a,z) in FIELDS.items():assert syms[n]==a and bytes(stock.mem_read(a,z))==bytes(candidate.mem_read(a,z))==bytes(z)
  def ret(u,v=0):u.reg_write(UC_ARM_REG_R0,v&0xffffffff);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  def read32(u,a):return struct.unpack('<I',bytes(u.mem_read(a,4)))[0]
  def snapshot(u):return bytes(u.mem_read(EVENT,8)),bytes(u.mem_read(ITER,12))
  def string(u,a):
   data=bytearray()
   for i in range(256):
    v=u.mem_read(a+i,1)[0]
    if not v:return data.decode()
    data.append(v)
   raise AssertionError('unterminated')
  def hook(u,a,size,user):
   nonlocal callback_calls,forced,panic_backend_calls
   f=states[id(u)];r0=u.reg_read(UC_ARM_REG_R0);mapping=native_stores if u is stock else candidate_stores
   if a in mapping and f['remaining']:
    f['remaining']-=1;f['injections']+=1;forced+=1;u.mem_write(LOCK,struct.pack('<I',f['lock_mutation']));u.reg_write(mapping[a],1);u.reg_write(UC_ARM_REG_PC,(a+4)|1);return
   if real_panic and a==0x100ec00:
    panic_backend_calls+=1;f['trace'].append(('panic_backend',r0,u.mem_read(0x2002d60c,1)[0],bytes(u.mem_read(0x20002400+(r0-0x20002000)//32*16,16))));ret(u);return
   if a in (0x8f234,syms['r1_sdk_power_shutdown_process']):f['process_caller']=u.reg_read(UC_ARM_REG_LR)
   if 0x100ed00<=a<0x100ed40 and (a-0x100ed00)%16==0:
    i=(a-0x100ed00)//16;idx=f['handler_indices'][i];f['handler_indices'][i]+=1;script=f['handler_scripts'][i];value=script[min(idx,len(script)-1)];f['trace'].append(('handler',i,r0,value,snapshot(u)));callback_calls+=1
    if f['mutate_handler'] and i==0:u.mem_write(EVENT,b'\x03')
    ret(u,value);return
   if a in (0x914ec,0x100ee40):
    i=f['mode_index'];f['mode_index']+=1;value=f['modes'][min(i,len(f['modes'])-1)];f['trace'].append(('mode',value,snapshot(u)))
    if f['mutate_mode'] and i==1:u.mem_write(EVENT,b'\x02')
    ret(u,value)
   elif a in (0x91638,0x100ee50):
    fmt=string(u,u.reg_read(UC_ARM_REG_R2));f['trace'].append(('log',r0,string(u,u.reg_read(UC_ARM_REG_R1)),fmt,u.reg_read(UC_ARM_REG_R3) if '%' in fmt else None));ret(u)
   elif not real_panic and a in (0x79b1c,0x100ee00):f['trace'].append(('panic',snapshot(u)));ret(u)
   elif a in (0x796a8,0x100ee10):
    i=f['dequeue_index'];f['dequeue_index']+=1;value=f['dequeue'][min(i,len(f['dequeue'])-1)];f['trace'].append(('dequeue',value));ret(u,value)
   elif a in (0x7a4d8,0x100ee20):f['trace'].append(('sd_enabled',f['enabled']));ret(u,f['enabled'])
   elif a in (0x58a9a,0x100ee30):assert r0==f['process_caller'],(hex(r0),hex(f['process_caller']));f['trace'].append(('reset_capture','process caller'));ret(u)
  def write(u,access,a,size,value,user):
   if not (0x40000000<=a<0x40001000 or 0xe000e000<=a<0xe000f000):return
   f=states[id(u)];f['trace'].append(('mmio',a,size,value))
   if a==0x40000500 or (a==0xe000ed0c and value&4):f['terminal']='off' if a==0x40000500 else 'reset';u.emu_stop()
  def svc(u,number,user):
   nonlocal svcs
   pc=u.reg_read(UC_ARM_REG_PC);assert bytes(u.mem_read(pc-2,2))==b'\x33\xdf';f=states[id(u)];f['trace'].append(('svc51',f['svc_status']));svcs+=1;u.reg_write(UC_ARM_REG_R0,f['svc_status'])
  from unicorn import UC_HOOK_INTR
  for u in (stock,candidate):u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_WRITE,write);u.hook_add(UC_HOOK_INTR,svc)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  def run(u,actions,started=0,event=0,lock=0,handlers=(),mask=0,enabled=0,modes=(0,),dequeue=(0,),svc_status=0,mutate_handler=False,mutate_mode=False,failures=0,lock_mutation=0):
   states[id(u)]=dict(trace=[],terminal=None,handler_scripts=[*handlers,*([(1,)]*(4-len(handlers)))],handler_indices=[0]*4,mode_index=0,modes=modes,dequeue=dequeue,dequeue_index=0,enabled=enabled,svc_status=svc_status,mutate_handler=mutate_handler,mutate_mode=mutate_mode,remaining=failures,injections=0,lock_mutation=lock_mutation);f=states[id(u)];u.mem_write(EVENT,bytes([event,started,0xa7,0xb8])+struct.pack('<I',lock));u.mem_write(ITER,bytes(12));u.mem_write(SET,struct.pack('<3I',RANGES,RANGES+16,4));split=min(len(handlers),2)
   for i,(first,last) in enumerate(((HANDLERS,HANDLERS+split*4),(HANDLERS+split*4,HANDLERS+len(handlers)*4))):u.mem_write(RANGES+i*8,struct.pack('<2I',first,first if mask&(1<<i) else last))
   u.mem_write(HANDLERS,struct.pack('<4I',*[0x100ed01+i*16 for i in range(4)]));u.mem_write(0x40000000,bytes(4096));u.mem_write(0xe000e000,bytes(4096));u.mem_write(0xe000ed0c,struct.pack('<I',0x12345700));results=[]
   if real_panic:
    u.mem_write(0x2002d60c,bytes(4128));u.mem_write(0x2002e61c,struct.pack('<I',0x20002000));u.mem_write(0x20002500,struct.pack('<3I',0x100ec01,0x100ec01,0x100ec01))
    for i in range(2):u.mem_write(0x20002000+i*32,struct.pack('<4I',0x20002500,0,0,0x20002400+i*16));u.mem_write(0x20002400+i*16,struct.pack('<I4B',0x20002020 if i==0 else 0,i,0,0xa7,0xb8)+b'\xc9'*8)
   for action in [('iter',),*actions]:
    name=action[0];arg=action[1] if len(action)>1 else 0;entry={'iter':0x7a53c,'api':0x79d50,'process':0x8f234,'dfu':0x567ac}[name] if u is stock else syms[{'iter':'nrf_section_iter_init','api':'nrf_pwr_mgmt_shutdown','process':'r1_sdk_power_shutdown_process','dfu':'r1_sdh_state_observer_567ac'}[name]]
    u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101);u.reg_write(UC_ARM_REG_R0,ITER if name=='iter' else arg);u.reg_write(UC_ARM_REG_R1,SET)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    u.emu_start(entry|1,0x20000100,count=200000)
    if not f['terminal']:assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)],(name,hex(u.reg_read(UC_ARM_REG_PC)))
    results.append((name,snapshot(u),f['terminal'],bytes(u.mem_read(0x2002d60c,4128)) if real_panic else None,bytes(u.mem_read(0x20002400,32)) if real_panic else None))
    if f['terminal']:break
   assert f['injections']==failures and f['remaining']==0
   return results,f['trace'],bytes(u.mem_read(0x40000000,4096)),bytes(u.mem_read(0xe000e000,4096))
  def compare(actions,**kwargs):
   nonlocal comparisons
   a=run(stock,actions,**kwargs);b=run(candidate,actions,**kwargs);assert a==b,(actions,kwargs,a,b);comparisons+=1
   if a[0][-1][2]:kind=a[0][-1][2];terminals[kind]=terminals.get(kind,0)+1
  for event,started,lock,modes in itertools.product(range(5),(0,1),(0,1,2,0xffffffff),((0,),(1,),(2,),(4,),(7,),(0,4,1))):compare([('api',event)],started=started,event=1,lock=lock,handlers=((0,),),modes=modes)
  scripts=((),((1,),),((0,1),),((1,),(0,1)),((1,),(1,),(1,)),((0,),(1,),(0,),(1,)))
  for event,handlers,mask,enabled,modes,dequeue in itertools.product(range(4),scripts,range(4),(0,1),((0,),(1,),(0,4,2)),((0,),(1,1,0))):compare([('api',event),('api',4),('api',4)],handlers=handlers,mask=mask,enabled=enabled,modes=modes,dequeue=dequeue)
  for event,enabled,status in itertools.product(range(4),(0,1),(0,1,0xffffffff)):compare([('process',)],started=1,event=event,enabled=enabled,svc_status=status)
  for modes in ((0,),(1,),(4,),(0,4,1)):compare([('api',0)],handlers=((1,),(1,)),mutate_handler=True,modes=modes);compare([('api',0)],handlers=((0,),),mutate_mode=True,modes=modes)
  for failures,mutation,initial in itertools.product((1,2),(0,0x12345678),(0,1)):compare([('api',0)],handlers=((0,),),lock=initial,failures=failures,lock_mutation=mutation)
  if real_dfu:
   for state,started,lock,handlers,enabled,modes in itertools.product(range(4),(0,1),(0,1,0xffffffff),((),((0,1),),((1,),(0,1))),(0,1),((0,),(1,),(0,4,1))):compare([('dfu',state)]+([('api',4)] if state==3 else []),started=started,lock=lock,handlers=handlers,enabled=enabled,modes=modes);dfu_cases+=1
 receipt.write_text(json.dumps(dict(application_sha256=sha(app),report_sha256=sha(rp),native_evidence_sha256=sha(ep),dfu_report_sha256=sha(dp) if real_dfu else None,actual_sdk_dfu_callback_executed=real_dfu,dfu_callback_workflows=dfu_cases,actual_logger_panic=real_panic,logger_report_sha256=sha(logger_report) if real_panic else None,panic_backend_callbacks_per_implementation=panic_backend_calls//2,forced_exclusive_failures_per_implementation=forced//2,iterator_report_sha256=sha(ip),comparisons=comparisons,callback_invocations_per_implementation=callback_calls//2,terminal_cases=terminals,svc51_calls_per_implementation=svcs//2,source_owned_cold_zero_bytes=sum(z for a,z in FIELDS.values()),scope='Actual pinned shutdown API/process, exclusive atomic swap and legacy iterator; locking, repeated/blocking handlers, continuation cursor, native logging modes, reset callsite and terminal register/SVC ordering',limitations=[('Actual logger panic/enable traversal executes; application panic callbacks, dequeue, shutdown callbacks, SDH replies and reset capture remain fixtures.' if real_panic else 'Shutdown callbacks, logging backend/dequeue, SDH replies and reset capture are fixtures. Physical off/reset effects are stopped at the terminal register write.'),'Canonical bool/short-enum ABI, bounded logger queues and handlers only; exception races and physical power/retention behavior remain unproven.','Synthetic handler ranges do not establish production table/startup allocation. Original compiler/image identity and full linking remain open.'],instruction_identity_proven=False),indent=2)+'\n');print(comparisons,'power comparisons;',terminals,'terminal cases')
if __name__=='__main__':main()
