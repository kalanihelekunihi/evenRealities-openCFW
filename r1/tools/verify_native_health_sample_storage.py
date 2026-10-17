#!/usr/bin/env python3
"""Native sample aggregators: byte/halfword values, fresh packet reads and bounded cache gates."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-health-sample-storage';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();SP=0x2003d000;DATA=0x20010000;ARENA=0x20016400;SIZE=0xc00
REGS=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3];SAVED=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11];KINDS={'hr':0,'spo2':1,'temperature':2,'stress':3,'hrv':5}
def main():
 c=json.loads((OUT/'contracts.json').read_text());obj=OUT/'native_health_sample_storage.o';app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';image=app.read_bytes();assert sha(app)==c['application_sha256']=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';digest=hashlib.sha256();counts={x['family']:0 for x in c['bodies']};obs={'hour':0,'average':0,'mode':0,'logs':0};states={};proof=[]
 with tempfile.TemporaryDirectory() as td:
  td=Path(td);spans=[(x['symbol'],int(x['address'],16),x['source_span_bytes'],'.text.'+x['symbol']) for x in c['bodies']]+[('stress_text',0xbf8e8,65,'.r1.health.storage.stress_text')];ld=td/'layout.ld';ld.write_text('SECTIONS {'+''.join(' .s%d 0x%x : { *(%s) }'%(i,a,section) for i,(n,a,l,section) in enumerate(spans))+''.join(' .cache_%s 0x%x : { *(.r1.health.storage.%s) }'%(x['family'],int(x['cache_address'],16),x['family']) for x in c['bodies'])+' /DISCARD/ : { *(.ARM.exidx*) } }\n'+''.join('%s = 0x%x;\n'%(n,int(a,16)|1) for a,n in c['providers'].items()));elf=td/'proof.elf';subprocess.run(['arm-none-eabi-ld','-T',str(ld),str(obj),'-o',str(elf)],check=True,stderr=subprocess.PIPE);replacements=[]
  for i,(name,a,length,section) in enumerate(spans):
   p=td/(str(i)+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j','.s'+str(i),'-O','binary',str(elf),str(p)],check=True);d=p.read_bytes();native=image[a-0x27000:a-0x27000+length];assert len(d)==length and d==native,(name,len(d),length,[(j,x,y) for j,(x,y) in enumerate(zip(d,native)) if x!=y][:10]);replacements.append((a,d));proof.append(dict(symbol=name,address=hex(a),size=length,sha256=sha(p)))
  def mutate(u,p,width,addtime,addvalue):
   if not p:return
   v=int.from_bytes(u.mem_read(p,width),'little');t=int.from_bytes(u.mem_read(p+width,4),'little');u.mem_write(p,((v+addvalue)&((1<<(width*8))-1)).to_bytes(width,'little'));u.mem_write(p+width,struct.pack('<I',(t+addtime)&0xffffffff))
  def hook(u,a,size,_):
   s=states[id(u)];case=s['case'];r=[u.reg_read(x) for x in REGS];width=s['width'];p=case['packet']
   if a==0x5aca6:
    assert r[0]==int.from_bytes(u.mem_read(p+width,4),'little');s['trace'].append(['hour',r]);obs['hour']+=1
    if case['mutation']&1:mutate(u,p,width,31,17)
    u.reg_write(UC_ARM_REG_R0,case['hour'])
   elif a==0x5aba0:
    assert r[:3]==[KINDS[s['family']],int.from_bytes(u.mem_read(p,width),'little'),int.from_bytes(u.mem_read(p+width,4),'little')];s['trace'].append(['average',r]);obs['average']+=1
    if case['mutation']&2:mutate(u,p,width,61,29)
    u.reg_write(UC_ARM_REG_R0,case['average'])
   elif a==0x914ec:
    value=case['modes'][s['modes']%len(case['modes'])];s['modes']+=1;obs['mode']+=1;s['trace'].append(['mode',value]);u.reg_write(UC_ARM_REG_R0,value);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR));return
   elif a in [0x91638,0x799d6,0x799f8]:
    s['trace'].append(['log',hex(a),r,bytes(u.mem_read(u.reg_read(UC_ARM_REG_SP),12)).hex()]);obs['logs']+=1;u.reg_write(UC_ARM_REG_R0,0x87654321)
   else:return
   for reg,value in zip(REGS[1:],[0xa1a1a1a1,0xb2b2b2b2,0xc3c3c3c3]):u.reg_write(reg,value)
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  machines=[]
  for side in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x100000);u.mem_write(0x27000,image);u.mem_map(0x20000000,0x40000)
   if side:
    for a,d in replacements:u.mem_write(a,d)
   u.hook_add(UC_HOOK_CODE,hook);machines.append(u)
  default=dict(value=70,time=0x80000001,hour=0,average=0x12345678,minimum=0,maximum=0,mutation=0,modes=[0],packet=DATA)
  cases=[]
  for body in c['bodies']:
   fam=body['family'];cache=int(body['cache_address'],16);width=2 if fam=='hrv' else 1
   for value in range(65536 if width==2 else 256):cases.append((body,dict(default,value=value,hour=value%24,minimum=(value//3)&((1<<(width*8))-1),maximum=(value//2)&((1<<(width*8))-1))))
   for value,hour,minimum,maximum,average,mutation,modes,packet_kind in itertools.product([0,1,127,255,256,65535],[0,23,24,25,255],[0,127],[0,127],[0,1,0xffffffff],range(4),[[0],[7],[0,4,2,1]],range(3)):
    cases.append((body,dict(default,value=value,hour=hour,minimum=minimum,maximum=maximum,average=average,mutation=mutation,modes=modes,packet=[DATA,cache+75 if width==1 else cache+147,cache+hour*3*width][packet_kind])))
   cases.append((body,dict(default,packet=0,modes=[7])))
  for body,case in cases:
   family=body['family'];width=2 if family=='hrv' else 1;mask=(1<<(width*8))-1;cache=int(body['cache_address'],16);slot=cache+case['hour']*width*3;p=case['packet'];initial=bytearray(b'\x96'*SIZE);initial[slot-ARENA:slot-ARENA+width*3]=((0x55&mask).to_bytes(width,'little')+(case['maximum']&mask).to_bytes(width,'little')+(case['minimum']&mask).to_bytes(width,'little'));packet=(case['value']&mask).to_bytes(width,'little')+struct.pack('<I',case['time']);packet_data=bytearray(packet+b'\x96'*10)
   if ARENA<=p<ARENA+SIZE:initial[p-ARENA:p-ARENA+len(packet)]=packet
   expected=bytearray(initial)
   def read(a,n):return bytes(expected[a-ARENA:a-ARENA+n]) if ARENA<=a<ARENA+SIZE else bytes(packet_data[a-DATA:a-DATA+n])
   def write(a,d):
    if ARENA<=a<ARENA+SIZE:expected[a-ARENA:a-ARENA+len(d)]=d
    else:packet_data[a-DATA:a-DATA+len(d)]=d
   if p:
    for bit,t,v in [(1,31,17),(2,61,29)]:
     if case['mutation']&bit:write(p,((int.from_bytes(read(p,width),'little')+v)&mask).to_bytes(width,'little'));write(p+width,struct.pack('<I',(int.from_bytes(read(p+width,4),'little')+t)&0xffffffff))
    value=int.from_bytes(read(p,width),'little');maximum=int.from_bytes(read(slot+width,width),'little')
    if value>maximum:write(slot+width,value.to_bytes(width,'little'))
    value=int.from_bytes(read(p,width),'little');minimum=int.from_bytes(read(slot+width*2,width),'little')
    if value<minimum or minimum==0:write(slot+width*2,value.to_bytes(width,'little'))
    write(slot,(case['average']&mask).to_bytes(width,'little'));last=cache+(147 if width==2 else 75);write(last,read(p,4));write(last+4,read(p+4,width))
   results=[]
   for u in machines:
    u.mem_write(ARENA,bytes(initial));u.mem_write(DATA,packet+b'\x96'*10);u.mem_write(SP-128,b'\x96'*256)
    for reg,value in zip(REGS,[p,0x11111111,0x22222222,0x33333333]):u.reg_write(reg,value)
    for i,reg in enumerate(SAVED):u.reg_write(reg,0x12340000+i)
    u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,0x20000101);s=dict(case=case,width=width,family=family,modes=0,trace=[]);states[id(u)]=s;u.emu_start(int(body['address'],16)|1,0x20000100,count=10000);assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==SP and [u.reg_read(reg) for reg in SAVED]==[0x12340000+i for i in range(8)]
    assert bytes(u.mem_read(ARENA,SIZE))==expected and bytes(u.mem_read(DATA,len(packet_data)))==packet_data,(family,case)
    results.append([[u.reg_read(reg) for reg in REGS],s['trace'],bytes(u.mem_read(ARENA,SIZE)).hex(),bytes(u.mem_read(DATA,16)).hex(),bytes(u.mem_read(SP-128,256)).hex()])
   assert results[0]==results[1],(family,case);counts[family]+=1;digest.update(json.dumps([family,case,results[0]],sort_keys=True).encode())
 receipt=dict(comparisons=sum(counts.values()),counts=counts,observations=obs,trace_sha256=digest.hexdigest(),exact_spans=proof,exact_bytes=sum(x['size'] for x in proof),object_sha256=sha(obj),driver_sha256=sha(Path(__file__)),report_sha256=sha(OUT/'report.json'),application_sha256=sha(app),all_65536_hrv_values_and_all_byte_values_checked=True,cache_last_packet_alias_and_provider_mutation_independent_oracle=True,all_five_storage_bodies_execute=True,hour_average_and_log_are_fixtures=True,cache_prefix_extent_is_not_full_context=True,full_private_history_or_raw_abi_verified=False,whole_image_complete=False,hardware_write_executed=False)
 (OUT/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
