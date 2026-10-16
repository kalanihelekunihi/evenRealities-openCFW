#!/usr/bin/env python3
"""Check saved-r3 byte views with actual cached-read/musl and phone accessors."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-time-sync-providers-runtime';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
CLASSES=[('devinfo',0x200069a8),('ble_mult',0x200069f4),('health',0x20006a68),('hsync',0x20006a8c),('power',0x20006abc),('serial',0x20006ad8),('r_size',0x20006b6c)]
FRAME=0x2003eff8;NODE=0x20006b6c;ALT=0x20001000

def main():
 rp=OUT/'report.json';b=json.loads(rp.read_text());obj=OUT/'time-sync-providers-source.o';assert sha(obj)==b['graph_object_sha256']
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 layout=ROOT/'r1/source-config/runtime/native_time_sync_providers_verification.ld';states={};digest=hashlib.sha256();obs=0;counts={'query_fixture':0,'query_cached':0,'timeout':0}
 with tempfile.TemporaryDirectory() as tmp:
  d=Path(tmp);elf=d/'test.elf';subprocess.run(['arm-none-eabi-ld','-T',str(layout),str(obj),'-o',str(elf)],check=True);sections={}
  for n in ['text','handles','phone','port']+[n for n,a in CLASSES]:
   p=d/(n+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j','.'+n,'-O','binary',str(elf),str(p)],check=True);sections[n]=p.read_bytes()
  syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
  assert syms['r1_r_size_kv_handle']==0x20007e00 and syms['r1_connection_field8']==0x200064ba and syms['r1_kv_port']==0x20006974
  cold=(BASE/'native-scatter-data/observed-initialized-data.bin').read_bytes()
  for n,a in CLASSES:assert sections[n]==cold[a-0x200064a8:a-0x200064a8+len(sections[n])]
  assert sections['handles']==cold[0x20007de8-0x200064a8:0x20007e04-0x200064a8]
  def hook(u,a,size,_):
   st=states[id(u)];source=st['source'];assert not source or not 0x27000<=a<0xc4d08
   read=a==(syms['r1_kv_class_read'] if source else 0x73930)
   if read:
    r=[u.reg_read(x) for x in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2]];assert r==[NODE,FRAME,1];st['events'].append(['read',r])
    if st['kind']=='query_fixture':
     if st['mutation']==1:u.mem_write(FRAME,bytes([st['value']]))
     if st['mutation']==2:u.mem_write(FRAME,struct.pack('<I',0xaabbcc00|st['value']))
     u.reg_write(UC_ARM_REG_R0,st['result'])
     for reg,v in [(UC_ARM_REG_R1,0xabcdef01),(UC_ARM_REG_R2,0x12345678),(UC_ARM_REG_R3,0x89abcdef)]:u.reg_write(reg,v)
     u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
    return
   kind={0x20000204:'ble',0x20000208:'enter',0x2000020c:'leave',0x20000210:'leave2'}.get(a) if source else {0x33850:'ble',0x20000208:'enter',0x2000020c:'leave',0x20000210:'leave2'}.get(a)
   if a==(syms['r1_phone_connection_handle_get'] if source else 0x4cba4):
    st['events'].append(['actual_phone_getter'])
    if st['mutation']==1:u.mem_write(0x200064ba,b'\x78\x56')
    if st['mutation']==2:u.mem_write(FRAME,b'\xfe')
   if not kind:return
   m=st['mutation'];r=[u.reg_read(x) for x in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]]
   if kind=='ble':
    assert r[1:]==[8,1,FRAME];st['events'].append(['ble',r,bytes(u.mem_read(r[3],1)).hex()])
    if m==3:u.mem_write(FRAME,b'\xaa\xbb\xcc\xdd')
   else:
    st['events'].append([kind])
    if m==1 and kind=='enter':u.mem_write(NODE+24,b'\xff')
    if m==2 and kind=='enter':u.mem_write(0x20007e00,struct.pack('<I',ALT));u.mem_write(NODE+20,b'\x00\x00')
    if m==3 and kind=='enter':u.mem_write(0x20006974,struct.pack('<I',0x20000880))
    if m==4 and kind.startswith('leave'):u.mem_write(FRAME,b'\x00')
   u.reg_write(UC_ARM_REG_R0,st['result'])
   for reg,v in [(UC_ARM_REG_R1,0xabcdef01),(UC_ARM_REG_R2,0x12345678),(UC_ARM_REG_R3,0x89abcdef)]:u.reg_write(reg,v)
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  machines=[]
  for source in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,raw);u.mem_map(0x1000000,0x20000);u.mem_write(0x1000000,sections['text']);u.mem_map(0x20000000,0x40000);u.hook_add(UC_HOOK_CODE,hook);machines.append(u)
  cases=[]
  for low,high,value,result,m in itertools.product(range(256),[0,0x12345600,0xffffff00],[0,1,255],[0,5,0xffffffff],range(3)):cases.append(('query_fixture',low|high,value,result,m,1,0))
  for low,value,size,m in itertools.product([0,1,254,255],[0,1,2,127,254,255],[0,1,2,65535],range(5)):cases.append(('query_cached',0x12345600|low,value,0xffffffff,m,size,0))
  for seed,value,phone,result,m in itertools.product([0,0xffffffff,0x12345600,0xabcdef01],[0,1,255,256,0xffffffff,0x12345678],[0,65535,0x1234],[0,1,0xffffffff,0x80000000],range(4)):cases.append(('timeout',seed,value,result,m,1,phone))
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  for number,(kind,seed,value,result,m,size,phone) in enumerate(cases):
   outputs=[]
   for source,u in enumerate(machines):
    u.mem_write(0x20000000,b'\x96'*0x40000)
    for n,a in CLASSES:u.mem_write(a,sections[n])
    u.mem_write(0x20007de8,sections['handles']);u.mem_write(ALT,sections['r_size']);u.mem_write(NODE+20,struct.pack('<H',size));u.mem_write(NODE+24,bytes([value&255]));u.mem_write(0x200064ba,struct.pack('<H',phone));u.mem_write(0x20006974,struct.pack('<I',0x20000800));u.mem_write(0x20000800+28,struct.pack('<II',0x20000209,0x2000020d));u.mem_write(0x20000880+28,struct.pack('<II',0x20000209,0x20000211));states[id(u)]=dict(source=source,events=[],kind=kind,mutation=m,result=result,value=value)
    u.reg_write(UC_ARM_REG_XPSR,0x01000000);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    for reg,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],[value,0x11223344,0x55667788,seed]):u.reg_write(reg,v)
    target=(syms['r1_protocol_time_timeout_callback'] if source else 0x84c82) if kind=='timeout' else (syms['r1_nv_recovery_needed_query_boundary'] if source else 0x7bb20)
    u.emu_start(target|1,0x20000100,count=10000);assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
    mem=bytes(u.mem_read(0x20000000,0x3e000))+bytes(u.mem_read(0x2003f000,0x1000));outputs.append([[u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R3)],states[id(u)]['events'],hashlib.sha256(mem).hexdigest()])
   if outputs[0]!=outputs[1]:(OUT/'counterexample.json').write_text(json.dumps(dict(number=number,case=[kind,seed,value,result,m,size,phone],outputs=outputs),indent=2)+'\n');raise AssertionError((number,kind))
   counts[kind]+=1;obs+=len(outputs[0][1]);digest.update(json.dumps([number,kind,seed,value,result,m,size,phone,outputs[0]],sort_keys=True).encode())
 receipt=dict(comparisons=sum(counts.values()),counts=counts,observations_per_side=obs,trace_sha256=digest.hexdigest(),actual_cached_read_musl_and_phone_accessor=True,source_cold_classes_handles_match=True,query_failure_retains_incoming_r3_byte=True,raw_r0_r3_callee_sp_and_nonstack_ram_checked=True,ble_enqueue_and_critical_callbacks_are_fixtures=True,post_getter_and_critical_mutations_are_explicit=True,no_native_candidate_execution=True,runtime_admission_changed=False,hardware_write_executed=False,cross_call_private_frame_history_verified=False,full_raw_abi_verified=False,instruction_identity=False,whole_image_complete=False,driver_sha256=sha(Path(__file__)),report_sha256=sha(rp),object_sha256=sha(obj),layout_sha256=sha(layout),application_sha256=sha(app))
 (OUT/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
