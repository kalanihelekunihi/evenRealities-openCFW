#!/usr/bin/env python3
"""Exact local sync frames/config and independent CMSIS callback state oracle."""
import hashlib,itertools,json,random,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-subscriber-sync';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();SP=0x2003d000;MUTEX=0x20006794;CONTROL=0x2001571c;ATTR=0x99bb8;NAME=0xbf784;REGS=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3];SAVED=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11];states={}
def main():
 c=json.loads((OUT/'contracts.json').read_text());obj=OUT/'native_subscriber_sync.o';app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();proof=[];digest=hashlib.sha256();counts=dict(lock=0,unlock=0,current=0,create_calls=0,acquire_calls=0,release_calls=0,current_calls=0)
 with tempfile.TemporaryDirectory() as temp:
  td=Path(temp);ld=td/'layout.ld';ld.write_text('SECTIONS {'+''.join(' .b%d 0x%x : { *(.text.%s) }'%(i,int(x['address'],16),x['symbol']) for i,x in enumerate(c['bodies']))+' .attr 0x99bb8 : { *(.r1.subscriber.attr) } .name 0xbf784 : { *(.r1.subscriber.name) } .mutex 0x20006794 : { *(.r1.subscriber.mutex) } .control 0x2001571c : { *(.r1.subscriber.control) } /DISCARD/ : { *(.ARM.exidx*) } }\nosMutexNew = 0x7d4d7;\nosMutexAcquire = 0x7d489;\nosMutexRelease = 0x7d537;\nxTaskGetCurrentTaskHandle = 0x9879d;\n');elf=td/'proof.elf';subprocess.run(['arm-none-eabi-ld','-T',str(ld),str(obj),'-o',str(elf)],check=True);spans=[]
  for sec,a,n in [*[(f'.b{i}',int(x['address'],16),x['source_span_bytes']) for i,x in enumerate(c['bodies'])],('.attr',ATTR,16),('.name',NAME,12),('.mutex',MUTEX,4),('.control',CONTROL,80)]:
   f=td/(sec[1:]+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j',sec,'-O','binary',str(elf),str(f)],check=True);d=f.read_bytes();assert len(d)==n
   if a<0x20000000:assert d==raw[a-0x27000:a-0x27000+n];spans.append((a,d))
   else:assert d==bytes(n)
   proof.append(dict(section=sec,address=hex(a),size=n,sha256=hashlib.sha256(d).hexdigest()))
  def hook(u,a,size,_):
   if a not in [0x7d4d6,0x7d488,0x7d536,0x9879c]:return
   s=states[id(u)];case=s['case'];r=[u.reg_read(x) for x in REGS];s['calls'].append([a,r]);counts[{0x7d4d6:'create_calls',0x7d488:'acquire_calls',0x7d536:'release_calls',0x9879c:'current_calls'}[a]]+=1
   if a==0x7d4d6:
    assert r[0]==ATTR and bytes(u.mem_read(ATTR,16))==struct.pack('<4I',NAME,0,CONTROL,80) and bytes(u.mem_read(NAME,12))==b'event_mutex\0';ret=case['created']
   else:ret=case['result']
   if case['mutation']:u.mem_write(MUTEX,struct.pack('<I',0x31415926));u.mem_write(CONTROL,b'\x57'*80)
   for reg,val in zip(REGS,[ret,0xa1a1a1a1,0xb2b2b2b2,0xc3c3c3c3]):u.reg_write(reg,val)
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  machines=[]
  for side in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x100000);u.mem_write(0x27000,raw);u.mem_map(0x20000000,0x40000)
   if side:
    for a,d in spans:u.mem_write(a,d)
   u.hook_add(UC_HOOK_CODE,hook);machines.append(u)
  rng=random.Random(0x5dcb0);values=[0,1,2,0xffffffff,0x80000000,0x20010000]+[rng.getrandbits(32) for _ in range(250)];cases=[dict(kind=k,handle=h,created=cr,result=res,mutation=m) for k,h,cr,res,m in itertools.product(['lock','unlock','current'],values,[0,1,0xffffffff],[0,1,0xffffffff],range(2))]
  for case in cases:
   k=case['kind'];h=case['handle'];created=case['created'];mut=case['mutation'];expected_handle=h;expected_seq=[];expected_r0=0
   if k=='lock':
    if not h:expected_seq.append(0x7d4d6);expected_handle=created
    expected_seq.append(0x7d488);expected_r0=case['result']
   elif k=='unlock':
    expected_r0=case['result'] if h else 0
    if h:expected_seq.append(0x7d536)
   else:expected_seq.append(0x9879c);expected_r0=case['result']
   if mut and expected_seq:expected_handle=0x31415926
   expected_control=b'\x57'*80 if mut and expected_seq else b'\x96'*80;results=[]
   for u in machines:
    u.mem_write(MUTEX,struct.pack('<I',h));u.mem_write(CONTROL,b'\x96'*80);u.mem_write(SP-128,b'\x96'*256)
    for reg,val in zip(REGS,[0x11223344,0x55667788,0x99aabbcc,0xddeeff00]):u.reg_write(reg,val)
    for i,reg in enumerate(SAVED):u.reg_write(reg,0x12340000+i)
    u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,0x20000101);s=dict(case=case,calls=[]);states[id(u)]=s;u.emu_start({'lock':0x5dcb1,'unlock':0x5dcd5,'current':0x7d815}[k],0x20000100,count=100)
    assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==SP and [u.reg_read(x) for x in SAVED]==[0x12340000+i for i in range(8)] and u.reg_read(UC_ARM_REG_R0)==expected_r0,case
    assert [x[0] for x in s['calls']]==expected_seq and int.from_bytes(u.mem_read(MUTEX,4),'little')==expected_handle and bytes(u.mem_read(CONTROL,80))==expected_control,case
    for a,r in s['calls']:
     if a==0x7d488:assert r[:2]==[h or created,0xffffffff],(case,r)
     if a==0x7d536:assert r[0]==h
    results.append([[u.reg_read(x) for x in REGS],s['calls'],bytes(u.mem_read(SP-128,256)).hex()])
   assert results[0]==results[1];counts[k]+=1;digest.update(json.dumps([case,results[0]],sort_keys=True).encode())
 v=dict(comparisons=sum(counts[k] for k in ['lock','unlock','current']),counts=counts,trace_sha256=digest.hexdigest(),exact_spans=proof,exact_rom_bytes=88,typed_ram_bytes=84,object_sha256=sha(obj),application_sha256=sha(app),report_sha256=sha(OUT/'report.json'),driver_sha256=sha(Path(__file__)),independent_state_and_call_oracle=True,mutex_and_task_providers_are_fixtures=True,full_raw_abi_or_private_histories_verified=False,whole_image_complete=False,hardware_write_executed=False);(OUT/'verification.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v))
if __name__=='__main__':main()
