#!/usr/bin/env python3
"""Pinned Nordic panic traversal and native shared frontend state layout."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();DATA=0x2002d60c;SIZE=4128;HEAD=DATA+4112;BACKENDS=0x20002000;CONTROLS=0x20002200;API=0x20003000

def main():
 out=BASE/'sdk-logger-frontend';rp=out/'report.json';r=json.loads(rp.read_text());obj=out/'logger.o';receipt=out/'panic-verification.json';receipt.unlink(missing_ok=True);assert sha(obj)==r['selected_object_sha256']
 for p,d in r['inputs'].items():assert sha(ROOT/p)==d,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';ep=out/'evidence.json';e=json.loads(ep.read_text());assert e['application_sha256']==sha(app)
 for row in e['functions']:
  p=out/row['ghidra_file'];assert sha(p)==row['ghidra_sha256'];a=int(row['entry'],16);assert bytes(json.loads(p.read_text())['data'])==app.read_bytes()[a-0x27000:a-0x27000+row['body_bytes']]
 rr=out/e['rea_panic_receipt']['file'];assert sha(rr)==e['rea_panic_receipt']['sha256'];rea=json.loads(rr.read_text());assert rea['subject']['digest']['sha256']==sha(BASE/'i2c5/stock-analysis-exec.elf') and rea['normalized_result']['procedure']['body']['total_bytes']==38
 states={};comparisons=0;callbacks=0
 with tempfile.TemporaryDirectory() as directory:
  t=Path(directory);ld=t/'layout.ld';elf=t/'test.elf';binary=t/'text.bin';ld.write_text('SECTIONS { .bss.r1_sdk_logger_data 0x2002d60c (NOLOAD) : { *(.bss.r1_sdk_logger_data) } .text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } /DISCARD/ : { *(.comment) *(.note*) } }');subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--entry=nrf_log_panic','--gc-sections',str(obj),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True);syms={x.split()[-1]:int(x.split()[0],16) for x in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x.split())==3};assert syms['r1_sdk_logger_data']==DATA
  stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
  for u in (stock,candidate):u.mem_map(0x20000,0xc0000);u.mem_map(0x1000000,0x10000);u.mem_map(0x20000000,0x40000)
  stock.mem_write(0x27000,app.read_bytes());candidate.mem_write(0x1000000,binary.read_bytes());stock.reg_write(UC_ARM_REG_SP,0x2003f000);stock.emu_start(0x283a1,0x27208,count=2000000);assert stock.reg_read(UC_ARM_REG_PC)==0x27208 and bytes(stock.mem_read(DATA,SIZE))==bytes(candidate.mem_read(DATA,SIZE))==bytes(SIZE)
  def hook(u,a,size,user):
   nonlocal callbacks
   if a!=0x100ed00:return
   f=states[id(u)];backend=u.reg_read(UC_ARM_REG_R0);idx=(backend-BACKENDS)//32;assert idx in range(5) and backend==BACKENDS+idx*32;cb=CONTROLS+idx*16;f['trace'].append((idx,u.mem_read(DATA,1)[0],struct.unpack('<I',bytes(u.mem_read(HEAD,4)))[0],bytes(u.mem_read(cb,16))));callbacks+=1;f['calls']+=1
   if f['calls']==1:
    if f['mutation']==1:u.mem_write(cb,bytes(4))
    elif f['mutation']==2:u.mem_write(HEAD,struct.pack('<I',BACKENDS+128))
    elif f['mutation']==3:u.mem_write(cb,struct.pack('<I',BACKENDS+128))
   u.reg_write(UC_ARM_REG_R0,0xffffffff);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  for u in (stock,candidate):u.hook_add(UC_HOOK_CODE,hook)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  def run(u,chain,autoflush,enabled,mutation):
   states[id(u)]=dict(trace=[],calls=0,mutation=mutation);data=bytearray((i*37+11)&255 for i in range(SIZE));data[0]=autoflush;struct.pack_into('<I',data,4112,BACKENDS+chain[0]*32 if chain else 0);u.mem_write(DATA-4,b'\xa7'*4+bytes(data)+b'\xb8'*4);u.mem_write(API,struct.pack('<3I',0x100ed01,0x100ed01,0x100ed01))
   for i in range(5):
    u.mem_write(BACKENDS+i*32,struct.pack('<4I',API,0x12345678,0,CONTROLS+i*16)+b'\xc9'*16);cb=bytearray([0xa7]*16);struct.pack_into('<I',cb,0,BACKENDS+chain[chain.index(i)+1]*32 if i in chain and chain.index(i)+1<len(chain) else 0);cb[4]=i;cb[5]=enabled;u.mem_write(CONTROLS+i*16,bytes(cb))
   u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
   for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
   u.emu_start((0x79b1c if u is stock else syms['nrf_log_panic'])|1,0x20000100,count=100000);assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
   return states[id(u)]['trace'],bytes(u.mem_read(DATA-4,SIZE+8)),bytes(u.mem_read(BACKENDS,160)),bytes(u.mem_read(CONTROLS,80))
  for args in itertools.product([tuple(range(n)) for n in range(5)],(0,1,2,255),(0,1,2,255),range(4)):
   a=run(stock,*args);b=run(candidate,*args);assert a==b,(args,a,b);comparisons+=1
  for chain,auto,mutation in itertools.product(((1,0),(2,0,1),(3,1,0,2)),(0,255),range(4)):
   args=(chain,auto,0,mutation);a=run(stock,*args);b=run(candidate,*args);assert a==b,(args,a,b);comparisons+=1
  for auto in range(256):
   args=((0,1),auto,0,0);a=run(stock,*args);b=run(candidate,*args);assert a==b,(args,a,b);comparisons+=1
 receipt.write_text(json.dumps(dict(application_sha256=sha(app),report_sha256=sha(rp),native_evidence_sha256=sha(ep),comparisons=comparisons,callback_invocations_per_implementation=callbacks//2,source_owned_cold_zero_bytes=SIZE,scope='Pinned panic and backend helpers, four-kilobyte shared ring layout; autoflush/enable ordering, empty/permuted lists and callback next/head mutations',limitations=['Backend panic callbacks are fixtures; production backend registration/data and transport shutdown remain unproven.','The 4128-byte source footprint matches native cold RAM; fields unused by panic require their own dequeue/standard/init contracts.','Acyclic bounded lists only; complete frontend, concurrency, physical logger transport and image equality remain open.'],instruction_identity_proven=False),indent=2)+'\n');print(comparisons,'logger panic comparisons;',callbacks//2,'backend callbacks')
if __name__=='__main__':main()
