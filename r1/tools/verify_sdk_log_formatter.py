#!/usr/bin/env python3
"""Native formatter control/argument contracts with lower printf/calendar/color fixtures."""
import hashlib,itertools,json,re,struct,subprocess,tempfile,sys
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();PARAM=0x20002000;CTX=PARAM+32;ARGS=PARAM+128;STRING=0x20003000
ENTRIES={'nrf_log_std_entry_process':0x79b48,'nrf_log_hexdump_entry_process':0x79a44,'postfix_process':0x813e0,'r1_log_prefix_process':0x8185c}
def main():
 real_calendar='--real-calendar' in sys.argv
 real_modules='--real-modules' in sys.argv or real_calendar
 real_printf='--real-printf' in sys.argv or real_modules
 out=BASE/'sdk-log-formatter';rp=out/'report.json';r=json.loads(rp.read_text());obj=out/'log-formatter.o';receipt=out/('calendar-integration-verification.json' if real_calendar else 'modules-integration-verification.json' if real_modules else 'printf-integration-verification.json' if real_printf else 'verification.json');receipt.unlink(missing_ok=True);assert sha(obj)==r['selected_object_sha256']
 for p,d in r['inputs'].items():assert sha(ROOT/p)==d,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';states={};comparisons=0;printf_calls=0;output_bytes=0;output_callbacks=0;timestamp_callbacks=0
 with tempfile.TemporaryDirectory() as directory:
  extra=[];module_sections=''
  if real_calendar:
   for name,file,key in [('native-log-calendar','log-calendar.o','selected_object_sha256'),('structured-time','structured_time.o',None),('integer-runtime','integer-runtime.o','relocatable_sha256')]:
    p=BASE/name/'report.json';q=json.loads(p.read_text());o=p.parent/file;assert sha(o)==(q[key] if key else q['units'][0]['object_sha256']);extra.append(str(o))
   module_sections='.r1.time.state 0x20016ac4 (NOLOAD) : { *(.r1.time.state) } .r1.time.registration 0x20006820 (NOLOAD) : { *(.r1.time.registration) } '
  if real_modules:
   p=BASE/'sdk-log-modules/report.json';q=json.loads(p.read_text());o=p.parent/'log-modules.o';assert sha(o)==q['selected_object_sha256'];extra.append(str(o));cfg=json.loads((p.parent/'configuration-evidence.json').read_text());module_sections+='.r1.log.modules 0xc441c : { *(.r1.log.modules) } '+''.join('.r1.log.module_name.'+str(row['index'])+' '+row['name_address']+' : { *(.r1.log.module_name.'+str(row['index'])+') } ' for row in cfg['rows'])
  if real_printf:
   for name,file,key in [('sdk-fprintf','fprintf.o','selected_object_sha256'),('runtime','memory-runtime.o','relocatable_sha256')]:
    path=BASE/name/file;assert sha(path)==json.loads((BASE/name/'report.json').read_text())[key];extra.append(str(path))
  t=Path(directory);ld=t/'layout.ld';elf=t/'test.elf';ld.write_text('SECTIONS { '+module_sections+'.text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } /DISCARD/ : { *(.comment) *(.note*) } }');bindings={n:0x100ee01+i*16 for i,n in enumerate(('nrf_fprintf','nrf_fprintf_buffer_flush','nrf_log_color_id_get','r1_log_local_datetime_fill'))};subprocess.run(['arm-none-eabi-ld','-T',str(ld),*(['--gc-sections','--undefined=nrf_log_hexdump_entry_process','--undefined=postfix_process','--undefined=r1_log_prefix_process'] if real_calendar else []),'--entry=nrf_log_std_entry_process',*['--defsym='+n+'='+hex(a) for n,a in bindings.items() if (not real_printf or n not in ('nrf_fprintf','nrf_fprintf_buffer_flush')) and (not real_modules or n!='nrf_log_color_id_get') and (not real_calendar or n!='r1_log_local_datetime_fill')],str(obj),*extra,'-o',str(elf)],check=True,capture_output=True);syms={x.split()[-1]:int(x.split()[0],16) for x in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x.split())==3}
  stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
  for u in (stock,candidate):u.mem_map(0x20000,0xc0000);u.mem_map(0x1000000,0x10000);u.mem_map(0x20000000,0x40000)
  stock.mem_write(0x27000,app.read_bytes());stock.reg_write(UC_ARM_REG_SP,0x2003f000);stock.emu_start(0x283a1,0x27208,count=2000000);assert stock.reg_read(UC_ARM_REG_PC)==0x27208
  b=elf.read_bytes();off=struct.unpack_from('<I',b,32)[0];ss,n=struct.unpack_from('<HH',b,46)
  for i in range(n):
   _,typ,flags,a,p,z,*_=struct.unpack_from('<10I',b,off+i*ss)
   if flags&2 and typ!=8 and z:candidate.mem_write(a,b[p:p+z])
  def cstr(u,a):
   if not a:return None
   result=bytearray()
   for i in range(256):
    v=u.mem_read(a+i,1)[0]
    if not v:return result.decode('latin1')
    result.append(v)
   raise AssertionError('unterminated format')
  def context(u):raw=bytes(u.mem_read(CTX,24));return raw[:13],raw[16:]
  hooks={0x78a40:'printf',0x78a5a:'flush',0x7965c:'color',0x8ac28:'calendar',**{bindings[n]&~1:k for n,k in [('nrf_fprintf','printf'),('nrf_fprintf_buffer_flush','flush'),('nrf_log_color_id_get','color'),('r1_log_local_datetime_fill','calendar')]}}
  if real_calendar:hooks={a:k for a,k in hooks.items() if k!='calendar'}
  if real_modules:hooks={a:k for a,k in hooks.items() if k!='color'}
  if real_printf:hooks={a:k for a,k in hooks.items() if k not in ('printf','flush')}
  def hook(u,a,size,user):
   nonlocal printf_calls,output_bytes,output_callbacks,timestamp_callbacks
   if real_calendar and a==0x20000120:
    assert u.reg_read(UC_ARM_REG_R0)==0;timestamp_callbacks+=1;states[id(u)]['trace'].append(('timestamp',));u.reg_write(UC_ARM_REG_R0,1700000000);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR));return
   if real_printf and a in (0x78a40,syms['nrf_fprintf']&~1):printf_calls+=1;return
   if real_printf and a==0x20000110:
    n=u.reg_read(UC_ARM_REG_R2);p=u.reg_read(UC_ARM_REG_R1);output_bytes+=n;output_callbacks+=1;assert p==0x20004000 and 0<n<=128;states[id(u)]['trace'].append(('output',u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(p,n))));u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR));return
   kind=hooks.get(a)
   if not kind:return
   f=states[id(u)];args=[u.reg_read(reg) for reg in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)]
   if kind=='printf':
    assert args[0]==CTX;fmt=cstr(u,args[1]);specs=re.findall(r'%(?:[-+ #0]*\d*(?:\.\d+)?[hl]*)([sdxcu])',fmt);values=[]
    for i,spec in enumerate(specs):
     v=args[2+i] if i<2 else struct.unpack('<I',bytes(u.mem_read(u.reg_read(UC_ARM_REG_SP)+(i-2)*4,4)))[0];values.append(cstr(u,v) if spec=='s' else v)
    f['trace'].append(('printf',fmt,values,context(u),bytes(u.mem_read(0x20004000,256)) if real_printf else None));printf_calls+=1;u.mem_write(CTX+8,struct.pack('<I',struct.unpack('<I',bytes(u.mem_read(CTX+8,4)))[0]+1))
   elif kind=='flush':assert args[0]==CTX;f['trace'].append(('flush',context(u),bytes(u.mem_read(0x20004000,256)) if real_printf else None));u.mem_write(CTX+8,bytes(4))
   elif kind=='color':f['trace'].append(('color',args[:2]));u.reg_write(UC_ARM_REG_R0,f['color'])
   else:f['trace'].append(('calendar',));u.mem_write(args[0],f['datetime'])
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  for u in (stock,candidate):u.hook_add(UC_HOOK_CODE,hook)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  def compare(name,n=0,severity=3,dropped=0,colors=0,color=0,auto=0,value=65,datetime=b'\xe8\x07\x0a\x0f\x0c\x22\x38'):
   nonlocal comparisons
   if real_printf and severity==0 and name!='postfix_process':return
   results=[];fmt='message '+ '%08x '*n
   for u in (stock,candidate):
    if real_calendar:
     u.mem_write(0x20016ac4,bytes(32));u.mem_write(0x20016ace,b'\1');u.mem_write(0x20006820,bytes(20));u.mem_write(0x20006828,struct.pack('<I',0x20005000));u.mem_write(0x20005000,struct.pack('<5I',0,0,0x20000121,0,0))
    u.mem_write(0x20004000,bytes([0x96])*256);states[id(u)]={'trace':[],'datetime':datetime,'color':color};u.mem_write(PARAM,struct.pack('<IHHBBH',0xaabbccdd,28,dropped,severity,colors,0x9696));u.mem_write(CTX,struct.pack('<3IB3x2I',0x20004000,128,7,auto,0x20001000,0x20000111));u.mem_write(ARGS,struct.pack('<8I',*[0x12345670+i for i in range(8)]));u.mem_write(STRING,fmt.encode()+b'\0');u.mem_write(STRING+256,bytes([value])*16);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.mem_write(0x2003f000,struct.pack('<I',CTX));u.reg_write(UC_ARM_REG_LR,0x20000101)
    args={'nrf_log_std_entry_process':(STRING,ARGS,n,PARAM),'nrf_log_hexdump_entry_process':(STRING+256,n,PARAM,CTX),'postfix_process':(PARAM,CTX,n),'r1_log_prefix_process':(PARAM,CTX)}[name]
    for reg,v in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),args):u.reg_write(reg,v)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    u.emu_start((ENTRIES[name] if u is stock else syms[name])|1,0x20000100,count=300000);assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)],(name,n);results.append((states[id(u)]['trace'],bytes(u.mem_read(PARAM,12)),context(u),bytes(u.mem_read(0x20004000,256)) if real_printf else None))
   assert results[0]==results[1],(name,n,severity,dropped,colors,color,auto,value,results);comparisons+=1
  for n,sev,drop,colors,auto in itertools.product(range(9),range(6),(0,1,65535),(0,1),(0,1)):compare('nrf_log_std_entry_process',n,sev,drop,colors,2,auto)
  for n,sev,drop,colors,auto in itertools.product(range(10),range(6),(0,1),(0,1),(0,1)):compare('nrf_log_hexdump_entry_process',n,sev,drop,colors,4,auto)
  for value in range(256):compare('nrf_log_hexdump_entry_process',8,value=value)
  for sev,colors,newline in itertools.product(range(6),(0,1),(0,1)):compare('postfix_process',newline,sev,colors=colors)
  for sev,color,drop,dt in itertools.product(range(6),range(9),(0,1,65535),(bytes(7),bytes([255])*7,b'\xe8\x07\x0a\x0f\x0c\x22\x38')):compare('r1_log_prefix_process',severity=sev,colors=1,color=color,dropped=drop,datetime=dt)
 receipt.write_text(json.dumps(dict(application_sha256=sha(app),report_sha256=sha(rp),timestamp_callbacks_per_implementation=timestamp_callbacks//2,actual_calendar=real_calendar,calendar_report_sha256=sha(BASE/'native-log-calendar/report.json') if real_calendar else None,structured_time_report_sha256=sha(BASE/'structured-time/report.json') if real_calendar else None,integer_report_sha256=sha(BASE/'integer-runtime/report.json') if real_calendar else None,actual_modules=real_modules,module_report_sha256=sha(BASE/'sdk-log-modules/report.json') if real_modules else None,actual_printf=real_printf,output_bytes_per_implementation=output_bytes//2,output_callbacks_per_implementation=output_callbacks//2,printf_report_sha256=sha(BASE/'sdk-fprintf/report.json') if real_printf else None,memory_report_sha256=sha(BASE/'runtime/report.json') if real_printf else None,comparisons=comparisons,printf_calls_per_implementation=printf_calls//2,scope='Pinned SDK std/hexdump/postfix with local native wall-clock prefix and ASCII classifier; formatting call order/arguments, auto-flush restoration, all256 hex byte values and color codes',limitations=['Printf/flush execute only in actual_printf mode, yielding byte-sink proof there. Calendar executes only in actual_calendar mode with a fixed timestamp-getter fixture; color lookup is actual only in actual_modules mode. No real-clock or physical-output proof.','Valid severity0..5 for call fixtures; byte-sink mode excludes severity0 prefixes because their null label is not a valid string. Bounded arguments/data and canonical bool states only.','Locale-specific printability is unproven; native ASCII classification is exercised through hexdump. Whole-image startup/linking and byte identity remain gates.'],instruction_identity_proven=False),indent=2)+'\n');print(comparisons,'log formatter comparisons;',printf_calls//2,'printf calls')
if __name__=='__main__':main()
