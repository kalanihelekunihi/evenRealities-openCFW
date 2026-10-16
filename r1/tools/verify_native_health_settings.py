#!/usr/bin/env python3
"""Health settings with actual flag/word helpers, KV and musl; lower effects emulated."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-health-settings-runtime';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();P=0x20003001;NODE=0x200069a8;ALT=0x20001000;FRAME=0x2003efc0
CLASSES=[('devinfo',NODE),('ble_mult',0x200069f4),('health',0x20006a68),('hsync',0x20006a8c),('power',0x20006abc),('serial',0x20006ad8),('r_size',0x20006b6c)]
LOGS={'get_ring':(0x84058,61),'get_sdk':(0x84098,55),'set_ring':(0x840d0,49),'set_sdk':(0x84104,43)}
def main():
 rp=OUT/'report.json';b=json.loads(rp.read_text());obj=OUT/'health-settings-source.o';assert sha(obj)==b['graph_object_sha256']
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 layout=ROOT/'r1/source-config/runtime/native_health_settings_verification.ld';states={};digest=hashlib.sha256();obs=0;counts={'handler':0,'get':0,'set':0};hits={k:0 for k in ['event','read','write','idle','checked','ack','mode','ring','sdk_get','sdk_set','enter','leave','leave2']}
 with tempfile.TemporaryDirectory() as tmp:
  d=Path(tmp);elf=d/'test.elf';subprocess.run(['arm-none-eabi-ld','-T',str(layout),str(obj),'-o',str(elf)],check=True);sections={}
  for n in ['text','handles','port']+[n for n,a in CLASSES]+list(LOGS):
   p=d/(n+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j','.'+n,'-O','binary',str(elf),str(p)],check=True);sections[n]=p.read_bytes()
  syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
  for n,(a,z) in LOGS.items():assert sections[n]==raw[a-0x27000:a-0x27000+z]
  def hook(u,a,size,_):
   st=states[id(u)];source=st['source'];assert not source or not 0x27000<=a<0xc4d08
   for name,native,kind in [('r1_kv_class_read',0x73930,'read'),('r1_kv_class_write',0x73968,'write')]:
    if a==(syms[name] if source else native):
     node=u.reg_read(UC_ARM_REG_R0);pointer=u.reg_read(UC_ARM_REG_R1);length=u.reg_read(UC_ARM_REG_R2);assert length==52
     if st['kind']!='handler':assert pointer==(0x2003efb8 if st['kind']=='set' else 0x2003efc0)
     event=[kind,node,length]
     if kind=='write':event+=[bytes(u.mem_read(pointer,length)).hex()]
     st['events'].append(event);return
   kind=({0x20000204:'idle',0x20000208:'checked',0x2000020c:'ack',0x20000210:'mode',0x20000214:'ring',0x20000218:'sdk_get',0x2000021c:'sdk_set',0x20000220:'enter',0x20000224:'leave',0x20000228:'leave2',0x2000022c:'event'} if source else {0x73688:'idle',0x84c5e:'checked',0x8287c:'ack',0x914ec:'mode',0x91638:'ring',0x799d6:'sdk_get',0x799f8:'sdk_set',0x20000220:'enter',0x20000224:'leave',0x20000228:'leave2',0x8d8fc:'event'}).get(a)
   if not kind:return
   r=[u.reg_read(x) for x in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];ret=st['result'];m=st['mutation'];event=[kind]
   if kind=='checked':
    extra=list(struct.unpack('<II',u.mem_read(u.reg_read(UC_ARM_REG_SP),8)));assert r[:3]==[0x1000ffff,14,0] and extra==[FRAME+24,12];event+=[r,bytes(u.mem_read(extra[0],12)).hex()]
   elif kind=='ack':
    extra=struct.unpack('<I',u.mem_read(u.reg_read(UC_ARM_REG_SP),4))[0];assert r[:3]==[0x1000ffff,14,1] and extra==0;event+=[r,extra]
    if m==4:u.mem_write(P+8,b'\x0c\x00')
   elif kind=='mode':
    ret=st['modes'][st['mi']%len(st['modes'])];st['mi']+=1;event+=[ret]
    if m==1:u.mem_write(P+16,b'\x02');u.mem_write(P+12,b'\x78\x56\x34\x12');u.mem_write(P+3,b'\x78\x56')
   elif kind=='ring':
    assert r[1]==r[2] and r[1] in [0x84058,0x840d0];event+=[r]
    words=1 if r[1]==0x84058 else 3;event+=[list(struct.unpack('<'+'I'*words,u.mem_read(u.reg_read(UC_ARM_REG_SP),4*words)))]
    if m==2:u.mem_write(P+16,b'\xff');u.mem_write(FRAME+(12 if st['set_mode'] else 8),b'\x07')
   elif kind=='sdk_get':event+=[r]
   elif kind=='sdk_set':event+=[r,list(struct.unpack('<II',u.mem_read(u.reg_read(UC_ARM_REG_SP),8)))]
   elif kind=='event':
    assert r[:3]==[0x100d,P+16,1];event+=[r[:3],bytes(u.mem_read(r[1],1)).hex()]
   if m==3 and kind in ['sdk_get','sdk_set']:u.mem_write(P+16,b'\x00');u.mem_write(FRAME+28,b'\xfe')
   if m==5 and kind=='enter':u.mem_write(0x20007de8,struct.pack('<I',ALT));u.mem_write(NODE+48,b'\x03')
   if m==6 and kind=='enter':u.mem_write(0x20006974,struct.pack('<I',0x20000880))
   if m==6 and kind=='idle':u.mem_write(P+16,b'\x00' if st['requested'] else b'\x01')
   st['events'].append(event);u.reg_write(UC_ARM_REG_R0,ret)
   for reg,v in [(UC_ARM_REG_R1,0xabcdef01),(UC_ARM_REG_R2,0x12345678),(UC_ARM_REG_R3,0x89abcdef)]:u.reg_write(reg,v)
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  machines=[]
  for source in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,raw);u.mem_map(0x1000000,0x20000);u.mem_write(0x1000000,sections['text']);u.mem_map(0x20000000,0x40000)
   for n,(a,z) in LOGS.items():u.mem_write(a,sections[n])
   u.hook_add(UC_HOOK_CODE,hook);machines.append(u)
  modes=[[0],[1],[2],[4],[7],[0,4,2],[1,0],[0xffffffff,0x80000000]];results=[0,1,0xffffffff,0x80000000];cases=[]
  for number,(value,header,type_,requested,m) in enumerate(itertools.product([0,1,2,3,127,128,254,255],[0,2],[0,1,255],[0,1,2,255],range(7))):cases.append(('handler',value,52,header,type_,requested,m,modes[number%8],results[(number//8)%4],0x20002001,24))
  for number,(header,value,mode,result,m) in enumerate(itertools.product([0,1,2,3,255],[0,1,2,3,127,128,254,255],modes,results,range(7))):cases.append(('handler',value,52,header,0,number%256,m,mode,result,0x20002001,[0,12,13,18,24,65535][number%6]))
  for number,(destination,value,size,m) in enumerate(itertools.product([0,0x20002001,NODE+24],range(256),[0,51,52,53],range(3))):cases.append(('get',value,size,0,0,0,m,modes[0],0xffffffff,destination,24))
  for number,(requested,value,size,m,result) in enumerate(itertools.product([0,1,2,255,0x80000000,0xffffffff],[0,1,2,255],[0,51,52,53],range(4),results)):cases.append(('set',value,size,0,0,requested,m,modes[0],result,0x20002001,24))
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  for number,(kind,value,size,header,type_,requested,m,mode,result,destination,length) in enumerate(cases):
   outputs=[];word=[0,1,0xffffffff,0x80000000,0x12345678][(number//3)%5];word_destination=[0,0x20002001,NODE+32][number%3]
   for source,u in enumerate(machines):
    u.mem_write(0x20000000,b'\x96'*0x40000)
    for n,a in CLASSES:u.mem_write(a,sections[n])
    u.mem_write(0x20007de8,sections['handles']);u.mem_write(ALT,sections['devinfo']);u.mem_write(NODE+20,struct.pack('<H',size));u.mem_write(NODE+48,bytes([value]));u.mem_write(NODE+56,struct.pack('<I',0xaabbcc00|value));u.mem_write(ALT+48,b'\x55');u.mem_write(ALT+56,struct.pack('<I',0x11223344));u.mem_write(0x20006974,struct.pack('<I',0x20000800));u.mem_write(0x20000800+28,struct.pack('<II',0x20000221,0x20000225));u.mem_write(0x20000880+28,struct.pack('<II',0x20000221,0x20000229));u.mem_write(P,bytes(range(64)));u.mem_write(P+5,bytes([header]));u.mem_write(P+8,struct.pack('<H',length));u.mem_write(P+12,struct.pack('<I',word));u.mem_write(P+16,bytes([requested&255]));states[id(u)]=dict(source=source,kind=kind,events=[],mutation=m,modes=mode,mi=0,result=result,requested=requested,set_mode=bool(header&2))
    u.reg_write(UC_ARM_REG_XPSR,0x01000000);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    args=[0x1000ffff,P,0x55667788,0x99aabbcc] if kind=='handler' else [destination if kind=='get' else requested,word_destination if kind=='get' else word,0x55667788,0x99aabbcc]
    for reg,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],args):u.reg_write(reg,v)
    symbol,address={'handler':('r1_native_health_settings_handler',0x83f24),'get':('r1_kv_dev_info_flag_word_get',0x73798),'set':('r1_kv_dev_info_flag0_word_set',0x73868)}[kind]
    u.emu_start((syms[symbol] if source else address)|1,0x20000100,count=20000);assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
    mem=bytes(u.mem_read(0x20000000,0x3e000))+bytes(u.mem_read(0x2003f000,0x1000));outputs.append([u.reg_read(UC_ARM_REG_R0),states[id(u)]['events'],hashlib.sha256(mem).hexdigest()])
   if outputs[0]!=outputs[1]:(OUT/'counterexample.json').write_text(json.dumps(dict(number=number,case=[kind,value,size,header,type_,requested,m,mode,result,destination,length],outputs=outputs),indent=2)+'\n');raise AssertionError((number,kind))
   counts[kind]+=1
   for event_record in outputs[0][1]:hits[event_record[0]]+=1
   obs+=len(outputs[0][1]);digest.update(json.dumps([number,kind,value,size,header,type_,requested,m,mode,result,destination,length,outputs[0]],sort_keys=True).encode())
 assert all(hits.values()),hits
 receipt=dict(comparisons=sum(counts.values()),counts=counts,lower_observation_counts=hits,observations_per_side=obs,trace_sha256=digest.hexdigest(),actual_handler_flag_word_helpers_kv_musl_accessor=True,event_idle_transport_logging_critical_are_fixtures=True,handler_workflows_use_successful_cached_reads=True,direct_helper_failed_read_seed_views_checked=True,accessor_before_ack_and_raw_requested_comparison_checked=True,live_event_status_after_setter_and_conditional_timestamp_checked=True,raw_r0_callee_sp_nonstack_ram_checked=True,no_native_candidate_execution=True,portable_planner_modified=False,runtime_admission_changed=False,hardware_write_executed=False,health_event_delivery_or_persistence_proven=False,full_raw_abi_verified=False,cross_call_private_frame_history_verified=False,instruction_identity=False,whole_image_complete=False,driver_sha256=sha(Path(__file__)),report_sha256=sha(rp),object_sha256=sha(obj),layout_sha256=sha(layout),application_sha256=sha(app))
 (OUT/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
