#!/usr/bin/env python3
"""Daily test fixture exact frames, signed PRNG remainder and cache-write oracle."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-health-daily-fixture';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();SP=0x2003d000;PAY=0x20011000;CACHE=0x20012000;REGS=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3];SAVED=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11];states={};RANDOM=[0,1,0x7fffffff,0xffffffff,0x80000000,40,0xffffffd7,0x12345678];U32=0xffffffff
PROVIDERS={0x914ec:'r1_structured_log_mode_get',0x91638:'r1_structured_log_format',0x799c0:'nrf_log_frontend_std_0',0x799c8:'nrf_log_frontend_std_1',0x799f8:'nrf_log_frontend_std_4',0x8ada4:'r1_time_backend_timestamp',0x8ad64:'r1_time_local_day_start',0x276a4:'r1_native_rand',0x5ace0:'r1_hr_daily_cache_accessor',0x5baec:'r1_spo2_daily_cache_accessor',0x8d40c:'r1_health_fixture_notify_hr',0x8e3f8:'r1_health_fixture_notify_spo2',0x8e560:'r1_health_fixture_notify_temperature'}
def srem(v,d):
 v=v-0x100000000 if v&0x80000000 else v;return v-(-((-v)//d) if v<0 else v//d)*d

def main():
 c=json.loads((OUT/'contracts.json').read_text());obj=OUT/'native_health_daily_fixture.o';app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();proof=[];digest=hashlib.sha256();counts=dict(cases=0,getter=0,random_calls=0,notifications=0,cache_gets=0);logs={}
 with tempfile.TemporaryDirectory() as temp:
  td=Path(temp);ld=td/'proof.ld';ld.write_text('SECTIONS {'+''.join(' .b%d %s : { *(.text.%s) }'%(i,x['address'],x['symbol']) for i,x in enumerate(c['bodies']))+' /DISCARD/ : { *(.ARM.exidx*) } }\n'+''.join('%s = 0x%x;\n'%(n,a+1) for a,n in PROVIDERS.items())+'__start_log_const_data = 0xc441c;\nr1_health_storage_temperature_prefix = 0x200165f4;\n');elf=td/'proof.elf';subprocess.run(['arm-none-eabi-ld','-T',str(ld),str(obj),'-o',str(elf)],check=True,stderr=subprocess.PIPE);replacements=[]
  for i,x in enumerate(c['bodies']):
   a=int(x['address'],16);f=td/(str(i)+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j','.b'+str(i),'-O','binary',str(elf),str(f)],check=True);d=f.read_bytes();assert len(d)==x['source_span_bytes'] and d==raw[a-0x27000:a-0x27000+len(d)];replacements.append((a,d));proof.append(dict(address=hex(a),size=len(d),sha256=hashlib.sha256(d).hexdigest()))
  def hook(u,a,size,_):
   if a not in [*PROVIDERS,0x5be5c]:return
   s=states[id(u)];case=s['case']
   if case.get('getter'):return
   r=[u.reg_read(x) for x in REGS];s['trace'].append([a,r,bytes(u.mem_read(u.reg_read(UC_ARM_REG_SP),16)).hex()]);ret=0x98765432
   if a==0x914ec:ret=case['mode']
   elif a==0x8ada4:ret=case['now']
   elif a==0x8ad64:ret=case['day']
   elif a in [0x5ace0,0x5baec,0x5be5c]:
    assert a==[0x5ace0,0x5baec,0x5be5c][case['kind']];s['gets']+=1;counts['cache_gets']+=1;ret=0 if case['fail'] and s['gets']==case['fail'] else CACHE
   elif a==0x276a4:ret=RANDOM[(s['random']+case['seed'])%len(RANDOM)];s['random']+=1;counts['random_calls']+=1
   elif a in [0x8d40c,0x8e3f8,0x8e560]:assert r==s['expected_args'],(case,r,s['expected_args']);s['notify'].append(a);counts['notifications']+=1;ret=0x12345678
   else:
    assert 0x8b690<=r[1]<0x8b818;logs[a]=logs.get(a,0)+1
    if a in [0x799c0,0x799c8,0x799f8]:assert r[0]==0x1c0003
   for reg,val in zip(REGS,[ret,0xa1a1a1a1,0xb2b2b2b2,0xc3c3c3c3]):u.reg_write(reg,val)
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  machines=[]
  for side in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x100000);u.mem_write(0x27000,raw);u.mem_map(0x20000000,0x40000)
   if side:
    for a,d in replacements:u.mem_write(a,d)
   u.hook_add(UC_HOOK_CODE,hook);machines.append(u)
  default=dict(kind=0,start=0,end=86400,day=0,now=86400,present=1,mode=0,fail=0,seed=0)
  cases=[dict(default,kind=k,start=st,end=en,day=day,now=now,mode=mode,fail=fail,seed=seed) for k,(st,en,day,now),mode,fail,seed in itertools.product(range(3),[(0,86400,0,86400),(3599,3600,0,3630),(7200,10800,0,10830),(0,0,0,0),(0,0,0,30),(0,0,0,31),(0,86400,1,86400),(0,86400,0,100000),(86400,0xffffffff,86400,0xffffffff),(0xfffffff0,1,0xffff0000,30),(23*3600,24*3600,0,86400),(46*3600,47*3600,0,47*3600)],range(8),[0,1,2,24],range(8))]
  cases += [dict(default,kind=kind,mode=mode,present=present) for kind,mode,present in itertools.product(range(256),range(8),range(2))]
  cases += [dict(default,getter=True,seed=seed) for seed in range(256)]
  for case in cases:
   expected=bytearray(b'\x96'*256);want_gets=want_random=0;notify=False;tail_log=False;getter=case.get('getter',False);frame=[PAY if case['present'] else 0,0x11223344,0x55667788,0x99aabbcc];result=frame[0]
   if getter:result=0x200165f4
   elif not case['present'] or case['kind']>2:tail_log=bool(case['mode']&2)
   else:
    frame[3]=case['now']
    if case['mode']&5:frame[:3]=[case['day'],case['start'],case['end']]
    if case['mode']&2:frame[:2]=[case['start'],case['end']]
   if not getter and case['present'] and case['kind']<=2 and case['end']>=((case['now']-30)&U32) and case['start']>=case['day']:
    floor=case['start']//3600*3600;start=min((((floor-case['day'])&U32)//3600)&255,23);length=min(((((case['end']//3600*3600-floor)&U32)//3600)&255),23)
    for hour in range(start,start+length+1):
     want_gets+=1
     if case['fail']==want_gets:tail_log=bool(case['mode']&2);break
     divs,adds,latest=[([40,40,15],[60,100,45],85),([3,7,5],[97,90,85],98),([30,40,50],[100,130,50],110)][case['kind']]
     frame[0]=CACHE+hour*3
     for j,(div,add) in enumerate(zip(divs,adds)):expected[hour*3+j]=(srem(RANDOM[(want_random+case['seed'])%8],div)+add)&255;want_random+=1
     if hour==start:expected[75]=latest;struct.pack_into('<2I',expected,76,case['now'],case['day'])
    else:notify=True;result=0x12345678
   if not getter and not notify:result=frame[0]
   if tail_log:result=0x98765432
   outputs=[]
   for u in machines:
    payload=bytes([case['kind']])+struct.pack('<2I',case['start'],case['end']);u.mem_write(PAY,payload);u.mem_write(CACHE,b'\x96'*256);u.mem_write(SP-128,b'\x96'*256)
    for reg,val in zip(REGS,[PAY if case['present'] else 0,0x11223344,0x55667788,0x99aabbcc]):u.reg_write(reg,val)
    for i,reg in enumerate(SAVED):u.reg_write(reg,0x12340000+i)
    u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,0x20000101);s=dict(case=case,expected_args=frame,trace=[],gets=0,random=0,notify=[]);states[id(u)]=s;u.emu_start(0x5be5d if getter else 0x8b379,0x20000100,count=20000)
    assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==SP and u.reg_read(UC_ARM_REG_R0)==result and [u.reg_read(x) for x in SAVED]==[0x12340000+i for i in range(8)],(case,u.reg_read(UC_ARM_REG_R0),result)
    assert bytes(u.mem_read(CACHE,256))==expected and s['gets']==want_gets and s['random']==want_random and bool(s['notify'])==notify,case
    outputs.append([[u.reg_read(x) for x in REGS],s['trace'],bytes(u.mem_read(SP-128,256)).hex()])
   assert outputs[0]==outputs[1];counts['getter' if getter else 'cases']+=1;digest.update(json.dumps([case,outputs[0]],sort_keys=True).encode())
 v=dict(comparisons=counts['cases']+counts['getter'],counts=counts,logs={hex(k):v for k,v in logs.items()},trace_sha256=digest.hexdigest(),exact_spans=proof,exact_bytes=1192,object_sha256=sha(obj),application_sha256=sha(app),report_sha256=sha(OUT/'report.json'),driver_sha256=sha(Path(__file__)),independent_hour_range_signed_random_and_cache_oracle=True,logging_time_cache_random_and_notification_providers_are_fixtures=True,temperature_accessor_executes_in_direct_getter_cases=True,full_daily_cache_extent_owned=False,full_raw_abi_or_private_histories_verified=False,whole_image_complete=False,hardware_write_executed=False);(OUT/'verification.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v))
if __name__=='__main__':main()
