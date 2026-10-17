#!/usr/bin/env python3
"""Charge notification frame, status precedence and seven-byte payload oracle."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-charge-notification';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();SP=0x2003d000;REGS=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3];SAVED=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
def main():
 c=json.loads((OUT/'contracts.json').read_text());raw=(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes();obj=OUT/'native_charge_notification.o';proof=[];digest=hashlib.sha256();count=0
 with tempfile.TemporaryDirectory() as temp:
  td=Path(temp);ld=td/'proof.ld';ld.write_text('SECTIONS { .body 0x838e0 : { *(.text.r1_event_service_000838e0) } .template 0x9a44c : { *(.r1.charge.notification.template) } /DISCARD/ : { *(.ARM.exidx*) } }\n'+''.join('%s = 0x%x;\n'%(n,int(a,16)|1) for a,n in c['providers'].items()));elf=td/'proof.elf';subprocess.run(['arm-none-eabi-ld','-T',str(ld),str(obj),'-o',str(elf)],check=True,stderr=subprocess.PIPE);replacements=[]
  for sec,a,size in [('body',0x838e0,80),('template',0x9a44c,8)]:
   f=td/(sec+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j','.'+sec,'-O','binary',str(elf),str(f)],check=True);d=f.read_bytes();assert len(d)==size and d==raw[a-0x27000:a-0x27000+size];replacements.append((a,d));proof.append(dict(address=hex(a),size=size,sha256=hashlib.sha256(d).hexdigest()))
  machines=[];states=[]
  for side in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x100000);u.mem_write(0x27000,raw);u.mem_map(0x20000000,0x40000)
   if side:
    for a,d in replacements:u.mem_write(a,d)
   s={};machines.append(u);states.append(s)
   def hook(u,a,size,s):
    case=s['case'];r=[u.reg_read(x) for x in REGS];sp=u.reg_read(UC_ARM_REG_SP);event=[hex(a)]
    if a==0x91270:result=case['byte']
    elif a==0x91256:result=case['active']
    elif a==0x91244:result=case['full']
    elif a==0x4cba4:
     result=case['handle']
     if case['mutation']:u.mem_write(SP-24,b'\xde\xad\xbe\xef\x55\x66\x77')
    else:
     assert r==[case['handle'],127,1,0] and struct.unpack('<II',u.mem_read(sp,8))==(SP-24,7);payload=bytes(u.mem_read(SP-24,7));want=bytes([case['byte']&255,3 if case['full'] else 1 if case['active'] else 2,1,0,0,0,0]) if not case['mutation'] else b'\xde\xad\xbe\xef\x55\x66\x77';assert payload==want,case;event+=[r,payload.hex()];result=case['result']
    s['events'].append(event);u.reg_write(UC_ARM_REG_R0,result)
    for reg,val in zip(REGS[1:],[0x11223344,0x55667788,0x99aabbcc]):u.reg_write(reg,val)
    u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
   for a in c['providers']:u.hook_add(UC_HOOK_CODE,hook,s,begin=int(a,16),end=int(a,16))
  cases=itertools.product(list(range(256))+[256,0x12345678,0xffffffff],[0,1,0xffffffff],[0,1,0xffffffff],[0,65535],[0,1,0xffffffff],[0,1])
  for byte,active,full,handle,result,mutation in cases:
   case=dict(byte=byte,active=active,full=full,handle=handle,result=result,mutation=mutation);outputs=[]
   for u,s in zip(machines,states):
    s.update(case=case,events=[]);u.mem_write(SP-64,b'\x96'*128)
    for reg,val in zip(REGS,[0xabcdef01,0x11223344,0x55667788,0x99aabbcc]):u.reg_write(reg,val)
    for i,reg in enumerate(SAVED):u.reg_write(reg,0x12340000+i)
    u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,0x20000101);u.emu_start(0x838e1,0x20000100,count=120)
    assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==SP and u.reg_read(UC_ARM_REG_R0)==result and [u.reg_read(x) for x in SAVED]==[0x12340000+i for i in range(8)],case
    assert [e[0] for e in s['events']]==['0x91270','0x91256','0x91244','0x4cba4','0x84c0c'];outputs.append([s['events'],[u.reg_read(x) for x in REGS],bytes(u.mem_read(SP-64,128)).hex()])
   assert outputs[0]==outputs[1],case
   count+=1;digest.update(json.dumps([case,outputs[0]],sort_keys=True).encode())
 v=dict(application_sha256=c['application_sha256'],comparisons=count,trace_sha256=digest.hexdigest(),exact_spans=proof,exact_bytes=88,object_sha256=sha(obj),report_sha256=sha(OUT/'report.json'),driver_sha256=sha(Path(__file__)),independent_status_payload_and_callback_mutation_oracle=True,all_charge_bytes_checked=True,charge_state_phone_and_protocol_providers_are_fixtures=True,full_raw_abi_or_private_histories_verified=False,whole_image_complete=False,hardware_write_executed=False);(OUT/'verification.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v))
if __name__=='__main__':main()
