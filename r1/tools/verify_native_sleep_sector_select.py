#!/usr/bin/env python3
"""Independent header qualification/oldest timestamp oracle with actual count."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-sleep-sector-select';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();SP=0x2003d000;CTX=0x200067b4;REGION=0x20013000;REGION2=REGION+64;OPS=0x20014000;OPS2=OPS+64;READ=0x20001000;READ2=READ+16;ERASE=READ+32;ERASE2=READ+48;REGS=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3];SAVED=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11];states={};MAGIC=0xccffaabb;VALID=0x66889977
PROVIDERS={0x914ec:'r1_structured_log_mode_get',0x91638:'r1_structured_log_format',0x799c0:'nrf_log_frontend_std_0',0x799c8:'nrf_log_frontend_std_1'}
def signed(i):return (i-256 if i&128 else i)&0xffffffff
def data(case,i):
 if case['entry']=='select':
  candidate=[(0xffffffff,0,0),(MAGIC,VALID^1,0),(0x12345678,0xffffffff,0xffffffff),(MAGIC,VALID,1),(0x12345678,0,0)][case['pattern']];return struct.pack('<4I',*(candidate if i==case['target'] else (MAGIC,VALID,i)),0x98765432)
 timestamp=[0xffffffff,100+(i%3),(i*17+7)&0xffffffff,0 if i==case['target'] else 0xffffffff,255-i][case['pattern']];return struct.pack('<4I',MAGIC,VALID,timestamp,0x12345678)
def main():
 c=json.loads((OUT/'contracts.json').read_text());obj=OUT/'native_sleep_sector_select.o';app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();proof=[];digest=hashlib.sha256();counts=dict(select=0,fallback=0,reads=0,erases=0,printf=0,std=0)
 with tempfile.TemporaryDirectory() as temp:
  td=Path(temp);countobj=td/'count.o';parent=BASE/'native-sleep-record/native_sleep_record.o';subprocess.run(['arm-none-eabi-ld','-r','--gc-sections','-u','r1_sleep_sector_count',str(parent),'-o',str(countobj)],check=True);ld=td/'proof.ld';bodies=c['bodies']+[dict(address='0x8fe14',symbol='r1_sleep_sector_count',source_span_bytes=20)];ld.write_text('SECTIONS {'+''.join(' .b%d %s : { *(.text.%s) }'%(i,x['address'],x['symbol']) for i,x in enumerate(bodies))+' /DISCARD/ : { *(.ARM.exidx*) } }\n'+''.join('%s = 0x%x;\n'%(n,a+1) for a,n in PROVIDERS.items())+'__start_log_const_data = 0xc441c;\nr1_sleep_sync_context_prefix = 0x200067b4;\n');elf=td/'proof.elf';subprocess.run(['arm-none-eabi-ld','-T',str(ld),str(obj),str(countobj),'-o',str(elf)],check=True,stderr=subprocess.PIPE);replacements=[]
  for i,x in enumerate(bodies):
   a=int(x['address'],16);f=td/(str(i)+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j','.b'+str(i),'-O','binary',str(elf),str(f)],check=True);d=f.read_bytes();assert len(d)==x['source_span_bytes'] and d==raw[a-0x27000:a-0x27000+len(d)];replacements.append((a,d));proof.append(dict(address=hex(a),size=len(d),sha256=hashlib.sha256(d).hexdigest()))
  def hook(u,a,size,_):
   if a not in [*PROVIDERS,READ,READ2,ERASE,ERASE2]:return
   s=states[id(u)];case=s['case'];r=[u.reg_read(x) for x in REGS];sp=u.reg_read(UC_ARM_REG_SP);s['trace'].append([a,r,bytes(u.mem_read(sp,16)).hex()]);ret=0x98765432
   if a==0x914ec:ret=case['mode']
   elif a in [READ,READ2]:
    i=s['reads'];s['reads']+=1;counts['reads']+=1;assert r[:3]==[((0x200000 if case['mutate'] and i else 0x100000)+i*4096)&0xffffffff,SP-40,16]
    if case['prefix']:u.mem_write(r[1],data(case,i)[:case['prefix']])
    if case['mutate']:u.mem_write(CTX+4,struct.pack('<2I',REGION2,OPS2))
    ret=case['read_result']
   elif a in [ERASE,ERASE2]:
    counts['erases']+=1;s['erases'].append([a,r[:2]])
    if case['mutate']:
     region=int.from_bytes(u.mem_read(CTX+4,4),'little');u.mem_write(region+52,struct.pack('<I',0x300000))
   elif a==0x91638:counts['printf']+=1;s['logs'].append([a,r[0],r[1],r[3] if r[0]==0xc400000 else None]);assert r[1]==r[2]
   else:counts['std']+=1;s['logs'].append([a,r[0],r[1],r[2] if a==0x799c8 else None])
   for reg,val in zip(REGS,[ret,0xa1a1a1a1,0xb2b2b2b2,0xc3c3c3c3]):u.reg_write(reg,val)
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  machines=[]
  for side in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x100000);u.mem_write(0x27000,raw);u.mem_map(0x20000000,0x40000)
   if side:
    for a,d in replacements:u.mem_write(a,d)
   u.hook_add(UC_HOOK_CODE,hook);machines.append(u)
  cases=[dict(entry=e,count=count,target=t,pattern=p,prefix=prefix,mutate=mut,mode=mode,read_result=rr,after=count//2) for e,count,t,p,prefix,mut,mode,rr in itertools.product(['select','fallback'],[0,1,2,3,127,128,129,254,255],[-1,0,1,127,128,253,254],range(5),[0,4,8,12,16],range(2),[0,7],[0,0xffffffff])]
  cases += [dict(entry=e,count=count,target=count-1,pattern=0 if e=='select' else 3,prefix=16,mutate=0,mode=7,read_result=0,after=count) for e,count in itertools.product(['select','fallback'],range(256))]
  for case in cases:
   header=bytearray(16);seq=[];logs=[];erases=[];chosen=-1;minimum=0xffffffff;reads=0
   for i in range(case['count']):
    seq.append(READ2 if case['mutate'] and i else READ);reads+=1;header[:case['prefix']]=data(case,i)[:case['prefix']];h0,h1,h2,_=struct.unpack('<4I',header)
    if case['entry']=='select':
     if h0==0xffffffff or (h1==0xffffffff and h2==0xffffffff) or (h0==MAGIC and h1!=VALID):chosen=i;break
    elif h2<minimum:chosen=i;minimum=h2
   if case['entry']=='select':result=signed(chosen) if chosen>=0 else 0xffffffff
   else:
    chosen=0 if chosen<0 else chosen;livecount=case['after'] if case['mutate'] and reads else case['count']
    if livecount<=chosen:
     seq+=[0x914ec]
     if not case['mode']&1:seq+=[0x914ec]
     if case['mode']&5:seq+=[0x91638];logs.append([0x91638,0x4000000,0x8fd70,None])
     seq+=[0x914ec]
     if case['mode']&2:seq+=[0x799c0];logs.append([0x799c0,0x1c0001,0x8fda0,None])
     chosen=0
    a=ERASE2 if case['mutate'] and reads else ERASE;seq.append(a);erases.append([a,[(0x200000 if case['mutate'] and reads else 0x100000)+chosen*4096,4096]])
    seq+=[0x914ec]
    if not case['mode']&1:seq+=[0x914ec]
    base=0x300000 if case['mutate'] else 0x100000
    if case['mode']&5:seq+=[0x91638];logs.append([0x91638,0xc400000,0x8fdc8,base+chosen*4096])
    seq+=[0x914ec]
    if case['mode']&2:seq+=[0x799c8];logs.append([0x799c8,0x1c0003,0x8fdf0,base+chosen*4096])
    result=signed(chosen)
   outputs=[]
   for u in machines:
    u.mem_write(CTX,struct.pack('<3I',0,REGION,OPS));u.mem_write(REGION,bytes(128));u.mem_write(REGION+52,struct.pack('<2I',0x100000,case['count']<<12));u.mem_write(REGION2+52,struct.pack('<2I',0x200000,case['after']<<12));u.mem_write(OPS,bytes(128));u.mem_write(OPS+40,struct.pack('<3I',READ+1,0,ERASE+1));u.mem_write(OPS2+40,struct.pack('<3I',READ2+1,0,ERASE2+1));u.mem_write(SP-128,b'\x96'*256)
    for reg,val in zip(REGS,[0x12345678,0x11223344,0x55667788,0x99aabbcc]):u.reg_write(reg,val)
    for i,reg in enumerate(SAVED):u.reg_write(reg,0x12340000+i)
    u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,0x20000101);s=dict(case=case,reads=0,trace=[],logs=[],erases=[]);states[id(u)]=s;u.emu_start(0x8fe29 if case['entry']=='select' else 0x8fc6d,0x20000100,count=30000)
    assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==SP and u.reg_read(UC_ARM_REG_R0)==result and [u.reg_read(x) for x in SAVED]==[0x12340000+i for i in range(8)],case
    assert [x[0] for x in s['trace']]==seq and s['reads']==reads and s['logs']==logs and s['erases']==erases and bytes(u.mem_read(SP-40,16))==header,case
    outputs.append([[u.reg_read(x) for x in REGS],s['trace'],s['logs'],s['erases'],bytes(u.mem_read(CTX,12)).hex(),bytes(u.mem_read(SP-128,256)).hex()])
   assert outputs[0]==outputs[1];counts[case['entry']]+=1;digest.update(json.dumps([case,outputs[0]],sort_keys=True).encode())
 v=dict(comparisons=counts['select']+counts['fallback'],counts=counts,trace_sha256=digest.hexdigest(),exact_spans=proof,exact_new_bytes=536,exact_joint_bytes=556,object_sha256=sha(obj),count_parent_object_sha256=sha(parent),application_sha256=sha(app),report_sha256=sha(OUT/'report.json'),driver_sha256=sha(Path(__file__)),independent_qualification_minimum_partial_read_and_log_oracle=True,actual_sector_count_executes=True,read_erase_mode_and_log_providers_are_fixtures=True,new_ram_state_bytes=0,full_raw_abi_or_private_histories_verified=False,whole_image_complete=False,hardware_write_executed=False);(OUT/'verification.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v))
if __name__=='__main__':main()
