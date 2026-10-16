#!/usr/bin/env python3
"""Native reset/flags/shared-client policy and command-byte adapters, with transport fixtures."""
import hashlib,itertools,json,struct,subprocess,tempfile,random,csv
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-battery-control';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();D=0x20016b84;M=0x20006878;T=0x20006638
ENTRIES={'r1_battery_charging_progress_reset':(0x4fe5c,14),'r1_battery_task_flags_set':(0x77240,10),'r1_shared_power_client_acquire':(0x50778,32),'r1_shared_power_client_release':(0x50758,28),'r1_yhm_shared_power_active':(0x355a8,20),'r1_yhm_shared_power_inactive':(0x35594,20)}
P={'osThreadFlagsSet':0x7d6f4,'r1_yhm_register_write_native':0x35760}
def main():
 vp=OUT/'verification.json';vp.unlink(missing_ok=True);rp=OUT/'report.json';r=json.loads(rp.read_text());obj=OUT/'native_battery_control.o';assert sha(obj)==r['units'][0]['object_sha256']
 for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';evidence={};socket='/var/folders/mh/nz9vzlpn7kzff18f77pztg880000gn/T/ghidra-mcp-kalani/ghidra-11353.sock'
 for n,(a,z) in ENTRIES.items():
  raw=subprocess.check_output(['curl','-fsS','--max-time','20','--unix-socket',socket,f'http://localhost/read_memory?program=stock-r1-native-analysis.elf&address=0x{a:x}&length={z}']);assert bytes(json.loads(raw)['data'])==app.read_bytes()[a-0x27000:a-0x27000+z];p=OUT/('ghidra-'+n+'.json');p.write_bytes(raw);evidence[p.name]=sha(p)
 rea=json.loads((OUT/'rea-release-body.json').read_text());body=rea['normalized_result']['body'];assert body['non_contiguous'] and body['total_bytes']==48 and body['ranges']==[{'start':'0x35594','end':'0x355a7'},{'start':'0x50758','end':'0x50773'}]
 row=next(r for r in csv.DictReader((ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv').open()) if r['image']=='application' and r['entry']=='0x00050758');(OUT/'evidence.json').write_text(json.dumps(dict(original_row=row,body_ranges=body['ranges'],total_body_bytes=48,release_entry_span_bytes=28,inactive_command_bytes=20,locked_ownership_changed=False,transport_scope='Original zero-context native register ABI; existing contextual YHM model is not assumed ABI-identical',data_roots={'device':hex(D),'mask':hex(M),'thread_handle':hex(T)}),indent=2)+'\n')
 counts={n:0 for n in ENTRIES};rng=random.Random(0x50778)
 with tempfile.TemporaryDirectory() as directory:
  d=Path(directory);ld=d/'layout.ld';elf=d/'test.elf';binary=d/'text.bin';bindings={n:0x1100001+i*16 for i,n in enumerate(P)};ld.write_text('SECTIONS { .text 0x1000000 : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }');subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--defsym=r1_battery_device_context='+hex(D),'--defsym=r1_battery_thread_handle='+hex(T),'--defsym=r1_shared_power_clients='+hex(M),*['--defsym='+n+'='+hex(a) for n,a in bindings.items()],str(obj),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary',str(elf),str(binary)],check=True);syms={v[2]:int(v[0],16) for l in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=l.split())==3};image=binary.read_bytes();assert len(image)<0x10000;machines=[];states={};kinds={a:n for n,a in P.items()};kinds.update({a&~1:n for n,a in bindings.items()})
  for _ in (0,1):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,0x10000);u.mem_write(0x1000000,image);u.mem_map(0x1100000,0x1000);u.mem_map(0x20000000,0x40000);machines.append(u)
  def hook(u,a,size,_):
   if a not in kinds:return
   f=states[id(u)];n=kinds[a];r=[u.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2)];value=f['result']
   if n=='osThreadFlagsSet':event=(n,*r[:2]);u.mem_write(T,struct.pack('<I',0x20019900))
   else:
    assert r[0:2]==[2,1];command=bytes(u.mem_read(r[2],1));assert command in (b'\xa8',b'\x28');event=(n,r[0],r[1],command.hex(),struct.unpack('<I',bytes(u.mem_read(M,4)))[0])
    if f['mutation'] is not None:u.mem_write(M,struct.pack('<I',f['mutation']))
   f['trace'].append(event);u.reg_write(UC_ARM_REG_R0,value);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  for u in machines:u.hook_add(UC_HOOK_CODE,hook)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  returning={'r1_battery_task_flags_set','r1_yhm_shared_power_active','r1_yhm_shared_power_inactive'}
  def case(name,arg=0,mask=0,result=0,mutation=None,handle=0,device=None):
   results=[];device=device if device is not None else bytes([0x93])*68
   for candidate,u in enumerate(machines):
    states[id(u)]={'trace':[],'result':result,'mutation':mutation};u.mem_write(D-8,b'\x96'*8+device+b'\x69'*8);u.mem_write(M-4,struct.pack('<3I',0xaabbccdd,mask,0x11223344));u.mem_write(T-4,struct.pack('<3I',0x12345678,handle,0x89abcdef));u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101);u.reg_write(UC_ARM_REG_R0,arg)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    u.emu_start((syms[name]|1) if candidate else ENTRIES[name][0]|1,0x20000100,count=10000);assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
    results.append((u.reg_read(UC_ARM_REG_R0) if name in returning else None,states[id(u)]['trace'],bytes(u.mem_read(D-8,84)),bytes(u.mem_read(M-4,12)),bytes(u.mem_read(T-4,12))))
   assert results[0]==results[1],(name,arg,mask,result,mutation,handle,results);counts[name]+=1
  masks=(*range(16),0x80000000,0x80000007,0x7fffffff,0xffffffff)
  for name,client,mask,result,mutation in itertools.product(('r1_shared_power_client_acquire','r1_shared_power_client_release'),(0,1,2,3,31,32,0xffffffff),masks,(0,1,0xffffffff),(None,0,0x80,0xffffffff)):case(name,client,mask,result,mutation)
  for name,result,mutation in itertools.product(('r1_yhm_shared_power_active','r1_yhm_shared_power_inactive'),(0,1,0xffffffff),(None,0,0x80,0xffffffff)):case(name,result=result,mutation=mutation)
  for handle,flags,result in itertools.product((0,1,0x20014418,0xffffffff),(0,1,8,16,0x80000000,0xffffffff),(0,1,0x80000004,0xffffffff)):case('r1_battery_task_flags_set',flags,result=result,handle=handle)
  for _ in range(1024):case('r1_battery_charging_progress_reset',device=rng.randbytes(68))
 vp.write_text(json.dumps(dict(comparisons=sum(counts.values()),counts=counts,report_sha256=sha(rp),object_sha256=sha(obj),driver_sha256=sha(Path(__file__)),application_sha256=sha(app),ghidra_evidence=evidence,rea_evidence={p.name:sha(p) for p in OUT.glob('rea-*.json')},body_evidence_sha256=sha(OUT/'evidence.json'),entries=ENTRIES,application_linked=False,instruction_identity=False,limitations=['Native register transport and CMSIS flag setter are fixtures','Void reset/client functions do not claim scratch returns; flag/command wrappers preserve raw returned status','Existing contextual YHM source API requires an authenticated context/ABI bridge; none is invented','Device context, client-mask and thread-handle initialization remain gated']),indent=2)+'\n');print('Battery control:',counts)
if __name__=='__main__':main()
