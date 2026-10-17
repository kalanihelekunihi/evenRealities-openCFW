#!/usr/bin/env python3
"""Consumer destructive traversal, fresh packet-head loads and native faults."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_INVALID
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-subscriber-consume';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();SP=0x2003d000;PACKET=0x20010000;NODE=PACKET+64;CTX=PACKET+144;CB=0x20001000;REGS=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3];SAVED=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11];states={}
def put(d,a,v):struct.pack_into('<I',d,a-PACKET,v&0xffffffff)
def main():
 obj=OUT/'native_subscriber_consume.o';app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();digest=hashlib.sha256();counts=dict(returned=0,faults=0,callbacks=0,locks=0,unlocks=0,current_calls=0)
 with tempfile.TemporaryDirectory() as tmp:
  td=Path(tmp);ld=td/'proof.ld';ld.write_text('SECTIONS { .body 0x8b0fc : { *(.text.r1_event_service_0008b0fc) } /DISCARD/ : { *(.ARM.exidx*) } }\nr1_subscriber_current_thread = 0x7d815;\nr1_subscriber_lock = 0x5dcb1;\nr1_subscriber_unlock = 0x5dcd5;\n');elf=td/'proof.elf';subprocess.run(['arm-none-eabi-ld','-T',str(ld),str(obj),'-o',str(elf)],check=True,stderr=subprocess.PIPE);f=td/'body.bin';subprocess.run(['arm-none-eabi-objcopy','-j','.body','-O','binary',str(elf),str(f)],check=True);replacement=f.read_bytes();assert len(replacement)==60 and replacement==raw[0x8b0fc-0x27000:0x8b138-0x27000]
  def invalid(u,access,a,size,value,_):states[id(u)]['fault']=[access,a,size,value];return False
  def hook(u,a,size,_):
   if a not in [0x5dcb0,0x5dcd4,0x7d814,CB,CB+16,CB+32,CB+48]:return
   s=states[id(u)];case=s['case'];r=[u.reg_read(x) for x in REGS];s['calls'].append([a,r]);ret=0x98765432
   if a==0x7d814:ret=case['current'];counts['current_calls']+=1
   elif a==0x5dcb0:
    counts['locks']+=1
    if case['lock_skip']:u.mem_write(PACKET,struct.pack('<I',NODE+16 if len(case['kinds'])>1 else 0))
   elif a==0x5dcd4:counts['unlocks']+=1;ret=case['result']
   else:
    counts['callbacks']+=1;assert r[:2]==[PACKET+6,a+1],(case,a,r)
    if case['mutation']==1:u.mem_write(PACKET,struct.pack('<I',NODE+48))
    elif case['mutation']==2:u.mem_write(PACKET,struct.pack('<I',0x30000000))
    elif case['mutation']==3:u.mem_write(NODE+(a-CB)//16*16+8,bytes(4))
   for reg,val in zip(REGS,[ret,0xa1a1a1a1,0xb2b2b2b2,0xc3c3c3c3]):u.reg_write(reg,val)
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  machines=[]
  for side in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x100000);u.mem_write(0x27000,raw);u.mem_map(0x20000000,0x40000)
   if side:u.mem_write(0x8b0fc,replacement)
   u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_INVALID,invalid);machines.append(u)
  cases=[dict(kinds=k,current=cur,present=pres,lock_skip=skip,mutation=mut,result=result,length=length) for k,cur,pres,skip,mut,result,length in itertools.product(itertools.product(range(4),repeat=3),[0,0x11223344,0x55667788],range(2),range(2),range(4),[0,1,0xffffffff],[0,1,65535])]
  cases += [dict(kinds=(),current=0,present=1,lock_skip=0,mutation=0,result=res,length=0) for res in [0,1,0xffffffff]]
  for case in cases:
   mem=bytearray(b'\x96'*192);put(mem,PACKET,NODE if case['kinds'] else 0);struct.pack_into('<H',mem,4,case['length']);put(mem,CTX,0x11223344);put(mem,CTX+4,0x55667788)
   for i,k in enumerate(case['kinds']):put(mem,NODE+i*16,CB+i*16+1 if k else 0);put(mem,NODE+i*16+4,0x30000000 if k==3 else CTX+(k-1)*4 if k else 0);put(mem,NODE+i*16+8,NODE+(i+1)*16 if i+1<len(case['kinds']) else 0)
   put(mem,NODE+48+8,0);expected=bytearray(mem);seq=[];fault=False;result=0
   if case['present']:
    seq=[0x7d814,0x5dcb0];current=NODE if case['kinds'] else 0
    if case['lock_skip']:current=NODE+16 if len(case['kinds'])>1 else 0;put(expected,PACKET,current)
    while current:
     i=(current-NODE)//16;k=case['kinds'][i]
     if k==3:fault=True;break
     local=(k==1 and case['current']==0x11223344) or (k==2 and case['current']==0x55667788)
     fresh=current
     if local:
      seq.append(CB+i*16)
      if case['mutation']==1:fresh=NODE+48;put(expected,PACKET,fresh)
      elif case['mutation']==2:put(expected,PACKET,0x30000000);fault=True;break
      elif case['mutation']==3:put(expected,current+8,0)
     current=struct.unpack_from('<I',expected,fresh-PACKET+8)[0];put(expected,PACKET,current)
    if not fault:seq.append(0x5dcd4);result=case['result']
   results=[]
   for u in machines:
    u.mem_write(PACKET,bytes(mem));u.mem_write(SP-128,b'\x96'*256)
    for reg,val in zip(REGS,[PACKET if case['present'] else 0,0x12345678,0x23456789,0x3456789a]):u.reg_write(reg,val)
    for i,reg in enumerate(SAVED):u.reg_write(reg,0x12340000+i)
    u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,0x20000101);s=dict(case=case,calls=[],fault=None);states[id(u)]=s
    try:u.emu_start(0x8b0fd,0x20000100,count=1000)
    except UcError:assert s['fault'],case
    assert bool(s['fault'])==fault and [x[0] for x in s['calls']]==seq,case
    if fault:assert s['fault'][1] in [0x30000008,0x30000000],(case,s['fault'])
    else:assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==SP and u.reg_read(UC_ARM_REG_R0)==result and [u.reg_read(x) for x in SAVED]==[0x12340000+i for i in range(8)],case
    assert bytes(u.mem_read(PACKET,192))==expected,case
    results.append([[u.reg_read(x) for x in REGS],u.reg_read(UC_ARM_REG_SP),s['calls'],s['fault'],bytes(u.mem_read(SP-128,256)).hex()])
   assert results[0]==results[1];counts['faults' if fault else 'returned']+=1;digest.update(json.dumps([case,results[0]],sort_keys=True).encode())
 v=dict(comparisons=counts['returned']+counts['faults'],counts=counts,trace_sha256=digest.hexdigest(),exact_bytes=60,exact_span_sha256=hashlib.sha256(replacement).hexdigest(),object_sha256=sha(obj),application_sha256=sha(app),report_sha256=sha(OUT/'report.json'),driver_sha256=sha(Path(__file__)),independent_traversal_and_mutation_oracle=True,lock_unlock_current_and_callbacks_are_fixtures=True,full_raw_abi_or_private_histories_verified=False,whole_image_complete=False,hardware_write_executed=False);(OUT/'verification.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v))
if __name__=='__main__':main()
