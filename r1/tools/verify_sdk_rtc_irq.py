#!/usr/bin/env python3
"""Native RTC IRQ, ordered W1C writes/callbacks, source-owned vector."""
import argparse,hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();RTC=0x40024000;HANDLERS=0x20007954
ENTRIES={'RTC2_IRQHandler':0x31750,'r1_sdk_rtc_irq_dispatch':0x7294c};OFFSETS=(0x140,0x144,0x148,0x14c,0x100,0x104);BITS=(1<<16,1<<17,1<<18,1<<19,1,2)
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--real-tick',action='store_true');opts=parser.parse_args()
 out=BASE/'sdk-nrfx-rtc';rp=out/'report.json';r=json.loads(rp.read_text());obj=out/'nrfx-rtc.o';assert sha(obj)==r['selected_object_sha256']
 for p,d in r['inputs'].items():assert sha(ROOT/p)==d,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';states={};count=0;callbacks=0
 objects=[obj];provider_reports={}
 if opts.real_tick:
  for name,file in [('native-rtc-lifecycle','rtc-lifecycle.o'),('native-rtc-device','rtc-device.o')]:
   report=BASE/name/'report.json';o=report.parent/file;assert sha(o)==json.loads(report.read_text())['selected_object_sha256'];objects.append(o);provider_reports[name+'/report.json']=sha(report)
 with tempfile.TemporaryDirectory() as directory:
  t=Path(directory);ld=t/'layout.ld';elf=t/'test.elf';binary=t/'text.bin';ld.write_text('SECTIONS { .r1.rtc.counter 0x2000737c (NOLOAD) : { *(.r1.rtc.counter) } .r1.rtc.record 0x20007384 : { *(.r1.rtc.record) } .r1.rtc.name 0xc07a0 : { *(.r1.rtc.name) } .r1.rtc.tm 0x20037e88 (NOLOAD) : { *(.r1.rtc.tm) } .r1.rtc.months 0xbdb18 : { *(.r1.rtc.months) } .r1.rtc.irq36.vector 0x270d0 : { *(.r1.rtc.irq36.vector) } .bss.r1_sdk_rtc_handlers 0x20007954 (NOLOAD) : { *(.bss.r1_sdk_rtc_handlers) } .text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } /DISCARD/ : { *(.comment) *(.note*) } }');subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--gc-sections',*['--undefined='+n for n in [*ENTRIES,'r1_rtc_irq36_vector',*(['r1_native_rtc_tick'] if opts.real_tick else [])]],*map(str,objects),'-o',str(elf)],check=True,capture_output=True);assert not subprocess.check_output(['arm-none-eabi-nm','-u',str(elf)],text=True).strip();subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True);syms={x.split()[-1]:int(x.split()[0],16) for x in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x.split())==3};assert syms['r1_sdk_rtc_handlers']==HANDLERS
  stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
  for u in (stock,candidate):u.mem_map(0x20000,0xc0000);u.mem_map(0x1000000,0x10000);u.mem_map(0x20000000,0x40000);u.mem_map(RTC,4096)
  stock.mem_write(0x27000,app.read_bytes());candidate.mem_write(0x1000000,binary.read_bytes());stock.reg_write(UC_ARM_REG_SP,0x2003f000);stock.emu_start(0x283a1,0x27208,count=2000000);assert stock.reg_read(UC_ARM_REG_PC)==0x27208;assert bytes(stock.mem_read(HANDLERS,4))==bytes(candidate.mem_read(HANDLERS,4))==bytes(4)
  v=t/'vector.bin';subprocess.run(['arm-none-eabi-objcopy','--dump-section','.r1.rtc.irq36.vector='+str(v),str(elf)],check=True);vector=v.read_bytes();assert len(vector)==4 and struct.unpack('<I',vector)[0]==syms['RTC2_IRQHandler']|1 and struct.unpack('<I',bytes(stock.mem_read(0x270d0,4)))[0]==0x31751;candidate.mem_write(0x270d0,vector)
  if opts.real_tick:
   for section,address in [('.r1.rtc.record',0x20007384),('.r1.rtc.name',0xc07a0),('.r1.rtc.months',0xbdb18)]:
    p=t/(section+'.bin');subprocess.run(['arm-none-eabi-objcopy','--dump-section',section+'='+str(p),str(elf)],check=True);data=p.read_bytes();assert data==bytes(stock.mem_read(address,len(data)));candidate.mem_write(address,data)
  def word(u,a):return struct.unpack('<I',bytes(u.mem_read(a,4)))[0]
  def write(u,access,a,size,value,user):
   if not RTC<=a<RTC+4096:return
   states[id(u)]['trace'].append(('write',a-RTC,size,value))
   if a in (RTC+0x308,RTC+0x348):u.mem_write(a-4,struct.pack('<I',word(u,a-4)&~value))
  def hook(u,a,size,user):
   nonlocal callbacks
   if opts.real_tick and a==((0x56274 if u is stock else syms['r1_native_rtc_tick'])&~1):states[id(u)]['trace'].append(('tick',u.reg_read(UC_ARM_REG_R0)));return
   if a not in (0x100ef00,0x100ef10):return
   f=states[id(u)];event=u.reg_read(UC_ARM_REG_R0);assert event<(24 if opts.real_tick else 6);f['trace'].append(('callback',(a-0x100ef00)//16,event,word(u,RTC+0x304),tuple(word(u,RTC+v) for v in OFFSETS)));callbacks+=1
   if f['calls']==0:
    if f['mutation']==1:u.mem_write(RTC+0x304,bytes(4))
    elif f['mutation']==2:
     u.mem_write(RTC+0x304,struct.pack('<I',sum(BITS)))
     for off in OFFSETS:u.mem_write(RTC+off,struct.pack('<I',1))
    elif f['mutation']==3:u.mem_write(HANDLERS,struct.pack('<I',0x100ef11))
   f['calls']+=1;u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  for u in (stock,candidate):u.hook_add(UC_HOOK_MEM_WRITE,write);u.hook_add(UC_HOOK_CODE,hook)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  for name,channels,enabled,pending,mutation in itertools.product(ENTRIES,(0,1,4),range(64),range(64),range(4)):
   if name=='RTC2_IRQHandler' and channels!=4:continue
   if opts.real_tick and (name!='RTC2_IRQHandler' or channels!=4):continue
   results=[]
   for u in (stock,candidate):
    states[id(u)]={'trace':[],'mutation':mutation,'calls':0};u.mem_write(RTC,bytes([0x97])*4096);u.mem_write(HANDLERS,struct.pack('<I',((0x56274 if u is stock else syms['r1_native_rtc_tick'])|1) if opts.real_tick else 0x100ef01));u.mem_write(RTC+0x304,struct.pack('<I',sum(bit for i,bit in enumerate(BITS) if enabled&(1<<i))));u.mem_write(RTC+0x344,struct.pack('<I',sum(BITS)))
    for i,off in enumerate(OFFSETS):u.mem_write(RTC+off,struct.pack('<I',0x80000001 if pending&(1<<i) else 0))
    if opts.real_tick:
     u.mem_write(0x2000737c,struct.pack('<hHI',0,7,1700000000));u.mem_write(0x20037e88,bytes([0x95])*32);u.mem_write(0x20007384+8,struct.pack('<2I',1700000001%60,(1700000001//60)%60));u.mem_write(0x20007384+60,struct.pack('<I',0x100ef01))
    u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
    for reg,value in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2),(RTC,0,channels)):u.reg_write(reg,value)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    u.emu_start((ENTRIES[name] if u is stock else syms[name])|1,0x20000100,count=100000);assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
    handler=word(u,HANDLERS);extra=()
    if opts.real_tick:
     if handler==((0x56274 if u is stock else syms['r1_native_rtc_tick'])|1):handler=0x56275
     extra=(bytes(u.mem_read(0x2000737c,96)),bytes(u.mem_read(0x20037e88,32)))
    results.append((extra,states[id(u)]['trace'],bytes(u.mem_read(RTC,4096)),handler))
   assert results[0]==results[1],(name,channels,enabled,pending,mutation,results);count+=1
 (out/('irq-real-tick-verification.json' if opts.real_tick else 'irq-verification.json')).write_text(json.dumps(dict(application_sha256=sha(app),report_sha256=sha(rp),comparisons=count,actual_native_tick=opts.real_tick,provider_reports=provider_reports,callbacks_per_implementation=callbacks//2,vector_bytes_pointer_normalized=4,scope=('Actual compiled native RTC tick/calendar and bounded alarm callbacks; ' if opts.real_tick else '')+'Actual pinned SDK IRQ wrapper and common dispatcher, all enabled/pending six-event masks, channel bounds 0/1/4, ordered MMIO writes and callbacks; callback disabling/enabling pending events and replacing handler',limitations=['W1C event/interrupt behavior is a controlled MMIO model. IRQ callbacks are fixtures by default; --real-tick executes actual native tick/calendar with alarm and handler-replacement fixtures. Physical interrupt delivery, concurrency, timing and whole-image equality remain unproven.','Original wrapper ownership extent162 is held as a boundary discrepancy; native wrapper bytes16 are supplemental.']),indent=2)+'\n');print(count,'RTC IRQ comparisons;',callbacks//2,'callbacks')
if __name__=='__main__':main()
