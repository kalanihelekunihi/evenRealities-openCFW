#!/usr/bin/env python3
"""Pinned kernel sleep status and tick stepping versus native firmware."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_INVALID
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
FIELDS={'xPendingReadyList':0x2002b21c,'xSuspendedTaskList':0x2002b244,'uxCurrentNumberOfTasks':0x20007824,'xYieldPending':0x20007838,'xPendedTicks':0x20007834,'xNextTaskUnblockTime':0x20007844};BACKENDS={'vPortEnterCritical':0x95cf4,'vPortExitCritical':0x95d24};ENTRIES={'eTaskConfirmSleepModeStatus':0x5cf78,'vTaskStepTick':0x9653c}
def main():
 out=BASE/'rtos-sleep-kernel';receipt=out/'verification.json';receipt.unlink(missing_ok=True);rp=out/'report.json';r=json.loads(rp.read_text());obj=out/'sleep-kernel.o';assert sha(obj)==r['selected_object_sha256']
 for p,d in r['inputs'].items():assert sha(ROOT/p)==d,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';states={};comparisons=0;assertions=0;counts={n:0 for n in ENTRIES};critical_calls=0
 with tempfile.TemporaryDirectory() as directory:
  t=Path(directory);ld=t/'layout.ld';elf=t/'test.elf';binary=t/'text.bin';ld.write_text('SECTIONS { .text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } /DISCARD/ : { *(.comment) *(.note*) } }');bindings={n:0x100ef01+i*16 for i,n in enumerate(BACKENDS)};subprocess.run(['arm-none-eabi-ld','-T',str(ld),*['--defsym='+n+'='+hex(a) for n,a in {**FIELDS,**bindings}.items()],str(obj),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True);syms={x.split()[-1]:int(x.split()[0],16) for x in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x.split())==3}
  stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
  for u in (stock,candidate):u.mem_map(0x20000,0xc0000);u.mem_map(0x1000000,0x10000);u.mem_map(0x20000000,0x40000)
  stock.mem_write(0x27000,app.read_bytes());candidate.mem_write(0x1000000,binary.read_bytes());kinds={a:n for n,a in BACKENDS.items()};kinds.update({a&~1:n for n,a in bindings.items()})
  def hook(u,a,size,user):
   nonlocal critical_calls
   if a in kinds:states[id(u)]['trace'].append(kinds[a]);critical_calls+=1;u.reg_write(UC_ARM_REG_R0,0xdeadbeef);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  def invalid(u,access,address,size,value,user):
   if address==0xffffffff and value==0:states[id(u)]['fault']=True
   return False
  for u in (stock,candidate):u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_INVALID,invalid)
  def put(u,a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  def case(name,values,arg=0):
   nonlocal comparisons,assertions
   results=[]
   for u in (stock,candidate):
    f={'trace':[],'fault':False};states[id(u)]=f;u.mem_write(0x2000781c,bytes([0xa5])*64);u.mem_write(0x2002b21c,bytes([0x93])*60)
    for a,v in values.items():put(u,a,v)
    u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101);u.reg_write(UC_ARM_REG_R0,arg);u.reg_write(UC_ARM_REG_BASEPRI,0);u.reg_write(UC_ARM_REG_PRIMASK,0)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    try:u.emu_start((ENTRIES[name] if u is stock else syms[name])|1,0x20000100,count=100000)
    except UcError:assert f['fault'],(name,u is stock,hex(u.reg_read(UC_ARM_REG_PC)))
    if not f['fault']:assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
    results.append((f['fault'],u.reg_read(UC_ARM_REG_R0) if name=='eTaskConfirmSleepModeStatus' else None,f['trace'],bytes(u.mem_read(0x2000781c,64)),bytes(u.mem_read(0x2002b21c,60)),u.reg_read(UC_ARM_REG_PRIMASK),u.reg_read(UC_ARM_REG_BASEPRI)))
   assert results[0]==results[1],(name,values,arg,results);comparisons+=1;assertions+=results[0][0];counts[name]+=1
  for pending,yielding,pended,number,suspended in itertools.product((0,1,2,0xffffffff),repeat=5):case('eTaskConfirmSleepModeStatus',{0x2002b21c:pending,0x20007838:yielding,0x20007834:pended,0x20007824:number,0x2002b244:suspended})
  for tick,jump,next_time,suspended,pended in itertools.product((0,1,2,100,0xfffffffe,0xffffffff),(0,1,2,99,100,0xfffffffe,0xffffffff),(0,1,2,100,0xfffffffe,0xffffffff),(0,1,0xffffffff),(0,1,0xfffffffe,0xffffffff)):case('vTaskStepTick',{0x20007828:tick,0x20007844:next_time,0x20007850:suspended,0x20007834:pended},jump)
 receipt.write_text(json.dumps(dict(application_sha256=sha(app),report_sha256=sha(rp),driver_sha256=sha(Path(__file__)),comparisons=comparisons,assertion_comparisons=assertions,comparisons_by_function=counts,critical_fixture_calls_per_implementation=critical_calls//2,scope='Unchanged sleep-status pending/yield/pended/all-suspended checks and tick-step unsigned wrap, equality-deferred tick, assertions and state canaries',limitations=['Critical entry/exit are explicit fixtures in this unit. Actual sleep, tick progression, native context switching and whole-image identity remain separate.']),indent=2)+'\n');print(comparisons,'sleep kernel comparisons;',assertions,'assertions;',counts,'critical calls:',critical_calls//2)
if __name__=='__main__':main()
