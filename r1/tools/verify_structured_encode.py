#!/usr/bin/env python3
"""Compare compact log frames and argument consumption with stock Thumb."""
import hashlib,json,struct,subprocess,tempfile,sys
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_C1_C0_2,UC_ARM_REG_FPEXC
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 real_float='--real-float' in sys.argv
 receipt=BASE/('structured-encode/float-integration-verification.json' if real_float else 'structured-encode/verification.json');receipt.unlink(missing_ok=True);app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 report=json.loads((BASE/'structured-encode/report.json').read_text());obj=BASE/'structured-encode/structured_encode.o';assert sha(obj)==report['units'][0]['object_sha256']
 for path,digest in report['inputs'].items():assert sha(ROOT/path)==digest,path
 others=[BASE/'runtime/memory-runtime.o',BASE/'structured-log/structured_log.o',BASE/'board-seams/stock_seams.o'];providers={};comparisons=0
 for path,name,field in zip(others,('runtime/report.json','structured-log/report.json','board-seams/report.json'),('relocatable_sha256','object','object')):
  r=json.loads((BASE/name).read_text());expected=r['relocatable_sha256'] if field=='relocatable_sha256' else r['units'][0]['object_sha256'];assert sha(path)==expected;providers[name]=sha(BASE/name)
 if real_float:
  floating=json.loads((BASE/'structured-float/report.json').read_text());floating_object=BASE/'structured-float/structured_float.o';assert sha(floating_object)==floating['units'][0]['object_sha256'];others.append(floating_object);providers['structured-float/report.json']=sha(BASE/'structured-float/report.json')
 with tempfile.TemporaryDirectory() as directory:
  tmp=Path(directory);ld=tmp/'layout.ld';elf=tmp/'test.elf';binary=tmp/'test.bin'
  ld.write_text('SECTIONS { .text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } .r1.log.clock 0x2000653c (NOLOAD) : { *(.r1.log.clock) } .r1.log.mode 0x200068ec : { *(.r1.log.mode) } .r1.log.level 0x200068ed : { *(.r1.log.level) } .r1.log.sequence 0x200068ee (NOLOAD) : { *(.r1.log.sequence) } /DISCARD/ : { *(.comment) *(.note*) } }')
  names=('osKernelGetTickCount','r1_structured_log_timestamp_adapter','r1_structured_log_local_timestamp','r1_log_double_to_float_bits','r1_structured_log_cache_append')
  subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--gc-sections','--entry=r1_structured_log_encode_format',*['--defsym='+n+'='+hex(0x100e001+i*16) for i,n in enumerate(names) if not (real_float and n=='r1_log_double_to_float_bits')],str(obj),*map(str,others),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True)
  syms={x.split()[-1]:int(x.split()[0],16) for x in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x.split())==3}
  stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB);stock.mem_map(0x20000,0xc0000);stock.mem_write(0x27000,app.read_bytes());events={id(stock):[],id(candidate):[]};tick=[0]
  for uc in (stock,candidate):
   uc.mem_map(0x1000000,0x10000);uc.mem_map(0x20000000,0x40000);uc.reg_write(UC_ARM_REG_C1_C0_2,0xf<<20);uc.reg_write(UC_ARM_REG_FPEXC,0x40000000)
  candidate.mem_write(0x1000000,binary.read_bytes());seams={a:n for a,n in zip((0x7d28c,0x514bc,0x8ad40,0x27f6c,0x41e80),names)};seams.update({0x100e000+i*16:n for i,n in enumerate(names)})
  if real_float:
   del seams[0x27f6c];del seams[0x100e030]
  def hook(uc,address,size,user):
   if address not in seams:return
   name=seams[address];value=0
   if name=='osKernelGetTickCount':value=tick[0];events[id(uc)].append(('tick',))
   elif name=='r1_structured_log_timestamp_adapter':value=0x12345678;events[id(uc)].append(('timestamp','adapter'))
   elif name=='r1_structured_log_local_timestamp':value=0x87654321;events[id(uc)].append(('timestamp','local'))
   elif name=='r1_log_double_to_float_bits':
    low,high=uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1);events[id(uc)].append(('float_input',low,high));value=low^high
   else:
    length=uc.reg_read(UC_ARM_REG_R1);assert 12<=length<=44;events[id(uc)].append(('frame',bytes(uc.mem_read(uc.reg_read(UC_ARM_REG_R0),length))))
   uc.reg_write(UC_ARM_REG_R0,value);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  for uc in (stock,candidate):uc.hook_add(UC_HOOK_CODE,hook)
  def run(uc,entry,fmt,requested,alignment,mode,level,severity,seq,clock,ticks,null_string=False):
   events[id(uc)].clear();tick[0]=ticks;uc.mem_write(0x200068ec,bytes([mode,level,seq]));uc.mem_write(0x2000653c,bytes([clock]));uc.mem_write(0x20002000,fmt.encode()+b'\0')
   for i,length in enumerate((0,1,15,16,17,80)):uc.mem_write(0x20004000+i*256,bytes(65+i+(j%26) for j in range(length))+b'\0')
   words=[(0 if null_string else 0x20004000+(i%6)*256) if 's' in fmt else ((i*0x1234567+0x89abcdef)&0xffffffff) for i in range(64)]
   pointer=0x20003000+alignment;uc.mem_write(pointer,struct.pack('<64I',*words));uc.reg_write(UC_ARM_REG_R0,(severity<<26)|(requested<<22)|0x12345);uc.reg_write(UC_ARM_REG_R1,0x20002000);uc.reg_write(UC_ARM_REG_R2,pointer);uc.reg_write(UC_ARM_REG_SP,0x2003f000);uc.reg_write(UC_ARM_REG_LR,0x20000101)
   
   try:uc.emu_start(entry|1,0x20000100,count=100000)
   except Exception as error:raise AssertionError((hex(entry),fmt,hex(uc.reg_read(UC_ARM_REG_PC)),str(error)))
   assert uc.reg_read(UC_ARM_REG_PC)==0x20000100
   return list(events[id(uc)]),bytes(uc.mem_read(0x200068ec,3))
  formats=['','literal','%u','%d','%i','%x','%X','%o','%p','%c','%f','%F','%s','%%','%%%u','%08x','%-8u','%+8d','%#x','%.3u','%.*u','%lu','%llu','%hhu','%hu','%llf','%q','%llq','%--u','%*u','%','%.','%.*','%l','%ll','x%u/y%u','%u'*10,'%s%s%s','%u%u%u%u%u%s%u%u%u','%.*s']
  cases=[]
  for fmt in formats:
   for requested in (0,1,2,8,15):
    for alignment in (0,4):
     for ticks in (0,999,1000,0xffffffff):cases.append((fmt,requested,alignment,0,3,3,ticks&255,ticks&1,ticks,False))
  for mode in (0,1,4,5,7):
   for level in (0,3,7):
    for severity in range(8):cases.append(('%u',1,0,mode,level,severity,255,0,1000,False))
  for prefix in range(6):cases.append(('%u'*prefix+'%s',prefix+1,0,0,3,3,255,1,123,False))
  for requested in (1,2,8):cases.append(('%s%s',requested,0,0,3,3,255,1,123,True))
  for args in cases:
   a=run(stock,0x46fd4,*args);b=run(candidate,syms['r1_structured_log_encode_format'],*args);assert a==b,(args,a,b);comparisons+=1
 receipt.write_text(json.dumps(dict(application_sha256=sha(app),report_sha256=sha(BASE/'structured-encode/report.json'),object_sha256=sha(obj),provider_reports=providers,comparisons=comparisons,actual_float_conversion=real_float,scope='Original compact-frame bytes, sequence/filter behavior, printf-like scanning, integer widths, string suffix/zero fill, floating argument alignment and source time selection',limitations=[('Clock/time and final cache append are intercepted; actual float conversion is executed.' if real_float else 'Clock/time, double-to-float and final cache append are intercepted; float conversion and transport are not proven.'),'Invalid strings, format pointers and concurrent state mutations remain untested.','Whole instruction and firmware identity remain open.'],instruction_identity_proven=False),indent=2)+'\n');print(f'{comparisons} structured encoder comparisons passed')
if __name__=='__main__':main()
