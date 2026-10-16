#!/usr/bin/env python3
"""Actual pinned tick/event bodies versus R1: no provider interception."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_MEM_INVALID
from unicorn.arm_const import *
from verify_rtos_scheduler_resume import FIELDS as SHARED
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
FIELDS={**SHARED,'xTickCount':(0x20007828,4),'xNumOfOverflows':(0x2000783c,4),'pxOverflowDelayedTaskList':(0x20007858,4),'xDelayedTaskList1':(0x2002b1f4,20),'xDelayedTaskList2':(0x2002b208,20)}
OWNED={'xNumOfOverflows','pxOverflowDelayedTaskList','xDelayedTaskList1','xDelayedTaskList2'};ENTRIES={'xTaskIncrementTick':0x987e0,'xTaskRemoveFromEventList':0x98a4c}
def main():
 out=BASE/'rtos-scheduler-tick';(out/'verification.json').unlink(missing_ok=True);rp=out/'report.json';r=json.loads(rp.read_text());obj=out/'scheduler-tick.o';assert sha(obj)==r['selected_object_sha256']
 for p,d in r['inputs'].items():assert sha(ROOT/p)==d,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';states={};comparisons=0;faults=0;counts={'xTaskIncrementTick':0,'xTaskRemoveFromEventList':0}
 with tempfile.TemporaryDirectory() as directory:
  t=Path(directory);ld=t/'layout.ld';elf=t/'test.elf';binary=t/'text.bin';ld.write_text('SECTIONS { .text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } '+''.join('.bss.'+n+' '+hex(a)+' (NOLOAD) : { *(.bss.'+n+') } ' for n,(a,z) in FIELDS.items() if n in OWNED)+'/DISCARD/ : { *(.comment) *(.note*) } }');subprocess.run(['arm-none-eabi-ld','-T',str(ld),*['--defsym='+n+'='+hex(a) for n,(a,z) in FIELDS.items() if n not in OWNED],str(obj),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True);syms={x.split()[-1]:int(x.split()[0],16) for x in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x.split())==3}
  for n,(a,z) in FIELDS.items():assert syms[n]==a
  stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
  for u in (stock,candidate):u.mem_map(0x20000,0xc0000);u.mem_map(0x1000000,0x10000);u.mem_map(0x20000000,0x40000)
  stock.mem_write(0x27000,app.read_bytes());candidate.mem_write(0x1000000,binary.read_bytes())
  def fault(u,access,address,size,value,user):
   if address==0xffffffff and value==0:states[id(u)]=True
   return False
  for u in (stock,candidate):u.hook_add(UC_HOOK_MEM_INVALID,fault)
  def put(u,a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
  def word(u,a):return struct.unpack('<I',bytes(u.mem_read(a,4)))[0]
  def init_list(u,a):u.mem_write(a,struct.pack('<5I',0,a+8,0xffffffff,a+8,a+8))
  def append(u,a,item,owner,value):
   sentinel=a+8;previous=word(u,sentinel+8);u.mem_write(item,struct.pack('<5I',value&0xffffffff,sentinel,previous,owner,a));put(u,previous+4,item);put(u,sentinel+8,item);put(u,a,word(u,a)+1)
  def reset(tick,suspended,current,yielding,pended,overflows,orientation,extra):
   delayed=0x2002b208 if orientation else 0x2002b1f4;overflow=0x2002b1f4 if orientation else 0x2002b208
   for u in (stock,candidate):
    u.mem_write(0x20001000,bytes([0xa5])*8192);u.mem_write(0x2000781c,bytes(64));u.mem_write(0x2002ad94,bytes(1180))
    for n,v in [('pxCurrentTCB',0x20001000),('uxCurrentNumberOfTasks',1),('uxTopReadyPriority',current),('uxSchedulerSuspended',suspended),('xTickCount',tick),('xYieldPending',yielding),('xPendedTicks',pended),('xNumOfOverflows',overflows),('pxDelayedTaskList',delayed),('pxOverflowDelayedTaskList',overflow),('xNextTaskUnblockTime',0xffffffff)]:put(u,FIELDS[n][0],v)
    for i in range(56):init_list(u,0x2002ad94+i*20)
    for a in (0x2002b1f4,0x2002b208,0x2002b21c,0x20001800):init_list(u,a)
    put(u,0x2000102c,current);put(u,0x20001028,0);append(u,0x2002ad94+current*20,0x20001004,0x20001000,0)
    if extra:put(u,0x2000282c,current);put(u,0x20002828,0);append(u,0x2002ad94+current*20,0x20002804,0x20002800,0)
   return delayed,overflow
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  def call(name,arg=0):
   nonlocal comparisons,faults
   results=[]
   for u in (stock,candidate):
    states[id(u)]=False;u.reg_write(UC_ARM_REG_R0,arg);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101);u.reg_write(UC_ARM_REG_BASEPRI,0)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    try:u.emu_start((ENTRIES[name] if u is stock else syms[name])|1,0x20000100,count=1000000)
    except UcError:assert states[id(u)],(name,u is stock,hex(u.reg_read(UC_ARM_REG_PC)))
    if not states[id(u)]:assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
    results.append((states[id(u)],None if states[id(u)] else u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(0x20001000,8192)),bytes(u.mem_read(0x2000781c,64)),bytes(u.mem_read(0x2002ad94,1180)),u.reg_read(UC_ARM_REG_BASEPRI)))
   assert results[0]==results[1],(name,[x[:2] for x in results],[(k,[(i,a,b) for i,(a,b) in enumerate(zip(results[0][k],results[1][k])) if a!=b][:12]) for k in range(2,5)]);comparisons+=1;faults+=results[0][0];counts[name]+=1;return results[0][0]
  for tick,shape,current,event,index_mode,suspended,yielding,pended,overflows,extra in itertools.product((0,1,99,0xfffffffe,0xffffffff),range(5),(0,1,15,55),(0,1),range(4),(0,1,0xffffffff),(0,1),(0,0xffffffff),(0,0x7fffffff),(0,1)):
   delayed,overflow=reset(tick,suspended,current,yielding,pended,overflows,index_mode>>1,extra)
   wakes=[[],[(tick+1)&0xffffffff],[(tick+2)&0xffffffff],sorted([(tick+1)&0xffffffff,(tick+2)&0xffffffff,(tick+2)&0xffffffff]),[0,1,0xffffffff]][shape]
   for u in (stock,candidate):
    for i,wake in enumerate(wakes):
     task=0x20002000+i*128;put(u,task+44,(0,15,55)[i]);put(u,task+40,0);append(u,delayed,task+4,task,wake)
     if event:append(u,0x20001800,task+24,task,i)
    # Overflow-delayed tasks become due only after list swap.
    for i,wake in enumerate((0,1)):
     task=0x20002400+i*128;put(u,task+44,(55,0)[i]);put(u,task+40,0);append(u,overflow,task+4,task,wake)
    put(u,FIELDS['xNextTaskUnblockTime'][0],wakes[0] if wakes else 0xffffffff)
    if index_mode&1 and wakes:put(u,delayed+4,0x20002004)
   call('xTaskIncrementTick')
  for priorities,current,suspended,yielding,index_mode,remaining in itertools.product(((0,),(1,),(15,),(55,),(0,55),(55,0),(15,1,55)),(0,1,15,55),(0,1,2,0xffffffff),(0,1),range(4),(0,1)):
   delayed,overflow=reset(99,suspended,current,yielding,0,0,index_mode>>1,0)
   for u in (stock,candidate):
    for i,priority in enumerate(priorities):
     task=0x20002000+i*128;put(u,task+44,priority);append(u,delayed,task+4,task,100+i);append(u,0x20001800,task+24,task,i)
    if remaining:append(u,delayed,0x20002c04,0x20002c00,123456)
    if index_mode&1:put(u,delayed+4,0x20002004);put(u,0x20001804,0x20002018)
   call('xTaskRemoveFromEventList',0x20001800)
  reset(0,0,0,0,0,0,0,0)
  for u in (stock,candidate):append(u,0x20001800,0x20002018,0,0)
  assert call('xTaskRemoveFromEventList',0x20001800)
 (out/'verification.json').write_text(json.dumps(dict(application_sha256=sha(app),report_sha256=sha(rp),driver_sha256=sha(Path(__file__)),comparisons=comparisons,assertion_comparisons=faults,comparisons_by_function=counts,provider_interception=False,scope='Actual unchanged pinned tick/event-list bodies and inline list operations; timeouts, event cancellation, tick/list overflow, suspended tick wrap, priorities/time slicing/yield, deferred pending-ready moves and NULL-owner assertion; full TCB canaries/state/list memory',limitations=['Controlled scheduler/list states cover bounded inputs; complete scheduler startup/context switching, full TCB allocation, physical interrupt concurrency and whole-image identity remain gates.']),indent=2)+'\n');print(comparisons,'tick/event comparisons;',faults,'assertions;',counts)
if __name__=='__main__':main()
