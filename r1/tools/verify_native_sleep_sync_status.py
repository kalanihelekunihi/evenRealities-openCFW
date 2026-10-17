#!/usr/bin/env python3
"""Sleep sync native record oracle, partial reads, fresh ops and actual wrapper."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-sleep-sync-status';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();SP=0x2003d000;PAY=0x20010000;CTX=0x200067b4;OPS=0x20013000;ALT=OPS+64;READ=0x20001000;READ2=READ+16;WRITE=READ+32;WRITE2=READ+48;REGS=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3];SAVED=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11];states={}
def main():
 c=json.loads((OUT/'contracts.json').read_text());wrapper=BASE/'native-health-service-wrappers/native_health_service_wrappers.o';obj=OUT/'native_sleep_sync_status.o';w=json.loads((BASE/'native-health-service-wrappers/contracts.json').read_text());bodies=c['bodies']+w['bodies'];app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();digest=hashlib.sha256();proof=[];counts=dict(direct=0,wrapper=0,reads=0,writes=0,clears=0,printf=0,std=0)
 providers={0x914ec:'r1_structured_log_mode_get',0x91638:'r1_structured_log_format',0x799c0:'nrf_log_frontend_std_0',0x799c8:'nrf_log_frontend_std_1',0x277aa:'__aeabi_memclr',0x8d8fc:'r1_event_publish'}
 with tempfile.TemporaryDirectory() as temp:
  td=Path(temp);ld=td/'proof.ld';ld.write_text('SECTIONS {'+''.join(' .b%d %s : { *(.text.%s) }'%(i,x['address'],x['symbol']) for i,x in enumerate(bodies))+' .context 0x200067b4 : { *(.r1.sleep.sync.context) } /DISCARD/ : { *(.ARM.exidx*) } }\n'+''.join('%s = 0x%x;\n'%(n,a+1) for a,n in providers.items())+'__start_log_const_data = 0xc441c;\n');elf=td/'proof.elf';subprocess.run(['arm-none-eabi-ld','-T',str(ld),str(obj),str(wrapper),'-o',str(elf)],check=True,stderr=subprocess.PIPE);replacements=[]
  for i,x in enumerate(bodies):
   a=int(x['address'],16);f=td/(str(i)+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j','.b'+str(i),'-O','binary',str(elf),str(f)],check=True);d=f.read_bytes();assert len(d)==x['source_span_bytes'] and d==raw[a-0x27000:a-0x27000+len(d)];replacements.append((a,d));proof.append(dict(address=hex(a),size=len(d),sha256=hashlib.sha256(d).hexdigest()))
  f=td/'context.bin';subprocess.run(['arm-none-eabi-objcopy','-j','.context','-O','binary',str(elf),str(f)],check=True);assert f.read_bytes()==bytes(12)
  def hook(u,a,size,_):
   if a not in [*providers,READ,READ2,WRITE,WRITE2]:return
   s=states[id(u)];case=s['case'];r=[u.reg_read(x) for x in REGS];sp=u.reg_read(UC_ARM_REG_SP);s['trace'].append([a,r,sp,bytes(u.mem_read(sp,32)).hex()]);ret=0x98765432
   if a==0x277aa:assert r[:2]==[SP-64,24];u.mem_write(r[0],bytes(24));counts['clears']+=1
   elif a==0x914ec:ret=case['mode']
   elif a in [READ,READ2]:
    i=s['reads'];s['reads']+=1;counts['reads']+=1;assert r[:3]==[0x100000+i*32,SP-64,24]
    f1,f2=struct.unpack('<2I',u.mem_read(PAY+i*12+4,8));header=struct.pack('<6I',0xdec0de00+i,i,f1^int(case['match']==1),f2^int(case['match']==2),0x98760000+i,0xffffffff)
    if case['prefix']:u.mem_write(r[1],header[:case['prefix']])
    if case['mutate']:u.mem_write(PAY+i*12,struct.pack('<2I',r[0]+7,f1^1));u.mem_write(CTX+8,struct.pack('<I',ALT))
    ret=case['read_result']
   elif a in [WRITE,WRITE2]:
    counts['writes']+=1;s['writes'].append([a,r[:3],word:=int.from_bytes(u.mem_read(r[1],4),'little')]);assert r[1:3]==[SP-40,4]
    if case['write_mutate']:u.mem_write(r[1],struct.pack('<I',(word+1)&0xffffffff))
    ret=case['write_result']
   elif a==0x91638:counts['printf']+=1;s['logs'].append([a,r[0],r[3] if r[0]==0x4400000 else None])
   elif a in [0x799c0,0x799c8]:counts['std']+=1;assert r[0]==0x1c0001;s['logs'].append([a,r[0],r[2] if a==0x799c8 else None])
   else:raise AssertionError(a)
   for reg,val in zip(REGS,[ret,0xa1a1a1a1,0xb2b2b2b2,0xc3c3c3c3]):u.reg_write(reg,val)
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  machines=[]
  for side in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x100000);u.mem_write(0x27000,raw);u.mem_map(0x20000000,0x40000)
   if side:
    for a,d in replacements:u.mem_write(a,d)
   u.hook_add(UC_HOOK_CODE,hook);machines.append(u)
  cases=[dict(length=n,match=match,prefix=pref,write_result=wr,mutate=mut,write_mutate=wm,mode=mode,read_result=rr,present=1,entry=entry) for n,match,pref,wr,mut,wm,mode,rr,entry in itertools.product([0,1,11,12,24,36],range(3),[0,8,12,16,24],[0,1,0xffffffff],range(2),range(2),range(8),[0,0xffffffff],['direct','wrapper'])]
  cases += [dict(length=n,match=match,prefix=pref,write_result=1,mutate=mut,write_mutate=1,mode=mode,read_result=0xffffffff,present=1,entry=entry) for n,match,pref,mode,mut,entry in itertools.product([3071,3072,3073,0xffffffff],range(3),[0,12,24],[0,7],range(2),['direct','wrapper'])]
  cases += [dict(length=n,match=0,prefix=24,write_result=0,mutate=0,write_mutate=0,mode=mode,read_result=0,present=0,entry=entry) for n,mode,entry in itertools.product([0,1,12,0xffffffff],range(8),['direct','wrapper'])]
  for case in cases:
   n=(case['length']//12)&255;packet=bytearray().join(struct.pack('<3I',0x100000+i*32,i*7,i*17) for i in range(n));expected=bytearray(packet);header=bytearray(24);marker=0x11223344;seq=[];expected_writes=[];expected_logs=[]
   if not case['present'] or not case['length']:
    seq+=[0x914ec]
    if case['mode']&1:pass
    else:seq+=[0x914ec]
    if case['mode']&5:seq+=[0x91638];expected_logs.append([0x91638,0x4000000,None])
    seq+=[0x914ec]
    if case['mode']&2:seq+=[0x799c0];expected_logs.append([0x799c0,0x1c0001,None])
   else:
    seq+=[0x277aa]
    for i in range(n):
     seq.append(READ2 if case['mutate'] and i else READ);addr,f1,f2=struct.unpack_from('<3I',expected,i*12);data=struct.pack('<6I',0xdec0de00+i,i,f1^int(case['match']==1),f2^int(case['match']==2),0x98760000+i,0xffffffff);header[:case['prefix']]=data[:case['prefix']]
     if case['mutate']:struct.pack_into('<2I',expected,i*12,addr+7,f1^1)
     _,new1,new2=struct.unpack_from('<3I',expected,i*12)
     if struct.unpack_from('<2I',header,8)!=(new1,new2):continue
     a=WRITE2 if case['mutate'] else WRITE;seq.append(a);expected_writes.append([a,[addr+20,SP-40,4],marker])
     if case['write_mutate']:marker=(marker+1)&0xffffffff
     if case['write_result']:
      seq+=[0x914ec]
      if not case['mode']&1:seq+=[0x914ec]
      if case['mode']&5:seq+=[0x91638];expected_logs.append([0x91638,0x4400000,addr+7 if case['mutate'] else addr])
      seq+=[0x914ec]
      if case['mode']&2:seq+=[0x799c8];expected_logs.append([0x799c8,0x1c0001,addr+7 if case['mutate'] else addr])
   outputs=[]
   for u in machines:
    u.mem_write(PAY,bytes(packet) or b'\0');u.mem_write(CTX,struct.pack('<3I',0,0,OPS));u.mem_write(OPS,bytes(128));u.mem_write(OPS+40,struct.pack('<2I',READ+1,WRITE+1));u.mem_write(ALT+40,struct.pack('<2I',READ2+1,WRITE2+1));u.mem_write(SP-128,b'\x96'*256)
    for reg,val in zip(REGS,[PAY if case['present'] else 0,case['length'],0x55667788,0x99aabbcc]):u.reg_write(reg,val)
    for i,reg in enumerate(SAVED):u.reg_write(reg,0x12340000+i)
    u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,0x20000101);s=dict(case=case,trace=[],reads=0,writes=[],logs=[]);states[id(u)]=s;u.emu_start(0x5b6f5 if case['entry']=='direct' else 0x8e1e1,0x20000100,count=20000)
    assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==SP and [u.reg_read(x) for x in SAVED]==[0x12340000+i for i in range(8)],case
    assert [x[0] for x in s['trace']]==seq and s['writes']==expected_writes and s['logs']==expected_logs and bytes(u.mem_read(PAY,len(packet)))==expected,case
    if case['present'] and case['length']:assert bytes(u.mem_read(SP-64,24))==header and int.from_bytes(u.mem_read(SP-40,4),'little')==marker
    outputs.append([[u.reg_read(x) for x in REGS],s['trace'],s['writes'],s['logs'],bytes(u.mem_read(CTX,12)).hex(),bytes(u.mem_read(SP-128,256)).hex()])
   assert outputs[0]==outputs[1];counts[case['entry']]+=1;digest.update(json.dumps([case,outputs[0]],sort_keys=True).encode())
 v=dict(comparisons=counts['direct']+counts['wrapper'],counts=counts,trace_sha256=digest.hexdigest(),exact_spans=proof,exact_new_bytes=412,exact_joint_bytes=766,new_ram_state_bytes=12,object_sha256s={str(p.relative_to(ROOT)):sha(p) for p in [obj,wrapper]},application_sha256=sha(app),report_sha256=sha(OUT/'report.json'),driver_sha256=sha(Path(__file__)),independent_record_partial_read_and_write_marker_oracle=True,actual_wrapper_and_backend_execute=True,io_memclear_and_log_providers_are_fixtures=True,full_context_extent_owned=False,full_raw_abi_or_private_histories_verified=False,whole_image_complete=False,hardware_write_executed=False);(OUT/'verification.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v))
if __name__=='__main__':main()
