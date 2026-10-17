#!/usr/bin/env python3
"""Independent bounded retry/sector truncation oracle; actual event/erase chain."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-sleep-record';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();SP=0x2003d000;PAY=0x20010000;CTX=0x200067b4;REGION=0x20013000;REGION2=REGION+64;OPS=0x20014000;OPS2=OPS+64;ERASE=0x20001000;ERASE2=ERASE+16;REGS=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3];SAVED=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11];states={}
PROVIDERS={0x914ec:'r1_structured_log_mode_get',0x91638:'r1_structured_log_format',0x799c0:'nrf_log_frontend_std_0',0x799c8:'nrf_log_frontend_std_1',0x8fe28:'r1_sleep_sector_select',0x8fc6c:'r1_sleep_sector_fallback',0x8fe98:'r1_sleep_sector_write',0x8b138:'r1_health_event_notification_throttle'}
def main():
 c=json.loads((OUT/'contracts.json').read_text());obj=OUT/'native_sleep_record.o';app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();proof=[];digest=hashlib.sha256();counts=dict(store=0,event=0,erase=0,erase_event=0,sector_count=0,selects=0,fallbacks=0,writes=0,erases=0,throttles=0)
 with tempfile.TemporaryDirectory() as temp:
  td=Path(temp);ld=td/'proof.ld';ld.write_text('SECTIONS {'+''.join(' .b%d %s : { *(.text.%s) }'%(i,x['address'],x['symbol']) for i,x in enumerate(c['bodies']))+' /DISCARD/ : { *(.ARM.exidx*) } }\n'+''.join('%s = 0x%x;\n'%(n,a+1) for a,n in PROVIDERS.items())+'__start_log_const_data = 0xc441c;\nr1_sleep_sync_context_prefix = 0x200067b4;\n');elf=td/'proof.elf';subprocess.run(['arm-none-eabi-ld','-T',str(ld),str(obj),'-o',str(elf)],check=True,stderr=subprocess.PIPE);replacements=[]
  for i,x in enumerate(c['bodies']):
   a=int(x['address'],16);f=td/(str(i)+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j','.b'+str(i),'-O','binary',str(elf),str(f)],check=True);d=f.read_bytes();assert len(d)==x['source_span_bytes'] and d==raw[a-0x27000:a-0x27000+len(d)];replacements.append((a,d));proof.append(dict(address=hex(a),size=len(d),sha256=hashlib.sha256(d).hexdigest()))
  def hook(u,a,size,_):
   if a not in [*PROVIDERS,ERASE,ERASE2]:return
   s=states[id(u)];case=s['case'];r=[u.reg_read(x) for x in REGS];sp=u.reg_read(UC_ARM_REG_SP);s['trace'].append([a,r,sp]);ret=0x98765432
   if a==0x914ec:ret=case['mode']
   elif a==0x8fe28:ret=case['select'][s['selects']];s['selects']+=1;counts['selects']+=1
   elif a==0x8fc6c:ret=0x99887766;counts['fallbacks']+=1
   elif a==0x8fe98:
    ret=case['write'][s['writes']];s['writes']+=1;counts['writes']+=1;s['write_calls'].append(r[:3])
    if case['mutate']:u.mem_write(CTX,b'\0');u.mem_write(PAY+30,b'\xff\xff')
   elif a in [ERASE,ERASE2]:
    counts['erases']+=1;s['erases'].append([a,r[:2]]);ret=case['erase_result']
    if case['mutate']:u.mem_write(CTX+4,struct.pack('<2I',REGION2,OPS2))
   elif a==0x8b138:assert sp==SP and r[0]==6;s['throttle']+=1;counts['throttles']+=1;ret=case['throttle_result']
   elif a==0x91638:
    assert r[1]==r[2];s['logs'].append([a,r[0],r[1],r[3] if r[0]==0xc400000 else None])
   else:
    s['logs'].append([a,r[0],r[1],r[2] if a==0x799c8 else None]);assert sp in [SP-48,SP-32,SP]
   for reg,val in zip(REGS,[ret,0xa1a1a1a1,0xb2b2b2b2,0xc3c3c3c3]):u.reg_write(reg,val)
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  machines=[]
  for side in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x100000);u.mem_write(0x27000,raw);u.mem_map(0x20000000,0x40000)
   if side:
    for a,d in replacements:u.mem_write(a,d)
   u.hook_add(UC_HOOK_CODE,hook);machines.append(u)
  default=dict(entry='store',init=1,length=32,present=1,select=[0x12345678,0xffffffff],write=[0,1],mode=0,mutate=0,region_present=1,size=8192,erase_result=0xffffffff,throttle_result=0xffffffff)
  cases=[dict(default,entry=entry,init=init,length=length,present=present,select=sel,write=wr,mode=mode,mutate=mut) for entry,init,length,present,sel,wr,mode,mut in itertools.product(['store','event'],[0,1,2,255],[0,1,3888,3889,0xffffffff],range(2),[[0xffffffff,0],[0x12345678,0xabcdef01],[0,0xffffffff]],[[1,1],[0,1],[0,0],[0xffffffff,0]],range(8),range(2))]
  cases += [dict(default,entry=entry,length=size,mode=7) for entry,size in itertools.product(['event'],[3856,3857,65503,65504,65535])]
  cases += [dict(default,entry=entry,init=value,mode=7,write=[1,0]) for entry,value in itertools.product(['store','event'],range(256))]
  cases += [dict(default,entry=entry,size=(value<<12)|0xfff,mutate=mut) for entry,value,mut in itertools.product(['erase','erase_event','sector_count'],range(256),range(2))]
  cases += [dict(default,entry=entry,size=size,region_present=present,mutate=mut) for entry,size,present,mut in itertools.product(['erase','erase_event','sector_count'],[0x100000,0xffffffff],range(2),range(2)) if present or entry=='sector_count']
  addresses=dict(store=0x5b890,event=0x8dc94,erase=0x5b2f8,erase_event=0x8dd88,sector_count=0x8fe14)
  for case in cases:
   entry=case['entry'];seq=[];logs=[];write_calls=[];erases=[];selected=0;throttle=0;result=0;n=((case['size']>>12)&255) if case['region_present'] else 0;length=((case['length']&65535)+32)&65535 if entry=='event' else case['length'];packet=bytearray(b'\x96'*64);struct.pack_into('<H',packet,30,case['length']&65535);expected=bytearray(packet)
   def logging(fmt_addr,std_addr,level=1,arg=None):
    seq.append(0x914ec)
    if not case['mode']&1:seq.append(0x914ec)
    if case['mode']&5:seq.append(0x91638);logs.append([0x91638,0xc400000 if arg is not None else 0x4000000,fmt_addr,arg])
    seq.append(0x914ec)
    if case['mode']&2:seq.append(0x799c8 if arg is not None else 0x799c0);logs.append([0x799c8 if arg is not None else 0x799c0,0x1c0000+level,std_addr,arg])
   def erase():
    for i in range(n):seq.append(ERASE2 if case['mutate'] and i else ERASE);erases.append([seq[-1],[((0x200000 if case['mutate'] and i else 0x100000)+i*4096)&0xffffffff,4096]])
   if entry in ['erase','erase_event']:erase();result=case['erase_result'] if n else 0
   elif entry=='sector_count':result=n
   elif entry=='event' and not case['present']:
    logging(0x8dd20,0x8dd3c);result=0x98765432 if case['mode']&2 else (case['mode']<<30)&0xffffffff
   else:
    if not case['init']:logging(0x5b9b8,0x5b9d8)
    elif length>3888 or not case['present']:logging(0x5b9f0,0x5ba1c)
    else:
     for attempt in range(2):
      seq.append(0x8fe28);selected=case['select'][attempt]
      if selected==0xffffffff:seq.append(0x8fc6c);selected=0x99887766
      seq.append(0x8fe98);write_calls.append([selected&255,PAY,length])
      if case['mutate']:expected[30:32]=b'\xff\xff'
      if case['write'][attempt]:result=1;logging(0x5baa0,0x5bac8,3,selected);break
     else:erase();logging(0x5ba40,0x5ba74)
    if entry=='event':
     if result:seq.append(0x8b138);throttle=1;result=case['throttle_result']
     else:logging(0x8dd50,0x8dd70);result=0x98765432 if case['mode']&2 else (case['mode']<<30)&0xffffffff
   outputs=[]
   for u in machines:
    u.mem_write(PAY,bytes(packet));u.mem_write(CTX,struct.pack('<3I',case['init'],REGION if case['region_present'] else 0,OPS));u.mem_write(REGION,bytes(128));u.mem_write(REGION+52,struct.pack('<2I',0x100000,case['size']));u.mem_write(REGION2+52,struct.pack('<2I',0x200000,case['size']));u.mem_write(OPS,bytes(128));u.mem_write(OPS+48,struct.pack('<I',ERASE+1));u.mem_write(OPS2+48,struct.pack('<I',ERASE2+1));u.mem_write(SP-128,b'\x96'*256)
    for reg,val in zip(REGS,[PAY if case['present'] else 0,case['length'],0x55667788,0x99aabbcc]):u.reg_write(reg,val)
    for i,reg in enumerate(SAVED):u.reg_write(reg,0x12340000+i)
    u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,0x20000101);s=dict(case=case,trace=[],logs=[],write_calls=[],selects=0,writes=0,erases=[],throttle=0);states[id(u)]=s;u.emu_start(addresses[entry]|1,0x20000100,count=20000)
    assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==SP and u.reg_read(UC_ARM_REG_R0)==result and [u.reg_read(x) for x in SAVED]==[0x12340000+i for i in range(8)],(case,u.reg_read(UC_ARM_REG_R0),result)
    assert [x[0] for x in s['trace']]==seq and s['logs']==logs and s['write_calls']==write_calls and s['erases']==erases and s['throttle']==throttle and bytes(u.mem_read(PAY,64))==expected,case
    outputs.append([[u.reg_read(x) for x in REGS],s['trace'],s['logs'],bytes(u.mem_read(CTX,12)).hex(),bytes(u.mem_read(SP-128,256)).hex()])
   assert outputs[0]==outputs[1];counts[entry]+=1;digest.update(json.dumps([case,outputs[0]],sort_keys=True).encode())
 v=dict(comparisons=sum(counts[k] for k in addresses),counts=counts,trace_sha256=digest.hexdigest(),exact_spans=proof,exact_bytes=924,object_sha256=sha(obj),application_sha256=sha(app),report_sha256=sha(OUT/'report.json'),driver_sha256=sha(Path(__file__)),independent_retry_size_sector_and_log_oracle=True,actual_event_store_erase_and_count_execute=True,sector_alloc_write_log_erase_and_throttle_providers_are_fixtures=True,new_ram_state_bytes=0,full_raw_abi_or_private_histories_verified=False,whole_image_complete=False,hardware_write_executed=False);(OUT/'verification.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v))
if __name__=='__main__':main()
