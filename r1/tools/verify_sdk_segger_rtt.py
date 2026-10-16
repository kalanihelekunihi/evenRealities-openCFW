#!/usr/bin/env python3
"""Native R1 RTT initialization and pinned SEGGER ring-write contracts."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();CB=0x2002e62c
FIELDS={'_SEGGER_RTT':(CB,120),'r1_rtt_up_buffer':(CB+120,512),'r1_rtt_down_buffer':(CB+632,64)}
SECTIONS={'.bss._SEGGER_RTT':CB,'.r1.rtt.up':CB+120,'.r1.rtt.down':CB+632,'.r1.rtt.terminal':0x36dbc,'.r1.rtt.identifier':0x9ca04}
def main():
 out=BASE/'sdk-segger-rtt';rp=out/'report.json';r=json.loads(rp.read_text());obj=out/'segger-rtt.o';receipt=out/'verification.json';receipt.unlink(missing_ok=True);assert sha(obj)==r['selected_object_sha256']
 for p,d in r['inputs'].items():assert sha(ROOT/p)==d,p
 mr=BASE/'runtime/report.json';mo=mr.parent/'memory-runtime.o';assert sha(mo)==json.loads(mr.read_text())['relocatable_sha256'];app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';comparisons=0
 with tempfile.TemporaryDirectory() as directory:
  t=Path(directory);ld=t/'layout.ld';elf=t/'test.elf';binary=t/'text.bin';ld.write_text('SECTIONS { '+''.join(n+' '+hex(a)+(' (NOLOAD)' if n not in ('.r1.rtt.terminal','.r1.rtt.identifier') else '')+' : { *('+n+') } ' for n,a in SECTIONS.items())+'.text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } /DISCARD/ : { *(.comment) *(.note*) } }');subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--gc-sections','--undefined=SEGGER_RTT_Init','--undefined=SEGGER_RTT_WriteNoLock',str(obj),str(mo),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True);syms={x.split()[-1]:int(x.split()[0],16) for x in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x.split())==3}
  stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
  for u in (stock,candidate):u.mem_map(0x20000,0xc0000);u.mem_map(0x1000000,0x10000);u.mem_map(0x20000000,0x40000)
  stock.mem_write(0x27000,app.read_bytes());candidate.mem_write(0x1000000,binary.read_bytes());stock.reg_write(UC_ARM_REG_SP,0x2003f000);stock.emu_start(0x283a1,0x27208,count=2000000);assert stock.reg_read(UC_ARM_REG_PC)==0x27208
  for n,(a,z) in FIELDS.items():assert syms[n]==a and bytes(stock.mem_read(a,z))==bytes(candidate.mem_read(a,z))==bytes(z)
  for section,a,z in [('.r1.rtt.terminal',0x36dbc,9),('.r1.rtt.identifier',0x9ca04,16)]:
   p=t/(str(a)+'.bin');subprocess.run(['arm-none-eabi-objcopy','--dump-section',section+'='+str(p),str(elf)],check=True);payload=p.read_bytes();assert len(payload)==z and payload==bytes(stock.mem_read(a,z));candidate.mem_write(a,payload)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  def call(native,name,args=()):
   nonlocal comparisons
   results=[]
   for u in (stock,candidate):
    u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
    for reg,v in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),args):u.reg_write(reg,v)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    u.emu_start((native if u is stock else syms[name])|1,0x20000100,count=300000);assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)],(name,args)
    results.append((u.reg_read(UC_ARM_REG_R0) if name=='SEGGER_RTT_WriteNoLock' else None,bytes(u.mem_read(CB,696)),bytes(u.mem_read(0x20002000,2048))))
   assert results[0]==results[1],(hex(native),name,args,results);comparisons+=1
  for fill,native in itertools.product(range(256),(0x36d68,0x31948)):
   for u in (stock,candidate):u.mem_write(CB,bytes([fill])*696)
   call(native,'SEGGER_RTT_Init');call(native,'SEGGER_RTT_Init')
  for size,idx,rd,wr,mode,length in itertools.product((2,7,16,64),(0,1),(0,1,3),(0,1,3),(0,1,2,3,0xffffffff),(0,1,2,3,8,63,64,65)):
   if rd>=size or wr>=size:continue
   avail=(rd-wr-1)%size
   if mode==2 and length>avail:continue
   for u in (stock,candidate):
    u.mem_write(CB,bytes([0xa7])*120);u.mem_write(CB+24+idx*24,struct.pack('<6I',0,0x20002000,size,wr,rd,mode));u.mem_write(0x20002000,bytes([0x96])*2048);u.mem_write(0x20003000,bytes(range(256)))
   call(0x31a18,'SEGGER_RTT_WriteNoLock',(idx,0x20003000,length))
 receipt.write_text(json.dumps(dict(application_sha256=sha(app),report_sha256=sha(rp),memory_report_sha256=sha(mr),comparisons=comparisons,cold_zero_bytes=696,terminal_name_bytes=9,reverse_identifier_bytes=16,scope='Native full-clear init and init thunk over all byte fills; pinned no-lock write skip/trim/invalid modes, wrap and blocking mode with sufficient free space on two channels',limitations=['Blocked writes awaiting debugger consumption and concurrent host/device accesses are not tested.','SDK generic initializer differs and is excluded; native reverse-identifier bytes and copy order are source-owned; original compiler instruction identity remains unproven.','Other SEGGER wrappers/read API bodies, whole-image startup/linking, physical debugger behavior and byte equality remain gates.'],instruction_identity_proven=False),indent=2)+'\n');print(comparisons,'SEGGER RTT comparisons')
if __name__=='__main__':main()
