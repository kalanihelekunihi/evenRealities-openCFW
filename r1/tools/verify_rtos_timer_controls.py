#!/usr/bin/env python3
"""Pinned timer controls plus real timer-active body versus native instructions."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_WRITE_UNMAPPED
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ENTRIES={'osTimerStart':(0x7d9b0,58),'osTimerStop':(0x7d9ea,68),'xTimerIsTimerActive':(0x98d68,46)}
BACKENDS={'xTaskGetSchedulerState':0x987a8,'xTimerGenericCommand':0x98d04,'vPortEnterCritical':0x95cf4,'vPortExitCritical':0x95d24}
def main():
 out=BASE/'rtos-timer-controls';receipt=out/'verification.json';receipt.unlink(missing_ok=True);reports={};objects=[]
 for module,objname in [('rtos-timer-controls','timer-controls.o'),('rtos-timer-active','timer-active.o')]:
  rp=BASE/module/'report.json';r=json.loads(rp.read_text());obj=BASE/module/objname;assert sha(obj)==r['selected_object_sha256'];objects.append(obj);reports[module+'/report.json']=sha(rp)
  for p,d in r['inputs'].items():assert sha(ROOT/p)==d,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 socket='/var/folders/mh/nz9vzlpn7kzff18f77pztg880000gn/T/ghidra-mcp-kalani/ghidra-11353.sock';evidence={}
 for name,(a,length) in ENTRIES.items():
  raw=subprocess.check_output(['curl','-fsS','--max-time','20','--unix-socket',socket,f'http://localhost/read_memory?program=stock-r1-native-analysis.elf&address=0x{a:x}&length={length}']);assert bytes(json.loads(raw)['data'])==app.read_bytes()[a-0x27000:a-0x27000+length];p=out/('ghidra-'+name+'.json');p.write_bytes(raw);evidence[p.name]=sha(p)
 with tempfile.TemporaryDirectory() as directory:
  t=Path(directory);ld=t/'layout.ld';elf=t/'test.elf';binary=t/'text.bin';ld.write_text('SECTIONS { .text 0x1000000 : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }');bindings={n:0x1100001+i*16 for i,n in enumerate(BACKENDS)}
  subprocess.run(['arm-none-eabi-ld','-T',str(ld),*['--defsym='+n+'='+hex(a) for n,a in bindings.items()],*map(str,objects),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary',str(elf),str(binary)],check=True);syms={x.split()[-1]:int(x.split()[0],16) for x in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x.split())==3};image=binary.read_bytes();assert len(image)<0x10000
  states={};machines=[]
  for candidate in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x20000000,0x40000);u.mem_map(0x1000000,0x10000);u.mem_write(0x1000000,image);u.mem_map(0x1100000,0x1000);machines.append(u)
  kinds={a:n for n,a in BACKENDS.items()};kinds.update({a&~1:n for n,a in bindings.items()})
  def hook(u,a,size,_):
   if a not in kinds:return
   f=states[id(u)];n=kinds[a];args=[u.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)];value=0
   if n=='xTaskGetSchedulerState':event=(n,);value=f['scheduler']
   elif n=='xTimerGenericCommand':event=(n,*args,struct.unpack('<I',bytes(u.mem_read(u.reg_read(UC_ARM_REG_SP),4)))[0]);value=f['result']
   else:
    event=(n,)
    if f['mutate']:u.mem_write(0x20002028,bytes([1 if n=='vPortEnterCritical' else 0]))
   f['trace'].append(event);u.reg_write(UC_ARM_REG_R0,value&0xffffffff);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  def fault(u,access,address,size,value,_):
   assert address==0xffffffff and size==4 and value==0;states[id(u)]['fault']=True;u.emu_stop();return False
  for u in machines:u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_WRITE_UNMAPPED,fault)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  def case(name,timer,ticks,status,ipsr=0,primask=0,basepri=0,scheduler=1,result=1,mutate=False):
   outcomes=[]
   for candidate,u in enumerate(machines):
    states[id(u)]={'trace':[],'fault':False,'scheduler':scheduler,'result':result,'mutate':mutate};u.mem_write(0x20002000,bytes([0xa5])*44);u.mem_write(0x20002028,bytes([status]));u.reg_write(UC_ARM_REG_IPSR,ipsr);u.reg_write(UC_ARM_REG_PRIMASK,primask);u.reg_write(UC_ARM_REG_BASEPRI,basepri);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101);u.reg_write(UC_ARM_REG_R0,timer);u.reg_write(UC_ARM_REG_R1,ticks)
    for i,r in enumerate(saved):u.reg_write(r,0x12345600+i)
    try:u.emu_start((syms[name] if candidate else ENTRIES[name][0])|1,0x20000100,count=10000)
    except Exception:
     if not states[id(u)]['fault']:raise
    f=states[id(u)]
    if f['fault']:outcome=('fault',f['trace'],u.reg_read(UC_ARM_REG_BASEPRI))
    else:
     assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000
     assert [u.reg_read(r) for r in saved]==[0x12345600+i for i in range(8)]
     outcome=(u.reg_read(UC_ARM_REG_R0),f['trace'],bytes(u.mem_read(0x20002000,44)),u.reg_read(UC_ARM_REG_BASEPRI),u.reg_read(UC_ARM_REG_PRIMASK))
    outcomes.append(outcome)
   assert outcomes[0]==outcomes[1],(name,timer,ticks,status,ipsr,primask,basepri,scheduler,result,mutate,outcomes)
   return states[id(machines[0])]['fault']
  counts={};faults=0
  for name in ('osTimerStart','osTimerStop'):
   count=0
   for timer,ticks,status,ipsr,primask,basepri,scheduler,result in itertools.product((0,0x20002000),(0,1,1024,0x7fffffff,0xffffffff),(0,1,2,255),(0,16),(0,1),(0,64),(0,1,2),(0,1,0xffffffff)):
    faults+=case(name,timer,ticks,status,ipsr,primask,basepri,scheduler,result);count+=1
   counts[name]=count
  counts['xTimerIsTimerActive']=0
  for timer,status,mutate in itertools.product((0,0x20002000),range(256),(False,True)):
   faults+=case('xTimerIsTimerActive',timer,0,status,mutate=mutate);counts['xTimerIsTimerActive']+=1
 rea={n:sha(out/n) for n in ('rea-timer-start.json','rea-timer-stop.json')}
 receipt.write_text(json.dumps(dict(comparisons=sum(counts.values()),counts=counts,assertion_faults=faults,provider_reports=reports,application_sha256=sha(app),ghidra_evidence=evidence,rea_evidence=rea,verifier_sha256=sha(Path(__file__)),entries=ENTRIES,lower_providers='critical sections, scheduler-state getter and timer command are fixtures; timer-active body is real',application_linked=False,instruction_identity=False,limitations=['REA timer-active decompilation failed; native instructions, corpus and independent Ghidra bytes authenticate that body','No physical concurrency/interrupt timing or canonical graph admission']),indent=2)+'\n');print('Timer controls and active predicate:',counts,'assertions',faults)
if __name__=='__main__':main()
