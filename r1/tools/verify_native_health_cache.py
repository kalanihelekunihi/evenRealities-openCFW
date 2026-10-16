#!/usr/bin/env python3
"""Execute cache accessors/resets with actual memory clear and shared metadata."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-health-cache-runtime';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
SP=0x2003d000;START=0x20016400;LENGTH=0x800
ROWS=[('activity',0x200166c4,584,576,580,0x5a9f0,0x48288,'r1_activity_daily_cache_accessor','r1_activity_daily_cache_reset'),('hr',0x2001654c,84,72,80,0x5ace0,0x7062c,'r1_hr_daily_cache_accessor','r1_heart_rate_daily_cache_reset'),('spo2',0x200165a0,84,72,80,0x5baec,0x90dd4,'r1_spo2_daily_cache_accessor','r1_spo2_daily_cache_reset'),('hrv',0x200169c0,160,144,156,0x5af18,0x706be,'r1_hrv_daily_cache_accessor','r1_hrv_daily_cache_reset')]
def main():
 rp=OUT/'report.json';r=json.loads(rp.read_text());obj=OUT/'health-cache-source.o';assert sha(obj)==r['graph_object_sha256']
 for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 evidence={p.name:sha(p) for p in (BASE/'native-health-cache').glob('rea-*.json')}
 for p in (BASE/'native-health-cache').glob('rea-*.json'):
  e=json.loads(p.read_text())['structuredContent'];n=e['normalized_result'];a=int(n['address'],16);assert n['complete'] and e['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and bytes.fromhex(n['bytes_hex'])==app.read_bytes()[a-0x27000:a-0x27000+n['returned_bytes']]
 states={};digest=hashlib.sha256();counts=dict(getter=0,reset=0,workflow=0);clears=0
 with tempfile.TemporaryDirectory(prefix='r1-health-cache-') as tmp:
  d=Path(tmp);ld=d/'layout.ld';ld.write_text('SECTIONS { '+''.join('.cache_'+name+' '+hex(addr)+' : { *(.r1.health.cache.'+name+') } ' for name,addr,*_ in ROWS)+'.text 0x1000000 : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }');elf=d/'test.elf';binary=d/'text.bin'
  subprocess.run(['arm-none-eabi-ld','-T',str(ld),'-e','r1_activity_daily_cache_reset',str(obj),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-j','.text','-O','binary',str(elf),str(binary)],check=True)
  syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
  for name,addr,size,offset,ts,*_ in ROWS:assert syms['r1_cache_'+name]==addr and syms['r1_daily_'+name+'_offset']==addr+offset and syms['r1_daily_'+name+'_timestamp']==addr+ts
  def hook(u,a,size,_):
   nonlocal clears
   if a in [0x277aa,syms['__aeabi_memclr']]:
    states[id(u)].append([u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1)])
    if a==0x277aa:clears+=1
  machines=[]
  for i in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,0x20000);u.mem_write(0x1000000,binary.read_bytes());u.mem_map(0x20000000,0x40000);u.hook_add(UC_HOOK_CODE,hook);machines.append(u)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  def invoke(u,entry,args):
   for reg,value in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],args):u.reg_write(reg,value)
   for i,reg in enumerate(saved):u.reg_write(reg,0x12340000+i)
   u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,0x20000101);u.emu_start(entry|1,0x20000100,count=100000)
   assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==SP and [u.reg_read(reg) for reg in saved]==[0x12340000+i for i in range(8)]
   return u.reg_read(UC_ARM_REG_R0)
  for row,timestamp,offset,seed,workflow in itertools.product(ROWS,[0,1,0x7fffffff,0x80000000,0xffffffff],[0,1,0xffff,0x10000,0xffff8000,0xffffffff],[0,0x55,0xaa,0xff],[0,1]):
   name,addr,size,off,ts,getter,reset,getname,resetname=row;results=[]
   for side,u in enumerate(machines):
    u.mem_write(START,bytes([seed])*LENGTH);u.mem_write(SP-1024,b'\x96'*2048);states[id(u)]=[];trace=[]
    if workflow:
     for other in ROWS:
      trace.append(invoke(u,syms[other[8]] if side else other[6],[timestamp^0xa5a5a5a5,offset^0x12345678,0x87654321,0xabcdef01]))
    trace.append(invoke(u,syms[resetname] if side else reset,[timestamp,offset,0x87654321,0xabcdef01]));trace.append(invoke(u,syms[getname] if side else getter,[0x12345678,offset,0x87654321,0xabcdef01]));assert trace[-1]==addr
    results.append([trace,states[id(u)],bytes(u.mem_read(START,LENGTH)).hex()])
   assert results[0]==results[1],(name,timestamp,offset,seed,workflow,results[0][:2],results[1][:2])
   counts['getter']+=1;counts['reset']+=1;counts['workflow']+=workflow;digest.update(json.dumps([name,timestamp,offset,seed,workflow,results[0]],sort_keys=True).encode())
 receipt=dict(comparisons=counts['getter'],counts=counts,native_clear_calls=clears,trace_sha256=digest.hexdigest(),report_sha256=sha(rp),object_sha256=sha(obj),driver_sha256=sha(Path(__file__)),application_sha256=sha(app),evidence=evidence,actual_eight_bodies_and_memory_clear=True,no_provider_fixtures=True,canonical_metadata_addresses_and_nonduplicate_cache_state_checked=True,raw_r0_callee_sp_full_cache_region_checked=True,producer_service_initialization_proven=False,full_private_frame_history_verified=False,instruction_identity=False,whole_image_complete=False,hardware_write_executed=False)
 (OUT/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
