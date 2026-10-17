#!/usr/bin/env python3
"""Native notification timing/state and actual health-consumer composition."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-health-notification-throttle';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();SP=0x2003d000;D=0x20010000;CELL=0x200067a4;REGS=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3];SAVED=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
STAGES=[0x8c150,0x8cd60,0x8c750,0x8baec,0x8b818];CONSUMERS={0x8a7f4:'activity',0x8a80a:'hr',0x8a83e:'hrv',0x8a8ae:'spo2'};STORAGE={0x5aa14:'r1_activity_event_storage',0x5ad90:'r1_hr_event_storage',0x5af60:'r1_hrv_event_storage',0x5bb2c:'r1_spo2_event_storage'}
def main():
 b=json.loads((OUT/'report.json').read_text());obj=OUT/'native-health-notification-throttle-runtime.o';assert sha(obj)==b['linked_sha256'];c=json.loads((OUT/'contracts.json').read_text());providers={int(a,16):n for a,n in c['providers'].items()};providers.update(STORAGE);app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';states={};digest=hashlib.sha256();counts=dict(direct=0,consumer_composed=0);obs=dict(gate=0,clock=0,stage=0,storage=0);eligible_count=0
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 with tempfile.TemporaryDirectory(prefix='r1-health-throttle-') as tmp:
  d=Path(tmp);ld=d/'layout.ld';elf=d/'test.elf';text=d/'text.bin';ld.write_text('SECTIONS { .last 0x200067a4 : { *(.r1.health.notify.last) } .text 0x1000000 : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }');bindings={n:0x1100001+256*i for i,n in enumerate(providers.values())};roots=b['roots']+['r1_event_service_%08x'%a for a in CONSUMERS];subprocess.run(['arm-none-eabi-ld','--gc-sections',*[v for n in roots for v in ['-u',n]],'-T',str(ld),*[f'--defsym={n}={a}' for n,a in bindings.items()],str(obj),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-j','.text','-O','binary',str(elf),str(text)],check=True);syms={v[2]:int(v[0],16) for l in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=l.split())==3};assert syms['r1_health_notification_last_timestamp']==CELL;hooks={a:a for a in providers};hooks.update({bindings[n]&~1:a for a,n in providers.items()})
  def put(u,a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
  def hook(u,a,size,_):
   if a not in hooks:return
   a=hooks[a];st=states[id(u)];case=st['case'];args=[u.reg_read(x) for x in REGS];extra=None
   if a==0x4cbb0:
    kind='gate';value=case['gate']
    if case['mutation']=='gate':put(u,CELL,case['inject'])
   elif a==0x8ada4:
    kind='clock';value=case['now']
    if case['mutation']=='clock':put(u,CELL,case['inject'])
   elif a in STAGES:
    kind='stage';index=STAGES.index(a);value=case['returns'][index];assert args[0]==(1 if index==4 else 0) and (index!=4 or args[1]==0);st['stages'].append(index)
    if case['mutation']=='stages':put(u,CELL,case['inject']+index)
   else:kind='storage';value=0x87654321;extra=bytes(u.mem_read(args[0],8)).hex()
   st['trace'].append([kind,hex(a),args,u.reg_read(UC_ARM_REG_SP),extra,value]);
   if not st['side']:obs[kind]+=1
   for reg,v in zip(REGS,[value,0x11111111,0x22222222,0x33333333]):u.reg_write(reg,v)
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  machines=[]
  for side in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,0x40000);u.mem_write(0x1000000,text.read_bytes());u.mem_map(0x1100000,4096);u.mem_map(0x20000000,0x40000);u.hook_add(UC_HOOK_CODE,hook);machines.append(u)
  default=dict(entry=0x8b138,kind=0,last=0,now=10800,gate=1,mutation='none',inject=0x80000000,returns=[0,1,0xffffffff,0x80000000,0x12345678],sampletime=0);cases=[]
  for kind,last,now,gate,mutation,inject in itertools.product([0,1,4,5,0xffffffff],[0,1,10799,10800,0x7fffffff,0x80000000,0xffffffff],[0,1,10799,10800,10801,0x7fffffff,0x80000000,0xffffffff],[0,1,256,0xffffffff],['none','gate','clock','stages'],[0,1,0xffffffff]):cases.append(dict(default,kind=kind,last=last,now=now,gate=gate,mutation=mutation,inject=inject))
  for last,delta,gate in itertools.product([1,100,0x7fffffff,0xffff0000],[0,1,10798,10799,10800,10801,21599,21600],[0,1,0xffffffff]):cases.append(dict(default,last=last,now=(last+delta)&0xffffffff,gate=gate))
  for returns in [[0]*5,[0xffffffff]*5,[256,0,1,0x80000000,0xffffffff]]:
   for last,now in [(0,0),(1,10800),(1,10801),(0xffffffff,0)]:cases.append(dict(default,last=last,now=now,returns=returns))
  for entry,sampletime,last,now,gate,mutation in itertools.product(CONSUMERS,[0,123],[0,1,10800,0xffffffff],[0,1,10799,10800,10801,0xffffffff],[0,1,0xffffffff],['none','gate','clock','stages']):cases.append(dict(default,entry=entry,sampletime=sampletime,last=last,now=now,gate=gate,mutation=mutation))
  for case in cases:
   composed=case['entry']!=0x8b138;family=CONSUMERS.get(case['entry']);consumer_clock=composed and (family=='spo2' or family in ['hr','hrv'] and not case['sampletime']);prior=case['inject'] if case['mutation']=='clock' and consumer_clock else case['last'];prior=case['inject'] if case['mutation']=='gate' else prior
   observed_last=case['inject'] if case['gate'] and case['mutation']=='clock' else prior;eligible=bool(case['gate']) and (observed_last==0 or case['now']<observed_last or case['now']-observed_last>=10800);expected_last=case['now'] if eligible else observed_last;results=[]
   for side,u in enumerate(machines):
    u.mem_write(SP-1024,b'\x96'*2048);u.mem_write(D,struct.pack('<4I',100,case['sampletime'],0xabcdef01,0x98765432));u.mem_write(CELL-4,struct.pack('<3I',0x13579bdf,case['last'],0x2468ace0));args=[D if composed else case['kind'],8,0xabcdef01,0x98765432]
    for reg,v in zip(REGS,args):u.reg_write(reg,v)
    for i,reg in enumerate(SAVED):u.reg_write(reg,0x12340000+i)
    u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,0x20000101);st=dict(case=case,side=side,trace=[],stages=[]);states[id(u)]=st;name='r1_event_service_%08x'%case['entry'] if composed else 'r1_health_event_notification_throttle';u.emu_start((syms[name] if side else case['entry'])|1,0x20000100,count=10000);assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==SP and [u.reg_read(x) for x in SAVED]==[0x12340000+i for i in range(8)]
    expected_stages=list(range(5)) if eligible else [];assert st['stages']==expected_stages and struct.unpack('<3I',u.mem_read(CELL-4,12))==(0x13579bdf,expected_last,0x2468ace0),(case,st,expected_last)
    if not composed:
     expected_r0=case['returns'][4] if eligible else (case['now']-observed_last if case['gate'] else 0);assert u.reg_read(UC_ARM_REG_R0)==expected_r0
    results.append([[u.reg_read(x) for x in REGS],st['trace'],bytes(u.mem_read(CELL-4,12)).hex(),bytes(u.mem_read(D,16)).hex()])
   if results[0]!=results[1]:(OUT/'counterexample.json').write_text(json.dumps(dict(case=case,results=results),indent=2)+'\n');raise AssertionError(case)
   counts['consumer_composed' if composed else 'direct']+=1;eligible_count+=eligible;digest.update(json.dumps([case,results[0]],sort_keys=True).encode())
 receipt=dict(comparisons=sum(counts.values()),counts=counts,eligible_sends=eligible_count,observation_counts=obs,trace_sha256=digest.hexdigest(),report_sha256=sha(OUT/'report.json'),object_sha256=sha(obj),driver_sha256=sha(Path(__file__)),application_sha256=sha(app),rea_bytes_sha256=sha(OUT/'rea-native-bytes.json'),independent_unsigned_throttle_and_state_oracle=True,actual_throttle_and_four_health_consumers_execute=True,gate_clock_send_stages_and_storage_are_fixtures=True,fresh_timestamp_state_after_callbacks_and_final_captured_time_store_checked=True,raw_r0_r3_callee_sp_typed_args_state_and_neighbor_guards_checked=True,full_dispatcher_composition=False,full_native_context_extent_proven=False,full_private_frame_history_verified=False,full_raw_abi_verified=False,instruction_identity=False,whole_image_complete=False,hardware_write_executed=False)
 (OUT/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
