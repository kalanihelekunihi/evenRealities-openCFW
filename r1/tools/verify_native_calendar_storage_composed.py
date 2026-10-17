#!/usr/bin/env python3
"""Actual five storage bodies -> average/hour with shared stress/row5 state."""
import hashlib,itertools,json,struct,subprocess,tempfile
from fractions import Fraction
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-calendar-frames';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();SP=0x2003d000;DATA=0x20010000;ARENA=0x20016400;SIZE=0xc00;ROWS=0x20016648
REGS=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3];SAVED=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11];KINDS={'hr':0,'spo2':1,'temperature':2,'stress':3,'hrv':5}
def f32(x,mode):
 if not x:return Fraction(0)
 n,d=x.numerator,x.denominator;e=n.bit_length()-d.bit_length();power=Fraction(2**e) if e>=0 else Fraction(1,2**-e)
 if x<power:e-=1
 scale=23-e;num=n<<scale if scale>=0 else n;den=d if scale>=0 else d<<-scale;q,r=divmod(num,den)
 if (mode==0 and (r*2>den or r*2==den and q%2)) or mode==1 and r:q+=1
 return Fraction(q,2**scale) if scale>=0 else Fraction(q*2**-scale)
def average(sum_,count,mode):
 if count==0:return 0 if sum_==0 else 65535
 quotient=f32(f32(Fraction(sum_),mode)/f32(Fraction(count),mode),mode);return min(0xffffffff,quotient.numerator//quotient.denominator)&65535

def main():
 cc=json.loads((OUT/'contracts.json').read_text());c=json.loads((BASE/'native-health-average/contracts.json').read_text());sc=json.loads((BASE/'native-health-sample-storage/contracts.json').read_text());bodies={x['family']:x for x in sc['bodies']};obj=OUT/'native_calendar_frames.o';config=OUT/'shared-calendar-config.o';averageobj=BASE/'native-health-average/native_health_average.o';storage=BASE/'native-health-sample-storage/native_health_sample_storage.o';app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';image=app.read_bytes();assert sha(app)==c['application_sha256']=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';digest=hashlib.sha256();states={};counts={'single_storage_calls':0,'alias_sequence_calls':0};proof=[]
 spans=[(x['symbol'],int(x['address'],16),x['source_span_bytes'],'.text.'+x['symbol']) for x in cc['bodies']+c['bodies']+sc['bodies']]+[('months',0x99c5c,24,'.rodata.month_days_forward')]+[('stress_text',0xbf8e8,65,'.r1.health.storage.stress_text')]
 with tempfile.TemporaryDirectory() as td:
  td=Path(td);ld=td/'layout.ld';providers=dict(sc['providers']);providers.update(c['providers']);ld.write_text('SECTIONS {'+''.join(' .s%d 0x%x : { *(%s) }'%(i,a,sec) for i,(n,a,l,sec) in enumerate(spans))+''.join(' .cache_%s 0x%x : { *(.r1.health.storage.%s) }'%(x['family'],int(x['cache_address'],16),x['family']) for x in sc['bodies'])+' .time_state 0x20016ac4 : { *(.r1.time.state) } .fallback 0x20016ae4 (NOLOAD) : { *(.bss.unix_to_broken_down_fallback) } .rows 0x20016648 : { *(.r1.health.average.rows0_4) } /DISCARD/ : { *(.ARM.exidx*) } }\n'+''.join('%s = 0x%x;\n'%(n,int(a,16)|1) for a,n in providers.items() if int(a,16) not in [0x5aba0,0x5aca6,0x8adb4,0x8af40]));elf=td/'proof.elf';subprocess.run(['arm-none-eabi-ld','-T',str(ld),str(obj),str(config),str(averageobj),str(storage),'-o',str(elf)],check=True,stderr=subprocess.PIPE);replacements=[]
  for i,(n,a,l,sec) in enumerate(spans):
   p=td/(str(i)+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j','.s'+str(i),'-O','binary',str(elf),str(p)],check=True);d=p.read_bytes();assert len(d)==l and d==image[a-0x27000:a-0x27000+l];replacements.append((a,d));proof.append(dict(symbol=n,address=hex(a),size=l,sha256=sha(p)))
  def mutate(u,p,width,value,time):
   v=int.from_bytes(u.mem_read(p,width),'little');t=int.from_bytes(u.mem_read(p+width,4),'little');u.mem_write(p,((v+value)&((1<<(width*8))-1)).to_bytes(width,'little'));u.mem_write(p+width,struct.pack('<I',(t+time)&0xffffffff))
  def hook(u,a,size,_):
   s=states[id(u)];case=s['case'];r=[u.reg_read(x) for x in REGS]
   if a in [0x5aba0,0x5aca6]:s['trace'].append(['actual-helper',hex(a),r]);return
   if a==0x8adb4:
    i=s['getters'];assert i<2;s['getters']+=1;u.mem_write(0x20016acc,struct.pack('<H',case['offsets'][i]&65535));s['trace'].append(['actual-offset',r,i]);return
   elif a==0x8af40:
    i=s['calendars'];assert i<2;s['calendars']+=1;s['trace'].append(['actual-calendar',r])
    if case['mutation']&(1<<i):mutate(u,s['packet'],s['width'],17 if i==0 else 29,31 if i==0 else 61)
    return
   elif a==0x5a7bc:s['trace'].append(['actual-unix',r]);return
   elif a==0x914ec:
    value=case['modes'][s['mode']%len(case['modes'])];s['mode']+=1;s['trace'].append(['mode',value]);u.reg_write(UC_ARM_REG_R0,value);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR));return
   elif a in [0x91638,0x799d6,0x799f8,0x799c8]:s['trace'].append(['log',hex(a),r,bytes(u.mem_read(u.reg_read(UC_ARM_REG_SP),12)).hex()]);u.reg_write(UC_ARM_REG_R0,0x87654321)
   else:return
   for reg,value in zip(REGS[1:],[0xa1a1a1a1,0xb2b2b2b2,0xc3c3c3c3]):u.reg_write(reg,value)
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  machines=[]
  for side in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x100000);u.mem_write(0x27000,image);u.mem_map(0x20000000,0x40000)
   if side:
    for a,d in replacements:u.mem_write(a,d)
   u.reg_write(UC_ARM_REG_C1_C0_2,0xf00000);u.reg_write(UC_ARM_REG_FPEXC,0x40000000);u.hook_add(UC_HOOK_CODE,hook);machines.append(u)
  default=dict(sequence=['hr'],value=0,offsets=(0,0),timestamp=0,mutation=0,packet_kind=0,rounding=0,count=1,sum=1,modes=[0])
  cases=[dict(default,sequence=[fam],value=value,offsets=hours,mutation=mutation,packet_kind=packet_kind,rounding=rounding,count=[0,1,65535][value%3],sum=[0,0x1000001,0xffffffff][value%3],modes=[0,4,2,1] if mutation else [0]) for fam,value,hours,mutation,packet_kind,rounding in itertools.product(bodies,[0,1,255,65535],[(0,0),(60,60),(0,60),(-60,0),(32767,-32768)],range(4),range(3),range(4))]
  cases += [dict(default,sequence=['hrv','stress','hrv'],value=value,offsets=hours,count=count,sum=sum_,rounding=rounding) for value,hours,count,sum_,rounding in itertools.product([0,1,255,65535],[(0,0),(60,60),(0,60),(-60,0)],[0,1,65535],[0,0xffffffff],range(4))]
  for case_index,case in enumerate(cases):
   case['timestamp']=[0,0x7fffffff,0xffffffff,951782400][case_index%4]
   expected=bytearray(b'\x96'*SIZE)
   for row in range(6):struct.pack_into('<BBHI',expected,ROWS-ARENA+row*8,23,0x73,case['count'],case['sum'])
   expected[0x20016ac4-ARENA:0x20016ae4-ARENA]=bytes(32);expected[0x20016ae4-ARENA:0x20016b08-ARENA]=bytes(36)
   for u in machines:u.mem_write(ARENA,bytes(expected))
   for step,family in enumerate(case['sequence']):
    body=bodies[family];width=2 if family=='hrv' else 1;mask=(1<<(width*8))-1;cache=int(body['cache_address'],16);outer_hour=(((case['timestamp']+step+case['offsets'][0]*60)&0xffffffff)//3600)%24;slot=cache+outer_hour*width*3;packet=[DATA,cache+(147 if width==2 else 75),slot][case['packet_kind']];packet_bytes=((case['value']+step)&mask).to_bytes(width,'little')+struct.pack('<I',(case['timestamp']+step)&0xffffffff);packet_expected=bytearray(packet_bytes+b'\x96'*10)
    if ARENA<=packet<ARENA+SIZE:expected[packet-ARENA:packet-ARENA+len(packet_bytes)]=packet_bytes
    struct.pack_into('<H',expected,0x20016acc-ARENA,case['offsets'][0]&65535);initial=bytes(expected)
    def read(a,n):return bytes(expected[a-ARENA:a-ARENA+n]) if ARENA<=a<ARENA+SIZE else bytes(packet_expected[a-DATA:a-DATA+n])
    def write(a,d):
     if ARENA<=a<ARENA+SIZE:expected[a-ARENA:a-ARENA+len(d)]=d
     else:packet_expected[a-DATA:a-DATA+len(d)]=d
    def model_mutation(value,time):write(packet,((int.from_bytes(read(packet,width),'little')+value)&mask).to_bytes(width,'little'));write(packet+width,struct.pack('<I',(int.from_bytes(read(packet+width,4),'little')+time)&0xffffffff))
    if case['mutation']&1:model_mutation(17,31)
    saved_value=int.from_bytes(read(packet,width),'little');inner_timestamp=int.from_bytes(read(packet+width,4),'little')
    if case['mutation']&2:model_mutation(29,61)
    row=ROWS+KINDS[family]*8;hour=(((inner_timestamp+case['offsets'][1]*60)&0xffffffff)//3600)%24;count=int.from_bytes(read(row+2,2),'little')
    if count==0 or read(row,1)[0]!=hour:write(row,bytes([hour])+bytes(7));count=0
    count=(count+1)&65535;sum_=(int.from_bytes(read(row+4,4),'little')+saved_value)&0xffffffff;write(row+2,struct.pack('<H',count));write(row+4,struct.pack('<I',sum_));avg=average(sum_,count,case['rounding'])
    value=int.from_bytes(read(packet,width),'little');maximum=int.from_bytes(read(slot+width,width),'little')
    if value>maximum:write(slot+width,value.to_bytes(width,'little'))
    value=int.from_bytes(read(packet,width),'little');minimum=int.from_bytes(read(slot+width*2,width),'little')
    if value<minimum or minimum==0:write(slot+width*2,value.to_bytes(width,'little'))
    write(slot,(avg&mask).to_bytes(width,'little'));last=cache+(147 if width==2 else 75);write(last,read(packet,4));write(last+4,read(packet+4,width))
    struct.pack_into('<H',expected,0x20016acc-ARENA,case['offsets'][1]&65535)
    results=[]
    for u in machines:
     # Carry prior state across the alias sequence; only new input bytes change.
     if ARENA<=packet<ARENA+SIZE:u.mem_write(packet,packet_bytes)
     u.mem_write(0x20016acc,struct.pack('<H',case['offsets'][0]&65535));u.mem_write(DATA,packet_bytes+b'\x96'*10);u.mem_write(SP-256,b'\x96'*512)
     for reg,value in zip(REGS,[packet,0x11111111,0x22222222,0x33333333]):u.reg_write(reg,value)
     for i,reg in enumerate(SAVED):u.reg_write(reg,0x12340000+i)
     u.reg_write(UC_ARM_REG_FPSCR,case['rounding']<<22);u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,0x20000101);s=dict(case=case,packet=packet,width=width,mode=0,calendars=0,getters=0,trace=[]);states[id(u)]=s;u.emu_start(int(body['address'],16)|1,0x20000100,count=10000)
     assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==SP and [u.reg_read(reg) for reg in SAVED]==[0x12340000+i for i in range(8)] and s['calendars']==2 and s['getters']==2
     assert bytes(u.mem_read(ARENA,SIZE))==expected and bytes(u.mem_read(DATA,len(packet_expected)))==packet_expected,(case,step,family)
     results.append([[u.reg_read(reg) for reg in REGS],s['trace'],[u.reg_read(reg) for reg in [UC_ARM_REG_S0,UC_ARM_REG_S1,UC_ARM_REG_S2,UC_ARM_REG_FPSCR]],bytes(u.mem_read(ARENA,SIZE)).hex(),bytes(u.mem_read(DATA,16)).hex(),bytes(u.mem_read(SP-256,512)).hex()])
    assert results[0]==results[1],(case,step);counts['alias_sequence_calls' if len(case['sequence'])>1 else 'single_storage_calls']+=1;digest.update(json.dumps([case,step,family,results[0]],sort_keys=True).encode())
 receipt=dict(comparisons=sum(counts.values()),counts=counts,sequences=len(cases),trace_sha256=digest.hexdigest(),exact_spans=proof,exact_bytes=sum(x['size'] for x in proof),object_sha256=sha(obj),shared_config_object_sha256=sha(config),average_object_sha256=sha(averageobj),storage_object_sha256=sha(storage),driver_sha256=sha(Path(__file__)),report_sha256=sha(OUT/'report.json'),application_sha256=sha(app),actual_storage_average_hour_offset_calendar_unix_source_chain_executes=True,hrv_stress_hrv_shared_row5_sequences_execute=True,independent_coupled_cache_fp_alias_and_mutation_oracle=True,calendar_provider_is_fixture=False,timezone_packet_changes_and_logging_are_controlled_fixtures=True,full_private_history_or_raw_abi_verified=False,whole_image_complete=False,hardware_write_executed=False)
 (OUT/'storage-composed-verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
