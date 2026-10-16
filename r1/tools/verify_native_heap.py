#!/usr/bin/env python3
"""Native heap4 extension differential, with scheduler suspend/resume fixtures."""
import hashlib,itertools,json,random,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_INVALID
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ENTRIES={'pvPortMalloc':0x855a0,'vPortFree':0x95d48,'r1_heap_initialize':0x84f98}
BACKENDS={'vTaskSuspendAll':0x9659c,'xTaskResumeAll':0x98b24}
def main():
 out=BASE/'native-heap';(out/'verification.json').unlink(missing_ok=True);rp=out/'report.json';report=json.loads(rp.read_text());obj=out/'heap.o';assert sha(obj)==report['selected_object_sha256']
 for p,d in report['inputs'].items():assert sha(ROOT/p)==d,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';states={};comparisons=0;faults=0;backend_calls=0
 with tempfile.TemporaryDirectory() as directory:
  t=Path(directory);ld=t/'layout.ld';elf=t/'test.elf';binary=t/'text.bin';ld.write_text('SECTIONS { .text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } .r1.heap.state 0x200077fc (NOLOAD) : { *(.r1.heap.state) } .r1.heap.storage 0x2001e588 (NOLOAD) : { *(.r1.heap.storage) } .r1.heap.start 0x2002ad88 (NOLOAD) : { *(.r1.heap.start) } /DISCARD/ : { *(.comment) *(.note*) } }');bindings={n:0x100ef01+i*16 for i,n in enumerate(BACKENDS)};subprocess.run(['arm-none-eabi-ld','-T',str(ld),*['--defsym='+n+'='+hex(a) for n,a in bindings.items()],str(obj),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True);syms={x.split()[-1]:int(x.split()[0],16) for x in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x.split())==3};assert (syms['r1_heap_storage'],syms['r1_heap_start'],syms['r1_heap_state'])==(0x2001e588,0x2002ad88,0x200077fc)
  stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
  for u in (stock,candidate):u.mem_map(0x20000,0xc0000);u.mem_map(0x1000000,0x10000);u.mem_map(0x20000000,0x40000)
  stock.mem_write(0x27000,app.read_bytes());candidate.mem_write(0x1000000,binary.read_bytes());kinds={a:n for n,a in BACKENDS.items()};kinds.update({a&~1:n for n,a in bindings.items()})
  def hook(u,a,size,user):
   nonlocal backend_calls
   if a not in kinds:return
   states[id(u)]['trace'].append(kinds[a]);backend_calls+=1;u.reg_write(UC_ARM_REG_R0,0xdeadbeef);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  def fault(u,access,address,size,value,user):
   if address==0xffffffff and value==0:states[id(u)]['fault']=True
   return False
  for u in (stock,candidate):u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_INVALID,fault)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  def reset(pattern=0):
   for u in (stock,candidate):u.mem_write(0x2001e580,bytes([pattern])*51232);u.mem_write(0x200077fc,bytes(20))
  def call(name,arg=0,lr=0x20000101):
   nonlocal comparisons,faults
   results=[]
   for u in (stock,candidate):
    f={'trace':[],'fault':False};states[id(u)]=f;u.reg_write(UC_ARM_REG_R0,arg);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,lr);u.reg_write(UC_ARM_REG_BASEPRI,0)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    try:u.emu_start((ENTRIES[name] if u is stock else syms[name])|1,lr&~1,count=2000000)
    except UcError:assert f['fault'],(name,hex(arg),u is stock,hex(u.reg_read(UC_ARM_REG_PC)))
    if not f['fault']:assert u.reg_read(UC_ARM_REG_PC)==lr&~1 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
    results.append((f['fault'],None if f['fault'] or name!='pvPortMalloc' else u.reg_read(UC_ARM_REG_R0),f['trace'],bytes(u.mem_read(0x2001e580,51232)),bytes(u.mem_read(0x200077fc,20)),u.reg_read(UC_ARM_REG_BASEPRI)))
   assert results[0]==results[1],(name,hex(arg),lr,[x[:3] for x in results],[(hex(0x2001e580+i),a,b) for i,(a,b) in enumerate(zip(results[0][3],results[1][3])) if a!=b][:20],results[0][4:],results[1][4:]);comparisons+=1;faults+=results[0][0];return results[0]
  for pattern in (0,0xa5,0xff):
   for requested in (*range(65),127,128,129,255,256,257,4095,4096,51143,51144,51151,51152,51159,51160,51167,51168,51175,51176,51183,51184,51185,51200,0x7fffffe0,0x7fffffff,0x80000000,0xffffffe0,0xfffffff0,0xffffffff):
    reset(pattern);r=call('pvPortMalloc',requested)
    if not r[0]:call('vPortFree',r[1]);assert struct.unpack('<5I',bytes(stock.mem_read(0x200077fc,20)))[1]==51184
   for order in itertools.permutations(range(4)):
    reset(pattern);handles=[call('pvPortMalloc',n,0x20000101+i*32)[1] for i,n in enumerate((1,8,33,256))]
    for i in order:call('vPortFree',handles[i])
    assert struct.unpack('<5I',bytes(stock.mem_read(0x200077fc,20)))[1]==51184
  rng=random.Random(0x855a0);reset(0x79);handles=[]
  for index in range(2000):
   if handles and rng.randrange(3)==0:call('vPortFree',handles.pop(rng.randrange(len(handles))))
   else:
    r=call('pvPortMalloc',rng.randrange(1,2049),0x20000101+(index%4)*32)
    if not r[0]:handles.append(r[1])
  for pointer in handles:call('vPortFree',pointer)
  reset(0x93);call('vPortFree',0);call('r1_heap_initialize');pointer=call('pvPortMalloc',8)[1];call('vPortFree',pointer);assert call('vPortFree',pointer)[0]
  for size,nextptr in ((16,0),(0x80000010,0x2001e600)):
   reset();call('r1_heap_initialize')
   for u in (stock,candidate):u.mem_write(0x2001e588,struct.pack('<4I',nextptr,size,0xdeadbeef,0x12345678))
   assert call('vPortFree',0x2001e598)[0]
 (out/'verification.json').write_text(json.dumps(dict(application_sha256=sha(app),report_sha256=sha(rp),driver_sha256=sha(Path(__file__)),comparisons=comparisons,assertion_comparisons=faults,backend_calls_per_implementation=backend_calls//2,heap_bytes_compared_per_call=51232,state_bytes_compared_per_call=20,scope='Actual native heap initialize/insert/malloc/free/fatal policy; request alignment/overflow/exhaustion, all four-block free permutations, deterministic fragmented sequences, NULL/double/invalid frees, header caller LR/padding, whole heap/state and guards',limitations=['Scheduler suspend/resume are bounded fixtures. Caller LR is directly controlled; real call-site normalization, scheduler concurrency, complete image linking, hardware and instruction identity remain gates.']),indent=2)+'\n');print(comparisons,'heap comparisons;',faults,'fatal assertions')
if __name__=='__main__':main()
