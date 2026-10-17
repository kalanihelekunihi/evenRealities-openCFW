#!/usr/bin/env python3
"""Native health service wrapper guards, logs, raw tails and stack payloads."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-health-service-wrappers';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();SP=0x2003d000;REGS=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3];SAVED=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11];states={};PROVIDERS={0x914ec:'r1_structured_log_mode_get',0x91638:'r1_structured_log_format',0x799c0:'nrf_log_frontend_std_0',0x799c8:'nrf_log_frontend_std_1',0x8d8fc:'r1_event_publish',0x5b6f4:'r1_sleep_sync_status_backend'}
def main():
 c=json.loads((OUT/'contracts.json').read_text());obj=OUT/'native_health_service_wrappers.o';app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();proof=[];digest=hashlib.sha256();counts=dict(status=0,sync=0,spo2=0,temperature=0,bridge_spo2=0,bridge_temperature=0,noop=0,mode_calls=0,printf=0,std=0,publish=0,backend=0)
 with tempfile.TemporaryDirectory() as temp:
  td=Path(temp);ld=td/'proof.ld';ld.write_text('SECTIONS {'+''.join(' .b%d %s : { *(.text.%s) }'%(i,x['address'],x['symbol']) for i,x in enumerate(c['bodies']))+' /DISCARD/ : { *(.ARM.exidx*) } }\n'+''.join('%s = 0x%x;\n'%(n,a+1) for a,n in PROVIDERS.items())+'__start_log_const_data = 0xc441c;\n');elf=td/'proof.elf';subprocess.run(['arm-none-eabi-ld','-T',str(ld),str(obj),'-o',str(elf)],check=True,stderr=subprocess.PIPE);replacements=[]
  for i,x in enumerate(c['bodies']):
   a=int(x['address'],16);f=td/(str(i)+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j','.b'+str(i),'-O','binary',str(elf),str(f)],check=True);data=f.read_bytes();assert len(data)==x['source_span_bytes'] and data==raw[a-0x27000:a-0x27000+len(data)];replacements.append((a,data));proof.append(dict(address=hex(a),size=len(data),sha256=hashlib.sha256(data).hexdigest()))
  def hook(u,a,size,_):
   if a not in PROVIDERS:return
   s=states[id(u)];case=s['case'];r=[u.reg_read(x) for x in REGS];sp=u.reg_read(UC_ARM_REG_SP);s['trace'].append([a,r,sp,bytes(u.mem_read(sp-8,24)).hex()]);ret=case['result']
   if a==0x914ec:ret=case['modes'][s['mode']%len(case['modes'])];s['mode']+=1;counts['mode_calls']+=1
   elif a==0x91638:
    counts['printf']+=1;assert r[:3]==[0xc400000 if case['kind']=='status' else 0x4000000,0x8e19c if case['kind']=='status' else 0x8e22c,0x8e19c if case['kind']=='status' else 0x8e22c]
    if case['kind']=='status':assert r[3]==case['args'][0]
   elif a in [0x799c0,0x799c8]:
    counts['std']+=1;assert sp==SP and r[:2]==[0x1c0003 if case['kind']=='status' else 0x1c0001,0x8e1c4 if case['kind']=='status' else 0x8e258]
    if case['kind']=='status':assert a==0x799c8 and r[2]==case['args'][0]
    else:assert a==0x799c0
   elif a==0x5b6f4:counts['backend']+=1;assert sp==SP and r==case['args']
   else:
    counts['publish']+=1;assert sp==SP-8 and r[:3]==[0x1003 if case['kind'] in ['spo2','bridge_spo2'] else 0x1007,SP-8,1] and bytes(u.mem_read(r[1],4))==struct.pack('<I',s['payload'])
    if case['mutate']:u.mem_write(r[1],b'\xcd')
   for reg,val in zip(REGS,[ret,0xa1a1a1a1,0xb2b2b2b2,0xc3c3c3c3]):u.reg_write(reg,val)
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  machines=[]
  for side in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x100000);u.mem_write(0x27000,raw);u.mem_map(0x20000000,0x40000)
   if side:
    for a,d in replacements:u.mem_write(a,d)
   u.hook_add(UC_HOOK_CODE,hook);machines.append(u)
  modes=[[x] for x in range(8)]+[[0,4,2],[1,2,0],[4,1,2]];default=dict(kind='status',args=[0,0x11223344,0x55667788,0x99aabbcc],modes=[0],result=0,mutate=0)
  values=list(range(256))+[0x80000000,0xffffffff,0x12345678,0xaabbcc00];cases=[dict(default,args=[v,*default['args'][1:]],modes=mo,result=res) for v,mo,res in itertools.product(values,modes,[0,1,0xffffffff])]
  cases += [dict(default,kind='sync',args=[p,n,0x55667788,0x99aabbcc],modes=mo,result=res) for p,n,mo,res in itertools.product([0,1,0x20010000,0xffffffff],[0,1,12,0xffffffff],modes,[0,1,0xffffffff])]
  cases += [dict(default,kind=k,args=[high|lo,*default['args'][1:]],result=res,mutate=mut) for k,high,lo,res,mut in itertools.product(['spo2','temperature'],[0,0x80000000,0xaabbcc00],range(256),[0,1,0xffffffff],range(2))]
  cases += [dict(default,kind=k,args=[v,*default['args'][1:]],result=res,mutate=mut) for k,v,res,mut in itertools.product(['bridge_spo2','bridge_temperature'],[0,1,2,255,0x80000000,0xffffffff],[0,1,0xffffffff],range(2))]
  cases += [dict(default,kind='noop',args=[v,v^0xffffffff,(v*3)&0xffffffff,(v*7)&0xffffffff]) for v in values]
  addresses=dict(status=0x8e154,sync=0x8e1e0,spo2=0x8a87e,temperature=0x8a896,bridge_spo2=0x8e274,bridge_temperature=0x8e552,noop=0x8e55c)
  for case in cases:
   k=case['kind'];args=case['args'];seq=[];mode_index=0;result=args[0];payload=1 if k=='bridge_spo2' else 0 if k=='bridge_temperature' else args[0];expected_r3=None
   def mode():
    nonlocal mode_index
    seq.append(0x914ec);r=case['modes'][mode_index%len(case['modes'])];mode_index+=1;return r
   if k in ['status','sync']:
    if k=='sync' and args[0] and args[1]:seq.append(0x5b6f4);result=case['result']
    else:
     if mode()&1 or mode()&4:seq.append(0x91638)
     value=mode();result=(value<<30)&0xffffffff
     if value&2:seq.append(0x799c8 if k=='status' else 0x799c0);result=case['result']
   elif k!='noop':
    low=payload&255;expected_r3=payload;result=low
    if low<2:
     seq.append(0x8d8fc);result=case['result']
     if case['mutate']:expected_r3=(payload&0xffffff00)|0xcd
   outputs=[]
   for u in machines:
    u.mem_write(SP-128,b'\x96'*256)
    for reg,val in zip(REGS,args):u.reg_write(reg,val)
    for i,reg in enumerate(SAVED):u.reg_write(reg,0x12340000+i)
    u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,0x20000101);s=dict(case=case,trace=[],mode=0,payload=payload);states[id(u)]=s;u.emu_start(addresses[k]|1,0x20000100,count=1000)
    assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==SP and u.reg_read(UC_ARM_REG_R0)==result and [u.reg_read(x) for x in SAVED]==[0x12340000+i for i in range(8)],case
    assert [x[0] for x in s['trace']]==seq and s['mode']==mode_index,case
    if expected_r3 is not None:assert u.reg_read(UC_ARM_REG_R3)==expected_r3,case
    if k=='noop':assert [u.reg_read(x) for x in REGS]==args
    outputs.append([[u.reg_read(x) for x in REGS],s['trace'],bytes(u.mem_read(SP-128,256)).hex()])
   assert outputs[0]==outputs[1];counts[k]+=1;digest.update(json.dumps([case,outputs[0]],sort_keys=True).encode())
 v=dict(comparisons=sum(counts[k] for k in addresses),counts=counts,trace_sha256=digest.hexdigest(),exact_spans=proof,exact_bytes=354,object_sha256=sha(obj),application_sha256=sha(app),report_sha256=sha(OUT/'report.json'),driver_sha256=sha(Path(__file__)),independent_guard_log_return_and_stack_payload_oracle=True,bridges_execute_actual_publish_helpers=True,log_mode_publish_and_sleep_backend_are_fixtures=True,new_ram_state_bytes=0,full_raw_abi_or_private_histories_verified=False,whole_image_complete=False,hardware_write_executed=False);(OUT/'verification.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v))
if __name__=='__main__':main()
