#!/usr/bin/env python3
"""Native and pinned SDK printf byte-stream/va-list/buffer contract comparisons."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();CTX=0x20002000;BUF=CTX+64;FMT=0x20003000;ARGV=FMT+1024;VA=ARGV+128;STR=FMT+1536
ENTRIES={'nrf_fprintf':0x78a40,'nrf_fprintf_fmt':0x78a72,'nrf_fprintf_buffer_flush':0x78a5a,'buffer_add':0x56744}
def main():
 out=BASE/'sdk-fprintf';rp=out/'report.json';r=json.loads(rp.read_text());receipt=out/'verification.json';receipt.unlink(missing_ok=True);obj=out/'fprintf.o';assert sha(obj)==r['selected_object_sha256']
 for p,d in r['inputs'].items():assert sha(ROOT/p)==d,p
 mr=BASE/'runtime/report.json';mo=mr.parent/'memory-runtime.o';assert sha(mo)==json.loads(mr.read_text())['relocatable_sha256'];app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';states={};comparisons=0;bytes_out=0
 with tempfile.TemporaryDirectory() as directory:
  t=Path(directory);ld=t/'layout.ld';elf=t/'test.elf';binary=t/'text.bin';ld.write_text('SECTIONS { .text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } /DISCARD/ : { *(.comment) *(.note*) } }');subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--entry=nrf_fprintf',str(obj),str(mo),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True);syms={x.split()[-1]:int(x.split()[0],16) for x in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x.split())==3}
  stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
  for u in (stock,candidate):u.mem_map(0x20000,0xc0000);u.mem_map(0x1000000,0x10000);u.mem_map(0x20000000,0x40000)
  stock.mem_write(0x27000,app.read_bytes());candidate.mem_write(0x1000000,binary.read_bytes());saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  def hook(u,a,size,user):
   nonlocal bytes_out
   if a!=0x100ed00:return
   ctx=u.reg_read(UC_ARM_REG_R0);p=u.reg_read(UC_ARM_REG_R1);n=u.reg_read(UC_ARM_REG_R2);assert p==BUF and 0<n<=64;payload=bytes(u.mem_read(p,n));states[id(u)].append((ctx,payload,struct.unpack('<I',bytes(u.mem_read(CTX+8,4)))[0]));bytes_out+=n;u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  for u in (stock,candidate):u.hook_add(UC_HOOK_CODE,hook)
  def compare(fmt,args=(),size=8,auto=0,prior=0,entry='nrf_fprintf',char=65):
   nonlocal comparisons
   results=[]
   for u in (stock,candidate):
    states[id(u)]=[];u.mem_write(CTX,struct.pack('<3IB3x2I',BUF,size,prior,auto,0x12345678,0x100ed01));u.mem_write(BUF,bytes([0xa7])*64);u.mem_write(FMT,(fmt or '').encode()+b'\0');u.mem_write(STR,b'Ab\nZ\0');values=list(args)+[0]*8;u.mem_write(ARGV,struct.pack('<8I',*values[:8]));u.mem_write(VA,struct.pack('<I',ARGV))
    def call(name,regs,stack=()):
     u.reg_write(UC_ARM_REG_SP,0x2003f000);u.mem_write(0x2003f000,struct.pack('<8I',*(list(stack)+[0]*8)[:8]));u.reg_write(UC_ARM_REG_LR,0x20000101)
     for reg,v in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),regs):u.reg_write(reg,v)
     for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
     u.emu_start((ENTRIES[name] if u is stock else syms[name])|1,0x20000100,count=300000);assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)],(name,fmt)
    if entry=='nrf_fprintf':call(entry,(CTX,FMT if fmt is not None else 0,values[0],values[1]),values[2:])
    elif entry=='nrf_fprintf_fmt':call(entry,(CTX,FMT if fmt is not None else 0,VA))
    elif entry=='buffer_add':call(entry,(CTX,char))
    else:call(entry,(CTX,))
    before=(bytes(u.mem_read(CTX,24)),bytes(u.mem_read(BUF,64)),struct.unpack('<I',bytes(u.mem_read(VA,4)))[0] if entry=='nrf_fprintf_fmt' else None);call('nrf_fprintf_buffer_flush',(CTX,));results.append((states[id(u)],before,bytes(u.mem_read(CTX,24)),bytes(u.mem_read(BUF,64))))
   assert results[0]==results[1],(fmt,args,size,auto,prior,entry,results);comparisons+=1
  formats=['%d','%i','%u','%x','%X','%p','%+d','%08d','%-12d','%.8d','%+012.8d','%08x','%12u','%-12u','%.0u','%ld','%hhd','%f:%d']
  for fmt,value,size,auto,entry in itertools.product(formats,(0,1,9,10,255,0x7fffffff,0x80000000,0xffffffff),(1,7,64),(0,1),('nrf_fprintf','nrf_fprintf_fmt')):compare(fmt,(value,123),size,auto,entry=entry)
  for fmt,args in [('plain\nCR\r\n',()),('%% / %c / %s',(10,STR)),('%12s/%-12s',(STR,STR)),('%d:%u:%x:%c:%s:%p',(0xffffffff,0xffffffff,0xabcd,90,STR,0x1234)),('',()),(None,())]:
   for size,auto,entry in itertools.product((1,2,7,64),(0,1),('nrf_fprintf','nrf_fprintf_fmt')):compare(fmt,args,size,auto,entry=entry)
  for size,auto,char in itertools.product((1,2,7,64),(0,1),range(256)):compare('',size=size,auto=auto,prior=size-1,entry='buffer_add',char=char)
  for size,prior in itertools.product((1,2,7,64),range(64)):
   if prior<=size:compare('',size=size,prior=prior,entry='nrf_fprintf_buffer_flush')
 receipt.write_text(json.dumps(dict(application_sha256=sha(app),report_sha256=sha(rp),memory_report_sha256=sha(mr),comparisons=comparisons,callback_bytes_per_implementation=bytes_out//2,configuration={'NRF_FPRINTF_FLAG_AUTOMATIC_CR_ON_LF_ENABLED':1,'NRF_FPRINTF_DOUBLE_ENABLED':0},scope='Actual SDK printf/va-list/flush/private byte writer, compiled strlen; exact buffered/callback bytes, flags/width/precision, signed extremes, strings and CR insertion',limitations=['Valid bounded formats, args and positive buffer sizes; null string arguments, unterminated formats and concurrent callbacks are not admitted.','Double formatting is disabled; unsupported specifier behavior is tested but no floating output is claimed.','Callbacks are byte sinks, not physical transport; original compiler/runtime identity, full image linking and byte equality remain unresolved.'],instruction_identity_proven=False),indent=2)+'\n');print(comparisons,'printf comparisons;',bytes_out//2,'callback bytes')
if __name__=='__main__':main()
