#!/usr/bin/env python3
"""Native RTC register, state and structured logging contracts versus pinned SDK."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();STATE=0x20007950;RTC=0x40024000;NVIC=0xe000e000;INPUT=0x20003000
ENTRIES={'nrfx_rtc_init':0x7ad6c,'nrfx_rtc_enable':0x7ad20,'nrfx_rtc_tick_enable':0x7ae4c,'r1_rtc_driver_initialize':0x7ad6c,'r1_rtc_driver_enable':0x7ad20,'r1_rtc_driver_tick_enable':0x7ae4c}
def main():
 out=BASE/'sdk-nrfx-rtc';rp=out/'report.json';r=json.loads(rp.read_text());obj=out/'nrfx-rtc.o';assert sha(obj)==r['selected_object_sha256']
 for p,d in r['inputs'].items():assert sha(ROOT/p)==d,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';states={};comparisons=0
 with tempfile.TemporaryDirectory() as directory:
  t=Path(directory);ld=t/'layout.ld';elf=t/'test.elf';binary=t/'text.bin';ld.write_text('SECTIONS { .r1.rtc.log.enabled 0x7ad5c : { *(.r1.rtc.log.enabled) } .r1.rtc.log.tick 0x7ae90 : { *(.r1.rtc.log.tick) } .r1.rtc.log.function 0x7ae28 : { *(.r1.rtc.log.function) } .bss.r1_sdk_rtc_control 0x20007950 (NOLOAD) : { *(.bss.r1_sdk_rtc_control) } .bss.r1_sdk_rtc_handlers 0x20007954 (NOLOAD) : { *(.bss.r1_sdk_rtc_handlers) } .text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } /DISCARD/ : { *(.comment) *(.note*) } }');bindings={'r1_structured_log_mode_get':0x100ee01,'r1_structured_log_format':0x100ee11,'nrf_strerror_get':0x100ee21};subprocess.run(['arm-none-eabi-ld','-T',str(ld),*['--defsym='+n+'='+hex(a) for n,a in bindings.items()],str(obj),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True);syms={x.split()[-1]:int(x.split()[0],16) for x in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x.split())==3};assert syms['r1_sdk_rtc_control']==STATE and syms['r1_sdk_rtc_handlers']==STATE+4
  stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
  for u in (stock,candidate):u.mem_map(0x20000,0xc0000);u.mem_map(0x1000000,0x10000);u.mem_map(0x20000000,0x40000);u.mem_map(RTC,4096);u.mem_map(NVIC,4096)
  stock.mem_write(0x27000,app.read_bytes());candidate.mem_write(0x1000000,binary.read_bytes());stock.reg_write(UC_ARM_REG_SP,0x2003f000);stock.emu_start(0x283a1,0x27208,count=2000000);assert stock.reg_read(UC_ARM_REG_PC)==0x27208;assert bytes(stock.mem_read(STATE,8))==bytes(candidate.mem_read(STATE,8))==bytes(8)
  for section,address in [('.r1.rtc.log.enabled',0x7ad5c),('.r1.rtc.log.tick',0x7ae90),('.r1.rtc.log.function',0x7ae28)]:
   p=t/(section+'.bin');subprocess.run(['arm-none-eabi-objcopy','--dump-section',section+'='+str(p),str(elf)],check=True);data=p.read_bytes();assert data==bytes(stock.mem_read(address,len(data)));candidate.mem_write(address,data)
  def cstr(u,p):
   data=bytes(u.mem_read(p,128));return data.split(b'\0',1)[0].decode()
  def hook(u,a,size,user):
   kind={0x914ec:'mode',0x91638:'format',0x7a5cc:'error',0x100ee00:'mode',0x100ee10:'format',0x100ee20:'error'}.get(a)
   if not kind:return
   f=states[id(u)];args=[u.reg_read(v) for v in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)]
   if kind=='mode':value=f['modes'][f['reads']%len(f['modes'])];f['reads']+=1;f['trace'].append(('mode',value));u.reg_write(UC_ARM_REG_R0,value)
   elif kind=='error':f['trace'].append(('error',args[0]));u.reg_write(UC_ARM_REG_R0,INPUT+96)
   else:
    data=(args[0],cstr(u,args[1]),cstr(u,args[2]));extra=()
    if args[0]==0x0c800000:extra=(cstr(u,args[3]),cstr(u,struct.unpack('<I',bytes(u.mem_read(u.reg_read(UC_ARM_REG_SP),4)))[0]))
    f['trace'].append(('format',data,extra));u.reg_write(UC_ARM_REG_R0,0)
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  def write(u,access,a,size,value,user):
   if RTC<=a<RTC+4096 or NVIC<=a<NVIC+4096:states[id(u)]['writes'].append((a,size,value))
  for u in (stock,candidate):u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_WRITE,write)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  for name,initial,modes,irq,priority,prescaler,reliable,tick,enable in itertools.product(ENTRIES,(0,1,2,255),((0,),(1,),(2,),(4,),(7,),(0,4,2),(1,0,4)),(36,), (0,6,7),(0,4095,65535),(0,1),(0,65,255),(0,1)):
   if name not in ('nrfx_rtc_init','r1_rtc_driver_initialize') and (priority,prescaler,reliable,tick)!=(0,0,0,0):continue
   results=[]
   for u in (stock,candidate):
    states[id(u)]={'trace':[],'writes':[],'reads':0,'modes':modes};u.mem_write(STATE,bytes([initial,0x96,0x79,0x88])+struct.pack('<I',0x12345679));u.mem_write(INPUT,struct.pack('<IbBBB',RTC,irq,0,4,0));u.mem_write(INPUT+16,struct.pack('<HBBB3x',prescaler,priority,tick,reliable));u.mem_write(INPUT+96,b'SUCCESS\0');u.mem_write(RTC,bytes([0x5a])*4096);u.mem_write(NVIC,bytes(4096));u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
    args=(INPUT,INPUT+16,0x12345679) if name in ('nrfx_rtc_init','r1_rtc_driver_initialize') else (INPUT,enable)
    for reg,v in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2),args):u.reg_write(reg,v)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    u.emu_start((ENTRIES[name] if u is stock else syms[name])|1,0x20000100,count=100000);assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(v) for v in saved]==[0x12345600+i for i in range(8)]
    results.append((u.reg_read(UC_ARM_REG_R0) if name in ('nrfx_rtc_init','r1_rtc_driver_initialize') else None,states[id(u)]['trace'],states[id(u)]['writes'],bytes(u.mem_read(STATE,8)),bytes(u.mem_read(RTC,4096)),bytes(u.mem_read(NVIC,4096))))
   assert results[0]==results[1],(name,initial,modes,priority,prescaler,reliable,tick,enable,[(i,results[0][i],results[1][i]) for i in range(6) if results[0][i]!=results[1][i]]);comparisons+=1
 (out/'verification.json').write_text(json.dumps(dict(application_sha256=sha(app),report_sha256=sha(rp),comparisons=comparisons,cold_zero_bytes=8,scope='Pinned SDK RTC init/enable/tick-enable, actual HAL/NVIC and native structured logging adapter; ordered MMIO writes, complete pages, driver state and dynamic logging modes',limitations=['Structured mode/format and error-string routines are bounded fixtures; physical timing, NVIC set/clear semantics, IRQ handler and startup sequence remain unproven.']),indent=2)+'\n');print(comparisons,'SDK RTC comparisons')
if __name__=='__main__':main()
