#!/usr/bin/env python3
"""Native touch command plus actual accessor/checked/header; effects are fixtures."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-touch-switch-runtime';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();P=0x20003001;FRAME=0x2003efe0
LOGS={'phone_ring':(0x84934,55),'phone_sdk':(0x8496c,49),'glasses_ring':(0x849a0,57),'glasses_sdk':(0x849dc,51)}
def main():
 rp=OUT/'report.json';b=json.loads(rp.read_text());obj=OUT/'touch-switch-source.o';assert sha(obj)==b['graph_object_sha256']
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 layout=ROOT/'r1/source-config/runtime/native_touch_switch_verification.ld';states={};digest=hashlib.sha256();obs=0;counts={'null':0,'unknown':0,'phone':0,'glasses':0}
 with tempfile.TemporaryDirectory() as tmp:
  d=Path(tmp);elf=d/'test.elf';subprocess.run(['arm-none-eabi-ld','-T',str(layout),str(obj),'-o',str(elf)],check=True);sections={}
  for n in ['text']+list(LOGS):
   p=d/(n+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j','.'+n,'-O','binary',str(elf),str(p)],check=True);sections[n]=p.read_bytes()
  syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
  for n,(a,z) in LOGS.items():assert sections[n]==raw[a-0x27000:a-0x27000+z]
  def hook(u,a,size,_):
   st=states[id(u)];source=st['source'];assert not source or not 0x27000<=a<0xc4d08
   if a==(syms['r1_packet_field12_get'] if source else 0x82bd4):st['after_accessor']=u.reg_read(UC_ARM_REG_LR)&~1
   if st['after_accessor']==a:
    st['after_accessor']=None
    if st['mutation']==1:u.mem_write(P+8,b'\x0c\x00');u.mem_write(P+12,bytes([st['changed'],st['value']]))
   kind=({0x20000204:'response',0x20000208:'open',0x2000020c:'close',0x20000210:'mode',0x20000214:'ring',0x20000218:'sdk'} if source else {0x828b4:'response',0x8e7d0:'open',0x8e6a0:'close',0x914ec:'mode',0x91638:'ring',0x799c8:'sdk'}).get(a)
   if not kind:return
   r=[u.reg_read(x) for x in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];ret=st['result'];m=st['mutation'];event=[kind]
   if kind=='response':
    assert r[2:]==[FRAME+8,1];event+=[r[0],bytes(u.mem_read(r[1],8)).hex(),r[2:],bytes(u.mem_read(r[2],1)).hex()]
    if m==2:u.mem_write(P+12,bytes([st['changed'],st['value']]))
    if m==3:u.mem_write(r[2],struct.pack('<I',0xaabbccdd))
   elif kind in ['open','close']:assert r[0]==0;event+=[r[0]]
   elif kind=='mode':
    ret=st['modes'][st['mi']%len(st['modes'])];st['mi']+=1;event+=[ret]
    if m==4:u.mem_write(P+12,bytes([st['changed'],st['mi']&1]))
   elif kind=='ring':
    assert r[0]==0x0c400000 and r[1]==r[2] and r[1] in [0x84934,0x849a0];event+=[r]
    if m==5:u.mem_write(P+12,bytes([st['changed'],st['value']]))
   elif kind=='sdk':
    assert r[0]==0x001c0003 and r[1] in [0x8496c,0x849dc];event+=[r[:3]]
    if m==6:u.mem_write(P+12,bytes([st['changed'],st['value']]))
   st['events'].append(event);u.reg_write(UC_ARM_REG_R0,ret)
   for reg,v in [(UC_ARM_REG_R1,0xabcdef01),(UC_ARM_REG_R2,0x12345678),(UC_ARM_REG_R3,0x89abcdef)]:u.reg_write(reg,v)
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  machines=[]
  for source in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,raw);u.mem_map(0x1000000,0x20000);u.mem_write(0x1000000,sections['text']);u.mem_map(0x20000000,0x40000)
   for n,(a,z) in LOGS.items():u.mem_write(a,sections[n])
   u.hook_add(UC_HOOK_CODE,hook);machines.append(u)
  modes=[[0],[1],[2],[4],[7],[0,4,2],[1,0],[0xffffffff,0x80000000]];results=[0,1,0x80000000,0xffffffff];handles=[0,65535,0x1000ffff];cases=[]
  for number,(length,selector,m) in enumerate(itertools.product([0,12,13,14,24,65535],range(256),range(7))):cases.append((length,selector,number%256,m,modes[number%8],results[(number//8)%4],handles[(number//32)%3],number%3))
  for selector,value,m,mode,result,handle in itertools.product([1,2],[0,1,2,255],range(7),modes,results,handles):cases.append((24,selector,value,m,mode,result,handle,3-selector))
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  for number,(length,selector,value,m,mode,result,handle,changed) in enumerate(cases):
   outputs=[]
   for source,u in enumerate(machines):
    u.mem_write(0x20000000,b'\x96'*0x40000);u.mem_write(P,bytes(range(64)));u.mem_write(P+8,struct.pack('<H',length));u.mem_write(P+12,bytes([selector,value]));states[id(u)]=dict(source=source,events=[],after_accessor=None,mutation=m,modes=mode,mi=0,result=result,changed=changed,value=value)
    u.reg_write(UC_ARM_REG_XPSR,0x01000000);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    for reg,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],[handle,P,0x55667788,0x99aabbcc]):u.reg_write(reg,v)
    u.emu_start((syms['r1_native_touch_switch_handler'] if source else 0x84874)|1,0x20000100,count=10000);assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
    mem=bytes(u.mem_read(0x20000000,0x3e000))+bytes(u.mem_read(0x2003f000,0x1000));outputs.append([[u.reg_read(reg) for reg in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]],states[id(u)]['events'],hashlib.sha256(mem).hexdigest()])
   if outputs[0]!=outputs[1]:(OUT/'counterexample.json').write_text(json.dumps(dict(number=number,case=[length,selector,value,m,mode,result,handle,changed],outputs=outputs),indent=2)+'\n');raise AssertionError(number)
   kinds=[x[0] for x in outputs[0][1]];kind='null' if length<=12 else 'glasses' if 'open' in kinds or 'close' in kinds else 'phone' if 'mode' in kinds else 'unknown';counts[kind]+=1;obs+=len(kinds);digest.update(json.dumps([number,length,selector,value,m,mode,result,handle,changed,outputs[0]],sort_keys=True).encode())
 receipt=dict(comparisons=sum(counts.values()),counts=counts,observations_per_side=obs,trace_sha256=digest.hexdigest(),actual_accessor_checked_send_and_ack_header=True,only_lower_response_touch_services_and_logging_are_fixtures=True,response_precedes_selector_read=True,fresh_switch_values_after_logs_checked=True,response_mutation_preserves_saved_word=True,raw_r0_r1_r2_r3_callee_sp_nonstack_ram_checked=True,short_backing_only_mapped_fixture=True,no_native_candidate_execution=True,portable_planner_modified=False,runtime_admission_changed=False,touch_service_effects_implemented=False,hardware_write_executed=False,full_raw_abi_verified=False,cross_call_private_frame_history_verified=False,instruction_identity=False,whole_image_complete=False,driver_sha256=sha(Path(__file__)),report_sha256=sha(rp),object_sha256=sha(obj),layout_sha256=sha(layout),application_sha256=sha(app))
 (OUT/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
