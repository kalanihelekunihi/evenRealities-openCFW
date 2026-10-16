#!/usr/bin/env python3
"""Nordic startup/RTC setup versus native with priority readback/clock/transfer fixtures."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE,UC_HOOK_MEM_INVALID
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ENTRIES={'xPortStartScheduler':0x979dc,'vPortSetupTimerInterrupt':0x95da4};BACKENDS={'nrf_drv_clock_lfclk_request':0x78990,'vPortStartFirstTask':0x27238}
def main():
 out=BASE/'rtos-port-start';receipt=out/'verification.json';receipt.unlink(missing_ok=True);rp=out/'report.json';r=json.loads(rp.read_text());obj=out/'port-start.o';assert sha(obj)==r['selected_object_sha256']
 for p,d in r['inputs'].items():assert sha(ROOT/p)==d,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';states={};comparisons=0;faults=0;bounded=0;counts={n:0 for n in ENTRIES}
 with tempfile.TemporaryDirectory() as directory:
  t=Path(directory);ld=t/'layout.ld';elf=t/'test.elf';binary=t/'text.bin';ld.write_text('SECTIONS { .text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } /DISCARD/ : { *(.comment) *(.note*) } }');bindings={n:0x100ef01+i*16 for i,n in enumerate(BACKENDS)};subprocess.run(['arm-none-eabi-ld','-T',str(ld),*['--defsym='+n+'='+hex(a) for n,a in bindings.items()],str(obj),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True);syms={x.split()[-1]:int(x.split()[0],16) for x in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x.split())==3}
  stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
  for u in (stock,candidate):u.mem_map(0x20000,0xc0000);u.mem_map(0x1000000,0x10000);u.mem_map(0x20000000,0x40000);u.mem_map(0xe000e000,0x1000);u.mem_map(0x40011000,0x1000)
  stock.mem_write(0x27000,app.read_bytes());candidate.mem_write(0x1000000,binary.read_bytes());kinds={a:n for n,a in BACKENDS.items()};kinds.update({a&~1:n for n,a in bindings.items()})
  def put(u,a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
  def word(u,a):return struct.unpack('<I',bytes(u.mem_read(a,4)))[0]
  def read(u,access,a,size,value,user):
   if a==0xe000e400:u.mem_write(a,bytes([u.mem_read(a,1)[0]&states[id(u)]['priority_mask']]))
  def write(u,access,a,size,value,user):
   if 0xe000e000<=a<0xe000f000 or 0x40011000<=a<0x40012000:states[id(u)]['writes'].append((a,size,value))
  def code(u,a,size,user):
   if a not in kinds:return
   f=states[id(u)];name=kinds[a];f['trace'].append((name,u.reg_read(UC_ARM_REG_R0)) if name=='nrf_drv_clock_lfclk_request' else (name,))
   if name=='vPortStartFirstTask' and not f['return_first']:f['bounded']=True;u.emu_stop();return
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  def invalid(u,access,a,size,value,user):states[id(u)]['fault']=(access,a,value);return False
  for u in (stock,candidate):u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_READ,read);u.hook_add(UC_HOOK_MEM_WRITE,write);u.hook_add(UC_HOOK_MEM_INVALID,invalid)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  def case(name,cpuid=0x410fc241,mask=0xe0,priority=0x40,pattern=0,nesting=0,primask=0,basepri=0,return_first=False):
   nonlocal comparisons,faults,bounded
   results=[]
   for u in (stock,candidate):
    f={'priority_mask':mask,'trace':[],'writes':[],'fault':None,'bounded':False,'return_first':return_first};states[id(u)]=f;u.mem_write(0xe000e000,bytes([0x93])*4096);u.mem_write(0x40011000,bytes([0xa5])*4096);u.mem_write(0x20007810,struct.pack('<3I',0xa5a5a5a5,nesting,0x12345678));put(u,0xe000ed00,cpuid);put(u,0xe000ed88,pattern);put(u,0xe000ef34,pattern);put(u,0xe000ed10,pattern);u.mem_write(0xe000e400,bytes([priority]));u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101);u.reg_write(UC_ARM_REG_IPSR,0);u.reg_write(UC_ARM_REG_PRIMASK,primask);u.reg_write(UC_ARM_REG_BASEPRI,basepri)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    try:u.emu_start((ENTRIES[name] if u is stock else syms[name])|1,0x20000100,count=100000)
    except UcError:assert f['fault'],(name,u is stock,hex(u.reg_read(UC_ARM_REG_PC)))
    if name=='vPortSetupTimerInterrupt':assert not f['fault'] and u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
    else:
     assert f['fault'] or f['bounded']
     if f['bounded']:
      assert u.mem_read(0x20007810,1)[0]==(2&mask) and word(u,0x20007814)==0 and word(u,0xe000ed88)==pattern|0xf00000 and word(u,0xe000ef34)==pattern|0xc0000000 and word(u,0xe000ed10)==pattern|16
    results.append((f['fault'],f['bounded'],f['trace'],f['writes'],bytes(u.mem_read(0x20007810,12)),bytes(u.mem_read(0xe000e000,4096)),bytes(u.mem_read(0x40011000,4096)),u.reg_read(UC_ARM_REG_PRIMASK),u.reg_read(UC_ARM_REG_BASEPRI)))
   assert results[0]==results[1],(name,cpuid,mask,priority,pattern,nesting,primask,basepri,return_first,[x[:4] for x in results]);comparisons+=1;faults+=bool(results[0][0]);bounded+=results[0][1];counts[name]+=1
  for cpuid,mask,priority,pattern,nesting,primask,basepri,return_first in itertools.product((0,0x410fc240,0x410fc241,0xffffffff),(0,0x80,0xe0,0xf0,0xfe,0xff),(0,0x40,0xff),(0,0x12345678,0xffffffff),(0,1,0xffffffff),(0,1),(0,64),(False,True)):case('xPortStartScheduler',cpuid,mask,priority,pattern,nesting,primask,basepri,return_first)
  for priority,pattern,primask,basepri in itertools.product((0,0x40,0xff),(0,0x12345678,0xffffffff),(0,1),(0,64)):case('vPortSetupTimerInterrupt',priority=priority,pattern=pattern,primask=primask,basepri=basepri)
 receipt.write_text(json.dumps(dict(application_sha256=sha(app),report_sha256=sha(rp),driver_sha256=sha(Path(__file__)),comparisons=comparisons,fault_comparisons=faults,bounded_first_task_cases=bounded,comparisons_by_function=counts,scope='Unchanged Nordic port/RTC setup: CPUID assertions, writable priority readback/raw2 mask, priority-group calculation, PendSV/RTC priority, LF-clock request, RTC31 prescaler/events/tasks/NVIC enable, critical reset, FPU and SEVONPEND setup; unexpected first-task return faults',limitations=['LF-clock request is a function fixture. First-task entry is bounded or returned as a fixture to test unexpected-return behavior. NVIC writable priority bits are a controlled hardware readback. No native context transfer, physical clock/RTC or whole-image identity proof.']),indent=2)+'\n');print(comparisons,'port-start comparisons;',faults,'faults;',bounded,'first-task boundaries;',counts)
if __name__=='__main__':main()
