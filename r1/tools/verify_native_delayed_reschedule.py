#!/usr/bin/env python3
"""Differential timer callback, isolated and composed with the real product push."""
import hashlib,itertools,json,random,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
from verify_native_delayed_schedule import A
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-delayed-reschedule';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
P={'vPortEnterCritical':0x95cf4,'vPortExitCritical':0x95d24,'osMutexAcquire':0x7d488,'osMutexRelease':0x7d536,'osTimerStart':0x7d9b0,'osKernelGetTickCount':0x7d28c,'r1_structured_log_mode_get':0x914ec,'r1_structured_log_format':0x91638,'nrf_log_frontend_std_0':0x799c0,'nrf_log_frontend_std_1':0x799c8,'nrf_log_frontend_std_2':0x799d6,'osMessageQueuePut':0x7d40c,'r1_native_delayed_push':0x659e8}
def main():
 receipt=OUT/'verification.json';receipt.unlink(missing_ok=True);reports={};objects={}
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 for module,filename in [('native-delayed-reschedule','native_delayed_reschedule.o'),('native-delayed-push','native_delayed_push.o')]:
  rp=BASE/module/'report.json';r=json.loads(rp.read_text());obj=BASE/module/filename;assert sha(obj)==r['units'][0]['object_sha256'];objects[module]=obj;reports[module+'/report.json']=sha(rp)
  for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p
 socket='/var/folders/mh/nz9vzlpn7kzff18f77pztg880000gn/T/ghidra-mcp-kalani/ghidra-11353.sock';raw=subprocess.check_output(['curl','-fsS','--max-time','20','--unix-socket',socket,'http://localhost/read_memory?program=stock-r1-native-analysis.elf&address=0x65f84&length=376']);assert bytes(json.loads(raw)['data'])==app.read_bytes()[0x65f84-0x27000:0x660fc-0x27000];(OUT/'ghidra-memory.json').write_bytes(raw)
 rea=BASE/'native-delayed-schedule/rea-65f84.json';assert json.loads(rea.read_text())['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8'
 counts={};pushes={};rng=random.Random(0x65f84)
 with tempfile.TemporaryDirectory() as directory:
  directory=Path(directory)
  for composed in (False,True):
   providers={n:a for n,a in P.items() if not (composed and n=='r1_native_delayed_push')};ld=directory/'layout.ld';elf=directory/'test.elf';binary=directory/'test.bin'
   ld.write_text('SECTIONS { .text 0x1000000 : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }\n'+'\n'.join(f'{n} = 0x{a:x};' for n,a in A.items())+'\n'+'\n'.join(f'{n} = 0x{0x1100001+i*16:x};' for i,n in enumerate(providers)))
   selected=[objects['native-delayed-reschedule']]+([objects['native-delayed-push']] if composed else []);subprocess.run(['arm-none-eabi-ld','-T',str(ld),*map(str,selected),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary',str(elf),str(binary)],check=True);syms={v[2]:int(v[0],16) for l in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(elf)],text=True).splitlines() if len(v:=l.split())==3};image=binary.read_bytes();assert len(image)<0x10000
   states={};machines=[];addresses={a:n for n,a in providers.items()};addresses.update({syms[n]&~1:n for n in providers})
   for _ in (0,1):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x20000000,0x40000);u.mem_map(0x1000000,0x10000);u.mem_write(0x1000000,image);u.mem_map(0x1100000,0x1000);machines.append(u)
   def hook(u,a,size,_):
    if a not in addresses:return
    f=states[id(u)];n=addresses[a];r=[u.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)];value=0
    def string(p):return bytes(u.mem_read(p,128)).split(b'\0')[0].decode()
    def push_event(callback,argument,timeout):
     f['pushes']+=1
     # Observe complete table at the push boundary, before controlled mutation.
     state=bytes(u.mem_read(A['r1_delayed_callbacks'],768)).hex()
     if f['mutation'] and f['pushes']==1:
      # Repopulate earlier slot and introduce a later due slot during queue submission.
      for slot,deadline in ((0,0),(63,1)):
       u.mem_write(A['r1_delayed_callbacks']+slot*4,struct.pack('<I',0x12345679+slot*2));u.mem_write(A['r1_delayed_arguments']+slot*4,struct.pack('<I',0xfedc0000+slot));u.mem_write(A['r1_delayed_deadlines']+slot*4,struct.pack('<I',deadline))
     return callback,argument,timeout,state
    if n=='r1_structured_log_mode_get':value=f['mode'][f['modes']%len(f['mode'])];f['modes']+=1;event=(n,value)
    elif n=='r1_structured_log_format':
     assert r[1]==r[2];event=(n,r[0],string(r[1]))
     if r[0]==0x04800000:event+=(r[3],struct.unpack('<I',bytes(u.mem_read(u.reg_read(UC_ARM_REG_SP),4)))[0])
     elif r[0]==0x04400000:event+=(r[3],)
    elif n.startswith('nrf_log_frontend_std_'):event=(n,r[0],string(r[1]),*r[2:2+int(n[-1])])
    elif n=='vPortEnterCritical':event=(n,);f['critical']+=1
    elif n=='vPortExitCritical':event=(n,);f['critical']-=1;assert f['critical']==0
    elif n=='osMutexAcquire':event=(n,*r[:2]);value=f['failed'][0]
    elif n=='osMutexRelease':event=(n,r[0]);value=f['failed'][1]
    elif n=='osTimerStart':event=(n,*r[:2]);value=f['failed'][2]
    elif n=='osKernelGetTickCount':event=(n,);value=f['ticks']
    elif n=='r1_native_delayed_push':event=(n,*push_event(*r[:3]))
    elif n=='osMessageQueuePut':
     argument,callback=struct.unpack('<2I',bytes(u.mem_read(r[1],8)));event=(n,r[0],r[2],*push_event(callback,argument,r[3]));value=f['queue_status']
    else:raise AssertionError(n)
    f['trace'].append(event);u.reg_write(UC_ARM_REG_R0,value&0xffffffff);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
   for u in machines:u.hook_add(UC_HOOK_CODE,hook)
   def case(input,elapsed,table,arguments,deadlines,mode,failed,ticks,mutation,ready,queue_status):
    outcomes=[]
    for candidate,u in enumerate(machines):
     states[id(u)]={'trace':[],'pushes':0,'critical':0,'modes':0,'mode':mode,'failed':failed,'ticks':ticks,'mutation':mutation,'queue_status':queue_status}
     u.mem_write(A['r1_delayed_context'],struct.pack('<6I',0x20012000,ready,0x20012100,0x20012200,0xaabbccdd,elapsed));u.mem_write(A['r1_delayed_callbacks'],struct.pack('<192I',*(table+arguments+deadlines)));u.reg_write(UC_ARM_REG_SP,0x2003e000);u.reg_write(UC_ARM_REG_LR,0x20000101);u.reg_write(UC_ARM_REG_R0,input)
     u.emu_start((syms['r1_native_delayed_reschedule']|1) if candidate else 0x65f85,0x20000100,count=50000);assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003e000 and states[id(u)]['critical']==0
     outcomes.append((states[id(u)]['trace'],bytes(u.mem_read(A['r1_delayed_context'],24)),bytes(u.mem_read(A['r1_delayed_callbacks'],768))))
    assert outcomes[0]==outcomes[1],(composed,input,elapsed,deadlines,mode,failed,mutation,outcomes)
    return states[id(machines[0])]['pushes']
   count=0;push_count=0
   for pattern,input,elapsed,mode,failed,mutation in itertools.product(range(8),(0,0xff000000,0xff000001,0xffffffff,0xfeffffff),(0,1,1024,0xffffffff),((0,),(1,),(2,),(4,),(7,),(0,4,2,1)),((0,0,0),(0xfffffffc,0xfffffffd,0xfffffffd)),(False,True)):
    table=[0]*64;arguments=[i*0x10203 for i in range(64)];deadlines=[rng.getrandbits(32) for _ in range(64)]
    if pattern==1:table[0]=0x7ca71;deadlines[0]=0
    elif pattern==2:table[31]=0x7ca71;deadlines[31]=0x7fffffff
    elif pattern==3:table[63]=0x7ca71;deadlines[63]=0xffffffff
    elif pattern==4:
     for i in range(64):table[i]=0x7ca71;deadlines[i]=i
    elif pattern==5:
     for i in range(0,64,7):table[i]=0x7ca71;deadlines[i]=rng.choice((0,1,1023,1024,1025,0x7fffffff,0xffffffff))
    elif pattern==6:table[0]=0x7ca71;deadlines[0]=(elapsed+0x7fffffff)&0xffffffff
    elif pattern==7:
     table[0]=table[63]=0x7ca71;deadlines[0]=1;deadlines[63]=2
    push_count+=case(input,elapsed,table,arguments,deadlines,mode,failed,rng.choice((0,1024,0xffffffff)),mutation,0x20013000,rng.choice((0,0xfffffffc)));count+=1
   counts['composed' if composed else 'isolated']=count;pushes['composed' if composed else 'isolated']=push_count
 receipt.write_text(json.dumps(dict(comparisons=counts,observed_pushes=pushes,provider_reports=reports,application_sha256=sha(app),object_sha256=sha(objects['native-delayed-reschedule']),report_sha256=sha(OUT/'report.json'),ghidra_memory_sha256=sha(OUT/'ghidra-memory.json'),rea_sha256=sha(rea),verifier_sha256=sha(Path(__file__)),verifier_import_sha256=sha(ROOT/'r1/tools/verify_native_delayed_schedule.py'),native_entry='0x65f84',native_size=376,application_linked=False,instruction_identity=False,limitations=['Queue, timer controls, logging and critical sections are fixtures','Composed mode executes real immediate-push body','No actual callback invocation or physical scheduling','Source initialization and canonical board composition remain gated']),indent=2)+'\n');print('Timer callback native comparisons:',counts,'push boundaries',pushes)
if __name__=='__main__':main()
