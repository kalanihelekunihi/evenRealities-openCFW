#!/usr/bin/env python3
"""Client bitfields, event post, and actual command caller; lower effects emulated."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-touch-services-runtime';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();P=0x20003001;CLIENTS=0x200067d8;THREAD=0x2000666c
LOGS={'close_ring':(0x8e708,37),'close_sdk':(0x8e738,31),'open_ring':(0x8e834,36),'open_sdk':(0x8e860,30),'phone_ring':(0x84934,55),'phone_sdk':(0x8496c,49),'glasses_ring':(0x849a0,57),'glasses_sdk':(0x849dc,51)}
def main():
 rp=OUT/'report.json';b=json.loads(rp.read_text());obj=OUT/'touch-services-source.o';assert sha(obj)==b['graph_object_sha256']
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 layout=ROOT/'r1/source-config/runtime/native_touch_services_verification.ld';states={};digest=hashlib.sha256();obs=0;counts={'open':0,'close':0,'post':0,'command':0}
 with tempfile.TemporaryDirectory() as tmp:
  d=Path(tmp);elf=d/'test.elf';subprocess.run(['arm-none-eabi-ld','-T',str(layout),str(obj),'-o',str(elf)],check=True);sections={}
  for n in ['text','clients','thread']+list(LOGS):
   p=d/(n+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j','.'+n,'-O','binary',str(elf),str(p)],check=True);sections[n]=p.read_bytes()
  syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3};assert syms['r1_touch_client_bits']==CLIENTS and syms['r1_touch_task_thread_handle']==THREAD
  for n,(a,z) in LOGS.items():assert sections[n]==raw[a-0x27000:a-0x27000+z]
  cold=(BASE/'native-scatter-data/observed-initialized-data.bin').read_bytes()
  for n,a in [('clients',CLIENTS),('thread',THREAD)]:assert sections[n]==cold[a-0x200064a8:a-0x200064a8+4]==bytes(4)
  def hook(u,a,size,_):
   st=states[id(u)];source=st['source'];assert not source or not 0x27000<=a<0xc4d08
   kind=({0x20000204:'response',0x20000208:'flags',0x2000020c:'release',0x20000210:'mode',0x20000214:'ring',0x20000218:'sdk'} if source else {0x828b4:'response',0x7d6f4:'flags',0x93424:'release',0x914ec:'mode',0x91638:'ring',0x799c8:'sdk'}).get(a)
   if not kind:return
   r=[u.reg_read(x) for x in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];ret=st['result'];m=st['mutation'];clients=struct.unpack('<I',u.mem_read(CLIENTS,4))[0];event=[kind]
   if kind=='response':
    assert r[2:]==[0x2003efe8,1];event+=[r[0],bytes(u.mem_read(r[1],8)).hex(),r[2:],bytes(u.mem_read(r[2],1)).hex()]
    if m==6:u.mem_write(P+12,b'\x02\x00');u.mem_write(r[2],b'\xdd\xcc\xbb\xaa')
   elif kind=='flags':
    event+=r[:2]
    if m==4:u.mem_write(CLIENTS,struct.pack('<I',0x80000000));u.mem_write(THREAD,struct.pack('<I',0x20008888))
   elif kind=='release':
    if m==5:u.mem_write(CLIENTS,struct.pack('<I',3));u.mem_write(THREAD,struct.pack('<I',0x20009999))
   elif kind=='mode':
    ret=st['modes'][st['mi']%len(st['modes'])];st['mi']+=1;event+=[ret]
    if m==1:u.mem_write(CLIENTS,struct.pack('<I',0x80000001 if st['mi']&1 else 0))
   elif kind=='ring':
    assert r[0]==0x0c400000 and r[1]==r[2] and r[1] in [0x8e708,0x8e834,0x84934,0x849a0];event+=[r]
    if m==2:u.mem_write(CLIENTS,bytes(4))
   elif kind=='sdk':
    assert r[0]==0x001c0003 and r[1] in [0x8e738,0x8e860,0x8496c,0x849dc];event+=[r[:3]]
    if m==3:u.mem_write(THREAD,struct.pack('<I',0x20007777));u.mem_write(CLIENTS,struct.pack('<I',3))
   event+=[clients];st['events'].append(event);u.reg_write(UC_ARM_REG_R0,ret)
   for reg,v in [(UC_ARM_REG_R1,0xabcdef01),(UC_ARM_REG_R2,0x12345678),(UC_ARM_REG_R3,0x89abcdef)]:u.reg_write(reg,v)
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  machines=[]
  for source in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,raw);u.mem_map(0x1000000,0x20000);u.mem_write(0x1000000,sections['text']);u.mem_map(0x20000000,0x40000)
   for n,(a,z) in LOGS.items():u.mem_write(a,sections[n])
   u.hook_add(UC_HOOK_CODE,hook);machines.append(u)
  modes=[[0],[1],[2],[4],[7],[0,4,2],[1,0],[0xffffffff,0x80000000]];results=[0,1,0x80000000,0xffffffff];bits=[0,1,2,3,0x80,0x80000000,0x80000001,0xffffffff];cases=[]
  for number,(kind,source,clients,m) in enumerate(itertools.product(['open','close'],list(range(256))+[256,257,287,288,0x10000,0x80000000,0xffffffff],bits,range(6))):cases.append((kind,source,clients,m,modes[number%8],results[(number//8)%4],24,2,1))
  for kind,source,clients,m,mode,result in itertools.product(['open','close'],[0,31,32,256,0xffffffff],bits,range(6),modes,results):cases.append((kind,source,clients,m,mode,result,24,2,1))
  for flags,result,m in itertools.product([0,1,2,4,0xffffffff],results,range(6)):cases.append(('post',flags,0,m,modes[0],result,24,2,1))
  for number,(length,selector,value,clients,m) in enumerate(itertools.product([0,12,13,24,65535],[0,1,2,3],[0,1,255],[0,1,3,0xffffffff],range(7))):cases.append(('command',0,clients,m,modes[number%8],results[(number//8)%4],length,selector,value))
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  for number,(kind,sourcearg,clients,m,mode,result,length,selector,value) in enumerate(cases):
   outputs=[]
   for source,u in enumerate(machines):
    u.mem_write(0x20000000,b'\x96'*0x40000);u.mem_write(CLIENTS,struct.pack('<I',clients));u.mem_write(THREAD,struct.pack('<I',[0,0x20006600][number%2]));u.mem_write(P,bytes(range(64)));u.mem_write(P+8,struct.pack('<H',length));u.mem_write(P+12,bytes([selector,value]));states[id(u)]=dict(source=source,events=[],mutation=m,modes=mode,mi=0,result=result)
    u.reg_write(UC_ARM_REG_XPSR,0x01000000);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    args=[0x1000ffff,P,0x55667788,0x99aabbcc] if kind=='command' else [sourcearg,0x11223344,0x55667788,0x99aabbcc]
    for reg,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],args):u.reg_write(reg,v)
    symbol,address={'open':('r1_service_touch_open',0x8e7d0),'close':('r1_service_touch_close',0x8e6a0),'post':('r1_touch_task_event_post',0x93504),'command':('r1_native_touch_switch_handler',0x84874)}[kind]
    u.emu_start((syms[symbol] if source else address)|1,0x20000100,count=10000);assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
    regs=[u.reg_read(UC_ARM_REG_R0)]
    if kind=='command':regs+=[u.reg_read(reg) for reg in [UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]]
    mem=bytes(u.mem_read(0x20000000,0x3e000))+bytes(u.mem_read(0x2003f000,0x1000));outputs.append([regs,states[id(u)]['events'],hashlib.sha256(mem).hexdigest()])
   if outputs[0]!=outputs[1]:(OUT/'counterexample.json').write_text(json.dumps(dict(number=number,case=[kind,sourcearg,clients,m,mode,result,length,selector,value],outputs=outputs),indent=2)+'\n');raise AssertionError((number,kind))
   counts[kind]+=1;obs+=len(outputs[0][1]);digest.update(json.dumps([number,kind,sourcearg,clients,m,mode,result,length,selector,value,outputs[0]],sort_keys=True).encode())
 receipt=dict(comparisons=sum(counts.values()),counts=counts,observations_per_side=obs,trace_sha256=digest.hexdigest(),actual_touch_services_task_post_and_command_accessor_checked_header=True,only_release_flags_response_logging_are_fixtures=True,all_low8_shift_counts_and_fullword_aliases_checked=True,fresh_client_and_thread_reads_after_effects_checked=True,native_pre_or_open_return_word_checked=True,raw_r0_callee_sp_nonstack_ram_and_caller_r1_r2_r3_checked=True,no_native_candidate_execution=True,portable_planner_modified=False,runtime_admission_changed=False,hardware_write_executed=False,synthetic_release_effect_implemented=False,full_raw_abi_verified=False,cross_call_private_frame_history_verified=False,instruction_identity=False,whole_image_complete=False,driver_sha256=sha(Path(__file__)),report_sha256=sha(rp),object_sha256=sha(obj),layout_sha256=sha(layout),application_sha256=sha(app))
 (OUT/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
