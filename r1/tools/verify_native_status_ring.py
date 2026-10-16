#!/usr/bin/env python3
"""Native status ring and getters with raw event result and callback mutation coverage."""
import hashlib,itertools,json,random,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-status-ring';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ENTRIES={'publish':('r1_status_record_ring_publish',0x5e118),'device':('r1_device_state_byte_2d_get',0x91264),'peers':('r1_peer_channel_count',0x4cb08),'charge':('r1_charge_state_byte_get',0x91270)}
def main():
 rp=BASE/'native-status-ring-runtime/report.json';b=json.loads(rp.read_text());obj=rp.parent/'status-ring-source.o';assert sha(obj)==b['status_object_sha256']
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 layout=ROOT/'r1/source-config/runtime/native_status_ring_verification.ld';states={};digest=hashlib.sha256();counts={n:0 for n in ENTRIES};obs=0;rng=random.Random(0x5e118)
 with tempfile.TemporaryDirectory() as tmp:
  d=Path(tmp);elf=d/'test.elf';subprocess.run(['arm-none-eabi-ld','-T',str(layout),str(obj),'-o',str(elf)],check=True);p=d/'text.bin';subprocess.run(['arm-none-eabi-objcopy','-j','.text','-O','binary',str(elf),str(p)],check=True);text=p.read_bytes();syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
  def ring(u):return bytes(u.mem_read(0x20006938,8)).hex()
  def mutate(u,m):
   if m==1:u.mem_write(0x20006938,b'\x00\x0f');u.mem_write(0x2000693c,b'\xff\xff')
   elif m==2:u.mem_write(0x20006938,b'\x03\x07');u.mem_write(0x2000693c,b'\xfe\xff')
   elif m==3:u.mem_write(0x20006938,b'\x00\xff')
  def hook(u,a,size,_):
   st=states[id(u)];source=st['source'];assert not source or not 0x27000<=a<0xc4d08
   kind=({0x20000200:'configuration',0x20000204:'update',0x20000208:'time',0x2000020c:'enter',0x20000210:'exit',0x20000214:'event'} if source else {0x7ba24:'configuration',0x31fd0:'update',0x8ad40:'time',0x95cf4:'enter',0x95d24:'exit',0x8d8fc:'event'}).get(a)
   if not kind:return
   regs=[u.reg_read(x) for x in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];ret=st['status'];m=st['mutation']
   if kind=='configuration':
    ret=st['configuration'];st['events'].append(['configuration',ret]);
    if m==4:u.mem_write(0x20016bb0,b'\x55\xaa')
   elif kind=='update':
    st['events'].append(['update',st['updated']]);u.mem_write(0x20016bb0,bytes([st['updated']]))
    if m==5:u.mem_write(0x200064ba,b'\xff\xff\xff\xff');u.mem_write(0x20016bb1,b'\xfe')
   elif kind=='time':
    ret=st['timestamp'];st['events'].append(['time',ret]);
    if m in [1,2,3]:mutate(u,m)
   elif kind=='enter':
    st['events'].append(['enter',ring(u)])
    if m==6:mutate(u,1)
    elif m==7:mutate(u,2)
   elif kind=='exit':
    st['events'].append(['exit',ring(u)])
    if m==8:mutate(u,3)
   else:st['events'].append(['event',regs[:3],ring(u)])
   u.reg_write(UC_ARM_REG_R0,ret)
   for reg,v in [(UC_ARM_REG_R1,0xabcdef01),(UC_ARM_REG_R2,0x12345678),(UC_ARM_REG_R3,0x89abcdef)]:u.reg_write(reg,v)
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  machines=[]
  for source in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,raw);u.mem_map(0x1000000,0x20000);u.mem_write(0x1000000,text);u.mem_map(0x20000000,0x40000);u.hook_add(UC_HOOK_CODE,hook);machines.append(u)
  cases=[];vals=[0,1,3,7,63,64,127,255,256,0xffffffff]
  for args,m in itertools.product(itertools.product(vals,repeat=4),range(3)):cases.append(('publish',args,m))
  for rd,wr,m in itertools.product([0,1,15,16,255],[0,1,15,16,255],range(9)):cases.append(('publish',(0xffffffff,0xffffffff,0xffffffff,0xffffffff),m,rd,wr))
  for m in range(9):cases.append(('publish',(1,1,0,1),m))
  for charge,configuration,updated in itertools.product(range(256),[0,0x55,0xffffff55,0xffffffff],[0,85,255]):cases.append(('charge',(),0,0,0,charge,configuration,updated))
  for val in range(256):cases.append(('device',(),0,0,0,0,0,0,val))
  for phone,glasses in itertools.product([0,1,0xfffe,0xffff],repeat=2):cases.append(('peers',(),0,0,0,0,0,0,0,phone,glasses))
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  for number,case in enumerate(cases):
   kind,args,m=case[:3];rd=case[3] if len(case)>3 else number%16;wr=case[4] if len(case)>4 else (number//16)%16;charge=case[5] if len(case)>5 else vals[number%10]&255;configuration=case[6] if len(case)>6 else [0,0x55,0xffffff55][number%3];updated=case[7] if len(case)>7 else vals[(number//7)%10]&255;device=case[8] if len(case)>8 else vals[(number//9)%10]&255;phone=case[9] if len(case)>9 else [0,1,65535][number%3];glasses=case[10] if len(case)>10 else [0,65535][number%2];status=[0,1,0xffffffff,0x80000000,0x12345678][number%5];timestamp=rng.getrandbits(32);dropped=[0,0xfffe,0xffff][number%3];results=[]
   for source,u in enumerate(machines):
    u.mem_write(0x20000000,b'\x96'*0x40000);u.mem_write(0x20006938,bytes([rd,wr,0xa5,0x5a])+struct.pack('<H',dropped)+b'\x96\x69');u.mem_write(0x20016bb0,bytes([charge,device]));u.mem_write(0x200064ba,struct.pack('<HH',phone,glasses));states[id(u)]=dict(source=source,events=[],status=status,configuration=configuration,updated=updated,timestamp=timestamp,mutation=m)
    u.reg_write(UC_ARM_REG_XPSR,0x01000000);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    for reg,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],list(args)+[0x11223344]*4):u.reg_write(reg,v)
    u.emu_start((syms[ENTRIES[kind][0]] if source else ENTRIES[kind][1])|1,0x20000100,count=10000);assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
    memory=bytes(u.mem_read(0x20000000,0x3e000))+bytes(u.mem_read(0x2003f000,0x1000));results.append([u.reg_read(UC_ARM_REG_R0),states[id(u)]['events'],hashlib.sha256(memory).hexdigest()])
   if results[0]!=results[1]:(OUT/'counterexample.json').write_text(json.dumps(dict(number=number,case=case,results=results),indent=2)+'\n');raise AssertionError((number,case))
   counts[kind]+=1;obs+=len(results[0][1]);digest.update(json.dumps([number,case,charge,configuration,updated,device,phone,glasses,status,timestamp,dropped,results[0]],sort_keys=True).encode())
 receipt=dict(comparisons=sum(counts.values()),counts=counts,observations_per_side=obs,trace_sha256=digest.hexdigest(),actual_source_device_peer_charge_getters=True,raw_r0_callee_sp_and_observed_nonstack_ram_checked=True,provider_register_clobbers_checked=True,captured_metadata_before_timestamp_critical_callbacks_checked=True,ring_drop_wrap_and_out_of_range_write_observed=True,only_configuration_battery_update_timestamp_critical_event_are_fixtures=True,no_native_candidate_execution=True,driver_sha256=sha(Path(__file__)),runtime_report_sha256=sha(rp),object_sha256=sha(obj),layout_sha256=sha(layout),application_sha256=sha(app),whole_battery_event_or_rtos_graph_executed=False,private_stack_identity_verified=False,full_raw_abi_verified=False,instruction_identity=False,whole_image_complete=False)
 (OUT/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
