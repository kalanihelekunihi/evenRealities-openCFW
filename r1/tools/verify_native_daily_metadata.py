#!/usr/bin/env python3
"""Daily metadata graphs execute source clock/division with named backend/logger fixtures."""
import hashlib,itertools,json,random,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-daily-metadata';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ROWS=[('activity',0x5a9f8,0x8a7f0,0x20016908,0x20016904),('hr',0x5ad08,0x8d534,0x2001659c,0x20016594),('hrv',0x5af44,0x8d884,0x20016a5c,0x20016a50),('spo2',0x5bb14,0x8e54e,0x200165f0,0x200165e8),('stress',0x5bcd4,0x8e558,0x200166c0,0x200166b8),('temperature',0x5be64,0x8e69c,0x20016644,0x2001663c)]
def main():
 rp=BASE/'native-daily-metadata-runtime/report.json';r=json.loads(rp.read_text());obj=rp.parent/'daily-metadata-source.o';assert sha(obj)==r['metadata_object_sha256']
 for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';layout=ROOT/'r1/source-config/runtime/native_daily_metadata_verification.ld';states={};digest=hashlib.sha256();counts={};backend_calls=0;logger_calls=0
 with tempfile.TemporaryDirectory() as tmp:
  d=Path(tmp);elf=d/'test.elf';binary=d/'text.bin';subprocess.run(['arm-none-eabi-ld','-T',str(layout),str(obj),'-o',str(elf)],check=True)
  sections={}
  for section in ['.text','.hr_ring','.hr_sdk']:
   path=d/(section[1:]+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j',section,'-O','binary',str(elf),str(path)],check=True);sections[section]=path.read_bytes()
  syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3};assert syms['r1_time_state']==0x20016ac4 and syms['r1_time_registration']==0x20006820
  assert sections['.hr_ring']==raw[0x5ad60-0x27000:0x5ad75-0x27000] and sections['.hr_sdk']==raw[0x5ad80-0x27000:0x5ad8f-0x27000]
  for name,_,_,timestamp,offset in ROWS:assert syms[f'r1_daily_{name}_timestamp']==timestamp and syms[f'r1_daily_{name}_offset']==offset
  def snapshot(u):return [bytes(u.mem_read(ts,4)).hex()+bytes(u.mem_read(off,2)).hex() for _,_,_,ts,off in ROWS]
  def hook(u,a,size,_):
   st=states[id(u)];source=st['source'];assert not source or not 0x27000<=a<0xc4d08
   if a==0x2000020c:
    assert u.reg_read(UC_ARM_REG_R0)==0;st['events'].append(['backend',snapshot(u)]);u.reg_write(UC_ARM_REG_R0,st['epoch'])
    if st['mutation']==1:u.mem_write(0x20016acc,struct.pack('<h',st['changed_offset']))
    u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR));return
   fixture={0x20000200:'mode',0x20000204:'ring',0x20000208:'sdk'} if source else {0x914ec:'mode',0x91638:'ring',0x799c8:'sdk'}
   if a not in fixture:return
   kind=fixture[a]
   if kind=='mode':
    value=st['modes'][st['mode_index']%len(st['modes'])];st['mode_index']+=1;st['events'].append(['mode',value,snapshot(u)]);u.reg_write(UC_ARM_REG_R0,value)
    if st['mutation']==2:u.mem_write(0x2001659c,struct.pack('<I',0x89abcdef+st['mode_index']))
   elif kind=='ring':
    regs=[u.reg_read(reg) for reg in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];assert regs[:3]==[0x0c400000,0x5ad60,0x5ad60];st['events'].append(['ring',regs,snapshot(u)]);u.reg_write(UC_ARM_REG_R0,0xaabbccdd)
    if st['mutation']==3:u.mem_write(0x2001659c,struct.pack('<I',0xfedcba98))
   else:
    regs=[u.reg_read(reg) for reg in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2]];assert regs[:2]==[0x001c0003,0x5ad80];st['events'].append(['sdk',regs,snapshot(u)]);u.reg_write(UC_ARM_REG_R0,st['sdk_return'])
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  machines=[]
  for source in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,raw);u.mem_map(0x1000000,0x20000);u.mem_write(0x1000000,sections['.text']);u.mem_map(0x20000000,0x40000);u.hook_add(UC_HOOK_CODE,hook);machines.append(u)
  rng=random.Random(0x5a9f8);epochs=[0,1,86399,86400,86401,0x7fffffff,0x80000000,0xffffffff]+[rng.getrandbits(32) for _ in range(8)];offsets=[-32768,-1440,-1,0,1,840,1440,32767];modes=[[0],[1],[2],[4],[7],[0,4,2],[1,0],[0xffffffff,0x80000000]];entries=[]
  for name,body,veneer,_,_ in ROWS:entries.extend([(name,'r1_daily_'+name+'_refresh',body),(name+'_veneer','r1_native_'+('hr' if name=='hr' else name)+'_cache_initialize',veneer)])
  entries.extend([('day','r1_time_local_day_start',0x8ad64),('offset','r1_time_utc_offset_get',0x8adb4)])
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  for (name,symbol,entry),epoch,offset,mode,mutation in itertools.product(entries,epochs,offsets,modes,range(4)):
   results=[];changed_offset=-offset if offset!=-32768 else 32767
   for source,u in enumerate(machines):
    u.mem_write(0x20000000,b'\x96'*0x40000);u.mem_write(0x20016acc,struct.pack('<h',offset));u.mem_write(0x20006828,struct.pack('<I',0x20002000));u.mem_write(0x20002008,struct.pack('<I',0x2000020d));states[id(u)]=dict(source=source,events=[],epoch=epoch,mutation=mutation,changed_offset=changed_offset,modes=mode,mode_index=0,sdk_return=epoch^0xa55a5aa5)
    u.reg_write(UC_ARM_REG_XPSR,0x01000000);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    for reg,value in [(UC_ARM_REG_R0,0x12345678),(UC_ARM_REG_R1,0x89abcdef),(UC_ARM_REG_R2,0x55667788),(UC_ARM_REG_R3,0x99aabbcc)]:u.reg_write(reg,value)
    u.emu_start((syms[symbol] if source else entry)|1,0x20000100,count=100000);assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
    memory=bytes(u.mem_read(0x20000000,0x3e000))+bytes(u.mem_read(0x2003f000,0x1000));results.append([u.reg_read(UC_ARM_REG_R0),states[id(u)]['events'],hashlib.sha256(memory).hexdigest()])
   if results[0]!=results[1]:
    failure=dict(name=name,epoch=epoch,offset=offset,mode=mode,mutation=mutation,results=results);(OUT/'counterexample.json').write_text(json.dumps(failure,indent=2)+'\n');raise AssertionError({k:v for k,v in failure.items() if k!='results'})
   counts[name]=counts.get(name,0)+1;backend_calls+=sum(x[0]=='backend' for x in results[0][1]);logger_calls+=sum(x[0] in ['ring','sdk'] for x in results[0][1]);digest.update(json.dumps([name,epoch,offset,mode,mutation,results[0]],sort_keys=True).encode())
 receipt=dict(comparisons=sum(counts.values()),counts=counts,backend_calls_per_side=backend_calls,logger_calls_per_side=logger_calls,trace_sha256=digest.hexdigest(),actual_source_day_offset_backend_and_u64_division=True,backend_and_logging_are_named_fixtures=True,source_metadata_fields_bytes=36,controlled_timezone_and_logger_mutations_are_fixtures=True,raw_r0_callee_sp_and_full_observed_nonstack_ram_checked=True,no_native_candidate_body_execution=True,driver_sha256=sha(Path(__file__)),object_sha256=sha(obj),runtime_report_sha256=sha(rp),layout_sha256=sha(layout),application_sha256=sha(app),instruction_identity=False,physical_clock_or_cache_verified=False,whole_image_complete=False)
 (OUT/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
