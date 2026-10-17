#!/usr/bin/env python3
"""Activity storage packed counters, bucket bounds, aliasing and bucket helper."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-activity-storage';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();SP=0x2003d000;CACHE=0x200166c4;ARENA=CACHE-16;SIZE=640;DATA=0x20010000
REGS=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3];SAVED=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
def main():
 c=json.loads((OUT/'contracts.json').read_text());cc=json.loads((BASE/'native-calendar-frames/contracts.json').read_text());calendarobj=BASE/'native-calendar-frames/native_calendar_frames.o';config=BASE/'native-calendar-frames/shared-calendar-config.o';obj=OUT/'native_activity_storage.o';cacheobj=OUT/'activity-cache.o';app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';image=app.read_bytes();assert sha(app)==c['application_sha256']=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';states={};digest=hashlib.sha256();counts={'storage':0};proof=[]
 spans=[(x['symbol'],int(x['address'],16),x['source_span_bytes'],'.text.'+x['symbol']) for x in c['bodies']+cc['bodies']]+[('months',0x99c5c,24,'.rodata.month_days_forward')]+[('multi_ring',0xbf92c,81,'.r1.activity.multi_ring'),('multi_sdk',0xbf980,75,'.r1.activity.multi_sdk')]
 with tempfile.TemporaryDirectory() as td:
  td=Path(td);ld=td/'layout.ld';ld.write_text('SECTIONS {'+''.join(' .s%d 0x%x : { *(%s) }'%(i,a,sec) for i,(n,a,l,sec) in enumerate(spans))+' .state 0x20016ac4 : { *(.r1.time.state) } .fallback 0x20016ae4 (NOLOAD) : { *(.bss.unix_to_broken_down_fallback) } .cache 0x200166c4 : { *(.r1.health.cache.activity) } /DISCARD/ : { *(.ARM.exidx*) } }\n'+''.join('%s = 0x%x;\n'%(n,int(a,16)|1) for a,n in c['providers'].items() if int(a,16) not in [0x5ac74,0x8adb4,0x8af40]));elf=td/'proof.elf';subprocess.run(['arm-none-eabi-ld','-T',str(ld),str(obj),str(cacheobj),str(calendarobj),str(config),'-o',str(elf)],check=True,stderr=subprocess.PIPE);replacement=[]
  for i,(n,a,length,sec) in enumerate(spans):
   p=td/(str(i)+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j','.s'+str(i),'-O','binary',str(elf),str(p)],check=True);d=p.read_bytes();assert len(d)==length and d==image[a-0x27000:a-0x27000+length];replacement.append((a,d));proof.append(dict(symbol=n,address=hex(a),size=length,sha256=sha(p)))
  def mutate(u,p):
   a,b,d,dur,t=struct.unpack('<4HI',u.mem_read(p,12));u.mem_write(p,struct.pack('<4HI',(a+1)&65535,(b+2)&65535,(d+3)&65535,(dur+4)&65535,(t+5)&0xffffffff))
  interested={0x5ac74,0x8adb4,0x8af40,0x914ec,0x91638,0x799f8,0x79a28}
  def hook(u,a,size,_):
   if a not in interested:return
   s=states[id(u)];case=s['case'];r=[u.reg_read(x) for x in REGS]
   if a==0x5ac74:s['trace'].append(['actual-bucket',r]);return
   elif a==0x8adb4:
    i=s['offsets'];assert i<2;s['offsets']+=1;u.mem_write(0x20016acc,struct.pack('<H',case['offset_pair'][i]&65535));s['trace'].append(['actual-offset',r]);return
   elif a==0x8af40:
    i=s['buckets'];assert i<2;s['buckets']+=1;s['trace'].append(['actual-calendar',r])
    if case['mutation']&(1<<i):mutate(u,s['packet'])
    return
   elif a==0x914ec:
    v=case['modes'][s['mode']%len(case['modes'])];s['mode']+=1;s['trace'].append(['mode',v]);u.reg_write(UC_ARM_REG_R0,v);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR));return
   else:s['trace'].append(['log',hex(a),r,bytes(u.mem_read(u.reg_read(UC_ARM_REG_SP),20)).hex()]);u.reg_write(UC_ARM_REG_R0,0x87654321)
   for reg,value in zip(REGS[1:],[0xa1a1a1a1,0xb2b2b2b2,0xc3c3c3c3]):u.reg_write(reg,value)
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  machines=[]
  for side in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x100000);u.mem_write(0x27000,image);u.mem_map(0x20000000,0x40000)
   if side:
    for a,d in replacement:u.mem_write(a,d)
   u.hook_add(UC_HOOK_CODE,hook);machines.append(u)
  default=dict(kind='storage',start=0,end=0,fields=(1,2,3),seed=0,duration=600,timestamp=0x80000001,mutation=0,modes=[0],packet_kind=0,hour=0,minute=0,written=8)
  cases=[dict(default,offset_pair=(0,0),timestamp=20000*86400+minute*600+second,duration=duration,fields=(minute,65535,4095),seed=0xffffffff) for minute,duration,second in itertools.product(range(144),[0,1,599,600,601,65535],[0,1,599])]
  cases += [dict(default,offset_pair=offsets,timestamp=timestamp,duration=65535,fields=(65535,65535,65535),seed=seed,mutation=mutation,packet_kind=alias,modes=[0,4,2,1]) for offsets,timestamp,mutation,alias,seed in itertools.product([(0,0),(60,60),(-60,60),(32767,-32768)],[0,1,599,600,86399,86400,0x7fffffff,0xffffffff],range(4),[0,1,3],[0,0xffffffff,0x55443322])]
  for case in cases:
   case['start']=(((case['timestamp']-case['duration']+case['offset_pair'][0]*60)&0xffffffff)//600)%144;case['end']=(((case['timestamp']+(5 if case['mutation']&1 else 0)+case['offset_pair'][1]*60)&0xffffffff)//600)%144
   packet=DATA if case['packet_kind']==0 else CACHE+case['start']*4 if case['packet_kind']==1 else CACHE+case['start']*4-2;initial=bytearray(b'\x96'*SIZE)
   for i in range(144):struct.pack_into('<I',initial,16+i*4,case['seed'])
   pdata=bytearray(struct.pack('<4HI',*case['fields'],case['duration'],case['timestamp']))
   if ARENA<=packet<=ARENA+SIZE-12:initial[packet-ARENA:packet-ARENA+12]=pdata
   expected=bytearray(initial);pexpected=bytearray(pdata)
   def read(a,n):return bytes(expected[a-ARENA:a-ARENA+n]) if ARENA<=a<ARENA+SIZE else bytes(pexpected[a-DATA:a-DATA+n])
   def write(a,d):
    if ARENA<=a<ARENA+SIZE:expected[a-ARENA:a-ARENA+len(d)]=d
    else:pexpected[a-DATA:a-DATA+len(d)]=d
   if case['kind']=='storage' and packet:
    for bit in [1,2]:
     if case['mutation']&bit:
      a,b,d,dur,t=struct.unpack('<4HI',read(packet,12));write(packet,struct.pack('<4HI',(a+1)&65535,(b+2)&65535,(d+3)&65535,(dur+4)&65535,(t+5)&0xffffffff))
    if case['start']<144 and case['end']<144:
     address=CACHE+case['start']*4;word=int.from_bytes(read(address,4),'little');word=(word&0xfffff000)|((word+int.from_bytes(read(packet+4,2),'little'))&4095);write(address,struct.pack('<I',word));word=(word&0xffc00fff)|((((word>>12)+int.from_bytes(read(packet+2,2),'little'))&1023)<<12);write(address,struct.pack('<I',word));word=(word&0x003fffff)|((((word>>22)+int.from_bytes(read(packet,2),'little'))&1023)<<22);write(address,struct.pack('<I',word))
   results=[]
   for u in machines:
    u.mem_write(0x20016ac4,bytes(68));u.mem_write(ARENA,bytes(initial));u.mem_write(DATA,bytes(pdata));u.mem_write(SP-128,b'\x96'*256)
    args=[case['timestamp'],0x11111111,0x22222222,0x33333333] if case['kind']=='bucket' else [packet,0x11111111,0x22222222,0x33333333]
    for reg,value in zip(REGS,args):u.reg_write(reg,value)
    for i,reg in enumerate(SAVED):u.reg_write(reg,0x12340000+i)
    u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,0x20000101);s=dict(case=case,packet=packet,buckets=0,offsets=0,mode=0,trace=[]);states[id(u)]=s;u.emu_start(0x5ac75 if case['kind']=='bucket' else 0x5aa15,0x20000100,count=10000)
    assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==SP and [u.reg_read(reg) for reg in SAVED]==[0x12340000+i for i in range(8)] and bytes(u.mem_read(ARENA,SIZE))==expected and bytes(u.mem_read(DATA,12))==pexpected,case
    if case['kind']=='bucket':assert u.reg_read(UC_ARM_REG_R0)==(((case['hour'] if case['written']>=5 else 0)*6+(case['minute']//10 if case['written']>=6 else 0))&255)
    else:assert s['buckets']==2 and s['offsets']==2 and int.from_bytes(u.mem_read(0x20016acc,2),'little')==case['offset_pair'][1]&65535
    results.append([[u.reg_read(reg) for reg in REGS],s['trace'],bytes(u.mem_read(ARENA,SIZE)).hex(),bytes(u.mem_read(DATA,12)).hex(),bytes(u.mem_read(SP-128,256)).hex(),bytes(u.mem_read(0x20016ac4,68)).hex()])
   assert results[0]==results[1],case;counts[case['kind']]+=1;digest.update(json.dumps([case,results[0]],sort_keys=True).encode())
 receipt=dict(comparisons=sum(counts.values()),counts=counts,trace_sha256=digest.hexdigest(),exact_spans=proof,exact_bytes=sum(x['size'] for x in proof),calendar_object_sha256=sha(calendarobj),shared_calendar_config_sha256=sha(config),object_sha256=sha(obj),reused_activity_cache_object_sha256=sha(cacheobj),driver_sha256=sha(Path(__file__)),report_sha256=sha(OUT/'report.json'),application_sha256=sha(app),actual_storage_bucket_offset_calendar_unix_source_chain_executes=True,packed_12_10_10_counter_wrap_and_alias_independent_oracle=True,whole_delta_deposited_in_start_bucket_preserved=True,calendar_or_bucket_provider_is_fixture=False,timezone_packet_updates_and_logging_are_controlled_fixtures=True,full_private_history_or_raw_abi_verified=False,whole_image_complete=False,hardware_write_executed=False)
 (OUT/'composed-verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
