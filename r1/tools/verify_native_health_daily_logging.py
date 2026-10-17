#!/usr/bin/env python3
"""Independent daily log argument/order oracle including provider cache mutation."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-health-daily-logging';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();SP=0x2003d000;CACHE=0x20012000;REGS=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3];SAVED=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11];states={};GETTERS=[0x5ace0,0x5baec,0x5be5c];PROVIDERS={0x914ec:'r1_structured_log_mode_get',0x91638:'r1_structured_log_format',0x799d6:'nrf_log_frontend_std_2',0x799f8:'nrf_log_frontend_std_4',**dict(zip(GETTERS,['r1_hr_daily_cache_accessor','r1_spo2_daily_cache_accessor','r1_temperature_daily_cache_accessor']))}
def pattern(seed,step=0):return bytes((seed+step*13+i*(29 if step else 17))&255 for i in range(84))
def main():
 c=json.loads((OUT/'contracts.json').read_text());obj=OUT/'native_health_daily_logging.o';app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();proof=[];digest=hashlib.sha256();counts=dict(cases=0,printf=0,std2=0,std4=0,mode_calls=0);texts={}
 for x in c['bodies']:
  for d in x['data']:
   if d['kind']=='text':texts[int(d['address'],16)]=d['value']
 with tempfile.TemporaryDirectory() as temp:
  td=Path(temp);ld=td/'proof.ld';ld.write_text('SECTIONS {'+''.join(' .b%d %s : { *(.text.%s) }'%(i,x['address'],x['symbol']) for i,x in enumerate(c['bodies']))+' /DISCARD/ : { *(.ARM.exidx*) } }\n'+''.join('%s = 0x%x;\n'%(n,a+1) for a,n in PROVIDERS.items())+'__start_log_const_data = 0xc441c;\n');elf=td/'proof.elf';subprocess.run(['arm-none-eabi-ld','-T',str(ld),str(obj),'-o',str(elf)],check=True,stderr=subprocess.PIPE);replacements=[]
  for i,x in enumerate(c['bodies']):
   a=int(x['address'],16);f=td/(str(i)+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j','.b'+str(i),'-O','binary',str(elf),str(f)],check=True);data=f.read_bytes();assert len(data)==x['source_span_bytes'] and data==raw[a-0x27000:a-0x27000+len(data)];replacements.append((a,data));proof.append(dict(address=hex(a),size=len(data),sha256=hashlib.sha256(data).hexdigest()))
  def hook(u,a,size,_):
   if a not in PROVIDERS:return
   s=states[id(u)];case=s['case'];r=[u.reg_read(x) for x in REGS];sp=u.reg_read(UC_ARM_REG_SP);s['trace'].append([a,r,bytes(u.mem_read(sp,12)).hex()]);ret=case['result']
   if a in GETTERS:assert a==GETTERS[case['kind']];ret=CACHE if case['present'] else 0
   elif a==0x914ec:
    ret=case['modes'][s['step']%len(case['modes'])];s['step']+=1;counts['mode_calls']+=1
    if case['mutate']:u.mem_write(CACHE,pattern(case['seed'],s['step']))
   else:
    assert r[1] in texts;stackwords=struct.unpack('<3I',u.mem_read(sp,12));s['logs'].append([a,[r[0],texts[r[1]],*r[2:]],list(stackwords[:3 if a==0x91638 and r[0]==0xd000000 else 1 if a==0x91638 else 2 if a==0x799f8 else 0])]);counts[{0x91638:'printf',0x799d6:'std2',0x799f8:'std4'}[a]]+=1
    if a==0x91638:assert r[2]==r[1];s['logs'][-1][1][2]=texts[r[2]]
   for reg,val in zip(REGS,[ret,0xa1a1a1a1,0xb2b2b2b2,0xc3c3c3c3]):u.reg_write(reg,val)
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  machines=[]
  for side in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x100000);u.mem_write(0x27000,raw);u.mem_map(0x20000000,0x40000)
   if side:
    for a,d in replacements:u.mem_write(a,d)
   u.hook_add(UC_HOOK_CODE,hook);machines.append(u)
  modes=[[i] for i in range(8)]+[[1,0,4,2,7,0],[0,4,1,2],[2,0,0,7,4]];seeds=[0,1,2,3,4,5,6,7,31,63,127,128,200,250,254,255]
  cases=[dict(kind=k,modes=mo,seed=seed,mutate=mut,present=present,result=result) for k,mo,seed,mut,present,result in itertools.product(range(3),modes,seeds,range(2),range(2),[0,1,0xffffffff])]
  cases += [dict(kind=k,modes=[7],seed=seed,mutate=0,present=1,result=0x98765432) for k,seed in itertools.product(range(3),range(256))]
  for case in cases:
   cache=pattern(case['seed']);expected=bytearray(cache);frame=[0x11223344,0x55667788,0x99aabbcc];step=0;expected_logs=[];result=0;strings=[d['value'] for d in c['bodies'][case['kind']]['data'] if d['kind']=='text'];offset=250 if case['kind']==2 else 0
   def mode():
    nonlocal step,expected
    value=case['modes'][step%len(case['modes'])];step+=1
    if case['mutate']:expected=bytearray(pattern(case['seed'],step))
    return value
   if case['present']:
    if mode()&1 or mode()&4:
     latest=expected[75]+offset;timestamp=int.from_bytes(expected[76:80],'little');frame[0]=timestamp;expected_logs.append([0x91638,[0xc800000,strings[0],strings[0],latest],[timestamp]])
    if mode()&2:expected_logs.append([0x799d6,[0x1c0003,strings[1],expected[75]+offset,int.from_bytes(expected[76:80],'little')],[]])
    for hour in range(24):
     if mode()&1 or mode()&4:
      low,high,avg=[x+offset for x in expected[hour*3:hour*3+3]];frame[:]=[low,avg,high];expected_logs.append([0x91638,[0xd000000,strings[2],strings[2],hour],[low,avg,high]])
     result=mode()
     enabled=result&2;result=(result<<30)&0xffffffff
     if enabled:
      low,high,avg=[x+offset for x in expected[hour*3:hour*3+3]];frame[:2]=[avg,high];expected_logs.append([0x799f8,[0x1c0003,strings[3],hour,low],[avg,high]]);result=case['result']
   outputs=[]
   for u in machines:
    u.mem_write(CACHE,cache);u.mem_write(SP-128,b'\x96'*256)
    for reg,val in zip(REGS,[0x87654321,0x11223344,0x55667788,0x99aabbcc]):u.reg_write(reg,val)
    for i,reg in enumerate(SAVED):u.reg_write(reg,0x12340000+i)
    u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,0x20000101);s=dict(case=case,trace=[],logs=[],step=0);states[id(u)]=s;u.emu_start(int(c['bodies'][case['kind']]['address'],16)|1,0x20000100,count=5000)
    assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==SP and [u.reg_read(x) for x in REGS]==[result,*frame] and [u.reg_read(x) for x in SAVED]==[0x12340000+i for i in range(8)],case
    assert s['logs']==expected_logs and s['step']==step and bytes(u.mem_read(CACHE,84))==expected,case
    outputs.append([s['trace'],s['logs'],bytes(u.mem_read(SP-128,256)).hex()])
   assert outputs[0]==outputs[1];counts['cases']+=1;digest.update(json.dumps([case,outputs[0]],sort_keys=True).encode())
 v=dict(comparisons=counts['cases'],counts=counts,trace_sha256=digest.hexdigest(),exact_spans=proof,exact_bytes=912,object_sha256=sha(obj),application_sha256=sha(app),report_sha256=sha(OUT/'report.json'),driver_sha256=sha(Path(__file__)),independent_log_order_arguments_and_stack_oracle=True,cache_mode_and_log_providers_are_fixtures=True,fresh_cache_after_mode_mutations_checked=True,full_cache_extent_owned=False,full_raw_abi_or_private_histories_verified=False,whole_image_complete=False,hardware_write_executed=False);(OUT/'verification.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v))
if __name__=='__main__':main()
