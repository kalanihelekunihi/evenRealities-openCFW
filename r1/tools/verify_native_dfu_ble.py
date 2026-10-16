#!/usr/bin/env python3
"""Actual native observer/auth SDK helper/getter; SVC and backend fixtures."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-dfu-ble-runtime';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();CTX=0x2002c110;EVENT=0x20002000;FRAME=0x2003efd0
def main():
 rp=OUT/'report.json';b=json.loads(rp.read_text());obj=OUT/'dfu-ble-source.o';assert sha(obj)==b['graph_object_sha256'];app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 layout=ROOT/'r1/source-config/runtime/native_dfu_ble_verification.ld';counts=dict(event=0,authorize=0);hits=dict(value_get=0,reply=0,prepare=0,write=0,callback=0,getter=0,indication=0);digest=hashlib.sha256();states={}
 with tempfile.TemporaryDirectory() as tmp:
  d=Path(tmp);elf=d/'test.elf';subprocess.run(['arm-none-eabi-ld','-T',str(layout),str(obj),'-o',str(elf)],check=True,capture_output=True);p=d/'text.bin';subprocess.run(['arm-none-eabi-objcopy','-j','.text','-O','binary',str(elf),str(p)],check=True);text=p.read_bytes();syms={x[2]:int(x[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x:=line.split())==3}
  def hook(u,a,size,_):
   st=states[id(u)];source=st['source'];assert not source or not 0x27000<=a<0xc4d08
   if a==st['after_getter']:
    st['after_getter']=None
    if st['mutation']==1:u.mem_write(CTX+4,struct.pack('<H',st['glass']))
   if a==(syms['r1_glasses_connection_handle_get'] if source else 0x4cb34):st['events'].append(['getter']);st['after_getter']=u.reg_read(UC_ARM_REG_LR)&~1
   if a==(syms['ble_srv_is_indication_enabled'] if source else 0x539a8):st['events'].append(['indication',bytes(u.mem_read(u.reg_read(UC_ARM_REG_R0),2)).hex()])
   instruction=int.from_bytes(u.mem_read(a,2),'little')
   if instruction&0xff00==0xdf00:
    svc=instruction&255;args=[u.reg_read(reg) for reg in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2]]
    if svc==173:
     assert args[2]==FRAME+16;v=struct.unpack('<HHI',u.mem_read(args[2],8));assert v== (2,0,FRAME+28)
     st['events'].append(['value_get',args,list(v),bytes(u.mem_read(FRAME+28,4)).hex()]);ret=st['value_status'];u.mem_write(FRAME+28,bytes([st['cccd'],0x5a])[:st['written']])
     if st['mutation']==1:u.mem_write(CTX+4,b'\xcd\xab')
    elif svc==176:
     assert args[1]==FRAME;reply=bytes(u.mem_read(args[1],16));ret=st['replies'][min(st['ri'],len(st['replies'])-1)];st['ri']+=1;st['events'].append(['reply',args[:2],reply.hex(),ret])
     if st['mutation']==2:u.mem_write(FRAME+4,b'\xfd\x01')
     if st['mutation']==3:u.mem_write(FRAME+4,b'\x00\x00');u.mem_write(CTX+4,b'\xfe\xff')
    else:raise AssertionError(svc)
    u.reg_write(UC_ARM_REG_R0,ret);u.reg_write(UC_ARM_REG_PC,(a+2)|1);return
   kind=({0x20000200:'prepare',0x20000204:'write',0x20000208:'callback',0x2000020c:'callback'} if source else {0x5207c:'prepare',0x521d8:'write',0x20000208:'callback',0x2000020c:'callback'}).get(a)
   if not kind:return
   arg=u.reg_read(UC_ARM_REG_R0);ret=st['result'];event=[kind]
   if kind=='prepare':
    event += [bytes(u.mem_read(CTX,28)).hex()]
    if st['mutation']==1:u.mem_write(CTX+20,struct.pack('<I',0x2000020d))
   elif kind=='write':
    assert arg in [EVENT+8,0x20003000];event += [arg,bytes(u.mem_read(arg,12)).hex()]
    if st['mutation']==1:u.mem_write(CTX+4,b'\x78\x56')
   elif kind=='callback':assert arg==2;event += [a,arg]
   st['events'].append(event)
   for reg,value in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],[ret,0x11223344,0x55667788,0x99aabbcc]):u.reg_write(reg,value)
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  machines=[]
  for source in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,raw);u.mem_map(0x1000000,0x10000);u.mem_write(0x1000000,text);u.mem_map(0x20000000,0x40000);u.hook_add(UC_HOOK_CODE,hook);machines.append(u)
  cases=[];seqs=[[0],[17,0],[17,17,0xffffffff]]
  for n,(event_id,conn,match,atype,op,waiting,seed) in enumerate(itertools.product([None,0,16,17,81,83,256,65535],[0,1,65535],[False,True],[0,2,255],[0,1,4,5,6,7,255],[0,1,2,255],[0,0x55,0xaa,255])):cases.append(('event',event_id,conn,match,atype,op,waiting,seed,[0,1,255][n%3],[0,1][(n//3)%2],n%3,seqs[(n//6)%3],(n//18)%4,[0,1,65535][(n//72)%3]))
  for n,(cccd,status,written,replies,seed) in enumerate(itertools.product(range(256),[0,1],[0,1,2],seqs,[0,0x55,0xaa,255])):cases.append(('authorize',81,1,True,2,1,1,seed,cccd,status,written,replies,n%4,1))
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  for number,case in enumerate(cases):
   kind,event_id,conn,match,atype,op,waiting,seed,cccd,status,written,replies,mutation,glass=case;outputs=[];result=[0,1,0xffffffff,0x80000000][[0,0x55,0xaa,255].index(seed)]
   for source,u in enumerate(machines):
    u.mem_write(0x20000000,bytes([seed])*0x40000);context=bytearray(28);struct.pack_into('<HHH',context,4,0x1234,0x4321,0x3344);struct.pack_into('<H',context,10,0x5678);struct.pack_into('<I',context,20,0x20000209);context[24]=waiting;context[25]=seed;u.mem_write(CTX,bytes(context));u.mem_write(0x200064bc,struct.pack('<H',glass));packet=bytearray(range(32));struct.pack_into('<H',packet,0,event_id or 0);struct.pack_into('<H',packet,4,conn);packet[6]=atype;packet[7]=0;struct.pack_into('<H',packet,8,0x4321 if match else 0x1111);packet[14]=op
    if event_id==83:struct.pack_into('<H',packet,6,0x4321 if match else 0x1111)
    u.mem_write(EVENT,bytes(packet));u.mem_write(0x20003000,bytes(range(32)))
    st=dict(source=source,events=[],after_getter=None,mutation=mutation,glass=glass,cccd=cccd,value_status=status,written=written,replies=replies,ri=0,result=result);states[id(u)]=st
    u.reg_write(UC_ARM_REG_XPSR,0x01000000);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
    arg=0x20003000 if kind=='authorize' else (0 if event_id is None else EVENT)
    for reg,value in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],[arg,0xdeadbeef,0x55667788,0x99aabbcc]):u.reg_write(reg,value)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    entry=syms['r1_native_dfu_ctrlpt_authorize' if kind=='authorize' else 'r1_native_dfu_ble_event'] if source else (0x7cdc8 if kind=='authorize' else 0x52154)
    try:u.emu_start(entry|1,0x20000100,count=10000)
    except Exception as error:
     (OUT/'execution-error.json').write_text(json.dumps(dict(number=number,source=source,case=case,pc=hex(u.reg_read(UC_ARM_REG_PC)),sp=hex(u.reg_read(UC_ARM_REG_SP)),lr=hex(u.reg_read(UC_ARM_REG_LR)),events=st['events'],error=str(error)),indent=2)+'\n');raise
    assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
    mem=bytes(u.mem_read(0x20000000,0x3e000))+bytes(u.mem_read(0x2003f000,0x1000));outputs.append([u.reg_read(UC_ARM_REG_R0),st['events'],hashlib.sha256(mem).hexdigest()])
   if outputs[0]!=outputs[1]:(OUT/'counterexample.json').write_text(json.dumps(dict(number=number,case=case,outputs=outputs),indent=2)+'\n');raise AssertionError(number)
   counts[kind]+=1
   for event in outputs[0][1]:hits[event[0]]+=1
   digest.update(json.dumps([number,case,outputs[0]],sort_keys=True).encode())
 assert all(hits.values()),hits
 r=dict(comparisons=sum(counts.values()),counts=counts,observation_counts=hits,trace_sha256=digest.hexdigest(),actual_native_observer_authorizer_sdk_bit_helper_and_glasses_getter=True,only_svc_backend_and_event_callbacks_are_fixtures=True,native_connection_updates_and_disconnect_divergence_checked=True,all_cccd_bytes_partial_value_writes_and_busy_retries_checked=True,native_external_auth_frame_addresses_and_reply_bytes_checked=True,fresh_connection_and_mutated_reply_status_checked=True,raw_r0_callee_sp_nonstack_ram_checked=True,no_native_candidate_execution=True,whole_sdk_observer_substitution_used=False,full_raw_abi_verified=False,cross_call_private_frame_history_verified=False,backend_preparation_and_control_point_execution_proven=False,hardware_write_executed=False,instruction_identity=False,whole_image_complete=False,driver_sha256=sha(Path(__file__)),report_sha256=sha(rp),object_sha256=sha(obj),layout_sha256=sha(layout),application_sha256=sha(app))
 (OUT/'verification.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
if __name__=='__main__':main()
