#!/usr/bin/env python3
"""Native RTC device bodies, cold record and complete request writes."""
import argparse,hashlib,itertools,json,random,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ENTRIES={'r1_native_rtc_gmtime':0x276c8,'r1_native_rtc_epoch_to_calendar':0x562e0,'r1_native_rtc_tick':0x56274,'r1_native_rtc_epoch_initialize':0x5649c,'r1_native_rtc_open':0x56318,'r1_native_rtc_register':0x563c4};COUNTER=0x2000737c;RECORD=COUNTER+8;INPUT=0x20003000;OUTPUT=0x20003100

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--real-driver',action='store_true');opts=parser.parse_args()
 out=BASE/'native-rtc-lifecycle';rp=out/'report.json';r=json.loads(rp.read_text());objects=[out/'rtc-lifecycle.o',BASE/'native-rtc-device/rtc-device.o',BASE/'runtime/memory-runtime.o',BASE/'runtime-memmove/memmove.o',BASE/'i2c5/stock_registry.o'];reports={n+'/report.json':sha(BASE/n/'report.json') for n in ('native-rtc-lifecycle','native-rtc-device','runtime','runtime-memmove','i2c5')}
 if opts.real_driver:
  objects.append(BASE/'native-rtc-error/rtc-error.o');reports['native-rtc-error/report.json']=sha(BASE/'native-rtc-error/report.json');assert sha(objects[-1])==json.loads((BASE/'native-rtc-error/report.json').read_text())['selected_object_sha256']
  objects.append(BASE/'sdk-nrfx-rtc/nrfx-rtc.o');reports['sdk-nrfx-rtc/report.json']=sha(BASE/'sdk-nrfx-rtc/report.json');assert sha(objects[-1])==json.loads((BASE/'sdk-nrfx-rtc/report.json').read_text())['selected_object_sha256']
 assert sha(objects[0])==r['selected_object_sha256'] and sha(objects[2])==json.loads((BASE/'runtime/report.json').read_text())['relocatable_sha256']
 assert sha(objects[3])==json.loads((BASE/'runtime-memmove/report.json').read_text())['units'][0]['object_sha256']
 for p,d in r['inputs'].items():assert sha(ROOT/p)==d,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';count=0
 with tempfile.TemporaryDirectory() as directory:
  t=Path(directory);ld=t/'layout.ld';elf=t/'test.elf';binary=t/'text.bin';ld.write_text('SECTIONS { .r1.rtc.error.ring 0x4e604 : { *(.r1.rtc.error.ring) } .r1.rtc.error.nordic 0x4e630 : { *(.r1.rtc.error.nordic) } .bss.r1_sdk_rtc_control 0x20007950 (NOLOAD) : { *(.bss.r1_sdk_rtc_control) } .bss.r1_sdk_rtc_handlers 0x20007954 (NOLOAD) : { *(.bss.r1_sdk_rtc_handlers) } .r1.rtc.log.enabled 0x7ad5c : { *(.r1.rtc.log.enabled) } .r1.rtc.log.tick 0x7ae90 : { *(.r1.rtc.log.tick) } .r1.rtc.log.function 0x7ae28 : { *(.r1.rtc.log.function) } .r1.registry.head 0x20007680 (NOLOAD) : { *(.r1.registry.head) } .r1.rtc.ops 0x200073dc : { *(.r1.rtc.ops) } .r1.rtc.defaults 0x9a638 : { *(.r1.rtc.defaults) } .r1.rtc.tm 0x20037e88 (NOLOAD) : { *(.r1.rtc.tm) } .r1.rtc.months 0xbdb18 : { *(.r1.rtc.months) } .r1.rtc.counter 0x2000737c (NOLOAD) : { *(.r1.rtc.counter) } .r1.rtc.record 0x20007384 : { *(.r1.rtc.record) } .r1.rtc.name 0xc07a0 : { *(.r1.rtc.name) } .text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } /DISCARD/ : { *(.comment) *(.note*) } }');subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--gc-sections',*['--undefined='+n for n in [*ENTRIES,'r1_rtc_boot_defaults','r1_rtc_device_ops']],*['--defsym='+n+'='+hex(a) for n,a in {'r1_rtc_driver_initialize':0x100ee01,'r1_rtc_driver_tick_enable':0x100ee11,'r1_rtc_driver_enable':0x100ee21,'r1_rtc_driver_error':0x100ee31}.items() if not opts.real_driver],*(['--defsym=r1_structured_log_mode_get=0x100ed01','--defsym=r1_structured_log_format=0x100ed11','--defsym=nrf_strerror_get=0x100ed21','--defsym=nrf_log_frontend_std_1=0x100ed31'] if opts.real_driver else []),*map(str,objects),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True);syms={x.split()[-1]:int(x.split()[0],16) for x in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x.split())==3}
  stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
  for u in (stock,candidate):u.mem_map(0x20000,0xc0000);u.mem_map(0x1000000,0x10000);u.mem_map(0x20000000,0x40000)
  if opts.real_driver:
   for u in (stock,candidate):u.mem_map(0x40024000,4096);u.mem_map(0xe000e000,4096)
  stock.mem_write(0x27000,app.read_bytes());candidate.mem_write(0x1000000,binary.read_bytes());stock.reg_write(UC_ARM_REG_SP,0x2003f000);stock.emu_start(0x283a1,0x27208,count=2000000);assert stock.reg_read(UC_ARM_REG_PC)==0x27208
  assert bytes(stock.mem_read(COUNTER,8))==bytes(candidate.mem_read(COUNTER,8))==bytes(8)
  for section,a,z in [('.r1.rtc.record',RECORD,88),('.r1.rtc.name',0xc07a0,8),('.r1.rtc.months',0xbdb18,12),('.r1.rtc.defaults',0x9a638,8)]:
   p=t/(section+'.bin');subprocess.run(['arm-none-eabi-objcopy','--dump-section',section+'='+str(p),str(elf)],check=True);data=p.read_bytes();assert len(data)==z and data==bytes(stock.mem_read(a,z));candidate.mem_write(a,data)
  ops=t/'ops.bin';subprocess.run(['arm-none-eabi-objcopy','--dump-section','.r1.rtc.ops='+str(ops),str(elf)],check=True);payload=ops.read_bytes();assert len(payload)==36
  for index,native,name in [(2,0x56318,'r1_native_rtc_open'),(4,0x5639c,'r1_native_rtc_snapshot'),(5,0x5649c,'r1_native_rtc_epoch_initialize'),(7,0x563f8,'r1_native_rtc_calendar_write'),(8,0x56444,'r1_native_rtc_callback_bind')]:assert struct.unpack_from('<I',payload,index*4)[0]==syms[name]|1 and struct.unpack('<I',bytes(stock.mem_read(0x200073dc+index*4,4)))[0]==native|1
  for index in (0,1,3,6):assert struct.unpack_from('<I',payload,index*4)[0]==0 and bytes(stock.mem_read(0x200073dc+index*4,4))==bytes(4)
  candidate.mem_write(0x200073dc,payload)
  traces={};callback_count=0;driver_status=0;driver_calls=0
  def hook(u,a,size,user):
   nonlocal callback_count,driver_calls
   if opts.real_driver and a in (0x914ec,0x100ed00):traces[id(u)].append(('mode',0));u.reg_write(UC_ARM_REG_R0,0);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR));return
   if opts.real_driver and a in (0x100ed10,0x100ed20,0x100ed30):raise AssertionError('mode-zero log sink called')
   real_kinds={syms['nrfx_rtc_init']&~1:'init',syms['nrfx_rtc_tick_enable']&~1:'tick-enable',syms['nrfx_rtc_enable']&~1:'enable',syms['r1_rtc_driver_error']&~1:'error'} if opts.real_driver else {}
   kind={**real_kinds,0x7ad6c:'init',0x7ae4c:'tick-enable',0x7ad20:'enable',0x4e5bc:'error',0x100ee00:'init',0x100ee10:'tick-enable',0x100ee20:'enable',0x100ee30:'error'}.get(a)
   if kind:
    driver_calls+=1;args=[u.reg_read(reg) for reg in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2)]
    if kind=='init':
     assert args[0]==RECORD+52 and args[2]==((0x56274 if u is stock else syms['r1_native_rtc_tick'])|1);traces[id(u)].append(('init',args[0],bytes(u.mem_read(args[1],8))))
     if not opts.real_driver:u.reg_write(UC_ARM_REG_R0,driver_status)
    elif kind=='error':traces[id(u)].append(('error',args[0]))
    else:
     assert args[0]==RECORD+52;traces[id(u)].append((kind,args[0],args[1] if kind=='tick-enable' else None))
    if not opts.real_driver:u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
    return
   if a!=0x100ef00:return
   traces[id(u)].append((u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(COUNTER,8))));callback_count+=1;u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  for u in (stock,candidate):u.hook_add(UC_HOOK_CODE,hook)
  assert bytes(stock.mem_read(0x20037e88,32))==bytes(candidate.mem_read(0x20037e88,32))==bytes(32)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  def compare(name,args,state,record,input_bytes,head=0):
   nonlocal count
   results=[]
   for u in (stock,candidate):
    if opts.real_driver:u.mem_write(0x20007950,bytes([1 if driver_status else 0])+bytes(7));u.mem_write(0x40024000,bytes(4096));u.mem_write(0xe000e000,bytes(4096))
    traces[id(u)]=[];u.mem_write(0x20007680,struct.pack('<I',head));u.mem_write(0x20037e88,bytes([0x9b])*32);u.mem_write(COUNTER,state);u.mem_write(RECORD,record+bytes([0x6d])*88);u.mem_write(INPUT,input_bytes+bytes(128-len(input_bytes)));u.mem_write(OUTPUT,bytes([0xa7])*96);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
    for reg,v in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),args):u.reg_write(reg,v)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    u.emu_start((ENTRIES[name] if u is stock else syms[name])|1,0x20000100,count=10000);assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(v) for v in saved]==[0x12345600+i for i in range(8)]
    extra=()
    if opts.real_driver:
     sdk=bytearray(u.mem_read(0x20007950,8));handler=struct.unpack_from('<I',sdk,4)[0]
     if handler:assert handler==((0x56274 if u is stock else syms['r1_native_rtc_tick'])|1);struct.pack_into('<I',sdk,4,0x56275)
     extra=(bytes(sdk),bytes(u.mem_read(0x40024000,4096)),bytes(u.mem_read(0xe000e000,4096)))
    results.append((extra,bytes(u.mem_read(0x20007680,4)),None if name=='r1_native_rtc_tick' else u.reg_read(UC_ARM_REG_R0),list(traces[id(u)]),bytes(u.mem_read(0x20037e88,32)),bytes(u.mem_read(COUNTER,184)),bytes(u.mem_read(INPUT,128)),bytes(u.mem_read(OUTPUT,96))))
   assert results[0]==results[1],(name,args,state.hex(),results);count+=1
  rng=random.Random(0x56274);record=struct.pack('<I',0xc07a0)+bytes(48)+struct.pack('<IbBBB',0x40024000,36,0,4,0)+bytes(28)
  epochs=[0,1,86399,86400,951782400,4107542399,4107542400,0x7fffffff,0x80000000,0xffffffff]+[rng.randrange(2**32) for _ in range(500)]
  for day in range(49711):compare('r1_native_rtc_gmtime',(INPUT,),bytes(8),record,struct.pack('<I',day*86400))
  for epoch in epochs:
   compare('r1_native_rtc_gmtime',(INPUT,),bytes(8),record,struct.pack('<I',epoch))
   compare('r1_native_rtc_epoch_to_calendar',(epoch,OUTPUT),bytes(8),record,b'')
  for divider,epoch,offset,match,callback in itertools.product((0,1,6,7,8,65535),(0,59,86399,1700000000,0xffffffff),(-32768,-720,0,480,32767),(False,True),(False,True)):
   rec=bytearray(record);local=(epoch+1+offset*60)&0xffffffff
   struct.pack_into('<2I',rec,8,(local%60 if match else 0xffffffff),(local//60)%60);struct.pack_into('<I',rec,60,0x100ef01 if callback else 0)
   compare('r1_native_rtc_tick',(0x12345678,),struct.pack('<hHI',offset,divider,epoch),bytes(rec),b'')
  for epoch,offset,match,opened,null in itertools.product((0,1,1700000000,0xffffffff),(-32768,-720,0,480,32767),(False,True),(0,1,255),(False,True)):
   rec=bytearray(record);rec[4]=opened;data=bytearray(128);struct.pack_into('<I',data,0,INPUT+80);struct.pack_into('<Ih',data,16+44,epoch,offset);name=b'sys rtc\0' if match else b'other\0';data[80:80+len(name)]=name
   compare('r1_native_rtc_epoch_initialize',(INPUT,0x87654321,0 if null else INPUT+16),bytes([0x97])*8,bytes(rec),bytes(data))
  for match,opened,driver_status in itertools.product((False,True),(0,1,255),(0,1,0x12345678)):
   rec=bytearray(record);rec[4]=opened;data=struct.pack('<I',INPUT+16)+bytes(12)+(b'sys rtc\0' if match else b'other\0');compare('r1_native_rtc_open',(INPUT,),bytes(8),bytes(rec),data)
  for mode in (0,1,2):
   data=bytearray(128);name=b'sys rtc\0' if mode==1 else b'other\0';data[80:80+len(name)]=name;struct.pack_into('<6I',data,96,INPUT+80,0x200073dc,0,0,0,0);compare('r1_native_rtc_register',(),bytes(8),record,bytes(data),head=INPUT+96 if mode else 0)
 (out/('real-driver-verification.json' if opts.real_driver else 'verification.json')).write_text(json.dumps(dict(application_sha256=sha(app),report_sha256=sha(rp),provider_reports=reports,provider_objects={str(p.relative_to(BASE)):sha(p) for p in objects},comparisons=count,cold_zero_bytes=8,cold_record_bytes=88,name_bytes=8,device_callbacks_per_implementation=callback_count//2,actual_sdk_driver=opts.real_driver,actual_native_error_logger=opts.real_driver,shared_breakdown_bytes=32,driver_calls_per_implementation=driver_calls//2,ops_bytes_pointer_normalized=36,config_bytes=8,scope='Native unsigned gmtime, epoch/calendar adapter, tick and epoch initialization with actual shared counter/record and memory; bounded alarm callback fixture',limitations=['Alarm and error callbacks remain bounded fixtures. Driver bridges are fixtures by default; --real-driver executes pinned SDK with mode-zero log fixtures. Registry calls execute actual source; physical timing, startup ordering and interrupt concurrency remain unproven.','Unchecked invalid pointer fault details and full firmware linking/byte identity remain unproven.']),indent=2)+'\n');print(count,'RTC lifecycle comparisons;',callback_count//2,'alarm callbacks')
if __name__=='__main__':main()
