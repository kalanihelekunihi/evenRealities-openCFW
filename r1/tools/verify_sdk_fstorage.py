#!/usr/bin/env python3
"""Pinned fstorage facade differential over controlled API records and two instances."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ENTRIES={'nrf_fstorage_init':0x78c78,'nrf_fstorage_erase':0x78c4c,'nrf_fstorage_write':0x78dac,'nrf_fstorage_is_busy':0x78c80}
A=0x20007dc0;B=A+20;C=0x20002000;API_A=0x20001000;API_B=0x20001100;INFO=0x20001200

def main():
 out=BASE/'sdk-fstorage';rp=out/'report.json';obj=out/'fstorage.o';r=json.loads(rp.read_text());receipt=out/'verification.json';receipt.unlink(missing_ok=True);assert sha(obj)==r['units'][0]['object_sha256']
 for p,d in r['inputs'].items():assert sha(ROOT/p)==d,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';states={};counts={n:0 for n in ENTRIES}
 with tempfile.TemporaryDirectory() as directory:
  t=Path(directory);ld=t/'layout.ld';elf=t/'test.elf';binary=t/'text.bin';ld.write_text('SECTIONS { .text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } /DISCARD/ : { *(.comment) *(.note*) } }')
  subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--entry=nrf_fstorage_init','--defsym=__start_fs_data='+hex(A),'--defsym=__stop_fs_data='+hex(B+20),str(obj),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True)
  syms={x.split()[-1]:int(x.split()[0],16) for x in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x.split())==3}
  stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
  for u in (stock,candidate):u.mem_map(0x20000,0xc0000);u.mem_map(0x1000000,0x10000);u.mem_map(0x20000000,0x40000)
  stock.mem_write(0x27000,app.read_bytes());candidate.mem_write(0x1000000,binary.read_bytes())
  assert struct.unpack('<II',bytes(stock.mem_read(0x78cc8,8)))==(A,B+20)
  def hook(u,address,size,user):
   if address not in (0x100e100,0x100e110,0x100e120,0x100e130,0x100e140):return
   f=states[id(u)];a=[u.reg_read(reg) for reg in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)];name={0x100e100:'init',0x100e110:'write',0x100e120:'erase',0x100e130:'busyA',0x100e140:'busyB'}[address]
   args=a[:2] if name=='init' else a[:1] if name.startswith('busy') else a if name=='erase' else a+list(struct.unpack('<I',bytes(u.mem_read(u.reg_read(UC_ARM_REG_SP),4))))
   f['trace'].append((name,args,bytes(u.mem_read(a[0],20))))
   if f['mutation']&1:u.mem_write(a[0],struct.pack('<I',API_B))
   if f['mutation']&2:u.mem_write(a[0]+12,struct.pack('<II',0x80000000,0xffffffff))
   if f['mutation']&4:u.mem_write(B,struct.pack('<I',API_B))
   value=(f['busy_a'] if name=='busyA' else f['busy_b']) if name.startswith('busy') else f['result'];u.reg_write(UC_ARM_REG_R0,value);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  for u in (stock,candidate):u.hook_add(UC_HOOK_CODE,hook)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  def run(u,name,context=A,api=API_A,api_a=API_A,api_b=API_B,api_c=API_A,busy_a=0,busy_b=0,result=0,mutation=0,address=0xd4000,length=4,source=0x20004000,parameter=0x12345678,erase_unit=4096,program_unit=4,start=0xd4000,end=0xf8000):
   u.mem_write(A-4,b'LEFT');u.mem_write(B+20,b'RGHT')
   for p,ptr in ((A,api_a),(B,api_b),(C,api_c)):u.mem_write(p,struct.pack('<5I',ptr,INFO,0x12345679,start,end))
   u.mem_write(INFO,struct.pack('<III',erase_unit,program_unit,0))
   for p,busy in ((API_A,0x100e131),(API_B,0x100e141)):u.mem_write(p,struct.pack('<8I',0x100e101,0,0,0x100e111,0x100e121,0,0,busy))
   f=dict(trace=[],busy_a=busy_a,busy_b=busy_b,result=result,mutation=mutation);states[id(u)]=f
   args=(context,api,parameter) if name.endswith('init') else (context,address,length,parameter) if name.endswith('erase') else (context,address,source,length) if name.endswith('write') else (context,)
   u.reg_write(UC_ARM_REG_SP,0x2003f000);u.mem_write(0x2003f000,struct.pack('<I',parameter));u.reg_write(UC_ARM_REG_LR,0x20000101)
   for reg,v in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),args):u.reg_write(reg,v)
   for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
   u.emu_start((ENTRIES[name] if u is stock else syms[name])|1,0x20000100,count=10000)
   assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
   assert bytes(u.mem_read(A-4,4))==b'LEFT' and bytes(u.mem_read(B+20,4))==b'RGHT'
   return u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(A,40)),bytes(u.mem_read(C,20)),f['trace']
  def compare(name,**kw):
   a=run(stock,name,**kw);b=run(candidate,name,**kw);assert a==b,(name,kw,a,b);counts[name]+=1
  for context,api,result,mutation,parameter in itertools.product((A,B,C),(API_A,API_B),(0,1,8,0x80000000,0xffffffff),range(8),(0,0x12345678,0xffffffff)):compare('nrf_fstorage_init',context=context,api=api,result=result,mutation=mutation,parameter=parameter)
  values=(0,1,3,4,4096,0x7fffffff,0x80000000,0xfffffffc,0xffffffff)
  for address,length,unit,start,end,result in itertools.product(values,values,(0,1,4096,0xffffffff),(0,0xd4000),(0,0xf8000,0xffffffff),(0,8,0xffffffff)):compare('nrf_fstorage_erase',address=address,length=length,erase_unit=unit,start=start,end=end,result=result)
  for address,length,source,unit,result in itertools.product(values,values,(0,0x20004000,0x20004001),(1,4,0xffffffff),(0,8,0xffffffff)):compare('nrf_fstorage_write',address=address,length=length,source=source,program_unit=unit,result=result)
  for name in ('nrf_fstorage_erase','nrf_fstorage_write'):
   for mutation,parameter in itertools.product(range(8),(0,0xffffffff)):compare(name,mutation=mutation,parameter=parameter)
  for context,api_a,api_b,api_c,busy_a,busy_b,mutation in itertools.product((0,A,B,C),(0,API_A,API_B),(0,API_A,API_B),(0,API_A,API_B),(0,1),(0,1),range(8)):compare('nrf_fstorage_is_busy',context=context,api_a=api_a,api_b=api_b,api_c=api_c,busy_a=busy_a,busy_b=busy_b,mutation=mutation)
 receipt.write_text(json.dumps(dict(application_sha256=sha(app),report_sha256=sha(rp),object_sha256=sha(obj),comparisons=sum(counts.values()),comparisons_by_entry=counts,instance_range_bytes_authenticated=40,scope='Unchanged SDK facades under native disabled checks/asserts: init API assignment and callback replies, unchecked invalid alignment/length/bounds dispatch, full argument forwarding, API/geometry mutation, canonical bool direct and fallback busy scans across both native instances',limitations=['API records and callbacks are controlled fixtures; the actual nrf_fstorage_sd implementation remains unresolved.','Two-instance range is authenticated, but secondary production context allocation/content and final fs_data linkage remain gates.','Mapped contexts/APIs and nonzero write program units only; invalid pointer faults and noncanonical bool returns are not portable contracts.','Original compiler/helper instruction identity, full image and hardware remain unproven.'],instruction_identity_proven=False),indent=2)+'\n');print(sum(counts.values()),'SDK fstorage comparisons passed')
if __name__=='__main__':main()
