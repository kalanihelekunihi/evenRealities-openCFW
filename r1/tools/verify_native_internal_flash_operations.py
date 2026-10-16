#!/usr/bin/env python3
"""Native flash arithmetic/copy/completion differential with controlled SDK APIs."""
import hashlib,itertools,json,struct,subprocess,tempfile,sys
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ENTRIES={'r1_internal_flash_page_erase':0x5c40c,'r1_internal_flash_mapped_read':0x5c464,'r1_internal_flash_word_write':0x5c480,'r1_internal_flash_wait':0x969fc,'r1_internal_flash_event_handler':0x65720}
CONTEXT=0x20007dc0;EVENT=0x20001000;OUT=0x20002000;SOURCE=0x20004000

def main():
 real_sdk='--real-sdk' in sys.argv
 out=BASE/'native-internal-flash-operations';rp=out/'report.json';obj=out/'native_internal_flash_operations.o';r=json.loads(rp.read_text());receipt=out/('sdk-integration-verification.json' if real_sdk else 'verification.json');receipt.unlink(missing_ok=True);assert sha(obj)==r['units'][0]['object_sha256']
 for p,d in r['inputs'].items():assert sha(ROOT/p)==d,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';states={};counts={n:0 for n in ENTRIES}
 sdk_rp=BASE/'sdk-fstorage/report.json';sdk_obj=BASE/'sdk-fstorage/fstorage.o'
 if real_sdk:assert sha(sdk_obj)==json.loads(sdk_rp.read_text())['units'][0]['object_sha256']
 with tempfile.TemporaryDirectory() as directory:
  t=Path(directory);ld=t/'layout.ld';elf=t/'test.elf';binary=t/'text.bin';ld.write_text('SECTIONS { .r1.flash.pending 0x20006f96 (NOLOAD) : { *(.r1.flash.pending) } .text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } /DISCARD/ : { *(.comment) *(.note*) } }')
  apis={'nrf_fstorage_erase':0x78c4c,'nrf_fstorage_write':0x78dac,'nrf_fstorage_is_busy':0x78c80,'nrf_sdh_evts_poll':0x7a4b4,'r1_native_watchdog_hw_feed':0x500fc,'osDelay':0x7d154};defs={n:0x100e001+i*16 for i,n in enumerate(apis) if not (real_sdk and n.startswith('nrf_fstorage_'))};defs['r1_internal_flash_context']=CONTEXT
  if real_sdk:defs.update(__start_fs_data=CONTEXT,__stop_fs_data=CONTEXT+40)
  subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--entry=r1_internal_flash_page_erase',*['--defsym='+n+'='+hex(a) for n,a in defs.items()],str(obj),*([str(sdk_obj)] if real_sdk else []),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True)
  syms={x.split()[-1]:int(x.split()[0],16) for x in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x.split())==3};assert syms['r1_internal_flash_pending']==0x20006f96
  stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
  for u in (stock,candidate):u.mem_map(0x20000,0xc0000);u.mem_map(0x1000000,0x10000);u.mem_map(0x10000000,0x1000);u.mem_map(0x20000000,0x40000)
  stock.mem_write(0x27000,app.read_bytes());candidate.mem_write(0x1000000,binary.read_bytes());stock.reg_write(UC_ARM_REG_SP,0x2003f000);stock.emu_start(0x283a1,0x27208,count=2000000);assert stock.reg_read(UC_ARM_REG_PC)==0x27208 and bytes(stock.mem_read(0x20006f96,1))==b'\0'
  api_names={a:n for n,a in apis.items() if not (real_sdk and n.startswith('nrf_fstorage_'))};api_names.update({defs[n]&~1:n for n in apis if n in defs})
  if real_sdk:api_names.update({0x100f100:'nrf_fstorage_erase',0x100f110:'nrf_fstorage_write',0x100f120:'nrf_fstorage_is_busy'})
  def hook(u,address,size,user):
   if address not in api_names:return
   f=states[id(u)];name=api_names[address];a=[u.reg_read(reg) for reg in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)];pending=bytes(u.mem_read(0x20006f96,1))[0]
   if name in ('nrf_fstorage_erase','nrf_fstorage_write'):
    vals=a if name.endswith('erase') else a+list(struct.unpack('<I',bytes(u.mem_read(u.reg_read(UC_ARM_REG_SP),4))));f['trace'].append((name,vals,pending));result=f['result'];f['busy_left']=f['busy']
    if f['mutation']&1:u.mem_write(CONTEXT+12,struct.pack('<I',0xfffffff0))
    if f['mutation']&2:u.mem_write(0x10000010,struct.pack('<I',17))
   elif name=='nrf_fstorage_is_busy':
    result=int(f['busy_left']>0);f['busy_left']-=result;f['trace'].append((name,a[0],result,pending))
   else:
    f['trace'].append((name,a[0] if name=='osDelay' else None,pending));result=0xffffffff
    if name=='nrf_sdh_evts_poll' and f['mutation']&4:u.mem_write(0x20006f96,b'\0')
   u.reg_write(UC_ARM_REG_R0,result);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  for u in (stock,candidate):u.hook_add(UC_HOOK_CODE,hook)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  seed=bytes((i*37+19)&255 for i in range(2048))
  def run(u,name,n=24,offset=0,base=SOURCE,page=4096,result=0,busy=0,mutation=0,pending=0,event_id=0,event_result=0,destination=OUT,context=CONTEXT):
   u.mem_write(CONTEXT,struct.pack('<5I',0x20005000 if real_sdk else 0,0x20005100 if real_sdk else 0,0,base,0xf8000));
   if real_sdk:
    u.mem_write(CONTEXT+20,bytes(20));u.mem_write(0x20005000,struct.pack('<8I',0,0,0,0x100f111,0x100f101,0,0,0x100f121));u.mem_write(0x20005100,struct.pack('<III',page,4,0))
   u.mem_write(0x10000010,struct.pack('<I',page));u.mem_write(0x20006f95,bytes([0x73,pending,0x91]));u.mem_write(EVENT,struct.pack('<6I',event_id,event_result,0x12345678,SOURCE,n,0));u.mem_write(OUT-4,b'LEFT'+bytes([0xa7])*2048+b'RGHT');u.mem_write(SOURCE-4,b'LEFT'+seed+b'RGHT');f=dict(trace=[],result=result,busy=busy,busy_left=busy,mutation=mutation);states[id(u)]=f
   args=(offset,n) if name.endswith('erase') else (SOURCE,n,offset) if name.endswith('write') else (destination,n,offset) if name.endswith('read') else (EVENT,) if name.endswith('handler') else (context,)
   u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
   for reg,v in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2),args):u.reg_write(reg,v)
   for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
   u.emu_start((ENTRIES[name] if u is stock else syms[name])|1,0x20000100,count=200000)
   assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
   assert bytes(u.mem_read(0x20006f95,1))==b'\x73' and bytes(u.mem_read(0x20006f97,1))==b'\x91'
   for p in (OUT,SOURCE):assert bytes(u.mem_read(p-4,4))==b'LEFT' and bytes(u.mem_read(p+2048,4))==b'RGHT'
   value=u.reg_read(UC_ARM_REG_R0) if name.endswith(('erase','write')) else None
   return value,bytes(u.mem_read(0x20006f96,1)),bytes(u.mem_read(CONTEXT,20)),bytes(u.mem_read(OUT,2048)),bytes(u.mem_read(SOURCE,2048)),f['trace']
  def compare(name,**kw):
   a=run(stock,name,**kw);b=run(candidate,name,**kw);assert a==b,(name,kw,a,b);counts[name]+=1
  for page in (1,4,17,4096,0x80000000,0xffffffff):
   lengths=sorted(set([0,1,page-1,page,0xffffffff]+[v for v in (page+1,page*2,page*2+1) if v<=0xffffffff]))
   for n in lengths:
    if (n+page-1)//page>5:continue
    for offset,base,result,busy,mutation in itertools.product((0,0xfffffffc),(0xd4000,0xffffffff),(0,8,0xffffffff),(0,2),range(8)):compare('r1_internal_flash_page_erase',n=n,page=page,offset=offset,base=base,result=result,busy=busy,mutation=mutation)
  for n in list(range(4100))+[0x10000,0x80000000,0xfffffffc,0xfffffffd,0xffffffff]:
   for result in (0,8,0xffffffff):compare('r1_internal_flash_word_write',n=n,result=result)
  for n,result,busy,mutation,offset,base in itertools.product((0,1,4,5,0xffffffff),(0,1),(0,1,3),range(8),(0,0xffffffff),(0xd4000,0xfffffffc)):compare('r1_internal_flash_word_write',n=n,result=result,busy=busy,mutation=mutation,offset=offset,base=base)
  for n in range(513):
   compare('r1_internal_flash_mapped_read',n=n);compare('r1_internal_flash_mapped_read',n=n,destination=SOURCE+1);compare('r1_internal_flash_mapped_read',n=n,offset=4,destination=SOURCE)
  for n in (0,1,17,512):compare('r1_internal_flash_mapped_read',n=n,base=0xfffffff0,offset=SOURCE+16)
  for event_id,event_result,pending in itertools.product(range(256),(0,1,0xffffffff),(0,1,2,255)):compare('r1_internal_flash_event_handler',event_id=event_id,event_result=event_result,pending=pending)
  for event_id,pending in itertools.product((0x100,0x101,0x102,0xffffff02,0xffffffff),range(256)):compare('r1_internal_flash_event_handler',event_id=event_id,pending=pending)
  for busy,mutation,pending,context in itertools.product(range(9),range(8),(0,1,255),(0,CONTEXT)):compare('r1_internal_flash_wait',busy=busy,mutation=mutation,pending=pending,context=context)
 receipt.write_text(json.dumps(dict(application_sha256=sha(app),report_sha256=sha(rp),object_sha256=sha(obj),comparisons=sum(counts.values()),actual_sdk_fstorage_facades_executed=real_sdk,sdk_report_sha256=sha(sdk_rp) if real_sdk else None,comparisons_by_entry=counts,cold_zero_bytes_compared=1,scope='Native page/word rounding and wrap, ignored erase errors versus rejected writes, bounded multi-page loops, exact wait/poll/watchdog/delay sequence, mapped forward byte-copy including overlap, event low-byte IDs/results and pending flag, guards/registers',limitations=['Nonzero page size and bounded erase iteration counts are covered; C division by zero is not a portable native contract.','SDK busy replies are canonical bool0/1; API callbacks, polling, watchdog and delay results are fixtures. SDK facades execute actual C only in integration mode. Poll-time pending mutation is controlled, not a real SDK interrupt.','Mapped copy ranges are bounded; invalid pointers, real flash persistence, scheduling, original compiler/link identity and full image remain unproven.'],instruction_identity_proven=False),indent=2)+'\n');print(sum(counts.values()),'lower internal-flash comparisons passed')
if __name__=='__main__':main()
