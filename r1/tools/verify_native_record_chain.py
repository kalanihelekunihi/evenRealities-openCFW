#!/usr/bin/env python3
"""Record source composition with actual C memcmp, KV/reinitialize boundary fixtures."""
import hashlib,itertools,json,struct,subprocess
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-record-chain';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();SP=0x2003d000;OLD=0x20010000;NEW=OLD+32;FLAG=0x20006da0;HANDLE=0x20007df0;REGS=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3];SAVED=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
def main():
 OUT.mkdir(exist_ok=True);app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();inputs={};bodies=[];objects=[];providers={}
 for stage,obj in [('native-record-update','native_record_update.o'),('native-record-providers','native_record_providers.o')]:
  p=BASE/stage/'contracts.json';c=json.loads(p.read_text());bodies+=c['bodies'];providers.update(c['providers']);objects.append(BASE/stage/obj)
  for f in [p,BASE/stage/'report.json',objects[-1]]:inputs[str(f.relative_to(ROOT))]=sha(f)
 mem=BASE/'native-record-update/memcmp-source.o';objects.append(mem);inputs[str(mem.relative_to(ROOT))]=sha(mem);names={x['symbol'] for x in bodies}|{'r1_native_memcmp'};providers={a:n for a,n in providers.items() if n not in names}
 ld=OUT/'proof.ld';ld.write_text('SECTIONS {'+''.join(' .b%d %s : { *(.text.%s) }'%(i,x['address'],x['symbol']) for i,x in enumerate(bodies))+' .memcmp 0x1000000 : { *(.text.r1_native_memcmp) } /DISCARD/ : { *(.ARM.exidx*) } }\n'+''.join('%s = 0x%x;\n'%(n,int(a,16)|1) for a,n in providers.items())+'__start_log_const_data = 0xc441c; r1_device_id_once_status = 0x20006da0; r1_health_settings_kv_handle = 0x20007df0;\n');elf=OUT/'proof.elf';subprocess.run(['arm-none-eabi-ld','-T',str(ld),*[str(x) for x in objects],'-o',str(elf)],check=True,stderr=subprocess.PIPE);replacements=[];spans=[];differences=[]
 for i,x in enumerate(bodies):
  a=int(x['address'],16);f=OUT/('body'+str(i)+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j','.b'+str(i),'-O','binary',str(elf),str(f)],check=True);data=f.read_bytes();native=raw[a-0x27000:a-0x27000+x['source_span_bytes']];assert len(data)==len(native);diff=[a+j for j,(v,w) in enumerate(zip(native,data)) if v!=w];assert all(0x6c68a<=v<0x6c68e for v in diff);differences+=diff;replacements.append((a,data));spans.append(dict(address=hex(a),size=len(data),native_sha256=hashlib.sha256(native).hexdigest(),source_sha256=sha(f)))
 assert differences and all(0x6c68a<=v<0x6c68e for v in differences)
 mb=OUT/'memcmp.bin';subprocess.run(['arm-none-eabi-objcopy','-j','.memcmp','-O','binary',str(elf),str(mb)],check=True);membytes=mb.read_bytes();machines=[];states=[];digest=hashlib.sha256();counts=dict(workflows=0,memcmp=0,read=0,write=0,reinitialize=0)
 for side in range(2):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x100000);u.mem_write(0x27000,raw);u.mem_map(0x20000000,0x40000);u.mem_map(0x1000000,0x1000)
  if side:
   for a,d in replacements:u.mem_write(a,d)
   u.mem_write(0x1000000,membytes)
  s={};machines.append(u);states.append(s)
  def observe_memcmp(u,a,size,s):s['events'].append(['memcmp'])
  u.hook_add(UC_HOOK_CODE,observe_memcmp,s,begin=0x1000000 if side else 0x2781a,end=0x1000000 if side else 0x2781a)
  def hook(u,a,size,s):
   r=[u.reg_read(x) for x in REGS];case=s['case'];event=[providers[hex(a)]]
   if a==0x914ec:result=case['mode']
   elif a in [0x91638,0x799c0]:event+=r[:3] if a==0x91638 else r[:2];result=0xabcdef01
   elif a==0x73930:
    assert r[:3]==[0x11223344,SP-40,12];event+=[r[0],r[2]];u.mem_write(r[1],b'\x77'*case['partial']);result=case['result']
    if case['mutation']:u.mem_write(NEW,bytes([0,2,255,0]+[0xdd]*8));u.mem_write(HANDLE,struct.pack('<I',0x99887766))
   elif a==0x73968:
    assert r[:3]==[0x99887766 if case['mutation'] else 0x11223344,SP-40,12];event+=[r[0],bytes(u.mem_read(r[1],12)).hex()];result=case['result']
   else:result=0xfedcba98
   s['events'].append(event);u.reg_write(UC_ARM_REG_R0,result);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  for a in providers:u.hook_add(UC_HOOK_CODE,hook,s,begin=int(a,16),end=int(a,16))
 old=bytes([40,1,170,70]+[0xa5]*8);records=[old,bytes([10,1,170,70]+[0xa5]*8)]
 for field,value in itertools.product(range(12),[0,1,39,40,41,42,43,69,70,79,80,100,170,179,180,219,255]):
  d=bytearray(old);d[field]=value;records.append(bytes(d))
 for data,flag,mode,mutation,partial,result in itertools.product(records,[0,1,2,255],[0,7],[0,1],[0,7,12],[0,0xffffffff]):
  case=dict(data=data.hex(),flag=flag,mode=mode,mutation=mutation,partial=partial,result=result);a,b,h,w=data[:4];valid=10<a<100 and b<=1 and 100<h<220 and 30<w<150;expected=[];want=0
  if valid:
   expected=['memcmp'];counts['memcmp']+=1
   if data!=old:
    final=bytes([0,2,255,0]+[0xdd]*8) if mutation else data;expected+=['r1_kv_class_read','r1_kv_class_write'];counts['read']+=1;counts['write']+=1
    change=abs(final[0]-old[0])>2 or final[1]!=old[1] or abs(final[2]-old[2])>9 or abs(final[3]-old[3])>9;trigger=bool(change and flag&1);want=0xfedcba98 if trigger else flag
    if trigger:
     expected+=['r1_structured_log_mode_get']
     if not mode&1:expected+=['r1_structured_log_mode_get']
     if mode&5:expected+=['r1_structured_log_format']
     expected+=['r1_structured_log_mode_get']
     if mode&2:expected+=['nrf_log_frontend_std_0']
     expected+=['r1_record12_reinitialize'];counts['reinitialize']+=1
  outputs=[]
  for u,s in zip(machines,states):
   s.update(case=case,events=[]);u.mem_write(OLD,old);u.mem_write(NEW,data);u.mem_write(FLAG,bytes([flag]));u.mem_write(HANDLE,struct.pack('<I',0x11223344));u.mem_write(SP-128,b'\x96'*256)
   for reg,val in zip(REGS,[OLD,NEW,0x55667788,0x99aabbcc]):u.reg_write(reg,val)
   for i,reg in enumerate(SAVED):u.reg_write(reg,0x12340000+i)
   u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,0x20000101);u.emu_start(0x6c66d,0x20000100,count=600)
   assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==SP and u.reg_read(UC_ARM_REG_R0)==want and [u.reg_read(x) for x in SAVED]==[0x12340000+i for i in range(8)],case
   assert [e[0] for e in s['events']]==expected,(case,s['events'],expected)
   if 'r1_kv_class_write' in expected:assert next(e for e in s['events'] if e[0]=='r1_kv_class_write')[2]==final.hex()
   assert bytes(u.mem_read(OLD,12))==old and bytes(u.mem_read(NEW,12))==(final if 'r1_kv_class_write' in expected else data)
   outputs.append([s['events'],u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(OLD,12)).hex(),bytes(u.mem_read(NEW,12)).hex(),bytes(u.mem_read(HANDLE,4)).hex()])
  assert outputs[0]==outputs[1],case
  counts['workflows']+=1;digest.update(json.dumps([case,outputs[0]],sort_keys=True).encode())
 v=dict(application_sha256=sha(app),workflows=counts['workflows'],counts=counts,trace_sha256=digest.hexdigest(),source_spans=spans,native_span_bytes=412,source_c_memcmp_text_bytes=len(membytes),memcmp_text_sha256=sha(mb),relocated_call_address='0x6c68a',differing_byte_addresses=[hex(a) for a in differences],inputs=inputs,proof_elf_sha256=sha(elf),proof_layout_sha256=sha(ld),driver_sha256=sha(Path(__file__)),actual_validator_wrapper_persist_apply_and_c_memcmp_execute=True,independent_validation_packet_and_threshold_oracle=True,kv_mode_log_and_reinitialize_providers_are_fixtures=True,full_raw_abi_or_private_histories_verified=False,whole_image_complete=False,hardware_write_executed=False);(OUT/'verification.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v))
if __name__=='__main__':main()
