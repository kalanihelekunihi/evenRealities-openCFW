#!/usr/bin/env python3
"""Supplemental initializer/attributes versus native; factory bodies are fixtures."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-delayed-initialize';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
RAM={'context':(0x20006718,24),'callbacks':(0x20015104,256),'arguments':(0x20015204,256),'deadlines':(0x20015304,256),'queue_cb':(0x20014350,80),'queue_storage':(0x200143a0,120),'thread_cb':(0x20014418,112),'thread_stack':(0x20014488,3072),'mutex_cb':(0x20015088,80),'timer_cb':(0x200150d8,44)}
P={'osMessageQueueNew':0x7d3b4,'osTimerNew':0x7d90c,'osMutexNew':0x7d4d6,'osThreadTerminate':0x7d8d6,'osThreadNew':0x7d818,'r1_structured_log_mode_get':0x914ec,'r1_structured_log_format':0x91638,'nrf_log_frontend_std_0':0x799c0,'r1_native_delayed_reschedule':0x65f84,'r1_native_delayed_worker':0x65ea8}
def main():
 receipt=OUT/'verification.json';receipt.unlink(missing_ok=True);reports={};objects=[]
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';binary=app.read_bytes()
 for module,filename in [('native-delayed-initialize','native_delayed_initialize.o'),('native-delayed-state','native_delayed_state.o')]:
  p=BASE/module/'report.json';r=json.loads(p.read_text());obj=p.parent/filename;assert sha(obj)==r['units'][0]['object_sha256'];objects.append(obj);reports[module+'/report.json']=sha(p)
  for path,h in r['inputs'].items():assert sha(ROOT/path)==h,path
 with tempfile.TemporaryDirectory() as directory:
  t=Path(directory)
  for n,(address,size) in RAM.items():
   data=t/(n+'.bin');copy=t/'copy.o'
   subprocess.run(['arm-none-eabi-objcopy','--dump-section','.r1.delayed.'+n+'='+str(data),str(objects[1]),str(copy)],check=True)
   assert data.read_bytes()==bytes(size),n
 evidence={};socket='/var/folders/mh/nz9vzlpn7kzff18f77pztg880000gn/T/ghidra-mcp-kalani/ghidra-11353.sock'
 for name,a,length in [('initializer',0x65740,296),('attributes',0x99364,92)]:
  raw=subprocess.check_output(['curl','-fsS','--max-time','20','--unix-socket',socket,f'http://localhost/read_memory?program=stock-r1-native-analysis.elf&address=0x{a:x}&length={length}']);assert bytes(json.loads(raw)['data'])==binary[a-0x27000:a-0x27000+length];p=OUT/('ghidra-'+name+'.json');p.write_bytes(raw);evidence[p.name]={'sha256':sha(p),'address':a,'length':length}
 with tempfile.TemporaryDirectory() as directory:
  t=Path(directory);ld=t/'layout.ld';elf=t/'test.elf';text=t/'text.bin';bindings={n:0x1100001+i*16 for i,n in enumerate(P)}
  ld.write_text('SECTIONS { '+''.join('.r1.delayed.'+n+' '+hex(a)+' (NOLOAD) : { *(.r1.delayed.'+n+') } ' for n,(a,z) in RAM.items())+'.text 0x1000000 : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }')
  subprocess.run(['arm-none-eabi-ld','-T',str(ld),*['--defsym='+n+'='+hex(a) for n,a in bindings.items()],*map(str,objects),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(text)],check=True);syms={v[2]:int(v[0],16) for l in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=l.split())==3};image=text.read_bytes();assert len(image)<0x10000
  states={};machines=[];kinds={a:n for n,a in P.items()};kinds.update({a&~1:n for n,a in bindings.items()})
  for _ in (0,1):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,binary);u.mem_map(0x1000000,0x10000);u.mem_write(0x1000000,image);u.mem_map(0x1100000,0x1000);u.mem_map(0x20000000,0x40000);machines.append(u)
  def string(u,a):return bytes(u.mem_read(a,128)).split(b'\0')[0].decode()
  def attr(u,address,words):
   values=list(struct.unpack('<'+'I'*words,bytes(u.mem_read(address,words*4))));values[0]=string(u,values[0]);return tuple(values)
  def hook(u,a,size,_):
   if a not in kinds:return
   f=states[id(u)];n=kinds[a];r=[u.reg_read(reg) for reg in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)];value=0
   if n=='r1_structured_log_mode_get':value=f['mode'][f['modes']%len(f['mode'])];f['modes']+=1;event=(n,value)
   elif n=='r1_structured_log_format':assert r[1]==r[2];event=(n,r[0],string(u,r[1]))
   elif n=='nrf_log_frontend_std_0':event=(n,r[0],string(u,r[1]))
   elif n=='osThreadTerminate':event=(n,r[0]);value=0xfffffffc
   elif n in ('r1_native_delayed_reschedule','r1_native_delayed_worker'):raise AssertionError('Initializer must pass callback tokens, not invoke them')
   else:
    index={'osMessageQueueNew':0,'osTimerNew':1,'osMutexNew':2,'osThreadNew':3}[n];f['calls'][index]+=1;value=0 if f['failures']&(1<<index) else 0x20010000+index*256+f['calls'][index]*16
    if n=='osMessageQueueNew':event=(n,r[0],r[1],attr(u,r[2],6))
    elif n=='osTimerNew':
     assert r[0]==(0x65f85 if u is machines[0] else bindings['r1_native_delayed_reschedule']);event=(n,'timer_callback',r[1],r[2],attr(u,r[3],4))
    elif n=='osMutexNew':event=(n,attr(u,r[0],4))
    else:
     assert r[0]==(0x65ea9 if u is machines[0] else bindings['r1_native_delayed_worker']);assert struct.unpack('<I',bytes(u.mem_read(0x2000671c,4)))[0]==0;event=(n,'worker',r[1],attr(u,r[2],9))
   f['trace'].append(event);u.reg_write(UC_ARM_REG_R0,value);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  for u in machines:u.hook_add(UC_HOOK_CODE,hook)
  # Authenticate source zero-storage semantics against the stock cold startup.
  cold=machines[0];cold.reg_write(UC_ARM_REG_SP,0x2003f000);cold.emu_start(0x283a1,0x27208,count=2000000);assert cold.reg_read(UC_ARM_REG_PC)==0x27208
  for n,(a,z) in RAM.items():assert bytes(cold.mem_read(a,z))==bytes(z),n
  counts=0
  for initial,failures,mode in itertools.product(range(16),range(16),((0,),(1,),(2,),(4,),(7,),(0,4,2,1))):
   for u in machines:
    states[id(u)]={'trace':[],'calls':[0]*4,'failures':failures,'modes':0,'mode':mode};context=[0x20018000+i*256 if initial&(1<<i) else 0 for i in range(4)]+[0x89abcdef,0xfedcba98];u.mem_write(0x20006718,struct.pack('<6I',*context));u.mem_write(0x20015104,bytes([0xa5])*768)
   for repeat in range(2):
    results=[]
    for candidate,u in enumerate(machines):
     u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
     u.emu_start((syms['r1_native_delayed_initialize']|1) if candidate else 0x65741,0x20000100,count=10000);assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000
     results.append((states[id(u)]['trace'],bytes(u.mem_read(0x20006718,24)),bytes(u.mem_read(0x20015104,768))))
    assert results[0]==results[1],(initial,failures,mode,repeat,results);counts+=1
 receipt.write_text(json.dumps(dict(comparisons=counts,initialization_sequences=1536,provider_reports=reports,verifier_sha256=sha(Path(__file__)),application_sha256=sha(app),ghidra_evidence=evidence,zero_state_ranges=RAM,supplemental_entry='0x65740',locked_ownership_row=False,source_state_compiled=True,source_attributes_compiled=True,provider_interception=True,application_linked=False,instruction_identity=False,limitations=['Factory and thread-terminate bodies remain controlled fixtures','Native callback tokens normalized only after exact address validation; ARM32 callback argument ABI retained','No worker invocation, lifecycle/kernel composition or canonical integration','Cold startup authenticates zero storage; complete source startup not established']),indent=2)+'\n');print('Supplemental initializer:',counts,'comparisons; source state and attributes authenticated')
if __name__=='__main__':main()
