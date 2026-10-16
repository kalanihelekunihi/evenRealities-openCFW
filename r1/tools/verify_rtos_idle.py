#!/usr/bin/env python3
"""Compare complete native/C idle-loop control flow at explicit iteration bounds."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_INVALID
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
BACKENDS={'r1_native_task_idle_cleanup':0x84fea,'r1_native_expected_idle_time':0x84f68,'r1_native_watchdog_hw_feed_thunk':0x95be8,'vTaskSuspendAll':0x9659c,'xTaskResumeAll':0x98b24,'vPortSuppressTicksAndSleep':0x95de4}
def main():
 out=BASE/'rtos-idle';receipt=out/'verification.json';receipt.unlink(missing_ok=True);rp=out/'report.json';r=json.loads(rp.read_text());obj=out/'idle.o';assert sha(obj)==r['selected_object_sha256']
 for p,d in r['inputs'].items():assert sha(ROOT/p)==d,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';states={};comparisons=0;assertions=0;fixture_calls=0
 with tempfile.TemporaryDirectory() as directory:
  t=Path(directory);ld=t/'layout.ld';elf=t/'test.elf';binary=t/'text.bin';ld.write_text('SECTIONS { .text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } /DISCARD/ : { *(.comment) *(.note*) } }');bindings={n:0x100ef01+i*16 for i,n in enumerate(BACKENDS)};subprocess.run(['arm-none-eabi-ld','-T',str(ld),*['--defsym='+n+'='+hex(a) for n,a in bindings.items()],'--defsym=pxReadyTasksLists=0x2002ad94','--defsym=xNextTaskUnblockTime=0x20007844',str(obj),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True);syms={x.split()[-1]:int(x.split()[0],16) for x in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x.split())==3}
  stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
  for u in (stock,candidate):u.mem_map(0x20000,0xc0000);u.mem_map(0x1000000,0x10000);u.mem_map(0x20000000,0x40000);u.mem_map(0xe000e000,0x1000)
  stock.mem_write(0x27000,app.read_bytes());candidate.mem_write(0x1000000,binary.read_bytes());kinds={a:n for n,a in BACKENDS.items()};kinds.update({a&~1:n for n,a in bindings.items()})
  def put(u,a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
  def hook(u,a,size,user):
   nonlocal fixture_calls
   if a not in kinds:return
   f=states[id(u)];name=kinds[a]
   if name=='r1_native_task_idle_cleanup':
    if f['iterations']==f['limit']:f['stopped']=True;u.emu_stop();return
    f['iterations']+=1;f['expected_calls']=0
   f['trace'].append((name,u.reg_read(UC_ARM_REG_R0)) if name=='vPortSuppressTicksAndSleep' else (name,));fixture_calls+=1;value=0xdeadbeef
   if name=='r1_native_expected_idle_time':value=f['expected'][min(f['expected_calls'],1)];f['expected_calls']+=1
   if name=='vTaskSuspendAll':put(u,0x20007844,f['after_next'])
   if name=='r1_native_task_idle_cleanup' and u is stock:return # native inline empty cleanup remains executed
   u.reg_write(UC_ARM_REG_R0,value);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  def fault(u,access,address,size,value,user):
   if address==0xffffffff and value==0:states[id(u)]['fault']=True
   return False
  for u in (stock,candidate):u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_INVALID,fault)
  for first,second,ready,tick,next_time,after_next,limit,primask in itertools.product((0,1,2,3,0xffffffff),(0,1,2,3,0xffffffff),(0,1,2,0xffffffff),(0,1,0xffffffff),(0,1,0xffffffff),(0,1,0xffffffff),(1,3),(0,1)):
   results=[]
   for u in (stock,candidate):
    f={'trace':[],'expected':(first,second),'expected_calls':0,'iterations':0,'limit':limit,'after_next':after_next,'fault':False,'stopped':False};states[id(u)]=f;u.mem_write(0x2000781c,bytes(64));put(u,0x20007828,tick);put(u,0x20007844,next_time);put(u,0x2002ad94,ready);put(u,0xe000ed04,0);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101);u.reg_write(UC_ARM_REG_R0,0x12345678);u.reg_write(UC_ARM_REG_IPSR,0);u.reg_write(UC_ARM_REG_PRIMASK,primask);u.reg_write(UC_ARM_REG_BASEPRI,0)
    try:u.emu_start((0x84fe8 if u is stock else syms['r1_native_idle_task'])|1,0x20000100,count=100000)
    except UcError:assert f['fault'],(u is stock,hex(u.reg_read(UC_ARM_REG_PC)))
    assert f['fault'] or f['stopped'];results.append((f['fault'],f['iterations'],f['trace'],bytes(u.mem_read(0x2000781c,64)),bytes(u.mem_read(0xe000ed04,4)),u.reg_read(UC_ARM_REG_PRIMASK),u.reg_read(UC_ARM_REG_BASEPRI)))
   assert results[0]==results[1],(first,second,ready,tick,next_time,after_next,limit,primask,results);comparisons+=1;assertions+=results[0][0]
 receipt.write_text(json.dumps(dict(application_sha256=sha(app),report_sha256=sha(rp),driver_sha256=sha(Path(__file__)),comparisons=comparisons,assertion_comparisons=assertions,fixture_calls_per_implementation=fixture_calls//2,native_loop_entry='0x84fe8',scope='Complete native/C idle-loop control flow: empty cleanup boundary, watchdog hook, yield PendSV write, preliminary/resampled idle time, scheduler suspension, tick-order assertion, sleep threshold and resume across1/3 iterations',limitations=['Cleanup, expected idle, hook, suspend/resume and tick-suppression providers use explicit fixtures here. Native empty cleanup executes inline. Infinite task is bounded at loop entry; no return ABI, native context transfer or physical sleep proof. Actual provider composition is separate.']),indent=2)+'\n');print(comparisons,'idle loop comparisons;',assertions,'matching assertions;',fixture_calls//2,'fixture calls')
if __name__=='__main__':main()
