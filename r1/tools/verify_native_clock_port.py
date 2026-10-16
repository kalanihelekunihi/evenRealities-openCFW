#!/usr/bin/env python3
"""Differential RTC request ABI; actual source registry, bounded device fixtures."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ENTRIES={'r1_clock_rtc_write':0x50df0,'r1_clock_rtc_bind':0x50de0,'r1_clock_backend_slot12':0x50d82,'r1_clock_backend_update':0x50db6,'r1_clock_backend_bind_tick':0x50daa}
def main():
 out=BASE/'native-clock-port';rp=out/'report.json';r=json.loads(rp.read_text());objects=[out/'clock-port.o',BASE/'i2c5/stock_registry.o',BASE/'structured-time/structured_time.o',BASE/'runtime/memory-runtime.o'];reports={}
 for directory in ('native-clock-port','i2c5','structured-time','runtime'):reports[directory+'/report.json']=sha(BASE/directory/'report.json')
 assert sha(objects[0])==r['selected_object_sha256']
 for p,d in r['inputs'].items():assert sha(ROOT/p)==d,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 count=0
 with tempfile.TemporaryDirectory() as directory:
  t=Path(directory);ld=t/'layout.ld';elf=t/'test.elf';binary=t/'text.bin';ld.write_text('SECTIONS { .r1.time.rtc 0x20007690 (NOLOAD) : { *(.r1.time.rtc) } .text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } /DISCARD/ : { *(.comment) *(.note*) } }');subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--gc-sections',*['--undefined='+n for n in ENTRIES],*map(str,objects),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True);syms={x.split()[-1]:int(x.split()[0],16) for x in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x.split())==3}
  stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB);traces={};status=0;value=0
  for u in (stock,candidate):u.mem_map(0x20000,0xc0000);u.mem_map(0x1000000,0x10000);u.mem_map(0x20000000,0x40000)
  stock.mem_write(0x27000,app.read_bytes());candidate.mem_write(0x1000000,binary.read_bytes())
  def hook(u,a,size,user):
   if a!=0x100ef00:return
   args=[u.reg_read(v) for v in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)];assert args[:2]==[0x20002000,0]
   if kind=='bind':traces[id(u)].append(('bind',args[2]))
   else:
    assert args[3]==0;traces[id(u)].append((kind,bytes(u.mem_read(args[2],64))))
    if kind=='read':u.mem_write(args[2]+56,struct.pack('<Q',value))
   u.reg_write(UC_ARM_REG_R0,status);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  for u in (stock,candidate):u.hook_add(UC_HOOK_CODE,hook)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  for name,epoch,offset,status,value,missing in itertools.product(ENTRIES,(0,1,0xffffffff),(0,480,0xffff8000,0x12345678),(0,1,0xffffffff),(0,0x12345678abcdef01),(False,True)):
   kind='read' if name.endswith('slot12') else 'bind' if 'bind' in name else 'write';results=[]
   for u in (stock,candidate):
    traces[id(u)]=[];u.mem_write(0x20007690,struct.pack('<I',0x20002000));u.mem_write(0x20002000,struct.pack('<6I',0,0x20002100,0,0,0,0));ops=[0]*9
    if not missing:ops[{'read':4,'write':5,'bind':8}[kind]]=0x100ef01
    u.mem_write(0x20002100,struct.pack('<9I',*ops));args=(epoch,offset,0x87654321,0x12345679) if name!='r1_clock_rtc_bind' else (epoch,0,0,0)
    u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
    for reg,v in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),args):u.reg_write(reg,v)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    u.emu_start((ENTRIES[name] if u is stock else syms[name])|1,0x20000100,count=10000);assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(v) for v in saved]==[0x12345600+i for i in range(8)]
    results.append((u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1) if kind=='read' else None,traces[id(u)]))
   assert results[0]==results[1],(name,epoch,offset,status,value,missing,results);count+=1
 (out/'verification.json').write_text(json.dumps(dict(application_sha256=sha(app),report_sha256=sha(rp),provider_reports=reports,provider_objects={str(p.relative_to(BASE)):sha(p) for p in objects},comparisons=count,scope='Actual source registry dispatch and memory; device operation fixtures; complete 64-byte request, low16 timezone, ignored status, 64-bit read, absent operation',limitations=['RTC device bodies and calendar backend slots20/24 remain unresolved. No physical RTC or instruction identity proof.']),indent=2)+'\n');print(count,'RTC port comparisons')
if __name__=='__main__':main()
