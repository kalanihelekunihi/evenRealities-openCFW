#!/usr/bin/env python3
"""Native shared mode, channel veneers and pair controls with typed leaf fixtures."""
import hashlib,itertools,json,random,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-gxt310-mode';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
REGIONS=[('word',0x6f6b4,4),('error_ring',0x6f6b8,64),('bounds',0x6f6f8,8),('error_sdk',0x6f700,56),('pair_bounds',0x51028,8),('pair0_ring',0x51030,44),('pair0_sdk',0x5105c,40),('pair2_ring',0x51084,44),('pair2_sdk',0x510b0,40)]
CALLS=[('r1_gxt310_register_write_native',0x6f644),('r1_structured_log_mode_get',0x914ec),('r1_structured_log_format',0x91638),('nrf_log_frontend_std_0',0x799c0),('nrf_log_frontend_std_1',0x799c8),('r1_gxt310_mode_channel0',0x6f804),('r1_gxt310_mode_channel2',0x6f81e)]
ENTRIES={'shared':('r1_gxt310_switch_mode_native',0x6f648),'channel0':('r1_gxt310_mode_channel0',0x6f804),'channel2':('r1_gxt310_mode_channel2',0x6f81e),'enable':('r1_gxt310_enable_pair_native',0x50f9c),'disable':('r1_gxt310_disable_pair_native',0x50f88)}
def main():
 vp=OUT/'verification.json';vp.unlink(missing_ok=True);rp=OUT/'report.json';report=json.loads(rp.read_text());obj=OUT/'native_gxt310_mode.o';assert sha(obj)==report['units'][0]['object_sha256']
 for p,h in report['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';layout=ROOT/'r1/source-config/runtime/native_gxt310_mode_verification.ld';states={};digest=hashlib.sha256();counts={k:0 for k in ENTRIES};callbacks=0;writes=0;rng=random.Random(0x6f648)
 with tempfile.TemporaryDirectory() as tmp:
  d=Path(tmp);elf=d/'test.elf';subprocess.run(['arm-none-eabi-ld','-T',str(layout),str(obj),'-o',str(elf)],check=True);syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3};sections=[]
  for name,a,n in [('text',0x1000000,None),*REGIONS]:
   p=d/(name+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j','.'+name,'-O','binary',str(elf),str(p)],check=True);data=p.read_bytes();sections.append((a,data))
   if n is not None:assert len(data)==n and data==raw[a-0x27000:a-0x27000+n]
  native={a:i for i,(_,a) in enumerate(CALLS)};compiled={syms[n]&~1:i for i,(n,_) in enumerate(CALLS)}
  def hook(u,address,size,_):
   st=states[id(u)];index=(compiled if st['source'] else native).get(address)
   if index is not None and index>=5 and st['kind'] not in ['enable','disable']:index=None
   if index is None:assert not st['source'] or not 0x27000<=address<0xc4d08;return
   args=[u.reg_read(reg) for reg in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]]
   if index==0:
    word=struct.unpack('<I',u.mem_read(args[2],4))[0];assert args[0]==st['address'] and args[1]==1 and args[3]==2 and word==(0xc201 if st['enabled']==0 else 0xc200)
    used=[args[0],1,2,word];u.mem_write(args[2],bytes.fromhex('efbeadde'));value=st['statuses'][0]
   elif index==1:value=st['modes'][st['mode_index']];st['mode_index']+=1;used=[value]
   elif index==2:used=args[:4 if args[0]==0x04400000 else 3];value=0x55aa55aa
   elif index in [3,4]:used=args[:2 if index==3 else 3];value=0x55aa55aa
   else:assert args[0]==int(st['kind']=='enable');used=[args[0]];value=st['statuses'][index-5]
   st['events'].append([index,used,value]);st['cell']=(st['cell']+index+1)&0xffffffff;u.mem_write(0x20006000,st['cell'].to_bytes(4,'little'))
   for i,reg in enumerate([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_R12]):u.reg_write(reg,(0xabcdef01+i*0x11111111)&0xffffffff)
   u.reg_write(UC_ARM_REG_R0,value);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  machines=[]
  for candidate in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,raw);u.mem_map(0x1000000,0x10000);u.mem_map(0x20000000,0x40000)
   if candidate:
    for a,data in sections:u.mem_write(a,data)
   u.hook_add(UC_HOOK_CODE,hook);machines.append(u)
  modes=[list(q)+list(reversed(q)) for q in itertools.product(range(8),repeat=3)]+[[rng.getrandbits(32) for _ in range(6)] for _ in range(128)];fixed=[[0]*6,[1]*6,[2]*6,[4]*6];statuses=[0,1,4,0x80000000,0xffffffff];enabled=[0,1,2,0xffffffff];cases=[]
  for address,en,status,q,fill in itertools.product(range(256),enabled,statuses,fixed,[0,0x96]):cases.append(('shared',address,en,(status,0),q,fill))
  for address,en,q,fill in itertools.product([0x90,0x94,0xffffffff],enabled,modes,[0,0x96]):cases.append(('shared',address,en,(0,0),q,fill))
  for kind,address in [('channel0',0x90),('channel2',0x94)]:
   for en,status,q,fill in itertools.product(enabled,statuses,fixed,[0,0x96]):cases.append((kind,address,en,(status,0),q,fill))
   for en,q,fill in itertools.product(enabled,modes,[0,0x96]):cases.append((kind,address,en,(0,0),q,fill))
  pair_statuses=[0,1,2,0x80000000,0xffffffff,0x12345678]
  for pair,q,fill in itertools.product(itertools.product(pair_statuses,repeat=2),modes,[0,0x96]):cases.append(('enable',0,1,pair,q,fill))
  for pair,fill in itertools.product(itertools.product(pair_statuses,repeat=2),[0,0x96]):cases.append(('disable',0,0,pair,[0]*6,fill))
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  for kind,address,en,pair,q,fill in cases:
   results=[]
   for candidate,u in enumerate(machines):
    u.mem_write(0x20000000,bytes([fill])*0x3e000);initial=bytearray(u.mem_read(0x20000000,0x3e000));u.reg_write(UC_ARM_REG_XPSR,0x01000000);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101);u.reg_write(UC_ARM_REG_R0,address if kind=='shared' else en);u.reg_write(UC_ARM_REG_R1,en)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    st=dict(source=candidate,kind=kind,address=address,enabled=en,statuses=pair,modes=q,mode_index=0,events=[],cell=int.from_bytes(bytes([fill])*4,'little'));states[id(u)]=st
    u.emu_start((syms[ENTRIES[kind][0]] if candidate else ENTRIES[kind][1])|1,0x20000100,count=10000);assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
    expected=pair[0]&pair[1] if kind=='enable' else pair[1] if kind=='disable' else int(pair[0]!=0);assert u.reg_read(UC_ARM_REG_R0)==expected
    if kind in ['enable','disable']:assert [e[0] for e in st['events'] if e[0]>=5]==[5,6]
    initial[0x6000:0x6004]=st['cell'].to_bytes(4,'little');actual=bytes(u.mem_read(0x20000000,0x3e000));assert initial==actual
    results.append([st['events'],st['mode_index'],u.reg_read(UC_ARM_REG_R0),hashlib.sha256(actual).hexdigest()])
   if results[0]!=results[1]:
    fail=dict(kind=kind,address=address,enabled=en,statuses=pair,modes=q,fill=fill,results=results);(OUT/'counterexample.json').write_text(json.dumps(fail,indent=2)+'\n');raise AssertionError(fail)
   counts[kind]+=1;callbacks+=len(results[0][0]);writes+=sum(e[0]==0 for e in results[0][0]);digest.update(json.dumps([kind,address,en,pair,q,fill,results[0]],sort_keys=True).encode())
 r=dict(comparisons=sum(counts.values()),counts=counts,callback_observations_per_side=callbacks,write_calls_per_side=writes,trace_sha256=digest.hexdigest(),full_four_byte_config_word_checked=True,zero_enabled_sets_low_byte_bit0_only=True,any_nonzero_write_result_is_success=True,write_buffer_mutated_by_fixture=True,pair_always_calls_both_channels_before_logging=True,pair_result_is_raw_bitwise_and=True,disable_raw_r0_matches_last_channel_fixture=True,full_width_statuses_and_modes_and_all_byte_addresses=True,raw_r0_callee_integer_stack_full_observed_nonstack_ram_and_typed_callback_args_order_checked=True,private_config_pointer_normalized=True,write_logging_and_pair_channel_providers_are_fixtures=True,source_data_bytes=308,candidate_native_body_execution_forbidden=True,unicorn_memory_write_hooks_disabled=True,whole_startup_graph_executed=False,physical_sensor_verified=False,instruction_identity=False,full_raw_abi_verified=False,application_sha256=sha(app),driver_sha256=sha(Path(__file__)),report_sha256=sha(rp),object_sha256=sha(obj),layout=str(layout.relative_to(ROOT)),layout_sha256=sha(layout),limitations=['Shared/channel tests use a named write fixture; pair tests use named channel fixtures so arbitrary uint32 return/bitwise behavior remains visible.','Source/native initialize the full four-byte configuration word; private frame addresses and other raw scratch/stack details remain gated.','Physical sensor/bus, actual full source startup, final data/link placement, original compiler and byte-identical image remain open.'])
 vp.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
if __name__=='__main__':main()
