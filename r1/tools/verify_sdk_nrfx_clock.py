#!/usr/bin/env python3
"""Native nrfx clock versus pinned C, executing all HAL/NVIC bodies."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_MEM_WRITE,UC_HOOK_MEM_READ
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();STATE=0x20007938;CLOCK=0x40000000;NVIC=0xe000e000
ENTRIES={'nrfx_clock_init':(0x7a66c,28),'nrfx_clock_enable':(0x7a640,34),'nrfx_clock_lfclk_start':(0x7a68c,26),'nrfx_clock_lfclk_stop':(0x7a6ac,38)}
def main():
 out=BASE/'sdk-nrfx-clock';rp=out/'report.json';r=json.loads(rp.read_text());obj=out/'nrfx-clock.o';receipt=out/'verification.json';receipt.unlink(missing_ok=True);assert sha(obj)==r['selected_object_sha256'] and not r['remaining_symbols']
 for p,d in r['inputs'].items():assert sha(ROOT/p)==d,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';blob=app.read_bytes();ep=out/'evidence.json';e=json.loads(ep.read_text());assert e['application_sha256']==sha(app)
 for row in e['functions']:
  p=out/row['ghidra_file'];assert sha(p)==row['ghidra_sha256'];a=int(row['entry'],16);assert bytes(json.loads(p.read_text())['data'])==blob[a-0x27000:a-0x27000+row['body_bytes']]
 states={};comparisons=0;status_reads=0
 with tempfile.TemporaryDirectory() as directory:
  t=Path(directory);ld=t/'layout.ld';elf=t/'test.elf';binary=t/'text.bin';ld.write_text('SECTIONS { .bss.r1_sdk_nrfx_clock_control 0x20007938 (NOLOAD) : { *(.bss.r1_sdk_nrfx_clock_control) } .text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } /DISCARD/ : { *(.comment) *(.note*) } }')
  subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--entry=nrfx_clock_init',str(obj),'-o',str(elf)],check=True,capture_output=True);assert not subprocess.check_output(['arm-none-eabi-nm','-u',str(elf)],text=True).strip();subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True);syms={x.split()[-1]:int(x.split()[0],16) for x in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x.split())==3};assert syms['r1_sdk_nrfx_clock_control']==STATE
  stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
  for u in (stock,candidate):u.mem_map(0x20000,0xc0000);u.mem_map(0x1000000,0x10000);u.mem_map(0x20000000,0x40000);u.mem_map(CLOCK,4096);u.mem_map(NVIC,4096)
  stock.mem_write(0x27000,blob);candidate.mem_write(0x1000000,binary.read_bytes());stock.reg_write(UC_ARM_REG_SP,0x2003f000);stock.emu_start(0x283a1,0x27208,count=2000000);assert stock.reg_read(UC_ARM_REG_PC)==0x27208 and bytes(stock.mem_read(STATE,8))==bytes(candidate.mem_read(STATE,8))==bytes(8)
  def write(u,access,a,size,value,user):
   if CLOCK<=a<CLOCK+4096 or NVIC<=a<NVIC+4096:states[id(u)]['trace'].append(('write',a,size,value))
  def read(u,access,a,size,value,user):
   nonlocal status_reads
   if CLOCK<=a<CLOCK+4096 or NVIC<=a<NVIC+4096:
    f=states[id(u)]
    if a==CLOCK+0x418:
     i=f['status_index'];f['status_index']+=1;status_reads+=1;v=(f['other']&~0x10000)|(0x10000 if i<f['busy_reads'] else 0);u.mem_write(a,struct.pack('<I',v))
    f['trace'].append(('read',a,size,bytes(u.mem_read(a,size))))
  for u in (stock,candidate):u.hook_add(UC_HOOK_MEM_WRITE,write);u.hook_add(UC_HOOK_MEM_READ,read)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  def run(u,name,arg,initialized,hf,cal,irq,busy,other):
   states[id(u)]=dict(trace=[],status_index=0,busy_reads=busy,other=other);u.mem_write(STATE-4,b'\xa7'*4+struct.pack('<I4B',0x12345679,initialized,hf,cal,0xc9)+b'\xb8'*4);u.mem_write(CLOCK,bytes([0x6d])*4096);u.mem_write(NVIC,bytes([0x9a])*4096);u.mem_write(NVIC+0x100,struct.pack('<I',irq));u.reg_write(UC_ARM_REG_PRIMASK,0);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101);u.reg_write(UC_ARM_REG_R0,arg)
   for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
   u.emu_start((ENTRIES[name][0] if u is stock else syms[name])|1,0x20000100,count=100000)
   assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
   return u.reg_read(UC_ARM_REG_R0) if name=='nrfx_clock_init' else None,bytes(u.mem_read(STATE-4,16)),bytes(u.mem_read(CLOCK,4096)),bytes(u.mem_read(NVIC,4096)),states[id(u)]['trace'],states[id(u)]['status_index']
  for name,initialized,hf,cal,irq,arg in itertools.product(ENTRIES,(0,1),(0,1),(0,1,255),(0,1,0xfffffffe,0xffffffff),(0,1,0x100ed01,0xffffffff)):
   args=(name,arg,initialized,hf,cal,irq,0,0);a=run(stock,*args);b=run(candidate,*args);assert a==b,(args,a,b);comparisons+=1
  for busy,other,irq in itertools.product(range(9),(0,1,0xffff,0x80000000,0xffffffff),(0,1)):
   args=('nrfx_clock_lfclk_stop',0,1,1,255,irq,busy,other);a=run(stock,*args);b=run(candidate,*args);assert a==b,(args,a,b);comparisons+=1
 receipt.write_text(json.dumps(dict(application_sha256=sha(app),report_sha256=sha(rp),native_evidence_sha256=sha(ep),selected_object_sha256=sha(obj),comparisons=comparisons,lf_status_reads_per_implementation=status_reads//2,source_owned_cold_zero_bytes=8,scope='All four nrfx clock APIs execute pinned HAL/NVIC helpers without code/SVC fixtures; exact register read/write traces, control state, ABI, start/stop ordering and bounded LFSTAT transitions',limitations=['MMIO models register values and bounded LFSTAT transitions; this is not physical hardware timing or analog oscillator proof.','Canonical bool states only; nonterminating stop loops and interrupt races remain unproven.','O0 preserves native eight-byte state layout; original compiler instructions and full-image linking/byte equality remain open.'],instruction_identity_proven=False),indent=2)+'\n');print(comparisons,'nrfx clock comparisons;',status_reads//2,'LF status reads')
if __name__=='__main__':main()
