#!/usr/bin/env python3
"""Native FAL adapters with actual C registry dispatch and memory helpers."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
FIELDS={'device_handle':(0x200077c0,4),'write_request':(0x2001e560,12),'read_request':(0x2001e56c,12),'geometry':(0x2001e578,16)}
ENTRIES={'r1_native_fal_device_initialize':0x71054,'r1_native_fal_device_read':0x87af8,'r1_native_fal_device_write':0x96fb0,'r1_native_fal_device_erase':0x5d4f8}
RECORD=0x200077c4;A=0x20001000;B=0x20001040;OPS=0x20001100;NAME=0x20001200;BUFFER=0x20002000

def main():
 out=BASE/'native-fal-device';rp=out/'report.json';obj=out/'native_fal_device.o';r=json.loads(rp.read_text());receipt=out/'verification.json';receipt.unlink(missing_ok=True);assert sha(obj)==r['units'][0]['object_sha256']
 for p,d in r['inputs'].items():assert sha(ROOT/p)==d,p
 mr=BASE/'runtime/report.json';memory=BASE/'runtime/memory-runtime.o';assert sha(memory)==json.loads(mr.read_text())['relocatable_sha256'];rr=BASE/'i2c5/report.json';registry=BASE/'i2c5/stock_registry.o';row=next(x for x in json.loads(rr.read_text())['units'] if x['source'].endswith('/stock_registry.c'));assert sha(registry)==row['object_sha256']
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';states={};count=0;calls=0
 with tempfile.TemporaryDirectory() as directory:
  t=Path(directory);ld=t/'layout.ld';elf=t/'test.elf';binary=t/'text.bin';ld.write_text('SECTIONS { '+''.join('.r1.fal.'+n+' '+hex(a)+' (NOLOAD) : { *(.r1.fal.'+n+') } ' for n,(a,z) in FIELDS.items())+'.r1.fal.device_record 0x200077c4 : { *(.r1.fal.device_record) } .r1.registry.head 0x20007680 (NOLOAD) : { *(.r1.registry.head) } .text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } /DISCARD/ : { *(.comment) *(.note*) } }')
  subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--entry=r1_native_fal_device_initialize',str(obj),str(registry),str(memory),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True)
  syms={x.split()[-1]:int(x.split()[0],16) for x in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x.split())==3}
  for n,(a,z) in FIELDS.items():assert syms['r1_fal_'+n]==a
  p=t/'record.bin';subprocess.run(['arm-none-eabi-objcopy','--dump-section','.r1.fal.device_record='+str(p),str(elf)],check=True);record=p.read_bytes();assert len(record)==56
  stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
  for u in (stock,candidate):u.mem_map(0x20000,0xc0000);u.mem_map(0x1000000,0x10000);u.mem_map(0x20000000,0x40000)
  stock.mem_write(0x27000,app.read_bytes());candidate.mem_write(0x1000000,binary.read_bytes());stock.reg_write(UC_ARM_REG_SP,0x2003f000);stock.emu_start(0x283a1,0x27208,count=2000000);assert stock.reg_read(UC_ARM_REG_PC)==0x27208
  native_record=bytes(stock.mem_read(RECORD,56));assert native_record[:36]==record[:36] and native_record[52:]==record[52:]==struct.pack('<I',32)
  assert struct.unpack_from('<4I',native_record,36)==tuple(a|1 for a in ENTRIES.values());assert struct.unpack_from('<4I',record,36)==tuple(syms[n]|1 for n in ENTRIES)
  for a,z in FIELDS.values():assert bytes(stock.mem_read(a,z))==bytes(z)
  def hook(u,address,size,user):
   nonlocal calls
   if address not in (0x100e100,0x100e110,0x100e120,0x100e130):return
   f=states[id(u)];a=[u.reg_read(reg) for reg in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)];calls+=1
   if address==0x100e100:
    f['trace'].append(('open',a[0]));
    if f['mutation']&1:u.mem_write(0x200077c0,struct.pack('<I',B))
   else:
    packet=a[2];words=struct.unpack('<III',bytes(u.mem_read(packet,12)));kind={0x100e110:'read',0x100e120:'write',0x100e130:'control'}[address];f['trace'].append((kind,a[0],a[1],packet,words))
    if kind=='control' and a[1]==1:u.mem_write(packet,bytes([f['pages'],0x73,0x82,0x91])+struct.pack('<III',f['base'],0xaabbccdd,f['page_size']))
    if f['mutation']&2 and not (kind=='control' and a[1]==1):u.mem_write(packet,struct.pack('<III',0x11223344,0x55667788,0x99aabbcc))
   u.reg_write(UC_ARM_REG_R0,f['result']);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  for u in (stock,candidate):u.hook_add(UC_HOOK_CODE,hook)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  def run(u,name,present=True,callbacks=15,result=0,mutation=0,pages=36,base=0xd4000,page_size=4096,offset=24,n=124,string_length=17,pointer=BUFFER):
   u.mem_write(RECORD,native_record if u is stock else record);u.mem_write(RECORD+24,struct.pack('<III',0x11223344,0x55667788,0x99aabbcc));u.mem_write(0x200077c0,struct.pack('<I',A if present else 0));u.mem_write(0x20007680,struct.pack('<I',A if present else 0));u.mem_write(NAME,b'device_flash\0');u.mem_write(BUFFER,b'x'*string_length+b'\0'+bytes(520-string_length));u.mem_write(0x2001e55c,b'LEFT'+bytes([0xa7])*40+b'RGHT')
   ops=[0]*9
   for i,slot in enumerate((0,4,5,6)):ops[slot]=(0x100e101+i*16) if callbacks&(1<<i) else 0
   u.mem_write(OPS,struct.pack('<9I',*ops))
   for a in (A,B):u.mem_write(a,struct.pack('<6I',NAME,OPS,0,0,0,0))
   f=dict(trace=[],result=result,mutation=mutation,pages=pages,base=base,page_size=page_size);states[id(u)]=f
   u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
   args=(offset,n) if name.endswith('erase') else (offset,pointer,n)
   for reg,v in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2),args):u.reg_write(reg,v)
   for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
   u.emu_start((ENTRIES[name] if u is stock else syms[name])|1,0x20000100,count=10000)
   assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
   assert bytes(u.mem_read(0x2001e55c,4))==b'LEFT' and bytes(u.mem_read(0x2001e588,4))==b'RGHT'
   return u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(RECORD+24,12)),bytes(u.mem_read(0x200077c0,4)),bytes(u.mem_read(0x2001e560,40)),f['trace']
  def compare(name,**kw):
   nonlocal count
   a=run(stock,name,**kw);b=run(candidate,name,**kw);assert a==b,(name,kw,a,b);count+=1
  for name in ENTRIES:
   for present,callbacks,result,mutation in itertools.product((False,True),range(16),(0,1,7,0xffffffff),range(4)):compare(name,present=present,callbacks=callbacks,result=result,mutation=mutation)
  for pages in range(256):
   for base,page_size in itertools.product((0,0xd4000,0xffffffff),(0,1,4096,0xffffffff)):compare('r1_native_fal_device_initialize',pages=pages,base=base,page_size=page_size)
  for name in list(ENTRIES)[1:]:
   for offset,n,result in itertools.product((0,1,24,0x80000000,0xffffffff),(0,1,24,512,0xffffffff),(0,1,7,0xffffffff)):compare(name,offset=offset,n=n,result=result)
  for length in range(513):compare('r1_native_fal_device_write',n=0,string_length=length)
 receipt.write_text(json.dumps(dict(application_sha256=sha(app),report_sha256=sha(rp),object_sha256=sha(obj),memory_report_sha256=sha(mr),registry_report_sha256=sha(rr),registry_object_sha256=sha(registry),comparisons=count,registry_callback_calls_per_implementation=calls//2,cold_zero_bytes_compared=sum(z for a,z in FIELDS.values()),device_record_bytes_pointer_normalized=56,scope='Native FAL record/binding/read/write/erase adapters with actual registry lookup/dispatch and C string helpers, all callback-presence masks and geometry page bytes, ignored open/read results, retained read length, zero-length strlen, request mutations, wrap arithmetic, guards/registers',limitations=['Registry flash records and driver operations are controlled fixtures; concrete native flash hardware/SDK operation bodies remain unresolved.','Only mapped string inputs are covered for zero-length write; null/invalid strings are not portable contracts.','Official FAL struct/callback types and mutable native configuration agree; original compiler/link/table identity and whole image remain unproven.'],instruction_identity_proven=False),indent=2)+'\n');print(count,'native FAL adapter comparisons passed')
if __name__=='__main__':main()
