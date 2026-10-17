#!/usr/bin/env python3
"""Independent sleep-report log fields, fresh reads, duration and fallback oracle."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_INVALID
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-sleep-report';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();SP=0x2003d000;PAY=0x20010000;REGS=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3];SAVED=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11];states={};PROVIDERS={0x914ec:'r1_structured_log_mode_get',0x91638:'r1_structured_log_format',0x799c0:'nrf_log_frontend_std_0',0x799f8:'nrf_log_frontend_std_4',0x8d8fc:'r1_event_publish',0x8dc94:'r1_event_service_0008dc94'}
def packet(case,step=0):
 p=bytearray((case['seed']+i*17+step*13)&255 for i in range(32));struct.pack_into('<2I',p,12,case['start'],case['end']);struct.pack_into('<H',p,30,(case['stages']+step)&65535);return p
def fields(p,g):
 u16=lambda a:struct.unpack_from('<H',p,a)[0];u32=lambda a:struct.unpack_from('<I',p,a)[0]
 return [[u32(12),u32(16),p[0],u16(30)],[p[1],p[2],u16(20),u16(8)],list(p[4:8]),[u16(22),u16(24),u16(26),u16(28)]][g]
def main():
 c=json.loads((OUT/'contracts.json').read_text());obj=OUT/'native_sleep_report.o';app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();digest=hashlib.sha256();proof=[];counts=dict(cases=0,faults=0,printf=0,std=0,publishes=0,fallbacks=0)
 with tempfile.TemporaryDirectory() as temp:
  td=Path(temp);ld=td/'proof.ld';ld.write_text('SECTIONS { .body 0x8dd90 : { *(.text.r1_event_service_0008dd90) } .components 0xbf8a4 : { *(.r1.sleep.report.components) } /DISCARD/ : { *(.ARM.exidx*) } }\n'+''.join('%s = 0x%x;\n'%(n,a+1) for a,n in PROVIDERS.items())+'__start_log_const_data = 0xc441c;\n');elf=td/'proof.elf';subprocess.run(['arm-none-eabi-ld','-T',str(ld),str(obj),'-o',str(elf)],check=True,stderr=subprocess.PIPE);replacements=[]
  for sec,a,n in [('.body',0x8dd90,964),('.components',0xbf8a4,65)]:
   f=td/(sec[1:]+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j',sec,'-O','binary',str(elf),str(f)],check=True);d=f.read_bytes();assert len(d)==n and d==raw[a-0x27000:a-0x27000+n],(sec,len(d),[(hex(a+i),hex(x),hex(y)) for i,(x,y) in enumerate(zip(d,raw[a-0x27000:a-0x27000+n])) if x!=y][:12]);replacements.append((a,d));proof.append(dict(address=hex(a),size=n,sha256=hashlib.sha256(d).hexdigest()))
  def invalid(u,access,a,size,value,_):states[id(u)]['fault']=[access,a,size,value];return False
  def hook(u,a,size,_):
   s=states[id(u)];case=s['case'];r=[u.reg_read(x) for x in REGS];sp=u.reg_read(UC_ARM_REG_SP);s['raw'].append([a,r,sp]);ret=0x98765432
   if a==0x914ec:
    s['trace'].append(['mode']);ret=case['modes'][s['step']%len(case['modes'])];s['step']+=1
    if case['mutate']:u.mem_write(PAY,bytes(packet(case,s['step'])))
   elif a==0x91638:
    counts['printf']+=1;n=(r[0]>>22)&15;args=([r[3]]+list(struct.unpack('<3I',u.mem_read(sp,12))))[:n];assert r[1]==r[2];s['trace'].append(['printf',r[0],r[1],args])
   elif a in [0x799c0,0x799f8]:
    counts['std']+=1;n=4 if a==0x799f8 else 0;args=([r[2],r[3]]+list(struct.unpack('<2I',u.mem_read(sp,8))))[:n];s['trace'].append(['std',r[0],r[1],args])
   elif a==0x8d8fc:
    counts['publishes']+=1;assert r[:3]==[0x2000,PAY,(struct.unpack('<H',u.mem_read(PAY+30,2))[0]+32)&65535];s['trace'].append(['publish',r[:3],bytes(u.mem_read(PAY,32)).hex()]);ret=case['publish']
    if case['mutate']:u.mem_write(PAY+20,b'\xa5'*12)
   else:
    counts['fallbacks']+=1;assert sp==SP and r==[PAY,*s['expected_frame']];s['trace'].append(['fallback',r,bytes(u.mem_read(PAY,32)).hex()]);ret=case['store']
   for reg,val in zip(REGS,[ret,0xa1a1a1a1,0xb2b2b2b2,0xc3c3c3c3]):u.reg_write(reg,val)
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  machines=[]
  for side in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x100000);u.mem_write(0x27000,raw);u.mem_map(0x20000000,0x40000)
   if side:
    for a,d in replacements:u.mem_write(a,d)
   for a in PROVIDERS:u.hook_add(UC_HOOK_CODE,hook,begin=a,end=a)
   u.hook_add(UC_HOOK_MEM_INVALID,invalid);machines.append(u)
  modes=[[i] for i in range(8)]+[[0,4,2],[1,2,0],[4,1,7,0]];default=dict(seed=0,start=0,end=3600,stages=0,modes=[0],publish=0,store=1,mutate=0,fault=False)
  ranges=[(0,0),(0,3599),(0,3600),(0,3601),(0xffffffff,3598),(0xffffffff,3599),(3600,0),(0xfffffff0,0xfffffff1)]
  cases=[dict(default,seed=seed,start=st,end=en,stages=65535,modes=mo,publish=pub,store=store,mutate=mut) for seed,(st,en),mo,pub,store,mut in itertools.product([0,1,127,128,255],ranges,modes,[0,1,0xffffffff],[0,1,0xffffffff],range(2))]
  cases += [dict(default,seed=seed,stages=stages,modes=[7],publish=pub) for seed,stages,pub in itertools.product(range(256),[0,1,65535],[0,1])]
  cases += [dict(default,modes=[mo],fault=True) for mo in [0,7]]
  for case in cases:
   p=packet(case);expected=bytearray(p);trace=[];frame=[0x11223344,0x55667788,0x99aabbcc];step=0;tail=False;result=0
   def mode():
    nonlocal step,expected
    trace.append(['mode']);value=case['modes'][step%len(case['modes'])];step+=1
    if case['mutate']:expected=packet(case,step)
    return value
   if not case['fault']:
    for g,(fmt,std) in enumerate([(0x8df44,0x8df78),(0x8df9c,0x8dfd8),(0xbf8a4,0x8e014),(0x8e050,0x8e090)]):
     if mode()&1 or mode()&4:args=fields(expected,g);frame[:]=args[1:];trace.append(['printf',0xd000000,fmt,args])
     if mode()&2:args=fields(expected,g);frame[:2]=args[2:];trace.append(['std',0x1c0003,std,args])
    if ((struct.unpack_from('<I',expected,16)[0]-struct.unpack_from('<I',expected,12)[0])&0xffffffff)<3600:
     if mode()&1 or mode()&4:trace.append(['printf',0xc000000,0x8e0c8,[]])
     value=mode();result=(value<<30)&0xffffffff
     if value&2:trace.append(['std',0x1c0003,0x8e0f0,[]]);result=0x98765432;tail=True
    else:
     length=(struct.unpack_from('<H',expected,30)[0]+32)&65535;trace.append(['publish',[0x2000,PAY,length],bytes(expected).hex()]);result=case['publish']
     if case['mutate']:expected[20:32]=b'\xa5'*12
     if not result:
      if mode()&1 or mode()&4:trace.append(['printf',0x4000000,0x8e114,[]])
      if mode()&2:trace.append(['std',0x1c0001,0x8e138,[]])
      trace.append(['fallback',[PAY,*frame],bytes(expected).hex()]);result=case['store']
   outputs=[]
   for u in machines:
    u.mem_write(PAY,bytes(p));u.mem_write(SP-128,b'\x96'*256)
    for reg,val in zip(REGS,[0x30000000 if case['fault'] else PAY,0x11223344,0x55667788,0x99aabbcc]):u.reg_write(reg,val)
    for i,reg in enumerate(SAVED):u.reg_write(reg,0x12340000+i)
    u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,0x20000101);s=dict(case=case,trace=[],raw=[],fault=None,step=0,expected_frame=frame);states[id(u)]=s
    try:u.emu_start(0x8dd91,0x20000100,count=5000)
    except UcError:assert s['fault'],case
    assert bool(s['fault'])==case['fault'],case
    if not case['fault']:
     assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==SP and u.reg_read(UC_ARM_REG_R0)==result and [u.reg_read(x) for x in SAVED]==[0x12340000+i for i in range(8)],case
     assert s['trace']==trace and s['step']==step and bytes(u.mem_read(PAY,32))==expected,case
     if not tail:assert [u.reg_read(x) for x in REGS[1:]]==frame or (trace[-1][0]=='fallback'),case
    outputs.append([[u.reg_read(x) for x in REGS],s['trace'],s['raw'],s['fault'],bytes(u.mem_read(SP-128,256)).hex()])
   assert outputs[0]==outputs[1];counts['faults' if case['fault'] else 'cases']+=1;digest.update(json.dumps([case,outputs[0]],sort_keys=True).encode())
 v=dict(comparisons=counts['cases']+counts['faults'],counts=counts,trace_sha256=digest.hexdigest(),exact_spans=proof,exact_bytes=1029,object_sha256=sha(obj),application_sha256=sha(app),report_sha256=sha(OUT/'report.json'),driver_sha256=sha(Path(__file__)),independent_fields_fresh_reads_duration_and_fallback_oracle=True,mode_log_publish_and_storage_are_fixtures=True,new_ram_state_bytes=0,full_raw_abi_or_private_histories_verified=False,whole_image_complete=False,hardware_write_executed=False);(OUT/'verification.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v))
if __name__=='__main__':main()
