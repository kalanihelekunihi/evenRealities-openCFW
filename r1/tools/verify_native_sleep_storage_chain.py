#!/usr/bin/env python3
"""Full local storage chain and C CRC against an independent image/state model."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-sleep-storage-chain';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();B=0x10000000;SP=0x2003d000;PAY=0x20010000;CTX=0x200067b4;REGION=0x20030000;OPS=REGION+128;READ=0x20001000;WRITE=READ+16;ERASE=READ+32;REGS=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3];SAVED=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11];MAGIC=0xccffaabb;VALID=0x66889977
STAGES=['native-sleep-record','native-sleep-sector-select','native-sleep-sector-write','native-sleep-sector-finalize'];states={};PROVIDERS={0x277aa:'__aeabi_memclr',0x914ec:'r1_structured_log_mode_get',0x91638:'r1_structured_log_format',0x799c0:'nrf_log_frontend_std_0',0x799c8:'nrf_log_frontend_std_1',0x799d6:'nrf_log_frontend_std_2',0x799e6:'nrf_log_frontend_std_3',0x8b138:'r1_health_event_notification_throttle'}
def crc(data):
 v=65535
 for x in data:
  v^=x
  for _ in range(8):v=(v>>1)^ (0xa001 if v&1 else 0)
 return v
class Image:
 def __init__(self,case):self.case=case;self.data=bytearray(b'\xff'*(case['sectors']*4096));self.trace=[];self.attempts=dict(data=0,header=0,commit=0,erase=0)
 def read(self,a,n):
  assert B<=a and a+n<=B+len(self.data),(a,n);d=bytes(self.data[a-B:a-B+n]);self.trace.append(['read',a,n,d.hex()]);return d
 def write(self,a,d):
  assert B<=a and a+len(d)<=B+len(self.data),(hex(a),len(d));kind='commit' if len(d)==16 else 'header' if len(d)==20 else 'data';self.attempts[kind]+=1;plan=self.case['error'];fail=(kind=='data' and ((plan=='data_once' and self.attempts[kind]==1) or (plan=='data_twice' and self.attempts[kind]<=2))) or (kind=='header' and plan=='header_once' and self.attempts[kind]==1) or (kind=='commit' and plan=='commit_once' and self.attempts[kind]==1);result=int(fail)
  if not fail:self.data[a-B:a-B+len(d)]=d
  self.trace.append(['write',a,len(d),hashlib.sha256(d).hexdigest(),result]);return result
 def erase(self,a,n):
  assert B<=a and a+n<=B+len(self.data);self.attempts['erase']+=1;result=int(self.case['error']=='erase_once' and self.attempts['erase']==1)
  if not result:self.data[a-B:a-B+n]=b'\xff'*n
  self.trace.append(['erase',a,n,result]);return result
 def log(self,level,fmt,std,args):
  mo=self.case['mode'];self.trace.append(['mode'])
  if not mo&1:self.trace.append(['mode'])
  if mo&5:self.trace.append(['printf',(level<<26)|(len(args)<<22),fmt,args])
  self.trace.append(['mode'])
  if mo&2:self.trace.append(['std',0x1c0000+level,std,args])
class Model(Image):
 def select(self):
  for i in range(self.case['sectors']):
   a,b,c,_=struct.unpack('<4I',self.read(B+i*4096,16))
   if a==0xffffffff or (b==0xffffffff and c==0xffffffff) or (a==MAGIC and b!=VALID):return i
  return None
 def fallback(self):
  best=0xffffffff;chosen=0
  for i in range(self.case['sectors']):
   v=struct.unpack_from('<I',self.read(B+i*4096,16),8)[0]
   if v<best:best=v;chosen=i
  self.erase(B+chosen*4096,4096);self.log(3,0x8fdc8,0x8fdf0,[B+chosen*4096]);return chosen
 def finalize(self,s):
  best=0xffffffff
  for i in range(self.case['sectors']):best=min(best,struct.unpack_from('<I',self.read(B+i*4096,16),8)[0])
  counter=(0 if best==0xffffffff else best)+1;self.log(3,0x902b0,0x902e4,[counter]);return int(self.write(B+s*4096,struct.pack('<4I',MAGIC,VALID,counter,0))==0)
 def writer(self,s,p):
  fixed=B+s*4096+16;dest=fixed+192;aligned=(len(p)+3)&65532;free=None;h=None
  for i in range(8):
   h=bytearray(self.read(fixed+i*24,24))
   if struct.unpack_from('<2I',h,8)==(0xffffffff,0xffffffff):free=i;break
   length,offset=struct.unpack_from('<2H',h);dest=B+s*4096+length+offset
  if free is None:return 0
  if B+(s+1)*4096<dest+aligned:self.log(1,0x900a0,0x900c4,[dest,aligned]);self.finalize(s);return 0
  result=self.write(dest,p[:aligned])
  if result:self.log(1,0x900e0,0x90114,[result]);return 0
  struct.pack_into('<2H',h,0,aligned,(dest-((B&65535)+(s<<12)))&65535);struct.pack_into('<H',h,6,struct.unpack_from('<H',p,10)[0]);h[8:16]=p[12:20];self.trace.append(['crc',aligned,hashlib.sha256(p[:aligned]).hexdigest()]);struct.pack_into('<H',h,18,crc(p[:aligned]));result=self.write(fixed+free*24,h[:20])
  if result:self.log(1,0x90140,0x90174,[result]);return 0
  self.log(3,0xbfaf8,0x901a4,[dest,len(p),free+1]);return self.finalize(s) if free==7 else 1
 def store(self,p):
  for _ in range(2):
   sector=self.select()
   if sector is None:sector=self.fallback()
   if self.writer(sector,p):self.log(3,0x5baa0,0x5bac8,[sector]);return 1
  for i in range(self.case['sectors']):self.erase(B+i*4096,4096)
  self.log(1,0x5ba40,0x5ba74,[]);return 0
 def call(self,p):
  result=self.store(p)
  if self.case['entry']=='event':
   if result:self.trace.append(['throttle',6]);return 0xcafebabe
   self.log(1,0x8dd50,0x8dd70,[]);return 0x98765432 if self.case['mode']&2 else (self.case['mode']<<30)&0xffffffff
  return result

def main():
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();objects=[BASE/stage/(stage.replace('-','_')+'.o') for stage in STAGES];crcobj=BASE/'r1__source__stock_checksums.c.o';contextobj=BASE/'native-sleep-sync-status/native_sleep_sync_status.o';bodies=[]
 for stage in STAGES:bodies+=json.loads((BASE/stage/'contracts.json').read_text())['bodies']
 proof=[];digest=hashlib.sha256();counts=dict(workflows=0,records=0,reads=0,writes=0,erases=0,crc=0);inputs={str(p.relative_to(ROOT)):sha(p) for p in [*objects,crcobj,contextobj,BASE/'native-sleep-sector-finalize/report.json',ROOT/'r1/source/stock_checksums.c',ROOT/'r1/source/stock_checksum_tables.inc',ROOT/'r1/source/include/r1_stock_checksums.h']}
 with tempfile.TemporaryDirectory() as tmp:
  td=Path(tmp);ctx=td/'context.o';subprocess.run(['arm-none-eabi-ld','-r','--gc-sections','-u','r1_sleep_sync_context_prefix',str(contextobj),'-o',str(ctx)],check=True);ld=td/'proof.ld';ld.write_text('SECTIONS {'+''.join(' .b%d %s : { *(.text.%s) }'%(i,x['address'],x['symbol']) for i,x in enumerate(bodies))+' .success 0xbfaf8 : { *(.r1.sleep.write.success) } .context 0x200067b4 : { *(.r1.sleep.sync.context) } .crc 0x5d87c : { *(.text) } .tables 0x995a8 : { *(.rodata) } /DISCARD/ : { *(.ARM.exidx*) } }\n'+''.join('%s = 0x%x;\n'%(n,a+1) for a,n in PROVIDERS.items())+'__start_log_const_data = 0xc441c;\n');elf=td/'proof.elf';subprocess.run(['arm-none-eabi-ld','-T',str(ld),*[str(p) for p in objects],str(crcobj),str(ctx),'-o',str(elf)],check=True,stderr=subprocess.PIPE);replacements=[]
  for sec,a,n,exact in [*[(f'.b{i}',int(x['address'],16),x['source_span_bytes'],True) for i,x in enumerate(bodies)],('.success',0xbfaf8,69,True),('.tables',0x995a8,1536,True),('.crc',0x5d87c,516,False),('.context',CTX,12,False)]:
   f=td/(sec[1:]+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j',sec,'-O','binary',str(elf),str(f)],check=True);d=f.read_bytes();assert len(d)==n
   if exact:assert d==raw[a-0x27000:a-0x27000+n]
   elif sec=='.context':assert d==bytes(12)
   replacements.append((a,d));proof.append(dict(section=sec,address=hex(a),size=n,sha256=hashlib.sha256(d).hexdigest(),native_exact=exact))
  (OUT/'source-chain-proof.elf').write_bytes(elf.read_bytes());(OUT/'source-chain-layout.ld').write_text(ld.read_text())
  def hook(u,a,size,_):
   s=states[id(u)];im=s['image'];r=[u.reg_read(x) for x in REGS];sp=u.reg_read(UC_ARM_REG_SP);ret=0x98765432
   if a==0x5d87c:im.trace.append(['crc',r[1],hashlib.sha256(bytes(u.mem_read(r[0],r[1]))).hexdigest()]);counts['crc']+=1;return
   if a==READ:counts['reads']+=1;u.mem_write(r[1],im.read(r[0],r[2]));ret=0xffffffff
   elif a==WRITE:counts['writes']+=1;ret=im.write(r[0],bytes(u.mem_read(r[1],r[2])))
   elif a==ERASE:counts['erases']+=1;ret=im.erase(r[0],r[1])
   elif a==0x277aa:u.mem_write(r[0],bytes(r[1]));ret=0
   elif a==0x914ec:im.trace.append(['mode']);ret=im.case['mode']
   elif a==0x8b138:assert r[0]==6;im.trace.append(['throttle',6]);ret=0xcafebabe
   elif a==0x91638:
    assert r[1]==r[2];n=(r[0]>>22)&15;args=([r[3]]+list(struct.unpack('<2I',u.mem_read(sp,8))))[:n];im.trace.append(['printf',r[0],r[1],args])
   else:
    n={0x799c0:0,0x799c8:1,0x799d6:2,0x799e6:3}[a];args=([r[2],r[3]]+list(struct.unpack('<I',u.mem_read(sp,4))))[:n];im.trace.append(['std',r[0],r[1],args])
   for reg,v in zip(REGS,[ret,0xa1a1a1a1,0xb2b2b2b2,0xc3c3c3c3]):u.reg_write(reg,v)
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  machines=[]
  for side in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x100000);u.mem_write(0x27000,raw);u.mem_map(0x20000000,0x40000)
   if side:
    for a,d in replacements:u.mem_write(a,d)
   for a in [READ,WRITE,ERASE,0x5d87c,*PROVIDERS]:u.hook_add(UC_HOOK_CODE,hook,begin=a,end=a)
   machines.append(u)
  cases=[dict(sectors=n,length=length,records=recs,mode=mode,error=err,entry=entry) for n,length,recs,mode,err,entry in itertools.product([1,2,3],[32,64,512,3888],[1,8,9,25],[0,7],['none','data_once','data_twice','header_once','commit_once','erase_once'],['store','event'])]
  for case in cases:
   model=Model(case);images=[Image(case),Image(case)]
   for u,im in zip(machines,images):
    u.mem_write(CTX,struct.pack('<3I',1,REGION,OPS));u.mem_write(REGION,bytes(256));u.mem_write(REGION+52,struct.pack('<2I',B,case['sectors']*4096));u.mem_write(OPS+40,struct.pack('<3I',READ+1,WRITE+1,ERASE+1));states[id(u)]=dict(image=im)
   for record in range(case['records']):
    p=bytearray((i*17+record*7+3)&255 for i in range(case['length']));struct.pack_into('<H2I',p,10,record&65535,0x10000000+record,0x20000000+record);struct.pack_into('<H',p,30,case['length']-32);start=len(model.trace);expected=model.call(bytes(p));outputs=[]
    for u,im in zip(machines,images):
     before=len(im.trace);u.mem_write(PAY,bytes(p));u.mem_write(SP-512,b'\x96'*768)
     for reg,v in zip(REGS,[PAY,len(p),0x55667788,0x99aabbcc]):u.reg_write(reg,v)
     for i,reg in enumerate(SAVED):u.reg_write(reg,0x12340000+i)
     u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,0x20000101);u.emu_start(0x5b891 if case['entry']=='store' else 0x8dc95,0x20000100,count=2000000)
     assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==SP and u.reg_read(UC_ARM_REG_R0)==expected and [u.reg_read(x) for x in SAVED]==[0x12340000+i for i in range(8)],(case,record,u.reg_read(UC_ARM_REG_R0),expected)
     observed=im.trace[before:];assert observed==model.trace[start:],(case,record,next(((i,a,b) for i,(a,b) in enumerate(zip(observed,model.trace[start:])) if a!=b),('length',len(observed),len(model.trace[start:]))));assert im.data==model.data,(case,record)
     outputs.append([u.reg_read(UC_ARM_REG_R0),observed,bytes(u.mem_read(CTX,12)).hex(),hashlib.sha256(im.data).hexdigest(),bytes(u.mem_read(PAY,len(p))).hex()])
    assert outputs[0]==outputs[1];counts['records']+=1;digest.update(json.dumps([case,record,outputs[0]],sort_keys=True).encode())
   counts['workflows']+=1
 v=dict(workflows=counts['workflows'],record_comparisons=counts['records'],counts=counts,trace_sha256=digest.hexdigest(),source_spans=proof,native_exact_storage_bytes=sum(x['size'] for x in proof if x['native_exact'] and x['section']!='.tables'),native_exact_checksum_table_bytes=1536,source_crc_text_bytes=516,inputs=inputs,proof_elf_sha256=sha(OUT/'source-chain-proof.elf'),proof_layout_sha256=sha(OUT/'source-chain-layout.ld'),driver_sha256=sha(Path(__file__)),application_sha256=sha(app),actual_record_event_select_fallback_write_finalize_erase_count_and_c_crc_execute=True,independent_repeated_append_error_and_flash_image_oracle=True,io_image_memclear_mode_log_and_throttle_are_fixtures=True,crc_standalone_placement_overlaps_unused_native_crc_routines=True,full_raw_abi_or_private_histories_verified=False,whole_image_complete=False,hardware_write_executed=False);(OUT/'verification.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps({k:v[k] for k in ['workflows','record_comparisons','counts','trace_sha256','native_exact_storage_bytes']}))
if __name__=='__main__':main()
