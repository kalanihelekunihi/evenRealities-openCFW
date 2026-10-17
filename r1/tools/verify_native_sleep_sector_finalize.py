#!/usr/bin/env python3
"""Finalizer minimum/partial-read/header oracle and live callback-table tests."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-sleep-sector-finalize';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();SP=0x2003d000;CTX=0x200067b4;REGION=0x20013000;REGION2=REGION+64;OPS=0x20014000;OPS2=OPS+64;READ=0x20001000;READ2=READ+16;WRITE=READ+32;WRITE2=READ+48;REGS=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3];SAVED=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11];states={};PROVIDERS={0x914ec:'r1_structured_log_mode_get',0x91638:'r1_structured_log_format',0x799c8:'nrf_log_frontend_std_1'}
def data(case,i):return struct.pack('<4I',0xccffaabb,0x66889977,[0xffffffff,(i*17+7)&0xffffffff,0xfffffffe if i else 0xffffffff,0][case['pattern']],0x12345678)
def main():
 c=json.loads((OUT/'contracts.json').read_text());obj=OUT/'native_sleep_sector_finalize.o';parent=BASE/'native-sleep-record/native_sleep_record.o';app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();digest=hashlib.sha256();counts=dict(cases=0,reads=0,writes=0,printf=0,std=0);proof=[]
 with tempfile.TemporaryDirectory() as temp:
  td=Path(temp);countobj=td/'count.o';subprocess.run(['arm-none-eabi-ld','-r','--gc-sections','-u','r1_sleep_sector_count',str(parent),'-o',str(countobj)],check=True);ld=td/'proof.ld';ld.write_text('SECTIONS { .body 0x901e4 : { *(.text.r1_sleep_sector_finalize) } .count 0x8fe14 : { *(.text.r1_sleep_sector_count) } /DISCARD/ : { *(.ARM.exidx*) } }\n'+''.join('%s = 0x%x;\n'%(n,a+1) for a,n in PROVIDERS.items())+'__start_log_const_data = 0xc441c;\nr1_sleep_sync_context_prefix = 0x200067b4;\n');elf=td/'proof.elf';subprocess.run(['arm-none-eabi-ld','-T',str(ld),str(obj),str(countobj),'-o',str(elf)],check=True,stderr=subprocess.PIPE);replacements=[]
  for sec,a,n in [('.body',0x901e4,292),('.count',0x8fe14,20)]:
   f=td/(sec[1:]+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j',sec,'-O','binary',str(elf),str(f)],check=True);d=f.read_bytes();assert len(d)==n and d==raw[a-0x27000:a-0x27000+n];replacements.append((a,d));proof.append(dict(address=hex(a),size=n,sha256=hashlib.sha256(d).hexdigest()))
  def hook(u,a,size,_):
   if a not in [*PROVIDERS,READ,READ2,WRITE,WRITE2]:return
   s=states[id(u)];case=s['case'];r=[u.reg_read(x) for x in REGS];sp=u.reg_read(UC_ARM_REG_SP);s['trace'].append([a,r,bytes(u.mem_read(sp,40)).hex()]);ret=0x98765432
   if a==0x914ec:
    ret=case['mode']
    if case['mutate']:u.mem_write(CTX+8,struct.pack('<I',OPS2))
   elif a in [READ,READ2]:
    i=s['reads'];s['reads']+=1;counts['reads']+=1;assert r[:3]==[(0x200000 if case['mutate'] and i else 0x100000)+i*4096,SP-80,16]
    if case['prefix']:u.mem_write(r[1],data(case,i)[:case['prefix']])
    if case['mutate']:u.mem_write(CTX+4,struct.pack('<2I',REGION2,OPS2));u.mem_write(REGION2+56,bytes(4))
    ret=case['read_result']
   elif a in [WRITE,WRITE2]:
    counts['writes']+=1;s['writes'].append([a,r[:3],bytes(u.mem_read(r[1],16)).hex()]);assert r[1:3]==[SP-64,16];ret=case['write_result']
    if case['mutate']:u.mem_write(r[1]+8,b'\x5a'*4)
   elif a==0x91638:counts['printf']+=1;assert r[:3]==[0xc400000,0x902b0,0x902b0];s['logs'].append([a,r[3]])
   else:counts['std']+=1;assert r[:2]==[0x1c0003,0x902e4];s['logs'].append([a,r[2]])
   for reg,val in zip(REGS,[ret,0xa1a1a1a1,0xb2b2b2b2,0xc3c3c3c3]):u.reg_write(reg,val)
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  machines=[]
  for side in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x100000);u.mem_write(0x27000,raw);u.mem_map(0x20000000,0x40000)
   if side:
    for a,d in replacements:u.mem_write(a,d)
   u.hook_add(UC_HOOK_CODE,hook);machines.append(u)
  default=dict(count=0,pattern=0,prefix=16,read_result=0,write_result=0,mode=0,mutate=0,sector=0)
  cases=[dict(default,count=n,pattern=p,prefix=prefix,read_result=rr,write_result=wr,mode=mo,mutate=mut,sector=sec) for n,p,prefix,rr,wr,mo,mut,sec in itertools.product([0,1,2,3],range(4),[0,8,12,16],[0,0xffffffff],[0,1,0xffffffff],range(8),range(2),[0,0xffffffff])]
  cases += [dict(default,count=n,pattern=p,prefix=prefix,mutate=mut,mode=mo,sector=255) for n,p,prefix,mut,mo in itertools.product(range(256),[0,1],[0,12,16],range(2),[0,7])]
  for case in cases:
   scratch=bytearray(16);minimum=0xffffffff;seq=[];logs=[]
   for i in range(case['count']):seq.append(READ2 if case['mutate'] and i else READ);scratch[:case['prefix']]=data(case,i)[:case['prefix']];minimum=min(minimum,struct.unpack_from('<I',scratch,8)[0])
   minimum=0 if minimum==0xffffffff else minimum;counter=(minimum+1)&0xffffffff;record=struct.pack('<4I',0xccffaabb,0x66889977,counter,0)
   seq.append(0x914ec)
   if not case['mode']&1:seq.append(0x914ec)
   if case['mode']&5:seq.append(0x91638);logs.append([0x91638,counter])
   seq.append(0x914ec)
   if case['mode']&2:seq.append(0x799c8);logs.append([0x799c8,counter])
   op=WRITE2 if case['mutate'] else WRITE;seq.append(op);writes=[[op,[(0x100000+(case['sector']<<12))&0xffffffff,SP-64,16],record.hex()]];outputs=[]
   for u in machines:
    u.mem_write(CTX,struct.pack('<3I',0,REGION,OPS));u.mem_write(REGION,bytes(128));u.mem_write(REGION+52,struct.pack('<2I',0x100000,case['count']<<12));u.mem_write(REGION2+52,struct.pack('<2I',0x200000,case['count']<<12));u.mem_write(OPS,bytes(128));u.mem_write(OPS+40,struct.pack('<2I',READ+1,WRITE+1));u.mem_write(OPS2+40,struct.pack('<2I',READ2+1,WRITE2+1));u.mem_write(SP-128,b'\x96'*256)
    for reg,val in zip(REGS,[case['sector'],0x11223344,0x55667788,0x99aabbcc]):u.reg_write(reg,val)
    for i,reg in enumerate(SAVED):u.reg_write(reg,0x12340000+i)
    u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,0x20000101);s=dict(case=case,trace=[],reads=0,writes=[],logs=[]);states[id(u)]=s;u.emu_start(0x901e5,0x20000100,count=20000)
    assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==SP and u.reg_read(UC_ARM_REG_R0)==int(case['write_result']==0) and [u.reg_read(x) for x in SAVED]==[0x12340000+i for i in range(8)],case
    assert [x[0] for x in s['trace']]==seq and s['writes']==writes and s['logs']==logs and bytes(u.mem_read(SP-80,16))==scratch,case
    outputs.append([[u.reg_read(x) for x in REGS],s['trace'],s['writes'],s['logs'],bytes(u.mem_read(CTX,12)).hex(),bytes(u.mem_read(SP-128,256)).hex()])
   assert outputs[0]==outputs[1];counts['cases']+=1;digest.update(json.dumps([case,outputs[0]],sort_keys=True).encode())
 v=dict(comparisons=counts['cases'],counts=counts,trace_sha256=digest.hexdigest(),exact_spans=proof,exact_new_bytes=292,exact_joint_bytes=312,object_sha256=sha(obj),count_parent_object_sha256=sha(parent),application_sha256=sha(app),report_sha256=sha(OUT/'report.json'),driver_sha256=sha(Path(__file__)),independent_minimum_partial_read_header_and_boolean_oracle=True,actual_sector_count_executes=True,read_write_mode_and_log_providers_are_fixtures=True,new_ram_state_bytes=0,full_raw_abi_or_private_histories_verified=False,whole_image_complete=False,hardware_write_executed=False);(OUT/'verification.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v))
if __name__=='__main__':main()
