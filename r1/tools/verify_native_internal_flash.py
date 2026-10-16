#!/usr/bin/env python3
"""Native registered flash policy; actual C registry, controlled Nordic adapters."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ENTRIES={'r1_internal_flash_callback_configuration':0x54970,'r1_internal_flash_erase_and_geometry_control':0x5498c,'r1_internal_flash_fstorage_configuration':0x549f0,'r1_internal_flash_device_read':0x54a4c,'r1_internal_flash_device_registration':0x54a8c,'r1_internal_flash_device_write':0x54aa4}
RECORD=0x20006f98;CONTEXT=0x20007dc0;PACKET=0x20001000;CONFIG=0x20001100;OUT=0x20002000;OTHER=0x20003000

def main():
 out=BASE/'native-internal-flash';rp=out/'report.json';obj=out/'native_internal_flash.o';r=json.loads(rp.read_text());receipt=out/'verification.json';receipt.unlink(missing_ok=True);assert sha(obj)==r['units'][0]['object_sha256']
 for p,d in r['inputs'].items():assert sha(ROOT/p)==d,p
 mr=BASE/'runtime/report.json';memory=BASE/'runtime/memory-runtime.o';assert sha(memory)==json.loads(mr.read_text())['relocatable_sha256'];rr=BASE/'i2c5/report.json';registry=BASE/'i2c5/stock_registry.o';row=next(x for x in json.loads(rr.read_text())['units'] if x['source'].endswith('/stock_registry.c'));assert sha(registry)==row['object_sha256']
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';states={};counts={n:0 for n in ENTRIES}
 with tempfile.TemporaryDirectory() as directory:
  t=Path(directory);ld=t/'layout.ld';elf=t/'test.elf';binary=t/'text.bin';ld.write_text('SECTIONS { .r1.flash.name 0xc06d4 : { *(.r1.flash.name) } .r1.flash.record 0x20006f98 : { *(.r1.flash.record) } .r1.flash.fstorage 0x20007dc0 : { *(.r1.flash.fstorage) } .r1.registry.head 0x20007680 (NOLOAD) : { *(.r1.registry.head) } .text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } /DISCARD/ : { *(.comment) *(.note*) } }')
  defs={'nrf_fstorage_sd':0x9c86c,'nrf_fstorage_init':0x100e201,'r1_internal_flash_event_handler':0x65721,'r1_adc_error':0x100e211,'r1_internal_flash_page_erase':0x100e221,'r1_internal_flash_mapped_read':0x100e231,'r1_internal_flash_word_write':0x100e241}
  subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--entry=r1_internal_flash_device_registration',*['--defsym='+n+'='+hex(a) for n,a in defs.items()],str(obj),str(registry),str(memory),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True)
  syms={x.split()[-1]:int(x.split()[0],16) for x in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x.split())==3};sections={}
  for sec in ('name','record','fstorage'):
   p=t/(sec+'.bin');subprocess.run(['arm-none-eabi-objcopy','--dump-section','.r1.flash.'+sec+'='+str(p),str(elf)],check=True);sections[sec]=p.read_bytes()
  stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
  for u in (stock,candidate):u.mem_map(0x20000,0xc0000);u.mem_map(0x1000000,0x10000);u.mem_map(0x10000000,0x2000);u.mem_map(0x20000000,0x40000)
  stock.mem_write(0x27000,app.read_bytes());candidate.mem_write(0x1000000,binary.read_bytes());candidate.mem_write(0xc06d4,sections['name']);stock.reg_write(UC_ARM_REG_SP,0x2003f000);stock.emu_start(0x283a1,0x27208,count=2000000);assert stock.reg_read(UC_ARM_REG_PC)==0x27208
  native_record=bytes(stock.mem_read(RECORD,80));native_context=bytes(stock.mem_read(CONTEXT,20));assert len(sections['record'])==80 and len(sections['fstorage'])==20
  assert native_record[:44]==sections['record'][:44] and native_context==sections['fstorage'] and bytes(stock.mem_read(0xc06d4,len(sections['name'])))==sections['name']
  slots={44:'r1_internal_flash_fstorage_configuration',60:'r1_internal_flash_device_read',64:'r1_internal_flash_device_write',68:'r1_internal_flash_erase_and_geometry_control',72:'r1_internal_flash_callback_configuration'}
  for offset in range(44,80,4):assert struct.unpack_from('<I',sections['record'],offset)[0]==(syms[slots[offset]]|1 if offset in slots else 0) and struct.unpack_from('<I',native_record,offset)[0]==(ENTRIES[slots[offset]]|1 if offset in slots else 0)
  def ret(u,v):u.reg_write(UC_ARM_REG_R0,v);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  def hook(u,address,size,user):
   f=states[id(u)];a=[u.reg_read(reg) for reg in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)]
   if address in (0x100e300,0x100e310,0x100e320):
    name='before' if address==0x100e300 else 'after' if address==0x100e310 else 'afterB';f['trace'].append((name,))
    if name=='before':
     if f['mutation']&1:u.mem_write(PACKET,struct.pack('<III',OUT+16,0xfffffffc,0xffff0001))
     if f['mutation']&2:u.mem_write(RECORD+16,struct.pack('<I',0x100e321));u.mem_write(RECORD+8,b'\0')
    ret(u,0xffffffff)
   elif address in (0x78c78,0x100e200):
    f['trace'].append(('sdk_init',tuple(a[:3])));u.mem_write(CONTEXT,struct.pack('<II',0x20004000,0x20004100));ret(u,f['result'])
   elif address in (0x4e5bc,0x100e210):f['trace'].append(('error',a[0]));ret(u,0xffffffff)
   elif address in (0x5c40c,0x100e220):f['trace'].append(('erase',a[0],a[1]));ret(u,f['result'])
   elif address in (0x5c464,0x100e230):
    f['trace'].append(('read',a[0],a[1],a[2]));u.mem_write(a[0],bytes([0x59])*min(a[1],128));ret(u,f['result'])
   elif address in (0x5c480,0x100e240):f['trace'].append(('write',a[0],a[1],a[2]));ret(u,f['result'])
  for u in (stock,candidate):u.hook_add(UC_HOOK_CODE,hook)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  def run(u,name,initialized=1,enabled=0,result=0,mutation=0,null=False,operation=0,length=124,offset=24,boundary=0xf8000,page=4096,pages=256,existing=0):
   u.mem_write(RECORD,native_record if u is stock else sections['record']);u.mem_write(RECORD+4,bytes([initialized]));u.mem_write(RECORD+8,bytes([enabled]));u.mem_write(RECORD+12,struct.pack('<II',0x100e301,0x100e311));u.mem_write(CONTEXT,native_context);u.mem_write(CONTEXT+12,struct.pack('<II',0xd4000,0xf8000));u.mem_write(PACKET,struct.pack('<III',OUT,offset,length)+b'KEEP');u.mem_write(CONFIG,bytes([enabled,0x73,0x82,0x91])+struct.pack('<II',0x100e301,0x100e311));u.mem_write(OUT-4,b'LEFT'+bytes([0xa7])*256+b'RGHT');u.mem_write(0x10000010,struct.pack('<II',page,pages));u.mem_write(0x10001014,struct.pack('<II',boundary,0xfe000));u.mem_write(0x20007680,struct.pack('<I',OTHER if existing else 0));u.mem_write(OTHER,struct.pack('<6I',0xc06d4 if existing==2 else 0x20003100,0x20003200,0,0,0,0));u.mem_write(0x20003100,b'other\0')
   f=dict(trace=[],result=result,mutation=mutation);states[id(u)]=f;u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
   args=(0,0 if null else CONFIG) if name.endswith('callback_configuration') else (0,operation,0 if null else PACKET,0)
   for reg,v in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),args):u.reg_write(reg,v)
   for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
   u.emu_start((ENTRIES[name] if u is stock else syms[name])|1,0x20000100,count=10000)
   assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
   assert bytes(u.mem_read(OUT-4,4))==b'LEFT' and bytes(u.mem_read(OUT+256,4))==b'RGHT'
   return u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(RECORD,44)),bytes(u.mem_read(CONTEXT,20)),bytes(u.mem_read(PACKET,16)),bytes(u.mem_read(OUT,256)),bytes(u.mem_read(0x20007680,4)),bytes(u.mem_read(OTHER,24)),f['trace']
  def compare(name,**kw):
   a=run(stock,name,**kw);b=run(candidate,name,**kw);assert a==b,(name,kw,a,b);counts[name]+=1
  for enabled,null in itertools.product(range(256),(False,True)):compare('r1_internal_flash_callback_configuration',enabled=enabled,null=null)
  for initialized,boundary,page,pages,result in itertools.product((0,1,2,255),(0,0xf8000,0xffffffff),(0,1,4096,0xffffffff),(0,256,0xffffffff),(0,8,0xffffffff)):compare('r1_internal_flash_fstorage_configuration',initialized=initialized,boundary=boundary,page=page,pages=pages,result=result)
  for name in ('r1_internal_flash_device_read','r1_internal_flash_device_write','r1_internal_flash_erase_and_geometry_control'):
   for initialized,enabled,null,operation,result,mutation in itertools.product((0,1,2,255),(0,1,2,255),(False,True),(0,1,2,0xffffffff),(0,1,8,0xffffffff),range(4)):compare(name,initialized=initialized,enabled=enabled,null=null,operation=operation,result=result,mutation=mutation)
   for length in range(65536):compare(name,length=length,operation=2 if name.endswith('control') else 0)
   for length,offset in itertools.product((0x10000,0x10001,0x80000000,0xffffffff),(0,0xfffffffc,0xffffffff)):compare(name,length=length,offset=offset)
  for existing in range(3):compare('r1_internal_flash_device_registration',existing=existing)
 receipt.write_text(json.dumps(dict(application_sha256=sha(app),report_sha256=sha(rp),object_sha256=sha(obj),memory_report_sha256=sha(mr),registry_report_sha256=sha(rr),registry_object_sha256=sha(registry),comparisons=sum(counts.values()),comparisons_by_entry=counts,record_bytes_pointer_normalized=80,fstorage_context_bytes_compared=20,name_bytes_compared=len(sections['name']),scope='Native registered flash policy: all callback flag bytes, geometry wrap/fallback and ignored SDK init errors, 16-bit request narrowing, error precedence, callback/request mutation, exact initialized records and registration with actual C registry',limitations=['Nordic init/read/write/erase and pre/post callbacks are controlled fixtures; live hardware operations/completion remain unresolved.','FICR/UICR are mapped fixtures; invalid values preserve stock arithmetic without physical safety claims.','Full-image linking, original compiler/link identity, byte equality and hardware remain unproven.'],instruction_identity_proven=False),indent=2)+'\n');print(sum(counts.values()),'native internal-flash comparisons passed')
if __name__=='__main__':main()
