#!/usr/bin/env python3
"""Compare unchanged pinned queue/list providers with authenticated R1 code."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_INVALID
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ROOTS={'xQueueGenericCreate':0x97b0e,'xQueueGenericCreateStatic':0x97b62,'xQueueCreateCountingSemaphore':0x97a88,'xQueueCreateCountingSemaphoreStatic':0x97ab0,'xQueueGenericReset':0x97ba4}
BACKENDS={'pvPortMalloc':0x855a0,'vPortEnterCritical':0x95cf4,'vPortExitCritical':0x95d24,'xTaskRemoveFromEventList':0x98a4c}
def main():
 out=BASE/'rtos-queue-create';(out/'verification.json').unlink(missing_ok=True);rp=out/'report.json';r=json.loads(rp.read_text());obj=out/'queue-create.o';assert sha(obj)==r['selected_object_sha256']
 for p,d in r['inputs'].items():assert sha(ROOT/p)==d,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';states={};count=0;assertions=0
 with tempfile.TemporaryDirectory() as directory:
  t=Path(directory);ld=t/'layout.ld';elf=t/'test.elf';binary=t/'text.bin';ld.write_text('SECTIONS { .text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } /DISCARD/ : { *(.comment) *(.note*) } }');bindings={n:0x100ef01+i*16 for i,n in enumerate(BACKENDS)};subprocess.run(['arm-none-eabi-ld','-T',str(ld),*['--defsym='+n+'='+hex(a) for n,a in bindings.items()],str(obj),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True);syms={x.split()[-1]:int(x.split()[0],16) for x in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x.split())==3}
  stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
  for u in (stock,candidate):
   u.mem_map(0x20000,0xc0000);u.mem_map(0x1000000,0x10000);u.mem_map(0x20000000,0x40000);u.mem_map(0xe000e000,0x2000)
  stock.mem_write(0x27000,app.read_bytes());candidate.mem_write(0x1000000,binary.read_bytes());kinds={a:n for n,a in BACKENDS.items()};kinds.update({a&~1:n for n,a in bindings.items()})
  def hook(u,a,size,user):
   name=kinds.get(a)
   if not name:return
   f=states[id(u)];arg=u.reg_read(UC_ARM_REG_R0);f['trace'].append((name,arg) if name in ('pvPortMalloc','xTaskRemoveFromEventList') else (name,));value=f['allocation'] if name=='pvPortMalloc' else f['remove'] if name=='xTaskRemoveFromEventList' else 0xdeadbeef;u.reg_write(UC_ARM_REG_R0,value);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  def fault(u,access,address,size,value,user):
   if address==0xffffffff and value==0:states[id(u)]['assert']=True
   return False
  for u in (stock,candidate):u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_INVALID,fault)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  cases=[]
  for length,item,kind,allocation in itertools.product((1,2,7,32),(0,1,4,17),(0,2,3,255),(0,0x20004000)):
   cases.append(('xQueueGenericCreate',(length,item,kind),allocation,0,0,0))
  for length,item,kind in itertools.product((1,2,7,32),(0,1,4,17),(0,2,3,255)):
   cases.append(('xQueueGenericCreateStatic',(length,item,0x20005000 if item else 0,0x20004000,kind),0,0,0,0))
  for length,initial in itertools.product((1,2,7,32),(0,1,2,7,32)):
   if initial<=length:
    for allocation in (0,0x20004000):cases.append(('xQueueCreateCountingSemaphore',(length,initial),allocation,0,0,0))
    cases.append(('xQueueCreateCountingSemaphoreStatic',(length,initial,0x20004000),0,0,0,0))
  for length,item,new,waiting,remove in itertools.product((1,2,7,32),(0,1,4,17),(0,1),(0,1),(0,1)):
   cases.append(('xQueueGenericReset',(0x20004000,new),0,waiting,remove,(length,item)))
  cases += [('xQueueGenericCreate',args,0,0,0,0) for args in ((0,0,3),(0x80000000,2,3),(0xffffffff,1,3),(1,0xffffffb0,3))]
  cases += [('xQueueCreateCountingSemaphore',(a,b),0,0,0,0) for a,b in ((0,0),(1,2),(2,0xffffffff))]
  cases += [('xQueueGenericReset',(a,1),0,0,0,shape) for a,shape in ((0,0),(0x20004000,(0,1)),(0x20004000,(0xffffffff,2)))]
  for name,args,allocation,waiting,remove,shape in cases:
   results=[]
   for u in (stock,candidate):
    f={'trace':[],'allocation':allocation,'remove':remove,'assert':False};states[id(u)]=f;u.mem_write(0x20003ff0,bytes([0xa5])*0x1200);u.mem_write(0xe000ed04,bytes(4));u.reg_write(UC_ARM_REG_BASEPRI,0);u.reg_write(UC_ARM_REG_PRIMASK,0);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
    if shape:
     length,item=shape
     for offset,value in ((0,0x20005000),(16,waiting),(60,length),(64,item)):u.mem_write(0x20004000+offset,struct.pack('<I',value))
    for i,reg in enumerate((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)):u.reg_write(reg,args[i] if i<len(args) else 0xdeadbeef)
    if len(args)>4:u.mem_write(0x2003f000,struct.pack('<I',args[4]))
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    try:u.emu_start((ROOTS[name] if u is stock else syms[name])|1,0x20000100,count=100000)
    except UcError:
     assert f['assert'],(name,args,hex(u.reg_read(UC_ARM_REG_PC)))
    if not f['assert']:assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
    results.append((f['assert'],None if f['assert'] else u.reg_read(UC_ARM_REG_R0),f['trace'],bytes(u.mem_read(0x20003ff0,0x1200)),bytes(u.mem_read(0xe000ed04,4)),u.reg_read(UC_ARM_REG_BASEPRI)))
   assert results[0]==results[1],(name,args,allocation,waiting,remove,shape,[(x[:3],x[4:]) for x in results],[(i,a,b) for i,(a,b) in enumerate(zip(results[0][3],results[1][3])) if a!=b][:20]);count+=1;assertions+=results[0][0]
 (out/'verification.json').write_text(json.dumps(dict(application_sha256=sha(app),report_sha256=sha(rp),driver_sha256=sha(Path(__file__)),comparisons=count,assertion_comparisons=assertions,scope='Actual unchanged pinned FreeRTOS queue constructors, initializer, reset and list initialization; full dirty 80-byte queue/storage canaries, allocation failure, counting values, static storage, reset wait-list/yield and fatal assertion paths',limitations=['Allocator, critical entry/exit and task removal are bounded fixtures. Actual task removal/scheduler, allocation, whole-image identity and physical behavior remain gates.']),indent=2)+'\n');print(count,'queue comparisons;',assertions,'assertions')
if __name__=='__main__':main()
