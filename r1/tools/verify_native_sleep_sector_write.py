#!/usr/bin/env python3
"""Independent eight-slot writer, capacity/header serialization and tail oracle."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-sleep-sector-write';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();SP=0x2003d000;PAY=0x20010000;CTX=0x200067b4;REGION=0x20030000;OPS=REGION+128;OPS2=OPS+64;OPS3=OPS+128;READ=0x20001000;READ2=READ+16;WRITE=READ+32;WRITE2=READ+48;WRITE3=READ+64;REGS=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3];SAVED=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11];states={};U32=0xffffffff;PAYLOAD=bytes((i*17+3)&255 for i in range(65536))
PROVIDERS={0x277aa:'__aeabi_memclr',0x5d87c:'r1_stock_crc16_modbus',0x914ec:'r1_structured_log_mode_get',0x91638:'r1_structured_log_format',0x799d6:'nrf_log_frontend_std_2',0x799c8:'nrf_log_frontend_std_1',0x799e6:'nrf_log_frontend_std_3',0x901e4:'r1_sleep_sector_finalize'}
def header(case,i):return struct.pack('<6I',((256+i*32)<<16)|16,0x55667788,0xffffffff if i==case['free'] else 0x11223344+i,0xffffffff if i==case['free'] else 0x22334455+i,0xaabbccdd,0xe0e0e0e0+i)
def mutate_payload(d):struct.pack_into('<H2I',d,10,0x4321,0x10203040,0x55667788)
def main():
 c=json.loads((OUT/'contracts.json').read_text());obj=OUT/'native_sleep_sector_write.o';app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();proof=[];digest=hashlib.sha256();counts=dict(cases=0,reads=0,data_writes=0,header_writes=0,crc=0,finalize=0,printf=0,std=0)
 with tempfile.TemporaryDirectory() as temp:
  td=Path(temp);ld=td/'proof.ld';ld.write_text('SECTIONS { .body 0x8fe98 : { *(.text.r1_sleep_sector_write) } .success 0xbfaf8 : { *(.r1.sleep.write.success) } /DISCARD/ : { *(.ARM.exidx*) } }\n'+''.join('%s = 0x%x;\n'%(n,a+1) for a,n in PROVIDERS.items())+'__start_log_const_data = 0xc441c;\nr1_sleep_sync_context_prefix = 0x200067b4;\n');elf=td/'proof.elf';subprocess.run(['arm-none-eabi-ld','-T',str(ld),str(obj),'-o',str(elf)],check=True,stderr=subprocess.PIPE);replacements=[]
  for sec,a,n in [('.body',0x8fe98,844),('.success',0xbfaf8,69)]:
   f=td/(sec[1:]+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j',sec,'-O','binary',str(elf),str(f)],check=True);d=f.read_bytes();assert len(d)==n and d==raw[a-0x27000:a-0x27000+n];replacements.append((a,d));proof.append(dict(address=hex(a),size=n,sha256=hashlib.sha256(d).hexdigest()))
  def hook(u,a,size,_):
   if a not in [*PROVIDERS,READ,READ2,WRITE,WRITE2,WRITE3]:return
   s=states[id(u)];case=s['case'];r=[u.reg_read(x) for x in REGS];sp=u.reg_read(UC_ARM_REG_SP);s['trace'].append([a,r,bytes(u.mem_read(sp,32)).hex()]);ret=0x98765432
   if a==0x277aa:assert r[:2]==[SP-72,24];u.mem_write(r[0],bytes(24))
   elif a==0x914ec:ret=case['mode']
   elif a in [READ,READ2]:
    i=s['reads'];s['reads']+=1;counts['reads']+=1;assert r[:3]==[((0x100000+(case['sector']<<12)+16)+i*24)&U32,SP-72,24]
    if case['prefix']:u.mem_write(r[1],header(case,i)[:case['prefix']])
    if case['mutation']&1:u.mem_write(REGION+52,struct.pack('<I',0x110000));u.mem_write(CTX+8,struct.pack('<I',OPS2))
    ret=0xffffffff
   elif a in [WRITE,WRITE2,WRITE3]:
    if r[1]==PAY:
     counts['data_writes']+=1;s['writes'].append([a,r[:3],hashlib.sha256(bytes(u.mem_read(r[1],r[2]))).hexdigest()]);ret=case['data_error']
     if case['mutation']&2:
      d=bytearray(u.mem_read(PAY,32));mutate_payload(d);u.mem_write(PAY,bytes(d))
    else:counts['header_writes']+=1;assert r[1:3]==[SP-72,20];s['writes'].append([a,r[:3],bytes(u.mem_read(r[1],20)).hex()]);ret=case['header_error']
   elif a==0x5d87c:
    counts['crc']+=1;assert r[:2]==[PAY,((case['length']+3)&U32)&65532];ret=case['crc']
    if case['mutation']&4:u.mem_write(CTX+8,struct.pack('<I',OPS3))
   elif a==0x901e4:counts['finalize']+=1;assert r[0]==case['sector'];s['finalized']+=1;ret=case['final_result']
   elif a==0x91638:
    counts['printf']+=1;assert r[1]==r[2];s['logs'].append([a,r[0],r[1],r[3],list(struct.unpack('<2I',u.mem_read(sp,8)))[:2 if r[0]==0xcc00000 else 1 if r[0]==0x4800000 else 0]])
   else:
    counts['std']+=1;assert r[0] in [0x1c0001,0x1c0003];s['logs'].append([a,r[0],r[1],r[2],r[3] if a!=0x799c8 else None,list(struct.unpack('<I',u.mem_read(sp,4))) if a==0x799e6 else []])
   for reg,val in zip(REGS,[ret,0xa1a1a1a1,0xb2b2b2b2,0xc3c3c3c3]):u.reg_write(reg,val)
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  machines=[]
  for side in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x100000);u.mem_write(0x27000,raw);u.mem_map(0x20000000,0x40000)
   if side:
    for a,d in replacements:u.mem_write(a,d)
   u.hook_add(UC_HOOK_CODE,hook);machines.append(u)
  default=dict(sector=0,length=32,free=0,prefix=24,data_error=0,header_error=0,mode=0,mutation=0,crc=0x89abcdef,final_result=1)
  cases=[dict(default,sector=sec,length=n,free=free,prefix=pref,data_error=de,header_error=he,mode=mode,mutation=mut) for sec,n,free,pref,de,he,mode,mut in itertools.product([0,1,255],[0,4,3888],[0,1,7,8],[0,12,24],[0,1],[0,1],[0,7],[0,1,2,7])]
  cases += [dict(default,sector=sec,length=n,free=free,mode=mode,final_result=fr) for sec,n,free,mode,fr in itertools.product([0,1,127,128,255,0xffffffff],[1,3,3889,65532,65533,65535,65536,0xffffffff],[0,7],range(8),[0,1,0xffffffff])]
  for case in cases:
   secshift=(case['sector']<<12)&U32;fixed=(0x100000+secshift+16)&U32;destination=(fixed+192)&U32;aligned=((case['length']+3)&U32)&65532;base=0x100000;scratch=bytearray(24);seq=[0x277aa];writes=[];logs=[];found=None;payload=bytearray(PAYLOAD);finalized=0;result=0
   for i in range(8):
    seq.append(READ2 if case['mutation']&1 and i else READ);scratch[:case['prefix']]=header(case,i)[:case['prefix']]
    if case['mutation']&1:base=0x110000
    if struct.unpack_from('<2I',scratch,8)==(0xffffffff,0xffffffff):found=i;break
    length,offset=struct.unpack_from('<2H',scratch);destination=(base+secshift+length+offset)&U32
   def errorlog(fmt,std,err):
    seq.append(0x914ec)
    if not case['mode']&1:seq.append(0x914ec)
    if case['mode']&5:seq.append(0x91638);logs.append([0x91638,0x4400000,fmt,err,[]])
    seq.append(0x914ec)
    if case['mode']&2:seq.append(0x799c8);logs.append([0x799c8,0x1c0001,std,err,None,[]])
   if found is not None:
    if ((base+secshift+4096)&U32)<((destination+aligned)&U32):
     seq.append(0x914ec)
     if not case['mode']&1:seq.append(0x914ec)
     if case['mode']&5:seq.append(0x91638);logs.append([0x91638,0x4800000,0x900a0,destination,[aligned]])
     seq.append(0x914ec)
     if case['mode']&2:seq.append(0x799d6);logs.append([0x799d6,0x1c0001,0x900c4,destination,aligned,[]])
     seq.append(0x901e4);finalized=1;result=0
    else:
     op=WRITE2 if case['mutation']&1 else WRITE;seq.append(op);writes.append([op,[destination,PAY,aligned],hashlib.sha256(payload[:aligned]).hexdigest()])
     if case['mutation']&2:mutate_payload(payload)
     if case['data_error']:errorlog(0x900e0,0x90114,case['data_error'])
     else:
      struct.pack_into('<2H',scratch,0,aligned,(destination-((base&65535)+secshift))&65535);struct.pack_into('<H',scratch,6,struct.unpack_from('<H',payload,10)[0]);scratch[8:16]=payload[12:20];seq.append(0x5d87c);struct.pack_into('<H',scratch,18,case['crc']&65535)
      op=WRITE3 if case['mutation']&4 else op;seq.append(op);writes.append([op,[(fixed+found*24)&U32,SP-72,20],scratch[:20].hex()])
      if case['header_error']:errorlog(0x90140,0x90174,case['header_error'])
      else:
       seq.append(0x914ec)
       if not case['mode']&1:seq.append(0x914ec)
       if case['mode']&5:seq.append(0x91638);logs.append([0x91638,0xcc00000,0xbfaf8,destination,[case['length'],found+1]])
       seq.append(0x914ec)
       if case['mode']&2:seq.append(0x799e6);logs.append([0x799e6,0x1c0003,0x901a4,destination,case['length'],[found+1]])
       result=1
       if found==7:seq.append(0x901e4);finalized=1;result=case['final_result']
   outputs=[]
   for u in machines:
    u.mem_write(PAY,PAYLOAD);u.mem_write(CTX,struct.pack('<3I',0,REGION,OPS));u.mem_write(REGION,bytes(512));u.mem_write(REGION+52,struct.pack('<I',0x100000))
    for op,read,write in [(OPS,READ,WRITE),(OPS2,READ2,WRITE2),(OPS3,READ2,WRITE3)]:u.mem_write(op+40,struct.pack('<2I',read+1,write+1))
    u.mem_write(SP-128,b'\x96'*256)
    for reg,val in zip(REGS,[case['sector'],PAY,case['length'],0x99aabbcc]):u.reg_write(reg,val)
    for i,reg in enumerate(SAVED):u.reg_write(reg,0x12340000+i)
    u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,0x20000101);s=dict(case=case,reads=0,trace=[],writes=[],logs=[],finalized=0);states[id(u)]=s;u.emu_start(0x8fe99,0x20000100,count=5000)
    assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==SP and u.reg_read(UC_ARM_REG_R0)==result and [u.reg_read(x) for x in SAVED]==[0x12340000+i for i in range(8)],(case,u.reg_read(UC_ARM_REG_R0),result)
    assert [x[0] for x in s['trace']]==seq and s['writes']==writes and s['logs']==logs and s['finalized']==finalized and bytes(u.mem_read(PAY,32))==payload[:32],case
    outputs.append([[u.reg_read(x) for x in REGS],s['trace'],s['writes'],s['logs'],bytes(u.mem_read(CTX,12)).hex(),bytes(u.mem_read(SP-128,256)).hex()])
   assert outputs[0]==outputs[1];counts['cases']+=1;digest.update(json.dumps([case,outputs[0]],sort_keys=True).encode())
 v=dict(comparisons=counts['cases'],counts=counts,trace_sha256=digest.hexdigest(),exact_spans=proof,exact_bytes=913,object_sha256=sha(obj),application_sha256=sha(app),report_sha256=sha(OUT/'report.json'),driver_sha256=sha(Path(__file__)),independent_slot_capacity_header_crc_and_log_oracle=True,io_memclear_crc_mode_log_and_finalizer_are_fixtures=True,new_ram_state_bytes=0,full_raw_abi_or_private_histories_verified=False,whole_image_complete=False,hardware_write_executed=False);(OUT/'verification.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v))
if __name__=='__main__':main()
