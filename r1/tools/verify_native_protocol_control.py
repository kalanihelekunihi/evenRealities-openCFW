#!/usr/bin/env python3
"""Control paths execute existing payload/header/handle source; external effects are fixtures."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-protocol-control';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ENTRIES={'connection':('r1_connection_control_adv_start_handler_plan_decode',0x83d04),'pair':('r1_pair_role_handler',0x842ec),'report':('r1_service_health_report_set',0x8b834),'command':('r1_protocol_command_00083e2c',0x83e2c),'signal':('r1_protocol_service_thread_flags_set',0x33ae4),'setting':('r1_health_report_setting_plan',0x82ece)}
LOGS=[('report_ring',0x8b87c),('report_sdk',0x8b8b8),('pair_ring',0x8436c),('pair_sdk',0x843a0)]
def main():
 rp=BASE/'native-protocol-control-runtime/report.json';r=json.loads(rp.read_text());obj=rp.parent/'protocol-control-source.o';assert sha(obj)==r['control_object_sha256']
 for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';layout=ROOT/'r1/source-config/runtime/native_protocol_control_verification.ld';states={};digest=hashlib.sha256();counts={k:0 for k in ENTRIES};observations=0
 with tempfile.TemporaryDirectory() as tmp:
  d=Path(tmp);elf=d/'test.elf';subprocess.run(['arm-none-eabi-ld','-T',str(layout),str(obj),'-o',str(elf)],check=True);sections={}
  for section in ['.text']+['.'+n for n,a in LOGS]:
   p=d/(section[1:]+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j',section,'-O','binary',str(elf),str(p)],check=True);sections[section]=p.read_bytes()
  syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3};assert syms['r1_health_report_enabled']==0x200067a0 and syms['r1_protocol_service_thread']==0x20006570 and syms['r1_connection_field8']==0x200064ba
  for name,a in LOGS:assert sections['.'+name]==raw[a-0x27000:a-0x27000+len(sections['.'+name])]
  def state(u):return [bytes(u.mem_read(0x200067a0,1)).hex(),struct.unpack('<I',u.mem_read(0x20006570,4))[0]]
  def hook(u,a,size,_):
   st=states[id(u)];source=st['source'];assert not source or not 0x27000<=a<0xc4d08
   if a==(syms['r1_packet_field12_get'] if source else 0x82bd4):st['after_accessor']=u.reg_read(UC_ARM_REG_LR)&~1
   if st['after_accessor']==a:
    st['after_accessor']=None
    if st['mutation']==6:u.mem_write(st['packet']+8,b'\x0c\x00')
    elif st['mutation']==7:u.mem_write(st['packet']+8,b'\x18\x00');u.mem_write(st['packet']+12,b'\x01')
   fixtures={0x20000200:'response',0x20000204:'mode',0x20000208:'ring',0x2000020c:'sdk',0x20000210:'encode',0x20000214:'role',0x20000218:'delay',0x2000021c:'flags'} if source else {0x828b4:'response',0x914ec:'mode',0x91638:'ring',0x799c8:'sdk',0x33850:'encode',0x4da28:'role',0x7d154:'delay',0x7d6f4:'flags'}
   kind=fixtures.get(a)
   if not kind:return
   regs=[u.reg_read(reg) for reg in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];value=st['returned']
   if kind=='mode':
    value=st['modes'][st['mode_index']%len(st['modes'])];st['mode_index']+=1;st['events'].append(['mode',value,state(u)])
    if st['mutation']==2:u.mem_write(st['packet']+12,bytes([0x70+st['mode_index']]));u.mem_write(st['packet']+3,b'\x78\x56');u.mem_write(0x200067a0,b'\xaa')
   elif kind in ['ring','sdk']:
    st['events'].append([kind,regs if kind=='ring' else regs[:3],state(u)])
    if st['mutation']==3:u.mem_write(st['packet']+12,b'\x7c');u.mem_write(st['packet']+3,b'\x34\x12');u.mem_write(0x200067a0,b'\xcc')
   elif kind=='response':
    h,payload,length=regs[1:];assert length in [0,1];st['events'].append(['response',regs[0],bytes(u.mem_read(h,8)).hex(),length,bytes(u.mem_read(payload,length)).hex() if length else '',state(u)])
    if st['mutation']==1:u.mem_write(0x200064ba,b'\x56\x34');u.mem_write(st['packet']+3,b'\xbc\x0a')
   elif kind=='encode':
    assert regs[2] in [1,12];st['events'].append(['encode',regs[:3],regs[3],bytes(u.mem_read(regs[3],regs[2])).hex(),state(u)])
    if st['mutation']==5:u.mem_write(st['packet']+3,b'\xbb\xaa');u.mem_write(st['packet']+12,b'\x5b')
   elif kind=='role':
    st['events'].append(['role',regs[0],state(u)])
    if st['mutation']==4:u.mem_write(st['packet']+3,b'\xef\xcd');u.mem_write(st['packet']+12,b'\x5a')
   elif kind=='delay':
    assert regs[0]==2000;st['events'].append(['delay',regs[0],state(u)])
    if st['mutation']==4:u.mem_write(0x20006570,bytes(4))
    elif st['mutation']==5:u.mem_write(0x20006570,struct.pack('<I',0x20002800))
   else:st['events'].append(['flags',regs[:2],state(u)])
   u.reg_write(UC_ARM_REG_R0,value)
   for reg,word in [(UC_ARM_REG_R1,0xabcdef01),(UC_ARM_REG_R2,0x12345678),(UC_ARM_REG_R3,0x89abcdef)]:u.reg_write(reg,word)
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  machines=[]
  for source in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x1000);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,raw);u.mem_map(0x1000000,0x20000);u.mem_write(0x1000000,sections['.text']);u.mem_map(0x20000000,0x40000)
   if source:
    for name,a in LOGS:u.mem_write(a,sections['.'+name])
   u.hook_add(UC_HOOK_CODE,hook);machines.append(u)
  modes=[[0],[1],[2],[4],[7],[0,4,2],[1,0],[0xffffffff,0x80000000]];values=[0,1,2,255,256,0xffffffff,0x80000000,0x12345678];handles=[0,0xffff,0x1000ffff];threads=[0,0x20002800,0xffffffff];cases=[]
  for length,handle,mutation,payload in itertools.product(list(range(29))+[255,256,65535],handles,range(8),[0,1,255]):cases.append(('connection',length,handle,mutation,payload,values[mutation],modes[0],threads[mutation%3]))
  for length,handle,mode,mutation,payload in itertools.product([0,12,13,24,65535],handles,modes,range(8),[0,1,2,255]):cases.append(('pair',length,handle,mutation,payload,0,mode,threads[mutation%3]))
  for value,mode,mutation in itertools.product(values,modes,range(8)):cases.append(('report',24,1,mutation,1,value,mode,threads[mutation%3]))
  for length,mode,mutation,payload in itertools.product([0,12,13,24,65535],modes,range(8),[0,1,2,255]):cases.append(('setting',length,1,mutation,payload,0,mode,threads[mutation%3]))
  for length,handle,thread,mutation in itertools.product([0,12,24],handles,threads,range(8)):cases.append(('command',length,handle,mutation,1,0,modes[0],thread))
  for value,thread,mutation in itertools.product(values,threads,range(8)):cases.append(('signal',24,1,mutation,1,value,modes[0],thread))
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  for number,(kind,length,handle,mutation,payload,value,mode,thread) in enumerate(cases):
   results=[];packet=0x20003000+(number&1);sequence=(number*257)&65535;returned=[0,1,0xffffffff,0x80000000,0x12345678][number%5]
   for source,u in enumerate(machines):
    u.mem_write(0x20000000,b'\x96'*0x40000);u.mem_write(0,bytes([payload]));u.mem_write(0x20006570,struct.pack('<I',thread));u.mem_write(0x200064ba,struct.pack('<H',[0,0xffff,0x1234][number%3]));data=bytearray(range(32));data[3:5]=struct.pack('<H',sequence);data[8:10]=struct.pack('<H',length);data[12]=payload;u.mem_write(packet,bytes(data));states[id(u)]=dict(source=source,events=[],packet=packet,mutation=mutation,modes=mode,mode_index=0,returned=returned,after_accessor=None)
    u.reg_write(UC_ARM_REG_XPSR,0x01000000);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    args=[value,0x11223344,0x55667788,0x99aabbcc] if kind in ['report','signal'] else [handle,packet,0x55667788,0x99aabbcc]
    for reg,word in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],args):u.reg_write(reg,word)
    u.emu_start((syms[ENTRIES[kind][0]] if source else ENTRIES[kind][1])|1,0x20000100,count=10000);assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
    memory=bytes(u.mem_read(0x20000000,0x3e000))+bytes(u.mem_read(0x2003f000,0x1000));results.append([u.reg_read(UC_ARM_REG_R0),states[id(u)]['events'],hashlib.sha256(memory).hexdigest()])
   if results[0]!=results[1]:(OUT/'counterexample.json').write_text(json.dumps(dict(number=number,case=[kind,length,handle,mutation,payload,value,mode,thread],results=results),indent=2)+'\n');raise AssertionError((number,kind,length,handle,mutation,payload,value,mode,thread))
   counts[kind]+=1;observations+=len(results[0][1]);digest.update(json.dumps([number,kind,length,handle,mutation,payload,value,mode,thread,results[0]],sort_keys=True).encode())
 receipt=dict(comparisons=sum(counts.values()),counts=counts,observations_per_side=observations,trace_sha256=digest.hexdigest(),actual_source_payload_flag_checked_phone_helpers=True,actual_setting_plan_to_report_setter=True,post_accessor_length_mutations_are_explicit_fixtures=True,fresh_mode_payload_sequence_phone_and_thread_reads_checked=True,provider_failures_do_not_add_early_aborts=True,report_full_word_log_then_low_byte_store_checked=True,only_logging_transport_role_os_are_fixtures=True,source_log_texts_match=True,raw_r0_callee_sp_and_observed_nonstack_ram_checked=True,private_response_pointer_not_compared=True,no_native_candidate_execution=True,driver_sha256=sha(Path(__file__)),runtime_report_sha256=sha(rp),object_sha256=sha(obj),layout_sha256=sha(layout),application_sha256=sha(app),whole_dispatch_or_rtos_graph_executed=False,physical_pairing_adv_or_reset_verified=False,full_raw_abi_verified=False,instruction_identity=False,whole_image_complete=False)
 (OUT/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
