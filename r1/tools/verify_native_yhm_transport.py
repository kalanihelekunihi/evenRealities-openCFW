#!/usr/bin/env python3
"""Native YHM transport state/callback contracts with registry boundary fixtures."""
import argparse,hashlib,itertools,json,random,struct,subprocess,tempfile,csv
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'r1/research/source-build/native-yhm-transport';C=0x2000687c;Q=0x20016b70
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ENTRIES={'r1_yhm_transport_acquire':(0x50608,8),'r1_yhm_transport_release':(0x507a0,8),'r1_yhm_transport_complete':(0x50558,26),'r1_yhm_register_read_record':(0x507cc,46),'r1_yhm_register_write_record':(0x50804,46),'r1_yhm_register_write_native':(0x35760,6)}
P={'r1_stock_dispatch_08':0x85d1a,'r1_stock_dispatch_0c':0x85cba,'r1_stock_dispatch_10':0x85d2c,'r1_stock_dispatch_14':0x85da8}
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--real-registry',action='store_true');args=parser.parse_args();real_registry=args.real_registry
 vp=OUT/('registry-integration-verification.json' if real_registry else 'verification.json');vp.unlink(missing_ok=True);rp=OUT/'report.json';report=json.loads(rp.read_text());obj=OUT/'native_yhm_transport.o'
 assert sha(obj)==report['units'][0]['object_sha256']
 for p,h in report['inputs'].items():assert sha(ROOT/p)==h
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';app_hash=sha(app);assert app_hash=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 socket='/var/folders/mh/nz9vzlpn7kzff18f77pztg880000gn/T/ghidra-mcp-kalani/ghidra-11353.sock';ghidra={}
 for n,(a,z) in ENTRIES.items():
  raw=subprocess.check_output(['curl','-fsS','--max-time','20','--unix-socket',socket,f'http://localhost/read_memory?program=stock-r1-native-analysis.elf&address=0x{a:x}&length={z}']);assert bytes(json.loads(raw)['data'])==app.read_bytes()[a-0x27000:a-0x27000+z]
  p=OUT/('ghidra-'+n+'.json');p.write_bytes(raw);ghidra[p.name]=sha(p)
 body=json.loads((OUT/'rea-35760.json').read_text());assert body['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8';body=body['normalized_result']['body'];assert body['ranges']==[{'start':'0x35760','end':'0x35765'},{'start':'0x50558','end':'0x50571'},{'start':'0x50804','end':'0x50831'}] and body['total_bytes']==78
 row=next(r for r in csv.DictReader((ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv').open()) if r['image']=='application' and r['entry']=='0x00035760')
 (OUT/'evidence.json').write_text(json.dumps(dict(original_write_row=row,write_body=body,completion_shared_with_read=True,read_entry='manual_provenance_supplement at0x507cc',locked_ownership_changed=False,data_roots={'context':hex(C),'request':hex(Q)},registry_providers='Existing r1_stock_dispatch_08/0c/10/14; fixture boundaries in this receipt'),indent=2)+'\n')
 counts={n:0 for n in ENTRIES};rng=random.Random(0x507cc);executed={'native':{n:0 for n in P},'source':{n:0 for n in P}};provider_reports={}
 registry_report=ROOT/'r1/research/source-build/i2c5/report.json';registry_object=registry_report.parent/'stock_registry.o'
 if real_registry:
  rr=json.loads(registry_report.read_text());unit=next(u for u in rr['units'] if u['source']=='r1/components/registry/stock_registry.c');assert sha(registry_object)==unit['object_sha256'] and sha(ROOT/unit['source'])==unit['source_sha256'];provider_reports['i2c5/report.json']=sha(registry_report)
 with tempfile.TemporaryDirectory() as directory:
  d=Path(directory);ld=d/'layout.ld';elf=d/'test.elf';binary=d/'text.bin';bindings={n:0x1100001+16*i for i,n in enumerate(P)};ld.write_text('SECTIONS { .text 0x1000000 : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }')
  subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--defsym=r1_yhm_transport_context='+hex(C),'--defsym=r1_yhm_request='+hex(Q),*(['--gc-sections',*['--undefined='+n for n in ENTRIES]] if real_registry else []),*['--defsym='+n+'='+hex(a) for n,a in bindings.items() if not real_registry],str(obj),*([str(registry_object)] if real_registry else []),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary',str(elf),str(binary)],check=True)
  syms={v[2]:int(v[0],16) for l in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=l.split())==3};image=binary.read_bytes();assert len(image)<65536;machines=[];states={};kinds={a:n for n,a in P.items()};kinds.update({a&~1:n for n,a in bindings.items()})
  graph_kinds={0x1100080+16*i:n for i,n in enumerate(P)}
  if real_registry:
   kinds=graph_kinds
  def hook(u,a,size,_):
   if real_registry:
    for n,native in P.items():
     if a==(syms[n] if id(u)==id(machines[1]) else native):executed['source' if id(u)==id(machines[1]) else 'native'][n]+=1
   f=states[id(u)];r=[u.reg_read(reg) for reg in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)]
   if a in kinds:
    n=kinds[a];f['trace'].append((n,*r[:1],*(r[1:] if n.endswith(('10','14')) else []),bytes(u.mem_read(Q,20)).hex()))
    if n.endswith(('10','14')):
     assert r[1:]==[0,Q,0]
     if n.endswith('10') and f['write']:u.mem_write(0x20002010,bytes([f['byte']]))
    f['index']+=1;result=(f['result']+f['index'])&0xffffffff
    if f['mutation']:
     u.mem_write(C+4,struct.pack('<I',0x20012300+f['index']*16));u.mem_write(C,struct.pack('<I',0x1100061 if f['index']&1 else 0))
   elif a==0x1100060:f['trace'].append(('callback',r[0]));assert r[0]==0;result=f['result']
   else:
    if id(u)==id(machines[1]) and a<0x1000000 and a!=0x20000100:raise AssertionError(('unexpected native source execution',hex(a)))
    return
   u.reg_write(UC_ARM_REG_R0,result);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  for _ in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,65536);u.mem_write(0x1000000,image);u.mem_map(0x1100000,4096);u.mem_map(0x20000000,0x40000);machines.append(u);u.hook_add(UC_HOOK_CODE,hook)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  def case_one(name,reg=0,length=0,result=0,mutation=False,write=False,callback=False,mode='valid'):
   results=[];request=rng.randbytes(20);byte=rng.randrange(256)
   for candidate,u in enumerate(machines):
    states[id(u)]={'trace':[],'index':0,'result':result,'mutation':mutation,'write':write,'byte':byte};u.mem_write(C-4,b'\x96'*24);u.mem_write(C,struct.pack('<4I',0x1100061 if callback else 0,0x20012200,0xaabbccdd,0x20013300));u.mem_write(Q-4,b'\x69'*4+request+b'\x96'*4);u.mem_write(0x20002000,b'\xa5'*32)
    if real_registry:
     ops=0x20014000;slots=[0]*9
     for i,n in enumerate(P):slots[{'r1_stock_dispatch_08':2,'r1_stock_dispatch_0c':3,'r1_stock_dispatch_10':4,'r1_stock_dispatch_14':5}[n]]=0 if mode=='missing_slots' else 0x1100081+16*i
     u.mem_write(ops,struct.pack('<9I',*slots))
     for device in (0x20012200,0x20013300,0x20012310,0x20012320,0x20012330,0x20012340):u.mem_write(device+4,struct.pack('<I',ops))
     if mode=='null_bus':u.mem_write(C+4,b'\x00'*4)
     if mode=='null_aux':u.mem_write(C+12,b'\x00'*4)
    for r,v in [(UC_ARM_REG_R0,reg),(UC_ARM_REG_R1,length),(UC_ARM_REG_R2,0x20002010),(UC_ARM_REG_SP,0x2003f000),(UC_ARM_REG_LR,0x20000101)]:u.reg_write(r,v)
    for i,r in enumerate(saved):u.reg_write(r,0x12345600+i)
    u.emu_start((syms[name] if candidate else ENTRIES[name][0])|1,0x20000100,count=2000)
    assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(r) for r in saved]==[0x12345600+i for i in range(8)]
    results.append((u.reg_read(UC_ARM_REG_R0),states[id(u)]['trace'],bytes(u.mem_read(C-4,24)),bytes(u.mem_read(Q-4,28)),bytes(u.mem_read(0x20002000,32))))
   assert results[0]==results[1],(name,reg,length,result,mutation,callback,results);counts[name]+=1
  def case(*args,**kwargs):
   for mode in (('valid','null_bus','null_aux','missing_slots') if real_registry else ('valid',)):case_one(*args,**kwargs,mode=mode)
  for name in ('r1_yhm_register_read_record','r1_yhm_register_write_record','r1_yhm_register_write_native'):
   for reg,length,result,mutation,write,callback in itertools.product((0,6,255,256,0xffffffff),(0,1,255,256,257,0xffffffff),(0,1,0xfffffffc,0xffffffff),(False,True),(False,True),(False,True)):case(name,reg,length,result,mutation,write,callback)
  for name,result,mutation,callback in itertools.product(('r1_yhm_transport_acquire','r1_yhm_transport_release','r1_yhm_transport_complete'),(0,1,0x80000000,0xffffffff),(False,True),(False,True)):case(name,result=result,mutation=mutation,callback=callback)
 vp.write_text(json.dumps(dict(comparisons=sum(counts.values()),counts=counts,real_registry=real_registry,registry_provider_interception=not real_registry,executed_registry_entry_counts=executed,provider_reports=provider_reports,report_sha256=sha(rp),object_sha256=sha(obj),driver_sha256=sha(Path(__file__)),application_sha256=app_hash,ghidra_evidence=ghidra,rea_evidence={p.name:sha(p) for p in OUT.glob('rea-*.json')},body_evidence_sha256=sha(OUT/'evidence.json'),application_linked=False,instruction_identity=False,limitations=['Registry bodies execute in integration mode; lower bus operations are fixtures','Context/request roots are address bindings, not source-owned initialization','Raw result follows completion release/callback; not interpreted as bus success','Physical serialization/concurrency and device behavior unproven']),indent=2)+'\n');print('YHM transport:',counts)
if __name__=='__main__':main()
