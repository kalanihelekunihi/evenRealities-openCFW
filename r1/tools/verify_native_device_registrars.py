#!/usr/bin/env python3
"""GPIO-output/STACMD native registrars and attributable GPIO/delay providers."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
GPIO_POINTERS=[(280,'r1_output_gpio_low',0x54f42),(284,'r1_output_gpio_high',0x54f3c),(288,'r1_output_gpio_toggle',0x54f8a),(292,'r1_output_gpio_driver0c',0x54d92),(296,'r1_output_gpio_driver10',0x54d8c),(300,'r1_output_gpio_driver14',0x54ea8),(312,'r1_output_gpio_open',0x54d98),(316,'r1_output_gpio_close',0x54c58),(320,'r1_output_gpio_slot10',0x54e20),(328,'r1_output_gpio_slot18',0x54d20),(332,'r1_output_gpio_slot1c',0x54cd0)]
STACMD_POINTERS=[(16,'r1_twi_gpio_low',0x791e4),(20,'r1_twi_gpio_high',0x794ac),(24,'r1_twi_gpio_output',0x7910c),(28,'r1_twi_gpio_input',0x790aa),(36,'r1_stacmd_delay_us',0x7a6fc),(40,'r1_twi_gpio_read',0x79408),(44,'r1_twi_gpio_release',0x7902c),(80,'r1_stacmd_open',0x5657c),(84,'r1_stacmd_close',0x56568),(88,'r1_stacmd_read',0x56590),(92,'r1_stacmd_write',0x5660c)]
NAMES=[(0xc0754,'ppg_led_en'),(0xc0770,'touch_ldo_en'),(0xc0780,'ppg_reset_en'),(0xc0760,'ship_mode_en'),(0xc0790,'touch_rdy_out'),(0xc07c8,'device_stacmd')]
ENTRIES={'r1_native_output_gpio_registration':0x54e78,'r1_yhm2710_stacmd_binding_configuration':0x565f4}
def main():
 out=BASE/'native-output-gpio-registration';objects=[];reports={}
 for name,file in [('native-output-gpio-registration','output-gpio-registration.o'),('native-stacmd-registration','stacmd-registration.o'),('runtime','memory-runtime.o'),('native-rtt-delay','rtt-delay.o')]:
  p=BASE/name/'report.json';r=json.loads(p.read_text());o=p.parent/file;assert sha(o)==r.get('selected_object_sha256',r.get('relocatable_sha256'));objects.append(o);reports[name+'/report.json']=sha(p)
 gp=BASE/'software-twi/gpio-report.json';gr=json.loads(gp.read_text());go=Path(gr['units'][0]['command'][-1]);assert sha(go)==gr['units'][0]['object_sha256'];objects.append(go);reports['software-twi/gpio-report.json']=sha(gp)
 p=BASE/'i2c5/report.json';objects.append(p.parent/'stock_registry.o');reports['i2c5/report.json']=sha(p)
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';count=0;primitive_count=0
 with tempfile.TemporaryDirectory() as directory:
  t=Path(directory);ld=t/'layout.ld';elf=t/'test.elf';binary=t/'text.bin';sections=' .r1.output_gpio.configuration 0x20007228 : { *(.r1.output_gpio.configuration) } .r1.stacmd.configuration 0x200075c4 : { *(.r1.stacmd.configuration) } .r1.registry.head 0x20007680 (NOLOAD) : { *(.r1.registry.head) } '
  for i,(address,_) in enumerate(NAMES):section='.r1.output_gpio.name'+str(i) if i<5 else '.r1.stacmd.name';sections+=section+' '+hex(address)+' : { *('+section+') } '
  ld.write_text('SECTIONS { '+sections+'.text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } /DISCARD/ : { *(.comment) *(.note*) } }');unknown=[n for _,n,_ in GPIO_POINTERS]+[n for _,n,_ in STACMD_POINTERS if n.startswith('r1_stacmd_') and n!='r1_stacmd_delay_us'];bindings={n:0x100ed01+i*16 for i,n in enumerate(unknown)};roots=[*ENTRIES,*[n for _,n,_ in STACMD_POINTERS if n not in unknown]];subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--gc-sections',*['--undefined='+n for n in roots],*['--defsym='+n+'='+hex(a) for n,a in bindings.items()],*map(str,objects),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True);syms={x.split()[-1]:int(x.split()[0],16) for x in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x.split())==3}
  stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
  for u in (stock,candidate):u.mem_map(0x20000,0xc0000);u.mem_map(0x1000000,0x10000);u.mem_map(0x20000000,0x40000);u.mem_map(0x50000000,4096)
  stock.mem_write(0x27000,app.read_bytes());candidate.mem_write(0x1000000,binary.read_bytes());stock.reg_write(UC_ARM_REG_SP,0x2003f000);stock.emu_start(0x283a1,0x27208,count=2000000);assert stock.reg_read(UC_ARM_REG_PC)==0x27208
  for section,a,z in [('.r1.output_gpio.configuration',0x20007228,340),('.r1.stacmd.configuration',0x200075c4,108),*[(('.r1.output_gpio.name'+str(i)) if i<5 else '.r1.stacmd.name',a,len(n)+1) for i,(a,n) in enumerate(NAMES)]]:
   p=t/(section+'.bin');subprocess.run(['arm-none-eabi-objcopy','--dump-section',section+'='+str(p),str(elf)],check=True);data=p.read_bytes();assert len(data)==z;candidate.mem_write(a,data)
   if z<100:assert data==bytes(stock.mem_read(a,z))
  def normalized(u,address,length,pointers):
   data=bytearray(u.mem_read(address,length))
   for off,name,native in pointers:
    assert struct.unpack_from('<I',data,off)[0]==(native|1 if u is stock else syms[name]|1);struct.pack_into('<I',data,off,native|1)
   return bytes(data)
  for a,z,ptr in [(0x20007228,340,GPIO_POINTERS),(0x200075c4,108,STACMD_POINTERS)]:assert normalized(stock,a,z,ptr)==normalized(candidate,a,z,ptr)
  initial={id(u):{a:bytes(u.mem_read(a,z)) for a,z in [(0x20007228,340),(0x200075c4,108)]} for u in (stock,candidate)}
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  def run(u,entry,args):
   u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
   for reg,value in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2),args):u.reg_write(reg,value)
   for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
   u.emu_start(entry|1,0x20000100,count=200000);assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)];return u.reg_read(UC_ARM_REG_R0)
  for name in ENTRIES:
   gpio=name=='r1_native_output_gpio_registration';base,length,pointers,record_count,stride,device_offset=(0x20007228,340,GPIO_POINTERS,5,56,32) if gpio else (0x200075c4,108,STACMD_POINTERS,1,108,48)
   for mask,opened,other in itertools.product(range(1<<record_count),(0,1,255),(False,True)):
    for u in (stock,candidate):
     u.mem_write(base,initial[id(u)][base]);u.mem_write(base-16,bytes([0x6d])*16);u.mem_write(base+length,bytes([0x6d])*16);chain=[]
     for i in range(record_count):
      u.mem_write(base+i*stride+4,bytes([opened]));u.mem_write(base+i*stride+device_offset+20,struct.pack('<I',0x87654321))
      if mask&(1<<i):chain.append(NAMES[i if gpio else 5][0])
     if other:u.mem_write(0x20003000,b'other\0');chain.insert(0,0x20003000)
     u.mem_write(0x20007680,struct.pack('<I',0x20002000 if chain else 0));u.mem_write(0x20002000,bytes(192))
     for i,addr in enumerate(chain):u.mem_write(0x20002000+i*24,struct.pack('<6I',addr,1,0,0,0,0x20002000+(i+1)*24 if i+1<len(chain) else 0))
    for repeat in range(2):
     results=[]
     for u in (stock,candidate):value=run(u,ENTRIES[name] if u is stock else syms[name],());results.append((value,normalized(u,base,length,pointers),bytes(u.mem_read(0x20007680,4)),bytes(u.mem_read(0x20002000,192)),bytes(u.mem_read(base-16,16)),bytes(u.mem_read(base+length,16))))
     assert results[0]==results[1],(name,mask,opened,other,repeat,results);count+=1
  for _,name,native in STACMD_POINTERS:
   if name in bindings:continue
   if name=='r1_stacmd_delay_us':cases=[(v,0,0) for v in (0,1,2,4,15,0x04000000)]
   else:cases=itertools.product(range(48),(0,1,3) if name=='r1_twi_gpio_input' else (0,),(0,0xffffffff,0xa55a33cc))
   for value,pull,pattern in cases:
    results=[]
    for u in (stock,candidate):u.mem_write(0x50000000,struct.pack('<I',pattern)*1024);ret=run(u,native if u is stock else syms[name],(value,pull));results.append((ret if name=='r1_twi_gpio_read' else None,bytes(u.mem_read(0x50000000,4096))))
    assert results[0]==results[1],(name,value,pull,pattern,results);primitive_count+=1
 result=dict(application_sha256=sha(app),provider_reports=reports,provider_objects={str(p.relative_to(BASE)):sha(p) for p in objects},registrar_comparisons=count,primitive_comparisons=primitive_count,cold_configuration_bytes_pointer_normalized=448,name_bytes=sum(len(n)+1 for _,n in NAMES),scope='Actual registry/memory, GPIO-output and STACMD constructors, exact cold records, duplicate subsets/repeated calls; actual pinned GPIO primitives and native delay kernel',limitations=['Fifteen operation/driver symbols remain metadata-only; transfer and GPIO device operation ABIs are not admitted. Delay checks prove bounded execution/state, not elapsed physical timing. No complete initcall stage/boot proof.'])
 for directory in ('native-output-gpio-registration','native-stacmd-registration'):(BASE/directory/'verification.json').write_text(json.dumps(result,indent=2)+'\n')
 print(count,'registrar comparisons;',primitive_count,'primitive comparisons;',result['name_bytes'],'name bytes')
if __name__=='__main__':main()
