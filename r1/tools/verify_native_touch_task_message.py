#!/usr/bin/env python3
"""Shared task sender plus actual timer/clear; RTOS and logging are fixtures."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-touch-task-message-runtime';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();QUEUE=0x20006670;THREAD=0x2000666c
LOGS={'null_ring':(0x935b8,42),'null_sdk':(0x935e4,36),'missed_ring':(0x93608,17),'missed_sdk':(0x9361c,11)}
def main():
 rp=OUT/'report.json';b=json.loads(rp.read_text());obj=OUT/'touch-task-message-source.o';assert sha(obj)==b['graph_object_sha256']
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 layout=ROOT/'r1/source-config/runtime/native_touch_task_message_verification.ld';states={};digest=hashlib.sha256();obs=0;counts={'sender':0,'timer':0,'workflow':0}
 with tempfile.TemporaryDirectory() as tmp:
  d=Path(tmp);elf=d/'test.elf';subprocess.run(['arm-none-eabi-ld','-T',str(layout),str(obj),'-o',str(elf)],check=True);sections={}
  for n in ['text','timer_code','queue','thread']+list(LOGS):
   p=d/(n+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j','.'+n,'-O','binary',str(elf),str(p)],check=True);sections[n]=p.read_bytes()
  syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3};assert syms['r1_touch_release_timer_callback']==0x934e4 and len(sections['timer_code'])==14 and syms['r1_touch_task_message_queue']==QUEUE and syms['r1_touch_task_thread_handle']==THREAD
  for n,(a,z) in LOGS.items():assert sections[n]==raw[a-0x27000:a-0x27000+z]
  cold=(BASE/'native-scatter-data/observed-initialized-data.bin').read_bytes()
  for n,a in [('queue',QUEUE),('thread',THREAD)]:assert sections[n]==cold[a-0x200064a8:a-0x200064a8+4]==bytes(4)
  def hook(u,a,size,_):
   st=states[id(u)];source=st['source'];assert not source or not 0x27000<=a<0xc4d08 or 0x934e4<=a<0x934f2
   if a==(syms['__aeabi_memclr'] if source else 0x277aa):
    assert u.reg_read(UC_ARM_REG_R0)==0x2003efd0 and u.reg_read(UC_ARM_REG_R1)==44;st['events'].append(['actual_clear',44])
   kind=({0x20000204:'put',0x20000208:'flags',0x2000020c:'mode',0x20000210:'ring',0x20000214:'sdk'} if source else {0x7d40c:'put',0x7d6f4:'flags',0x914ec:'mode',0x91638:'ring',0x799c0:'sdk'}).get(a)
   if not kind:return
   r=[u.reg_read(x) for x in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];m=st['mutation'];ret=st['put_result'];event=[kind]
   if kind=='put':
    assert r[2:]==[0,0];event+=[r,bytes(u.mem_read(r[1],44)).hex() if r[1] else None]
    if st['kind']=='timer':assert r[1]==0x2003efd0 and bytes(u.mem_read(r[1],44))==bytes(4)+b'\x05\x00\x00\x00'+bytes(36)
    if m==1:u.mem_write(QUEUE,bytes(4));u.mem_write(THREAD,struct.pack('<I',0x20009999))
    if m==2 and r[1]:u.mem_write(r[1],b'\xdd\xcc\xbb\xaa')
   elif kind=='flags':
    assert r[1]==0x400000;event+=r[:2];ret=st['flag_result']
    if m==3:u.mem_write(QUEUE,bytes(4));u.mem_write(THREAD,struct.pack('<I',0x20008888))
   elif kind=='mode':
    ret=st['modes'][st['mi']%len(st['modes'])];st['mi']+=1;event+=[ret]
    if m==4:u.mem_write(QUEUE,struct.pack('<I',0x20007777));u.mem_write(THREAD,struct.pack('<I',0x20006666))
   elif kind=='ring':
    assert r[0]==0x04000000 and r[1]==r[2] and r[1] in [0x935b8,0x93608];event+=r[:3]
    if m==5:u.mem_write(QUEUE,struct.pack('<I',0x20005555))
   elif kind=='sdk':assert r[0]==0x001c0001 and r[1] in [0x935e4,0x9361c];event+=r[:2]
   st['events'].append(event);u.reg_write(UC_ARM_REG_R0,ret)
   for reg,v in [(UC_ARM_REG_R1,0xabcdef01),(UC_ARM_REG_R2,0x12345678),(UC_ARM_REG_R3,0x89abcdef)]:u.reg_write(reg,v)
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  machines=[]
  for source in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,raw);u.mem_map(0x1000000,0x20000);u.mem_write(0x1000000,sections['text']);u.mem_map(0x20000000,0x40000)
   if source:u.mem_write(0x934e4,sections['timer_code'])
   for n,(a,z) in LOGS.items():u.mem_write(a,sections[n])
   u.hook_add(UC_HOOK_CODE,hook);machines.append(u)
  modes=[[0],[1],[2],[4],[7],[0,4,2],[1,0],[0xffffffff,0x80000000]];results=[0,1,0xffffffff,0x80000000];cases=[]
  for message,queue,thread,put_result,flag_result,mode,m in itertools.product([0,0x20002000,0x20002001],[0,0x20008000],[0,0x20009000],results,results,modes,range(6)):cases.append(('sender',message,queue,thread,put_result,flag_result,mode,m))
  for queue,thread,put_result,flag_result,mode,m in itertools.product([0,0x20008000],[0,0x20009000],results,results,modes,range(6)):cases.append(('timer',0,queue,thread,put_result,flag_result,mode,m))
  for queue,put_result,mode,m in itertools.product([0,0x20008000],results,modes,range(6)):cases.append(('workflow',0x20002001,queue,0x20009000,put_result,0xffffffff,mode,m))
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  for number,(kind,message,queue,thread,put_result,flag_result,mode,m) in enumerate(cases):
   outputs=[]
   for source,u in enumerate(machines):
    u.mem_write(0x20000000,b'\x96'*0x40000);u.mem_write(QUEUE,struct.pack('<I',queue));u.mem_write(THREAD,struct.pack('<I',thread));u.mem_write(0x20002000,bytes(range(64)));states[id(u)]=dict(source=source,kind=kind,events=[],mutation=m,modes=mode,mi=0,put_result=put_result,flag_result=flag_result);regs=[]
    for iteration in range(2 if kind=='workflow' else 1):
     u.reg_write(UC_ARM_REG_XPSR,0x01000000);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
     for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
     for reg,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],[message,0x11223344,0x55667788,0x99aabbcc]):u.reg_write(reg,v)
     target=(syms['r1_touch_release_timer_callback'] if source else 0x934e4) if kind=='timer' else (syms['r1_touch_task_message_boundary'] if source else 0x93514)
     u.emu_start(target|1,0x20000100,count=10000);assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)];regs.append(u.reg_read(UC_ARM_REG_R0))
    mem=bytes(u.mem_read(0x20000000,0x3e000))+bytes(u.mem_read(0x2003f000,0x1000));outputs.append([regs,states[id(u)]['events'],hashlib.sha256(mem).hexdigest()])
   if outputs[0]!=outputs[1]:(OUT/'counterexample.json').write_text(json.dumps(dict(number=number,case=[kind,message,queue,thread,put_result,flag_result,mode,m],outputs=outputs),indent=2)+'\n');raise AssertionError((number,kind))
   counts[kind]+=1;obs+=len(outputs[0][1]);digest.update(json.dumps([number,kind,message,queue,thread,put_result,flag_result,mode,m,outputs[0]],sort_keys=True).encode())
 receipt=dict(comparisons=sum(counts.values()),counts=counts,observations_per_side=obs,trace_sha256=digest.hexdigest(),actual_sender_timer_callback_and_attributed_clear=True,only_queue_flags_logging_are_fixtures=True,null_message_only_controlled_queue_boundary_fixture=True,fresh_thread_after_put_and_boolean_result_checked=True,two_call_queue_mutation_workflows_checked=True,callback_source14bytes_at_native_verification_vma=True,raw_r0_callee_sp_and_nonstack_ram_checked=True,portable_planner_modified=False,runtime_admission_changed=False,hardware_write_executed=False,rtos_delivery_proven=False,shared_task_context_complete=False,full_raw_abi_verified=False,cross_call_private_frame_history_verified=False,instruction_identity=False,whole_image_complete=False,driver_sha256=sha(Path(__file__)),report_sha256=sha(rp),object_sha256=sha(obj),layout_sha256=sha(layout),application_sha256=sha(app))
 (OUT/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
