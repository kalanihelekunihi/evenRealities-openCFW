#!/usr/bin/env python3
"""Native dispatcher frames with independent branch/packet oracle; providers fixtures."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-health-get-dispatch';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();SP=0x2003d000;DATA=0x20010000;STAMP=0x200067a4;REGS=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3];SAVED=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
def main():
 c=json.loads((OUT/'contracts.json').read_text());raw=(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes();obj=OUT/'native_health_get_dispatch.o';proof=[];digest=hashlib.sha256();count=0
 with tempfile.TemporaryDirectory() as temp:
  td=Path(temp);ld=td/'proof.ld';ld.write_text('SECTIONS { .body 0x8b8e8 : { *(.text.r1_event_service_0008b8e8) } .templates 0x99bc8 : { *(.r1.health.get.templates) } /DISCARD/ : { *(.ARM.exidx*) } }\n'+''.join('%s = 0x%x;\n'%(n,a|1) for a,n in [(int(a,16),n) for a,n in c['providers'].items()])+'__start_log_const_data = 0xc441c; r1_health_notification_last_timestamp = 0x200067a4;\n');elf=td/'proof.elf';subprocess.run(['arm-none-eabi-ld','-T',str(ld),str(obj),'-o',str(elf)],check=True);replacements=[]
  for sec,a,size in [('body',0x8b8e8,516),('templates',0x99bc8,28)]:
   f=td/(sec+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j','.'+sec,'-O','binary',str(elf),str(f)],check=True);d=f.read_bytes();assert len(d)==size and d==raw[a-0x27000:a-0x27000+size];replacements.append((a,d));proof.append(dict(address=hex(a),size=size,sha256=hashlib.sha256(d).hexdigest()))
  machines=[];states=[]
  for side in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x100000);u.mem_write(0x27000,raw);u.mem_map(0x20000000,0x40000)
   if side:
    for a,d in replacements:u.mem_write(a,d)
   state={};states.append(state);machines.append(u)
   def hook(u,a,size,opaque):
    s=opaque;case=s['case'];r=[u.reg_read(x) for x in REGS];sp=u.reg_read(UC_ARM_REG_SP);name=c['providers'][hex(a)];event=[name]
    if a==0x914ec:result=case['mode']
    elif a in [0x91638,0x799d6]:event+=r+[bytes(u.mem_read(sp,4)).hex()] if a==0x91638 else r;result=0x12345678
    elif a==0x8ada4:
     result=0x87654321
     if case['mutation']==1:u.mem_write(DATA,bytes([case['module']^1,case['kind'],0x34,0x12]))
    elif a in [0x8d6ac,0x8d858,0x8e524]:
     fam={0x8d6ac:0,0x8e524:1,0x8d858:5}[a];sample=case['sample'];event+=[fam];u.mem_write(r[0],struct.pack('<II',sample,0x98765432));result=int(sample!=0)
    elif a==0x8adb4:
     result=0xffff8123
     if case['mutation']==2:u.mem_write(DATA+2,b'\xcd\xab')
    elif a in [0x83930,0x83972,0x83c20]:event+=[r[1],r[2],None if r[0]==0 else bytes(u.mem_read(r[0],12 if a==0x83972 else 8)).hex()];result=0xdeadbeef
    elif a==0x8d8fc:event+=r[:3];result=0x76543210
    else:event+=r[:2] if a==0x8b818 else [r[0]];result=0xfedcba98
    s['events'].append(event);u.reg_write(UC_ARM_REG_R0,result);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
   for a in c['providers']:u.hook_add(UC_HOOK_CODE,hook,state,begin=int(a,16),end=int(a,16))
  for module,kind,sample,mode,mutation in itertools.product([0,1,2,3,4,5,6,7,255],[0,1,2,255],[0,1,69,70,100,101,255,65535],[0,1,2,4,7],[0,1,2]):
   case=dict(module=module,kind=kind,sample=sample,mode=mode,mutation=mutation);outputs=[]
   for u,s in zip(machines,states):
    s.update(case=case,events=[]);u.mem_write(DATA,bytes([module,kind,0x78,0x56]));u.mem_write(STAMP,b'\xa5'*4);u.mem_write(SP-128,b'\x96'*256)
    for reg,val in zip(REGS,[DATA,0x11223344,0x55667788,0x99aabbcc]):u.reg_write(reg,val)
    for i,reg in enumerate(SAVED):u.reg_write(reg,0x12340000+i)
    u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,0x20000101);u.emu_start(0x8b8e9,0x20000100,count=500)
    assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==SP and [u.reg_read(x) for x in SAVED]==[0x12340000+i for i in range(8)],case
    assert bytes(u.mem_read(STAMP,4))==struct.pack('<I',0x87654321)
    # Independent semantic events after timestamp: branch selection, fresh request ID, packet bytes.
    events=s['events'];idx=next(i for i,x in enumerate(events) if x[0]=='r1_time_backend_timestamp');actual=events[idx+1:];m=module^1 if mutation==1 else module;request=0x1234 if mutation==1 else 0x5678;expected=[]
    if kind==0 and m in [0,1,5]:
     fam={0:'hr',1:'spo2',5:'hrv'}[m];expected.append(['r1_'+fam+'_latest_sample',m]);valid=sample!=0 and (m!=1 or 70<=sample%256<=100)
     packet=None
     if valid:
      expected.append(['r1_time_utc_offset_get']);request=0xabcd if mutation==2 else request;packet=bytearray(struct.pack('<'+'I'*(3 if m==5 else 2),*([0,0x10000,0] if m==5 else [0,0x10000])));struct.pack_into('<I',packet,2,0x98765432);packet[7:7+(2 if m==5 else 1)]=sample.to_bytes(2,'little') if m==5 else bytes([sample%256]);struct.pack_into('<H',packet,0,0x8123)
     expected.append(['r1_health_get_'+fam+'_encode',0,request,None if packet is None else packet.hex()])
    elif kind==0 and m==4:expected=[['r1_event_publish',0x1009,0,0]]
    elif kind==1 and m in [0,1,4,5]:expected=[['r1_health_notification_stage_'+{0:'0008c150',1:'0008cd60',4:'0008baec',5:'0008c750'}[m],request]]
    elif kind==1 and m==6:expected=[['r1_health_notification_stage_0008b818',1,request]]
    assert actual==expected,(case,actual,expected)
    assert sum(x[0]=='r1_structured_log_format' for x in events)==int(bool(mode&5)) and sum(x[0]=='nrf_log_frontend_std_2' for x in events)==int(bool(mode&2))
    outputs.append([events,[u.reg_read(x) for x in REGS],bytes(u.mem_read(SP-128,256)).hex(),bytes(u.mem_read(DATA,4)).hex()])
   assert outputs[0]==outputs[1],case
   count+=1;digest.update(json.dumps([case,outputs[0]],sort_keys=True).encode())
 v=dict(application_sha256=c['application_sha256'],comparisons=count,trace_sha256=digest.hexdigest(),exact_spans=proof,exact_bytes=544,object_sha256=sha(obj),report_sha256=sha(OUT/'report.json'),driver_sha256=sha(Path(__file__)),independent_branch_packet_and_fresh_command_oracle=True,all_providers_are_fixtures=True,actual_getter_composition_verified=False,full_raw_abi_or_private_histories_verified=False,whole_image_complete=False,hardware_write_executed=False);(OUT/'verification.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v))
if __name__=='__main__':main()
