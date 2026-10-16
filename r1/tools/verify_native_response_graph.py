#!/usr/bin/env python3
"""Execute phone/header/response, gates, encoding, CRC, copy and callback dispatch."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-response-graph-runtime';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ENTRIES={'response':('r1_protocol_send_response',0x828b4),'header':('r1_protocol_response_send_0x100',0x84c0c),'phone':('r1_phone_cmd_send_op1',0x83896)}
LOGS={'alloc_ring':(0x82a28,43),'alloc_sdk':(0x82a54,37),'tx_ring':(0x82a7c,58),'tx_sdk':(0x82ab8,52),'send_ring':(0x82aec,53),'send_sdk':(0x82b24,47)}
H=0x20003001;I=0x20004001;M=0x20010000

def main():
 rp=OUT/'report.json';b=json.loads(rp.read_text());obj=OUT/'response-graph-source.o';assert sha(obj)==b['graph_object_sha256']
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';layout=ROOT/'r1/source-config/runtime/native_response_graph_verification.ld';states={};digest=hashlib.sha256();counts={n:0 for n in ENTRIES};obs=0
 with tempfile.TemporaryDirectory() as tmp:
  d=Path(tmp);elf=d/'test.elf';subprocess.run(['arm-none-eabi-ld','-T',str(layout),str(obj),'-o',str(elf)],check=True);sections={}
  for n in ['text']+list(LOGS):
   p=d/(n+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j','.'+n,'-O','binary',str(elf),str(p)],check=True);sections[n]=p.read_bytes()
  syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
  for n,(a,z) in LOGS.items():assert sections[n]==raw[a-0x27000:a-0x27000+z]
  def hook(u,a,size,_):
   st=states[id(u)];source=st['source'];assert not source or not 0x27000<=a<0xc4d08
   kind=({0x20000200:'alloc',0x20000204:'free',0x20000208:'mode',0x2000020c:'ring',0x20000210:'sdk1',0x20000214:'sdk2',0x20000218:'sdk4'} if source else {0x855a0:'alloc',0x95d48:'free',0x914ec:'mode',0x91638:'ring',0x799c8:'sdk1',0x799d6:'sdk2',0x799f8:'sdk4'}).get(a)
   if a==0x2000021c:kind='callback'
   if not kind:return
   r=[u.reg_read(x) for x in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];sp=u.reg_read(UC_ARM_REG_SP);ret=st['result'];m=st['mutation']
   if kind=='alloc':
    ret=M if st['allocation'] else 0;st['events'].append(['alloc',r[0],ret])
    if m==1:u.mem_write(H,bytes.fromhex('a50356783412bcde'));u.mem_write(0x200064ba,b'\x56\x34')
   elif kind=='free':assert r[0]==M;st['events'].append(['free',r[0]])
   elif kind=='mode':
    ret=st['modes'][st['mi']%len(st['modes'])];st['mi']+=1;st['events'].append(['mode',ret])
    if m==2:u.mem_write(M+1,bytes([st['mi']]));u.mem_write(M+3,bytes([0x70+st['mi']]))
   elif kind=='callback':
    assert r[1]==M and r[3]==0x2000021d;st['events'].append(['callback',r,bytes(u.mem_read(M,r[2])).hex()])
    if m==3:u.mem_write(0x20006c20,bytes(4));u.mem_write(M+6,b'\xab\xcd')
   else:
    name=next(n for n,(addr,z) in LOGS.items() if addr==r[1]);n=2 if name.startswith('alloc') else 4 if name.startswith('tx') else 1
    if kind=='ring':args=[r[3]]+(list(struct.unpack('<'+'I'*(n-1),u.mem_read(sp,4*(n-1)))) if n>1 else []);assert r[1]==r[2]
    else:args=r[2:2+min(n,2)]+(list(struct.unpack('<II',u.mem_read(sp,8))) if n==4 else [])
    st['events'].append([kind,r[:2],args])
    if m==4:u.mem_write(M+5,b'\xf1\x34\x56');u.mem_write(H+2,b'\x12\x34')
   u.reg_write(UC_ARM_REG_R0,ret)
   for reg,v in [(UC_ARM_REG_R1,0xabcdef01),(UC_ARM_REG_R2,0x12345678),(UC_ARM_REG_R3,0x89abcdef)]:u.reg_write(reg,v)
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  machines=[]
  for source in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,raw);u.mem_map(0x1000000,0x20000);u.mem_write(0x1000000,sections['text']);u.mem_map(0x20000000,0x40000)
   for n,(a,z) in LOGS.items():u.mem_write(a,sections[n])
   u.hook_add(UC_HOOK_CODE,hook);machines.append(u)
  modes=[[0],[1],[2],[4],[7],[0,4,2]];cases=[]
  for kind,gates,allocation,hookptr,result,mode,m in itertools.product(ENTRIES,[(65535,65535),(0,65535),(65535,1)],(False,True),(0,0x2000021d),(0,1,0xffffffff),modes,range(5)):cases.append((kind,gates,allocation,hookptr,result,mode,m))
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  for number,(kind,gates,allocation,hookptr,result,mode,m) in enumerate(cases):
   handle=[0,65535,0x1000ffff][number%3];length=[0,1,7,15,255,65524][number%6];version=[0,1,3,4][number%4];nonnull=number%7!=0;results=[]
   for source,u in enumerate(machines):
    u.mem_write(0x20000000,b'\x96'*0x40000);u.mem_write(H,bytes([0xa5,version,0x12,0x34,0x78,0x56,0xbc,0xde]));u.mem_write(I,bytes(range(256))*2);u.mem_write(0x200064ba,struct.pack('<HH',*gates));u.mem_write(0x20006b88,struct.pack('<H',(number*257)&65535));u.mem_write(0x20006ba0,b'\x00\x64\x64\x64');u.mem_write(0x20006c20,struct.pack('<I',hookptr));states[id(u)]=dict(source=source,events=[],allocation=allocation,result=result,modes=mode,mi=0,mutation=m)
    u.reg_write(UC_ARM_REG_XPSR,0x01000000);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    args=[handle,H if nonnull else 0,I,length] if kind=='response' else [handle,0x123456,0xa5,(number*257)&65535] if kind=='header' else [I if nonnull else 0,0xa5,0x123456,0x99aabbcc]
    if kind=='header':u.mem_write(0x2003f000,struct.pack('<II',I if nonnull else 0,length))
    for reg,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],args):u.reg_write(reg,v)
    u.emu_start((syms[ENTRIES[kind][0]] if source else ENTRIES[kind][1])|1,0x20000100,count=100000);assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
    memory=bytes(u.mem_read(0x20000000,0x3e000))+bytes(u.mem_read(0x2003f000,0x1000));results.append([u.reg_read(UC_ARM_REG_R0),states[id(u)]['events'],hashlib.sha256(memory).hexdigest()])
   if results[0]!=results[1]:(OUT/'counterexample.json').write_text(json.dumps(dict(number=number,case=[kind,gates,allocation,hookptr,result,mode,m],length=length,version=version,results=results),indent=2)+'\n');raise AssertionError((number,kind,gates,allocation,hookptr,result,mode,m))
   counts[kind]+=1;obs+=len(results[0][1]);digest.update(json.dumps([number,kind,gates,allocation,hookptr,result,mode,m,results[0]],sort_keys=True).encode())
 receipt=dict(comparisons=sum(counts.values()),counts=counts,observations_per_side=obs,trace_sha256=digest.hexdigest(),actual_response_header_phone_encoder_gates_crc_memory_hook=True,only_allocator_logging_and_lower_callback_are_fixtures=True,raw_r0_callee_sp_and_observed_nonstack_ram_checked=True,private_header_pointer_not_compared=True,no_native_candidate_execution=True,driver_sha256=sha(Path(__file__)),report_sha256=sha(rp),object_sha256=sha(obj),layout_sha256=sha(layout),application_sha256=sha(app),whole_allocator_ble_or_rtos_graph_executed=False,full_raw_abi_verified=False,instruction_identity=False,whole_image_complete=False)
 (OUT/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
