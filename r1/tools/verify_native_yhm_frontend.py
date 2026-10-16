#!/usr/bin/env python3
"""Native YHM frontend ABI and callback reload checks; lower transport is a fixture."""
import hashlib,itertools,json,random,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'r1/research/source-build/native-yhm-frontend';C=0x200075c4
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ENTRIES={'r1_yhm_ready_native':(0x3541c,28),'r1_yhm_register_read_native':(0x3540c,6),'r1_yhm_register_read_byte_native':(0x35412,8)}
def main():
 vp=OUT/'verification.json';vp.unlink(missing_ok=True);rp=OUT/'report.json';report=json.loads(rp.read_text());obj=OUT/'native_yhm_frontend.o'
 assert sha(obj)==report['units'][0]['object_sha256']
 for p,h in report['inputs'].items():assert sha(ROOT/p)==h
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';app_hash=sha(app);assert app_hash=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 socket='/var/folders/mh/nz9vzlpn7kzff18f77pztg880000gn/T/ghidra-mcp-kalani/ghidra-11353.sock';ghidra={}
 for n,(a,z) in ENTRIES.items():
  raw=subprocess.check_output(['curl','-fsS','--max-time','20','--unix-socket',socket,f'http://localhost/read_memory?program=stock-r1-native-analysis.elf&address=0x{a:x}&length={z}']);assert bytes(json.loads(raw)['data'])==app.read_bytes()[a-0x27000:a-0x27000+z]
  p=OUT/('ghidra-'+n+'.json');p.write_bytes(raw);ghidra[p.name]=sha(p)
 for n,(a,z) in ENTRIES.items():
  r=json.loads((OUT/f'rea-{a:x}.json').read_text());assert r['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8';assert r['normalized_result']['entrypoint']==hex(a) and r['normalized_result']['body']['total_bytes']==z
 counts={n:0 for n in ENTRIES};rng=random.Random(0x3541c)
 with tempfile.TemporaryDirectory() as directory:
  d=Path(directory);ld=d/'layout.ld';elf=d/'test.elf';binary=d/'text.bin';ld.write_text('SECTIONS { .text 0x1000000 : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }')
  subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--defsym=r1_stacmd='+hex(C),'--defsym=r1_yhm_register_read_record=0x1100001',str(obj),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary',str(elf),str(binary)],check=True)
  syms={v[2]:int(v[0],16) for l in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=l.split())==3};image=binary.read_bytes();assert len(image)<65536;machines=[];states={}
  def hook(u,a,size,_):
   f=states[id(u)];r=[u.reg_read(reg) for reg in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2)]
   if a in (0x507cc,0x1100000):
    f['trace'].append(('read',r[0],r[1],r[2]));assert r[2]==0x20002010
    if f['write']:u.mem_write(r[2],bytes([f['byte']]))
    result=f['result']
   elif a==0x1100020:
    f['trace'].append(('select',r[0],r[1]));result=0xdeadbeef
    if f['mutation']:
     u.mem_write(C+12,struct.pack('<I',0x87654321));u.mem_write(C+40,struct.pack('<I',0x1100061))
   elif a in (0x1100040,0x1100060):f['trace'].append(('probe',a,r[0]));result=f['result']
   else:
    if id(u)==id(machines[1]) and a<0x1000000 and a!=0x20000100:raise AssertionError(('unexpected native source execution',hex(a)))
    return
   u.reg_write(UC_ARM_REG_R0,result);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  for _ in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,65536);u.mem_write(0x1000000,image);u.mem_map(0x1100000,4096);u.mem_map(0x20000000,0x40000);machines.append(u);u.hook_add(UC_HOOK_CODE,hook)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  def case(name,reg=0,length=0,result=0,mutation=False,write=False,byte=0,line=0,context=0):
   results=[]
   for candidate,u in enumerate(machines):
    states[id(u)]={'trace':[],'result':result,'mutation':mutation,'write':write,'byte':byte};u.mem_write(C,b'\xa5'*48);u.mem_write(C+12,struct.pack('<I',context));u.mem_write(C+28,struct.pack('<I',0x1100021));u.mem_write(C+32,bytes([line]));u.mem_write(C+40,struct.pack('<I',0x1100041));u.mem_write(0x20002000,b'\x96'*32)
    u.reg_write(UC_ARM_REG_R0,reg);u.reg_write(UC_ARM_REG_R1,0x20002010 if name=='r1_yhm_register_read_byte_native' else length);u.reg_write(UC_ARM_REG_R2,0x20002010);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
    for i,r in enumerate(saved):u.reg_write(r,0x12345600+i)
    u.emu_start((syms[name] if candidate else ENTRIES[name][0])|1,0x20000100,count=1000)
    assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(r) for r in saved]==[0x12345600+i for i in range(8)]
    results.append((u.reg_read(UC_ARM_REG_R0),states[id(u)]['trace'],bytes(u.mem_read(C,48)),bytes(u.mem_read(0x20002000,32))))
   assert results[0]==results[1],(name,reg,length,result,mutation,results)
   if name=='r1_yhm_ready_native':assert results[0][0]==int(result!=0) and results[0][1]==[('select',context,line),('probe',0x1100060 if mutation else 0x1100040,0x87654321 if mutation else context)]
   else:assert results[0][0]==result and results[0][1]==[('read',reg,1 if name=='r1_yhm_register_read_byte_native' else length&255,0x20002010)]
   counts[name]+=1
  for result,mutation,line,context in itertools.product((0,1,2,0x80000000,0xffffffff),(False,True),(0,1,127,255),(0,1,0x20014418,0xffffffff)):case('r1_yhm_ready_native',result=result,mutation=mutation,line=line,context=context)
  for name in ('r1_yhm_register_read_native','r1_yhm_register_read_byte_native'):
   for reg,length,result,write in itertools.product((0,1,6,255,256,0x80000000,0xffffffff),(0,1,255,256,257,0xffffffff),(0,1,0x80000000,0xffffffff),(False,True)):case(name,reg,length,result,write=write,byte=rng.randrange(256))
 vp.write_text(json.dumps(dict(comparisons=sum(counts.values()),counts=counts,report_sha256=sha(rp),object_sha256=sha(obj),driver_sha256=sha(Path(__file__)),application_sha256=app_hash,ghidra_evidence=ghidra,rea_evidence={p.name:sha(p) for p in OUT.glob('rea-*.json')},application_linked=False,instruction_identity=False,limitations=['Read record transport is a fixture; both output-write and no-write outcomes tested','Callback context is a test address binding; source initialization and hardware concurrency unresolved','Raw status stack-byte semantics remain gated; these wrappers do not invent read success checks']),indent=2)+'\n');print('YHM frontend:',counts)
if __name__=='__main__':main()
