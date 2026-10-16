#!/usr/bin/env python3
"""Compare both real classifier entries with native, leaving raw status explicit."""
import hashlib,json,random,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'r1/research/source-build/native-charger-state'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ENTRIES={'r1_yhm_charge_state_native':(0x35272,40),'r1_native_charger_state_get':(0x50618,4)}
def main():
 receipt=OUT/'verification.json';receipt.unlink(missing_ok=True)
 report=OUT/'report.json';r=json.loads(report.read_text());obj=OUT/'native_charger_state.o'
 assert sha(obj)==r['units'][0]['object_sha256']
 for p,h in r['inputs'].items():assert sha(ROOT/p)==h
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';app_hash=sha(app)
 assert app_hash=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 socket='/var/folders/mh/nz9vzlpn7kzff18f77pztg880000gn/T/ghidra-mcp-kalani/ghidra-11353.sock';evidence={}
 for n,(a,z) in ENTRIES.items():
  raw=subprocess.check_output(['curl','-fsS','--max-time','20','--unix-socket',socket,f'http://localhost/read_memory?program=stock-r1-native-analysis.elf&address=0x{a:x}&length={z}'])
  assert bytes(json.loads(raw)['data'])==app.read_bytes()[a-0x27000:a-0x27000+z]
  p=OUT/('ghidra-'+n+'.json');p.write_bytes(raw);evidence[p.name]=sha(p)
 for p in OUT.glob('rea-*.json'):
  q=json.loads(p.read_text());assert q['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8'
 body=json.loads((OUT/'rea-classifier-body.json').read_text())['normalized_result']['body']
 assert body['total_bytes']==26 and body['span_bytes']==40 and body['ranges']==[{'start':'0x35272','end':'0x3527f'},{'start':'0x3528e','end':'0x35299'}]
 rng=random.Random(0x35272);values=[*range(256),0x7fffffff,0x80000000,0xfffffffa,0xffffffff,*[rng.getrandbits(32) for _ in range(2048)]];counts={n:0 for n in ENTRIES}
 with tempfile.TemporaryDirectory() as directory:
  d=Path(directory);ld=d/'layout.ld';elf=d/'test.elf';binary=d/'text.bin'
  ld.write_text('SECTIONS { .text 0x1000000 : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }')
  subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--defsym=r1_yhm_status_native=0x1100001',str(obj),'-o',str(elf)],check=True,capture_output=True)
  subprocess.run(['arm-none-eabi-objcopy','-O','binary',str(elf),str(binary)],check=True)
  syms={v[2]:int(v[0],16) for l in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=l.split())==3}
  image=binary.read_bytes();assert len(image)<65536;machines=[];states={}
  def hook(u,a,size,_):
   if a in (0x3529a,0x1100000):
    states[id(u)]['calls']+=1;u.reg_write(UC_ARM_REG_R0,states[id(u)]['status']);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
   elif id(u)==id(machines[1]) and a<0x1000000 and a!=0x20000100:raise AssertionError(('unexpected native source execution',hex(a)))
  for _ in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,65536);u.mem_write(0x1000000,image);u.mem_map(0x1100000,4096);u.mem_map(0x20000000,0x40000);machines.append(u);u.hook_add(UC_HOOK_CODE,hook)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  for name,(a,z) in ENTRIES.items():
   for status in values:
    results=[]
    for candidate,u in enumerate(machines):
     states[id(u)]={'status':status,'calls':0};u.mem_write(0x20002000,b'\xa5'*64);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
     for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
     u.emu_start((syms[name] if candidate else a)|1,0x20000100,count=1000)
     assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000
     assert [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
     assert bytes(u.mem_read(0x20002000,64))==b'\xa5'*64
     results.append((u.reg_read(UC_ARM_REG_R0),states[id(u)]['calls']))
    expected=1 if 10<=status<=12 else 2 if status==13 else 0
    assert results==[(expected,1),(expected,1)],(name,status,results);counts[name]+=1
 receipt.write_text(json.dumps(dict(comparisons=sum(counts.values()),counts=counts,report_sha256=sha(report),object_sha256=sha(obj),driver_sha256=sha(Path(__file__)),application_sha256=app_hash,ghidra_evidence=evidence,rea_evidence={p.name:sha(p) for p in OUT.glob('rea-*.json')},classifier_body_bytes=26,classifier_span_bytes=40,table_bytes=14,application_linked=False,instruction_identity=False,limitations=['Raw status is a fixture; native read failure may retain an incoming stack byte','Existing contextual YHM model checks transport result; no silent substitution','Whole battery provider graph, canonical admission and source state initialization remain gates']),indent=2)+'\n')
 print('Charger classifier:',counts)
if __name__=='__main__':main()
