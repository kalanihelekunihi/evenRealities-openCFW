#!/usr/bin/env python3
"""Registration linked-list oracle, allocation faults, typed roots/routes proof."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_INVALID
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-subscriber-registration';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();SP=0x2003d000;ROOTS=0x20015708;HEADER=0x20010000;ALT=HEADER+16;NODES=HEADER+32;NEWHEADER=HEADER+128;NEWNODE=HEADER+144;MEMSIZE=192;REGS=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3];SAVED=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11];states={}
def put(d,a,v):struct.pack_into('<I',d,a-HEADER,v&0xffffffff)
def main():
 c=json.loads((OUT/'contracts.json').read_text());obj=OUT/'native_subscriber_registration.o';app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();proof=[];digest=hashlib.sha256();counts=dict(returned=0,allocation_faults=0,lock_calls=0,unlock_calls=0,allocations=0)
 with tempfile.TemporaryDirectory() as temp:
  td=Path(temp);ld=td/'layout.ld';ld.write_text('SECTIONS { .body 0x8af8c : { *(.text.r1_subscriber_register) } .routes 0x99ba8 : { *(.r1.subscriber.routes) } .roots 0x20015708 : { *(.r1.subscriber.roots) } /DISCARD/ : { *(.ARM.exidx*) } }\nr1_subscriber_lock = 0x5dcb1;\nr1_subscriber_unlock = 0x5dcd5;\npvPortMalloc = 0x855a1;\nr1_event_sensor = 0x2000668c;\nr1_event_system = 0x20006608;\n');elf=td/'proof.elf';subprocess.run(['arm-none-eabi-ld','-T',str(ld),str(obj),'-o',str(elf)],check=True,stderr=subprocess.PIPE);replacements=[]
  for sec,a,n in [('.body',0x8af8c,156),('.routes',0x99ba8,16),('.roots',ROOTS,20)]:
   f=td/(sec[1:]+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j',sec,'-O','binary',str(elf),str(f)],check=True);d=f.read_bytes();assert len(d)==n
   if a<0x20000000:assert d==raw[a-0x27000:a-0x27000+n];replacements.append((a,d))
   else:assert d==bytes(20)
   proof.append(dict(section=sec,address=hex(a),size=n,sha256=hashlib.sha256(d).hexdigest()))
  def invalid(u,access,a,size,value,_):states[id(u)]['fault']=[access,a,size,value];return False
  def hook(u,a,size,_):
   if a not in [0x5dcb0,0x5dcd4,0x855a0]:return
   s=states[id(u)];case=s['case'];r=[u.reg_read(x) for x in REGS];s['calls'].append([a,r]);ret=0x98765432
   if a==0x5dcb0:
    counts['lock_calls']+=1
    if case['swap']:u.mem_write(ROOTS+case['index']*4,struct.pack('<I',ALT))
   elif a==0x5dcd4:counts['unlock_calls']+=1
   else:
    counts['allocations']+=1;s['allocs']+=1;assert r[0]==12
    header=ALT if case['swap'] else HEADER if case['present'] else NEWHEADER
    alloc_header=not case['swap'] and not case['present'] and s['allocs']==1
    ret=NEWHEADER if alloc_header else NEWNODE
    if case['fail']==s['allocs']:ret=0
    if not alloc_header and case['mutate']:u.mem_write(header,bytes(4))
   for reg,val in zip(REGS,[ret,0xa1a1a1a1,0xb2b2b2b2,0xc3c3c3c3]):u.reg_write(reg,val)
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  machines=[]
  for side in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x100000);u.mem_write(0x27000,raw);u.mem_map(0x20000000,0x40000)
   if side:
    for a,d in replacements:u.mem_write(a,d)
   u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_INVALID,invalid);machines.append(u)
  cases=[dict(index=idx,present=present,count=count,callback=callback,context=context,fail=fail,swap=swap,mutate=mut) for idx,present,count,callback,context,fail,swap,mut in itertools.product([0,1,4,5,0xffffffff],range(2),[0,1,2,4],[0,0x10001,0x10011,0x10031,0xffffffff],[0,0x20006610],range(3),range(2),range(2))]
  for case in cases:
   mem=bytearray(b'\x96'*MEMSIZE);n=case['count'];first=NODES if n else 0;tail=NODES+(n-1)*16 if n else 0
   for a in [HEADER,ALT]:put(mem,a,first);put(mem,a+4,tail);put(mem,a+8,0x76543210)
   for i in range(n):put(mem,NODES+i*16,0x10001+i*16);put(mem,NODES+i*16+4,0x20006610);put(mem,NODES+i*16+8,NODES+(i+1)*16 if i+1<n else 0)
   roots=bytearray(20)
   if case['index']<5:struct.pack_into('<I',roots,case['index']*4,HEADER if case['present'] else 0)
   expected=bytearray(mem);expected_roots=bytearray(roots);seq=[];fault=False;result=0;allocs=0
   if case['index']<5:
    seq.append(0x5dcb0);head=ALT if case['swap'] else HEADER if case['present'] else NEWHEADER
    if case['swap']:struct.pack_into('<I',expected_roots,case['index']*4,ALT)
    if head==NEWHEADER:
     seq.append(0x855a0);allocs+=1
     if case['fail']==allocs:fault=True
     else:expected[head-HEADER:head-HEADER+12]=bytes(12);struct.pack_into('<I',expected_roots,case['index']*4,head)
    effective_n=n if head!=NEWHEADER else 0
    duplicate=case['callback'] in [0x10001+i*16 for i in range(effective_n)]
    if not fault and duplicate:seq.append(0x5dcd4)
    elif not fault:
     seq.append(0x855a0);allocs+=1
     if case['mutate']:put(expected,head,0)
     if case['fail']==allocs:fault=True
     else:
      put(expected,NEWNODE,case['callback']);put(expected,NEWNODE+4,case['context'] or 0x20006694);put(expected,NEWNODE+8,0)
      if effective_n and not case['mutate']:put(expected,tail+8,NEWNODE)
      else:put(expected,head,NEWNODE)
      put(expected,head+4,NEWNODE);seq.append(0x5dcd4);result=1
   outputs=[]
   for u in machines:
    u.mem_write(HEADER,bytes(mem));u.mem_write(ROOTS,bytes(roots));u.mem_write(SP-128,b'\x96'*256)
    for reg,val in zip(REGS,[case['index'],case['callback'],case['context'],0x87654321]):u.reg_write(reg,val)
    for i,reg in enumerate(SAVED):u.reg_write(reg,0x12340000+i)
    u.reg_write(UC_ARM_REG_BASEPRI,0);u.reg_write(UC_ARM_REG_CONTROL,0);u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,0x20000101);s=dict(case=case,calls=[],fault=None,allocs=0);states[id(u)]=s
    try:u.emu_start(0x8af8d,0x20000100,count=1000)
    except UcError:assert s['fault'],case
    assert bool(s['fault'])==fault and [x[0] for x in s['calls']]==seq and s['allocs']==allocs,case
    if fault:assert s['fault'][1:]==[0xffffffff,4,0] and u.reg_read(UC_ARM_REG_BASEPRI)==64,case
    else:assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==SP and u.reg_read(UC_ARM_REG_R0)==result and [u.reg_read(x) for x in SAVED]==[0x12340000+i for i in range(8)],case
    assert bytes(u.mem_read(HEADER,MEMSIZE))==expected and bytes(u.mem_read(ROOTS,20))==expected_roots,case
    outputs.append([[u.reg_read(x) for x in REGS],u.reg_read(UC_ARM_REG_SP),u.reg_read(UC_ARM_REG_BASEPRI),s['calls'],s['fault'],bytes(u.mem_read(SP-128,256)).hex()])
   assert outputs[0]==outputs[1],case;counts['allocation_faults' if fault else 'returned']+=1;digest.update(json.dumps([case,outputs[0]],sort_keys=True).encode())
 v=dict(comparisons=counts['returned']+counts['allocation_faults'],counts=counts,trace_sha256=digest.hexdigest(),exact_spans=proof,exact_rom_bytes=172,typed_ram_bytes=20,object_sha256=sha(obj),application_sha256=sha(app),report_sha256=sha(OUT/'report.json'),driver_sha256=sha(Path(__file__)),independent_list_allocation_and_callback_oracle=True,lock_unlock_and_heap_are_fixtures=True,full_raw_abi_or_private_histories_verified=False,whole_image_complete=False,hardware_write_executed=False);(OUT/'verification.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v))
if __name__=='__main__':main()
