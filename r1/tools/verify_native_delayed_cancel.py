#!/usr/bin/env python3
"""Native cancellation including wildcard/null matching and ordered epoch reads."""
import hashlib,itertools,json,random,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
from verify_native_delayed_schedule import A
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-delayed-cancel';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
P={'osMutexAcquire':0x7d488,'osMutexRelease':0x7d536,'osTimerStop':0x7d9ea,'osKernelGetTickCount':0x7d28c,'r1_native_delayed_reschedule':0x65f84,'r1_structured_log_mode_get':0x914ec,'r1_structured_log_format':0x91638,'nrf_log_frontend_std_0':0x799c0}
def main():
 vp=OUT/'verification.json';vp.unlink(missing_ok=True);rp=OUT/'report.json';r=json.loads(rp.read_text());obj=OUT/'native_delayed_cancel.o';assert sha(obj)==r['units'][0]['object_sha256']
 for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';raw=subprocess.check_output(['curl','-fsS','--max-time','20','--unix-socket','/var/folders/mh/nz9vzlpn7kzff18f77pztg880000gn/T/ghidra-mcp-kalani/ghidra-11353.sock','http://localhost/read_memory?program=stock-r1-native-analysis.elf&address=0x65d64&length=228']);assert bytes(json.loads(raw)['data'])==app.read_bytes()[0x65d64-0x27000:0x65e48-0x27000];(OUT/'ghidra-memory.json').write_bytes(raw)
 rea=json.loads((OUT/'rea-pseudocode.json').read_text());assert rea['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8'
 rng=random.Random(0x65d64);count=0;matched=0
 with tempfile.TemporaryDirectory() as directory:
  d=Path(directory);ld=d/'layout.ld';elf=d/'test.elf';binary=d/'text.bin';bindings={n:0x1100001+i*16 for i,n in enumerate(P)};ld.write_text('SECTIONS { .text 0x1000000 : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }');subprocess.run(['arm-none-eabi-ld','-T',str(ld),*['--defsym='+n+'='+hex(a) for n,a in {**bindings,**A}.items()],str(obj),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary',str(elf),str(binary)],check=True);syms={v[2]:int(v[0],16) for l in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=l.split())==3};image=binary.read_bytes();assert len(image)<0x10000;states={};machines=[];kinds={a:n for n,a in P.items()};kinds.update({a&~1:n for n,a in bindings.items()})
  for _ in (0,1):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,0x10000);u.mem_write(0x1000000,image);u.mem_map(0x1100000,0x1000);u.mem_map(0x20000000,0x40000);machines.append(u)
  def hook(u,a,size,_):
   if a not in kinds:return
   f=states[id(u)];n=kinds[a];r=[u.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2)];value=0
   def string(p):return bytes(u.mem_read(p,128)).split(b'\0')[0].decode()
   if n=='osMutexAcquire':event=(n,*r[:2]);value=f['failed'][0]
   elif n=='osMutexRelease':event=(n,r[0]);value=f['failed'][1]
   elif n=='osKernelGetTickCount':
    event=(n,);value=f['ticks']
    if f['mutation']:u.mem_write(0x20006728,struct.pack('<I',0x12345678))
   elif n=='osTimerStop':
    event=(n,r[0]);value=0xfffffffc
    if f['mutation']:u.mem_write(0x20006728,struct.pack('<I',0x87654321))
   elif n=='r1_native_delayed_reschedule':event=(n,r[0])
   elif n=='r1_structured_log_mode_get':value=f['mode'][f['modes']%len(f['mode'])];f['modes']+=1;event=(n,value)
   elif n=='r1_structured_log_format':assert r[1]==r[2];event=(n,r[0],string(r[1]))
   elif n=='nrf_log_frontend_std_0':event=(n,r[0],string(r[1]))
   else:raise AssertionError(n)
   f['trace'].append(event);u.reg_write(UC_ARM_REG_R0,value);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  for u in machines:u.hook_add(UC_HOOK_CODE,hook)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  for pattern,callback,argument,ready,failed,mode,mutation in itertools.product(range(8),(0,0x7ca71,0xffffffff),(0,1,0x89abcdef),(0,0x20014418),((0,0),(0xfffffffc,0),(0,0xfffffffd),(0xfffffffc,0xfffffffd)),((0,),(1,),(2,),(4,),(7,),(0,4,2,1)),(False,True)):
   table=[0]*64;arguments=[rng.choice((0,1,0x89abcdef,0xffffffff)) for _ in range(64)];deadlines=[rng.getrandbits(32) for _ in range(64)]
   if pattern in (1,2,3):slot=(0,31,63)[pattern-1];table[slot]=callback;arguments[slot]=argument
   elif pattern==4:
    for i in range(0,64,3):table[i]=callback;arguments[i]=argument if i%2 else argument^0x55555555
   elif pattern==5:table=[0x12345679]*64
   elif pattern==6:table=[callback]*64;arguments=[argument]*64
   elif pattern==7:table=[rng.choice((0,callback,0x12345679)) for _ in range(64)]
   ticks=rng.choice((0,1,1024,0x00418938,0xffffffff));epoch=rng.choice((0,1,0xffffffff));results=[]
   for candidate,u in enumerate(machines):
    states[id(u)]={'trace':[],'failed':failed,'mode':mode,'modes':0,'ticks':ticks,'mutation':mutation};u.mem_write(0x20006718,struct.pack('<6I',0x20014350,ready,0x20015088,0x200150d8,epoch,0xabcdef01));u.mem_write(0x20015104,struct.pack('<192I',*(table+arguments+deadlines)));u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101);u.reg_write(UC_ARM_REG_R0,callback);u.reg_write(UC_ARM_REG_R1,argument)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    u.emu_start((syms['r1_native_delayed_cancel']|1) if candidate else 0x65d65,0x20000100,count=10000);assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
    results.append((u.reg_read(UC_ARM_REG_R0),states[id(u)]['trace'],bytes(u.mem_read(0x20006718,24)),bytes(u.mem_read(0x20015104,768))))
   assert results[0]==results[1],(pattern,callback,argument,ready,failed,mode,mutation,results);count+=1;matched+=results[0][0]
 vp.write_text(json.dumps(dict(comparisons=count,matched_cases=matched,report_sha256=sha(rp),object_sha256=sha(obj),verifier_sha256=sha(Path(__file__)),helper_sha256=sha(ROOT/'r1/tools/verify_native_delayed_schedule.py'),application_sha256=sha(app),ghidra_memory_sha256=sha(OUT/'ghidra-memory.json'),rea_sha256=sha(OUT/'rea-pseudocode.json'),native_entry='0x65d64',native_size=228,application_linked=False,instruction_identity=False,limitations=['Mutex/timer/log/tick/reschedule providers are fixtures','Preserves null-callback slot matches, argument0 wildcard, ignored acquire failure and ordered tick/epoch read','Actual cancellation/timer graph and canonical admission remain separate gates']),indent=2)+'\n');print('Cancellation:',count,'native comparisons;',matched,'matches')
if __name__=='__main__':main()
