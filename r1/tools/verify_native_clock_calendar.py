#!/usr/bin/env python3
"""Native default calendar ports and selected Gregorian conversion contracts."""
import hashlib,itertools,json,random,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ENTRIES={'r1_clock_backend_slot20':0x50d64,'r1_clock_backend_slot24':0x50d8a,'time_calendar_broken_down_to_unix':0x5a8ac,'time_calendar_to_utc':0x8ae58,'time_calendar_utc_to_calendar':0x8af40}
def main():
 out=BASE/'native-clock-calendar';rp=out/'report.json';r=json.loads(rp.read_text());objects=[out/'clock-calendar.o',BASE/'native-clock-port/clock-port.o',BASE/'native-log-calendar/log-calendar.o',BASE/'i2c5/stock_registry.o',BASE/'structured-time/structured_time.o',BASE/'runtime/memory-runtime.o'];reports={}
 for directory in ('native-clock-calendar','native-clock-port','native-log-calendar','i2c5','structured-time','runtime'):reports[directory+'/report.json']=sha(BASE/directory/'report.json')
 assert sha(objects[0])==r['selected_object_sha256']
 for p,d in r['inputs'].items():assert sha(ROOT/p)==d,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 count=0;callbacks=0
 with tempfile.TemporaryDirectory() as directory:
  t=Path(directory);ld=t/'layout.ld';elf=t/'test.elf';binary=t/'text.bin';ld.write_text('SECTIONS { .r1.time.rtc 0x20007690 (NOLOAD) : { *(.r1.time.rtc) } .r1.time.state 0x20016ac4 (NOLOAD) : { *(.r1.time.state) } .text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } /DISCARD/ : { *(.comment) *(.note*) } }');subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--gc-sections',*['--undefined='+n for n in ENTRIES],*map(str,objects),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True);syms={x.split()[-1]:int(x.split()[0],16) for x in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x.split())==3}
  stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB);traces={};epoch=0;status=0
  for u in (stock,candidate):u.mem_map(0x20000,0xc0000);u.mem_map(0x1000000,0x10000);u.mem_map(0x20000000,0x40000)
  stock.mem_write(0x27000,app.read_bytes());candidate.mem_write(0x1000000,binary.read_bytes())
  def hook(u,a,size,user):
   nonlocal callbacks
   if a not in (0x100ef00,0x100ef10):return
   args=[u.reg_read(v) for v in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)];assert args[:2]==[0x20002000,0] and args[3]==0;callbacks+=1
   traces[id(u)].append(('get' if a==0x100ef00 else 'set',bytes(u.mem_read(args[2],64))))
   if a==0x100ef00:u.mem_write(args[2]+44,struct.pack('<I',epoch))
   u.reg_write(UC_ARM_REG_R0,status);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  for u in (stock,candidate):u.hook_add(UC_HOOK_CODE,hook)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11];INPUT=0x20003000;OUTPUT=0x20003100
  def compare(name,args,input_bytes=b'',tz=0):
   nonlocal count
   results=[]
   for u in (stock,candidate):
    traces[id(u)]=[];u.mem_write(0x20007690,struct.pack('<I',0x20002000));u.mem_write(0x20002000,struct.pack('<6I',0,0x20002100,0,0,0,0));u.mem_write(0x20002100,struct.pack('<9I',0,0,0,0,0x100ef01,0x100ef11,0,0,0));u.mem_write(0x20016ac4,bytes([0x96])*32);u.mem_write(0x20016acc,struct.pack('<H',tz&65535));u.mem_write(INPUT,input_bytes+bytes(64-len(input_bytes)));u.mem_write(OUTPUT,bytes([0xa7])*32);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
    for reg,v in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),args):u.reg_write(reg,v&0xffffffff)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    u.emu_start((ENTRIES[name] if u is stock else syms[name])|1,0x20000100,count=100000);assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(v) for v in saved]==[0x12345600+i for i in range(8)]
    results.append((u.reg_read(UC_ARM_REG_R0),traces[id(u)],bytes(u.mem_read(OUTPUT,32)),bytes(u.mem_read(INPUT,64)),bytes(u.mem_read(0x20016ac4,32))))
   assert results[0]==results[1],(name,args,input_bytes.hex(),tz,results);count+=1
  rng=random.Random(0x8af40)
  for epoch,status,null in itertools.product([0,1,86399,86400,951782400,1700000000,0x7fffffff,0x80000000,0xffffffff]+[rng.randrange(2**32) for _ in range(100)],(0,1,0xffffffff),(False,True)):compare('r1_clock_backend_slot20',(0 if null else OUTPUT,))
  for epoch,offset,null in itertools.product([0,1,86399,951782400,0x7fffffff,0xffffffff]+[rng.randrange(2**32) for _ in range(100)],(0,480,-720,32767,-32768,0x12345678),(False,True)):compare('time_calendar_utc_to_calendar',(epoch,offset,0 if null else OUTPUT))
  for year,month,day,hour,minute,second in itertools.product((1969,1970,2000,2029,2030,65535),(0,1,2,12,13),(0,1,29,31,32),(0,23,24),(0,59,60),(0,59,60)):
   data=struct.pack('<H6B',year,month,day,hour,minute,second,255)
   for tz in (-720,0,480):
    compare('r1_clock_backend_slot24',(INPUT,),data,tz=tz);compare('time_calendar_to_utc',(INPUT,tz),data,tz=tz)
  for year,month,day in itertools.product(range(1970,2030),range(1,13),(1,28,29,30,31)):
   data=struct.pack('<H6B',year,month,day,23,59,59,255)
   compare('time_calendar_broken_down_to_unix',(INPUT,),struct.pack('<9I',59,59,23,day,month-1,year-1900,255,0,0))
   for tz in (-720,480):
    compare('time_calendar_to_utc',(INPUT,tz),data);compare('r1_clock_backend_slot24',(INPUT,),data,tz=tz)
  for n in range(1000):
   fields=[rng.choice((0,1,23,59,60,0xffffffff)),rng.randrange(256),rng.randrange(256),rng.randrange(33),rng.randrange(14),rng.randrange(69,131),rng.randrange(256),0,0]
   compare('time_calendar_broken_down_to_unix',(INPUT,),struct.pack('<9I',*fields))
  for tz in (-32768,0,32767):compare('r1_clock_backend_slot24',(0,),tz=tz);compare('time_calendar_to_utc',(0,tz))
  compare('time_calendar_broken_down_to_unix',(0,))
 (out/'verification.json').write_text(json.dumps(dict(application_sha256=sha(app),report_sha256=sha(rp),provider_reports=reports,provider_objects={str(p.relative_to(BASE)):sha(p) for p in objects},comparisons=count,device_callbacks_per_implementation=callbacks//2,scope='Native calendar ports/converters with actual source Gregorian forward converter, registry, RTC requests and shared state; device operation fixtures',limitations=['Device operation bodies, startup ordering and hardware behavior remain unproven. Native standalone forward-converter pointer ABI is not promoted by its internal value-ABI use. No instruction identity or whole-image equality claim.']),indent=2)+'\n');print(count,'calendar port comparisons;',callbacks//2,'device callbacks')
if __name__=='__main__':main()
