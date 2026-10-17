#!/usr/bin/env python3
"""Native time update/snapshot contracts with callback mutation and cache oracles."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_INVALID
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-time-update';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();SP=0x2003d000;STATE=0x20016ac4;REG=0x20006820;DATA=0x20010000;OPS=DATA+128;OPS2=DATA+160;GET=0x20001000;UPDATE=GET+16;UPDATE2=GET+32
REGS=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3];SAVED=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
def put(d,a,v):struct.pack_into('<I',d,a,v&0xffffffff)
def main():
 c=json.loads((OUT/'contracts.json').read_text());obj=OUT/'native_time_update.o';config=OUT/'shared-time-config.o';app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';image=app.read_bytes();assert sha(app)==c['application_sha256']=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';states={};digest=hashlib.sha256();counts={'setter':0,'snapshot':0,'update':0,'faults':0,'get_calls':0,'update_calls':0,'clears':0};proof=[]
 with tempfile.TemporaryDirectory() as td:
  td=Path(td);ld=td/'layout.ld';ld.write_text('SECTIONS {'+''.join(' .s%d 0x%x : { *(.text.%s) }'%(i,int(x['address'],16),x['symbol']) for i,x in enumerate(c['bodies']))+' .state 0x20016ac4 : { *(.r1.time.state) } .registration 0x20006820 : { *(.r1.time.registration) } /DISCARD/ : { *(.ARM.exidx*) } }\n__aeabi_memclr = 0x277ab;\n');elf=td/'proof.elf';subprocess.run(['arm-none-eabi-ld','-T',str(ld),str(obj),str(config),'-o',str(elf)],check=True,stderr=subprocess.PIPE);replacement=[]
  for i,x in enumerate(c['bodies']):
   a=int(x['address'],16);p=td/(str(i)+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j','.s'+str(i),'-O','binary',str(elf),str(p)],check=True);d=p.read_bytes();assert len(d)==x['source_span_bytes'] and d==image[a-0x27000:a-0x27000+len(d)];replacement.append((a,d));proof.append(dict(symbol=x['symbol'],address=hex(a),size=len(d),sha256=sha(p)))
  def invalid(u,access,address,size,value,_):states[id(u)]['fault']=[access,address,size,value];return False
  def hook(u,a,size,_):
   if a not in [GET,UPDATE,UPDATE2,0x277aa]:return
   s=states[id(u)];case=s['case'];r=[u.reg_read(x) for x in REGS];s['trace'].append([hex(a),r]);counts['get_calls' if a==GET else 'clears' if a==0x277aa else 'update_calls']+=1
   if a==0x277aa:assert r[:2]==[STATE+12,20];u.mem_write(r[0],bytes(20));u.reg_write(UC_ARM_REG_R0,0)
   elif a==GET:
    assert r[0]==0x12345678
    if case['mutation']&1:u.mem_write(STATE+12,b'\x42'*20);u.mem_write(REG,b'\x05')
    if case['mutation']&2:u.mem_write(SP-52,struct.pack('<I',OPS2));u.mem_write(SP-56,struct.pack('<I',0xaabbccdd))
    u.reg_write(UC_ARM_REG_R0,0x98765432)
   else:
    redirected=case['capture']!=1 and case['get'] and case['mutation']&2;assert a==(UPDATE2 if redirected else UPDATE) and r[:3]==[case['timestamp'],case['offset'],0xaabbccdd if redirected else 0x12345678],(case,a,r)
    if case['mutation']&4:u.mem_write(STATE+12,b'\x35'*20);u.mem_write(REG,b'\x09');u.mem_write(STATE+8,b'\x34\x12')
    u.reg_write(UC_ARM_REG_R0,case['result'])
   for reg,value in zip(REGS[1:],[0xa1a1a1a1,0xb2b2b2b2,0xc3c3c3c3]):u.reg_write(reg,value)
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  machines=[]
  for side in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x100000);u.mem_write(0x27000,image);u.mem_map(0x20000000,0x40000)
   if side:
    for a,d in replacement:u.mem_write(a,d)
   u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_INVALID,invalid);machines.append(u)
  default=dict(kind='update',registered=1,snapshot_flag=1,backend=OPS,capture=0,get=1,update=1,offset=480,old_offset=480,timestamp=0x80000001,result=1,mutation=0,outops=DATA,outctx=DATA+4,pending=0)
  cases=[dict(default,kind='setter',pending=v) for v in range(256)]
  cases += [dict(default,kind='snapshot',snapshot_flag=flag,backend=backend,outops=out[0],outctx=out[1]) for flag,backend,out in itertools.product(range(256),[0,1,2,3,OPS,OPS+1,0xffffffff],[(DATA,DATA+4),(0,0),(REG+20,DATA+4),(DATA,REG+16)])]
  cases += [dict(default,registered=reg,capture=cap,result=result) for reg,cap,result in itertools.product([0,1,2,255],range(256),[0,1,0xffffffff])]
  cases += [dict(default,registered=reg,snapshot_flag=flag,backend=backend,capture=cap,get=get_,update=upd,offset=off,result=result,mutation=mutation,old_offset=0xffff) for reg,flag,backend,cap,get_,upd,off,result,mutation in itertools.product([0,1],[0,1],[0,OPS],[0,1,255],range(2),range(2),[0,480,0x0000ffff,0xffffffff,0x00008000,0xffff8000],[0,1,0xffffffff],[0,3,4,7])]
  cases += [dict(default,backend=0x30000000),dict(default,kind='snapshot',outops=0x30000000),dict(default,kind='snapshot',outctx=0x30000000)]
  for case in cases:
   state=bytearray(b'\x69'*32);state[10]=case['registered'];state[11]=case['pending'];struct.pack_into('<H',state,8,case['old_offset']);registration=bytearray(b'\x73'*24);registration[0]=case['capture'];registration[12]=case['snapshot_flag'];put(registration,4,0x11223344);put(registration,16,case['backend']);put(registration,20,0x12345678);data=bytearray(b'\x96'*256);put(data,OPS-DATA+8,GET+1 if case['get'] else 0);put(data,OPS-DATA+16,UPDATE+1 if case['update'] else 0);put(data,OPS2-DATA+16,UPDATE2+1);expected_state=bytearray(state);expected_reg=bytearray(registration);expected_data=bytearray(data);mask=((0-case['snapshot_flag'])&0xffffffff)&case['backend'];expected_fault=False;expected_r0=None;expected_clears=0;expected_get=0;expected_update=0
   if case['kind']=='setter':expected_state[11]=1;expected_r0=1
   elif case['kind']=='snapshot':
    expected_r0=int(bool(mask))
    if mask:
     for p,v in [(case['outops'],case['backend']),(case['outctx'],None)]:
      if not p:continue
      if p==0x30000000:expected_fault=True;break
      if v is None:v=int.from_bytes(expected_reg[20:24],'little')
      if REG<=p<REG+24:put(expected_reg,p-REG,v)
      else:put(expected_data,p-DATA,v)
   elif not case['registered'] or not mask:expected_r0=0
   elif case['backend']==0x30000000:expected_fault=True
   elif not case['update']:expected_r0=0
   else:
    old=int.from_bytes(state[8:10],'little');old=(old-65536 if old&32768 else old)&0xffffffff
    if old!=case['offset']:struct.pack_into('<H',expected_state,8,case['offset']&65535);expected_state[12:32]=bytes(20);expected_clears+=1
    capture=case['capture']!=1;expected_get=int(capture and case['get']);expected_update=1
    if expected_get and case['mutation']&1:expected_state[12:32]=b'\x42'*20;expected_reg[0]=5
    if case['mutation']&4:expected_state[12:32]=b'\x35'*20;expected_reg[0]=9;expected_state[8:10]=b'\x34\x12'
    expected_r0=case['result']
    if expected_r0:
     expected_state[12:32]=bytes(20);expected_clears+=1
     if capture:expected_reg[0]=1;put(expected_reg,4,0x98765432 if case['get'] else 0)
   outputs=[]
   for u in machines:
    u.mem_write(STATE,bytes(state));u.mem_write(REG,bytes(registration));u.mem_write(DATA,bytes(data));u.mem_write(SP-128,b'\x96'*256)
    args=[case['outops'],case['outctx'],0x22222222,0x33333333] if case['kind']=='snapshot' else [case['timestamp'],case['offset'],0x22222222,0x33333333]
    for reg,value in zip(REGS,args):u.reg_write(reg,value)
    for i,reg in enumerate(SAVED):u.reg_write(reg,0x12340000+i)
    u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,0x20000101);s=dict(case=case,trace=[],fault=None);states[id(u)]=s
    try:u.emu_start({'setter':0x8aea5,'snapshot':0x5a991,'update':0x8aeb1}[case['kind']],0x20000100,count=1000)
    except UcError:assert s['fault']
    assert bool(s['fault'])==expected_fault,case
    if not expected_fault:
     assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==SP and [u.reg_read(reg) for reg in SAVED]==[0x12340000+i for i in range(8)] and u.reg_read(UC_ARM_REG_R0)==expected_r0,(case,u.reg_read(UC_ARM_REG_R0),expected_r0)
     assert bytes(u.mem_read(STATE,32))==expected_state and bytes(u.mem_read(REG,24))==expected_reg and bytes(u.mem_read(DATA,256))==expected_data,case
     assert sum(x[0]==hex(GET) for x in s['trace'])==expected_get and sum(x[0] in [hex(UPDATE),hex(UPDATE2)] for x in s['trace'])==expected_update and sum(x[0]==hex(0x277aa) for x in s['trace'])==expected_clears
    outputs.append([[u.reg_read(reg) for reg in REGS],u.reg_read(UC_ARM_REG_SP),s['fault'],s['trace'],bytes(u.mem_read(STATE,32)).hex(),bytes(u.mem_read(REG,24)).hex(),bytes(u.mem_read(DATA,256)).hex(),bytes(u.mem_read(SP-128,256)).hex()])
   assert outputs[0]==outputs[1],case;counts[case['kind']]+=1;counts['faults']+=int(expected_fault);digest.update(json.dumps([case,outputs[0]],sort_keys=True).encode())
 receipt=dict(comparisons=sum(counts[k] for k in ['setter','snapshot','update']),counts=counts,trace_sha256=digest.hexdigest(),exact_spans=proof,exact_bytes=sum(x['size'] for x in proof),object_sha256=sha(obj),shared_config_object_sha256=sha(config),driver_sha256=sha(Path(__file__)),report_sha256=sha(OUT/'report.json'),application_sha256=sha(app),actual_flag_update_and_snapshot_execute=True,backend_callbacks_and_memclr_are_fixtures=True,independent_state_cache_and_callback_contract_oracle=True,all_capture_and_snapshot_flag_bytes_checked=True,fresh_stack_snapshot_and_context_after_get_mutation_checked=True,full_private_history_or_raw_abi_verified=False,whole_image_complete=False,hardware_write_executed=False)
 (OUT/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
