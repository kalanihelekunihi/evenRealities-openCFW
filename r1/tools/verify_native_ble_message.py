#!/usr/bin/env python3
"""Native/source BLE encoder comparisons with actual source memory copy."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-ble-message';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
LOGS=[0x33990,0x339bc,0x339e4,0x33a14,0x33a3c,0x33a64,0x33a88,0x33ab8]
def main():
 rp=BASE/'native-ble-message-runtime/report.json';report=json.loads(rp.read_text());obj=rp.parent/'ble-message-source.o';assert sha(obj)==report['message_object_sha256']
 for p,h in report['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 layout=ROOT/'r1/source-config/runtime/native_ble_message_verification.ld';states={};digest=hashlib.sha256();count=obs=0
 with tempfile.TemporaryDirectory() as tmp:
  d=Path(tmp);elf=d/'test.elf';subprocess.run(['arm-none-eabi-ld','-T',str(layout),str(obj),'-o',str(elf)],check=True)
  sections={}
  for section in ['.text']+['.log'+str(i) for i in range(8)]:
   p=d/(section[1:]+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j',section,'-O','binary',str(elf),str(p)],check=True);sections[section]=p.read_bytes()
  syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
  assert syms['r1_ble_message_queue']==0x20006574 and syms['r1_protocol_service_thread']==0x20006570
  for i,a in enumerate(LOGS):assert sections['.log'+str(i)]==raw[a-0x27000:a-0x27000+len(sections['.log'+str(i)])]
  def word(u,a):return struct.unpack('<I',u.mem_read(a,4))[0]
  def put(u,a,v):u.mem_write(a,struct.pack('<I',v))
  def hook(u,a,size,_):
   st=states[id(u)];source=st['source'];assert not source or not 0x27000<=a<0xc4d08
   kind=({0x20000200:'alloc',0x20000204:'free',0x20000208:'queue',0x2000020c:'flags',0x20000210:'mode',0x20000214:'ring',0x20000218:'sdk'} if source else {0x855a0:'alloc',0x95d48:'free',0x7d40c:'queue',0x7d6f4:'flags',0x914ec:'mode',0x91638:'ring',0x799c0:'sdk'}).get(a)
   if not kind:return
   r=[u.reg_read(x) for x in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];result=st['status'];mutation=st['mutation']
   if kind=='alloc':
    result=st['allocation'];st['events'].append(['alloc',r[0],result])
    if mutation==1:put(u,0x20006574,0x20002004);put(u,0x20006570,0x20002104);u.mem_write(st['payload'] or 0x20003000,b'\x5a'*128)
   elif kind=='queue':
    ptr=word(u,r[1]);st['queue_cell']=r[1];st['events'].append(['queue',r[0],ptr,r[2:],bytes(u.mem_read(ptr,12+st['length'])).hex()]);result=st['queue_status']
    if mutation==2:put(u,r[1],0x20004100);put(u,0x20006570,0x20002108)
    elif mutation==3:put(u,0x20006570,0);put(u,0x20006574,0)
   elif kind=='free':st['events'].append(['free',r[0]])
   elif kind=='flags':st['events'].append(['flags',r[:2]])
   elif kind=='mode':
    result=st['modes'][st['mode_index']%len(st['modes'])];st['mode_index']+=1;st['events'].append(['mode',result])
    if mutation==4 and st['queue_cell']:put(u,st['queue_cell'],0x20004104)
   elif kind in ['ring','sdk']:
    st['events'].append([kind,r[:3] if kind=='ring' else r[:2]])
    if mutation==5 and st['queue_cell']:put(u,st['queue_cell'],0x20004108)
   u.reg_write(UC_ARM_REG_R0,result)
   for reg,v in [(UC_ARM_REG_R1,0xabcdef01),(UC_ARM_REG_R2,0x12345678),(UC_ARM_REG_R3,0x89abcdef)]:u.reg_write(reg,v)
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  machines=[]
  for source in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,raw);u.mem_map(0x1000000,0x20000);u.mem_write(0x1000000,sections['.text']);u.mem_map(0x20000000,0x40000)
   for i,a in enumerate(LOGS):u.mem_write(a,sections['.log'+str(i)])
   u.hook_add(UC_HOOK_CODE,hook);machines.append(u)
  modes=[[0],[1],[2],[4],[7],[0,4,2],[1,0],[0xffffffff,0x80000000]]
  cases=list(itertools.product([0,1,2,3,4,7,12,15,16,31,64,65],[0,0x20003001],[0,0x20002000],[0,0x20004000],[0,1,0xffffffff],modes,range(6)))
  cases += [(n,p,0x20002000,0,0,m,mut) for n,p,m,mut in itertools.product([0xfffffff0,0xfffffff1,0xffffffff],[0,0x20003001],modes,range(6))]
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  for number,(length,payload,queue,allocation,qstatus,mode,mutation) in enumerate(cases):
   results=[];handle=[0,0xffff,0x1000ffff,0xffffffff][number%4];event=[0,2,0x200,0xffffffff][number%4];status=[0,1,0xffffffff,0x80000000][number%4]
   for source,u in enumerate(machines):
    u.mem_write(0x20000000,b'\x96'*0x40000);u.mem_write(0x20003000,bytes(range(128)));put(u,0x20006574,queue);put(u,0x20006570,[0,0x20002100,0xffffffff][number%3]);states[id(u)]=dict(source=source,events=[],length=length,payload=payload,allocation=allocation,queue_status=qstatus,modes=mode,mode_index=0,mutation=mutation,queue_cell=None,status=status)
    u.reg_write(UC_ARM_REG_XPSR,0x01000000);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    for reg,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],[handle,event,length,payload]):u.reg_write(reg,v)
    u.emu_start((syms['r1_ble_thread_message_encode'] if source else 0x33850)|1,0x20000100,count=10000)
    assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
    memory=bytes(u.mem_read(0x20000000,0x3e000))+bytes(u.mem_read(0x2003f000,0x1000));results.append([u.reg_read(UC_ARM_REG_R0),states[id(u)]['events'],hashlib.sha256(memory).hexdigest()])
   if results[0]!=results[1]:(OUT/'counterexample.json').write_text(json.dumps(dict(number=number,case=[length,payload,queue,allocation,qstatus,mode,mutation],results=results),indent=2)+'\n');raise AssertionError((number,length,payload,queue,allocation,qstatus,mode,mutation))
   count+=1;obs+=len(results[0][1]);digest.update(json.dumps([number,length,payload,queue,allocation,qstatus,mode,mutation,results[0]],sort_keys=True).encode())
 receipt=dict(comparisons=count,observations_per_side=obs,trace_sha256=digest.hexdigest(),actual_source_memory_move=True,source_log_texts_match=True,allocation_rounding_and_wrap_checked=True,fresh_queue_thread_and_local_message_reads_checked=True,provider_register_clobbers_checked=True,only_allocation_queue_flags_logging_are_fixtures=True,private_queue_item_pointer_not_compared=True,raw_r0_callee_sp_and_observed_nonstack_ram_checked=True,no_native_candidate_execution=True,driver_sha256=sha(Path(__file__)),runtime_report_sha256=sha(rp),object_sha256=sha(obj),layout_sha256=sha(layout),application_sha256=sha(app),whole_allocator_queue_or_rtos_graph_executed=False,full_raw_abi_verified=False,instruction_identity=False,whole_image_complete=False)
 (OUT/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
