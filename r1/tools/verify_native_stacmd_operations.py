#!/usr/bin/env python3
"""Fixed-state STACMD operation contracts; lower wire/frame bodies remain fixtures."""
import argparse,csv,hashlib,itertools,json,random,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'r1/research/source-build/native-stacmd-operations';C=0x200075c4;F=C-4;Q=0x20002000;B=0x20003000
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ENTRIES={'r1_stacmd_close':(0x56568,14),'r1_stacmd_open':(0x5657c,16),'r1_stacmd_read':(0x56590,94),'r1_stacmd_write':(0x5660c,40)}
P={'r1_stacmd_bus_recovery_native':0x5cc8c,'r1_stacmd_read_frame_native':0x28bb0,'r1_stacmd_write_retry_native':0x35698}
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--real-retry',action='store_true');args=parser.parse_args();real_retry=args.real_retry
 vp=OUT/('retry-integration-verification.json' if real_retry else 'verification.json');vp.unlink(missing_ok=True);rp=OUT/'report.json';r=json.loads(rp.read_text());obj=OUT/'native_stacmd_operations.o'
 assert sha(obj)==r['units'][0]['object_sha256']
 for p,h in r['inputs'].items():assert sha(ROOT/p)==h
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';app_hash=sha(app);assert app_hash=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 socket='/var/folders/mh/nz9vzlpn7kzff18f77pztg880000gn/T/ghidra-mcp-kalani/ghidra-11353.sock';evidence={}
 for n,(a,z) in ENTRIES.items():
  raw=subprocess.check_output(['curl','-fsS','--max-time','20','--unix-socket',socket,f'http://localhost/read_memory?program=stock-r1-native-analysis.elf&address=0x{a:x}&length={z}']);assert bytes(json.loads(raw)['data'])==app.read_bytes()[a-0x27000:a-0x27000+z];p=OUT/('ghidra-'+n+'.json');p.write_bytes(raw);evidence[p.name]=sha(p)
 rows=[row for row in csv.DictReader((ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv').open()) if row['image']=='application' and int(row['entry'],16) in [a for a,z in ENTRIES.values()]]
 (OUT/'evidence.json').write_text(json.dumps(dict(ownership_rows=rows,rea_function_metadata_available=False,rea_limitation='REA procedure_info returned no structured function metadata for these four manual-provenance entries; native Ghidra-MCP bytes and locked manual rows are used',locked_ownership_changed=False,state={'configuration':hex(C),'failed_counter':hex(F)},abi='Read/write preserve registry four-word ABI with request in r2; open/close ignore passed device and use fixed state'),indent=2)+'\n')
 counts={n:0 for n in ENTRIES};rng=random.Random(0x56590);providers=dict(P);provider_reports={};extra_objects=[];retry_entries={'native':0,'source':0};frame_entries={'native':0,'source':0}
 if real_retry:
  retry_dir=OUT.parent/'native-stacmd-write-retry';report=retry_dir/'report.json';retry=json.loads(report.read_text());retry_object=retry_dir/'native_stacmd_write_retry.o';assert sha(retry_object)==retry['units'][0]['object_sha256'];extra_objects=[retry_object];provider_reports['native-stacmd-write-retry/report.json']=sha(report);providers.pop('r1_stacmd_write_retry_native');providers.update(r1_stacmd_write_frame_native=0x28c6c,r1_structured_log_mode_get=0x914ec,r1_structured_log_format=0x91638,nrf_log_frontend_std_1=0x799c8)
 with tempfile.TemporaryDirectory() as directory:
  d=Path(directory);ld=d/'layout.ld';elf=d/'test.elf';binary=d/'text.bin';bindings={n:0x1100001+i*16 for i,n in enumerate(providers)};ld.write_text('SECTIONS { .text 0x1000000 : { *(.text*) *(.rodata*) *(.r1.stacmd_retry.*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }')
  subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--defsym=r1_stacmd='+hex(C),'--defsym=r1_stacmd_failed_transactions='+hex(F),*['--defsym='+n+'='+hex(a) for n,a in bindings.items()],str(obj),*map(str,extra_objects),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary',str(elf),str(binary)],check=True)
  syms={v[2]:int(v[0],16) for l in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=l.split())==3};image=binary.read_bytes();assert len(image)<65536;machines=[];states={};kinds={a:n for n,a in providers.items()};kinds.update({a&~1:n for n,a in bindings.items()})
  def hook(u,a,size,_):
   side='source' if id(u)==id(machines[1]) else 'native'
   if real_retry and a==(syms['r1_stacmd_write_retry_native'] if side=='source' else 0x35698):retry_entries[side]+=1
   if a not in kinds:
    if id(u)==id(machines[1]) and a<0x1000000 and a!=0x20000100:raise AssertionError(('unexpected native source execution',hex(a)))
    return
   f=states[id(u)];n=kinds[a];r=[u.reg_read(reg) for reg in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)];result=0
   if n=='r1_structured_log_mode_get':u.reg_write(UC_ARM_REG_R0,0);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR));return
   if n in ('r1_structured_log_format','nrf_log_frontend_std_1'):raise AssertionError('unexpected log with mode0')
   if n=='r1_stacmd_write_frame_native':
    f['trace'].append(('write_frame',*r));assert r==[0x44,f['reg'],f['length'],B];result=f['raw_result'];frame_entries[side]+=1
   elif n.endswith('recovery_native'):f['trace'].append(('recovery',));f['attempt']+=1
   elif n.endswith('read_frame_native'):
    f['trace'].append(('read',*r));assert r==[0x44,f['reg'],f['length'],B];result=f['raw_result'] if f['attempt']==f['success'] else 0
    if f['length']:u.mem_write(B,bytes([f['attempt']]))
   else:f['trace'].append(('write',*r[:3]));assert r[:3]==[f['reg'],f['length'],B];result=f['raw_result']
   if f['mutation']:
    u.mem_write(C+4,b'\0');u.mem_write(Q,b'\xfe');u.mem_write(Q+8,b'\x00');u.mem_write(Q+16,b'\x00');u.mem_write(F,struct.pack('<I',0xffffffff))
   u.reg_write(UC_ARM_REG_R0,result);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  for _ in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,65536);u.mem_write(0x1000000,image);u.mem_map(0x1100000,4096);u.mem_map(0x20000000,0x40000);machines.append(u);u.hook_add(UC_HOOK_CODE,hook)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  def case(name,opened=0,null=False,length=0,reg=0,success=0,raw_result=1,mutation=False,counter=0):
   results=[];config=rng.randbytes(108);request=bytearray(rng.randbytes(20));request[0]=reg;request[8]=length;request[16]=length;struct.pack_into('<I',request,4,B);struct.pack_into('<I',request,12,B)
   for candidate,u in enumerate(machines):
    states[id(u)]={'trace':[],'attempt':0,'reg':reg,'length':length,'success':success,'raw_result':raw_result,'mutation':mutation};u.mem_write(F-4,b'\x96'*4+struct.pack('<I',counter)+config+b'\x69'*4);u.mem_write(C+4,bytes([opened]));u.mem_write(Q,bytes(request));u.mem_write(B-4,b'\xa5'*264)
    for r,v in [(UC_ARM_REG_R0,0),(UC_ARM_REG_R1,0xffffffff),(UC_ARM_REG_R2,0 if null else Q),(UC_ARM_REG_R3,0xdeadbeef),(UC_ARM_REG_SP,0x2003f000),(UC_ARM_REG_LR,0x20000101)]:u.reg_write(r,v)
    for i,r in enumerate(saved):u.reg_write(r,0x12345600+i)
    u.emu_start((syms[name] if candidate else ENTRIES[name][0])|1,0x20000100,count=10000)
    assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(r) for r in saved]==[0x12345600+i for i in range(8)]
    results.append((u.reg_read(UC_ARM_REG_R0),states[id(u)]['trace'],bytes(u.mem_read(F-4,120)),bytes(u.mem_read(Q,20)),bytes(u.mem_read(B-4,264))))
   assert results[0]==results[1],(name,opened,null,length,success,mutation,counter,results);counts[name]+=1
  for name,opened in itertools.product(('r1_stacmd_open','r1_stacmd_close'),range(256)):case(name,opened)
  for opened,null,length,success,raw_result,mutation,counter in itertools.product((0,1,255),(False,True),(0,1,3,255),(0,1,8,9,10),(1,0x80000000),(False,True),(0,0xffffffff)):case('r1_stacmd_read',opened,null,length,rng.randrange(256),success,raw_result,mutation,counter)
  for opened,null,length,raw_result,mutation in itertools.product((0,1,255),(False,True),(0,1,255),(0,1,0xffffffff),(False,True)):case('r1_stacmd_write',opened,null,length,rng.randrange(256),raw_result=raw_result,mutation=mutation)
 vp.write_text(json.dumps(dict(comparisons=sum(counts.values()),counts=counts,real_retry=real_retry,retry_provider_interception=not real_retry,provider_reports=provider_reports,executed_retry_entry_counts=retry_entries,executed_write_frame_counts=frame_entries,report_sha256=sha(rp),object_sha256=sha(obj),driver_sha256=sha(Path(__file__)),application_sha256=app_hash,ghidra_evidence=evidence,body_evidence_sha256=sha(OUT/'evidence.json'),application_linked=False,instruction_identity=False,limitations=['Retry executes in integration mode; recovery and frame/logger providers remain fixtures','REA function metadata unavailable for manual-provenance entries; native bytes and locked ownership rows authenticated','Bus recovery/read-frame/write-retry providers remain fixtures','Fixed configuration/counter are test bindings; registration ABI and state ownership integration remain open','Nonzero-length null output fault behavior is not claimed; no production null fallback added','Physical timing/concurrency and whole-image byte identity unproven']),indent=2)+'\n');print('STACMD operations:',counts)
if __name__=='__main__':main()
