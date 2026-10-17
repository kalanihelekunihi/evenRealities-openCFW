#!/usr/bin/env python3
"""Record apply thresholds and persistence sequential-copy callback oracle."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-record-providers';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();SP=0x2003d000;OLD=0x20010000;NEW=OLD+32;FLAG=0x20006da0;HANDLE=0x20007df0;REGS=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3];SAVED=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
def main():
 c=json.loads((OUT/'contracts.json').read_text());raw=(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes();obj=OUT/'native_record_providers.o';proof=[];digest=hashlib.sha256();counts=dict(apply=0,persist=0,reinitialize=0,read=0,write=0)
 with tempfile.TemporaryDirectory() as temp:
  td=Path(temp);ld=td/'proof.ld';ld.write_text('SECTIONS {'+''.join(' .b%d %s : { *(.text.%s) }'%(i,x['address'],x['symbol']) for i,x in enumerate(c['bodies']))+' /DISCARD/ : { *(.ARM.exidx*) } }\n'+''.join('%s = 0x%x;\n'%(n,int(a,16)|1) for a,n in c['providers'].items())+'__start_log_const_data = 0xc441c; r1_device_id_once_status = 0x20006da0; r1_health_settings_kv_handle = 0x20007df0;\n');elf=td/'proof.elf';subprocess.run(['arm-none-eabi-ld','-T',str(ld),str(obj),'-o',str(elf)],check=True,stderr=subprocess.PIPE);replacements=[]
  for i,x in enumerate(c['bodies']):
   a=int(x['address'],16);f=td/(str(i)+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j','.b'+str(i),'-O','binary',str(elf),str(f)],check=True);d=f.read_bytes();assert len(d)==x['source_span_bytes'] and d==raw[a-0x27000:a-0x27000+len(d)];replacements.append((a,d));proof.append(dict(address=hex(a),size=len(d),sha256=hashlib.sha256(d).hexdigest()))
  machines=[];states=[]
  for side in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x100000);u.mem_write(0x27000,raw);u.mem_map(0x20000000,0x40000)
   if side:
    for a,d in replacements:u.mem_write(a,d)
   s={};machines.append(u);states.append(s)
   def hook(u,a,size,s):
    r=[u.reg_read(x) for x in REGS];case=s['case'];event=[hex(a)]
    if a==0x914ec:result=case['mode']
    elif a==0x91638:assert r[:3]==[0xc000000,0x6c5cc,0x6c5cc];event+=r;result=0x12345678
    elif a==0x799c0:assert r[:2]==[0x1c0003,0x6c60c];event+=r;result=0xabcdef01
    elif a==0x4c37c:result=case['result']
    elif a==0x73930:
     assert r[:3]==[0x11223344,SP-24,12];event+=r[:3];result=case['result'];u.mem_write(r[1],b'\x77'*case['read_count'])
     if case['mutation']:u.mem_write(HANDLE,struct.pack('<I',0x99887766));u.mem_write(case['ptr'],bytes(range(12)))
    else:
     assert r[:3]==[0x99887766 if case['mutation'] else 0x11223344,SP-24,12];event+=[r[0],bytes(u.mem_read(r[1],12)).hex()];result=case['result']
    s['events'].append(event);u.reg_write(UC_ARM_REG_R0,result);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
   for a in c['providers']:u.hook_add(UC_HOOK_CODE,hook,s,begin=int(a,16),end=int(a,16))
  cases=[]
  for field,value,flag,mode in itertools.product(range(4),range(256),[0,1,2,255],[0,7]):
   old=bytes([40,1,170,70]+[0xa5]*8);new=bytearray(old);new[field]=value;cases.append(dict(kind='apply',old=old.hex(),new=bytes(new).hex(),oldptr=OLD,newptr=NEW,flag=flag,mode=mode,result=0xfedcba98))
  for oldptr,newptr in [(0,NEW),(OLD,0),(0,0)]:cases.append(dict(kind='apply',old=bytes(12).hex(),new=bytes(12).hex(),oldptr=oldptr,newptr=newptr,flag=1,mode=7,result=1))
  for ptr,read_count,mutation,result in itertools.product([0,NEW,SP-24,SP-20],[0,1,7,12],[0,1],[0,1,0xffffffff]):cases.append(dict(kind='persist',ptr=ptr,read_count=read_count,mutation=mutation,result=result))
  for case in cases:
   apply=case['kind']=='apply';expected=[];want=0
   if apply:
    old=bytes.fromhex(case['old']);new=bytes.fromhex(case['new']);change=abs(new[0]-old[0])>2 or new[1]!=old[1] or abs(new[2]-old[2])>9 or abs(new[3]-old[3])>9;trigger=bool(change and case['flag']&1 and case['oldptr'] and case['newptr']);want=case['oldptr'] if not case['oldptr'] or not case['newptr'] else case['result'] if trigger else case['flag']
    if trigger:
     expected=['0x914ec']
     if not case['mode']&1:expected+=['0x914ec']
     if case['mode']&5:expected+=['0x91638']
     expected+=['0x914ec']
     if case['mode']&2:expected+=['0x799c0']
     expected+=['0x4c37c'];counts['reinitialize']+=1
   else:
    want=case['result'] if case['ptr'] else 0
    if case['ptr']:expected=['0x73930','0x73968'];counts['read']+=1;counts['write']+=1
   outputs=[]
   for u,s in zip(machines,states):
    s.update(case=case,events=[]);u.mem_write(OLD,b'\xa5'*64);u.mem_write(SP-64,b'\x96'*128);u.mem_write(HANDLE,struct.pack('<I',0x11223344))
    if apply:u.mem_write(OLD,old);u.mem_write(NEW,new);u.mem_write(FLAG,bytes([case['flag']]));args=[case['oldptr'],case['newptr'],0x55667788,0x99aabbcc];entry=0x6c53c
    else:
     u.mem_write(NEW,bytes(range(0xa0,0xac)));args=[case['ptr'],0x11223344,0x55667788,0x99aabbcc];entry=0x73604
     # Native push places incoming r1-r3 at its scratch buffer before read.
     memory={SP-64+i:0x96 for i in range(128)};memory.update({NEW+i:0xa0+i for i in range(12)});memory.update({SP-24+i:v for i,v in enumerate(struct.pack('<6I',*args[1:],0x12340000,0x12340001,0x20000101))})
     if case['ptr']:
      memory.update({SP-24+i:0x77 for i in range(case['read_count'])})
      if case['mutation']:memory.update({case['ptr']+i:i for i in range(12)})
      for off in [0,4,8]:
       word=bytes(memory[case['ptr']+off+i] for i in range(4));memory.update({SP-24+off+i:v for i,v in enumerate(word)})
      wanted_payload=bytes(memory[SP-24+i] for i in range(12)).hex()
    expected_saved=[0x12340000+i for i in range(8)]
    if not apply and case['ptr']:expected_saved[:2]=[int.from_bytes(bytes(memory[SP-12+off+i] for i in range(4)),'little') for off in [0,4]]
    for reg,val in zip(REGS,args):u.reg_write(reg,val)
    for i,reg in enumerate(SAVED):u.reg_write(reg,0x12340000+i)
    u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,0x20000101);u.emu_start(entry|1,0x20000100,count=250)
    assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==SP and u.reg_read(UC_ARM_REG_R0)==want and [u.reg_read(x) for x in SAVED]==expected_saved,case
    assert [e[0] for e in s['events']]==expected,(case,s['events'],expected)
    if not apply and case['ptr']:assert s['events'][-1][2]==wanted_payload,(case,s['events'],wanted_payload)
    outputs.append([s['events'],[u.reg_read(x) for x in REGS],bytes(u.mem_read(SP-64,128)).hex(),bytes(u.mem_read(OLD,64)).hex(),bytes(u.mem_read(HANDLE,4)).hex()])
   assert outputs[0]==outputs[1],case
   counts[case['kind']]+=1;digest.update(json.dumps([case,outputs[0]],sort_keys=True).encode())
 v=dict(application_sha256=c['application_sha256'],comparisons=len(cases),counts=counts,trace_sha256=digest.hexdigest(),exact_spans=proof,exact_bytes=308,object_sha256=sha(obj),report_sha256=sha(OUT/'report.json'),driver_sha256=sha(Path(__file__)),existing_status_byte_and_kv_handle_reused=True,independent_threshold_and_sequential_copy_oracle=True,mode_log_reinitialize_and_kv_providers_are_fixtures=True,full_raw_abi_or_private_histories_verified=False,whole_image_complete=False,hardware_write_executed=False);(OUT/'verification.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v))
if __name__=='__main__':main()
