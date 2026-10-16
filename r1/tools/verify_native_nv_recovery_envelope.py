#!/usr/bin/env python3
"""Build-only native parser/query comparisons; recovery dispatch is an emulated fixture."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-nv-recovery-envelope-runtime';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();P=0x20003001
LOGS={'null_ring':(0x84208,47),'null_sdk':(0x84238,41),'fields_ring':(0x84264,54),'fields_sdk':(0x8429c,48)}
def main():
 rp=OUT/'report.json';b=json.loads(rp.read_text());obj=OUT/'nv-recovery-envelope-source.o';assert sha(obj)==b['envelope_object_sha256']
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';layout=ROOT/'r1/source-config/runtime/native_nv_recovery_envelope_verification.ld';states={};digest=hashlib.sha256();counts={'envelope':0,'query':0};obs=0
 with tempfile.TemporaryDirectory() as tmp:
  d=Path(tmp);elf=d/'test.elf';subprocess.run(['arm-none-eabi-ld','-T',str(layout),str(obj),'-o',str(elf)],check=True);sections={}
  for n in ['text']+list(LOGS):
   p=d/(n+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j','.'+n,'-O','binary',str(elf),str(p)],check=True);sections[n]=p.read_bytes()
  syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3};assert syms['r1_connection_field8']==0x200064ba
  for n,(a,z) in LOGS.items():assert sections[n]==raw[a-0x27000:a-0x27000+z]
  def fields(u):return bytes(u.mem_read(P+12,5)).hex()
  def hook(u,a,size,_):
   st=states[id(u)];source=st['source'];assert not source or not 0x27000<=a<0xc4d08
   if a==(syms['r1_packet_field12_get'] if source else 0x82bd4):st['after_accessor']=u.reg_read(UC_ARM_REG_LR)&~1
   if st['after_accessor']==a:
    st['after_accessor']=None
    if st['mutation']==6:u.mem_write(P+8,bytes(2));u.mem_write(P+12,b'\xff')
   kind=({0x20000200:'dispatch',0x20000204:'response',0x20000208:'mode',0x2000020c:'ring',0x20000210:'sdk0',0x20000214:'sdk3'} if source else {0x7c450:'dispatch',0x828b4:'response',0x914ec:'mode',0x91638:'ring',0x799c0:'sdk0',0x799e6:'sdk3'}).get(a)
   if not kind:return
   r=[u.reg_read(x) for x in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];ret=st['result'];m=st['mutation']
   if kind=='mode':
    ret=st['modes'][st['mi']%len(st['modes'])];st['mi']+=1;st['events'].append(['mode',ret,fields(u)])
    if m==1:u.mem_write(P+12,bytes([st['mi']&255])+struct.pack('<HH',100+st['mi'],200+st['mi']))
   elif kind=='dispatch':
    assert r[3]==P+17;st['events'].append(['dispatch',r,bytes(u.mem_read(r[3],min(r[1],16))).hex()])
   elif kind=='response':
    assert r[3]==0;st['events'].append(['response',r[0],bytes(u.mem_read(r[1],8)).hex(),r[2:]])
    if m==3:u.mem_write(0x200064ba,b'\x78\x56')
   elif kind=='ring':
    if r[1]==0x84208:st['events'].append(['ring',r[:3]])
    else:
     assert r[:3]==[0x0cc00000,0x84264,0x84264];extra=struct.unpack('<II',u.mem_read(u.reg_read(UC_ARM_REG_SP),8));st['events'].append(['ring',r,list(extra)])
    if m==2:u.mem_write(P+12,b'\x02\x74\x00\xff\xff')
   elif kind=='sdk0':st['events'].append(['sdk0',r[:2]])
   else:
    assert r[:2]==[0x001c0003,0x8429c];extra=struct.unpack('<I',u.mem_read(u.reg_read(UC_ARM_REG_SP),4))[0];st['events'].append(['sdk3',r,extra])
    if m==4:u.mem_write(P+12,b'\x01\x00\x00\x34\x12')
   if m==5 and kind in ['ring','sdk0','sdk3']:u.mem_write(P+8,b'\x0c\x00');u.mem_write(P+12,b'\xfe\xff\xff\x00\x00')
   u.reg_write(UC_ARM_REG_R0,ret)
   for reg,v in [(UC_ARM_REG_R1,0xabcdef01),(UC_ARM_REG_R2,0x12345678),(UC_ARM_REG_R3,0x89abcdef)]:u.reg_write(reg,v)
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  machines=[]
  for source in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,raw);u.mem_map(0x1000000,0x20000);u.mem_write(0x1000000,sections['text']);u.mem_map(0x20000000,0x40000)
   for n,(a,z) in LOGS.items():u.mem_write(a,sections[n])
   u.hook_add(UC_HOOK_CODE,hook);machines.append(u)
  modes=[[0],[1],[2],[4],[7],[0,4,2],[1,0],[0xffffffff,0x80000000]];cases=[]
  for number,(packetlen,cmd,length,crc,m) in enumerate(itertools.product([0,1,12,13,16,17,24,65535],[0,1,2,3,255],[0,1,116,65535],[0,1,65535],range(7))):cases.append(('envelope',packetlen,cmd,length,crc,m,modes[number%8],[0,1,0xffffffff,0x80000000][number%4],0xffff))
  for packetlen,mode,m in itertools.product([0,24],modes,range(7)):cases.append(('envelope',packetlen,2,116,1,m,mode,0x12345678,0))
  for phone,result,m in itertools.product([0,65535,0x1234],[0,1,0xffffffff,0x80000000],range(7)):cases.append(('query',24,2,116,1,m,modes[0],result,phone))
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  for number,(kind,packetlen,cmd,length,crc,m,mode,result,phone) in enumerate(cases):
   results=[]
   for source,u in enumerate(machines):
    u.mem_write(0x20000000,b'\x96'*0x40000);u.mem_write(P,bytes(range(64)));u.mem_write(P+8,struct.pack('<H',packetlen));u.mem_write(P+12,bytes([cmd])+struct.pack('<HH',length,crc));u.mem_write(0x200064ba,struct.pack('<H',phone));states[id(u)]=dict(source=source,events=[],after_accessor=None,mutation=m,modes=mode,mi=0,result=result)
    u.reg_write(UC_ARM_REG_XPSR,0x01000000);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    for reg,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],[0x1000ffff,P,0x55667788,0x99aabbcc]):u.reg_write(reg,v)
    target=(syms['r1_native_nv_recovery_envelope_handler'] if source else 0x84150) if kind=='envelope' else (syms['r1_phone_link_ready_query'] if source else 0x83c86)
    u.emu_start(target|1,0x20000100,count=10000);assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
    resultregs=[u.reg_read(UC_ARM_REG_R0)]
    if kind=='query':resultregs += [u.reg_read(reg) for reg in [UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];assert resultregs==[int(result!=0),0,0,0]
    memory=bytes(u.mem_read(0x20000000,0x3e000))+bytes(u.mem_read(0x2003f000,0x1000));results.append([resultregs,states[id(u)]['events'],hashlib.sha256(memory).hexdigest()])
   if results[0]!=results[1]:(OUT/'counterexample.json').write_text(json.dumps(dict(number=number,case=[kind,packetlen,cmd,length,crc,m,mode,result,phone],results=results),indent=2)+'\n');raise AssertionError((number,kind,packetlen,cmd,length,crc,m,mode,result,phone))
   counts[kind]+=1;obs+=len(results[0][1]);digest.update(json.dumps([number,kind,packetlen,cmd,length,crc,m,mode,result,phone,results[0]],sort_keys=True).encode())
 receipt=dict(comparisons=sum(counts.values()),counts=counts,observations_per_side=obs,trace_sha256=digest.hexdigest(),actual_accessor_phone_getter_inverse_header=True,lower_native_dispatch_is_fixture_only=True,post_accessor_mutations_are_explicit_fixtures=True,short_backing_reads_only_in_mapped_emulator_fixture=True,fresh_envelope_fields_after_logs_checked=True,query_r0_r1_r2_r3_and_callee_sp_checked=True,raw_r0_and_nonstack_ram_checked=True,no_native_candidate_execution=True,bounded_planner_modified=False,hardware_write_executed=False,driver_sha256=sha(Path(__file__)),report_sha256=sha(rp),object_sha256=sha(obj),layout_sha256=sha(layout),application_sha256=sha(app),native_persistent_dispatch_implemented=False,full_raw_abi_verified=False,instruction_identity=False,whole_image_complete=False)
 (OUT/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
