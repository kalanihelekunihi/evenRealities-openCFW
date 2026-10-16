#!/usr/bin/env python3
"""Native RTC device bodies, cold record and complete request writes."""
import hashlib,itertools,json,random,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ENTRIES={'r1_native_rtc_snapshot':0x5639c,'r1_native_rtc_calendar_write':0x563f8,'r1_native_rtc_callback_bind':0x56444,'r1_native_memory_move':0x2775c};COUNTER=0x2000737c;RECORD=COUNTER+8;INPUT=0x20003000;OUTPUT=0x20003100

def main():
 out=BASE/'native-rtc-device';rp=out/'report.json';r=json.loads(rp.read_text());objects=[out/'rtc-device.o',BASE/'runtime/memory-runtime.o',BASE/'runtime-memmove/memmove.o'];reports={n+'/report.json':sha(BASE/n/'report.json') for n in ('native-rtc-device','runtime','runtime-memmove')}
 assert sha(objects[0])==r['selected_object_sha256'] and sha(objects[1])==json.loads((BASE/'runtime/report.json').read_text())['relocatable_sha256']
 assert sha(objects[2])==json.loads((BASE/'runtime-memmove/report.json').read_text())['units'][0]['object_sha256']
 for p,d in r['inputs'].items():assert sha(ROOT/p)==d,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';count=0
 with tempfile.TemporaryDirectory() as directory:
  t=Path(directory);ld=t/'layout.ld';elf=t/'test.elf';binary=t/'text.bin';ld.write_text('SECTIONS { .r1.rtc.counter 0x2000737c (NOLOAD) : { *(.r1.rtc.counter) } .r1.rtc.record 0x20007384 : { *(.r1.rtc.record) } .r1.rtc.name 0xc07a0 : { *(.r1.rtc.name) } .text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } /DISCARD/ : { *(.comment) *(.note*) } }');subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--gc-sections',*['--undefined='+n for n in ENTRIES],*map(str,objects),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True);syms={x.split()[-1]:int(x.split()[0],16) for x in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x.split())==3}
  stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
  for u in (stock,candidate):u.mem_map(0x20000,0xc0000);u.mem_map(0x1000000,0x10000);u.mem_map(0x20000000,0x40000)
  stock.mem_write(0x27000,app.read_bytes());candidate.mem_write(0x1000000,binary.read_bytes());stock.reg_write(UC_ARM_REG_SP,0x2003f000);stock.emu_start(0x283a1,0x27208,count=2000000);assert stock.reg_read(UC_ARM_REG_PC)==0x27208
  assert bytes(stock.mem_read(COUNTER,8))==bytes(candidate.mem_read(COUNTER,8))==bytes(8)
  for section,a,z in [('.r1.rtc.record',RECORD,88),('.r1.rtc.name',0xc07a0,8)]:
   p=t/(section+'.bin');subprocess.run(['arm-none-eabi-objcopy','--dump-section',section+'='+str(p),str(elf)],check=True);data=p.read_bytes();assert len(data)==z and data==bytes(stock.mem_read(a,z));candidate.mem_write(a,data)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  def compare(name,args,state,record,input_bytes):
   nonlocal count
   results=[]
   for u in (stock,candidate):
    u.mem_write(COUNTER,state);u.mem_write(RECORD,record+bytes([0x6d])*88);u.mem_write(INPUT,input_bytes+bytes(128-len(input_bytes)));u.mem_write(OUTPUT,bytes([0xa7])*96);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
    for reg,v in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),args):u.reg_write(reg,v)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    u.emu_start((ENTRIES[name] if u is stock else syms[name])|1,0x20000100,count=10000);assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(v) for v in saved]==[0x12345600+i for i in range(8)]
    results.append((u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(COUNTER,184)),bytes(u.mem_read(INPUT,128)),bytes(u.mem_read(OUTPUT,96))))
   assert results[0]==results[1],(name,args,state.hex(),results);count+=1
  rng=random.Random(0x5639c);record=struct.pack('<I',0xc07a0)+bytes(rng.randrange(256) for _ in range(84))
  for epoch,divider,offset,null in itertools.product([0,1,4294967,4294968,0x7fffffff,0xffffffff]+[rng.randrange(2**32) for _ in range(100)],(0,1,7,8,65535),(0,480,65535),(False,True)):
   compare('r1_native_rtc_snapshot',(0xffffffff,0x87654321,0 if null else OUTPUT,0xabcdef01),struct.pack('<HHI',offset,divider,epoch),record,b'')
  for match,opened,callback in itertools.product((False,True),(0,1,255),(0,1,0x12345679,0xffffffff)):
   rec=bytearray(record);rec[4]=opened;data=struct.pack('<I',INPUT+16)+(bytes(12))+((b'sys rtc' if match else b'sys rtc2')+b'\0');compare('r1_native_rtc_callback_bind',(INPUT,0xabcdef01,callback,0xffffffff),bytes([0x97])*8,bytes(rec),data)
  for match,source,n in itertools.product((False,True),(INPUT+32,RECORD+4,RECORD+8,RECORD+12),range(40)):
   data=struct.pack('<I',INPUT+16)+bytes(12)+((b'sys rtc\0' if match else b'other\0')+bytes(8));data=data[:32].ljust(32,b'\0')+bytes(rng.randrange(256) for _ in range(44));compare('r1_native_rtc_calendar_write',(INPUT,source,0xffffffff,0x12345678),bytes([0x97])*8,record,data)
  for alignment,shift,length in itertools.product(range(4),(-16,-3,-1,0,1,3,16),range(65)):
   data=bytes(rng.randrange(256) for _ in range(128));src=INPUT+32+alignment;compare('r1_native_memory_move',(src+shift,src,length),bytes([0x97])*8,record,data)
 (out/'verification.json').write_text(json.dumps(dict(application_sha256=sha(app),report_sha256=sha(rp),provider_reports=reports,provider_objects={str(p.relative_to(BASE)):sha(p) for p in objects},comparisons=count,cold_zero_bytes=8,cold_record_bytes=88,name_bytes=8,direct_memmove_comparisons=1820,scope='Native snapshot/calendar-write/callback-bind, actual source memmove/strcmp, complete request/record and canary comparison, overlapping memmove and second-record non-scanning',limitations=['RTC open/tick/epoch initialization and registry registration are not yet admitted; interrupt concurrency and physical timing remain unproven.','Unchecked invalid pointer fault details and full firmware linking/byte identity remain unproven.']),indent=2)+'\n');print(count,'RTC device comparisons; 104 cold bytes')
if __name__=='__main__':main()
