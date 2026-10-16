#!/usr/bin/env python3
"""Native profile command with raw trailing event bytes; actual accessor/ack."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-user-profile-runtime';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();P=0x20003001;EVENT=0x2003efe4

def main():
 rp=OUT/'report.json';b=json.loads(rp.read_text());obj=OUT/'user-profile-source.o';assert sha(obj)==b['graph_object_sha256']
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 layout=ROOT/'r1/source-config/runtime/native_user_profile_verification.ld';states={};digest=hashlib.sha256();obs=0;counts={'matrix':0,'fields':0,'workflow':0};hits={k:0 for k in ['response','event','mode','ring','sdk']}
 with tempfile.TemporaryDirectory() as tmp:
  d=Path(tmp);elf=d/'test.elf';subprocess.run(['arm-none-eabi-ld','-T',str(layout),str(obj),'-o',str(elf)],check=True);sections={}
  for n in ['text','ring','sdk']:
   p=d/(n+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j','.'+n,'-O','binary',str(elf),str(p)],check=True);sections[n]=p.read_bytes()
  syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
  for n,a in [('ring',0x84adc),('sdk',0x84b08)]:assert sections[n]==raw[a-0x27000:a-0x27000+len(sections[n])]
  def hook(u,a,size,_):
   st=states[id(u)];source=st['source'];assert not source or not 0x27000<=a<0xc4d08
   if a==(syms['r1_packet_field12_get'] if source else 0x82bd4):st['after_accessor']=u.reg_read(UC_ARM_REG_LR)&~1
   if st['after_accessor']==a:
    st['after_accessor']=None
    if st['mutation']==6:u.mem_write(P+8,b'\x18\x00');u.mem_write(P+12,b'\xff\x02\xfa\x7f\x81\xff')
   kind=({0x20000204:'response',0x20000208:'event',0x2000020c:'mode',0x20000210:'ring',0x20000214:'sdk'} if source else {0x828b4:'response',0x8d8fc:'event',0x914ec:'mode',0x91638:'ring',0x799f8:'sdk'}).get(a)
   if not kind:return
   r=[u.reg_read(x) for x in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];ret=st['result'];m=st['mutation'];event=[kind]
   if kind=='response':
    assert r[2:]==[0,0];event+=[r[0],bytes(u.mem_read(r[1],8)).hex(),r[2:]]
    if m==4:u.mem_write(P+8,b'\x18\x00');u.mem_write(P+12,b'\x00\xfe\x7f\xff\x80\x01');u.mem_write(EVENT+10,b'\x55\xaa')
   elif kind=='event':
    assert r[:3]==[0x100a,EVENT,12];event+=[r[:3],bytes(u.mem_read(r[1],12)).hex()]
    if m==5:u.mem_write(EVENT+10,b'\x12\x34')
   elif kind=='mode':
    ret=st['modes'][st['mi']%len(st['modes'])];st['mi']+=1;event+=[ret]
    if m==1:u.mem_write(P+8,b'\x0c\x00');u.mem_write(P+3,b'\x78\x56');u.mem_write(P+12,b'\x01\x23\x45\x67\x89\xab')
   elif kind=='ring':
    assert r[:3]==[0x0d000000,0x84adc,0x84adc];extra=list(struct.unpack('<III',u.mem_read(u.reg_read(UC_ARM_REG_SP),12)));event+=[r,extra]
    if m==2:u.mem_write(P+3,b'\xfe\xdc');u.mem_write(P+12,b'\x00\xff\x34\x12\xcd\xab')
   elif kind=='sdk':
    assert r[:2]==[0x001c0003,0x84b08];extra=list(struct.unpack('<II',u.mem_read(u.reg_read(UC_ARM_REG_SP),8)));event+=[r,extra]
    if m==3:u.mem_write(P+3,b'\x10\x32');u.mem_write(P+12,b'\xff\x02\xfa\x7f\x81\xff')
   st['events'].append(event);u.reg_write(UC_ARM_REG_R0,ret)
   for reg,v in [(UC_ARM_REG_R1,0xabcdef01),(UC_ARM_REG_R2,0x12345678),(UC_ARM_REG_R3,0x89abcdef)]:u.reg_write(reg,v)
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  machines=[]
  for source in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,raw);u.mem_map(0x1000000,0x20000);u.mem_write(0x1000000,sections['text']);u.mem_map(0x20000000,0x40000)
   for n,a in [('ring',0x84adc),('sdk',0x84b08)]:u.mem_write(a,sections[n])
   u.hook_add(UC_HOOK_CODE,hook);machines.append(u)
  modes=[[0],[1],[2],[4],[7],[0,4,2],[1,0],[0xffffffff,0x80000000]];results=[0,1,0xffffffff,0x80000000];seeds=[0,0x55,0xaa,0xff];cases=[]
  for number,(length,first,m,seed) in enumerate(itertools.product([0,12,13,17,18,24,65535],range(256),range(7),seeds)):cases.append(('matrix',length,first,number%256,0x1234,0xabcd,m,seed,modes[number%8],results[(number//8)%4]))
  for number,(first,second,third,fourth,m,mode) in enumerate(itertools.product([0,1,255],[0,1,255],[0,1,255,256,32768,65535],[0,1,255,256,32768,65535],range(7),modes)):cases.append(('fields',24,first,second,third,fourth,m,seeds[number%4],mode,results[(number//4)%4]))
  for length,first,m,seed,mode,result in itertools.product([12,13,24],[0,1,255],range(7),seeds,modes,results):cases.append(('workflow',length,first,255,0xffff,0x8000,m,seed,mode,result))
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  for number,(kind,length,first,second,third,fourth,m,seed,mode,result) in enumerate(cases):
   outputs=[]
   for source,u in enumerate(machines):
    u.mem_write(0x20000000,bytes([seed])*0x40000);u.mem_write(P,bytes(range(64)));u.mem_write(P+8,struct.pack('<H',length));u.mem_write(P+12,bytes([first,second])+struct.pack('<HH',third,fourth));states[id(u)]=dict(source=source,events=[],after_accessor=None,mutation=m,modes=mode,mi=0,result=result);regs=[]
    for iteration in range(2 if kind=='workflow' else 1):
     u.reg_write(UC_ARM_REG_XPSR,0x01000000);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
     for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
     for reg,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],[0x1000ffff,P,0x55667788,0x99aabbcc]):u.reg_write(reg,v)
     u.emu_start((syms['r1_native_user_profile_handler'] if source else 0x84a10)|1,0x20000100,count=10000);assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)];regs.append(u.reg_read(UC_ARM_REG_R0))
    mem=bytes(u.mem_read(0x20000000,0x3e000))+bytes(u.mem_read(0x2003f000,0x1000));outputs.append([regs,states[id(u)]['events'],hashlib.sha256(mem).hexdigest()])
   if outputs[0]!=outputs[1]:(OUT/'counterexample.json').write_text(json.dumps(dict(number=number,case=[kind,length,first,second,third,fourth,m,seed,mode,result],outputs=outputs),indent=2)+'\n');raise AssertionError((number,kind))
   counts[kind]+=1
   for event_record in outputs[0][1]:hits[event_record[0]]+=1
   obs+=len(outputs[0][1]);digest.update(json.dumps([number,kind,length,first,second,third,fourth,m,seed,mode,result,outputs[0]],sort_keys=True).encode())
 assert all(hits.values()),hits
 receipt=dict(comparisons=sum(counts.values()),counts=counts,lower_observation_counts=hits,observations_per_side=obs,trace_sha256=digest.hexdigest(),actual_packet_accessor_and_flag_ack=True,only_lower_response_event_logging_are_fixtures=True,all_first_byte_values_and_halfword_edges_checked=True,event_last_two_bytes_preserve_seed_and_mutations=True,two_call_event_tail_workflows_checked=True,fresh_payload_after_logs_and_ack_checked=True,raw_r0_callee_sp_and_nonstack_ram_checked=True,no_native_candidate_execution=True,portable_policy_modified=False,runtime_admission_changed=False,hardware_write_executed=False,profile_event_delivery_proven=False,full_raw_abi_verified=False,cross_call_private_frame_history_verified=False,instruction_identity=False,whole_image_complete=False,driver_sha256=sha(Path(__file__)),report_sha256=sha(rp),object_sha256=sha(obj),layout_sha256=sha(layout),application_sha256=sha(app))
 (OUT/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
