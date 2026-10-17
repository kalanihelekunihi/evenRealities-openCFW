#!/usr/bin/env python3
"""HR init and byte event helper, including native stack callback mutations."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-health-init';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();SP=0x2003d000;REGS=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3];SAVED=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
def main():
 c=json.loads((OUT/'contracts.json').read_text());raw=(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes();obj=OUT/'native_health_init.o';proof=[];digest=hashlib.sha256();counts=dict(service=0,helper=0,publish=0,format=0,standard=0)
 with tempfile.TemporaryDirectory() as temp:
  td=Path(temp);ld=td/'proof.ld';ld.write_text('SECTIONS {'+''.join(' .b%d %s : { *(.text.%s) }'%(i,x['address'],x['symbol']) for i,x in enumerate(c['bodies']))+' /DISCARD/ : { *(.ARM.exidx*) } }\n'+''.join('%s = 0x%x;\n'%(n,int(a,16)|1) for a,n in c['providers'].items() if a!='0x8a866')+'__start_log_const_data = 0xc441c;\n');elf=td/'proof.elf';subprocess.run(['arm-none-eabi-ld','-T',str(ld),str(obj),'-o',str(elf)],check=True,stderr=subprocess.PIPE);replacements=[]
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
    if a==0x914ec:result=case['modes'][s['mode_index']];s['mode_index']+=1;event+=[result]
    elif a==0x91638:assert r[:3]==[0xc000000,0x8d3c4,0x8d3c4];result=case['result'];event+=r
    elif a==0x799c0:assert r[:2]==[0x1c0003,0x8d3f0];result=case['result'];event+=r
    else:
     value=1 if case['entry']==0x8d380 else case['value'];assert r[:3]==[0x1001,SP-8,1] and bytes(u.mem_read(r[1],4))==struct.pack('<I',value);event+=[r[0],bytes(u.mem_read(r[1],4)).hex(),r[2]];result=case['result']
     if case['mutation']:u.mem_write(r[1],struct.pack('<I',0xaabbccdd))
    s['events'].append(event);u.reg_write(UC_ARM_REG_R0,result);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
   for a in [0x914ec,0x91638,0x799c0,0x8d8fc]:u.hook_add(UC_HOOK_CODE,hook,s,begin=a,end=a)
  cases=[dict(entry=0x8d380,value=0x12345678,modes=list(modes),result=result,mutation=mutation) for modes,result,mutation in itertools.product(itertools.product([0,1,2,4,7,0xffffffff],repeat=3),[0,1,0x80000000,0xffffffff],[0,1])]+[dict(entry=0x8a866,value=value,modes=[0,0,0],result=result,mutation=mutation) for value,result,mutation in itertools.product(list(range(256))+[256,257,259,260,65535,0xffffffff],[0,1,0x80000000,0xffffffff],[0,1])]
  for case in cases:
   service=case['entry']==0x8d380;value=1 if service else case['value'];pub=service or value&255<4;expected_names=[]
   if service:
    modes=case['modes'];expected_names.append('0x914ec');i=1
    if not modes[0]&1:expected_names.append('0x914ec');i=2
    fmt=bool(modes[0]&1 or modes[1]&4)
    if fmt:expected_names.append('0x91638');counts['format']+=1
    expected_names.append('0x914ec')
    if modes[i]&2:expected_names.append('0x799c0');counts['standard']+=1
   if pub:expected_names.append('0x8d8fc');counts['publish']+=1
   outputs=[]
   for u,s in zip(machines,states):
    s.update(case=case,events=[],mode_index=0);u.mem_write(SP-64,b'\x96'*128)
    for reg,val in zip(REGS,[case['value'],0x11223344,0x55667788,0x99aabbcc]):u.reg_write(reg,val)
    for i,reg in enumerate(SAVED):u.reg_write(reg,0x12340000+i)
    u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,0x20000101);u.emu_start(case['entry']|1,0x20000100,count=250)
    assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==SP and [u.reg_read(x) for x in SAVED]==[0x12340000+i for i in range(8)],case
    assert [e[0] for e in s['events']]==expected_names and u.reg_read(UC_ARM_REG_R0)==(case['result'] if pub else value&255) and u.reg_read(UC_ARM_REG_R3)==(0xaabbccdd if pub and case['mutation'] else value),(case,s['events'])
    outputs.append([s['events'],[u.reg_read(x) for x in REGS],bytes(u.mem_read(SP-64,128)).hex()])
   assert outputs[0]==outputs[1],case
   counts['service' if service else 'helper']+=1;digest.update(json.dumps([case,outputs[0]],sort_keys=True).encode())
 v=dict(application_sha256=c['application_sha256'],comparisons=len(cases),counts=counts,trace_sha256=digest.hexdigest(),exact_spans=proof,exact_bytes=164,object_sha256=sha(obj),report_sha256=sha(OUT/'report.json'),driver_sha256=sha(Path(__file__)),actual_nested_publish_helper_executes=True,independent_logging_byte_guard_and_stack_mutation_oracle=True,mode_log_and_publish_providers_are_fixtures=True,full_raw_abi_or_private_histories_verified=False,whole_image_complete=False,hardware_write_executed=False);(OUT/'verification.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v))
if __name__=='__main__':main()
