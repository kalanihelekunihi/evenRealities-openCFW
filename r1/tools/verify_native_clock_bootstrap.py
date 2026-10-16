#!/usr/bin/env python3
"""Native snapshot/bootstrap/tick contracts, shared globals and typed default table."""
import argparse,hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();REG=0x20006820;STATE=0x20016ac4;OPS=0x20002000;CFG=0x20003000;OUT=CFG+32
ENTRIES={'r1_clock_initialize':0x8adc0,'r1_clock_backend_snapshot':0x5a990,'r1_clock_backend_bind':0x5a9b4,'r1_clock_second_changed':0x5a9d0,'r1_clock_default_backend_get':0x5a988}
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--real-ports',action='store_true');opts=parser.parse_args()
 out=BASE/'native-clock-bootstrap';rp=out/'report.json';r=json.loads(rp.read_text());receipt=out/('real-ports-verification.json' if opts.real_ports else 'verification.json');receipt.unlink(missing_ok=True);objects=[];reports={}
 for name,file,key in [('native-clock-bootstrap','clock-bootstrap.o','selected_object_sha256'),('structured-time','structured_time.o',None),('runtime','memory-runtime.o','relocatable_sha256')]:
  p=BASE/name/'report.json';q=json.loads(p.read_text());o=p.parent/file;assert sha(o)==(q[key] if key else q['units'][0]['object_sha256']);objects.append(o);reports[name+'/report.json']=sha(p)
 reg_report=BASE/'i2c5/report.json';registry=reg_report.parent/'stock_registry.o';assert sha(registry)==next(x['object_sha256'] for x in json.loads(reg_report.read_text())['units'] if x['source'].endswith('stock_registry.c'));objects.append(registry);reports['i2c5/report.json']=sha(reg_report)
 if opts.real_ports:
  for name,file in [('native-clock-port','clock-port.o'),('native-clock-calendar','clock-calendar.o'),('native-log-calendar','log-calendar.o')]:
   p=BASE/name/'report.json';q=json.loads(p.read_text());o=p.parent/file;assert sha(o)==q['selected_object_sha256'];objects.append(o);reports[name+'/report.json']=sha(p)
 for p,d in r['inputs'].items():assert sha(ROOT/p)==d,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';states={};comparisons=0;callbacks=0
 with tempfile.TemporaryDirectory() as directory:
  t=Path(directory);ld=t/'layout.ld';elf=t/'test.elf';binary=t/'text.bin';ld.write_text('SECTIONS { .r1.clock.backend 0x99c8c : { *(.r1.clock.backend) } .r1.clock.defaults 0x99c54 : { *(.r1.clock.defaults) } .r1.time.state 0x20016ac4 (NOLOAD) : { *(.r1.time.state) } .r1.time.registration 0x20006820 (NOLOAD) : { *(.r1.time.registration) } .r1.time.rtc 0x20007690 (NOLOAD) : { *(.r1.time.rtc) } .text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } /DISCARD/ : { *(.comment) *(.note*) } }');bindings={n:0x100ed01+i*16 for i,n in enumerate(('r1_clock_backend_slot12','r1_clock_backend_slot20','r1_clock_backend_slot24','r1_clock_backend_update','r1_clock_backend_bind_tick','r1_event_publish')) if not opts.real_ports or n=='r1_event_publish'};subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--gc-sections',*['--undefined='+n for n in ENTRIES],*['--defsym='+n+'='+hex(a) for n,a in bindings.items()],*map(str,objects),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True);syms={x.split()[-1]:int(x.split()[0],16) for x in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x.split())==3};assert syms['r1_clock_default_backend']==0x99c8c and syms['r1_clock_boot_defaults']==0x99c54
  stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
  for u in (stock,candidate):u.mem_map(0x20000,0xc0000);u.mem_map(0x1000000,0x10000);u.mem_map(0x20000000,0x40000)
  stock.mem_write(0x27000,app.read_bytes());candidate.mem_write(0x1000000,binary.read_bytes());stock.reg_write(UC_ARM_REG_SP,0x2003f000);stock.emu_start(0x283a1,0x27208,count=2000000);assert stock.reg_read(UC_ARM_REG_PC)==0x27208
  for a,z in [(REG,24),(STATE,32),(0x20007690,4)]:assert bytes(stock.mem_read(a,z))==bytes(candidate.mem_read(a,z))==bytes(z)
  for section,a,z in [('.r1.clock.backend',0x99c8c,32),('.r1.clock.defaults',0x99c54,8)]:
   p=t/(str(a)+'.bin');subprocess.run(['arm-none-eabi-objcopy','--dump-section',section+'='+str(p),str(elf)],check=True);data=p.read_bytes();assert len(data)==z
   if z==8:assert data==bytes(stock.mem_read(a,z))
   else:
    native=(0x50d86,0x50d60,0x50d7e,0x50d82,0x50db6,0x50d64,0x50d8a,0x50daa);names=('default_init','default_deinit','default_get','r1_clock_backend_slot12','r1_clock_backend_update','r1_clock_backend_slot20','r1_clock_backend_slot24','r1_clock_backend_bind_tick')
    for i,(v,n) in enumerate(zip(native,names)):assert struct.unpack_from('<I',data,i*4)[0]==syms[n]|1 and struct.unpack('<I',bytes(stock.mem_read(a+i*4,4)))[0]==v|1
   candidate.mem_write(a,data)
  kinds={0x50db6:'update',0x50daa:'bind',0x8d8fc:'publish',bindings.get('r1_clock_backend_update',0x100fe01)&~1:'update',bindings.get('r1_clock_backend_bind_tick',0x100fe11)&~1:'bind',bindings['r1_event_publish']&~1:'publish',0x100ef00:'rtc',0x100ef10:'init',0x100ef20:'get',0x100ef30:'update',0x100ef40:'bind'}
  if opts.real_ports:
   del kinds[0x50db6];del kinds[0x50daa]
  def hook(u,a,size,user):
   nonlocal callbacks
   kind=kinds.get(a)
   if not kind:return
   f=states[id(u)];args=[u.reg_read(reg) for reg in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)];callbacks+=1
   if kind=='rtc':assert args[:2]==[0x20004000,0] and args[3]==0;f['trace'].append(('rtc',bytes(u.mem_read(args[2],64))));u.mem_write(args[2]+44,struct.pack('<I',f['epoch']));value=0
   elif kind=='get':f['trace'].append(('get',args[0]));value=f['epoch']
   elif kind=='init':f['trace'].append(('init',args[0]));value=f['init_result']
   elif kind=='bind':assert args[:3]==[0,0,0] and args[3]==((0x5a9d0 if u is stock else syms['r1_clock_second_changed'])|1);f['trace'].append(('bind',));value=0
   elif kind=='publish':assert args[0]==4 and args[2]==1;f['trace'].append(('publish',struct.unpack('<I',bytes(u.mem_read(args[1],4)))[0]));value=0
   else:f['trace'].append(('update',args[:3]));value=0
   u.reg_write(UC_ARM_REG_R0,value);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  for u in (stock,candidate):u.hook_add(UC_HOOK_CODE,hook)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  def compare(name,args=(),flag=0,backend=0,context=0,registered=0,mask=7,init_result=1,epoch=1700000000,initial_epoch=0,offset=480,null_config=False):
   nonlocal comparisons
   results=[]
   for u in (stock,candidate):
    states[id(u)]={'trace':[],'init_result':init_result,'epoch':epoch};u.mem_write(REG,bytes([0xa7])*24);u.mem_write(REG+8,struct.pack('<I',backend));u.mem_write(REG+12,bytes([flag]));u.mem_write(REG+16,struct.pack('<2I',backend,context));u.mem_write(STATE,bytes([0x96])*32);u.mem_write(STATE+10,bytes([registered]));u.mem_write(STATE+4,struct.pack('<I',initial_epoch));u.mem_write(OPS,struct.pack('<8I',0x100ef11 if mask&1 else 0,0,0x100ef21 if mask&8 else 0,0,0x100ef31 if mask&2 else 0,0,0,0x100ef41 if mask&4 else 0));u.mem_write(CFG,struct.pack('<HHI',offset,0x1234,epoch));u.mem_write(OUT,bytes([0xb8])*16);u.mem_write(0x20007690,struct.pack('<I',0x20004000));u.mem_write(0x20004000,struct.pack('<6I',0,0x20004100,0,0,0,0));u.mem_write(0x20004100,struct.pack('<9I',0,0,0,0,0x100ef01,0,0,0,0))
    actual=(0 if null_config else CFG,context) if name=='r1_clock_initialize' else args;u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
    for reg,v in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),actual):u.reg_write(reg,v)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    u.emu_start((ENTRIES[name] if u is stock else syms[name])|1,0x20000100,count=100000);assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)],name;results.append((u.reg_read(UC_ARM_REG_R0) if name!='r1_clock_second_changed' else None,states[id(u)]['trace'],bytes(u.mem_read(REG,24)),bytes(u.mem_read(STATE,32)),bytes(u.mem_read(OUT,16))))
   assert results[0]==results[1],(name,args,flag,backend,registered,mask,offset,null_config,results);comparisons+=1
  for flag,backend,outs in itertools.product((0,1,2,255),(0,1,2,256,OPS,0x99c8c,0xffffffff),range(4)):compare('r1_clock_backend_snapshot',(OUT if outs&1 else 0,OUT+4 if outs&2 else 0),flag=flag,backend=backend,context=0x12345678)
  for pointer,mask in itertools.product((0,OPS,0x99c8c),range(16)):compare('r1_clock_backend_bind',(pointer,0x87654321),flag=255,backend=OPS,mask=mask)
  compare('r1_clock_default_backend_get')
  for registered,flag,backend,mask,init_result,context,cfg in itertools.product((0,1,255),(0,1),(0,OPS),range(16),(0,1),(0,0x12345678),((480,1700000000,False),(65535,0xffffffff,False),(0,0,True))):compare('r1_clock_initialize',registered=registered,flag=flag,backend=backend,mask=mask,init_result=init_result,context=context,offset=cfg[0],epoch=cfg[1],null_config=cfg[2])
  for backend,epoch,initial,payload in itertools.product((OPS,0x99c8c),(0,1,0xffffffff),(0,1),(0,1,0x87654321)):compare('r1_clock_second_changed',(payload,),backend=backend,mask=8,epoch=epoch,initial_epoch=initial)
 receipt.write_text(json.dumps(dict(application_sha256=sha(app),report_sha256=sha(rp),provider_reports=reports,comparisons=comparisons,callback_calls_per_implementation=callbacks//2,actual_calendar_and_rtc_request_ports=opts.real_ports,default_backend_bytes_pointer_normalized=32,default_config_bytes=8,shared_cold_zero_bytes=60,scope='Native snapshot/bind/bootstrap/default-table/tick ABI; actual registry timestamp adapter/thunk and memory code, default/custom backends, early return, callbacks and incoming-R1/payload quirks',limitations=['Native bootstrap/binder/default accessor/tick spans are supplemental and absent from ownership/pseudocode inventory. Missing Ghidra function boundary is preserved; Thumb and native differential execution provide their contracts.',('Default/calendar ports execute actual source bodies; underlying RTC operations are bounded fixtures or absent slots.' if opts.real_ports else 'Default-port update/control/unused slots and RTC device operations remain provider fixtures.')+' Registered backend faults, full RTC startup and real event transport are unproven.','Incoming R1 is the fallback callback context; tick publishes incoming R0 rather than getter result. No safer normalization is admitted. Whole-image startup/linking, physical behavior and byte equality remain unresolved.'],instruction_identity_proven=False),indent=2)+'\n');print(comparisons,'clock bootstrap comparisons;',callbacks//2,'callbacks')
if __name__=='__main__':main()
