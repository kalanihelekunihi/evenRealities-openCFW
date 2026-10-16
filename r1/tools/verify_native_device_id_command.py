#!/usr/bin/env python3
"""Device ID command and operation11; identity provider and response are fixtures."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-device-id-command-runtime';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();P=0x20003001;FRAME=0x2003efb8;ID=FRAME+32;RESPONSE=FRAME+4

def main():
 rp=OUT/'report.json';b=json.loads(rp.read_text());obj=OUT/'device-id-command-source.o';assert sha(obj)==b['graph_object_sha256']
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 layout=ROOT/'r1/source-config/runtime/native_device_id_command_verification.ld';states={};digest=hashlib.sha256();obs=0;counts={'command':0,'workflow':0,'op11':0,'status':0,'clear':0}
 with tempfile.TemporaryDirectory() as tmp:
  d=Path(tmp);elf=d/'test.elf';subprocess.run(['arm-none-eabi-ld','-T',str(layout),str(obj),'-o',str(elf)],check=True);sections={}
  for n in ['text','default','ring','sdk','status','phone']:
   p=d/(n+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j','.'+n,'-O','binary',str(elf),str(p)],check=True);sections[n]=p.read_bytes()
  syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3};assert syms['r1_device_id_once_status']==0x20006da5 and syms['r1_connection_field8']==0x200064ba
  for n,a in [('default',0x9a56c),('ring',0x83ef0),('sdk',0x83f10)]:assert sections[n]==raw[a-0x27000:a-0x27000+len(sections[n])]
  cold=(BASE/'native-scatter-data/observed-initialized-data.bin').read_bytes();assert sections['status']==cold[0x20006da5-0x200064a8:0x20006da6-0x200064a8]==b'\0'
  def hook(u,a,size,_):
   st=states[id(u)];source=st['source'];assert not source or not 0x27000<=a<0xc4d08
   if a==(syms['r1_phone_connection_handle_get'] if source else 0x4cba4):
    st['events'].append(['actual_phone_getter'])
    if st['mutation']==5:u.mem_write(0x200064ba,b'\x78\x56')
   kind=({0x20000204:'id',0x20000208:'response',0x2000020c:'mode',0x20000210:'ring',0x20000214:'sdk'} if source else {0x6ab88:'id',0x84c0c:'response',0x914ec:'mode',0x91638:'ring',0x799d6:'sdk'}).get(a)
   if not kind:return
   r=[u.reg_read(x) for x in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];ret=st['result'];m=st['mutation'];event=[kind]
   if kind=='id':
    assert r[0]==ID;event+=[r[0],bytes(u.mem_read(ID,28)).hex(),bytes(u.mem_read(0x20006da5,1)).hex()];u.mem_write(ID,bytes(range(1,st['length']+1)))
    if m==1:u.mem_write(P+3,b'\x78\x56');u.mem_write(0x20006da5,b'\x01')
   elif kind=='response':
    extra=list(struct.unpack('<II',u.mem_read(u.reg_read(UC_ARM_REG_SP),8)));assert r[1]==11 and extra[1]==25;event+=[r,extra,bytes(u.mem_read(extra[0],25)).hex()]
   elif kind=='mode':
    ret=st['modes'][st['mi']%len(st['modes'])];st['mi']+=1;event+=[ret]
    if m==2:u.mem_write(ID,b'\xaa\xbb\x00');u.mem_write(P+3,b'\xfe\xdc')
   elif kind=='ring':
    arg=struct.unpack('<I',u.mem_read(u.reg_read(UC_ARM_REG_SP),4))[0];assert r[:3]==[0x0c800000,0x83ef0,0x83ef0] and arg==ID;event+=[r,arg,bytes(u.mem_read(arg,28)).hex()]
    if m==3:u.mem_write(RESPONSE,b'\xfe');u.mem_write(ID,b'\xdd\x00');u.mem_write(P+3,b'\x10\x32')
   elif kind=='sdk':
    assert r[:2]==[0x001c0003,0x83f10] and r[3]==ID;event+=[r,bytes(u.mem_read(ID,28)).hex()]
    if m==4:u.mem_write(RESPONSE,b'\xfc');u.mem_write(P+3,b'\x54\x76')
   st['events'].append(event);u.reg_write(UC_ARM_REG_R0,ret)
   for reg,v in [(UC_ARM_REG_R1,0xabcdef01),(UC_ARM_REG_R2,0x12345678),(UC_ARM_REG_R3,0x89abcdef)]:u.reg_write(reg,v)
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  machines=[]
  for source in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,raw);u.mem_map(0x1000000,0x20000);u.mem_write(0x1000000,sections['text']);u.mem_map(0x20000000,0x40000)
   for n,a in [('default',0x9a56c),('ring',0x83ef0),('sdk',0x83f10)]:u.mem_write(a,sections[n])
   u.hook_add(UC_HOOK_CODE,hook);machines.append(u)
  modes=[[0],[1],[2],[4],[7],[0,4,2],[1,0],[0xffffffff,0x80000000]];results=[0,1,0x80000000,0xffffffff];cases=[]
  for number,(status,length,mode,m) in enumerate(itertools.product([0,1,2,255],[0,1,24,25,28],modes,range(6))):cases.append(('command',status,length,mode,m,results[number%4],0x1234,RESPONSE))
  for status,mode,m,result in itertools.product([0,1,255],modes,range(6),results):cases.append(('workflow',status,25,mode,m,result,65535,RESPONSE))
  for payload,phone,result,m in itertools.product([0,0x20002001],[0,65535,0x1234],results,range(6)):cases.append(('op11',0,25,modes[0],m,result,phone,payload))
  for kind,status in itertools.product(['status','clear'],range(256)):cases.append((kind,status,0,modes[0],0,0,0,0))
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  for number,(kind,status,length,mode,m,result,phone,payload) in enumerate(cases):
   outputs=[]
   for source,u in enumerate(machines):
    u.mem_write(0x20000000,b'\x96'*0x40000);u.mem_write(P,bytes(range(64)));u.mem_write(0x20002001,bytes(range(32)));u.mem_write(0x20006da5,bytes([status]));u.mem_write(0x200064ba,struct.pack('<H',phone));states[id(u)]=dict(source=source,events=[],mutation=m,modes=mode,mi=0,result=result,length=length)
    regout=[]
    for iteration in range(2 if kind=='workflow' else 1):
     u.reg_write(UC_ARM_REG_XPSR,0x01000000);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
     for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
     args=[payload,0x10000001,0x20000002,0x99aabbcc] if kind=='op11' else [0x1000ffff,P,0x55667788,0x99aabbcc]
     for reg,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],args):u.reg_write(reg,v)
     symbol,address={'command':('r1_protocol_command_00083e50',0x83e50),'workflow':('r1_protocol_command_00083e50',0x83e50),'op11':('r1_phone_cmd_send_op11',0x838ba),'status':('r1_device_id_status_get',0x6abd8),'clear':('r1_device_id_status_clear',0x6aadc)}[kind]
     u.emu_start((syms[symbol] if source else address)|1,0x20000100,count=10000);assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
     regout.append([u.reg_read(reg) for reg in [UC_ARM_REG_R0,UC_ARM_REG_R2,UC_ARM_REG_R3]])
    mem=bytes(u.mem_read(0x20000000,0x3e000))+bytes(u.mem_read(0x2003f000,0x1000));outputs.append([regout,states[id(u)]['events'],hashlib.sha256(mem).hexdigest()])
   if outputs[0]!=outputs[1]:(OUT/'counterexample.json').write_text(json.dumps(dict(number=number,case=[kind,status,length,mode,m,result,phone,payload],outputs=outputs),indent=2)+'\n');raise AssertionError((number,kind))
   counts[kind]+=1;obs+=len(outputs[0][1]);digest.update(json.dumps([number,kind,status,length,mode,m,result,phone,payload,outputs[0]],sort_keys=True).encode())
 receipt=dict(comparisons=sum(counts.values()),counts=counts,observations_per_side=obs,trace_sha256=digest.hexdigest(),actual_status_accessors_op11_phone_getter_and_musl_memory=True,id_read_response_and_logging_are_fixtures=True,one_shot_two_call_workflow_checked=True,provider_writes_limited_to_mapped_28byte_fixture=True,raw_r0_r2_r3_callee_sp_and_nonstack_ram_checked=True,no_native_candidate_execution=True,native_cached_svc_identity_provider_implemented=False,status_alias_to_eventual_context_required=True,hardware_write_executed=False,full_raw_abi_verified=False,cross_call_private_frame_history_verified=False,instruction_identity=False,whole_image_complete=False,driver_sha256=sha(Path(__file__)),report_sha256=sha(rp),object_sha256=sha(obj),layout_sha256=sha(layout),application_sha256=sha(app))
 (OUT/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
