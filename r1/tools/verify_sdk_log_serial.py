#!/usr/bin/env python3
"""Native serial dispatcher with actual memory-object/atomic/critical/copy providers."""
import hashlib,itertools,json,struct,subprocess,tempfile,re,sys
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();POOL=0x20002000;CB=POOL+32;STACK=POOL+64;MEM=POOL+128;USER=0x20003000

def main():
 real_formatter='--real-formatter' in sys.argv
 out=BASE/'sdk-log-serial';rp=out/'report.json';r=json.loads(rp.read_text());receipt=out/('formatter-integration-verification.json' if real_formatter else 'verification.json');receipt.unlink(missing_ok=True)
 for p,d in r['inputs'].items():assert sha(ROOT/p)==d,p
 objects=[];reports={}
 for name,file,key in [('sdk-log-serial','log-serial.o','selected_object_sha256'),('sdk-memobj','memobj.o','selected_object_sha256'),('sdk-critical','critical-only.o','selected_object_sha256'),('sdk-logger-frontend','nrf_atomic-selected.o',None),('runtime','memory-runtime.o','relocatable_sha256')]:
  p=BASE/name/'report.json';q=json.loads(p.read_text());o=p.parent/file;assert sha(o)==(q[key] if key else next(x['object_sha256'] for x in q['units'] if x['source'].endswith('/nrf_atomic.c')));objects.append(o);reports[name+'/report.json']=sha(p)
 if real_formatter:
  p=BASE/'sdk-log-formatter/report.json';q=json.loads(p.read_text());o=p.parent/'log-formatter.o';assert sha(o)==q['selected_object_sha256'];objects.append(o);reports['sdk-log-formatter/report.json']=sha(p)
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';comparisons=0;callbacks=0;states={}
 with tempfile.TemporaryDirectory() as directory:
  t=Path(directory);ld=t/'layout.ld';elf=t/'test.elf';binary=t/'text.bin';ld.write_text('SECTIONS { .bss.nrf_nvic_state 0x2002c2fc (NOLOAD) : { *(.bss.nrf_nvic_state) } .text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } /DISCARD/ : { *(.comment) *(.note*) } }');bindings=({'nrf_fprintf':0x100ed01,'nrf_fprintf_buffer_flush':0x100ed11,'nrf_log_color_id_get':0x100ed21,'r1_log_local_datetime_fill':0x100ed31} if real_formatter else {'nrf_log_std_entry_process':0x100ee01,'nrf_log_hexdump_entry_process':0x100ee11});subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--entry=nrf_log_backend_serial_put',*['--defsym='+n+'='+hex(a) for n,a in bindings.items()],*map(str,objects),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True);syms={x.split()[-1]:int(x.split()[0],16) for x in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x.split())==3}
  stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
  for u in (stock,candidate):u.mem_map(0x20000,0xc0000);u.mem_map(0x1000000,0x10000);u.mem_map(0x20000000,0x40000);u.mem_map(0xe000e000,4096)
  stock.mem_write(0x27000,app.read_bytes());candidate.mem_write(0x1000000,binary.read_bytes());
  stock.reg_write(UC_ARM_REG_SP,0x2003f000);stock.emu_start(0x283a1,0x27208,count=2000000);assert stock.reg_read(UC_ARM_REG_PC)==0x27208
  if real_formatter:
   b=elf.read_bytes();off=struct.unpack_from('<I',b,32)[0];ss,ns=struct.unpack_from('<HH',b,46)
   for i in range(ns):
    _,typ,flags,a,p,z,*_=struct.unpack_from('<10I',b,off+i*ss)
    if flags&2 and typ!=8 and z:candidate.mem_write(a,b[p:p+z])
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  def cstr(u,a):
   if not a:return None
   result=bytearray()
   for i in range(256):
    v=u.mem_read(a+i,1)[0]
    if not v:return result.decode('latin1')
    result.append(v)
   raise AssertionError('unterminated')
  formatter_entries={0x79b48:'std',0x79a44:'hex',0x100ee00:'std',0x100ee10:'hex'}
  if real_formatter:formatter_entries.update({syms['nrf_log_std_entry_process']&~1:'std',syms['nrf_log_hexdump_entry_process']&~1:'hex'})
  def hook(u,a,size,user):
   nonlocal callbacks
   if real_formatter and a in (0x78a40,0x78a5a,0x7965c,0x8ac28,0x100ed00,0x100ed10,0x100ed20,0x100ed30):
    args=[u.reg_read(reg) for reg in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)]
    if a in (0x78a40,0x100ed00):
     fmt=cstr(u,args[1]);specs=re.findall(r'%(?:[-+ #0]*\d*(?:\.\d+)?[hl]*)([sdxcu])',fmt);values=[]
     for i,spec in enumerate(specs):
      v=args[i+2] if i<2 else struct.unpack('<I',bytes(u.mem_read(u.reg_read(UC_ARM_REG_SP)+(i-2)*4,4)))[0];values.append(cstr(u,v) if spec=='s' else v)
     raw=bytes(u.mem_read(args[0],24));states[id(u)].append(('printf',fmt,values,raw[:13],raw[16:]))
    elif a in (0x78a5a,0x100ed10):states[id(u)].append(('flush',));u.mem_write(args[0]+8,bytes(4))
    elif a in (0x7965c,0x100ed20):u.reg_write(UC_ARM_REG_R0,2)
    else:states[id(u)].append(('calendar',));u.mem_write(args[0],b'\xe8\x07\x0a\x0f\x0c\x22\x38')
    u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR));return
   if a not in formatter_entries:return
   args=[u.reg_read(reg) for reg in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)];std=formatter_entries[a]=='std';params=args[3] if std else args[2];ctx=struct.unpack('<I',bytes(u.mem_read(u.reg_read(UC_ARM_REG_SP),4)))[0] if std else args[3];io=bytes(u.mem_read(ctx,24));trace=('std',args[0],bytes(u.mem_read(args[1],args[2]*4))) if std else ('hex',bytes(u.mem_read(args[0],args[1])));states[id(u)].append((trace,bytes(u.mem_read(params+4,6)),io[:13],io[16:]));callbacks+=1
   if real_formatter:return
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  for u in (stock,candidate):u.hook_add(UC_HOOK_CODE,hook)
  native={'nrf_memobj_pool_init':0x79c98,'nrf_memobj_alloc':0x79bfe,'nrf_memobj_get':0x79c90,'nrf_memobj_write':0x79cca,'nrf_log_backend_serial_put':0x79598}
  def call(u,name,args):
   u.reg_write(UC_ARM_REG_SP,0x2003f000);u.mem_write(0x2003f000,struct.pack('<I',args[4] if len(args)>4 else 0));u.reg_write(UC_ARM_REG_LR,0x20000101)
   for reg,v in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),args):u.reg_write(reg,v)
   for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
   u.emu_start((native[name] if u is stock else syms[name])|1,0x20000100,count=300000);assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)],name;return u.reg_read(UC_ARM_REG_R0)
  cases=[]
  for n,sev in itertools.product(range(7),range(8)):cases.append(struct.pack('<2I',1|(sev<<3)|(n<<6)|(0x9a000<<10),0)+struct.pack('<'+str(n)+'I',*[0x12345000+i for i in range(n)]))
  for n,sev in itertools.product((0,1,7,8,9,15,16,17,79,80),range(8)):cases.append(struct.pack('<2I',2|(sev<<3)|(n<<22),0)+bytes(range(n)))
  if real_formatter:cases=[p for p in cases if ((struct.unpack_from('<I',p)[0]>>3)&7)<=5]
  for kind in (0,3):cases.append(struct.pack('<2I',kind,0))
  for payload,meta,refs,bsize in itertools.product(cases,(0,0x1234001c,0xffffffff),(0,1),(0,1,16,4096)):
   results=[]
   for u in (stock,candidate):
    states[id(u)]=[];u.reg_write(UC_ARM_REG_PRIMASK,0);u.mem_write(0x20007a18,bytes(4));u.mem_write(0x9a000,('message '+'%08x '*((struct.unpack_from('<I',payload)[0]>>6)&15)).encode()+b'\0');u.mem_write(POOL,bytes(2048));u.mem_write(POOL,struct.pack('<5I',CB,STACK,STACK+8,MEM,24));u.mem_write(USER,payload[:4]+struct.pack('<I',meta)+payload[8:]);u.mem_write(0x2002c2fc,bytes(12));u.mem_write(0xe000e000,bytes(4096));u.mem_write(0x2003e000,bytes([0x96])*4096);call(u,'nrf_memobj_pool_init',(POOL,));p=call(u,'nrf_memobj_alloc',(POOL,len(payload)));assert p;call(u,'nrf_memobj_write',(p,USER,len(payload),0))
    if refs:call(u,'nrf_memobj_get',(p,))
    call(u,'nrf_log_backend_serial_put',(0x20001000,p,0x20004000,bsize,0x20000111));results.append((states[id(u)],bytes(u.mem_read(POOL,2048)),bytes(u.mem_read(0x2002c2fc,12))))
   assert results[0]==results[1],(payload,meta,refs,bsize,[(i,results[0][i],results[1][i]) for i in range(3) if results[0][i]!=results[1][i]]);comparisons+=1
 receipt.write_text(json.dumps(dict(application_sha256=sha(app),report_sha256=sha(rp),provider_reports=reports,actual_formatter=real_formatter,comparisons=comparisons,formatter_callbacks_per_implementation=callbacks//2,scope='Actual serial dispatcher and SDK memory-object/pool/reference/copy/critical code; standard0..6, all severities, hex8-byte chunking, empty/unknown types and reference release',limitations=['Standard/hexdump formatters execute only in actual_formatter mode; printf/flush/calendar/color remain fixtures in that mode. No emitted byte stream or transport proof.','Timestamp is omitted by native two-word headers and disabled configuration; unused timestamp and structure padding are excluded from comparison.','Only valid bounded packets are tested; whole-image startup/linking, hardware and byte identity remain unresolved.'],instruction_identity_proven=False),indent=2)+'\n');print(comparisons,'serial dispatcher comparisons;',callbacks//2,'formatter callbacks')
if __name__=='__main__':main()
