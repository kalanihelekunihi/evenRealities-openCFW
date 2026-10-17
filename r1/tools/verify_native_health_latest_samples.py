#!/usr/bin/env python3
"""Latest getters with independent sequential memory oracle and cache aliases."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-health-latest-samples';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();SP=0x2003d000;DATA=0x20010000;REGS=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3];SAVED=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11];FAMILIES={'hr':(0x2001654c,84,75,1,0x8d6ac,0x5ace8),'spo2':(0x200165a0,84,75,1,0x8e524,0x5baf4),'hrv':(0x200169c0,160,147,2,0x8d858,0x5af20)}
def main():
 c=json.loads((OUT/'contracts.json').read_text());obj=OUT/'native_health_latest_samples.o';config=OUT/'shared-caches.o';app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();proof=[];digest=hashlib.sha256();counts=dict(hr=0,spo2=0,hrv=0,sample=0,packed=0)
 with tempfile.TemporaryDirectory() as temp:
  td=Path(temp);ld=td/'proof.ld';ld.write_text('SECTIONS {'+''.join(' .b%d %s : { *(.text.%s) }'%(i,x['address'],x['symbol']) for i,x in enumerate(c['bodies']))+''.join(' .cache_%s 0x%x : { *(.r1.health.cache.%s) }'%(fam,info[0],fam) for fam,info in FAMILIES.items())+' /DISCARD/ : { *(.ARM.exidx*) } }\n');elf=td/'proof.elf';subprocess.run(['arm-none-eabi-ld','-T',str(ld),str(obj),str(config),'-o',str(elf)],check=True,stderr=subprocess.PIPE);replacements=[]
  for i,x in enumerate(c['bodies']):
   a=int(x['address'],16);f=td/(str(i)+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j','.b'+str(i),'-O','binary',str(elf),str(f)],check=True);d=f.read_bytes();assert len(d)==x['source_span_bytes'] and d==raw[a-0x27000:a-0x27000+len(d)];replacements.append((a,d));proof.append(dict(address=hex(a),size=len(d),sha256=hashlib.sha256(d).hexdigest()))
  syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
  for fam,info in FAMILIES.items():
   assert syms['r1_health_storage_'+fam+'_prefix']==syms['r1_cache_'+fam]==info[0];f=td/(fam+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j','.cache_'+fam,'-O','binary',str(elf),str(f)],check=True);assert f.read_bytes()==bytes(info[1])
  machines=[]
  for side in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x100000);u.mem_write(0x27000,raw);u.mem_map(0x20000000,0x40000)
   if side:
    for a,d in replacements:u.mem_write(a,d)
   machines.append(u)
  cases=[dict(family=fam,kind=kind,value=value,timestamp=ts,dest=dest) for fam,kind,value,ts,dest in itertools.product(FAMILIES,['sample','packed'],[0,1,255,256,65535],[0,1,0x80000000,0xffffffff],['data','null','sample','next','tail','base','stack']) if fam=='hrv' or value<=255]
  cases += [dict(family='hrv',kind='packed',value=v,timestamp=0x98765432,dest='data') for v in range(65536)]
  cases += [dict(family=fam,kind=kind,value=v,timestamp=0x12345678,dest='data') for fam,kind,v in itertools.product(['hr','spo2'],['sample','packed'],range(256))]
  for case in cases:
   fam=case['family'];base,size,offset,width,wrap,packed=FAMILIES[fam];dest={'data':DATA,'null':0,'sample':base+offset,'next':base+offset+1,'tail':base+size-8,'base':base,'stack':SP-16}[case['dest']];cache=bytearray(b'\x96'*size);cache[offset:offset+width]=case['value'].to_bytes(width,'little');struct.pack_into('<I',cache,offset+width,case['timestamp']);memory={base+i:v for i,v in enumerate(cache)};memory.update({DATA+i:0xa5 for i in range(16)});memory.update({SP-64+i:0x96 for i in range(128)})
   def read(a,n):return bytes(memory[a+i] for i in range(n))
   def write(a,d):memory.update({a+i:v for i,v in enumerate(d)})
   iswrap=case['kind']=='sample'
   if iswrap:write(SP-16,struct.pack('<4I',0x55667788,0x99aabbcc,0x12340000,0x20000101))
   result=0
   if dest:
    if iswrap:write(dest,bytes(1 if fam=='spo2' else 4));write(dest+4,bytes(4));write(SP-16,bytes(8));out=SP-16
    else:out=dest
    if int.from_bytes(read(base+offset,width),'little'):
     write(out,read(base+offset,4));write(out+4,read(base+offset+4,width));result=1
    if iswrap and result:write(dest,read(SP-16,width));write(dest+4,read(SP-16+width,4))
   outputs=[]
   for u in machines:
    u.mem_write(base,bytes(cache));u.mem_write(DATA,b'\xa5'*16);u.mem_write(SP-64,b'\x96'*128)
    for reg,val in zip(REGS,[dest,0x11223344,0x55667788,0x99aabbcc]):u.reg_write(reg,val)
    for i,reg in enumerate(SAVED):u.reg_write(reg,0x12340000+i)
    u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,0x20000101);u.emu_start((wrap if iswrap else packed)|1,0x20000100,count=200)
    assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==SP and u.reg_read(UC_ARM_REG_R0)==result and [u.reg_read(x) for x in SAVED]==[0x12340000+i for i in range(8)],case
    assert bytes(u.mem_read(base,size))==read(base,size) and bytes(u.mem_read(DATA,16))==read(DATA,16),case
    if iswrap:assert bytes(u.mem_read(SP-16,8))==read(SP-16,8),case
    outputs.append([[u.reg_read(x) for x in REGS],bytes(u.mem_read(base,size)).hex(),bytes(u.mem_read(DATA,16)).hex(),bytes(u.mem_read(SP-64,128)).hex()])
   assert outputs[0]==outputs[1];counts[fam]+=1;counts[case['kind']]+=1;digest.update(json.dumps([case,outputs[0]],sort_keys=True).encode())
 v=dict(comparisons=sum(counts[x] for x in FAMILIES),counts=counts,trace_sha256=digest.hexdigest(),exact_spans=proof,exact_bytes=230,object_sha256=sha(obj),config_sha256=sha(config),application_sha256=sha(app),report_sha256=sha(OUT/'report.json'),driver_sha256=sha(Path(__file__)),independent_sequential_copy_zero_and_alias_oracle=True,all_hrv_values_and_byte_sample_values_checked=True,actual_nested_getters_execute=True,existing_cache_owners_and_aliases_verified=True,full_raw_abi_or_private_histories_verified=False,whole_image_complete=False,hardware_write_executed=False);(OUT/'verification.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v))
if __name__=='__main__':main()
