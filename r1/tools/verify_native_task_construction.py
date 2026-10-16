#!/usr/bin/env python3
"""Native112-byte task construction versus C, actual port/list/memory bodies."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_INVALID
from unicorn.arm_const import *
from verify_rtos_task_wait import FIELDS as SHARED
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
FIELDS={**SHARED,'uxTaskNumber':(0x20007840,4),'xTasksWaitingTermination':(0x2002b230,20),'xSchedulerRunning':(0x20007830,4),'uxCriticalNesting':(0x20007814,4)}
OWNED={'uxTaskNumber','xTasksWaitingTermination'}
ENTRIES={'r1_native_task_initialize':0x850b6,'r1_native_task_create':0x983b8,'r1_native_task_create_static':0x98418,'prvAddNewTaskToReadyList':0x84d68,'pxPortInitialiseStack':0x856c0,'prvTaskExitError':0x854e0,'vListInitialiseItem':0x95ca6}
BACKENDS={'pvPortMalloc':0x855a0,'vPortFree':0x95d48,'vPortEnterCritical':0x95cf4,'vPortExitCritical':0x95d24}
def main():
 out=BASE/'native-task-construction';receipt=out/'verification.json';receipt.unlink(missing_ok=True);rp=out/'report.json';r=json.loads(rp.read_text());obj=out/'task-construction.o';assert sha(obj)==r['selected_object_sha256']
 for p,d in r['inputs'].items():assert sha(ROOT/p)==d,p
 memory=BASE/'runtime/memory-runtime.o';assert sha(memory)==json.loads((BASE/'runtime/report.json').read_text())['relocatable_sha256'];rawlist=BASE/'rtos-queue-create/list.o';qr=json.loads((BASE/'rtos-queue-create/report.json').read_text());assert sha(rawlist)==next(x['object_sha256'] for x in qr['units'] if x['source'].endswith('/list.c'));heap=BASE/'native-heap/heap.o';assert sha(heap)==json.loads((BASE/'native-heap/report.json').read_text())['selected_object_sha256']
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';states={};comparisons=0;faults=0;counts={n:0 for n in ENTRIES}
 with tempfile.TemporaryDirectory() as directory:
  t=Path(directory);extra=[]
  for name,source,root in [('list',rawlist,'vListInitialise'),('fault',heap,'r1_malloc_failed_hook')]:
   selected=t/(name+'.o');subprocess.run(['arm-none-eabi-ld','-r','--gc-sections','--undefined='+root,str(source),'-o',str(selected)],check=True);extra.append(str(selected))
  ld=t/'layout.ld';elf=t/'test.elf';binary=t/'text.bin';ld.write_text('SECTIONS { .r1.task.initial_xpsr 0x9c4cc : { *(.r1.task.initial_xpsr) } .text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } '+''.join('.bss.'+n+' '+hex(a)+' (NOLOAD) : { *(.bss.'+n+') } ' for n,(a,z) in FIELDS.items() if n in OWNED)+'/DISCARD/ : { *(.comment) *(.note*) } }');bindings={n:0x100ef01+i*16 for i,n in enumerate(BACKENDS)};subprocess.run(['arm-none-eabi-ld','-T',str(ld),*['--defsym='+n+'='+hex(a) for n,(a,z) in FIELDS.items() if n not in OWNED],*['--defsym='+n+'='+hex(a) for n,a in bindings.items()],str(obj),str(memory),*extra,'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True);syms={x.split()[-1]:int(x.split()[0],16) for x in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x.split())==3};assert syms['r1_native_initial_xpsr']==0x9c4cc
  for n,(a,z) in FIELDS.items():assert syms[n]==a
  stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
  for u in (stock,candidate):u.mem_map(0x20000,0xc0000);u.mem_map(0x1000000,0x10000);u.mem_map(0x20000000,0x40000);u.mem_map(0xe000e000,0x1000)
  stock.mem_write(0x27000,app.read_bytes());candidate.mem_write(0x1000000,binary.read_bytes());constant=t/'xpsr.bin';subprocess.run(['arm-none-eabi-objcopy','--dump-section','.r1.task.initial_xpsr='+str(constant),str(elf)],check=True);assert constant.read_bytes()==bytes(stock.mem_read(0x9c4cc,4))==struct.pack('<I',0x1000000);candidate.mem_write(0x9c4cc,constant.read_bytes());kinds={a:n for n,a in BACKENDS.items()};kinds.update({a&~1:n for n,a in bindings.items()})
  def put(u,a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
  def word(u,a):return struct.unpack('<I',bytes(u.mem_read(a,4)))[0]
  def init_list(u,a):u.mem_write(a,struct.pack('<5I',0,a+8,0xffffffff,a+8,a+8))
  def hook(u,a,size,user):
   if a not in kinds:return
   f=states[id(u)];name=kinds[a];arg=u.reg_read(UC_ARM_REG_R0);trace=(name,);value=0xdeadbeef
   if name=='pvPortMalloc':index=f['allocations'];f['allocations']+=1;trace=(name,arg);value=0 if f['fail']==index+1 else 0x20004000 if not index else 0x20002000
   elif name=='vPortFree':trace=(name,arg)
   f['trace'].append(trace);u.reg_write(UC_ARM_REG_R0,value);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  def fault(u,access,address,size,value,user):
   if address==0xffffffff and value==0:states[id(u)]['fault']=True
   return False
  for u in (stock,candidate):u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_INVALID,fault)
  def reset(current=0,number=0,running=0,oldpriority=0,counter=0,dirty=False,offset=0):
   for u in (stock,candidate):
    u.mem_write(0x20001000,bytes([0xa5])*0x5000);u.mem_write(0x20007810,bytes(76));u.mem_write(0x2002ad94,bytes([0x93 if dirty else 0])*1220);u.mem_write(0xe000ed04,bytes(4));u.mem_write(0x20003000,b'0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJK\0');put(u,0x20002030,0x20004000+offset);put(u,0x2000102c,oldpriority)
    for n,v in [('pxCurrentTCB',0x20001000 if current else 0),('uxCurrentNumberOfTasks',number),('uxTopReadyPriority',oldpriority),('xSchedulerRunning',running),('uxTaskNumber',counter),('uxTopUsedPriority',55),('pxDelayedTaskList',0x2002b1f4),('pxOverflowDelayedTaskList',0x2002b208),('xNextTaskUnblockTime',0xffffffff)]:put(u,FIELDS[n][0],v)
    if not dirty:
     for i in range(56):init_list(u,0x2002ad94+i*20)
     for a in (0x2002b1f4,0x2002b208,0x2002b21c,0x2002b230,0x2002b244):init_list(u,a)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  def call(name,args=(),fail=0,loop=False):
   nonlocal comparisons,faults
   results=[]
   for u in (stock,candidate):
    f={'trace':[],'fault':False,'fail':fail,'allocations':0};states[id(u)]=f;u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101);u.reg_write(UC_ARM_REG_BASEPRI,0)
    for reg,value in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),args):u.reg_write(reg,value)
    for i,value in enumerate(args[4:]):put(u,0x2003f000+i*4,value)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    try:u.emu_start((ENTRIES[name] if u is stock else syms[name])|1,0x20000100,count=2000 if loop else 2000000)
    except UcError:assert f['fault'],(name,args,u is stock,hex(u.reg_read(UC_ARM_REG_PC)))
    if loop and not f['fault']:assert u.reg_read(UC_ARM_REG_PC)!=0x20000100 and u.reg_read(UC_ARM_REG_BASEPRI)==64
    if not f['fault'] and not loop:assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
    memory=bytearray(u.mem_read(0x20001000,0x5000));pointer=syms['prvTaskExitError']|1
    if u is candidate:
     # Only native stack LR words are normalized; scan the controlled stack range.
     for off in range(0x2f00,0x4200,4):
      value=struct.unpack_from('<I',memory,off)[0]
      if value==pointer:
       assert struct.unpack('<I',bytes(stock.mem_read(0x20001000+off,4)))[0]==0x854e1
       struct.pack_into('<I',memory,off,0x854e1)
    results.append((f['fault'],u.reg_read(UC_ARM_REG_R0) if name in ('r1_native_task_create','r1_native_task_create_static','pxPortInitialiseStack') and not f['fault'] else None,f['trace'],bytes(memory),bytes(u.mem_read(0x20007810,76)),bytes(u.mem_read(0x2002ad94,1220)),bytes(u.mem_read(0xe000ed04,4)),u.reg_read(UC_ARM_REG_BASEPRI)))
   assert results[0]==results[1],(name,args,fail,[x[:3] for x in results],[(k,[(i,a,b) for i,(a,b) in enumerate(zip(results[0][k],results[1][k])) if a!=b][:12]) for k in range(3,7)]);comparisons+=1;faults+=results[0][0];counts[name]+=1
  for top,code,param in itertools.product((0x20004400,0x20004404),(0,0x12345678,0x12345679),(0,0xffffffff)):
   reset();call('pxPortInitialiseStack',(top,code,param))
  for depth,priority,name,outptr,offset in itertools.product((0,1,16,17,64,256),(0,15,55,56,0xffffffff),(0,0x20003000,0x2000302e),(0,0x20002100),(0,4)):
   reset(offset=offset);call('r1_native_task_initialize',(0x12345679,name,depth,0x87654321,priority,outptr,0x20002000,0))
  for current,number,running,oldpriority,priority,counter in itertools.product((0,1),(0,1,0xffffffff),(0,1),(0,55),(0,15,55),(0,0xffffffff)):
   if current and not number:continue
   reset(current,number,running,oldpriority,counter,dirty=not current and number==0)
   for u in (stock,candidate):put(u,0x2000202c,priority)
   call('prvAddNewTaskToReadyList',(0x20002000,))
  for depth,priority,name,current,running,fail in itertools.product((16,17,64),(0,55),(0,0x20003000),(0,1),(0,1),(0,1,2)):
   reset(current,current,running,15);call('r1_native_task_create',(0x12345679,name,depth,0x87654321,priority,0x20002100),fail)
   reset(current,current,running,15);call('r1_native_task_create_static',(0x12345679,name,depth,0x87654321,priority,0x20004000,0x20002000))
  for stack,tcb,priority in ((0,0x20002000,0),(0x20004000,0,0),(0x20004000,0x20002000,56)):
   reset();call('r1_native_task_create_static',(0x12345679,0,16,0,priority,stack,tcb))
  for nesting in (0,1,0xfffffffe,0xffffffff):
   reset()
   for u in (stock,candidate):put(u,0x20007814,nesting)
   call('prvTaskExitError',loop=True)
  reset();call('vListInitialiseItem',(0x20002004,))
 receipt.write_text(json.dumps(dict(application_sha256=sha(app),report_sha256=sha(rp),driver_sha256=sha(Path(__file__)),comparisons=comparisons,assertion_comparisons=faults,comparisons_by_function=counts,tcb_bytes_compared=112,initial_xpsr_bytes_compared=4,provider_reports={'runtime/report.json':sha(BASE/'runtime/report.json'),'rtos-queue-create/report.json':sha(BASE/'rtos-queue-create/report.json'),'native-heap/report.json':sha(BASE/'native-heap/report.json')},scope='Actual native112-byte static/dynamic construction/initializer, unchanged ready-list registration/list setup/port stack/return-error and list-item initialization; full data/stack/state, failure cleanup, masks and guards',limitations=['Allocator/free and critical boundaries are bounded fixtures. Native/source stack task-return pointers are normalized. Full CMSIS thread wrapper, real allocation/critical composition, scheduler startup/context switching and whole-image identity remain gates.']),indent=2)+'\n');print(comparisons,'task construction comparisons;',faults,'assertions;',counts)
if __name__=='__main__':main()
