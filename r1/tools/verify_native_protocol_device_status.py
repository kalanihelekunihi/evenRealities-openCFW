#!/usr/bin/env python3
"""Actual shared byte getter/new charge predicates with live status payload and ABI."""
import csv,hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_INVALID
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-protocol-device-status';I=0x20010000;SP=0x2003f000;CELL=0x20016bb0;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
P={'r1_advertising_configuration_byte_get':0x7ba24,'r1_native_charger_state_get':0x50618,'r1_battery_runtime_update_service':0x31fd0,'r1_phone_cmd_send_op1':0x83896}
def main():
 vp=OUT/'verification.json';vp.unlink(missing_ok=True);reports={};objects=[]
 for module,filename in [('native-protocol-device-status','native_protocol_device_status.o'),('native-status-record','native_status_record.o')]:
  path=BASE/module/'report.json';j=json.loads(path.read_text());unit=j['units'][0];obj=path.parent/filename;assert sha(obj)==unit['object_sha256'] and sha(ROOT/unit['source'])==unit['source_sha256'];objects.append(obj);reports[module+'/report.json']=sha(path)
  for p,h in j['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';ah=sha(app);assert ah=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';ledger=ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv';rows=[row for row in csv.DictReader(ledger.open()) if row['image']=='application' and row['entry'] in ('0x00083de4','0x00091244','0x00091256')];assert len(rows)==3;evidence={}
 for address,size in [(0x83de4,66),(0x91244,18),(0x91256,14)]:
  p=OUT/('rea-'+format(address,'x')+'.json');p.write_bytes((BASE/'native-battery-runtime'/('rea-next-'+format(address,'x')+'-body.json')).read_bytes());j=json.loads(p.read_text());assert j['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and j['normalized_result']['body']['total_bytes']==size;evidence[p.name]=sha(p)
  raw=subprocess.check_output(['curl','-fsS','--max-time','20','--unix-socket','/var/folders/mh/nz9vzlpn7kzff18f77pztg880000gn/T/ghidra-mcp-kalani/ghidra-11353.sock','http://localhost/read_memory?program=stock-r1-native-analysis.elf&address='+hex(address)+'&length='+str(size)]);assert bytes(json.loads(raw)['data'])==app.read_bytes()[address-0x27000:address-0x27000+size];p=OUT/('ghidra-'+format(address,'x')+'.json');p.write_bytes(raw);evidence[p.name]=sha(p)
 machines=[];states={};counts={'full':0,'active':0,'status':0};providers=dict.fromkeys(P,0);predicate_entries={side:{'full':0,'active':0,'byte':0} for side in ('native','source')};status_null_faults=0;trace_hash=hashlib.sha256()
 with tempfile.TemporaryDirectory() as temporary:
  d=Path(temporary);ld=d/'layout.ld';elf=d/'test.elf';binary=d/'text.bin';bindings={name:0x1100001+16*i for i,name in enumerate(P)};ld.write_text('SECTIONS { .default_record 0x9a4c4 : { *(.r1.protocol_status.default_record) } .text 0x1000000 : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }');roots=['r1_device_status_handler','r1_charge_state_is_full','r1_charge_state_is_active'];subprocess.run(['arm-none-eabi-ld','--gc-sections',*['--undefined='+name for name in roots],'-T',str(ld),'--defsym=r1_device_state_byte_2c='+hex(CELL),*['--defsym='+name+'='+hex(a) for name,a in bindings.items()],*map(str,objects),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-j','.text','-O','binary',str(elf),str(binary)],check=True);syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
  p=d/'default.bin';subprocess.run(['arm-none-eabi-objcopy','-j','.default_record','-O','binary',str(elf),str(p)],check=True);default=p.read_bytes();assert default==app.read_bytes()[0x9a4c4-0x27000:0x9a4cc-0x27000]==bytes.fromhex('0002010000000000');default_section={'address':0x9a4c4,'bytes':8,'sha256':sha(p)}
  kinds={a:name for name,a in P.items()};kinds.update({a&~1:name for name,a in bindings.items()})
  def invalid(u,access,address,size,value,_):states[id(u)]['fault']=(access,address,size);return False
  def entries(u,address,size,_):
   side='native' if u is machines[0] else 'source'
   for name,native,symbol in [('full',0x91244,'r1_charge_state_is_full'),('active',0x91256,'r1_charge_state_is_active'),('byte',0x91270,'r1_charge_state_byte_get')]:
    if address in (native,syms[symbol]):predicate_entries[side][name]+=1
  def hook(u,address,size,_):
   f=states[id(u)];name=kinds[address];f['counts'][name]+=1;regs=[u.reg_read(reg) for reg in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)];value=0;event=(name,);out3=0x33330000
   if name=='r1_advertising_configuration_byte_get':
    value=f['configuration']
    if f['mutation']==1:u.mem_write(CELL,bytes([f['charge']^255]));u.mem_write(f['packet']+3,b'\x11\x11')
   elif name=='r1_battery_runtime_update_service':
    u.mem_write(CELL,bytes([f['updated']]));value=0x80000007
    if f['mutation']==1:u.mem_write(f['packet']+3,b'\x22\x22')
   elif name=='r1_native_charger_state_get':
    index=f['charger_calls'];assert index<len(f['charger_states']);value=f['charger_states'][index];out3|=index;f['charger_calls']+=1
    if f['kind']=='status' and index==0:f['latched_charge']=bytes(u.mem_read(CELL,1))[0] or 1
    if f['kind']=='status' and f['mutation']==index+2:u.mem_write(CELL,bytes([f['charge']^255]));u.mem_write(f['packet']+3,struct.pack('<H',0x3333 if index==0 else 0x4444))
   else:
    sequence=struct.unpack('<H',bytes(u.mem_read(f['packet']+3,2)))[0];assert regs==[SP-24,0,sequence,0x33330001],(f,regs,sequence);payload=bytes(u.mem_read(regs[0],8));expected=struct.pack('<II',f['latched_charge']|((3 if f['charger_states'][1]==2 else 1 if f['charger_states'][0]==1 else 2)<<8)|0x10000,0);assert payload==expected,(f,payload.hex(),expected.hex());event+=(sequence,payload.hex());value=f['raw'];out3=0x33333333;f['payload']=payload
    if f['mutation']==4:u.mem_write(regs[0],bytes(byte^0xa5 for byte in payload))
   f['trace'].append(event)
   for reg,v in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),(value,0x11111111,0x22222222,out3)):u.reg_write(reg,v)
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  for _ in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,65536);u.mem_write(0x1000000,binary.read_bytes());u.mem_map(0x1100000,4096);u.mem_map(0x20000000,0x40000);u.mem_write(0x9a4c4,default);machines.append(u);u.hook_add(UC_HOOK_MEM_INVALID,invalid)
   for a in kinds:u.hook_add(UC_HOOK_CODE,hook,begin=a,end=a)
   for native,symbol in [(0x91244,'r1_charge_state_is_full'),(0x91256,'r1_charge_state_is_active'),(0x91270,'r1_charge_state_byte_get')]:
    for a in (native,syms[symbol]):u.hook_add(UC_HOOK_CODE,entries,begin=a,end=a)
   if len(machines)==2:
    def reject(u,address,size,_):
     if address not in P.values():raise AssertionError(('source executed native',hex(address)))
    u.hook_add(UC_HOOK_CODE,reject,begin=0x20000,end=0xe0000)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  raw_values=itertools.chain(range(65536),(0x10000,0x10001,0x10002,0x80000000,0xffffffff));raw_values=list(raw_values)
  predicates=((kind,I,0,0,[value],0,0,0) for kind,value in itertools.product(('full','active'),raw_values))
  status=(('status',I,charge,config,[active,full],mutation,raw,0) for charge,config,active,full,mutation,raw in itertools.product(range(256),(0,85,0x10055),(0,1,2,0xffffffff),(0,1,2,0xffffffff),range(5),(0,7,0xffffffff)))
  sequences=(('status',I,sequence&255,0,[sequence%3,(sequence//3)%3],0,0x80000007,sequence) for sequence in range(65536))
  aliases=(('status',packet,charge,0,[active,full],0,raw,65535) for packet,charge,active,full,raw in itertools.product((SP-24,SP-23,SP-21,SP-20,SP-16,SP-8,SP-4),(0,255),(0,1,2),(0,1,2),(0,0xffffffff)))
  nulls=[('status',0,1,0,[1,2],0,0,0)]
  for index,(kind,packet,charge,configuration,charger_states,mutation,raw,sequence) in enumerate(itertools.chain(predicates,status,sequences,aliases,nulls)):
   results=[]
   for candidate,u in enumerate(machines):
    u.mem_write(I,b'\x5a'*32);u.mem_write(I+3,struct.pack('<H',sequence));u.mem_write(SP-160,b'\x96'*192);u.mem_write(SP-24,struct.pack('<6I',0x22220000|(index&65535),0x33330000|(index&65535),0x12345600,0x12345601,0x12345602,0x20000101));u.mem_write(CELL,bytes([charge]));u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,0x20000101);states[id(u)]={'kind':kind,'packet':packet,'charge':charge,'updated':(charge+37)&255,'configuration':configuration,'charger_states':charger_states,'charger_calls':0,'mutation':mutation,'raw':raw,'trace':[],'fault':None,'counts':dict.fromkeys(P,0),'payload':None}
    for reg,value in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),(index,packet,0x22220000|(index&65535),0x33330000|(index&65535))):u.reg_write(reg,value)
    for k,reg in enumerate(saved):u.reg_write(reg,0x12345600+k)
    symbol={'status':'r1_device_status_handler','full':'r1_charge_state_is_full','active':'r1_charge_state_is_active'}[kind];entry=syms[symbol] if candidate else {'status':0x83de4,'full':0x91244,'active':0x91256}[kind]
    try:u.emu_start(entry|1,0x20000100,count=1000)
    except UcError:assert not packet and states[id(u)]['fault']==(19,3,2)
    f=states[id(u)]
    if f['fault']:results.append(('fault',f['fault'],f['trace'],f['counts']));continue
    assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==SP and [u.reg_read(reg) for reg in saved]==[0x12345600+k for k in range(8)];regs=[u.reg_read(reg) for reg in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)];assert f['charger_calls']==(2 if kind=='status' else 1)
    if kind=='status':
     payload=bytes(byte^0xa5 for byte in f['payload']) if mutation==4 else f['payload'];expected=[raw,0x11111111,*struct.unpack('<2I',payload)]
    else:expected=[int(charger_states[0]==(2 if kind=='full' else 1)),0x11111111,0x22222222,0x33330000]
    assert regs==expected,(index,kind,candidate,regs,expected);results.append((regs,f['trace'],f['counts'],bytes(u.mem_read(I,32)),bytes(u.mem_read(CELL,1)),bytes(u.mem_read(SP-24,24)) if kind=='status' else None))
   assert results[0]==results[1],(index,kind,packet,charge,configuration,charger_states,mutation,raw,sequence,results);counts[kind]+=1
   if results[0][0]=='fault':status_null_faults+=1
   for name,count in results[0][3 if results[0][0]=='fault' else 2].items():providers[name]+=count
   trace_hash.update(json.dumps((kind,packet,charge,configuration,charger_states,mutation,raw,sequence,results[0]),default=lambda value:value.hex()).encode())
 vp.write_text(json.dumps(dict(comparisons=sum(counts.values()),counts=counts,provider_calls_per_side=providers,predicate_entries=predicate_entries,all_predicate_state_halfwords=True,all_status_sequence_halfwords=True,all_status_charge_bytes=True,live_distinct_charger_calls=True,live_header_and_cell_mutation=True,full_r0_r1_r2_r3=True,native_status_frame24=True,record_mutation_and_header_aliases=True,null_header_faults=status_null_faults,actual_shared_byte_getter=True,source_owned_default_record=default_section,trace_sha256=trace_hash.hexdigest(),ownership_rows=rows,ownership_sha256=sha(ledger),evidence=evidence,provider_reports=reports,driver_sha256=sha(Path(__file__)),application_sha256=ah,application_linked=False,instruction_identity=False,limitations=['Raw charger, optional updater and operation sender are boundary fixtures; shared charge-byte getter and both predicates execute','Exact native24-byte savedframe/8-byte payload compared; private Cworker stack outside that frame and logger/provider writes there remain gated','Full-word config85 path reloads state after modeled refresh; actual recursive updater composition remains gated','Null-header readfault is emulated evidence; hardware power/concurrency, canonical/fullstartup and instruction/wholeimage identity unproven']),indent=2)+'\n');print('Protocol device status:',counts,providers,predicate_entries,status_null_faults)
if __name__=='__main__':main()
