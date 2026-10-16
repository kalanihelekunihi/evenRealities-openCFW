#!/usr/bin/env python3
"""Differential power command frame/tail behavior; lower effects are fixtures."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-power-command-runtime';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();P=0x20003001;FRAME=0x2003efe8
KINDS=['ack','delay','marker','voltage','timestamp','fields','flags','mode','ring','sdk'];NATIVE=[0x8287c,0x7d154,0x7efd6,0x91290,0x8ada4,0x73710,0x7d6f4,0x914ec,0x91638,0x799c0]
def main():
 rp=OUT/'report.json';b=json.loads(rp.read_text());obj=OUT/'power-command-source.o';assert sha(obj)==b['graph_object_sha256']
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 layout=ROOT/'r1/source-config/runtime/native_power_command_verification.ld';states={};digest=hashlib.sha256();obs=0;counts={'null':0,'rejected':0,'changed':0,'reset':0,'off':0,'resume':0}
 with tempfile.TemporaryDirectory() as tmp:
  d=Path(tmp);elf=d/'test.elf';subprocess.run(['arm-none-eabi-ld','-T',str(layout),str(obj),'-o',str(elf)],check=True);sections={}
  for n in ['text','ring','sdk','thread']:
   p=d/(n+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j','.'+n,'-O','binary',str(elf),str(p)],check=True);sections[n]=p.read_bytes()
  syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3};assert syms['r1_low_battery_thread_handle']==0x20006548
  for n,a in [('ring',0xc0278),('sdk',0xc02c4)]:assert sections[n]==raw[a-0x27000:a-0x27000+len(sections[n])]
  assert sections['thread']==bytes(4)
  def hook(u,a,size,_):
   st=states[id(u)];source=st['source'];assert not source or not 0x27000<=a<0xc4d08
   if a==(syms['r1_packet_field12_get'] if source else 0x82bd4):st['after_accessor']=u.reg_read(UC_ARM_REG_LR)&~1
   if st['after_accessor']==a:
    st['after_accessor']=None
    if st['mutation']==1:u.mem_write(P+8,b'\x0c\x00');u.mem_write(P+3,b'\x78\x56');u.mem_write(P+12,bytes([st['next']]))
   kind=(dict(zip(range(0x20000204,0x2000022c,4),KINDS)) if source else dict(zip(NATIVE,KINDS))).get(a)
   if not kind:return
   r=[u.reg_read(x) for x in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];ret=st['result'];m=st['mutation'];event=[kind]
   if kind=='ack':
    extra=struct.unpack('<I',u.mem_read(u.reg_read(UC_ARM_REG_SP),4))[0];assert r[:3]==[0x1000ffff,18,1] and extra in [0,1];event+=[r,extra]
    if m==2:u.mem_write(P+12,bytes([st['next']]));u.mem_write(P+3,b'\xfe\xdc')
   elif kind=='delay':
    assert r[0]==100;event+=[r[0]]
    if m==3:u.mem_write(P+12,bytes([st['next']]))
   elif kind=='marker':assert r[0]==1;event+=[r[0]]
   elif kind=='voltage':
    ret=st['voltage'];event+=[ret,bytes(u.mem_read(FRAME,8)).hex()]
    if m==4:u.mem_write(FRAME+4,struct.pack('<I',0xcafeffff))
   elif kind=='timestamp':
    ret=st['timestamp'];event+=[ret]
    if m==5:u.mem_write(FRAME+4,struct.pack('<I',0xdeadbeef))
   elif kind=='fields':
    assert r[0]==FRAME;event+=[r[0],bytes(u.mem_read(r[0],8)).hex()]
    if m==6:u.mem_write(FRAME,struct.pack('<II',0x76543210,0xfedcba98))
   elif kind=='flags':assert r[1] in [1,2,256];event+=r[:2]
   elif kind=='mode':ret=st['modes'][st['mi']%len(st['modes'])];st['mi']+=1;event+=[ret]
   elif kind=='ring':assert r[:3]==[0x0c000000,0xc0278,0xc0278];event+=r[:3]
   elif kind=='sdk':assert r[:2]==[0x001c0003,0xc02c4];event+=r[:2]
   st['events'].append(event)
   if m==7 and kind in ['marker','fields','ring','sdk']:u.mem_write(0x20006548,struct.pack('<I',0x20008888))
   if m==8 and kind=='mode':u.mem_write(0x20006548,struct.pack('<I',0x20009999))
   u.reg_write(UC_ARM_REG_R0,ret)
   for reg,v in [(UC_ARM_REG_R1,0xabcdef01),(UC_ARM_REG_R2,0x12345678),(UC_ARM_REG_R3,0x89abcdef)]:u.reg_write(reg,v)
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  machines=[]
  for source in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,raw);u.mem_map(0x1000000,0x20000);u.mem_write(0x1000000,sections['text']);u.mem_map(0x20000000,0x40000)
   for n,a in [('ring',0xc0278),('sdk',0xc02c4)]:u.mem_write(a,sections[n])
   u.hook_add(UC_HOOK_CODE,hook);machines.append(u)
  modes=[[0],[1],[2],[4],[7],[0,4,2],[1,0],[0xffffffff,0x80000000]];seeds=[0,0xffffffff,0x12345678,0xaabb0000];results=[0,1,0x80000000,0xffffffff];volts=[0,1,0x3fff,0x4000,0xffff,0xffffffff];cases=[]
  for number,(length,command,m) in enumerate(itertools.product([0,12,13,24,65535],range(256),range(9))):cases.append((length,command,m,number%256,modes[number%8],seeds[(number//8)%4],results[(number//32)%4],volts[(number//128)%6]))
  for number,(command,changed,m,mode,seed,result,voltage) in enumerate(itertools.product([1,2,3],[0,1,2,3,4,255],[2,3],modes,seeds,results,volts)):cases.append((24,command,m,changed,mode,seed,result,voltage))
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  for number,(length,command,m,changed,mode,seed,result,voltage) in enumerate(cases):
   outputs=[];timestamp=[0,1,0xffffffff,0x80000000,0x12345678][number%5]
   for source,u in enumerate(machines):
    u.mem_write(0x20000000,b'\x96'*0x40000);u.mem_write(P,bytes(range(64)));u.mem_write(P+8,struct.pack('<H',length));u.mem_write(P+12,bytes([command]));u.mem_write(0x20006548,struct.pack('<I',[0,0x20007777][number%2]));states[id(u)]=dict(source=source,events=[],after_accessor=None,mutation=m,next=changed,modes=mode,mi=0,result=result,voltage=voltage,timestamp=timestamp)
    u.reg_write(UC_ARM_REG_XPSR,0x01000000);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    for reg,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],[0x1000ffff,P,0x55667788,seed]):u.reg_write(reg,v)
    u.emu_start((syms['r1_protocol_command_000843c8'] if source else 0x843c8)|1,0x20000100,count=10000);assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
    mem=bytes(u.mem_read(0x20000000,0x3e000))+bytes(u.mem_read(0x2003f000,0x1000));outputs.append([[u.reg_read(reg) for reg in [UC_ARM_REG_R0,UC_ARM_REG_R2,UC_ARM_REG_R3]],states[id(u)]['events'],hashlib.sha256(mem).hexdigest()])
   if outputs[0]!=outputs[1]:(OUT/'counterexample.json').write_text(json.dumps(dict(number=number,case=[length,command,m,changed,mode,seed,result,voltage],outputs=outputs),indent=2)+'\n');raise AssertionError(number)
   events=outputs[0][1];kinds=[x[0] for x in events];kind='null' if not events else 'rejected' if 'delay' not in kinds else 'reset' if 'marker' in kinds else 'off' if 'fields' in kinds else 'resume' if 'flags' in kinds else 'changed';counts[kind]+=1;obs+=len(events);digest.update(json.dumps([number,length,command,m,changed,mode,seed,result,voltage,timestamp,outputs[0]],sort_keys=True).encode())
 receipt=dict(comparisons=sum(counts.values()),counts=counts,observations_per_side=obs,trace_sha256=digest.hexdigest(),actual_packet_accessor=True,all_lower_effects_are_fixtures=True,explicit_post_call_mutations=True,command_reread_after_delay_checked=True,event_preserves_incoming_upper16=True,tail_and_nontail_r2_r3_restore_checked=True,raw_r0_r2_r3_callee_sp_and_nonstack_ram_checked=True,no_native_candidate_execution=True,runtime_admission_changed=False,hardware_write_executed=False,full_raw_abi_verified=False,cross_call_private_frame_history_verified=False,instruction_identity=False,whole_image_complete=False,driver_sha256=sha(Path(__file__)),report_sha256=sha(rp),object_sha256=sha(obj),layout_sha256=sha(layout),application_sha256=sha(app))
 (OUT/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
