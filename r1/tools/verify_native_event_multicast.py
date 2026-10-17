#!/usr/bin/env python3
"""Native multicast frame, independent traversal/copy oracle, provider fixtures."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-event-multicast';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();SP=0x2003d000;ROOTS=0x20015708;HEAD=0x20011000;NODE=0x20012000;CTX=0x20013000;HEAP=0x20018000;PAY=0x30000000;CB=0x20001000
REGS=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3];SAVED=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
PROVIDERS={'r1_subscriber_lock':0x5dcb0,'r1_subscriber_unlock':0x5dcd4,'r1_subscriber_current_thread':0x7d814,'memmove':0x2775c,'pvPortMalloc':0x855a0,'vPortFree':0x95d48,'r1_event_publish':0x8d8fc};states={}
def word(u,a):return int.from_bytes(u.mem_read(a,4),'little')
def put(u,a,v):u.mem_write(a,struct.pack('<I',v))
def main():
 c=json.loads((OUT/'contracts.json').read_text());obj=OUT/'native_event_multicast.o';app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';image=app.read_bytes();digest=hashlib.sha256();counts=dict(cases=0,callbacks=0,publishes=0,copies=0,allocations=0)
 with tempfile.TemporaryDirectory() as tmp:
  td=Path(tmp);ld=td/'proof.ld';ld.write_text('SECTIONS { .body 0x8b028 : { *(.text.r1_event_service_0008b028) } /DISCARD/ : { *(.ARM.exidx*) } }\n'+''.join('%s = 0x%x;\n'%(n,a+1) for n,a in PROVIDERS.items())+'r1_subscriber_roots = 0x20015708;\nr1_subscriber_routes = 0x99ba8;\n');elf=td/'proof.elf';subprocess.run(['arm-none-eabi-ld','-T',str(ld),str(obj),'-o',str(elf)],check=True,stderr=subprocess.PIPE);binary=td/'body.bin';subprocess.run(['arm-none-eabi-objcopy','-j','.body','-O','binary',str(elf),str(binary)],check=True);replacement=binary.read_bytes();assert replacement==image[0x8b028-0x27000:0x8b0fc-0x27000] and len(replacement)==212
  def hook(u,a,size,_):
   if a not in [*PROVIDERS.values(),CB,CB+16,CB+32,CB+48]:return
   s=states[id(u)];case=s['case'];r=[u.reg_read(x) for x in REGS];ret=0;s['calls'].append([a,r[:3]])
   if a==0x2775c:u.mem_write(r[0],bytes(u.mem_read(r[1],r[2])) if r[2] else b'');counts['copies']+=1
   elif a==0x855a0:assert r[0]==(case['length']+8)&65535;ret=HEAP if case['allocate'] else 0;counts['allocations']+=1
   elif a==0x7d814:ret=0xabcdef01
   elif a==0x8d8fc:counts['publishes']+=1;ret=case['queue_result']
   elif a in [CB,CB+16,CB+32,CB+48]:
    i=(a-CB)//16;assert r[:2]==[PAY,CTX];counts['callbacks']+=1
    if case['mutation']:put(u,NODE+i*16+8,0)
   elif a==0x95d48:assert r[0]==HEAP
   for reg,val in zip(REGS,[ret,0xa1a1a1a1,0xb2b2b2b2,0xc3c3c3c3]):u.reg_write(reg,val)
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  machines=[]
  for side in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x100000);u.mem_write(0x27000,image);u.mem_map(0x20000000,0x40000);u.mem_map(PAY,0x20000)
   if side:u.mem_write(0x8b028,replacement)
   u.hook_add(UC_HOOK_CODE,hook);machines.append(u)
  cases=[dict(kinds=k,length=n,allocate=al,present=1,mutation=0,queue_result=0) for k,n,al in itertools.product(itertools.product(range(5),repeat=4),[0,4,12],range(2))]
  cases += [dict(kinds=k,length=n,allocate=al,present=pres,mutation=mut,queue_result=q) for k,n,al,pres,mut,q in itertools.product([(1,2,3,1),(2,2,3,3),(0,0,0,0)], [0,1,2,3,4,5,255,65527,65528,65535,65536],range(2),range(2),range(2),[0,1,0xffffffff])]
  cases += [dict(kinds=(),length=n,allocate=al,present=1,mutation=0,queue_result=0) for n,al in itertools.product([0,4,12,65536],range(2))]
  for case in cases:
   n=case['length'];payload=bytes((i*17+3)&255 for i in range(n));root=bytearray(b'\x65'*16);struct.pack_into('<I',root,0,NODE if case['kinds'] else 0);nodes=bytearray(b'\x45'*64);contexts=struct.pack('<4I',0xabcdef01,0x12345678,0x99887766,0x11111111);ctxs=[0,CTX,0x20006694,0x20006610,CTX+4]
   for i,k in enumerate(case['kinds']):struct.pack_into('<3I',nodes,i*16,CB+i*16+1 if k else 0,ctxs[k],NODE+(i+1)*16 if i+1<len(case['kinds']) else 0)
   expected_root=bytearray(root);expected_nodes=bytearray(nodes);expected_heap=bytearray(b'\x96'*(n+8));seq=[]
   if case['present']:
    seq.append(0x5dcb0)
    if n<=4:expected_root[8:12]=bytes(4);expected_root[8:8+n]=payload;seq.append(0x2775c)
    seq.append(0x7d814)
    if case['kinds']:
     seq.append(0x855a0)
     if case['allocate']:struct.pack_into('<IH',expected_heap,0,NODE,n&65535);expected_heap[6:6+n]=payload;seq.append(0x2775c)
     mask=set()
     for i,k in enumerate(case['kinds']):
      if k==1:
       seq.append(CB+i*16)
       if case['mutation']:struct.pack_into('<I',expected_nodes,i*16+8,0);break
      elif k in [2,3] and k not in mask:
       mask.add(k)
       if case['allocate']:seq.append(0x8d8fc)
     if case['allocate']:seq.append(0x95d48)
    seq.append(0x5dcd4)
   results=[]
   for u in machines:
    put(u,ROOTS+7*4,HEAD if case['present'] else 0);u.mem_write(HEAD,bytes(root));u.mem_write(NODE,bytes(nodes));u.mem_write(CTX,contexts);put(u,0x20006694,0x12345678);put(u,0x20006610,0x99887766);u.mem_write(HEAP,b'\x96'*(n+8));u.mem_write(PAY,payload or b'\0');u.mem_write(SP-128,b'\x96'*256)
    for reg,val in zip(REGS,[7,PAY,n,0x87654321]):u.reg_write(reg,val)
    for i,reg in enumerate(SAVED):u.reg_write(reg,0x12340000+i)
    u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,0x20000101);s=dict(case=case,calls=[]);states[id(u)]=s;u.emu_start(0x8b029,0x20000100,count=2000)
    assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==SP and [u.reg_read(x) for x in SAVED]==[0x12340000+i for i in range(8)] and u.reg_read(UC_ARM_REG_R0)==case['present'],case
    assert [x[0] for x in s['calls']]==seq,(case,s['calls'],seq)
    assert bytes(u.mem_read(HEAD,16))==expected_root and bytes(u.mem_read(NODE,64))==expected_nodes and bytes(u.mem_read(HEAP,n+8))==expected_heap,case
    for a,r in s['calls']:
     if a==0x8d8fc:assert r in [[2,HEAP,(n+8)&65535],[0x1000,HEAP,(n+8)&65535]],(case,r)
    results.append([[u.reg_read(x) for x in REGS],s['calls'],bytes(u.mem_read(SP-128,256)).hex()])
   assert results[0]==results[1];digest.update(json.dumps([case,results[0]],sort_keys=True).encode());counts['cases']+=1
 v=dict(comparisons=counts['cases'],counts=counts,trace_sha256=digest.hexdigest(),exact_bytes=212,exact_span_sha256=hashlib.sha256(replacement).hexdigest(),object_sha256=sha(obj),application_sha256=sha(app),report_sha256=sha(OUT/'report.json'),driver_sha256=sha(Path(__file__)),independent_traversal_and_copy_oracle=True,providers_and_callbacks_are_fixtures=True,full_private_history_or_raw_abi_verified=False,whole_image_complete=False,hardware_write_executed=False)
 (OUT/'verification.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v))
if __name__=='__main__':main()
