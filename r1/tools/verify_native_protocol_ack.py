#!/usr/bin/env python3
"""Actual ACK accessor/lock/scan/handler, with explicit RTOS/delayed/callback fixtures."""
import hashlib,itertools,json,random,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-protocol-ack';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();TABLE=0x20019ef4;CACHE=0x20006b8c
ENTRIES={'lock':('r1_ack_table_lock',0x48234),'unlock':('r1_ack_table_unlock',0x48258),'payload':('r1_packet_field12_get',0x82bd4),'resolve':('r1_ack_resolver',0x83028),'packet':('r1_packet_ack_handler',0x842cc),'restart':('r1_delayed_event_restart',0x84130),'noop':('r1_delayed_restart_callback',0x4d2f0)}
def main():
 rp=BASE/'native-protocol-ack-runtime/report.json';r=json.loads(rp.read_text());obj=rp.parent/'protocol-ack-source.o';assert sha(obj)==r['ack_object_sha256']
 for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';layout=ROOT/'r1/source-config/runtime/native_protocol_ack_verification.ld';states={};digest=hashlib.sha256();counts={k:0 for k in ENTRIES};observations=0
 with tempfile.TemporaryDirectory() as tmp:
  d=Path(tmp);elf=d/'test.elf';subprocess.run(['arm-none-eabi-ld','-T',str(layout),str(obj),'-o',str(elf)],check=True);sections={}
  for section in ['.text','.callback','.attributes','.name']:
   p=d/(section[1:]+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j',section,'-O','binary',str(elf),str(p)],check=True);sections[section]=p.read_bytes()
  assert sections['.callback']==raw[0x4d2f0-0x27000:0x4d2f2-0x27000] and sections['.attributes']==raw[0x9a434-0x27000:0x9a444-0x27000] and sections['.name']==raw[0xc0228-0x27000:0xc0232-0x27000]
  syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3};assert syms['r1_ack_mutex']==CACHE and syms['r1_ack_mutex_control']==0x20019ea4 and syms['r1_protocol_reset_workspace']==TABLE
  def snapshot(u):return [struct.unpack('<I',u.mem_read(CACHE,4))[0],hashlib.sha256(u.mem_read(TABLE,640)).hexdigest()]
  def hook(u,a,size,_):
   st=states[id(u)];source=st['source'];assert not source or not 0x27000<=a<0xc4d08 or 0x4d2f0<=a<0x4d2f2
   fixtures={0x20000200:'new',0x20000204:'acquire',0x20000208:'release',0x2000020c:'cancel',0x20000210:'schedule',0x20000220:'callback_a',0x20000224:'callback_b'} if source else {0x7d4d6:'new',0x7d488:'acquire',0x7d536:'release',0x65d64:'cancel',0x65b4c:'schedule',0x20000220:'callback_a',0x20000224:'callback_b'}
   kind=fixtures.get(a)
   if not kind:return
   r0=u.reg_read(UC_ARM_REG_R0);r1=u.reg_read(UC_ARM_REG_R1);r2=u.reg_read(UC_ARM_REG_R2);result=st['status']
   if kind=='new':
    assert r0==0x9a434 and bytes(u.mem_read(r0,16))==sections['.attributes'];st['events'].append(['new',r0,snapshot(u)]);result=st['new_result']
    if st['mutation']==3:u.mem_write(CACHE,struct.pack('<I',0xdeadbeef));u.mem_write(TABLE,b'\xff')
   elif kind=='acquire':
    assert r1==0xffffffff;st['events'].append(['acquire',r0,r1,snapshot(u)])
    if st['mutation']==1:u.mem_write(CACHE,struct.pack('<I',0x20002900));u.mem_write(TABLE,st['injected'])
   elif kind=='release':
    st['events'].append(['release',r0,snapshot(u)])
    if st['mutation']==2:
     slot=TABLE+20*max(st['match'],0);u.mem_write(slot+8,struct.pack('<2I',0x20000225,0xfedcba98));u.mem_write(CACHE,bytes(4))
   elif kind.startswith('callback'):
    st['events'].append([kind,r0,snapshot(u)]);result=st['status']^(0xaaaa5555 if kind=='callback_a' else 0x5555aaaa)
   elif kind=='cancel':assert [r0,r1]==[0x4d2f1,0];st['events'].append(['cancel',r0,r1])
   else:assert [r0,r1,r2]==[0x4d2f1,st['handle'],0x7800];st['events'].append(['schedule',r0,r1,r2])
   u.reg_write(UC_ARM_REG_R0,result);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  machines=[]
  for source in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,raw);u.mem_map(0x1000000,0x20000);u.mem_write(0x1000000,sections['.text']);u.mem_map(0x20000000,0x40000)
   if source:
    for section,address in [('.callback',0x4d2f0),('.attributes',0x9a434),('.name',0xc0228)]:u.mem_write(address,sections[section])
   u.hook_add(UC_HOOK_CODE,hook);machines.append(u)
  rng=random.Random(0x83028);cases=[]
  # kind, match, active, callback mode, key profile, mutation, cached, advertised length
  for match,active,callback,mutation,cached in itertools.product(range(-1,32),[0,1,255],range(3),range(4),[0,0x20002800]):cases.append(('resolve',match,active,callback,0,mutation,cached,18))
  for match,key,cached in itertools.product(range(-1,32),range(1,7),[0,0x20002800]):cases.append(('resolve',match,1,1,key,0,cached,18))
  for match,active,callback,mutation,length in itertools.product(range(-1,32),[0,1,255],range(3),range(4),[0,12,13,18,65535]):cases.append(('packet',match,active,callback,0,mutation,0 if match&1 else 0x20002800,length))
  for _ in range(1024):cases.append(('resolve',rng.randrange(-1,32),rng.choice([0,1,255]),rng.randrange(3),7,rng.randrange(4),rng.choice([0,0x20002800]),18))
  for kind,cached,key,mutation in itertools.product(['lock','unlock','restart','noop'],[0,0x20002800,0xffffffff],range(8),range(4)):cases.append((kind,0,1,1,key,mutation,cached,18))
  for length,alignment in itertools.product(list(range(17))+[255,256,65535],range(2)):cases.append(('payload',alignment,1,1,alignment,0,0,length))
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  for number,(kind,match,active,callback,key,mutation,cached,length) in enumerate(cases):
   query=[0x12,0x34,0x56,0x789a]
   if 1<=key<=4:query[key-1]|=0x100 if key<4 else 0x10000
   elif key==5:query=[255,255,255,65535]
   elif key==6:query=[0,0,0,0]
   elif key==7:query=[rng.randrange(256),rng.randrange(256),rng.randrange(256),rng.randrange(65536)]
   argument=rng.getrandbits(32);status=[0,1,0xffffffff,0x80000000,0x12345678,0x89abcdef,0x55aa55aa,0xa55a5aa5][number%8];new_result=[0,0x20002800,0xffffffff][number%3];handle=argument;packet=0x20003000+(number&1);callback_pointer=[0,0x20000221,0x20000225][callback]
   def record(present,callback,arg,first=None):return struct.pack('<4BH2x3I',present,query[0]&255 if first is None else first,query[1]&255,query[2]&255,query[3]&65535,callback,arg,0x11223344)
   table=b''.join(record(1,0x20000221,argument^i,first=(query[0]+1)&255) for i in range(32));table=bytearray(table)
   if match>=0:
    table[match*20:(match+1)*20]=record(active,callback_pointer,argument)
    if callback==2 and match<31:table[(match+1)*20:(match+2)*20]=record(active,0x20000221,argument^0xffffffff)
   injected=record(255,0x20000225,argument^0x12345678);results=[]
   for source,u in enumerate(machines):
    u.mem_write(0x20000000,b'\x96'*0x40000);u.mem_write(TABLE,bytes(table));u.mem_write(CACHE,struct.pack('<I',cached));payload=bytearray(range(32));payload[8:10]=struct.pack('<H',length);payload[12:15]=bytes(x&255 for x in query[:3]);payload[16:18]=struct.pack('<H',query[3]&65535);u.mem_write(packet,bytes(payload));states[id(u)]=dict(source=source,events=[],mutation=mutation,status=status,new_result=new_result,match=match,injected=injected,handle=handle);returns=[]
    for step in range(2 if kind in ['resolve','packet'] else 1):
     u.reg_write(UC_ARM_REG_XPSR,0x01000000);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
     for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
     args=query if kind=='resolve' else [packet,argument,status,0xaabbccdd] if kind=='payload' else [handle,packet,status,argument]
     for reg,value in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],args):u.reg_write(reg,value)
     u.emu_start((syms[ENTRIES[kind][0]] if source else ENTRIES[kind][1])|1,0x20000100,count=20000);assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)];returns.append(u.reg_read(UC_ARM_REG_R0))
    memory=bytes(u.mem_read(0x20000000,0x3e000))+bytes(u.mem_read(0x2003f000,0x1000));results.append([returns,states[id(u)]['events'],hashlib.sha256(memory).hexdigest()])
   if results[0]!=results[1]:
    fail=dict(number=number,kind=kind,match=match,active=active,callback=callback,key=key,query=query,mutation=mutation,cached=cached,length=length,results=results);(OUT/'counterexample.json').write_text(json.dumps(fail,indent=2)+'\n');raise AssertionError({k:v for k,v in fail.items() if k!='results'})
   counts[kind]+=1;observations+=len(results[0][1]);digest.update(json.dumps([number,kind,match,active,callback,key,query,argument,mutation,cached,length,results[0]],sort_keys=True).encode())
 receipt=dict(workflows=sum(counts.values()),counts=counts,observations_per_side=observations,trace_sha256=digest.hexdigest(),actual_source_accessor_lock_unlock_resolver_handler=True,all32_slots_duplicate_first_match_and_two_call_sequences=True,full_word_keys_not_truncated_by_resolver=True,lazy_mutex_null_creation_and_unconditional_acquire_checked=True,clear_before_unlock_callback_captured_before_unlock=True,mutex_and_delayed_and_ack_callback_bodies_are_fixtures=True,source_workspace_reused=True,source_descriptor_and_name_match_native=True,source_restart_callback_two_bytes_match_native=True,controlled_provider_mutations_not_physical_concurrency=True,raw_r0_callee_sp_and_observed_nonstack_ram_checked=True,candidate_native_execution_forbidden_except_compiled_noop=True,application_sha256=sha(app),driver_sha256=sha(Path(__file__)),runtime_report_sha256=sha(rp),object_sha256=sha(obj),layout_sha256=sha(layout),whole_ack_rtos_graph_executed=False,physical_concurrency_verified=False,full_raw_abi_verified=False,instruction_identity=False,whole_image_complete=False)
 (OUT/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
