#!/usr/bin/env python3
"""Reset/reaper contracts with source clear and explicit init/scheduler/event fixtures."""
import hashlib,itertools,json,random,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-protocol-reset';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 rp=BASE/'native-protocol-reset-runtime/report.json';r=json.loads(rp.read_text());obj=rp.parent/'protocol-reset-source.o';assert sha(obj)==r['reset_object_sha256']
 for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';layout=ROOT/'r1/source-config/runtime/native_protocol_reset_verification.ld';states={};digest=hashlib.sha256();counts={'reset':0,'arm':0,'tick':0};events=0
 with tempfile.TemporaryDirectory() as tmp:
  d=Path(tmp);elf=d/'test.elf';subprocess.run(['arm-none-eabi-ld','-T',str(layout),str(obj),'-o',str(elf)],check=True);sections={}
  for section in ['.text','.callback']:
   p=d/(section[1:]+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j',section,'-O','binary',str(elf),str(p)],check=True);sections[section]=p.read_bytes()
  syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3};assert syms['r1_protocol_reaper_tick']==0x83cd0 and syms['r1_protocol_sequence']==0x20006b88 and syms['r1_protocol_reset_workspace']==0x20019ef4
  def snap(u):return [bytes(u.mem_read(0x20006b88,2)).hex(),hashlib.sha256(u.mem_read(0x20019ef4,640)).hexdigest()]
  def hook(u,a,size,_):
   st=states[id(u)];source=st['source'];assert not source or not 0x27000<=a<0xc4d08 or 0x83cd0<=a<0x83cd0+len(sections['.callback'])
   if a==(syms['__aeabi_memclr'] if source else 0x277aa):assert [u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1)]==[0x20019ef4,640];st['events'].append(['clear',snap(u)]);return
   fixtures={0x20000200:'init',0x20000204:'schedule',0x20000208:'event'} if source else {0x830a8:'init',0x65b4c:'schedule',0x8d8fc:'event'}
   if a not in fixtures:return
   kind=fixtures[a]
   if kind=='init':
    st['events'].append(['init',snap(u)])
    if st['mutation']==1:u.mem_write(0x20019ef4,b'\x5a'*640);u.mem_write(0x20006b88,b'\x34\x12')
   elif kind=='schedule':
    regs=[u.reg_read(reg) for reg in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2]];assert regs==[0x83cd1,0,0x384000];st['events'].append(['schedule',regs,snap(u)])
    if st['mutation']==2:u.mem_write(0x20019ef4,b'\xa5'*640);u.mem_write(0x20006b88,b'\xcd\xab')
   else:
    assert u.reg_read(UC_ARM_REG_R0)==16 and u.reg_read(UC_ARM_REG_R2)==1;ptr=u.reg_read(UC_ARM_REG_R1);assert bytes(u.mem_read(ptr,1))==b'\x01';st['events'].append(['event',16,'01',1,snap(u)])
    if st['mutation']==3:u.mem_write(ptr,b'\xff');u.mem_write(0x20006b88,b'\x77\x88')
   u.reg_write(UC_ARM_REG_R0,st['returned']);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  machines=[]
  for source in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,raw);u.mem_map(0x1000000,0x20000);u.mem_write(0x1000000,sections['.text']);u.mem_map(0x20000000,0x40000)
   if source:u.mem_write(0x83cd0,sections['.callback'])
   u.hook_add(UC_HOOK_CODE,hook);machines.append(u)
  rng=random.Random(0x82f78);patterns=[bytes(640),bytes([255])*640,bytes(i%256 for i in range(640))]+[rng.randbytes(640) for _ in range(13)];values=[0,1,0xffff,0x80000000,0xffffffff,0x12345678,0x89abcdef,0x55aa55aa];entries={'reset':('r1_native_proto_port_reset',0x82f78),'arm':('r1_ack_reaper_arm',0x83cf4),'tick':('r1_protocol_reaper_tick',0x83cd0)};saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  for kind,data,returned,mutation,sequence in itertools.product(entries,patterns,values,range(4),[0,1,65535]):
   results=[]
   for source,u in enumerate(machines):
    u.mem_write(0x20000000,b'\x96'*0x40000);u.mem_write(0x20019ef4,data);u.mem_write(0x20006b88,struct.pack('<H',sequence));states[id(u)]=dict(source=source,events=[],mutation=mutation,returned=returned)
    u.reg_write(UC_ARM_REG_XPSR,0x01000000);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    for reg,val in [(UC_ARM_REG_R0,returned),(UC_ARM_REG_R1,0x55667788),(UC_ARM_REG_R2,0x98765432),(UC_ARM_REG_R3,returned^0xaabbccdd)]:u.reg_write(reg,val)
    u.emu_start((syms[entries[kind][0]] if source else entries[kind][1])|1,0x20000100,count=10000);assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
    memory=bytes(u.mem_read(0x20000000,0x3e000))+bytes(u.mem_read(0x2003f000,0x1000));results.append([u.reg_read(UC_ARM_REG_R0),states[id(u)]['events'],hashlib.sha256(memory).hexdigest()])
   assert results[0]==results[1],(kind,returned,mutation,sequence,results)
   counts[kind]+=1;events+=len(results[0][1]);digest.update(json.dumps([kind,data.hex(),returned,mutation,sequence,results[0]],sort_keys=True).encode())
 receipt=dict(comparisons=sum(counts.values()),counts=counts,events_per_side=events,trace_sha256=digest.hexdigest(),actual_source_clear=True,init_scheduler_and_event_are_named_fixtures=True,one_byte_event_payload_checked_private_pointer_not_compared=True,source_callback_placed_at_native_address_for_pointer_equality=True,callback_native_body_execution_replaced_with_compiled_source=True,raw_r0_callee_sp_and_observed_nonstack_ram_checked=True,whole_protocol_graph=False,instruction_identity=False,whole_image_complete=False,application_sha256=sha(app),driver_sha256=sha(Path(__file__)),runtime_report_sha256=sha(rp),object_sha256=sha(obj),layout_sha256=sha(layout),source_callback_bytes=len(sections['.callback']))
 (OUT/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
