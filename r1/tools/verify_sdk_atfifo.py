#!/usr/bin/env python3
"""Pinned FIFO/exclusive primitives against native code, including controlled retries."""
import hashlib,itertools,json,struct,subprocess,tempfile,re
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ENTRIES={'nrf_atfifo_init':0x77f40,'nrf_atfifo_clear':0x77f30,'nrf_atfifo_item_alloc':0x77f66,'nrf_atfifo_item_free':0x77f7c,'nrf_atfifo_item_get':0x77f92,'nrf_atfifo_item_put':0x77fa8,'nrf_atfifo_wspace_req':0x272b8,'nrf_atfifo_wspace_close':0x272f0,'nrf_atfifo_rspace_req':0x27302,'nrf_atfifo_rspace_close':0x2733c,'nrf_atfifo_space_clear':0x2734e,'nrf_atomic_flag_set_fetch':0x78074,'nrf_atomic_u32_fetch_or':0x780a6}
FIFO=0x20001000;CTX=0x20001100;BUFFER=0x20002000;WORD=0x20003000
REGS={**{'r'+str(i):getattr(__import__('unicorn.arm_const',fromlist=['*']),'UC_ARM_REG_R'+str(i)) for i in range(13)},'ip':UC_ARM_REG_R12,'lr':UC_ARM_REG_LR}
def main():
 out=BASE/'sdk-atfifo';rp=out/'report.json';obj=out/'atfifo-atomic.o';r=json.loads(rp.read_text());receipt=out/'verification.json';receipt.unlink(missing_ok=True);assert sha(obj)==r['selected_object_sha256']
 for p,d in r['inputs'].items():assert sha(ROOT/p)==d,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';states={};counts={n:0 for n in ENTRIES};forced=0
 with tempfile.TemporaryDirectory() as directory:
  t=Path(directory);ld=t/'layout.ld';elf=t/'test.elf';binary=t/'text.bin';ld.write_text('SECTIONS { .text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } /DISCARD/ : { *(.comment) *(.note*) } }')
  subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--entry=nrf_atfifo_init',str(obj),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True)
  syms={x.split()[-1]:int(x.split()[0],16) for x in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x.split())==3}
  def stores(path,extra=()):
   dis=subprocess.check_output(['arm-none-eabi-objdump','-d',*extra,str(path)],text=True);result={}
   for line in dis.splitlines():
    m=re.search(r'^\s*([0-9a-f]+):.*\bstrex\s+(r\d+|ip|lr),',line)
    if m:result[int(m[1],16)]=REGS[m[2]]
   return result
  candidate_stores=stores(elf);native_stores=stores(BASE/'i2c5/stock-analysis-exec.elf',('--start-address=0x272b8','--stop-address=0x273b2'));assert candidate_stores and native_stores
  stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
  for u in (stock,candidate):u.mem_map(0x20000,0xc0000);u.mem_map(0x1000000,0x10000);u.mem_map(0x20000000,0x40000)
  stock.mem_write(0x27000,app.read_bytes());candidate.mem_write(0x1000000,binary.read_bytes())
  def hook(u,address,size,user):
   f=states[id(u)];mapping=native_stores if u is stock else candidate_stores
   if address not in mapping or f['remaining']==0:return
   f['remaining']-=1;f['injections']+=1
   if f['mutate']:
    if f['name'].startswith('nrf_atomic_'):u.mem_write(WORD,struct.pack('<I',0xa5a50000))
    elif f['name'] in ('nrf_atfifo_wspace_req','nrf_atfifo_item_alloc'):u.mem_write(FIFO+4,struct.pack('<I',f['item']))
    elif f['name'] in ('nrf_atfifo_rspace_req','nrf_atfifo_item_get'):u.mem_write(FIFO+8,struct.pack('<I',f['item']<<16))
   u.reg_write(mapping[address],1);u.reg_write(UC_ARM_REG_PC,(address+4)|1)
  for u in (stock,candidate):u.hook_add(UC_HOOK_CODE,hook)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11];seed=bytes((i*37+19)&255 for i in range(2048))
  def run(u,name,item=28,slots=5,hw=0,hr=0,tw=0,tr=0,context=0x12345678,buf_size=None,buffer=BUFFER,value=0,mask=1,fail=0,mutate=False):
   size=item*slots if buf_size is None else buf_size;u.mem_write(FIFO-4,b'LEFT'+struct.pack('<IIIHH',BUFFER,tw|(tr<<16),hw|(hr<<16),size,item)+b'RGHT');u.mem_write(CTX-4,b'LEFT'+struct.pack('<I',context)+b'RGHT');u.mem_write(BUFFER-4,b'LEFT'+seed+b'RGHT');u.mem_write(WORD-4,b'LEFT'+struct.pack('<I',value)+b'RGHT');f=dict(name=name,remaining=fail,injections=0,mutate=mutate,item=item);states[id(u)]=f
   args=(WORD,mask) if name.startswith('nrf_atomic_') else (FIFO,buffer,size,item) if name=='nrf_atfifo_init' else (FIFO,CTX)
   u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
   for reg,v in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),args):u.reg_write(reg,v)
   for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
   u.emu_start((ENTRIES[name] if u is stock else syms[name])|1,0x20000100,count=10000)
   assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
   for p,z in ((FIFO,16),(CTX,4),(BUFFER,2048),(WORD,4)):assert bytes(u.mem_read(p-4,4))==b'LEFT' and bytes(u.mem_read(p+z,4))==b'RGHT'
   assert f['injections']==fail,(name,fail,f)
   result=None if name.endswith(('wspace_close','rspace_close')) else u.reg_read(UC_ARM_REG_R0)
   return result,bytes(u.mem_read(FIFO,16)),bytes(u.mem_read(CTX,4)),bytes(u.mem_read(WORD,4)),bytes(u.mem_read(BUFFER,2048)),f['injections']
  def compare(name,**kw):
   nonlocal forced
   a=run(stock,name,**kw);b=run(candidate,name,**kw);assert a==b,(name,kw,a,b);counts[name]+=1;forced+=kw.get('fail',0)
  for size,item,buffer in itertools.product(list(range(1025))+[32767,32768,65534,65535],(1,2,3,4,28,255),(0,BUFFER)):compare('nrf_atfifo_init',buf_size=size,item=item,buffer=buffer)
  fifo_names=[n for n in ENTRIES if n.startswith('nrf_atfifo_') and n!='nrf_atfifo_init']
  for item,slots in itertools.product((1,4,28),(2,5)):
   for hw,hr,tw,tr in itertools.product(range(slots),repeat=4):
    for name in fifo_names:compare(name,item=item,slots=slots,hw=hw*item,hr=hr*item,tw=tw*item,tr=tr*item)
  values=sorted(set([0,1,0xffffffff,0x80000000,0xa5a55a5a]+[1<<i for i in range(32)]+[0xffffffff^(1<<i) for i in range(32)]+[(i*2654435761)&0xffffffff for i in range(128)]))
  for name,value,mask in itertools.product(('nrf_atomic_flag_set_fetch','nrf_atomic_u32_fetch_or'),values,(0,1,2,0x80000000,0xffffffff)):compare(name,value=value,mask=mask)
  for name in fifo_names+['nrf_atomic_flag_set_fetch','nrf_atomic_u32_fetch_or']:
   kw=dict(hw=84,hr=84,tw=0,tr=0,context=0) if name in ('nrf_atfifo_wspace_req','nrf_atfifo_item_alloc') else dict(hw=0,hr=0,tw=56,tr=56,context=0)
   for fail in (1,2):compare(name,fail=fail,**kw)
   if name in ('nrf_atfifo_wspace_req','nrf_atfifo_item_alloc','nrf_atfifo_rspace_req','nrf_atfifo_item_get') or name.startswith('nrf_atomic_'):compare(name,fail=1,mutate=True,**kw)
 receipt.write_text(json.dumps(dict(application_sha256=sha(app),report_sha256=sha(rp),selected_object_sha256=sha(obj),comparisons=sum(counts.values()),comparisons_by_entry=counts,forced_exclusive_failures_per_implementation=forced,scope='Pinned FIFO init/clear/reserve/commit/read/release and flag/fetch OR, valid tag-position cross products, full-word atomic patterns, exclusive instructions actually executed, one/two forced STREX failures and intervening metadata/word mutations, guards/registers',limitations=['Forced STREX status and selected metadata changes are controlled interleavings, not physical interrupt or multicore/concurrency proof.','FIFO geometry/tag positions are bounded and aligned, item size nonzero; invalid-pointer and divide-by-zero behavior are not portable contracts.','Original compiler/instruction identity, complete firmware linking and physical behavior remain unproven.'],instruction_identity_proven=False),indent=2)+'\n');print(sum(counts.values()),'FIFO/atomic comparisons passed;',forced,'forced exclusive retries')
if __name__=='__main__':main()
