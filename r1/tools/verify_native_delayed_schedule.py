#!/usr/bin/env python3
"""Differential product-body test; lower providers are controlled fixtures."""
import hashlib,itertools,json,random,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build/native-delayed-schedule'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
P={'r1_structured_log_mode_get':0x914ec,'r1_structured_log_format':0x91638,'nrf_log_frontend_std_0':0x799c0,'osDelay':0x7d154,'osMutexAcquire':0x7d488,'osMutexRelease':0x7d536,'osTimerStop':0x7d9ea,'osKernelGetTickCount':0x7d28c,'r1_native_delayed_push':0x659e8,'r1_native_delayed_reschedule':0x65f84}
A={'r1_delayed_context':0x20006718,'r1_delayed_callbacks':0x20015104,'r1_delayed_arguments':0x20015204,'r1_delayed_deadlines':0x20015304}
def main():
 receipt=BASE/'verification.json';receipt.unlink(missing_ok=True)
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 obj=BASE/'native_delayed_schedule.o';report=BASE/'report.json';r=json.loads(report.read_text());assert sha(obj)==r['units'][0]['object_sha256']
 for path,digest in r['inputs'].items():assert sha(ROOT/path)==digest,path
 # Independent Ghidra-MCP read must match the authenticated shipped bytes.
 socket='/var/folders/mh/nz9vzlpn7kzff18f77pztg880000gn/T/ghidra-mcp-kalani/ghidra-11353.sock'
 raw=subprocess.check_output(['curl','-fsS','--max-time','20','--unix-socket',socket,'http://localhost/read_memory?program=stock-r1-native-analysis.elf&address=0x65b4c&length=308'])
 gh=json.loads(raw);native=app.read_bytes()[0x65b4c-0x27000:0x65c80-0x27000];assert bytes(gh['data'])==native
 (BASE/'ghidra-memory.json').write_bytes(raw)
 rea=json.loads((BASE/'rea-pseudocode.json').read_text());assert rea['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8'
 with tempfile.TemporaryDirectory() as d:
  d=Path(d);ld=d/'layout.ld';elf=d/'test.elf';binary=d/'test.bin'
  ld.write_text('SECTIONS { .text 0x1000000 : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }\n'+'\n'.join(f'{n} = 0x{v:x};' for n,v in A.items())+'\n'+'\n'.join(f'{n} = 0x{0x1100001+i*16:x};' for i,n in enumerate(P)))
  subprocess.run(['arm-none-eabi-ld','-T',str(ld),str(obj),'-o',str(elf)],check=True)
  subprocess.run(['arm-none-eabi-objcopy','-O','binary',str(elf),str(binary)],check=True)
  symbols={line.split()[2]:int(line.split()[0],16) for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(elf)],text=True).splitlines() if len(line.split())==3}
  image=binary.read_bytes();assert len(image)<0x10000
  def run(candidate,case):
   slot,delay,mode,failed,ready,callback,ticks,epoch=case
   uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);uc.mem_map(0x20000,0xc0000);uc.mem_write(0x27000,app.read_bytes());uc.mem_map(0x20000000,0x40000);uc.mem_map(0x1000000,0x10000);uc.mem_write(0x1000000,image);uc.mem_map(0x1100000,0x1000)
   context=struct.pack('<6I',0x20012000,ready,0x20012100,0x20012200,epoch,0x12345678);uc.mem_write(A['r1_delayed_context'],context)
   table=[0x77770001+i*2 for i in range(64)];
   if slot<64:table[slot]=0
   uc.mem_write(A['r1_delayed_callbacks'],struct.pack('<192I',*(table+[0xaabbccdd]*64+[0x11223344]*64)))
   events=[];waits=0;modes=0
   addresses={symbols[n]&~1 if candidate else a:n for n,a in P.items()}
   def string(a):
    data=bytes(uc.mem_read(a,128));return data.split(b'\0')[0].decode()
   def hook(u,a,size,_):
    nonlocal waits,modes
    if a==0x26000:u.emu_stop();return
    if a not in addresses:return
    n=addresses[a];args=[u.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2)];value=0
    if n=='r1_structured_log_mode_get':
     # Changing modes checks repeated getter calls and short-circuit behavior.
     value=mode[modes%len(mode)];modes+=1;event=(n,value)
    elif n in ('r1_structured_log_format','nrf_log_frontend_std_0'):event=(n,args[0],string(args[1]))
    elif n=='osDelay':
     waits+=1;event=(n,args[0]);assert args[0]==10
     if waits==3:u.mem_write(A['r1_delayed_context']+4,struct.pack('<I',0x20013000))
    elif n=='osMutexAcquire':event=(n,*args[:2]);value=failed[0]
    elif n=='osMutexRelease':event=(n,args[0]);value=failed[1]
    elif n=='osTimerStop':event=(n,args[0]);value=0xfffffffd
    elif n=='osKernelGetTickCount':event=(n,);value=ticks
    elif n=='r1_native_delayed_push':event=(n,*args)
    elif n=='r1_native_delayed_reschedule':event=(n,args[0])
    else:raise AssertionError(n)
    events.append(event);u.reg_write(UC_ARM_REG_R0,value);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
   uc.hook_add(UC_HOOK_CODE,hook);sp=0x2003e000;uc.reg_write(UC_ARM_REG_SP,sp);uc.reg_write(UC_ARM_REG_LR,0x26001)
   for reg,value in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2),(callback,0x89abcdef,delay)):uc.reg_write(reg,value)
   uc.emu_start((symbols['r1_native_delayed_schedule']|1) if candidate else 0x65b4d,0x26000,count=10000)
   assert uc.reg_read(UC_ARM_REG_PC)==0x26000 and uc.reg_read(UC_ARM_REG_SP)==sp
   return events,bytes(uc.mem_read(A['r1_delayed_context'],24)),bytes(uc.mem_read(A['r1_delayed_callbacks'],768))
  rng=random.Random(0x65b4c);cases=[]
  for slot,delay,mode,failed,ready in itertools.product((0,1,31,63,64),(0,1,2,3072,0xffffffff),((0,),(1,),(2,),(4,),(7,),(0,4,2,1,0)),((0,0),(0xfffffffc,0),(0,0xfffffffd),(0xfffffffc,0xfffffffd)),(0,0x20013000)):
   cases.append((slot,delay,mode,failed,ready,rng.choice((0,0x7ca71,0x12345679)),rng.choice((0,1024,0x00418938,0xffffffff)),rng.choice((0,1000,0xffffffff))))
  for i,c in enumerate(cases):
   a=run(False,c);b=run(True,c);assert a==b,(i,c,a,b)
 receipt.write_text(json.dumps(dict(comparisons=len(cases),source_inputs=r['inputs'],report_sha256=sha(report),object_sha256=sha(obj),application_sha256=sha(app),ghidra_memory_sha256=sha(BASE/'ghidra-memory.json'),rea_sha256=sha(BASE/'rea-pseudocode.json'),verifier_sha256=sha(Path(__file__)),native_entry='0x65b4c',native_size=308,contract='void; trace and complete context plus 192 table words',lower_providers='controlled fixtures',application_linked=False,instruction_identity=False,unresolved=['immediate push 0x659e8','reschedule 0x65f84','osTimerStop 0x7d9ea','context/table initialization and canonical composition']),indent=2)+'\n')
 print('Delayed scheduler:',len(cases),'native/source comparisons passed')
if __name__=='__main__':main()
