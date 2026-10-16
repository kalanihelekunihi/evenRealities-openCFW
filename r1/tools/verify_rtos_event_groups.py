#!/usr/bin/env python3
"""Native event set/ISR/deferred callback and timer-pend contracts, bounded wake/queue fixtures."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_INVALID
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();E=0x20001000
ENTRIES={'xEventGroupSetBits':0x977f4,'xEventGroupGetBitsFromISR':0x977de,'xEventGroupSetBitsFromISR':0x9787c,'vEventGroupSetBitsCallback':0x95c8c,'xTimerPendFunctionCallFromISR':0x98d98}
BACKENDS={'vTaskSuspendAll':0x9659c,'xTaskResumeAll':0x98b24,'vTaskRemoveFromUnorderedEventList':0x963e8,'xQueueGenericSendFromISR':0x97da4}
def main():
 out=BASE/'rtos-event-groups';vp=out/'verification.json';vp.unlink(missing_ok=True);reports={};objects=[]
 for name,file in [('rtos-event-groups','event-groups.o'),('rtos-timer-pend','timer-pend.o')]:
  rp=BASE/name/'report.json';r=json.loads(rp.read_text());o=rp.parent/file;assert sha(o)==r['selected_object_sha256'];objects.append(o);reports[name+'/report.json']=sha(rp)
  for p,d in r['inputs'].items():assert sha(ROOT/p)==d,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';states={};comparisons=0;faults=0;counts={n:0 for n in ENTRIES}
 with tempfile.TemporaryDirectory() as directory:
  t=Path(directory);ld=t/'layout.ld';elf=t/'test.elf';binary=t/'text.bin';ld.write_text('SECTIONS { .text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } /DISCARD/ : { *(.comment) *(.note*) } }');bindings={n:0x100ee01+i*16 for i,n in enumerate(BACKENDS)};subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--defsym=xTimerQueue=0x2000785c',*['--defsym='+n+'='+hex(a) for n,a in bindings.items()],*map(str,objects),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True);syms={x.split()[-1]:int(x.split()[0],16) for x in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x.split())==3};stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
  for u in (stock,candidate):u.mem_map(0x20000,0xc0000);u.mem_map(0x1000000,0x10000);u.mem_map(0x20000000,0x40000);u.mem_map(0xe000e000,4096)
  stock.mem_write(0x27000,app.read_bytes());candidate.mem_write(0x1000000,binary.read_bytes());kinds={a:n for n,a in BACKENDS.items()};kinds.update({a&~1:n for n,a in bindings.items()})
  def word(u,a):return struct.unpack('<I',bytes(u.mem_read(a,4)))[0]
  def put(u,a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
  def hook(u,a,size,user):
   if a not in kinds:return
   f=states[id(u)];name=kinds[a];args=[u.reg_read(reg) for reg in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)];value=0;trace=(name,)
   if name=='vTaskSuspendAll':put(u,0x20007850,word(u,0x20007850)+1)
   elif name=='xTaskResumeAll':put(u,0x20007850,word(u,0x20007850)-1);value=1
   elif name=='vTaskRemoveFromUnorderedEventList':
    item=args[0];trace=(name,item,args[1]);container=word(u,item+16);n=word(u,item+4);p=word(u,item+8);put(u,item,args[1]|0x80000000);put(u,n+8,p);put(u,p+4,n)
    if word(u,container+4)==item:put(u,container+4,p)
    put(u,container,word(u,container)-1);put(u,item+16,0)
   elif name=='xQueueGenericSendFromISR':
    message=list(struct.unpack('<4I',bytes(u.mem_read(args[1],16))));assert message[0]==0xfffffffe
    if f['name']=='xEventGroupSetBitsFromISR':assert message[1]==(0x95c8d if u is stock else syms['vEventGroupSetBitsCallback']|1);message[1]=0x95c8d
    trace=(name,args[0],message,bool(args[2]),args[3]);assert args[3]==0;value=f['status']
    if args[2]:put(u,args[2],f['yield'])
   f['trace'].append(trace);u.reg_write(UC_ARM_REG_R0,value&0xffffffff);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  def fault(u,access,a,size,value,user):states[id(u)]['fault']=(access,a,value);return False
  for u in (stock,candidate):u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_INVALID,fault)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  def case(name,args,bits=0,waiters=(),mask=0,queue=0x20004000,status=1,yielding=0):
   nonlocal comparisons,faults
   results=[]
   for u in (stock,candidate):
    f={'name':name,'trace':[],'fault':None,'status':status,'yield':yielding};states[id(u)]=f;u.mem_write(E,bytes([0x93])*0x4100);put(u,E,bits);u.mem_write(E+4,struct.pack('<5I',0,E+12,0xffffffff,E+12,E+12));put(u,0x20007850,0);put(u,0x2000785c,queue);put(u,0x20005000,0x12345678)
    for index,(value,all_bits,clear) in enumerate(waiters):
     item=0x20002000+index*32;tail=word(u,E+20);u.mem_write(item,struct.pack('<5I',value|(0x04000000 if all_bits else 0)|(0x01000000 if clear else 0),E+12,tail,0x20003000+index*256,E+4));put(u,tail+4,item);put(u,E+20,item);put(u,E+4,index+1)
    u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101);u.reg_write(UC_ARM_REG_BASEPRI,mask)
    for reg,value in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),args):u.reg_write(reg,value)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    try:u.emu_start((ENTRIES[name] if u is stock else syms[name])|1,0x20000100,count=100000)
    except UcError:assert f['fault'],(name,args,u is stock,hex(u.reg_read(UC_ARM_REG_PC)))
    if not f['fault']:assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
    results.append((f['fault'],None if f['fault'] or name=='vEventGroupSetBitsCallback' else u.reg_read(UC_ARM_REG_R0),f['trace'],bytes(u.mem_read(E,0x4100)),bytes(u.mem_read(0x20007850,16)),u.reg_read(UC_ARM_REG_BASEPRI)))
   assert results[0]==results[1],(name,args,bits,waiters,mask,[x[:3] for x in results],[(i,a,b) for i,(a,b) in enumerate(zip(results[0][3],results[1][3])) if a!=b][:16]);comparisons+=1;faults+=bool(results[0][0]);counts[name]+=1
  shapes=[(),((1,False,True),(2,False,False),(3,True,True)),((4,False,True),(2,True,True),(1,False,False))]+[((value,all_bits,clear),) for value,all_bits,clear in itertools.product((1,2,3),(0,1),(0,1))]
  for name,bits,flags,waiters,mask in itertools.product(('xEventGroupSetBits','vEventGroupSetBitsCallback'),(0,1,3,7,0xffffff),(0,1,2,3,4,0xffffff,0x1000000,0xffffffff),shapes,(0,64,224)):case(name,(E,flags),bits,waiters,mask)
  for bits,mask,ptr in itertools.product((0,1,3,0xffffff,0xffffffff),(0,64,224),(0,E)):case('xEventGroupGetBitsFromISR',(ptr,),bits=bits,mask=mask)
  for ptr,flags,queue,status,woken,yielding in itertools.product((0,E),(0,1,0xffffff,0xffffffff),(0,0x20004000),(0,1,0xffffffff),(0,0x20005000),(0,1,0xffffffff)):case('xEventGroupSetBitsFromISR',(ptr,flags,woken),queue=queue,status=status,yielding=yielding)
  for callback,param,value,queue,status,woken,yielding in itertools.product((0,0x100f001),(0,E,0xffffffff),(0,1,0xffffffff),(0,0x20004000),(0,1,0xffffffff),(0,0x20005000),(0,1,0xffffffff)):case('xTimerPendFunctionCallFromISR',(callback,param,value,woken),queue=queue,status=status,yielding=yielding)
  for name in ('xEventGroupSetBits','vEventGroupSetBitsCallback'):case(name,(0,1))
 vp.write_text(json.dumps(dict(application_sha256=sha(app),provider_reports=reports,driver_sha256=sha(Path(__file__)),comparisons=comparisons,fault_comparisons=faults,comparisons_by_function=counts,scope='Actual pinned event set/get-ISR/set-ISR/callback and shared timer-pend body; bit any/all matching, waiter ordering/clear-on-exit, assertions, mask restore and exact four-word command-2 payload',limitations=['Unordered task wake/removal and scheduler/ISR queue send are explicit fixtures. Callback code and event set execute together; no actual deferred timer queue drain or physical ISR/task resumption is established. Callback pointer normalized only after exact native/source symbol check. Not canonical admission or image identity proof.']),indent=2)+'\n');print(comparisons,'event/pended callback comparisons;',faults,'faults;',counts)
if __name__=='__main__':main()
