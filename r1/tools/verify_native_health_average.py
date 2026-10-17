#!/usr/bin/env python3
"""Native averaging/hour helpers with rational IEEE binary32 and state oracles."""
import hashlib,itertools,json,struct,subprocess,tempfile
from fractions import Fraction
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-health-average';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();SP=0x2003d000;ROWS=0x20016648
REGS=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3];SAVED=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
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
 c=json.loads((OUT/'contracts.json').read_text());obj=OUT/'native_health_average.o';shared=OUT/'stress-prefix.o';app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';image=app.read_bytes();assert sha(app)==c['application_sha256']=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';states={};digest=hashlib.sha256();counts={'average':0,'hour':0};proof=[]
 with tempfile.TemporaryDirectory() as td:
  td=Path(td);ld=td/'layout.ld';ld.write_text('SECTIONS { .average 0x5aba0 : { *(.text.r1_health_storage_average) } .hour 0x5aca6 : { *(.text.r1_health_storage_hour_index) } .rows 0x20016648 : { *(.r1.health.average.rows0_4) } .stress 0x20016670 : { *(.r1.health.storage.stress) } /DISCARD/ : { *(.ARM.exidx*) } }\n'+''.join('%s = 0x%x;\n'%(n,int(a,16)|1) for a,n in c['providers'].items() if int(a,16)!=0x5aca6));elf=td/'proof.elf';subprocess.run(['arm-none-eabi-ld','-T',str(ld),str(obj),str(shared),'-o',str(elf)],check=True,stderr=subprocess.PIPE);replacements=[]
  for sec,a,length in [('average',0x5aba0,212),('hour',0x5aca6,30)]:
   p=td/(sec+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j','.'+sec,'-O','binary',str(elf),str(p)],check=True);d=p.read_bytes();assert len(d)==length and d==image[a-0x27000:a-0x27000+length];replacements.append((a,d));proof.append(dict(section=sec,address=hex(a),size=length,sha256=sha(p)))
  syms={x[2]:int(x[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x:=line.split())==3};assert syms['r1_health_average_rows']==ROWS and syms['r1_health_storage_stress_prefix']==ROWS+40
  def hook(u,a,size,_):
   s=states[id(u)];case=s['case'];r=[u.reg_read(x) for x in REGS]
   if a==0x8adb4:s['trace'].append(['offset',r]);u.reg_write(UC_ARM_REG_R0,case['offset'])
   elif a==0x8af40:
    assert r[:2]==[case['timestamp'],case['offset']];s['trace'].append(['calendar',r]);data=struct.pack('<H6B',2026,10,16,case['hour'],59,58,5);u.mem_write(r[2],data[:case['written']]);u.reg_write(UC_ARM_REG_R0,case['calendar_result'])
   elif a==0x914ec:
    v=case['modes'][s['mode']%len(case['modes'])];s['mode']+=1;s['trace'].append(['mode',v]);u.reg_write(UC_ARM_REG_R0,v);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR));return
   elif a in [0x91638,0x799c8]:s['trace'].append(['log',hex(a),r]);u.reg_write(UC_ARM_REG_R0,0x87654321)
   else:return
   for reg,value in zip(REGS[1:],[0xa1a1a1a1,0xb2b2b2b2,0xc3c3c3c3]):u.reg_write(reg,value)
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  machines=[]
  for side in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x100000);u.mem_write(0x27000,image);u.mem_map(0x20000000,0x40000)
   if side:
    for a,d in replacements:u.mem_write(a,d)
   u.reg_write(UC_ARM_REG_C1_C0_2,0xf00000);u.reg_write(UC_ARM_REG_FPEXC,0x40000000);u.hook_add(UC_HOOK_CODE,hook);machines.append(u)
  default=dict(kind='average',type=0,value=1,timestamp=0x80000001,offset=0xffffffff,hour=23,written=8,calendar_result=1,old_hour=23,count=1,sum=1,rounding=0,modes=[0])
  cases=[dict(default,type=type_,value=value,count=count,sum=sum_,old_hour=old_hour,hour=hour,rounding=rounding) for type_,value,count,sum_,old_hour,hour,rounding in itertools.product(range(6),[0,1,255,65535,0xffffffff],[0,1,2,65534,65535],[0,1,0xffffff,0x1000001,0x7fffffff,0xffffffff],[0,23],[0,23],range(4))]
  cases += [dict(default,type=t,modes=m) for t,m in itertools.product([6,7,255,0x7fffffff,0xffffffff],[[0],[7],[0,4,2]])]
  cases += [dict(default,kind='hour',hour=h,written=w,offset=o,calendar_result=r) for h,w,o,r in itertools.product(range(256),range(9),[0,1,0xffffffff],[0,1,0xffffffff])]
  for case in cases:
   initial=bytearray(b'\x96'*80);expected=bytearray(initial);effective_hour=case['hour'] if case['written']>=5 else 0;expected_r0=effective_hour
   if case['kind']=='average' and case['type']<=5:
    a=case['type']*8;initial[a:a+8]=struct.pack('<BBHI',case['old_hour'],0x73,case['count'],case['sum']);expected=bytearray(initial)
    if not case['count'] or case['old_hour']!=effective_hour:expected[a:a+8]=bytes([effective_hour])+bytes(7)
    count=(int.from_bytes(expected[a+2:a+4],'little')+1)&65535;sum_=(int.from_bytes(expected[a+4:a+8],'little')+case['value'])&0xffffffff;struct.pack_into('<H',expected,a+2,count);struct.pack_into('<I',expected,a+4,sum_);expected_r0=average(sum_,count,case['rounding'])
   elif case['kind']=='average':expected_r0=0
   results=[]
   for u in machines:
    u.mem_write(ROWS-16,b'\x69'*112);u.mem_write(ROWS,bytes(initial));u.mem_write(SP-128,b'\x96'*256)
    args=[case['timestamp'],0x11111111,0x22222222,0x33333333] if case['kind']=='hour' else [case['type'],case['value'],case['timestamp'],0x33333333]
    for reg,value in zip(REGS,args):u.reg_write(reg,value)
    for i,reg in enumerate(SAVED):u.reg_write(reg,0x12340000+i)
    for reg,value in zip([UC_ARM_REG_S0,UC_ARM_REG_S1,UC_ARM_REG_S2],[0x12345678,0x23456789,0x3456789a]):u.reg_write(reg,value)
    u.reg_write(UC_ARM_REG_FPSCR,case['rounding']<<22);u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,0x20000101);s=dict(case=case,trace=[],mode=0);states[id(u)]=s;u.emu_start(0x5aca7 if case['kind']=='hour' else 0x5aba1,0x20000100,count=10000)
    assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==SP and [u.reg_read(reg) for reg in SAVED]==[0x12340000+i for i in range(8)] and u.reg_read(UC_ARM_REG_R0)==expected_r0 and bytes(u.mem_read(ROWS,80))==expected,(case,u.reg_read(UC_ARM_REG_R0),expected_r0)
    results.append([[u.reg_read(reg) for reg in REGS],s['trace'],[u.reg_read(reg) for reg in [UC_ARM_REG_S0,UC_ARM_REG_S1,UC_ARM_REG_S2,UC_ARM_REG_FPSCR]],bytes(u.mem_read(ROWS-16,112)).hex(),bytes(u.mem_read(SP-128,256)).hex()])
   assert results[0]==results[1],case;counts[case['kind']]+=1;digest.update(json.dumps([case,results[0]],sort_keys=True).encode())
 receipt=dict(comparisons=sum(counts.values()),counts=counts,trace_sha256=digest.hexdigest(),exact_spans=proof,exact_bytes=sum(x['size'] for x in proof),object_sha256=sha(obj),reused_stress_prefix_object_sha256=sha(shared),driver_sha256=sha(Path(__file__)),report_sha256=sha(OUT/'report.json'),application_sha256=sha(app),rational_binary32_all_four_rounding_modes_and_count_sum_wrap_oracle=True,actual_average_and_hour_execute=True,offset_calendar_and_log_are_fixtures=True,all_calendar_hour_bytes_and_partial_outputs_checked=True,row5_alias_uses_existing_stress_prefix_section=True,full_private_history_or_raw_abi_verified=False,whole_image_complete=False,hardware_write_executed=False)
 (OUT/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
