#!/usr/bin/env python3
"""Actual health dispatcher/search/all14 targets with real source flag helpers; only lower providers are fixtures."""
import csv,hashlib,itertools,json,random,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-health-commands-runtime';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ADDRESSES=[0x8280c,0x82844,0x8287c,0x82c44,0x82c8a,0x82cce,0x82d14,0x82d5a,0x82d9e,0x82dbe,0x82df8,0x82dfa,0x82e34,0x82e66,0x82e9a,0x82ece]
def main():
 rp=OUT/'report.json';r=json.loads(rp.read_text());obj=OUT/'health-dispatch-graph-source.o';assert sha(obj)==r['graph_object_sha256']
 for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';layout=ROOT/'r1/source-config/runtime/native_health_dispatch_graph_verification.ld';ledger=list(csv.DictReader((ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv').open()));byentry={int(x['entry'],16):x['upstream_symbol'] for x in ledger if x['image']=='application'};entries=[(int.from_bytes(raw[0x9a454-0x27000+i*8:0x9a454-0x27000+i*8+2],'little'),byentry[int.from_bytes(raw[0x9a454-0x27000+i*8+4:0x9a454-0x27000+i*8+8],'little')&~1]) for i in range(14)];assert len(entries)==14;states={};digest=hashlib.sha256();counts={name:0 for _,name in entries};responses=0;events=0
 with tempfile.TemporaryDirectory() as tmp:
  d=Path(tmp);elf=d/'test.elf';binary=d/'text.bin';subprocess.run(['arm-none-eabi-ld','-T',str(layout),str(obj),'-o',str(elf)],check=True);subprocess.run(['arm-none-eabi-objcopy','-j','.text','-O','binary',str(elf),str(binary)],check=True);syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3};handler_indexes=[{entry:symbol for entry,symbol in byentry.items() if symbol in counts},{syms[symbol]:symbol for _,symbol in entries}];table=d/'table.bin';subprocess.run(['arm-none-eabi-objcopy','-j','.health_table','-O','binary',str(elf),str(table)],check=True)
  def hook(u,a,size,_):
   st=states[id(u)];source=st['source'];assert not source or not 0x27000<=a<0xc4d08
   symbol=handler_indexes[source].get(a)
   if symbol:st['events'].append(['handler',symbol,u.reg_read(UC_ARM_REG_R3)])
   fixture={0x20000200:'response',0x20000204:'event',0x20000208:'setting'} if source else {0x828b4:'response',0x8d8fc:'event',0x8b834:'setting'}
   if a not in fixture:return
   kind=fixture[a];r0=u.reg_read(UC_ARM_REG_R0);r1=u.reg_read(UC_ARM_REG_R1);r2=u.reg_read(UC_ARM_REG_R2);r3=u.reg_read(UC_ARM_REG_R3)
   if kind=='response':
    assert r2==0 and r3==0;st['events'].append(['response',r0,bytes(u.mem_read(r1,8)).hex(),r2,r3])
    if st['mutation']==1:u.mem_write(st['packet']+3,struct.pack('<H',st['changed_sequence']));u.mem_write(st['packet']+5,b'\x03')
    elif st['mutation']==2:u.mem_write(r1,b'\xff'*8)
   elif kind=='event':
    assert r2 in [0,1,8];payload=bytes(u.mem_read(r1,r2)).hex() if r2 else '';assert r1 or not r2;st['events'].append(['event',r0,payload,r2])
    if st['mutation']==2 and r2:u.mem_write(r1,b'\xaa'*r2)
   else:assert r0 in [0,1];st['events'].append(['setting',r0])
   u.reg_write(UC_ARM_REG_R0,st['returned']);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  machines=[]
  for source in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x1000);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,raw);u.mem_map(0x1000000,0x20000);u.mem_write(0x1000000,binary.read_bytes());u.mem_map(0x20000000,0x40000);
   if source:u.mem_write(0x9a454,table.read_bytes())
   u.hook_add(UC_HOOK_CODE,hook);machines.append(u)
  rng=random.Random(0x82c44);cases=[]
  for (a,name),flags,pattern,mutation in itertools.product(entries,range(256),range(4),range(3)):
   handle=[0,0xffff,0xffffffff,0x12345678][pattern];seq=[0,1,0xffff,(flags*257)^0x55aa][pattern];seed=[0,0xffffffff,0x80000000,rng.getrandbits(32)][pattern];cases.append((a,name,handle,flags,pattern,mutation,seq,seed))
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  for a,name,handle,flags,pattern,mutation,sequence,seed in cases:
   results=[];packet=0x20003000+(pattern&1);returned=(seed^0x55aa33cc)&0xffffffff;command=[0,1,0xffff,0xffffffff,0x12345678,0x80000000,0x101,0x501][pattern%8];version=(flags*0x01010101)^(0xabcdef00 if pattern&2 else 0);extra=(flags*0x01010101)^(0xabcdef00 if pattern&4 else 0)
   for source,u in enumerate(machines):
    u.mem_write(0,b'\x00' if pattern&1 else b'\xff');u.mem_write(0x20000000,b'\x96'*0x40000);payload=bytearray(range(32));payload[3:5]=struct.pack('<H',sequence&65535);payload[5]=flags;payload[6]=a>>8;payload[7]=a&255;payload[8:10]=struct.pack('<H',[12,13,0,65535][pattern%4]);payload[12]=[0,1,2,255][pattern%4];u.mem_write(packet,bytes(payload));states[id(u)]=dict(source=source,events=[],returned=returned,mutation=mutation,packet=packet,changed_sequence=(sequence^0x8080)&65535)
    u.reg_write(UC_ARM_REG_XPSR,0x01000000);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101);u.mem_write(0x2003f000,struct.pack('<I',extra))
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    args=[handle,packet,seed^0xaabbccdd,seed]
    for reg,value in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],args):u.reg_write(reg,value)
    u.emu_start((syms['r1_health_registration_dispatcher'] if source else 0x82be8)|1,0x20000100,count=10000);assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
    memory=bytes(u.mem_read(0x20000000,0x3e000))+bytes(u.mem_read(0x2003f000,0x1000));results.append([u.reg_read(UC_ARM_REG_R0),states[id(u)]['events'],hashlib.sha256(memory).hexdigest()])
   if results[0]!=results[1]:
    fail=dict(name=name,handle=handle,flags=flags,pattern=pattern,mutation=mutation,sequence=sequence,seed=seed,results=results);(OUT/'counterexample.json').write_text(json.dumps(fail,indent=2)+'\n');raise AssertionError({k:v for k,v in fail.items() if k!='results'})
   counts[name]+=1;responses+=sum(e[0]=='response' for e in results[0][1]);events+=sum(e[0]=='event' for e in results[0][1]);digest.update(json.dumps([name,handle,flags,pattern,mutation,sequence,seed,results[0]],sort_keys=True).encode())
 receipt=dict(comparisons=sum(counts.values()),counts=counts,response_calls_per_side=responses,event_calls_per_side=events,trace_sha256=digest.hexdigest(),all_256_flag_bytes=True,actual_source_dispatch_search_all14_handlers=True,actual_source_flag_helpers_execute=True,only_lower_response_event_setting_providers_are_fixtures=True,event_seed_word_retained_not_zeroed=True,sequence_reloaded_after_response_and_no_flag_recheck=True,report_length12_address0_read_is_explicit_fixture=True,unaligned_packets_and_header_truncations_checked=True,raw_r0_callee_sp_and_observed_nonstack_ram_checked=True,private_event_header_pointers_not_compared=True,candidate_native_execution_forbidden=True,driver_sha256=sha(Path(__file__)),object_sha256=sha(obj),report_sha256=sha(rp),layout_sha256=sha(layout),application_sha256=sha(app),bounded_health_dispatch_graph_executed=True,whole_dispatch_graph_executed=False,physical_delivery_verified=False,instruction_identity=False,whole_image_complete=False)
 (OUT/'graph-verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
