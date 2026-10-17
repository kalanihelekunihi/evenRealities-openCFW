#!/usr/bin/env python3
"""Actual dispatcher/getters/encoders/sender; independent packet/header oracle."""
import hashlib,itertools,json,struct,subprocess
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-health-get-chain';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();SP=0x2003d000;DATA=0x20010000;STAMP=0x200067a4;REGS=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3];SAVED=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11];CACHES={0:(0x2001654c,84,75,1),1:(0x200165a0,84,75,1),5:(0x200169c0,160,147,2)}
def main():
 OUT.mkdir(exist_ok=True);raw=(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes();inputs={};bodies=[];objects=[]
 for stage,obj in [('native-health-get-dispatch','native_health_get_dispatch.o'),('native-health-latest-samples','native_health_latest_samples.o'),('native-health-get-encoders','native_health_get_encoders.o')]:
  p=BASE/stage/'contracts.json';c=json.loads(p.read_text());bodies+=c['bodies'];objects.append(BASE/stage/obj)
  for f in [p,BASE/stage/'report.json',objects[-1]]:inputs[str(f.relative_to(ROOT))]=sha(f)
 config=BASE/'native-health-latest-samples/shared-caches.o';objects.append(config);inputs[str(config.relative_to(ROOT))]=sha(config)
 allproviders={}
 for stage in ['native-health-get-dispatch','native-health-get-encoders']:allproviders.update(json.loads((BASE/stage/'contracts.json').read_text())['providers'])
 body_names={x['symbol'] for x in bodies};providers={a:n for a,n in allproviders.items() if n not in body_names}
 layout='SECTIONS {'+''.join(' .b%d %s : { *(.text.%s) }'%(i,x['address'],x['symbol']) for i,x in enumerate(bodies))+' .templates 0x99bc8 : { *(.r1.health.get.templates) }'+''.join(' .cache%d 0x%x : { *(.r1.health.cache.%s) }'%(m,a,{0:'hr',1:'spo2',5:'hrv'}[m]) for m,(a,_,_,_) in CACHES.items())+' /DISCARD/ : { *(.ARM.exidx*) } }\n'+''.join('%s = 0x%x;\n'%(n,int(a,16)|1) for a,n in providers.items())+'__start_log_const_data = 0xc441c; r1_health_notification_last_timestamp = 0x200067a4;\n'
 ld=OUT/'proof.ld';ld.write_text(layout);elf=OUT/'proof.elf';subprocess.run(['arm-none-eabi-ld','-T',str(ld),*[str(o) for o in objects],'-o',str(elf)],check=True,stderr=subprocess.PIPE);proof=[];replacements=[]
 for sec,a,size in [('b'+str(i),int(x['address'],16),x['source_span_bytes']) for i,x in enumerate(bodies)]+[('templates',0x99bc8,28)]:
  f=OUT/(sec+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j','.'+sec,'-O','binary',str(elf),str(f)],check=True);d=f.read_bytes();assert len(d)==size and d==raw[a-0x27000:a-0x27000+size];replacements.append((a,d));proof.append(dict(address=hex(a),size=size,sha256=hashlib.sha256(d).hexdigest()))
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 for m,(a,size,_,_) in CACHES.items():
  fam={0:'hr',1:'spo2',5:'hrv'}[m];assert syms['r1_cache_'+fam]==syms['r1_health_storage_'+fam+'_prefix']==a;f=OUT/('cache'+str(m)+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j','.cache'+str(m),'-O','binary',str(elf),str(f)],check=True);assert f.read_bytes()==bytes(size)
 machines=[];states=[];digest=hashlib.sha256();counts=dict(workflows=0,response=0,flag=0,invalid_handle=0,offset=0)
 for side in range(2):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x100000);u.mem_write(0x27000,raw);u.mem_map(0x20000000,0x40000)
  if side:
   for a,d in replacements:u.mem_write(a,d)
  s={};machines.append(u);states.append(s)
  def hook(u,a,size,s):
   r=[u.reg_read(x) for x in REGS];sp=u.reg_read(UC_ARM_REG_SP);case=s['case'];event=[providers[hex(a)]]
   if a==0x914ec:result=case['mode']
   elif a in [0x91638,0x799d6]:event+=r+[bytes(u.mem_read(sp,4)).hex()] if a==0x91638 else r;result=0x12345678
   elif a==0x8ada4:result=0x87654321
   elif a==0x8adb4:
    result=case['offset']
    if case['mutation']:u.mem_write(DATA+2,b'\xcd\xab')
   elif a==0x4cba4:
    result=case['handle']
    if case['mutation']:u.mem_write(DATA+2,b'\x11\x22')
   elif a==0x8280c:event+=[r,bytes(u.mem_read(sp,4)).hex()];result=case['result']
   elif a==0x828b4:event+=[r[0],bytes(u.mem_read(r[1],8)).hex(),r[3],bytes(u.mem_read(r[2],r[3])).hex()];result=case['result']
   else:raise AssertionError((hex(a),case))
   s['events'].append(event);u.reg_write(UC_ARM_REG_R0,result);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  for a in providers:u.hook_add(UC_HOOK_CODE,hook,s,begin=int(a,16),end=int(a,16))
 for module,sample,mode,offset,handle,result,mutation in itertools.product([0,1,5],[0,1,69,70,100,101,255,256,65535],[0,7],[0,0xffff8123],[0,65535,0xffffffff],[0,2],[0,1]):
  case=dict(module=module,sample=sample,mode=mode,offset=offset,handle=handle,result=result,mutation=mutation);outputs=[];width=CACHES[module][3];value=sample&((1<<(width*8))-1);valid=value!=0 and (module!=1 or 70<=value<=100);request=0xabcd if valid and mutation else 0x5678;command={0:0x102,1:0x202,5:0x402}[module];expected=[]
  if valid:expected.append(['r1_time_utc_offset_get']);counts['offset']+=1
  expected.append(['r1_phone_connection_handle_get'])
  if not valid:expected.append(['r1_protocol_send_flag_set_a',[handle,command,2,request],'00000000']);want=int(result!=0);counts['flag']+=1
  elif handle==65535:want=0;counts['invalid_handle']+=1
  else:
   packet=bytearray(9 if module==5 else 8);struct.pack_into('<H',packet,0,offset&65535);struct.pack_into('<I',packet,2,0x98765432);packet[6]=1;packet[7:]=value.to_bytes(width,'little');header=bytes([3,2,command>>8,command&255])+struct.pack('<I',request);expected.append(['r1_protocol_send_response',handle,header.hex(),len(packet),packet.hex()]);want=int(result==0);counts['response']+=1
  for u,s in zip(machines,states):
   s.update(case=case,events=[]);u.mem_write(DATA,bytes([module,0,0x78,0x56]));u.mem_write(STAMP,b'\xa5'*4);u.mem_write(SP-256,b'\x96'*512)
   for m,(a,size,off,w) in CACHES.items():
    cache=bytearray(b'\xa5'*size);cache[off:off+w]=(sample&((1<<(w*8))-1)).to_bytes(w,'little');struct.pack_into('<I',cache,off+w,0x98765432);u.mem_write(a,bytes(cache))
   for reg,val in zip(REGS,[DATA,0x11223344,0x55667788,0x99aabbcc]):u.reg_write(reg,val)
   for i,reg in enumerate(SAVED):u.reg_write(reg,0x12340000+i)
   u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,0x20000101);u.emu_start(0x8b8e9,0x20000100,count=600)
   assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==SP and u.reg_read(UC_ARM_REG_R0)==want and [u.reg_read(x) for x in SAVED]==[0x12340000+i for i in range(8)],case
   events=s['events'];idx=next(i for i,x in enumerate(events) if x[0]=='r1_time_backend_timestamp');assert events[idx+1:]==expected,(case,events[idx+1:],expected);assert bytes(u.mem_read(STAMP,4))==struct.pack('<I',0x87654321)
   for a,size,off,w in CACHES.values():
    expected_cache=bytearray(b'\xa5'*size);expected_cache[off:off+w]=(sample&((1<<(w*8))-1)).to_bytes(w,'little');struct.pack_into('<I',expected_cache,off+w,0x98765432);assert bytes(u.mem_read(a,size))==bytes(expected_cache),case
   outputs.append([events,[u.reg_read(x) for x in REGS],bytes(u.mem_read(SP-256,512)).hex(),bytes(u.mem_read(DATA,4)).hex(),[bytes(u.mem_read(a,size)).hex() for a,size,_,_ in CACHES.values()]])
  assert outputs[0]==outputs[1],case
  counts['workflows']+=1;digest.update(json.dumps([case,outputs[0]],sort_keys=True).encode())
 v=dict(application_sha256=c['application_sha256'],workflows=counts['workflows'],counts=counts,trace_sha256=digest.hexdigest(),exact_spans=proof,exact_bytes=sum(x['size'] for x in proof),inputs=inputs,proof_elf_sha256=sha(elf),proof_layout_sha256=sha(ld),driver_sha256=sha(Path(__file__)),actual_dispatcher_getters_encoders_and_sender_execute=True,shared_cache_bytes=328,independent_packet_header_and_result_oracle=True,time_offset_phone_log_flag_and_response_providers_are_fixtures=True,full_raw_abi_or_private_histories_verified=False,whole_image_complete=False,hardware_write_executed=False);(OUT/'verification.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v))
if __name__=='__main__':main()
