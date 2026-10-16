#!/usr/bin/env python3
"""Native lazy handle discovery, reentry and callback-mutation comparison."""
import argparse,hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'r1/research/source-build/native-yhm-initialize';C=0x2000687c
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
P={'r1_stock_registry_find':0x85ce0,'r1_stock_dispatch_08':0x85d1a,'r1_stock_dispatch_18':0x85ccc}
NAMES=['device_stacmd','ship_mode_en','device_stacmd_irq','vpmic_isns_adc']
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--real-registry',action='store_true');args=parser.parse_args();real_registry=args.real_registry
 vp=OUT/('registry-integration-verification.json' if real_registry else 'verification.json');vp.unlink(missing_ok=True);rp=OUT/'report.json';r=json.loads(rp.read_text());obj=OUT/'native_yhm_initialize.o'
 assert sha(obj)==r['units'][0]['object_sha256']
 for p,h in r['inputs'].items():assert sha(ROOT/p)==h
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';app_hash=sha(app);assert app_hash=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 socket='/var/folders/mh/nz9vzlpn7kzff18f77pztg880000gn/T/ghidra-mcp-kalani/ghidra-11353.sock'
 raw=subprocess.check_output(['curl','-fsS','--max-time','20','--unix-socket',socket,'http://localhost/read_memory?program=stock-r1-native-analysis.elf&address=0x50578&length=144']);assert bytes(json.loads(raw)['data'])==app.read_bytes()[0x50578-0x27000:0x50608-0x27000];(OUT/'ghidra-memory.json').write_bytes(raw)
 rea=json.loads((OUT/'rea-body.json').read_text());assert rea['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and rea['normalized_result']['body']['total_bytes']==70
 comparisons=0;workflows=0;executed={side:{n:0 for n in (*P,'strcmp')} for side in ('native','source')};provider_reports={};extra_objects=[]
 if real_registry:
  for module,source,objname in [('i2c5','r1/components/registry/stock_registry.c','stock_registry.o'),('runtime','third-party/upstream/musl-memory-1.2.5/strcmp.c','strcmp.o')]:
   report=OUT.parent/module/'report.json';unit=next(u for u in json.loads(report.read_text())['units'] if u['source']==source);o=report.parent/objname;assert sha(o)==unit['object_sha256'] and sha(ROOT/source)==unit['source_sha256'];extra_objects.append(o);provider_reports[module+'/report.json']=sha(report)
 with tempfile.TemporaryDirectory() as directory:
  d=Path(directory);ld=d/'layout.ld';elf=d/'test.elf';binary=d/'text.bin';bindings={n:0x1100001+16*i for i,n in enumerate(P)};ld.write_text('SECTIONS { .text 0x1000000 : { *(.text*) *(.rodata*) } .r1.registry.head 0x20007680 : { *(.r1.registry.head) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }')
  subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--defsym=r1_yhm_transport_context='+hex(C),*(['--gc-sections','--undefined=r1_yhm_device_handles_initialize'] if real_registry else []),*['--defsym='+n+'='+hex(a) for n,a in bindings.items() if not real_registry],str(obj),*map(str,extra_objects),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-j','.text','-O','binary',str(elf),str(binary)],check=True)
  syms={v[2]:int(v[0],16) for l in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=l.split())==3};image=binary.read_bytes();assert len(image)<65536;machines=[];states={};kinds={a:n for n,a in P.items()};kinds.update({a&~1:n for n,a in bindings.items()})
  if real_registry:kinds={0x1100080:'r1_stock_dispatch_08',0x1100090:'r1_stock_dispatch_18'}
  def hook(u,a,size,_):
   if real_registry:
    for n,native in {**P,'strcmp':0x277fe}.items():
     if a==(syms[n] if id(u)==id(machines[1]) else native):executed['source' if id(u)==id(machines[1]) else 'native'][n]+=1
   if a not in kinds:
    if id(u)==id(machines[1]) and a<0x1000000 and a!=0x20000100:raise AssertionError(('unexpected native source execution',hex(a)))
    return
   f=states[id(u)];n=kinds[a];r=[u.reg_read(reg) for reg in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2)]
   if n=='r1_stock_registry_find':
    name=bytes(u.mem_read(r[0],32)).split(b'\0',1)[0].decode();index=NAMES.index(name);f['trace'].append(('find',name));value=0 if f['missing']&(1<<index) else 0x20015000+index*32
    if f['mutation']:u.mem_write(C+16,struct.pack('<I',0x20016660))
   else:
    f['trace'].append((n,*r[:1],*(r[1:] if n.endswith('18') else [])));value=0xffffffff
    if n.endswith('18'):assert r[1:]==[0,0]
    if f['mutation'] and n.endswith('08'):u.mem_write(C+8,struct.pack('<I',0x20015550));u.mem_write(C+12,b'\0'*4)
   u.reg_write(UC_ARM_REG_R0,value);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  for _ in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,65536);u.mem_write(0x1000000,image);u.mem_map(0x1100000,4096);u.mem_map(0x20000000,0x40000);machines.append(u);u.hook_add(UC_HOOK_CODE,hook)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  for present,missing,mutation,missing_ops in itertools.product(range(16),range(16),(False,True),((False,True) if real_registry else (False,))):
   workflows+=1
   for u in machines:
    states[id(u)]={'trace':[],'missing':missing,'mutation':mutation};u.mem_write(C-4,b'\x96'*28);u.mem_write(C,struct.pack('<5I',0x1100061,*[0x20014000+i*32 if present&(1<<i) else 0 for i in range(4)]))
    if real_registry:
     ops=0x20017000;slots=[0]*9;slots[2]=0 if missing_ops else 0x1100081;slots[6]=0 if missing_ops else 0x1100091;u.mem_write(ops,struct.pack('<9I',*slots))
     records=[0x20015000+i*32 for i in range(4) if not missing&(1<<i)]
     for i,name in enumerate(NAMES):
      text=0x20018000+i*64;u.mem_write(text,name.encode()+b'\0')
      record=0x20015000+i*32;next_record=records[records.index(record)+1] if record in records and records.index(record)+1<len(records) else 0
      u.mem_write(record,struct.pack('<6I',text,ops,0,0,0,next_record))
     for record in [0x20014000+i*32 for i in range(4)]+[0x20015550]:u.mem_write(record+4,struct.pack('<I',ops))
     u.mem_write(0x20007680,struct.pack('<I',records[0] if records else 0))
   for repeat in range(3):
    results=[]
    for candidate,u in enumerate(machines):
     states[id(u)]['trace']=[];u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
     for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
     u.emu_start((syms['r1_yhm_device_handles_initialize'] if candidate else 0x50578)|1,0x20000100,count=10000)
     assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
     results.append((states[id(u)]['trace'],bytes(u.mem_read(C-4,28))))
    assert results[0]==results[1],(present,missing,mutation,repeat,results);comparisons+=1
 vp.write_text(json.dumps(dict(comparisons=comparisons,workflows=workflows,real_registry=real_registry,registry_provider_interception=not real_registry,executed_registry_entry_counts=executed,provider_reports=provider_reports,calls_per_workflow=3,report_sha256=sha(rp),object_sha256=sha(obj),driver_sha256=sha(Path(__file__)),application_sha256=app_hash,ghidra_memory_sha256=sha(OUT/'ghidra-memory.json'),rea_sha256=sha(OUT/'rea-body.json'),application_linked=False,instruction_identity=False,limitations=['Registry lookup/dispatch and pinned musl strcmp execute in integration mode; lower operation callbacks remain fixtures','Transport context is a test binding; zero initialization and callback ownership remain gated','Void initializer scratch return is not claimed; lookup/configuration success is not assumed']),indent=2)+'\n');print('YHM initialization:',comparisons,'comparisons;',workflows,'three-call workflows')
if __name__=='__main__':main()
