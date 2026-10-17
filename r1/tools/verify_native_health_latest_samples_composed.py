#!/usr/bin/env python3
"""Actual cache storage -> packed/public getters with one existing state owner."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
from build_native_dfu_backend_runtime import allocated_sections
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-health-latest-samples';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();SP=0x2003d000;DATA=0x20010000;DEST=DATA+64;REGS=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3];SAVED=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11];states={};INFO={'hr':(0x2001654c,84,1,75,0x5ad90,0x8d6ac,0x5ace8),'spo2':(0x200165a0,84,1,75,0x5bb2c,0x8e524,0x5baf4),'hrv':(0x200169c0,160,2,147,0x5af60,0x8d858,0x5af20)}
def main():
 c=json.loads((OUT/'contracts.json').read_text());sc=json.loads((BASE/'native-health-sample-storage/contracts.json').read_text());storage=BASE/'native-health-sample-storage/native_health_sample_storage.o';getter=OUT/'native_health_latest_samples.o';config=OUT/'shared-caches.o';bodies=c['bodies']+[x for x in sc['bodies'] if x['family'] in INFO];app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();proof=[];digest=hashlib.sha256();counts=dict(workflows=0,storage_calls=0,getter_calls=0,hour=0,average=0,logs=0)
 with tempfile.TemporaryDirectory() as temp:
  td=Path(temp);joint=td/'joint.o';roots=[x['symbol'] for x in bodies];aliases={f'r1_health_storage_{fam}_prefix':f'r1_cache_{fam}' for fam in INFO};cfg=td/'config-without-aliases.o';subprocess.run(['arm-none-eabi-objcopy',*[v for name in aliases for v in ['--strip-symbol',name]],str(config),str(cfg)],check=True);assert allocated_sections(cfg)==allocated_sections(config)
  subprocess.run(['arm-none-eabi-ld','-r','--gc-sections',*[v for n in roots for v in ['-u',n]],*[f'--defsym={a}={b}' for a,b in aliases.items()],str(cfg),str(storage),str(getter),'-o',str(joint)],check=True);assert not any(s in allocated_sections(joint) for s in ['.r1.health.storage.hr','.r1.health.storage.hrv','.r1.health.storage.spo2'])
  ld=td/'proof.ld';ld.write_text('SECTIONS {'+''.join(' .b%d %s : { *(.text.%s) }'%(i,x['address'],x['symbol']) for i,x in enumerate(bodies))+''.join(' .cache_%s 0x%x : { *(.r1.health.cache.%s) }'%(fam,i[0],fam) for fam,i in INFO.items())+' /DISCARD/ : { *(.ARM.exidx*) } }\n'+''.join('%s = 0x%x;\n'%(n,int(a,16)+1) for a,n in sc['providers'].items()));elf=td/'proof.elf';subprocess.run(['arm-none-eabi-ld','-T',str(ld),str(joint),'-o',str(elf)],check=True,stderr=subprocess.PIPE);replacements=[]
  for i,x in enumerate(bodies):
   a=int(x['address'],16);f=td/(str(i)+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j','.b'+str(i),'-O','binary',str(elf),str(f)],check=True);d=f.read_bytes();assert len(d)==x['source_span_bytes'] and d==raw[a-0x27000:a-0x27000+len(d)];replacements.append((a,d));proof.append(dict(address=hex(a),size=len(d),sha256=hashlib.sha256(d).hexdigest()))
  syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
  for fam in INFO:assert syms[f'r1_health_storage_{fam}_prefix']==syms[f'r1_cache_{fam}']==INFO[fam][0]
  def hook(u,a,size,_):
   s=states[id(u)];case=s['case'];r=[u.reg_read(x) for x in REGS];s['trace'].append([a,r]);ret=0x98765432
   if a==0x5aca6:counts['hour']+=1;assert r[0]==s['timestamp'];ret=case['hour']
   elif a==0x5aba0:counts['average']+=1;assert r[:3]==[{'hr':0,'spo2':1,'hrv':5}[case['family']],s['value'],s['timestamp']];ret=case['average']
   elif a==0x914ec:ret=case['mode']
   else:counts['logs']+=1
   for reg,val in zip(REGS,[ret,0xa1a1a1a1,0xb2b2b2b2,0xc3c3c3c3]):u.reg_write(reg,val)
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  machines=[]
  for side in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x100000);u.mem_write(0x27000,raw);u.mem_map(0x20000000,0x40000)
   if side:
    for a,d in replacements:u.mem_write(a,d)
   for a in sc['providers']:u.hook_add(UC_HOOK_CODE,hook,begin=int(a,16),end=int(a,16))
   machines.append(u)
  cases=[dict(family=fam,hour=hour,value=value,average=avg,time=ts,mode=mode) for fam,hour,value,avg,ts,mode in itertools.product(INFO,[0,23],[0,1,64,70,100,255,256,65535],[0,1,0xffffffff],[0,1,0xffffffff],[0,7])]
  for case in cases:
   fam=case['family'];base,size,width,last,store,wrap,packed=INFO[fam];mask=(1<<(width*8))-1;caches={f:bytearray(i[1]) for f,i in INFO.items()};outputs=[]
   for u in machines:
    for f,i in INFO.items():u.mem_write(i[0],bytes(i[1]))
   for tick,value in enumerate([case['value']&mask,(case['value']+1)&mask,0]):
    timestamp=(case['time']+tick*7)&0xffffffff;packet=value.to_bytes(width,'little')+struct.pack('<I',timestamp);cache=caches[fam];at=case['hour']*width*3;maximum=int.from_bytes(cache[at+width:at+width*2],'little');minimum=int.from_bytes(cache[at+width*2:at+width*3],'little')
    if value>maximum:cache[at+width:at+width*2]=value.to_bytes(width,'little')
    if value<minimum or minimum==0:cache[at+width*2:at+width*3]=value.to_bytes(width,'little')
    cache[at:at+width]=(case['average']&mask).to_bytes(width,'little');cache[last:last+width+4]=packet
    calloutputs=[]
    for u in machines:
     s=dict(case=case,value=value,timestamp=timestamp,trace=[]);states[id(u)]=s
     def call(a,arg):
      u.mem_write(SP-128,b'\x96'*256)
      for reg,val in zip(REGS,[arg,0x11223344,0x55667788,0x99aabbcc]):u.reg_write(reg,val)
      for j,reg in enumerate(SAVED):u.reg_write(reg,0x12340000+j)
      u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,0x20000101);u.emu_start(a|1,0x20000100,count=2000);assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==SP and [u.reg_read(r) for r in SAVED]==[0x12340000+j for j in range(8)]
     u.mem_write(DATA,packet);call(store,DATA)
     for f,i in INFO.items():assert bytes(u.mem_read(i[0],i[1]))==caches[f],(case,tick,f)
     getters=[]
     for a,iswrap in [(packed,False),(wrap,True)]:
      expected=bytearray(b'\xa5'*12)
      if iswrap:expected[:1 if fam=='spo2' else 4]=bytes(1 if fam=='spo2' else 4);expected[4:8]=bytes(4)
      if value:
       if iswrap:expected[:width]=value.to_bytes(width,'little');expected[4:8]=struct.pack('<I',timestamp)
       else:expected[:width+4]=packet
      u.mem_write(DEST,b'\xa5'*12);call(a,DEST);assert u.reg_read(UC_ARM_REG_R0)==int(value!=0) and bytes(u.mem_read(DEST,12))==expected,(case,tick,a);getters.append([[u.reg_read(r) for r in REGS],bytes(u.mem_read(DEST,12)).hex()])
     calloutputs.append([s['trace'],getters,[bytes(u.mem_read(i[0],i[1])).hex() for i in INFO.values()]])
    assert calloutputs[0]==calloutputs[1];counts['storage_calls']+=1;counts['getter_calls']+=2;digest.update(json.dumps([case,tick,calloutputs[0]],sort_keys=True).encode())
   counts['workflows']+=1
 v=dict(workflows=counts['workflows'],counts=counts,trace_sha256=digest.hexdigest(),exact_spans=proof,exact_bytes=1446,inputs={str(p.relative_to(ROOT)):sha(p) for p in [storage,getter,config]},report_sha256=sha(OUT/'report.json'),driver_sha256=sha(Path(__file__)),application_sha256=sha(app),actual_storage_packed_and_public_getters_execute=True,one_source_owner_per_hr_spo2_hrv_cache=True,hour_average_mode_and_log_providers_are_fixtures=True,independent_sequential_cache_and_sample_oracle=True,full_raw_abi_or_private_histories_verified=False,whole_image_complete=False,hardware_write_executed=False);(OUT/'composed-verification.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps({k:v[k] for k in ['workflows','counts','trace_sha256','exact_bytes']}))
if __name__=='__main__':main()
