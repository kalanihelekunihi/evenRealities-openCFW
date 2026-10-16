#!/usr/bin/env python3
"""Bounded supplemental worker loops versus native; queue/callbacks are fixtures."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_FETCH_UNMAPPED
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-delayed-worker';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
P={'osMessageQueueGet':0x7d310,'r1_structured_log_mode_get':0x914ec,'r1_structured_log_format':0x91638,'nrf_log_frontend_std_1':0x799c8}
def main():
 receipt=OUT/'verification.json';receipt.unlink(missing_ok=True);rp=OUT/'report.json';r=json.loads(rp.read_text());obj=OUT/'native_delayed_worker.o';assert sha(obj)==r['units'][0]['object_sha256']
 for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';raw=subprocess.check_output(['curl','-fsS','--max-time','20','--unix-socket','/var/folders/mh/nz9vzlpn7kzff18f77pztg880000gn/T/ghidra-mcp-kalani/ghidra-11353.sock','http://localhost/read_memory?program=stock-r1-native-analysis.elf&address=0x65ea8&length=96']);assert bytes(json.loads(raw)['data'])==app.read_bytes()[0x65ea8-0x27000:0x65f08-0x27000];(OUT/'ghidra-memory.json').write_bytes(raw)
 comparisons=0;faults=0;callbacks=0;receives=0
 with tempfile.TemporaryDirectory() as directory:
  d=Path(directory);ld=d/'layout.ld';elf=d/'test.elf';binary=d/'text.bin';bindings={n:0x1100001+i*16 for i,n in enumerate(P)};ld.write_text('SECTIONS { .text 0x1000000 : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }');subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--defsym=r1_delayed_context=0x20006718',*['--defsym='+n+'='+hex(a) for n,a in bindings.items()],str(obj),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary',str(elf),str(binary)],check=True);syms={v[2]:int(v[0],16) for l in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=l.split())==3};image=binary.read_bytes();assert len(image)<0x10000;machines=[];states={};kinds={a:n for n,a in P.items()};kinds.update({a&~1:n for n,a in bindings.items()})
  for _ in (0,1):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,0x10000);u.mem_write(0x1000000,image);u.mem_map(0x1100000,0x1000);u.mem_map(0x1200000,0x1000);u.mem_map(0x20000000,0x40000);machines.append(u)
  def string(u,p):return bytes(u.mem_read(p,128)).split(b'\0')[0].decode()
  def hook(u,a,size,_):
   f=states[id(u)]
   if u is machines[1]:assert not 0x20000<=a<0xe0000,('source entered stock code',hex(a))
   if a in (0x1200000,0x1200010):
    f['callbacks']+=1;f['trace'].append(('callback',a,u.reg_read(UC_ARM_REG_R0)))
    if f['mutate']:u.mem_write(0x20006718,struct.pack('<I',0x20010000+f['callbacks']*64))
    for i,reg in enumerate((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)):u.reg_write(reg,0xdead0000+i)
    u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR));return
   if a not in kinds:return
   n=kinds[a];r=[u.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)];value=0
   if n=='osMessageQueueGet':
    if f['next']==len(f['statuses']):f['boundary']=True;u.emu_stop();return
    index=f['next'];f['next']+=1;value=f['statuses'][index];event=(n,r[0],r[2],r[3]);assert r[2]==0 and r[3]==0xffffffff
    if value==0:
     callback=0 if f['null'] and index==len(f['statuses'])-1 else 0x1200001+(index%2)*16
     u.mem_write(r[1],struct.pack('<2I',0x89abcdef+index,callback))
   elif n=='r1_structured_log_mode_get':value=f['mode'][f['modes']%len(f['mode'])];f['modes']+=1;event=(n,value)
   elif n=='r1_structured_log_format':assert r[1]==r[2];event=(n,r[0],string(u,r[1]),r[3])
   elif n=='nrf_log_frontend_std_1':event=(n,r[0],string(u,r[1]),r[2])
   else:raise AssertionError(n)
   f['trace'].append(event);u.reg_write(UC_ARM_REG_R0,value);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  def fault(u,access,address,size,value,_):
   assert address==0;states[id(u)]['fault']=True;u.emu_stop();return False
  for u in machines:u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_FETCH_UNMAPPED,fault)
  def case(statuses,mode,mutate,null=False):
   nonlocal comparisons,faults,callbacks,receives
   results=[]
   for candidate,u in enumerate(machines):
    states[id(u)]={'trace':[],'callbacks':0,'next':0,'modes':0,'mode':mode,'statuses':statuses,'mutate':mutate,'null':null,'boundary':False,'fault':False};u.mem_write(0x20006718,struct.pack('<6I',0x20011000,0x12345678,0,0,0x89abcdef,0xfedcba98));u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101);u.reg_write(UC_ARM_REG_R0,0x13579bdf)
    try:u.emu_start((syms['r1_native_delayed_worker']|1) if candidate else 0x65ea9,0x20000100,count=10000)
    except UcError:
     if not states[id(u)]['fault']:raise
    f=states[id(u)];assert f['fault'] or f['boundary'];results.append((f['trace'],bytes(u.mem_read(0x20006718,24)),f['fault'],f['boundary']))
   assert results[0]==results[1],(statuses,mode,mutate,null,results);comparisons+=1;f=states[id(machines[0])];faults+=f['fault'];callbacks+=f['callbacks'];receives+=f['next']
  for statuses,mode,mutate in itertools.product(itertools.product((0,1,0xfffffffc,0xfffffffd,0x80000000),repeat=3),((0,),(1,),(2,),(4,),(7,),(0,4,2,1)),(False,True)):
   case(statuses,mode,mutate)
  for mode,mutate in itertools.product(((0,),(1,),(2,),(4,),(7,),(0,4,2,1)),(False,True)):case((0xfffffffc,0,0),mode,mutate,True)
 receipt.write_text(json.dumps(dict(comparisons=comparisons,null_callback_faults=faults,callback_invocations_per_implementation=callbacks,queue_receives_per_implementation=receives,report_sha256=sha(rp),object_sha256=sha(obj),verifier_sha256=sha(Path(__file__)),application_sha256=sha(app),ghidra_memory_sha256=sha(OUT/'ghidra-memory.json'),supplemental_entry='0x65ea8',native_size=96,locked_ownership_row=False,application_linked=False,instruction_identity=False,limitations=['Queue and callback execution are controlled fixtures; queue success supplies the full8-byte record','Stops at the next receive boundary or authenticated null callback fault; no worker return/SP-restoration claim','Source ignores worker argument; no physical scheduling or actual blocked receive/resume','Supplemental recovery is outside locked ownership/corpus rows']),indent=2)+'\n');print('Supplemental worker:',comparisons,'bounded comparisons;',callbacks,'callbacks;',faults,'null callback faults')
if __name__=='__main__':main()
