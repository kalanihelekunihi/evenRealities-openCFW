#!/usr/bin/env python3
"""Native backend/SVCI/CMSIS policy, with API-visible HVX frames and raw probe."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-dfu-backend-runtime';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();CTX=0x2002c110;ALT=0x20001000;BACK=0x20007934;STATE=0x2002c12c;NAME=0x2002c138;WRITE=0x20003000
def main():
 rp=OUT/'report.json';b=json.loads(rp.read_text());app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';layout=ROOT/'r1/source-config/runtime/native_dfu_backend_verification.ld';states={};digest=hashlib.sha256();counts={n:0 for n in ['control','sys','response','prepare','finalize','adv','observer']};hits={n:0 for n in ['hvx','clear','set','command','handler','callback','power','mode','ring','sdk','copy']};raw_probe=None;raw_differences=0
 modes=[[0],[1],[2],[4],[7],[0,4,2]];seqs=[[0],[17,0],[0x100,0],[0xffffffff,0]]
 for composed in [False,True]:
  obj=OUT/('dfu-backend-observer-source.o' if composed else 'dfu-backend-source.o');assert sha(obj)==b['composed_object_sha256' if composed else 'graph_object_sha256']
  with tempfile.TemporaryDirectory() as tmp:
   d=Path(tmp);elf=d/'test.elf';subprocess.run(['arm-none-eabi-ld','-T',str(layout),str(obj),'-o',str(elf)],check=True,capture_output=True);p=d/'text.bin';subprocess.run(['arm-none-eabi-objcopy','-j','.text','-O','binary',str(elf),str(p)],check=True);text=p.read_bytes();syms={x[2]:int(x[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x:=line.split())==3};assert syms['nrf_dfu_set_adv_name_svci_async_def']==STATE
   def hook(u,a,size,_):
    st=states[id(u)];source=st['source'];assert not source or not 0x27000<=a<0xc4d08
    if a==st['after_copy']:
     st['after_copy']=None
     if st['mutation']==2:u.mem_write(WRITE+13,b'\xff')
    if a==(syms['memcpy'] if source else 0x2775c):
     args=[u.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2]];st['events'].append(['copy',args]);st['after_copy']=u.reg_read(UC_ARM_REG_LR)&~1
    instruction=int.from_bytes(u.mem_read(a,2),'little')
    if instruction&0xff00==0xdf00:
     svc=instruction&255;r0=u.reg_read(UC_ARM_REG_R0);r1=u.reg_read(UC_ARM_REG_R1)
     if svc==174:
      fields=struct.unpack('<HBBHHII',u.mem_read(r1,16));handle,type_,pad,offset,pad2,lenptr,dataptr=fields;expected={'control':0x2003efd0,'sys':0x2003efd8,'response':0x2003efe8}[st['kind']];assert lenptr==expected and r1==expected+4 and dataptr==expected+20 and type_==2 and pad==pad2==offset==0
      frame=bytes(u.mem_read(lenptr,24));event=['hvx',r0,r1,fields,bytes(u.mem_read(dataptr,3)).hex(),struct.unpack('<H',u.mem_read(lenptr,2))[0]]
      if st['kind']=='response':event.append(frame.hex())
      st['frames'].append(frame.hex());ret=st['hvx'][min(st['hi'],len(st['hvx'])-1)];st['hi']+=1;event += [ret,st['hvxlen']];u.mem_write(lenptr,struct.pack('<H',st['hvxlen']))
      if st['mutation']==3:u.mem_write(CTX+4,b'\x88\x88');u.mem_write(WRITE+12,b'\xff')
     elif svc in [61,60]:
      assert [r0,r1]==([0,0xffffffff] if svc==61 else [0,0xb1]);event=['clear' if svc==61 else 'set',r0,r1];ret=st['clear' if svc==61 else 'set']
      if st['mutation']==1:u.mem_write(CTX+20,struct.pack('<I',0x2000020d))
     else:raise AssertionError(svc)
     st['events'].append(event);u.reg_write(UC_ARM_REG_R0,ret);u.reg_write(UC_ARM_REG_PC,(a+2)|1);return
    fixed={0x20000200:'command',0x20000204:'handler',0x20000208:'callback',0x2000020c:'callback',0x20000210:'callback',0x20000214:'callback'}
    lower=({syms['nrf_pwr_mgmt_shutdown']&~1:'power',syms['r1_structured_log_mode_get']&~1:'mode',syms['r1_structured_log_format']&~1:'ring',syms['nrf_log_frontend_std_0']&~1:'sdk'} if source else {0x79d50:'power',0x914ec:'mode',0x91638:'ring',0x799c0:'sdk'})
    kind=fixed.get(a) or lower.get(a)
    if not kind:return
    args=[u.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2]];event=[kind];ret=st['callback_result'];m=st['mutation']
    if kind=='command':
     assert args[:2]==[NAME,STATE+8];event += [args[:2],bytes(u.mem_read(NAME,28)).hex()];ret=st['command']
     if m==2:u.mem_write(BACK,struct.pack('<I',ALT))
    elif kind=='handler':
     assert args[:2]==[st['sys_evt'],STATE+8];event += [args[:2]];ret=st['handler']
     if m==2:u.mem_write(BACK,struct.pack('<I',ALT))
    elif kind=='callback':
     assert args[0] in range(4);event += [a,args[0]]
     if m==1 and args[0] in [0,3]:u.mem_write(BACK,struct.pack('<I',ALT));u.mem_write(CTX+20,struct.pack('<I',0x2000020d))
    elif kind=='power':assert args[0]==2;event += [args[0]]
    elif kind=='mode':ret=st['modes'][st['mi']%len(st['modes'])];st['mi']+=1;event += [ret]
    elif kind=='ring':assert args==[0x04000000,0xc2a98,0xc2a98];event += [args]
    elif kind=='sdk':assert args[:2]==[0x001c0001,0xc2b6c];event += [args[:2]]
    st['events'].append(event)
    for reg,value in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],[ret,0x11223344,0x55667788,0x99aabbcc]):u.reg_write(reg,value)
    u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
   machines=[]
   for source in range(2):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,raw);u.mem_map(0x1000000,0x20000);u.mem_write(0x1000000,text);u.mem_map(0x20000000,0x40000);u.hook_add(UC_HOOK_CODE,hook);machines.append(u)
   cases=[]
   # Fields: kind,alternate,opcode,length,waiting,command,handler,hvx,len,clear,set,seed,mutation,modes,missing.
   if not composed:
    for n,(op,length,waiting,command,seed) in enumerate(itertools.product(range(256),[0,1,20,21,255],[0,1,255],[0,6,15,0xffffffff],[0,0xaa])):cases.append(('control',n%2,op,length,waiting,command,0,seqs[n%4],[0,3,4][(n//4)%3],0,0,seed,(n//12)%4,modes[(n//48)%6],0))
    for n,(missing,sys_evt,result,hvx,len_,alt,m,seed) in enumerate(itertools.product(range(4),[0,1,65535,0xffffffff],[0,8,1,15,0xffffffff],seqs,[0,3,4],range(2),range(4),[0,0x55,0xaa,255])):cases.append(('sys',alt,sys_evt,1,seed,0,result,hvx,len_,0,0,seed,m,modes[n%6],missing))
    for op,rc,result,len_,seed in itertools.product([0,1,2,255,256,65535,0xffffffff],[0,1,6,255,256,0xffffffff],[0,1,12,17,0x100,0xffffffff],[0,2,3,4,65535],[0,0x55,0xaa,255]):cases.append(('response',0,op,rc,0,0,0,[result],len_,0,0,seed,0,[0],0))
    for kind,clear,set_,alt,m,seed in itertools.product(['prepare','finalize'],[0,1,0x100,0xffffffff],[0,1,0x100,0xffffffff],range(2),range(4),[0,0x55,0xaa,255]):cases.append((kind,alt,1,1,0,0,0,[0],3,clear,set_,seed,m,[0],0))
    for n,(waiting,result,mode,alt,m,seed) in enumerate(itertools.product([0,1,2,255],[0,1,6,15,0x100,0xffffffff],modes,range(2),range(4),[0,0x55,0xaa,255])):cases.append(('adv',alt,2,20,waiting,result,0,[0],3,0,0,seed,m,mode,0))
   else:
    for waiting,clear,set_,alt,m,seed in itertools.product([0,1,2,255],[0,1,0x100,0xffffffff],[0,1,0x100,0xffffffff],range(2),range(4),[0,0x55,0xaa,255]):cases.append(('observer',alt,2,1,waiting,0,0,[0],3,clear,set_,seed,m,[0],0))
   saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
   for number,case in enumerate(cases):
    kind,alt,opcode,length,waiting,command,handler,hvx,hvxlen,clear,set_,seed,mutation,mode,missing=case;outputs=[];rawframes=[]
    for source,u in enumerate(machines):
     u.mem_write(0x20000000,bytes([seed])*0x40000)
     for address,callback,conn in [(CTX,0x20000209,0x1111),(ALT,0x20000211,0x2222)]:
      ctx=bytearray(28);struct.pack_into('<HH',ctx,4,conn,0x1234);struct.pack_into('<I',ctx,20,callback);ctx[24]=waiting;ctx[25]=waiting;u.mem_write(address,bytes(ctx))
     u.mem_write(BACK,struct.pack('<I',ALT if alt else CTX));u.mem_write(STATE,struct.pack('<III',0 if missing&1 else 0x20000201,0 if missing&2 else 0x20000205,0x87654321));u.mem_write(NAME,struct.pack('<I',0x10203040)+bytes([seed])*20+struct.pack('<I',length));packet=bytearray(range(64));packet[12]=opcode&255;packet[13]=length&255;u.mem_write(WRITE,bytes(packet));u.mem_write(0x20002000,struct.pack('<HHHH',83,8,0x9999,0x1234)+bytes(24))
     st=dict(source=source,kind=kind,events=[],frames=[],after_copy=None,command=command,handler=handler,hvx=hvx,hi=0,hvxlen=hvxlen,clear=clear,set=set_,callback_result=[0,1,0xffffffff,0x80000000][[0,0x55,0xaa,255].index(seed)],mutation=mutation,modes=mode,mi=0,sys_evt=opcode);states[id(u)]=st
     u.reg_write(UC_ARM_REG_XPSR,0x01000000);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
     args=[WRITE,0,0,0]
     if kind=='sys':args=[opcode,0xdeadbeef,0,0]
     elif kind=='response':args=[opcode,length,0,0]
     elif kind=='adv':args=[NAME,0,0,0]
     elif kind=='observer':args=[0x20002000,0xdeadbeef,0,0]
     for reg,value in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],args):u.reg_write(reg,value)
     for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
     source_name={'control':'r1_dfu_control_point_write_boundary','sys':'r1_native_dfu_on_sys_evt','response':'r1_native_dfu_response','prepare':'r1_dfu_bootloader_prepare_boundary','finalize':'r1_native_dfu_finalize','adv':'r1_native_dfu_set_adv_name','observer':'r1_native_dfu_ble_event'}[kind];native={'control':0x521d8,'sys':0x52278,'response':0x522d8,'prepare':0x5207c,'finalize':0x52050,'adv':0x8ed5c,'observer':0x52154}[kind]
     try:u.emu_start((syms[source_name] if source else native)|1,0x20000100,count=20000)
     except Exception as error:(OUT/'execution-error.json').write_text(json.dumps(dict(source=source,case=case,pc=hex(u.reg_read(UC_ARM_REG_PC)),events=st['events'],error=str(error)),indent=2)+'\n');raise
     assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
     mem=bytes(u.mem_read(0x20000000,0x3e000))+bytes(u.mem_read(0x2003f000,0x1000));outputs.append([u.reg_read(UC_ARM_REG_R0),st['events'],hashlib.sha256(mem).hexdigest()]);rawframes.append(st['frames'])
    if outputs[0]!=outputs[1]:(OUT/'counterexample.json').write_text(json.dumps(dict(case=case,outputs=outputs),indent=2)+'\n');raise AssertionError((kind,number))
    if rawframes[0]!=rawframes[1]:
     raw_differences+=1
     if raw_probe is None:raw_probe=dict(matched=False,kind='unused_hvx_frame_padding_history',case=case,native_raw_frames=rawframes[0],source_raw_frames=rawframes[1],api_visible_outputs_match=True,no_padding_normalization=True)
    counts[kind]+=1
    for event in outputs[0][1]:hits[event[0]]+=1
    digest.update(json.dumps([kind,number,case,outputs[0]],sort_keys=True).encode())
 assert all(hits.values()),hits
 probe=raw_probe or dict(matched=True,kind='bounded_raw_frame_history',full_private_history_proven=False);probe['different_cases']=raw_differences;probe['driver_sha256']=sha(Path(__file__));(OUT/'raw-frame-history-probe.json').write_text(json.dumps(probe,indent=2)+'\n')
 r=dict(comparisons=sum(counts.values()),counts=counts,observation_counts=hits,trace_sha256=digest.hexdigest(),actual_six_backend_bodies_memory_and_composed_hvc_observer=True,only_svc_svci_callback_power_logging_are_fixtures=True,canonical_and_backend_contexts_distinct_and_fresh_checked=True,all_control_opcodes_name_limits_and_fresh_copy_length_checked=True,response_api_frames_direct_raw_padding_and_hvx_length_checked=True,shared_svci_missing_pending_busy_and_result_paths_checked=True,raw_r0_callee_sp_nonstack_ram_checked=True,no_native_candidate_execution=True,raw_frame_probe_sha256=sha(OUT/'raw-frame-history-probe.json'),raw_frame_difference_cases=raw_differences,full_private_frame_history_verified=False,full_raw_abi_verified=False,service_initialization_proven=False,physical_dfu_execution_proven=False,hardware_write_executed=False,instruction_identity=False,whole_image_complete=False,driver_sha256=sha(Path(__file__)),report_sha256=sha(rp),object_sha256=b['graph_object_sha256'],composed_object_sha256=b['composed_object_sha256'],layout_sha256=sha(layout),application_sha256=sha(app))
 (OUT/'verification.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
if __name__=='__main__':main()
