#!/usr/bin/env python3
"""Synthetic release, timer callback and actual services; lower effects emulated."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-touch-release-runtime';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();P=0x20003001;CONTACT=0x20016a60;PENDING=0x200067c4;SYNTH=0x200067c6
LOGS={'close_ring':(0x8e708,37),'close_sdk':(0x8e738,31),'open_ring':(0x8e834,36),'open_sdk':(0x8e860,30),'phone_ring':(0x84934,55),'phone_sdk':(0x8496c,49),'glasses_ring':(0x849a0,57),'glasses_sdk':(0x849dc,51)}
def main():
 rp=OUT/'report.json';b=json.loads(rp.read_text());obj=OUT/'touch-release-source.o';assert sha(obj)==b['graph_object_sha256']
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 layout=ROOT/'r1/source-config/runtime/native_touch_release_verification.ld';states={};digest=hashlib.sha256();obs=0;counts={'release':0,'all_pairs':0,'timer':0,'close':0,'command':0}
 with tempfile.TemporaryDirectory() as tmp:
  d=Path(tmp);elf=d/'test.elf';subprocess.run(['arm-none-eabi-ld','-T',str(layout),str(obj),'-o',str(elf)],check=True);sections={}
  for n in ['text','timer_code','contact','pending','synthetic','clients','thread']+list(LOGS):
   p=d/(n+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j','.'+n,'-O','binary',str(elf),str(p)],check=True);sections[n]=p.read_bytes()
  syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3};assert syms['r1_touch_release_timer_callback']==0x934e4 and syms['r1_touch_contact_state']==CONTACT and syms['r1_touch_release_timer_pending']==PENDING and syms['r1_touch_synthetic_flag']==SYNTH
  assert len(sections['timer_code'])==14 and sections['contact']==bytes(100)
  for n,(a,z) in LOGS.items():assert sections[n]==raw[a-0x27000:a-0x27000+z]
  def hook(u,a,size,_):
   st=states[id(u)];source=st['source'];assert not source or not 0x27000<=a<0xc4d08 or 0x934e4<=a<0x934e4+len(sections['timer_code'])
   if a==(syms['__aeabi_memclr'] if source else 0x277aa):
    ptr=u.reg_read(UC_ARM_REG_R0);length=u.reg_read(UC_ARM_REG_R1);assert length in [44,100];st['events'].append(['actual_clear',length,bytes(u.mem_read(ptr,length)).hex()])
   kind=({0x20000204:'response',0x20000208:'flags',0x2000020c:'cancel',0x20000210:'mode',0x20000214:'ring',0x20000218:'sdk',0x2000021c:'gesture',0x20000220:'message'} if source else {0x828b4:'response',0x7d6f4:'flags',0x65d64:'cancel',0x914ec:'mode',0x91638:'ring',0x799c8:'sdk',0x3e938:'gesture',0x93514:'message'}).get(a)
   if not kind:return
   r=[u.reg_read(x) for x in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];ret=st['result'];m=st['mutation'];event=[kind]
   if kind=='cancel':
    assert r[:2]==[0x934e5,0];event+=r[:2]
    if m==1:u.mem_write(CONTACT+8,b'\x01');u.mem_write(CONTACT+36,b'\x00\x00');u.mem_write(CONTACT+60,b'\xff');u.mem_write(PENDING,b'\xff')
   elif kind=='gesture':
    if st['kind'] in ['release','all_pairs']:assert r[0] in [0x2003efe0,0x2003efe4]
    event+=[bytes(u.mem_read(r[0],4)).hex(),bytes(u.mem_read(SYNTH,1)).hex()]
    if m==2:u.mem_write(CONTACT,bytes([0x77])*100);u.mem_write(PENDING,b'\x01');u.mem_write(SYNTH,b'\xff')
    if m==3:u.mem_write(r[0],b'\xdd\xcc\xbb\xaa')
   elif kind=='message':
    assert r[0]==0x2003efd0;event+=[bytes(u.mem_read(r[0],44)).hex()]
    if m==4:u.mem_write(CONTACT+36,b'\xff');u.mem_write(PENDING,b'\x02')
   elif kind=='response':event+=[r[0],bytes(u.mem_read(r[1],8)).hex(),r[3],bytes(u.mem_read(r[2],r[3])).hex()]
   elif kind=='flags':event+=r[:2]
   elif kind=='mode':ret=st['modes'][st['mi']%len(st['modes'])];st['mi']+=1;event+=[ret]
   elif kind=='ring':event+=[r]
   elif kind=='sdk':event+=[r[:3]]
   st['events'].append(event);u.reg_write(UC_ARM_REG_R0,ret)
   for reg,v in [(UC_ARM_REG_R1,0xabcdef01),(UC_ARM_REG_R2,0x12345678),(UC_ARM_REG_R3,0x89abcdef)]:u.reg_write(reg,v)
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  machines=[]
  for source in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,raw);u.mem_map(0x1000000,0x20000);u.mem_write(0x1000000,sections['text']);u.mem_map(0x20000000,0x40000)
   if source:u.mem_write(0x934e4,sections['timer_code'])
   for n,(a,z) in LOGS.items():u.mem_write(a,sections[n])
   u.hook_add(UC_HOOK_CODE,hook);machines.append(u)
  modes=[[0],[1],[2],[4],[7],[0,4,2]];results=[0,1,0xffffffff,0x80000000];cases=[]
  for number,(active,slide,pending,velocity,last,m) in enumerate(itertools.product([0,1,2,255],[0,1,2],[0,1,255],[0,1,255],[0,127,128,255],range(5))):cases.append(('release',active,slide,pending,0,0,velocity,last,m,modes[number%6],results[number%4]))
  for first,second in itertools.product(range(256),repeat=2):cases.append(('all_pairs',1,1,0,first,second,[0,1,255][first%3],[0,128][second%2],0,modes[0],0))
  for kind,active,slide,pending,mode,m,result in itertools.product(['close','command'],[0,1,2],[0,1],[0,1],modes,range(5),results):cases.append((kind,active,slide,pending,255,0,0,255,m,mode,result))
  for argument,result,m in itertools.product([0,1,255,0xffffffff],results,range(5)):cases.append(('timer',argument,0,0,0,0,0,0,m,modes[0],result))
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  for number,(kind,active,slide,pending,first,second,velocity,last,m,mode,result) in enumerate(cases):
   outputs=[]
   for source,u in enumerate(machines):
    u.mem_write(0x20000000,b'\x96'*0x40000);u.mem_write(CONTACT,bytes((i*7)&255 for i in range(100)));u.mem_write(CONTACT+8,bytes([slide]));u.mem_write(CONTACT+36,bytes([active&255,first]));u.mem_write(CONTACT+60,bytes([second]));u.mem_write(CONTACT+95,bytes([velocity,last]));u.mem_write(PENDING,bytes([pending]));u.mem_write(SYNTH,bytes([number%3]));u.mem_write(0x200067d8,struct.pack('<I',1));u.mem_write(0x2000666c,struct.pack('<I',0x20008000));u.mem_write(P,bytes(range(64)));u.mem_write(P+8,b'\x18\x00');u.mem_write(P+12,b'\x02\x00');states[id(u)]=dict(source=source,kind=kind,events=[],mutation=m,modes=mode,mi=0,result=result)
    u.reg_write(UC_ARM_REG_XPSR,0x01000000);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    args=[0x1000ffff,P,0x55667788,0x99aabbcc] if kind=='command' else [active if kind=='timer' else 0,0x11223344,0x55667788,0x99aabbcc]
    for reg,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],args):u.reg_write(reg,v)
    symbol,address={'release':('r1_touch_synthetic_release_boundary',0x93424),'all_pairs':('r1_touch_synthetic_release_boundary',0x93424),'timer':('r1_touch_release_timer_callback',0x934e4),'close':('r1_service_touch_close',0x8e6a0),'command':('r1_native_touch_switch_handler',0x84874)}[kind]
    u.emu_start((syms[symbol] if source else address)|1,0x20000100,count=20000);assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
    regs=[u.reg_read(UC_ARM_REG_R0)]
    if kind=='command':regs+=[u.reg_read(reg) for reg in [UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]]
    mem=bytes(u.mem_read(0x20000000,0x3e000))+bytes(u.mem_read(0x2003f000,0x1000));outputs.append([regs,states[id(u)]['events'],hashlib.sha256(mem).hexdigest()])
   if outputs[0]!=outputs[1]:(OUT/'counterexample.json').write_text(json.dumps(dict(number=number,case=[kind,active,slide,pending,first,second,velocity,last,m,mode,result],outputs=outputs),indent=2)+'\n');raise AssertionError((number,kind))
   counts[kind]+=1;obs+=len(outputs[0][1]);digest.update(json.dumps([number,kind,active,slide,pending,first,second,velocity,last,m,mode,result,outputs[0]],sort_keys=True).encode())
 receipt=dict(comparisons=sum(counts.values()),counts=counts,observations_per_side=obs,trace_sha256=digest.hexdigest(),actual_release_callback_clear_services_and_command_graph=True,all_coordinate_byte_pairs_checked=True,only_cancel_gesture_message_flags_response_logging_are_fixtures=True,actual_attributed_clear_with_native_end_pointer_result=True,callback_source14bytes_at_native_verification_vma=True,caller_gesture_private_pointer_values_not_compared=True,raw_r0_callee_sp_nonstack_ram_and_command_r1_r2_r3_checked=True,portable_planner_modified=False,runtime_admission_changed=False,hardware_write_executed=False,gesture_and_task_message_effects_implemented=False,full_raw_abi_verified=False,cross_call_private_frame_history_verified=False,instruction_identity=False,whole_image_complete=False,driver_sha256=sha(Path(__file__)),report_sha256=sha(rp),object_sha256=sha(obj),layout_sha256=sha(layout),application_sha256=sha(app))
 (OUT/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
