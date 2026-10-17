#!/usr/bin/env python3
"""Sample encoder/sender composition with independent header and result oracle."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-health-get-encoders';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();SP=0x2003d000;DATA=0x20010000;REGS=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3];SAVED=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
def main():
 c=json.loads((OUT/'contracts.json').read_text());raw=(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes();obj=OUT/'native_health_get_encoders.o';proof=[];digest=hashlib.sha256();counts=dict(encoder=0,sender=0,response=0,flag=0,invalid_handle=0)
 with tempfile.TemporaryDirectory() as temp:
  td=Path(temp);ld=td/'proof.ld';ld.write_text('SECTIONS {'+''.join(' .b%d %s : { *(.text.%s) }'%(i,x['address'],x['symbol']) for i,x in enumerate(c['bodies']))+' /DISCARD/ : { *(.ARM.exidx*) } }\n'+''.join('%s = 0x%x;\n'%(n,int(a,16)|1) for a,n in c['providers'].items() if a!='0x82ef4'));elf=td/'proof.elf';subprocess.run(['arm-none-eabi-ld','-T',str(ld),str(obj),'-o',str(elf)],check=True,stderr=subprocess.PIPE);replacements=[]
  for i,x in enumerate(c['bodies']):
   a=int(x['address'],16);f=td/(str(i)+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j','.b'+str(i),'-O','binary',str(elf),str(f)],check=True);d=f.read_bytes();assert len(d)==x['source_span_bytes'] and d==raw[a-0x27000:a-0x27000+len(d)];replacements.append((a,d));proof.append(dict(address=hex(a),size=len(d),sha256=hashlib.sha256(d).hexdigest()))
  machines=[];states=[]
  for side in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x100000);u.mem_write(0x27000,raw);u.mem_map(0x20000000,0x40000)
   if side:
    for a,d in replacements:u.mem_write(a,d)
   s={};machines.append(u);states.append(s)
   def hook(u,a,size,s):
    r=[u.reg_read(x) for x in REGS];sp=u.reg_read(UC_ARM_REG_SP);case=s['case']
    if a==0x4cba4:s['events'].append(['phone']);result=case['handle'];u.mem_write(DATA,bytes([case['handle']&255])*16)
    elif a==0x8280c:s['events'].append(['flag',r,bytes(u.mem_read(sp,4)).hex()]);result=case['result']
    else:s['events'].append(['response',r[0],bytes(u.mem_read(r[1],8)).hex(),r[2],r[3],bytes(u.mem_read(r[2],min(r[3],16))).hex() if r[2] else None]);result=case['result']
    u.reg_write(UC_ARM_REG_R0,result);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
   for a in [0x4cba4,0x8280c,0x828b4]:u.hook_add(UC_HOOK_CODE,hook,s,begin=a,end=a)
  cases=[]
  for entry,ptr,flag,request,handle,result in itertools.product([0x83930,0x83972,0x83c20],[0,DATA],[0,1,2,255,0xffffffff],[0,65535,0x98765432],[0,1,65535,0x10000,0xffffffff],[0,1,2,0xffffffff]):cases.append(dict(entry=entry,ptr=ptr,flag=flag,request=request,handle=handle,result=result,command={0x83930:0x102,0x83972:0x402,0x83c20:0x202}[entry],length=9 if entry==0x83972 else 8))
  for command,flag,request,handle,length,result,ptr in itertools.product([0,0x102,0x12345678,0xffffffff],[0,1,2,255,0xffffffff],[0,65535,0x98765432],[0,1,65535,0x10000,0xffffffff],[0,9,0xffffffff],[0,1,2,0xffffffff],[0,DATA]):cases.append(dict(entry=0x82ef4,ptr=ptr,flag=flag,request=request,handle=handle,result=result,command=command,length=length))
  for case in cases:
   outputs=[];encoder=case['entry']!=0x82ef4;handle=case['handle'];ptr=case['ptr'];expected=[['phone']] if encoder else [];result=case['result'];args=[ptr,case['flag'],case['request'],0x99aabbcc] if encoder else [handle,case['command'],case['flag'],case['request']]
   if encoder and not ptr:expected.append(['flag',[handle,case['command'],2,case['request']],'00000000']);want=int(result!=0);counts['flag']+=1
   elif handle==65535:want=0;counts['invalid_handle']+=1
   else:
    h=bytes([((case['flag']^1)|2)&255,2,(case['command']>>8)&255,case['command']&255])+struct.pack('<I',case['request']&65535);payload=bytes([handle&255])*min(case['length'],16) if encoder else b'\xa5'*min(case['length'],16);expected.append(['response',handle,h.hex(),ptr,case['length'],payload.hex() if ptr else None]);want=int(result==0);counts['response']+=1
   for u,s in zip(machines,states):
    s.update(case=case,events=[]);u.mem_write(DATA,b'\xa5'*16);u.mem_write(SP-128,b'\x96'*256);u.mem_write(SP,struct.pack('<II',ptr,case['length']))
    for reg,val in zip(REGS,args):u.reg_write(reg,val)
    for i,reg in enumerate(SAVED):u.reg_write(reg,0x12340000+i)
    u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,0x20000101);u.emu_start(case['entry']|1,0x20000100,count=300)
    assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==SP and u.reg_read(UC_ARM_REG_R0)==want and [u.reg_read(x) for x in SAVED]==[0x12340000+i for i in range(8)],case
    assert s['events']==expected,(case,s['events'],expected);outputs.append([s['events'],[u.reg_read(x) for x in REGS],bytes(u.mem_read(SP-128,256)).hex(),bytes(u.mem_read(DATA,16)).hex()])
   assert outputs[0]==outputs[1],case
   counts['encoder' if encoder else 'sender']+=1;digest.update(json.dumps([case,outputs[0]],sort_keys=True).encode())
 v=dict(application_sha256=c['application_sha256'],comparisons=len(cases),counts=counts,trace_sha256=digest.hexdigest(),exact_spans=proof,exact_bytes=280,object_sha256=sha(obj),report_sha256=sha(OUT/'report.json'),driver_sha256=sha(Path(__file__)),actual_nested_sample_sender_executes=True,independent_header_result_and_provider_oracle=True,phone_flag_and_response_providers_are_fixtures=True,full_raw_abi_or_private_histories_verified=False,whole_image_complete=False,hardware_write_executed=False);(OUT/'verification.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v))
if __name__=='__main__':main()
