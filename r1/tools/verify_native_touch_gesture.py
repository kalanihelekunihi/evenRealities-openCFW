#!/usr/bin/env python3
"""Native gesture state/packet behavior; lower effects are explicit fixtures."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-touch-gesture-runtime';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();P=0x20003001;FRAME=0x2003efd0;CONTACT=0x20016a60
LOGS={'reset_ring':(0x3ebfc,35),'reset_sdk':(0x3ec20,29),'single_ring':(0xbfcd8,101),'single_sdk':(0xbfd40,95),'double_ring':(0xbfc10,101),'double_sdk':(0xbfc78,95),'long_ring':(0xbff24,99),'long_sdk':(0xbff88,93),'up_ring':(0xbfe64,98),'up_sdk':(0xbfec8,92),'down_ring':(0xbfda0,100),'down_sdk':(0xbfe04,94),'release_ring':(0xbfb40,105),'release_sdk':(0xbfbac,99)}
KINDS=['schedule','marker','flags','tick','config','handle','tx','mode','ring','sdk'];NATIVE=[0x65b4c,0x7efd6,0x7d6f4,0x7d28c,0x7ba24,0x4cb34,0x34064,0x914ec,0x91638,0x799c0]
def main():
 rp=OUT/'report.json';b=json.loads(rp.read_text());obj=OUT/'touch-gesture-source.o';assert sha(obj)==b['graph_object_sha256']
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 layout=ROOT/'r1/source-config/runtime/native_touch_gesture_verification.ld';states={};digest=hashlib.sha256();obs=0;hits={k:0 for k in KINDS}
 with tempfile.TemporaryDirectory() as tmp:
  d=Path(tmp);elf=d/'test.elf';subprocess.run(['arm-none-eabi-ld','-T',str(layout),str(obj),'-o',str(elf)],check=True);sections={}
  data=['contact','pending','direction','synthetic','count','clients','time','up_time','down_time','thread']
  for n in ['text']+data+list(LOGS):
   p=d/(n+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j','.'+n,'-O','binary',str(elf),str(p)],check=True);sections[n]=p.read_bytes()
  syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3};assert syms['r1_touch_release_timer_pending']==0x200067c4 and syms['r1_touch_contact_state']==CONTACT
  for n,(a,z) in LOGS.items():assert sections[n]==raw[a-0x27000:a-0x27000+z]
  cold=(BASE/'native-scatter-data/observed-initialized-data.bin').read_bytes()
  for n,a in [('direction',0x200067c5),('count',0x200067cc),('time',0x200067dc),('up_time',0x200067e0),('down_time',0x200067e4)]:assert sections[n]==cold[a-0x200064a8:a-0x200064a8+len(sections[n])]
  def hook(u,a,size,_):
   st=states[id(u)];source=st['source'];assert not source or not 0x27000<=a<0xc4d08
   kind=(dict(zip(range(0x20000204,0x2000022c,4),KINDS)) if source else dict(zip(NATIVE,KINDS))).get(a)
   if not kind:return
   r=[u.reg_read(x) for x in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];ret=st['result'];m=st['mutation'];event=[kind]
   if kind=='schedule':
    assert r[:3]==[0x934e5,0,307];event+=r[:3]
    if m==4:u.mem_write(P,b'\x10\x05\x06\x00');u.mem_write(0x200067c4,b'\x00')
   elif kind=='marker':
    assert r[0]==2;event+=[r[0]]
    if m==2:u.mem_write(0x200067c5,b'\x02');u.mem_write(0x200067cc,b'\x02\x00');u.mem_write(0x20006548,struct.pack('<I',0x20009999));u.mem_write(CONTACT+40,struct.pack('<I',0xabcdef01))
   elif kind=='flags':
    assert r[1]==2;event+=r[:2]
    if m==3:u.mem_write(P,b'\x08\x01\x02\xff')
   elif kind=='tick':
    ret=st['tick'];event+=[ret]
    if m==5:u.mem_write(P+1,b'\xdd\xcc')
   elif kind=='config':
    ret=st['config'];event+=[ret,bytes(u.mem_read(FRAME,12)).hex()]
    if m==6:u.mem_write(FRAME,b'\xaa\xbb\xcc\xdd\x11\x22\x33\x44\x55\x66\x77\x88')
   elif kind=='handle':
    ret=st['first'] if st['hi']==0 else st['second'];st['hi']+=1;event+=[ret]
    if m==7:st['second']=0x1000ffff
   elif kind=='tx':
    assert r[1]==FRAME and r[2] in [5,11];event+=r[:3]+[bytes(u.mem_read(r[1],12)).hex()]
    if m==8:u.mem_write(FRAME,b'\x78\x56\x34\x12\x98\xba\xdc\xfe\x10\x32\x54\x76')
   elif kind=='mode':
    ret=st['modes'][st['mi']%len(st['modes'])];st['mi']+=1;event+=[ret]
    if m==1:u.mem_write(P,b'\x42\x11\x22\x00')
   elif kind=='ring':assert r[0]==0x0c000000 and r[1]==r[2] and r[1] in [v[0] for k,v in LOGS.items() if k.endswith('ring')];event+=r[:3]
   elif kind=='sdk':assert r[0]==0x001c0003 and r[1] in [v[0] for k,v in LOGS.items() if k.endswith('sdk')];event+=r[:2]
   st['events'].append(event);u.reg_write(UC_ARM_REG_R0,ret)
   for reg,v in [(UC_ARM_REG_R1,0xabcdef01),(UC_ARM_REG_R2,0x12345678),(UC_ARM_REG_R3,0x89abcdef)]:u.reg_write(reg,v)
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  machines=[]
  for source in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,raw);u.mem_map(0x1000000,0x20000);u.mem_write(0x1000000,sections['text']);u.mem_map(0x20000000,0x40000)
   for n,(a,z) in LOGS.items():u.mem_write(a,sections[n])
   u.hook_add(UC_HOOK_CODE,hook);machines.append(u)
  modes=[[0],[1],[2],[4],[7],[0,4,2],[1,0],[0xffffffff,0x80000000]];results=[0,1,0xffffffff,0x80000000];times=[0,399,400,401,1000,1001,0xffffffff,0x80000000];cases=[]
  # Every event-byte combination, direction counter edges and lower-call mutations.
  for number,(event,previous,count,m) in enumerate(itertools.product(range(256),[0,1,2],[0,1,2,65535],range(9))):cases.append((event,previous,count,m,2,number%3,times[number%8],modes[(number//8)%8],[0,85,255,0x10055][number%4],0x1234,0x5678,results[(number//4)%4]))
  for event,now,previous,count in itertools.product([1,2,4,32,64,96],times,[0,1,2],[0,1,2,65535]):cases.append((event,previous,count,0,0,0,now,modes[0],85,0xffff,0,0))
  for event,config,first,second,mode,m in itertools.product([4,8,16,32,64,2],[0,85,255,0x10055],[0,65535,0x1000ffff,0x80000000],[0,65535,0x1000ffff,0x1234],modes,range(9)):cases.append((event,0,0,m,0,0,1001,mode,config,first,second,0xffffffff))
  for event,clients,request,mode,m in itertools.product([1,2,32,64],[0,2,3,0xffffffff],[0,1,255],modes,range(9)):cases.append((event,1,2,m,clients,request,401,mode,0,0xffff,0xffff,0x80000000))
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  for number,(event,previous,count,m,clients,request,now,mode,config,first,second,result) in enumerate(cases):
   outputs=[];tick=[0,1,0xffffffff,0x80000000,0x12345678][number%5]
   for source,u in enumerate(machines):
    u.mem_write(0x20000000,b'\x96'*0x40000);u.mem_write(CONTACT,bytes(100));u.mem_write(CONTACT+40,struct.pack('<I',now));u.mem_write(CONTACT+48,bytes([(number//2)%2]));u.mem_write(0x200067c4,bytes([number%2,previous,number%3]));u.mem_write(0x200067cc,struct.pack('<H',count));u.mem_write(0x200067d8,struct.pack('<IIII',clients,*([0,1,0xffffffff,0x80000000][(number//3)%4] for _ in range(3))));u.mem_write(0x20006548,struct.pack('<I',0x20008888));u.mem_write(P,bytes([event,19,249,request]));states[id(u)]=dict(source=source,events=[],mutation=m,modes=mode,mi=0,result=result,tick=tick,config=config,first=first,second=second,hi=0)
    u.reg_write(UC_ARM_REG_XPSR,0x01000000);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    for reg,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],[P,0x11223344,0x55667788,0x99aabbcc]):u.reg_write(reg,v)
    u.emu_start((syms['r1_touch_gesture_dispatch_boundary'] if source else 0x3e938)|1,0x20000100,count=20000);assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
    regs=[u.reg_read(reg) for reg in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];mem=bytes(u.mem_read(0x20000000,0x3e000))+bytes(u.mem_read(0x2003f000,0x1000));outputs.append([regs,states[id(u)]['events'],hashlib.sha256(mem).hexdigest()])
   if outputs[0]!=outputs[1]:(OUT/'counterexample.json').write_text(json.dumps(dict(number=number,case=[event,previous,count,m,clients,request,now,mode,config,first,second,result],outputs=outputs),indent=2)+'\n');raise AssertionError(number)
   for event_record in outputs[0][1]:hits[event_record[0]]+=1
   obs+=len(outputs[0][1]);digest.update(json.dumps([number,event,previous,count,m,clients,request,now,mode,config,first,second,result,tick,outputs[0]],sort_keys=True).encode())
 assert all(hits[k]>0 for k in KINDS),hits
 receipt=dict(lower_observation_counts=hits,independent_pending_and_contact_mode_fixtures=True,comparisons=len(cases),observations_per_side=obs,trace_sha256=digest.hexdigest(),actual_native_control_and_canonical_state_aliases=True,all_lower_effects_are_fixtures=True,every_event_byte_precedence_and_counter_edges_checked=True,post_effect_mutations_and_fresh_reads_checked=True,timestamp_thresholds_and_packet_length_gates_checked=True,fullword_handle_and_second_fresh_read_checked=True,raw_r0_r1_r2_r3_callee_sp_and_nonstack_ram_checked=True,no_native_candidate_execution=True,portable_planner_modified=False,runtime_admission_changed=False,hardware_write_executed=False,ble_delivery_or_reset_proven=False,full_raw_abi_verified=False,cross_call_private_frame_history_verified=False,instruction_identity=False,whole_image_complete=False,driver_sha256=sha(Path(__file__)),report_sha256=sha(rp),object_sha256=sha(obj),layout_sha256=sha(layout),application_sha256=sha(app))
 (OUT/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
