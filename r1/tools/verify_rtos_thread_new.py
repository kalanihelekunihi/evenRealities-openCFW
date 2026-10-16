#!/usr/bin/env python3
"""CMSIS thread attributes/context versus native; constructor fixtures only."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
BACKENDS={'xTaskGetSchedulerState':0x987a8,'r1_native_task_create':0x983b8,'r1_native_task_create_static':0x98418}
def main():
 out=BASE/'rtos-thread-new';receipt=out/'verification.json';receipt.unlink(missing_ok=True);rp=out/'report.json';r=json.loads(rp.read_text());obj=out/'thread-new.o';assert sha(obj)==r['selected_object_sha256']
 for p,d in r['inputs'].items():assert sha(ROOT/p)==d,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';states={};comparisons=0;calls=0
 with tempfile.TemporaryDirectory() as directory:
  t=Path(directory);ld=t/'layout.ld';elf=t/'test.elf';binary=t/'text.bin';ld.write_text('SECTIONS { .text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } /DISCARD/ : { *(.comment) *(.note*) } }');bindings={n:0x100ef01+i*16 for i,n in enumerate(BACKENDS)};subprocess.run(['arm-none-eabi-ld','-T',str(ld),*['--defsym='+n+'='+hex(a) for n,a in bindings.items()],str(obj),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True);syms={x.split()[-1]:int(x.split()[0],16) for x in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x.split())==3}
  stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
  for u in (stock,candidate):u.mem_map(0x20000,0xc0000);u.mem_map(0x1000000,0x10000);u.mem_map(0x20000000,0x40000)
  stock.mem_write(0x27000,app.read_bytes());candidate.mem_write(0x1000000,binary.read_bytes());kinds={a:n for n,a in BACKENDS.items()};kinds.update({a&~1:n for n,a in bindings.items()})
  def hook(u,a,size,user):
   nonlocal calls
   if a not in kinds:return
   f=states[id(u)];name=kinds[a];calls+=1
   if name=='xTaskGetSchedulerState':trace=(name,);value=f['scheduler']
   else:
    args=[u.reg_read(reg) for reg in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)];sp=u.reg_read(UC_ARM_REG_SP);extra=struct.unpack('<3I',bytes(u.mem_read(sp,12)))
    if name=='r1_native_task_create':
     priority,out=extra[:2];assert out&3==0 and struct.unpack('<I',bytes(u.mem_read(out,4)))[0]==0;trace=(name,*args,priority);u.mem_write(out,struct.pack('<I',f['handle']));value=f['status']
    else:trace=(name,*args,*extra);value=f['handle']
   f['trace'].append(trace);u.reg_write(UC_ARM_REG_R0,value&0xffffffff);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  for u in (stock,candidate):u.hook_add(UC_HOOK_CODE,hook)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  def case(attr,code=0x12345679,ipsr=0,primask=0,basepri=0,scheduler=1,handle=0x20003300,status=1):
   nonlocal comparisons
   results=[]
   for u in (stock,candidate):
    states[id(u)]={'trace':[],'scheduler':scheduler,'handle':handle,'status':status};u.mem_write(0x20003000,struct.pack('<9I',*attr) if attr else bytes(36));u.mem_write(0x20003200,b'thread\0');u.mem_write(0x20003300,bytes([0x95])*128);u.mem_write(0x20004000,bytes([0xa5])*256);u.reg_write(UC_ARM_REG_IPSR,ipsr);u.reg_write(UC_ARM_REG_PRIMASK,primask);u.reg_write(UC_ARM_REG_BASEPRI,basepri);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
    for reg,value in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2),(code,0x87654321,0x20003000 if attr else 0)):u.reg_write(reg,value)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    u.emu_start((0x7d818 if u is stock else syms['osThreadNew'])|1,0x20000100,count=100000);assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)];results.append((u.reg_read(UC_ARM_REG_R0),states[id(u)]['trace'],bytes(u.mem_read(0x20003000,36)),bytes(u.mem_read(0x20003300,128)),bytes(u.mem_read(0x20004000,256)),u.reg_read(UC_ARM_REG_IPSR),u.reg_read(UC_ARM_REG_PRIMASK),u.reg_read(UC_ARM_REG_BASEPRI)))
   assert results[0]==results[1],(attr,code,ipsr,primask,basepri,scheduler,handle,status,results);comparisons+=1
  for cb,cbsize,stack,stacksize,priority,bits,handle,status in itertools.product((0,0x20003300),(0,91,92,111,112,113),(0,0x20004000),(0,1,3,4,5,1023,1024,262144,262148,0xffffffff),(0,1,24,55,56,57,0xffffffff),(0,1,2,0x80000000),(0,0x20003300),(0,1,0xffffffff)):
   case((0xfffffff0,bits,cb,cbsize,stack,stacksize,priority,0xffffffff,0x12345678),handle=handle,status=status)
  representatives=(None,(0,0,0,0,0,0,0,0,0),(0x20003200,0,0,0,0,129,55,1,0),(0x20003200,0,0x20003300,112,0x20004000,129,38,1,0),(0,1,0x20003300,112,0x20004000,128,24,0,0),(0,0,0x20003300,111,0x20004000,128,24,0,0))
  for attr,code,ipsr,primask,basepri,scheduler,handle,status in itertools.product(representatives,(0,0x12345679),(0,16),(0,1),(0,128),(0,1,2),(0,0x20003300),(0,1,0xffffffff)):case(attr,code,ipsr,primask,basepri,scheduler,handle,status)
 receipt.write_text(json.dumps(dict(application_sha256=sha(app),report_sha256=sha(rp),driver_sha256=sha(Path(__file__)),comparisons=comparisons,backend_calls_per_implementation=calls//2,scope='Actual unchanged CMSIS osThreadNew/IRQ predicate,112-byte static threshold, attr combinations, priority/joinable rules, defaults, static32/dynamic16-bit depth, ignored fields, allocator status and interrupt/mask states',limitations=['Native constructors and scheduler-state read are fixtures in this unit. Attribute acceptance does not establish successful kernel construction; priority56 and tiny stacks retain native downstream behavior. No task execution, context switching, hardware or whole-image identity proof.']),indent=2)+'\n');print(comparisons,'CMSIS thread-new comparisons;',calls//2,'backend calls')
if __name__=='__main__':main()
