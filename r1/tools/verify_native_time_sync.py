#!/usr/bin/env python3
"""Differential command control flow; lower effects are explicitly emulated."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-time-sync-runtime';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();P=0x20003001
LOGS={'lost_ring':0x847c8,'lost_sdk':0x847f0,'valid_ring':0x84814,'valid_sdk':0x8483c}
NATIVE=[0x65d64,0x8adb4,0x8ada4,0x8d8fc,0x8287c,0x82b54,0x7bb20,0x83c86,0x7bbe8,0x914ec,0x91638,0x799c0]
KINDS=['cancel','offset','timestamp','event','flag','ack','needed','query','report','mode','ring','sdk']
def main():
 rp=OUT/'report.json';b=json.loads(rp.read_text());obj=OUT/'time-sync-source.o';assert sha(obj)==b['graph_object_sha256']
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 layout=ROOT/'r1/source-config/runtime/native_time_sync_verification.ld';states={};digest=hashlib.sha256();obs=0;counts={'null':0,'query':0,'report':0}
 with tempfile.TemporaryDirectory() as tmp:
  d=Path(tmp);elf=d/'test.elf';subprocess.run(['arm-none-eabi-ld','-T',str(layout),str(obj),'-o',str(elf)],check=True);sections={}
  for n in ['text']+list(LOGS):
   p=d/(n+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j','.'+n,'-O','binary',str(elf),str(p)],check=True);sections[n]=p.read_bytes()
  syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
  for n,a in LOGS.items():assert sections[n]==raw[a-0x27000:a-0x27000+len(sections[n])]
  def hook(u,a,size,_):
   st=states[id(u)];source=st['source'];assert not source or not 0x27000<=a<0xc4d08
   kind=(dict(zip(range(0x20000204,0x20000234,4),KINDS)) if source else dict(zip(NATIVE,KINDS))).get(a)
   if not kind:return
   r=[u.reg_read(x) for x in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];ret=st['result'];m=st['mutation'];event=[kind]
   if kind=='cancel':assert r[:2]==[0x84c83,0];event+=r[:2]
   elif kind=='offset':ret=st['offset'];event+=[ret]
   elif kind=='timestamp':ret=st['timestamp'];event+=[ret]
   elif kind=='event':assert r[0]==3 and r[2]==12;event+=[r[0],bytes(u.mem_read(r[1],12)).hex(),r[2]]
   elif kind=='flag':
    extra=struct.unpack('<I',u.mem_read(u.reg_read(UC_ARM_REG_SP),4))[0];assert r[:3]==[0x1000ffff,5,1] and extra==0;event+=[r,extra]
   elif kind=='ack':
    extra=list(struct.unpack('<III',u.mem_read(u.reg_read(UC_ARM_REG_SP),12)));assert r==[0x1000ffff,4,1,1] and extra==[0,0,0];event+=[r,extra]
   elif kind=='needed':ret=st['needed'];event+=[ret]
   elif kind in ['query','report']:pass
   elif kind=='mode':ret=st['modes'][st['mi']%len(st['modes'])];st['mi']+=1;event+=[ret]
   elif kind=='ring':assert r[0]==0x0c000000 and r[1]==r[2] and r[1] in [0x847c8,0x84814];event+=r[:3]
   elif kind=='sdk':assert r[0]==0x001c0003 and r[1] in [0x847f0,0x8483c];event+=r[:2]
   st['events'].append(event)
   # Explicit lower-call mutation fixtures test capture and fresh reads. A changed
   # advertised length never grants a new bounds guarantee to this native ABI.
   triggers={1:'cancel',2:'offset',3:'timestamp',4:'event',5:'flag',6:'mode',7:'ring'}
   if triggers.get(m)==kind:u.mem_write(P+3,b'\x78\x56');u.mem_write(P+8,b'\x0c\x00');u.mem_write(P+12,bytes([st['mi']&255,0xfe,0xdc,0xba,0x98,0x76]))
   u.reg_write(UC_ARM_REG_R0,ret)
   for reg,v in [(UC_ARM_REG_R1,0xabcdef01),(UC_ARM_REG_R2,0x12345678),(UC_ARM_REG_R3,0x89abcdef)]:u.reg_write(reg,v)
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  machines=[]
  for source in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,raw);u.mem_map(0x1000000,0x20000);u.mem_write(0x1000000,sections['text']);u.mem_map(0x20000000,0x40000)
   for n,a in LOGS.items():u.mem_write(a,sections[n])
   u.hook_add(UC_HOOK_CODE,hook);machines.append(u)
  modes=[[0],[1],[2],[4],[7],[0,4,2],[1,0],[0xffffffff,0x80000000]]
  cases=list(itertools.product([0,1,12,13,17,18,24,65535],[0,1,0x80000000,0xffffffff],modes,[0,1,0x80000000,0xffffffff],range(8)))
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  for number,(length,needed,mode,result,m) in enumerate(cases):
   outputs=[];offset=[0,1,0x7fff,0xffff8000,0xffffffff][number%5];timestamp=[0,1,0xffffffff,0x80000000,0x12345678][number%5]
   for source,u in enumerate(machines):
    u.mem_write(0x20000000,b'\x96'*0x40000);u.mem_write(P,bytes(range(64)));u.mem_write(P+8,struct.pack('<H',length));states[id(u)]=dict(source=source,events=[],mutation=m,modes=mode,mi=0,result=result,offset=offset,timestamp=timestamp,needed=needed)
    u.reg_write(UC_ARM_REG_XPSR,0x01000000);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    for reg,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],[0x1000ffff,P,0x55667788,0x99aabbcc]):u.reg_write(reg,v)
    u.emu_start((syms['r1_protocol_command_000846dc'] if source else 0x846dc)|1,0x20000100,count=10000)
    assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
    mem=bytes(u.mem_read(0x20000000,0x3e000))+bytes(u.mem_read(0x2003f000,0x1000));outputs.append([u.reg_read(UC_ARM_REG_R0),states[id(u)]['events'],hashlib.sha256(mem).hexdigest()])
   if outputs[0]!=outputs[1]:(OUT/'counterexample.json').write_text(json.dumps(dict(number=number,case=[length,needed,mode,result,m],outputs=outputs),indent=2)+'\n');raise AssertionError(number)
   kind='null' if len(outputs[0][1])==1 else 'query' if needed else 'report';counts[kind]+=1;obs+=len(outputs[0][1]);digest.update(json.dumps([number,length,needed,mode,result,m,offset,timestamp,outputs[0]],sort_keys=True).encode())
 receipt=dict(comparisons=len(cases),counts=counts,observations_per_side=obs,trace_sha256=digest.hexdigest(),actual_packet_accessor=True,all_lower_effects_are_fixtures=True,explicit_post_call_mutations=True,event_bytes_and_fresh_sequence_checked=True,cancellation_before_null_accessor_checked=True,short_backing_only_mapped_fixture=True,raw_r0_callee_sp_and_nonstack_ram_checked=True,no_native_candidate_execution=True,runtime_admission_changed=False,hardware_write_executed=False,full_raw_abi_verified=False,instruction_identity=False,whole_image_complete=False,driver_sha256=sha(Path(__file__)),report_sha256=sha(rp),object_sha256=sha(obj),layout_sha256=sha(layout),application_sha256=sha(app))
 (OUT/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
