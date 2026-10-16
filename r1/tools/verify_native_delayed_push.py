#!/usr/bin/env python3
"""Check immediate push and its real delayed-scheduler caller against stock."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC
from verify_native_delayed_schedule import P as SCHEDULE_PROVIDERS,A
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-delayed-push';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
P={**{n:a for n,a in SCHEDULE_PROVIDERS.items() if n!='r1_native_delayed_push'},'nrf_log_frontend_std_1':0x799c8,'osMessageQueuePut':0x7d40c}
def main():
 receipt=OUT/'verification.json';receipt.unlink(missing_ok=True)
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 providers={};objects=[]
 for module,filename in [('native-delayed-push','native_delayed_push.o'),('native-delayed-schedule','native_delayed_schedule.o')]:
  rp=BASE/module/'report.json';r=json.loads(rp.read_text());obj=BASE/module/filename;assert sha(obj)==r['units'][0]['object_sha256'];objects.append(obj);providers[module+'/report.json']=sha(rp)
  for path,digest in r['inputs'].items():assert sha(ROOT/path)==digest,path
 socket='/var/folders/mh/nz9vzlpn7kzff18f77pztg880000gn/T/ghidra-mcp-kalani/ghidra-11353.sock'
 raw=subprocess.check_output(['curl','-fsS','--max-time','20','--unix-socket',socket,'http://localhost/read_memory?program=stock-r1-native-analysis.elf&address=0x659e8&length=144']);assert bytes(json.loads(raw)['data'])==app.read_bytes()[0x659e8-0x27000:0x65a78-0x27000];(OUT/'ghidra-memory.json').write_bytes(raw)
 rea=BASE/'native-delayed-schedule/rea-659e8.json';assert json.loads(rea.read_text())['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8'
 with tempfile.TemporaryDirectory() as directory:
  d=Path(directory);ld=d/'layout.ld';elf=d/'test.elf';binary=d/'test.bin'
  ld.write_text('SECTIONS { .text 0x1000000 : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }\n'+'\n'.join(f'{n} = 0x{v:x};' for n,v in A.items())+'\n'+'\n'.join(f'{n} = 0x{0x1100001+i*16:x};' for i,n in enumerate(P)))
  subprocess.run(['arm-none-eabi-ld','-T',str(ld),*map(str,objects),'-o',str(elf)],check=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary',str(elf),str(binary)],check=True)
  syms={v[2]:int(v[0],16) for l in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(elf)],text=True).splitlines() if len(v:=l.split())==3};image=binary.read_bytes();assert len(image)<0x10000
  def run(candidate,case):
   entry,ready,queue,status,mode,callback,argument,timeout,mutation=case
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x20000000,0x40000);u.mem_map(0x1000000,0x10000);u.mem_write(0x1000000,image);u.mem_map(0x1100000,0x1000)
   u.mem_write(A['r1_delayed_context'],struct.pack('<6I',queue,ready,0x20012100,0x20012200,1000,2000));u.mem_write(A['r1_delayed_callbacks'],bytes([0x5a])*768)
   events=[];modes=0;waits=0;addresses={syms[n]&~1 if candidate else a:n for n,a in P.items()}
   def string(a):return bytes(u.mem_read(a,128)).split(b'\0')[0].decode()
   def hook(uc,a,size,_):
    nonlocal modes,waits
    if a==0x26000:uc.emu_stop();return
    if a not in addresses:return
    n=addresses[a];r=[uc.reg_read(reg) for reg in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)];value=0
    if n=='r1_structured_log_mode_get':
     value=mode[modes%len(mode)];modes+=1;event=(n,value)
     if mutation:uc.mem_write(A['r1_delayed_context'],struct.pack('<I',0x20012400))
    elif n=='r1_structured_log_format':
     assert r[1]==r[2];event=(n,r[0],string(r[1]))+((r[3],) if r[0]==0x04400000 else ())
    elif n=='nrf_log_frontend_std_0':event=(n,r[0],string(r[1]))
    elif n=='nrf_log_frontend_std_1':event=(n,r[0],string(r[1]),r[2])
    elif n=='osMessageQueuePut':
     event=(n,r[0],bytes(uc.mem_read(r[1],8)).hex(),r[2],r[3]);value=status
     if mutation:uc.mem_write(A['r1_delayed_context']+4,struct.pack('<I',0))
    elif n=='osDelay':
     assert r[0]==10;waits+=1;event=(n,r[0])
     if waits==2:uc.mem_write(A['r1_delayed_context']+4,struct.pack('<I',0x20013000))
    else:raise AssertionError(('Unexpected lower call',n,r))
    events.append(event);uc.reg_write(UC_ARM_REG_R0,value);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook);sp=0x2003e000;u.reg_write(UC_ARM_REG_SP,sp);u.reg_write(UC_ARM_REG_LR,0x26001)
   for reg,value in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2),(callback,argument,timeout)):u.reg_write(reg,value)
   native=0x659e9 if entry=='push' else 0x65b4d;name='r1_native_delayed_push' if entry=='push' else 'r1_native_delayed_schedule'
   u.emu_start((syms[name]|1) if candidate else native,0x26000,count=10000);assert u.reg_read(UC_ARM_REG_PC)==0x26000 and u.reg_read(UC_ARM_REG_SP)==sp
   return events,bytes(u.mem_read(A['r1_delayed_context'],24)),bytes(u.mem_read(A['r1_delayed_callbacks'],768))
  counts={}
  for entry in ('push','schedule'):
   total=0
   for ready,queue,status,mode,callback,argument,timeout,mutation in itertools.product((0,0x20013000),(0,0x20012000),(0,0xfffffffc,0xfffffffd,0xffffffff),((0,),(1,),(2,),(4,),(7,),(0,4,2,1)),(0,0x7ca71),(0,0x89abcdef),((0,1,0xffffffff) if entry=='push' else (0,1)),(False,True)):
    c=(entry,ready,queue,status,mode,callback,argument,timeout,mutation);a=run(False,c);b=run(True,c);assert a==b,(c,a,b);total+=1
   counts[entry]=total
 receipt.write_text(json.dumps(dict(comparisons=counts['push'],schedule_composition_comparisons=counts['schedule'],report_sha256=sha(OUT/'report.json'),object_sha256=sha(OUT/'native_delayed_push.o'),provider_reports=providers,application_sha256=sha(app),ghidra_memory_sha256=sha(OUT/'ghidra-memory.json'),rea_sha256=sha(rea),verifier_sha256=sha(Path(__file__)),verifier_import_sha256=sha(ROOT/'r1/tools/verify_native_delayed_schedule.py'),native_entry='0x659e8',native_size=144,lower_providers='controlled fixtures; real schedule and push compose',application_linked=False,instruction_identity=False,limitations=['Only immediate-delay scheduler paths composed','No actual queue/kernel graph or state initialization admission','Void ABI; caller-saved scratch/stack bytes not compared']),indent=2)+'\n');print('Immediate push and scheduler composition passed:',counts)
if __name__=='__main__':main()
