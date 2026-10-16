#!/usr/bin/env python3
"""Returning fatal logger: exact native dynamic mode and producer contracts."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=BASE/'native-rtc-error';rp=out/'report.json';r=json.loads(rp.read_text());obj=out/'rtc-error.o';assert sha(obj)==r['selected_object_sha256']
 for p,d in r['inputs'].items():assert sha(ROOT/p)==d,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';states={};count=0
 with tempfile.TemporaryDirectory() as directory:
  t=Path(directory);ld=t/'layout.ld';elf=t/'test.elf';binary=t/'text.bin';ld.write_text('SECTIONS { .r1.rtc.error.ring 0x4e604 : { *(.r1.rtc.error.ring) } .r1.rtc.error.nordic 0x4e630 : { *(.r1.rtc.error.nordic) } .text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } /DISCARD/ : { *(.comment) *(.note*) } }');subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--defsym=r1_structured_log_mode_get=0x100ee01','--defsym=r1_structured_log_format=0x100ee11','--defsym=nrf_log_frontend_std_1=0x100ee21',str(obj),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True);syms={x.split()[-1]:int(x.split()[0],16) for x in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x.split())==3}
  stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
  for u in (stock,candidate):u.mem_map(0x20000,0xc0000);u.mem_map(0x1000000,0x10000);u.mem_map(0x20000000,0x40000)
  stock.mem_write(0x27000,app.read_bytes());candidate.mem_write(0x1000000,binary.read_bytes());descriptor_bytes=0
  for section,address in [('.r1.rtc.error.ring',0x4e604),('.r1.rtc.error.nordic',0x4e630)]:
   p=t/(section+'.bin');subprocess.run(['arm-none-eabi-objcopy','--dump-section',section+'='+str(p),str(elf)],check=True);data=p.read_bytes();assert data==bytes(stock.mem_read(address,len(data)));candidate.mem_write(address,data);descriptor_bytes+=len(data)
  def cstr(u,p):return bytes(u.mem_read(p,80)).split(b'\0',1)[0]
  def hook(u,a,size,user):
   f=states[id(u)];kind={0x914ec:'mode',0x91638:'format',0x799c8:'std1',0x100ee00:'mode',0x100ee10:'format',0x100ee20:'std1'}.get(a)
   if not kind:return
   args=[u.reg_read(reg) for reg in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)]
   if kind=='mode':value=f['modes'][f['reads']];f['reads']+=1;f['trace'].append(('mode',value));u.reg_write(UC_ARM_REG_R0,value)
   elif kind=='format':assert args[0]==0x04400000 and args[1]==args[2]==0x4e604;f['trace'].append(('format',args[0],cstr(u,args[1]),args[3]));u.reg_write(UC_ARM_REG_R0,0)
   else:assert args[0]==0x001c0001 and args[1]==0x4e630;f['trace'].append(('std1',args[0],cstr(u,args[1]),args[2]));u.reg_write(UC_ARM_REG_R0,0)
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  for u in (stock,candidate):u.hook_add(UC_HOOK_CODE,hook)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  for modes,error in itertools.product(itertools.product(range(8),repeat=3),(0,1,8,0x87654321,0xffffffff)):
   results=[]
   for u in (stock,candidate):
    states[id(u)]={'trace':[],'reads':0,'modes':modes};u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101);u.reg_write(UC_ARM_REG_R0,error)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    u.emu_start((0x4e5bc if u is stock else syms['r1_rtc_driver_error'])|1,0x20000100,count=10000);assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(v) for v in saved]==[0x12345600+i for i in range(8)];results.append(states[id(u)]['trace'])
   assert results[0]==results[1],(modes,error,results);count+=1
 (out/'verification.json').write_text(json.dumps(dict(application_sha256=sha(app),report_sha256=sha(rp),comparisons=count,descriptor_bytes=descriptor_bytes,scope='Native returning fatal-error helper, all three-read mode sequences, exact structured/std1 producer words and strings; lower logging fixtures',limitations=['Actual logging transports, IRQ concurrency and hardware are unproven. Native void-return register residue is not an ISO return-value contract.']),indent=2)+'\n');print(count,'fatal-error logger comparisons;',descriptor_bytes,'string bytes')
if __name__=='__main__':main()
