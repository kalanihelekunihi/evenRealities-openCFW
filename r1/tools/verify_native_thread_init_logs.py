#!/usr/bin/env python3
"""Service/storage wrappers versus native across changing mode getter results."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-thread-init-logs';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ENTRIES={'r1_native_service_hardware_initialize':0x45c84,'r1_native_storage_hardware_initialize':0x45d00}
DESCRIPTORS={'service_ring':0x45cc4,'service_sdk':0x45ce8,'storage_ring':0x45d40,'storage_sdk':0x45d64}
P={'r1_structured_log_mode_get':0x914ec,'r1_structured_log_format':0x91638,'nrf_log_frontend_std_0':0x799c0}
def main():
 vp=OUT/'verification.json';vp.unlink(missing_ok=True);rp=OUT/'report.json';r=json.loads(rp.read_text());obj=OUT/'native_thread_init_logs.o';assert sha(obj)==r['units'][0]['object_sha256']
 for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';evidence={};socket='/var/folders/mh/nz9vzlpn7kzff18f77pztg880000gn/T/ghidra-mcp-kalani/ghidra-11353.sock'
 for name,a in ENTRIES.items():
  raw=subprocess.check_output(['curl','-fsS','--max-time','20','--unix-socket',socket,f'http://localhost/read_memory?program=stock-r1-native-analysis.elf&address=0x{a:x}&length=64']);assert bytes(json.loads(raw)['data'])==app.read_bytes()[a-0x27000:a-0x27000+64];p=OUT/('ghidra-'+name+'.json');p.write_bytes(raw);evidence[p.name]=sha(p)
 counts={n:0 for n in ENTRIES}
 with tempfile.TemporaryDirectory() as directory:
  d=Path(directory);ld=d/'layout.ld';elf=d/'test.elf';binary=d/'text.bin';bindings={n:0x1100001+i*16 for i,n in enumerate(P)};ld.write_text('SECTIONS { '+''.join('.r1.thread_init_log.'+n+' '+hex(a)+' : { *(.r1.thread_init_log.'+n+') } ' for n,a in DESCRIPTORS.items())+'.text 0x1000000 : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }');subprocess.run(['arm-none-eabi-ld','-T',str(ld),*['--defsym='+n+'='+hex(a) for n,a in bindings.items()],str(obj),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True);syms={v[2]:int(v[0],16) for l in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=l.split())==3};image=binary.read_bytes();assert len(image)<0x10000;states={};machines=[];kinds={a:n for n,a in P.items()};kinds.update({a&~1:n for n,a in bindings.items()})
  for _ in (0,1):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,0x10000);u.mem_write(0x1000000,image);u.mem_map(0x1100000,0x1000);u.mem_map(0x20000000,0x40000);machines.append(u)
  descriptor_data={}
  for name,address in DESCRIPTORS.items():
   data=d/(name+'.bin');copy=d/'copy.elf'
   subprocess.run(['arm-none-eabi-objcopy','--dump-section','.r1.thread_init_log.'+name+'='+str(data),str(elf),str(copy)],check=True)
   payload=data.read_bytes();assert payload==app.read_bytes()[address-0x27000:address-0x27000+len(payload)]
   descriptor_data[name]={'address':address,'bytes':len(payload),'sha256':hashlib.sha256(payload).hexdigest()};machines[1].mem_write(address,payload)
  def hook(u,a,size,_):
   if a not in kinds:return
   f=states[id(u)];n=kinds[a];r=[u.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2)];value=0
   if n=='r1_structured_log_mode_get':value=f['modes'][f['next']];f['next']+=1;event=(n,value)
   else:
    if n=='r1_structured_log_format':assert r[1]==r[2]
    event=(n,r[0],r[1],bytes(u.mem_read(r[1],64)).split(b'\0')[0].decode())
   f['trace'].append(event);u.reg_write(UC_ARM_REG_R0,value);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  for u in machines:u.hook_add(UC_HOOK_CODE,hook)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  values=(*range(8),0xffffffff,0x80000000,0xfffffffe,0xfffffffd,0xfffffffb)
  for name,modes in itertools.product(ENTRIES,itertools.product(values,repeat=3)):
   results=[]
   for candidate,u in enumerate(machines):
    states[id(u)]={'trace':[],'modes':modes,'next':0};u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    u.emu_start((syms[name]|1) if candidate else ENTRIES[name]|1,0x20000100,count=1000);assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
    results.append(states[id(u)]['trace'])
   assert results[0]==results[1],(name,modes,results);counts[name]+=1
 rea={n:sha(OUT/n) for n in ('rea-service.json','rea-storage.json')}
 vp.write_text(json.dumps(dict(comparisons=sum(counts.values()),counts=counts,report_sha256=sha(rp),object_sha256=sha(obj),driver_sha256=sha(Path(__file__)),application_sha256=sha(app),ghidra_evidence=evidence,rea_evidence=rea,entries=ENTRIES,source_descriptor_data=descriptor_data,application_linked=False,instruction_identity=False,limitations=['Lower logging providers are controlled fixtures','Void ABI; scratch return register not compared','Names are existing caller bindings; native wrappers emit logs only, not hardware initialization']),indent=2)+'\n');print('Thread initialization-log wrappers:',counts)
if __name__=='__main__':main()
