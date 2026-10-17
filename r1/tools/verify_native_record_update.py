#!/usr/bin/env python3
"""Record validation and update frame with independent predicate/callback oracle."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-record-update';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();SP=0x2003d000;OLD=0x20010000;NEW=OLD+32;REGS=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3];SAVED=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
def main():
 c=json.loads((OUT/'contracts.json').read_text());raw=(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes();obj=OUT/'native_record_update.o';proof=[];digest=hashlib.sha256();counts=dict(validate=0,update=0,compare=0,persist=0,apply=0)
 with tempfile.TemporaryDirectory() as temp:
  td=Path(temp);ld=td/'proof.ld';ld.write_text('SECTIONS {'+''.join(' .b%d %s : { *(.text.%s) }'%(i,x['address'],x['symbol']) for i,x in enumerate(c['bodies']))+' /DISCARD/ : { *(.ARM.exidx*) } }\n'+''.join('%s = 0x%x;\n'%(n,int(a,16)|1) for a,n in c['providers'].items() if a!='0x6c640'));elf=td/'proof.elf';subprocess.run(['arm-none-eabi-ld','-T',str(ld),str(obj),'-o',str(elf)],check=True,stderr=subprocess.PIPE);replacements=[]
  for i,x in enumerate(c['bodies']):
   a=int(x['address'],16);f=td/(str(i)+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j','.b'+str(i),'-O','binary',str(elf),str(f)],check=True);d=f.read_bytes();assert len(d)==x['source_span_bytes'] and d==raw[a-0x27000:a-0x27000+len(d)];replacements.append((a,d));proof.append(dict(address=hex(a),size=len(d),sha256=hashlib.sha256(d).hexdigest()))
  machines=[];states=[]
  for side in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x100000);u.mem_write(0x27000,raw);u.mem_map(0x20000000,0x40000)
   if side:
    for a,d in replacements:u.mem_write(a,d)
   s={};machines.append(u);states.append(s)
   def hook(u,a,size,s):
    r=[u.reg_read(x) for x in REGS];case=s['case'];event=[hex(a)]
    if a==0x2781a:
     assert r[:3]==[case['oldptr'],case['newptr'],12];event+=[bytes(u.mem_read(r[0],12)).hex(),bytes(u.mem_read(r[1],12)).hex()];result=case['compare']
     if case['mutation']==1:u.mem_write(case['newptr'],b'\xff'*12)
    elif a==0x73604:
     assert r[0]==case['newptr'];event+=[bytes(u.mem_read(r[0],12)).hex()];result=0x87654321
     if case['mutation']==2:u.mem_write(case['newptr'],b'\xdd'*12)
    else:assert r[:2]==[case['oldptr'],case['newptr']];event+=[bytes(u.mem_read(r[1],12)).hex()];result=case['apply_result']
    s['events'].append(event);u.reg_write(UC_ARM_REG_R0,result);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
   for a in [0x2781a,0x73604,0x6c53c]:u.hook_add(UC_HOOK_CODE,hook,s,begin=a,end=a)
  records=[]
  for field,value in itertools.product(range(4),range(256)):
   d=bytearray([40,1,170,70]+[0x96]*8);d[field]=value;records.append(bytes(d))
  records += [bytes([a,b,h,w]+[0x96]*8) for a,b,h,w in itertools.product([10,11,99,100],[0,1,2],[100,101,219,220],[30,31,149,150])]
  cases=[dict(entry=0x6c640,data=d.hex(),oldptr=OLD,newptr=NEW,compare=1,mutation=0,apply_result=0) for d in records]
  for data,oldptr,newptr,compare,mutation,result in itertools.product([bytes([40,1,170,70]+[0x96]*8),bytes([10,1,170,70]+[0x96]*8)],[0,OLD],[0,NEW,OLD],[0,1,0xffffffff],[0,1,2],[0,1,0xffffffff]):cases.append(dict(entry=0x6c66c,data=data.hex(),oldptr=oldptr,newptr=newptr,compare=compare,mutation=mutation,apply_result=result))
  for case in cases:
   data=bytes.fromhex(case['data']);a,b,h,w=data[:4];valid=10<a<100 and b<=1 and 100<h<220 and 30<w<150;update=case['entry']==0x6c66c;expected=[];want=int(valid)
   if update:
    if not case['oldptr']:want=0
    elif not case['newptr']:want=case['oldptr']
    elif not valid:want=0
    else:
     old=data if case['newptr']==OLD else b'\xa5'*12;expected=[['0x2781a',old.hex(),data.hex()]];counts['compare']+=1;want=case['compare']
     if want:
      current=b'\xff'*12 if case['mutation']==1 else data;expected.append(['0x73604',current.hex()]);current=b'\xdd'*12 if case['mutation']==2 else current;expected.append(['0x6c53c',current.hex()]);want=case['apply_result'];counts['persist']+=1;counts['apply']+=1
   outputs=[]
   for u,s in zip(machines,states):
    s.update(case=case,events=[]);u.mem_write(OLD,b'\xa5'*64);u.mem_write(case['newptr'] or NEW,data);u.mem_write(SP-64,b'\x96'*128)
    for reg,val in zip(REGS,[case['oldptr'] if update else case['newptr'],case['newptr'],0x55667788,0x99aabbcc]):u.reg_write(reg,val)
    for i,reg in enumerate(SAVED):u.reg_write(reg,0x12340000+i)
    u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,0x20000101);u.emu_start(case['entry']|1,0x20000100,count=200)
    assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==SP and u.reg_read(UC_ARM_REG_R0)==want and [u.reg_read(x) for x in SAVED]==[0x12340000+i for i in range(8)],case
    assert s['events']==expected,(case,s['events'],expected);outputs.append([s['events'],[u.reg_read(x) for x in REGS],bytes(u.mem_read(SP-64,128)).hex(),bytes(u.mem_read(OLD,64)).hex()])
   assert outputs[0]==outputs[1],case
   counts['update' if update else 'validate']+=1;digest.update(json.dumps([case,outputs[0]],sort_keys=True).encode())
 v=dict(application_sha256=c['application_sha256'],comparisons=len(cases),counts=counts,trace_sha256=digest.hexdigest(),exact_spans=proof,exact_bytes=104,object_sha256=sha(obj),report_sha256=sha(OUT/'report.json'),driver_sha256=sha(Path(__file__)),actual_nested_validator_executes=True,independent_range_guard_and_callback_oracle=True,memcmp_persist_and_apply_providers_are_fixtures=True,full_raw_abi_or_private_histories_verified=False,whole_image_complete=False,hardware_write_executed=False);(OUT/'verification.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v))
if __name__=='__main__':main()
