#!/usr/bin/env python3
"""Pinned timer creation, real callback/ID getter versus native; factory boundaries explicit."""
import hashlib,itertools,json,struct,subprocess,tempfile,csv
from pathlib import Path
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_WRITE_UNMAPPED,UC_HOOK_MEM_FETCH_UNMAPPED
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'rtos-timer-new';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ENTRIES={'osTimerNew':(0x7d90c,158),'TimerCallback':(0x34088,24),'pvTimerGetTimerID':(0x8569c,34)}
P={'xTaskGetSchedulerState':0x987a8,'pvPortMalloc':0x855a0,'vPortFree':0x95d48,'xTimerCreate':0x98c48,'xTimerCreateStatic':0x98c7c,'vPortEnterCritical':0x95cf4,'vPortExitCritical':0x95d24}
def main():
 vp=OUT/'verification.json';vp.unlink(missing_ok=True);reports={};objects=[]
 for module,filename in [('rtos-timer-new','timer-new.o'),('rtos-timer-id','timer-id.o')]:
  p=BASE/module/'report.json';r=json.loads(p.read_text());obj=p.parent/filename;assert sha(obj)==r['selected_object_sha256'];objects.append(obj);reports[module+'/report.json']=sha(p)
  for f,h in r['inputs'].items():assert sha(ROOT/f)==h,f
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';evidence={};socket='/var/folders/mh/nz9vzlpn7kzff18f77pztg880000gn/T/ghidra-mcp-kalani/ghidra-11353.sock'
 for n,(a,z) in ENTRIES.items():
  raw=subprocess.check_output(['curl','-fsS','--max-time','20','--unix-socket',socket,f'http://localhost/read_memory?program=stock-r1-native-analysis.elf&address=0x{a:x}&length={z}']);assert bytes(json.loads(raw)['data'])==app.read_bytes()[a-0x27000:a-0x27000+z];p=OUT/('ghidra-'+n+'.json');p.write_bytes(raw);evidence[p.name]=sha(p)
 ownership=ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv';row=next(x for x in csv.DictReader(ownership.open()) if x['image']=='application' and x['entry']=='0x0008569c')
 correction={'original_row':row,'effective_symbol':'pvTimerGetTimerID','evidence':'Timer callback0x34088 supplies its TimerHandle_t to0x8569c, reads callback metadata from returned ID after clearing allocation bit; native getter reads offset28 under critical section. Pinned timer ID getter matches; original task-tag label is not supported for this call path.'};(OUT/'attribution-correction.json').write_text(json.dumps(correction,indent=2)+'\n')
 counts={n:0 for n in ENTRIES};faults=0;callbacks=0
 with tempfile.TemporaryDirectory() as directory:
  d=Path(directory);ld=d/'layout.ld';elf=d/'test.elf';binary=d/'text.bin';bindings={n:0x1100001+i*16 for i,n in enumerate(P)};ld.write_text('SECTIONS { .text 0x1000000 : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }');subprocess.run(['arm-none-eabi-ld','-T',str(ld),*['--defsym='+n+'='+hex(a) for n,a in bindings.items()],*map(str,objects),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary',str(elf),str(binary)],check=True);syms={v[2]:int(v[0],16) for l in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=l.split())==3};image=binary.read_bytes();assert len(image)<0x10000;machines=[];states={};kinds={a:n for n,a in P.items()};kinds.update({a&~1:n for n,a in bindings.items()})
  for _ in (0,1):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,0x10000);u.mem_write(0x1000000,image);u.mem_map(0x1100000,0x1000);u.mem_map(0x1200000,0x1000);u.mem_map(0x20000000,0x40000);machines.append(u)
  def hook(u,a,size,_):
   f=states[id(u)]
   if a==0x1200000:f['trace'].append(('user_callback',u.reg_read(UC_ARM_REG_R0)));u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR));return
   if a not in kinds:return
   n=kinds[a];r=[u.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)];value=0
   if n=='xTaskGetSchedulerState':event=(n,);value=f['scheduler']
   elif n=='pvPortMalloc':assert r[0]==8;event=(n,r[0]);value=0x20004000 if f['malloc'] else 0
   elif n=='vPortFree':event=(n,r[0])
   elif n in ('xTimerCreate','xTimerCreateStatic'):
    extra=struct.unpack('<2I',bytes(u.mem_read(u.reg_read(UC_ARM_REG_SP),8)));assert extra[0]==(0x34089 if u is machines[0] else syms['TimerCallback']|1);event=(n,*r,'CMSIS_callback')+((extra[1],) if n=='xTimerCreateStatic' else ());value=0x20007000 if f['create'] else 0
   else:event=(n,)
   f['trace'].append(event);u.reg_write(UC_ARM_REG_R0,value);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  def fault(u,access,a,size,value,_):
   assert a in (0,0xffffffff);states[id(u)]['fault']=(a,size,value);u.emu_stop();return False
  for u in machines:u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_WRITE_UNMAPPED,fault);u.hook_add(UC_HOOK_MEM_FETCH_UNMAPPED,fault)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  def case(name,args,attr=None,irq=(0,0,0,2),malloc=True,create=True,timer_id=0,callback=0x1200001):
   nonlocal faults,callbacks
   outcomes=[]
   for candidate,u in enumerate(machines):
    states[id(u)]={'trace':[],'scheduler':irq[3],'malloc':malloc,'create':create,'fault':None};u.mem_write(0x20002000,bytes([0xa5])*128);u.mem_write(0x2000201c,struct.pack('<I',timer_id));u.mem_write(0x20003000,struct.pack('<4I',*attr) if attr is not None else bytes(16));u.mem_write(0x20004000,bytes([0xb6])*16);u.mem_write(0x20005000,struct.pack('<2I',callback,0x89abcdef));u.mem_write(0x20006000,b'Timer\0');u.reg_write(UC_ARM_REG_IPSR,irq[0]);u.reg_write(UC_ARM_REG_PRIMASK,irq[1]);u.reg_write(UC_ARM_REG_BASEPRI,irq[2]);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    for reg,v in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),args):u.reg_write(reg,v)
    try:u.emu_start((syms[name]|1) if candidate else ENTRIES[name][0]|1,0x20000100,count=10000)
    except UcError:
     if not states[id(u)]['fault']:raise
    f=states[id(u)]
    if not f['fault']:assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
    outcomes.append((f['fault'],None if name=='TimerCallback' or f['fault'] else u.reg_read(UC_ARM_REG_R0),f['trace'],bytes(u.mem_read(0x20002000,128)),bytes(u.mem_read(0x20004000,16)),u.reg_read(UC_ARM_REG_BASEPRI)))
   assert outcomes[0]==outcomes[1],(name,args,attr,irq,malloc,create,timer_id,outcomes);counts[name]+=1;faults+=bool(states[id(machines[0])]['fault']);callbacks+=sum(e[0]=='user_callback' for e in states[id(machines[0])]['trace'])
  attrs=[None]+[(name,0xabcdef01,cb,size) for name,cb,size in itertools.product((0,0x20006000),(0,0x20002000),(0,1,43,44,51,52,64,0xffffffff))]
  for attr,func,type,malloc,create,irq in itertools.product(attrs,(0,0x1200001),(0,1,0xffffffff),(False,True),(False,True),((0,0,0,1),(0,0,0,2),(16,0,0,2),(0,1,0,2),(0,0,64,2),(0,1,64,1))):
   case('osTimerNew',(func,type,0x89abcdef,0x20003000 if attr is not None else 0),attr,irq,malloc,create)
  for timer,timer_id,callback in itertools.product((0,0x20002000),(0,1,0x20005000,0x20005001),(0,0x1200001)):
   case('TimerCallback',(timer,),timer_id=timer_id,callback=callback)
  for timer,timer_id in itertools.product((0,0x20002000),(0,1,0x20005000,0x20005001,0xffffffff)):case('pvTimerGetTimerID',(timer,),timer_id=timer_id)
 rea={n:sha(OUT/n) for n in ('rea-creation.json','rea-callback.json')}
 vp.write_text(json.dumps(dict(comparisons=sum(counts.values()),counts=counts,assertion_or_null_callback_faults=faults,user_callbacks_per_implementation=callbacks,provider_reports=reports,driver_sha256=sha(Path(__file__)),application_sha256=sha(app),ghidra_evidence=evidence,rea_evidence=rea,attribution_correction_sha256=sha(OUT/'attribution-correction.json'),entries=ENTRIES,application_linked=False,instruction_identity=False,limitations=['Malloc/free, timer factories, critical boundaries and scheduler-state getter are controlled fixtures','Callback trampoline executes actual timer-ID getter; user callback is a fixture','Only licensed pinned bodies admitted; locked ownership correction retained separately','REA ID getter query failed; independent native bytes, caller and source contract support that entry']),indent=2)+'\n');print('CMSIS timer creation/callback/getter:',counts,'faults',faults)
if __name__=='__main__':main()
