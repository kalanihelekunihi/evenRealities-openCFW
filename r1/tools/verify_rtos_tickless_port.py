#!/usr/bin/env python3
"""Nordic RTC sleep versus native with explicit RTC/wake and lower fixtures."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
BACKENDS={'eTaskConfirmSleepModeStatus':0x5cf78,'nrf_sdh_is_enabled':0x7a4d8,'r1_adc_error':0x4e5bc,'vTaskStepTick':0x9653c}
def main():
 out=BASE/'rtos-tickless-port';receipt=out/'verification.json';receipt.unlink(missing_ok=True);rp=out/'report.json';r=json.loads(rp.read_text());obj=out/'tickless-port.o';assert sha(obj)==r['selected_object_sha256']
 for p,d in r['inputs'].items():assert sha(ROOT/p)==d,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';states={};comparisons=0;svcs=0;waits=0;fpus=0
 with tempfile.TemporaryDirectory() as directory:
  t=Path(directory);ld=t/'layout.ld';elf=t/'test.elf';binary=t/'text.bin';ld.write_text('SECTIONS { .text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } /DISCARD/ : { *(.comment) *(.note*) } }');bindings={n:0x100ef01+i*16 for i,n in enumerate(BACKENDS)};subprocess.run(['arm-none-eabi-ld','-T',str(ld),*['--defsym='+n+'='+hex(a) for n,a in bindings.items()],'--defsym=nrf_nvic_state=0x2002c2fc',str(obj),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True);syms={x.split()[-1]:int(x.split()[0],16) for x in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x.split())==3}
  stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
  for u in (stock,candidate):u.mem_map(0x20000,0xc0000);u.mem_map(0x1000000,0x10000);u.mem_map(0x20000000,0x40000);u.mem_map(0xe000e000,0x1000);u.mem_map(0x40011000,0x1000);u.reg_write(UC_ARM_REG_C1_C0_2,0xf00000);u.reg_write(UC_ARM_REG_FPEXC,0x40000000)
  stock.mem_write(0x27000,app.read_bytes());candidate.mem_write(0x1000000,binary.read_bytes());kinds={a:n for n,a in BACKENDS.items()};kinds.update({a&~1:n for n,a in bindings.items()})
  def put(u,a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
  def read(u,access,a,size,value,user):
   if a==0x40011504:
    f=states[id(u)];put(u,a,f['enter'] if f['reads']==0 else f['exit']);f['reads']+=1
  def write(u,access,a,size,value,user):
   if 0x40011000<=a<0x40012000 or 0xe000e100<=a<0xe000e300:states[id(u)]['writes'].append((a,size,value))
  def code(u,a,size,user):
   nonlocal svcs,waits
   f=states[id(u)]
   if a in kinds:
    name=kinds[a];value=f['status'] if name=='eTaskConfirmSleepModeStatus' else f['sd'] if name=='nrf_sdh_is_enabled' else 0
    f['trace'].append((name,u.reg_read(UC_ARM_REG_R0)) if name in ('r1_adc_error','vTaskStepTick') else (name,));u.reg_write(UC_ARM_REG_R0,value);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR));return
   op=bytes(u.mem_read(a,2))
   if op==b'\x41\xdf':f['trace'].append(('svc65',));svcs+=1;u.reg_write(UC_ARM_REG_R0,f['svc_status']);u.reg_write(UC_ARM_REG_PC,(a+2)|1)
   if op==b'\x20\xbf':f['trace'].append(('wfe',));waits+=1;u.reg_write(UC_ARM_REG_PC,(a+2)|1)
  for u in (stock,candidate):u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_READ,read);u.hook_add(UC_HOOK_MEM_WRITE,write)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  def case(expected,enter,delta,status,sd,svc_status,nested,primask,pending,fpscr):
   nonlocal comparisons,fpus
   results=[]
   for u in (stock,candidate):
    f={'enter':enter,'exit':(enter+delta)&0xffffff,'reads':0,'trace':[],'writes':[],'status':status,'sd':sd,'svc_status':svc_status};states[id(u)]=f;u.mem_write(0x40011000,bytes([0x93])*4096);u.mem_write(0xe000e000,bytes(4096));u.mem_write(0x2002c2fc,struct.pack('<3I',0xa5a5a5a5,0x12345678,nested));put(u,0xe000e180,0x87654321);put(u,0xe000e184,0xabcdef01);put(u,0xe000e200,1);put(u,0xe000e204,64 if pending else 0);u.reg_write(UC_ARM_REG_FPSCR,fpscr);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101);u.reg_write(UC_ARM_REG_R0,expected);u.reg_write(UC_ARM_REG_IPSR,0);u.reg_write(UC_ARM_REG_PRIMASK,primask);u.reg_write(UC_ARM_REG_BASEPRI,0)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    try:u.emu_start((0x95de4 if u is stock else syms['vPortSuppressTicksAndSleep'])|1,0x20000100,count=100000)
    except UcError as e:raise AssertionError((u is stock,hex(u.reg_read(UC_ARM_REG_PC)),expected,status,sd,nested,primask,pending,hex(fpscr))) from e
    assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
    results.append((f['reads'],f['trace'],f['writes'],bytes(u.mem_read(0x2002c2fc,12)),bytes(u.mem_read(0x40011000,4096)),bytes(u.mem_read(0xe000e100,0x200)),u.reg_read(UC_ARM_REG_FPSCR),u.reg_read(UC_ARM_REG_PRIMASK),u.reg_read(UC_ARM_REG_BASEPRI)))
   assert results[0]==results[1],(expected,enter,delta,status,sd,svc_status,nested,primask,pending,hex(fpscr),[(x[:3],x[-3:]) for x in results]);comparisons+=1;fpus+=int(pending and status!=0 and expected!=0)
  for expected,enter,delta,status,sd,nested,primask in itertools.product((0,1,2,100,0xfffffd,0xfffffe,0xffffffff),(0,0xfffffe),(0,1,100,0xffffff),(0,1,2),(0,1),(0,1),(0,1)):case(expected,enter,delta,status,sd,0,nested,primask,0,0)
  for expected,status,sd,svc_status,nested,primask,pending,fpscr in itertools.product((0,1,100),(0,1,2),(0,1),(0,7),(0,1,0xffffffff),(0,1),(0,1),(0,0x9f,0xf000009f)):case(expected,0xfffffe,100,status,sd,svc_status,nested,primask,pending,fpscr)
 receipt.write_text(json.dumps(dict(application_sha256=sha(app),report_sha256=sha(rp),driver_sha256=sha(Path(__file__)),comparisons=comparisons,svc65_fixture_calls_per_implementation=svcs//2,wfe_fixture_calls_per_implementation=waits//2,pending_fpu_sleep_cases=fpus,scope='Pinned RTC sleep, native configuration/FPU/error binding, SoftDevice NVIC critical state, RTC24-bit compare/delta/debug clamp, abort/zero/sleep, SVC error continuation, WFE branch and pending FPU FPSCR clear; ordered MMIO writes and registers',limitations=['Sleep-status, tick-step, SD-enabled and error handlers are explicit lower fixtures. RTC two counter reads are controlled. SVC65 and WFE are explicit instruction fixtures, not physical wait/SoftDevice execution. Memory-backed MMIO write equality does not prove peripheral semantics or hardware wake.']),indent=2)+'\n');print(comparisons,'RTC sleep comparisons;',svcs//2,'SVC65 fixtures;',waits//2,'WFE fixtures;',fpus,'pending FPU cases')
if __name__=='__main__':main()
