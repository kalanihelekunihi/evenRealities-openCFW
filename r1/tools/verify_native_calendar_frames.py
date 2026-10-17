#!/usr/bin/env python3
"""Native calendar frames with datetime, sequential alias and int16 offset oracles."""
import datetime,hashlib,itertools,json,random,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_MEM_INVALID
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-calendar-frames';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();SP=0x2003d000;DATA=0x20010000;STATE=0x20016ac4;FALLBACK=0x20016ae4
REGS=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3];SAVED=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11];EPOCH=datetime.datetime(1970,1,1)
def date(t):return EPOCH+datetime.timedelta(seconds=t&0xffffffff)
def main():
 obj=OUT/'native_calendar_frames.o';config=OUT/'shared-calendar-config.o';app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';image=app.read_bytes();assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';states={};digest=hashlib.sha256();counts={'offset':0,'unix':0,'utc':0,'faults':0};proof=[]
 with tempfile.TemporaryDirectory() as td:
  td=Path(td);ld=td/'layout.ld';ld.write_text('SECTIONS { .offset 0x8adb4 : { *(.text.r1_time_utc_offset_get) } .utc 0x8af40 : { *(.text.time_calendar_utc_to_calendar) } .unix 0x5a7bc : { *(.text.time_calendar_unix_to_broken_down) } .months 0x99c5c : { *(.rodata.month_days_forward) } .state 0x20016ac4 : { *(.r1.time.state) } .fallback 0x20016ae4 (NOLOAD) : { *(.bss.unix_to_broken_down_fallback) } /DISCARD/ : { *(.ARM.exidx*) } }');elf=td/'proof.elf';subprocess.run(['arm-none-eabi-ld','-T',str(ld),str(obj),str(config),'-o',str(elf)],check=True,stderr=subprocess.PIPE);replacements=[]
  for sec,a,length in [('offset',0x8adb4,12),('utc',0x8af40,76),('unix',0x5a7bc,240),('months',0x99c5c,24)]:
   p=td/(sec+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j','.'+sec,'-O','binary',str(elf),str(p)],check=True);d=p.read_bytes();assert len(d)==length and d==image[a-0x27000:a-0x27000+length];replacements.append((a,d));proof.append(dict(section=sec,address=hex(a),size=length,sha256=sha(p)))
  syms={x[2]:int(x[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x:=line.split())==3};assert [syms[n] for n in ['r1_time_state','unix_to_broken_down_fallback','month_days_forward']]==[STATE,FALLBACK,0x99c5c]
  def invalid(u,access,address,size,value,_):states[id(u)]['fault']=[access,address,size,value];return False
  machines=[]
  for side in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x100000);u.mem_write(0x27000,image);u.mem_map(0x20000000,0x40000)
   if side:
    for a,d in replacements:u.mem_write(a,d)
   u.hook_add(UC_HOOK_MEM_INVALID,invalid);machines.append(u)
  rng=random.Random(0x5a7bc);timestamps=[0,1,59,60,3599,3600,86399,86400,0x7fffffff,0x80000000,0xffffffff]+[rng.getrandbits(32) for _ in range(1000)]
  for year in range(1970,2107):
   for month,day in [(1,1),(2,28),(3,1),(12,31)]:
    t=int((datetime.datetime(year,month,day)-EPOCH).total_seconds())
    if 0<=t<=0xffffffff:timestamps += [t,(t-1)&0xffffffff,(t+86399)&0xffffffff]
  default=dict(kind='offset',timestamp=0,offset=0,output=DATA+64,input=DATA)
  cases=[dict(default,offset=o) for o in range(65536)]
  cases += [dict(default,kind='unix',timestamp=t,output=o,input=i) for t,o,i in itertools.product(timestamps,[0,DATA+64],[DATA])]
  cases += [dict(default,kind='utc',timestamp=t,offset=o,output=DATA+64) for t,o in itertools.product(timestamps,[0,1,0xffffffff,32767,0xffff8000,0x7fffffff,0x80000000])]
  cases += [dict(default,kind='unix',timestamp=t,input=DATA+delta,output=DATA) for t,delta in itertools.product([0,86400,0x7fffffff,0x80000000,0xffffffff],range(0,36,4))]
  cases += [dict(default,kind=kind,output=o,input=i,timestamp=0xffffffff,offset=0xffffffff) for kind,o,i in itertools.product(['utc','unix'],[0,DATA+1,0x30000000],[DATA,0x30000000])]
  for case in cases:
   data=bytearray(b'\x96'*128);fallback=bytearray(b'\x69'*36)
   if DATA<=case['input']<DATA+128:struct.pack_into('<I',data,case['input']-DATA,case['timestamp'])
   expected=bytearray(data);expected_fallback=bytearray(fallback);expected_fault=False;expected_r0=None
   if case['kind']=='offset':expected_r0=case['offset']&65535;expected_r0=(expected_r0-65536 if expected_r0&32768 else expected_r0)&0xffffffff
   elif case['kind']=='utc':
    if case['output']==0:expected_r0=0
    elif case['output']==0x30000000:expected_fault=True
    else:
     d=date((case['timestamp']+case['offset']*60)&0xffffffff);struct.pack_into('<H6B',expected,case['output']-DATA,d.year,d.month,d.day,d.hour,d.minute,d.second,(d.weekday()+1)%7);expected_r0=1
   else:
    if case['input']==0x30000000 or case['output']==0x30000000:expected_fault=True
    else:
     output=case['output'] or FALLBACK;d=date(case['timestamp']);dest=expected if output!=FALLBACK else expected_fallback;off=output-DATA if output!=FALLBACK else 0
     for index,value in [(8,d.hour),(4,d.minute),(0,d.second),(20,d.year-1900),(28,d.timetuple().tm_yday-1),(12,d.day),(16,d.month-1)]:struct.pack_into('<I',dest,off+index,value)
     reread=int.from_bytes(expected[case['input']-DATA:case['input']-DATA+4],'little');struct.pack_into('<I',dest,off+24,(reread//86400+4)%7);struct.pack_into('<I',dest,off+32,0);expected_r0=output
   results=[]
   for u in machines:
    u.mem_write(DATA,bytes(data));u.mem_write(STATE,b'\x73'*32);u.mem_write(STATE+8,struct.pack('<H',case['offset']&65535));u.mem_write(FALLBACK,bytes(fallback));u.mem_write(SP-256,b'\x96'*512)
    args=[0x12345678,0x11111111,0x22222222,0x33333333] if case['kind']=='offset' else [case['input'],case['output'],0x22222222,0x33333333] if case['kind']=='unix' else [case['timestamp'],case['offset'],case['output'],0x33333333]
    for reg,value in zip(REGS,args):u.reg_write(reg,value)
    for i,reg in enumerate(SAVED):u.reg_write(reg,0x12340000+i)
    u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,0x20000101);s=dict(fault=None);states[id(u)]=s
    try:u.emu_start({'offset':0x8adb5,'unix':0x5a7bd,'utc':0x8af41}[case['kind']],0x20000100,count=10000)
    except UcError:assert s['fault']
    assert bool(s['fault'])==expected_fault,case
    if not expected_fault:assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==SP and [u.reg_read(reg) for reg in SAVED]==[0x12340000+i for i in range(8)] and u.reg_read(UC_ARM_REG_R0)==expected_r0 and bytes(u.mem_read(DATA,128))==expected and bytes(u.mem_read(FALLBACK,36))==expected_fallback,(case,u.reg_read(UC_ARM_REG_R0),expected_r0)
    results.append([[u.reg_read(reg) for reg in REGS],u.reg_read(UC_ARM_REG_SP),s['fault'],bytes(u.mem_read(DATA,128)).hex(),bytes(u.mem_read(STATE,32)).hex(),bytes(u.mem_read(FALLBACK,36)).hex(),bytes(u.mem_read(SP-256,512)).hex()])
   assert results[0]==results[1],case;counts[case['kind']]+=1;counts['faults']+=int(expected_fault);digest.update(json.dumps([case,results[0]],sort_keys=True).encode())
 receipt=dict(comparisons=len(cases),counts=counts,trace_sha256=digest.hexdigest(),exact_spans=proof,exact_bytes=sum(x['size'] for x in proof),object_sha256=sha(obj),shared_config_object_sha256=sha(config),driver_sha256=sha(Path(__file__)),report_sha256=sha(OUT/'report.json'),application_sha256=sha(app),all_65536_offset_words_checked=True,datetime_and_native_sequential_alias_oracle=True,actual_calendar_chain_executes_without_provider_fixtures=True,shared_config_native_placements_are_verification_bindings=True,full_private_history_or_raw_abi_verified=False,whole_image_complete=False,hardware_write_executed=False)
 (OUT/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
