#!/usr/bin/env python3
"""Actual registration/reset order, raw initializer return and mutable log callbacks."""
import csv,hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-protocol-port';S=0x20006c20;R=S+4;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
DESCRIPTORS=[('init_ring',0x83108,48),('init_sdk',0x83140,42),('null_ring',0x8335c,57),('null_sdk',0x83398,51),('registered_ring',0x833cc,64),('registered_sdk',0x8340c,58)]
P={'r1_structured_log_mode_get':0x914ec,'r1_structured_log_format':0x91638,'nrf_log_frontend_std_0':0x799c0}
def main():
 vp=OUT/'verification.json';vp.unlink(missing_ok=True);objects=[];reports={}
 for module,filename in [('native-protocol-port','native_protocol_port.o'),('native-protocol-send-registration','native_protocol_send_registration.o'),('native-protocol-send-hook','native_protocol_send_hook.o')]:
  p=BASE/module/'report.json';j=json.loads(p.read_text());u=j['units'][0];obj=p.parent/filename;assert sha(obj)==u['object_sha256'] and sha(ROOT/u['source'])==u['source_sha256'];objects.append(obj);reports[module+'/report.json']=sha(p)
  for path,digest in j['inputs'].items():assert sha(ROOT/path)==digest,path
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';ah=sha(app);assert ah=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';ledger=ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv';rows=[r for r in csv.DictReader(ledger.open()) if r['image']=='application' and int(r['entry'],16) in (0x830a8,0x832d4)];assert [int(r['size']) for r in rows]==[84,124];evidence={}
 for address in (0x830a8,0x832d4):
  p=OUT/('rea-'+format(address,'x')+'.json');p.write_bytes((BASE/'native-battery-runtime'/('rea-next-'+format(address,'x')+'-body.json')).read_bytes());j=json.loads(p.read_text());assert j['error']['code']=='invalid_request';evidence[p.name]=sha(p)
 for label,address,length in [('init-body-data',0x830a8,196),('receive-body-data',0x832d4,372)]:
  raw=subprocess.check_output(['curl','-fsS','--max-time','20','--unix-socket','/var/folders/mh/nz9vzlpn7kzff18f77pztg880000gn/T/ghidra-mcp-kalani/ghidra-11353.sock','http://localhost/read_memory?program=stock-r1-native-analysis.elf&address='+hex(address)+'&length='+str(length)]);assert bytes(json.loads(raw)['data'])==app.read_bytes()[address-0x27000:address-0x27000+length];p=OUT/('ghidra-'+label+'.json');p.write_bytes(raw);evidence[p.name]=sha(p)
 cold=[]
 for poison in (165,90,255,60):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x20000000,0x40000);u.mem_write(0x20000000,bytes([poison])*0x40000);writes=[]
  def wh(u,access,a,n,v,_):
   if a<R+4 and a+n>R:writes.append({'pc':u.reg_read(UC_ARM_REG_PC),'address':a,'bytes':n,'value':v})
  u.hook_add(UC_HOOK_MEM_WRITE,wh);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.emu_start(0x283a1,0x27208,count=2000000);assert u.reg_read(UC_ARM_REG_PC)==0x27208 and bytes(u.mem_read(R,4))==b'\0'*4 and writes;cold.append({'poison':poison,'writes':writes})
 modes=[(0,),(1,),(2,),(3,),(4,),(5,),(6,),(7,),(0,4,2),(0,0,2),(1,2),(4,0,0),(0xffffffff,)]
 machines=[];states={};counts={name:0 for name in P};comparisons=0;entry_counts={'receive':0,'init':0};sections={}
 with tempfile.TemporaryDirectory() as temporary:
  d=Path(temporary);ld=d/'layout.ld';elf=d/'test.elf';binary=d/'text.bin';bindings={name:0x1100001+16*i for i,name in enumerate(P)};ld.write_text('SECTIONS { .send 0x20006c20 : { *(.r1.protocol.send_hook) } .receive 0x20006c24 : { *(.r1.protocol.receive_hook) } '+''.join('.'+name+' '+hex(address)+' : { *(.r1.protocol_port.'+name+') } ' for name,address,size in DESCRIPTORS)+'.text 0x1000000 : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }');subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--defsym=r1_fragment_message=0x32409','--defsym=r1_eus_ingress_plan_decode=0x8316d',*['--defsym='+name+'='+hex(address) for name,address in bindings.items()],*map(str,objects),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-j','.text','-O','binary',str(elf),str(binary)],check=True);syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
  for name,address,size in DESCRIPTORS:
   p=d/(name+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j','.'+name,'-O','binary',str(elf),str(p)],check=True);assert p.read_bytes()==app.read_bytes()[address-0x27000:address-0x27000+size];sections[name]={'address':address,'bytes':size,'sha256':sha(p)}
  p=d/'receive.bin';subprocess.run(['arm-none-eabi-objcopy','-j','.receive','-O','binary',str(elf),str(p)],check=True);assert p.read_bytes()==b'\0'*4;receive_section={'address':R,'bytes':4,'sha256':sha(p)}
  kinds={address:name for name,address in P.items()};kinds.update({address&~1:name for name,address in bindings.items()})
  def writehook(u,access,address,size,value,_):
   if address<R+4 and address+size>S:states[id(u)]['writes'].append((address,size,value))
  def hook(u,address,size,_):
   f=states[id(u)];name=kinds[address];r=[u.reg_read(reg) for reg in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)];value=f['raw'];event=(name,);f['counts'][name]+=1
   if name=='r1_structured_log_mode_get':value=f['mode'][f['mode_index']%len(f['mode'])];f['mode_index']+=1;event+=(value,)
   elif name=='r1_structured_log_format':
    assert r[1]==r[2] and (r[0],r[1]) in [(0x0c000000,0x83108),(0x04000000,0x8335c),(0x0c000000,0x833cc)];event+=tuple(r[:3])
   else:assert (r[0],r[1]) in [(0x001c0003,0x83140),(0x001c0001,0x83398),(0x001c0003,0x8340c)];event+=tuple(r[:2])
   f['trace'].append(event);f['last']=(name,value)
   if f['mutation']:
    counter=len(f['trace']);u.mem_write(S,struct.pack('<II',0xabcd0000+counter,0xface0000+counter))
   for reg,v in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),(value,0x11111111,0x22222222,0x33333333)):u.reg_write(reg,v)
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  for _ in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,65536);u.mem_write(0x1000000,binary.read_bytes());u.mem_map(0x1100000,4096);u.mem_map(0x20000000,0x40000);machines.append(u)
   for address in kinds:u.hook_add(UC_HOOK_CODE,hook,begin=address,end=address)
   u.hook_add(UC_HOOK_MEM_WRITE,writehook,begin=S,end=R+3)
   if len(machines)==2:
    def reject(u,address,size,_):raise AssertionError(('source executed native',hex(address)))
    u.hook_add(UC_HOOK_CODE,reject,begin=0x20000,end=0xe0000)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  extra=(0,1,65535,65536,0x80000000,0xffffffff,0x8316d,0x20000201)
  cases=itertools.chain((('receive',callback,(0,),False,0) for callback in range(65536)),(('receive',callback,mode,mutation,raw) for callback,mode,mutation,raw in itertools.product(extra,modes,(False,True),(0,7,0xffffffff))),(('init',seed,mode,mutation,raw) for seed,mode,mutation,raw in itertools.product((0,1,0xffffffff,0x8316d),modes,(False,True),(0,7,0xffffffff))))
  for index,(entry,callback,mode,mutation,raw) in enumerate(cases):
   results=[]
   for candidate,u in enumerate(machines):
    u.mem_write(S-4,b'\x96'*16);u.mem_write(S,struct.pack('<II',(index*997)&0xffffffff,index^0xdeadbeef));u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101);u.reg_write(UC_ARM_REG_R0,callback);states[id(u)]={'mode':mode,'mode_index':0,'mutation':mutation,'raw':raw,'last':None,'trace':[],'writes':[],'counts':dict.fromkeys(P,0)}
    for k,reg in enumerate(saved):u.reg_write(reg,0x12345600+k)
    address=(syms['r1_proto_port_init' if entry=='init' else 'r1_proto_register_ble_recv_callback'] if candidate else 0x830a8 if entry=='init' else 0x832d4);u.emu_start(address|1,0x20000100,count=1000);assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+k for k in range(8)];f=states[id(u)];expected=(raw if f['last'][0]=='nrf_log_frontend_std_0' else (f['last'][1]<<30)&0xffffffff) if entry=='init' else 0 if callback else 0xffffffff;assert u.reg_read(UC_ARM_REG_R0)==expected,(entry,callback,mode,mutation,raw,candidate,u.reg_read(UC_ARM_REG_R0),expected)
    expected_writes=[(S,4,0),(R,4,0),(S,4,0x32409),(R,4,0x8316d)] if entry=='init' else [(R,4,callback)] if callback else [];assert f['writes']==expected_writes,(entry,candidate,f['writes'],expected_writes);results.append((expected,f['trace'],f['writes'],f['counts'],bytes(u.mem_read(S-4,16))))
   assert results[0]==results[1],(index,entry,callback,mode,mutation,raw);comparisons+=1;entry_counts[entry]+=1
   for name,count in results[0][3].items():counts[name]+=count
 vp.write_text(json.dumps(dict(comparisons=comparisons,counts=entry_counts,provider_calls_per_side=counts,all_callback_halfwords=True,mode_sequences=len(modes),actual_send_and_receive_registration=True,reset_and_registration_store_order=True,raw_initializer_r0_checked=True,live_callback_mutation=True,source_descriptor_sections=sections,source_owned_receive_section=receive_section,cold_runs=cold,rea_boundary_available=False,ownership_rows=rows,ownership_sha256=sha(ledger),provider_reports=reports,evidence=evidence,driver_sha256=sha(Path(__file__)),application_sha256=ah,application_linked=False,instruction_identity=False,limitations=['REA has neither entry; locked ownership, native calls/literal targets and exact Ghidra-MCP bytes are attribution evidence','Ingress body is an opaque symbolic target binding and is not executed; complete product initialization remains gated','Raw returnr0/callee-saved ABI and ordered stores checked; volatile r1/r2/r3, enabled real logger composition, warm state and interrupt/concurrency remain gated']),indent=2)+'\n');print('Protocol port:',comparisons,entry_counts,counts)
if __name__=='__main__':main()
