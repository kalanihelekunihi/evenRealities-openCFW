#!/usr/bin/env python3
"""Native YHM configuration and paired GXT IDs against recovered source bodies."""
import hashlib,itertools,json,random,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-device-checks';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
CALLS=[('r1_yhm_chip_id_native',0x3530c),('r1_yhm_register_write_native',0x35760),('r1_rtt_delay_cycles',0x9a670),('r1_structured_log_mode_get',0x914ec),('r1_structured_log_format',0x91638),('nrf_log_frontend_std_0',0x799c0),('r1_gxt310_bus_acquire',0x50f28),('r1_gxt310_enable_pair_native',0x50f9c),('r1_gxt310_chip_id_channel0',0x6f812),('r1_gxt310_chip_id_channel2',0x6f82c),('r1_gxt310_disable_pair_native',0x50f88),('r1_gxt310_bus_release',0x50efc)]
REGIONS=[('bounds',0x351ec,8),('error_ring',0x351f4,32),('error_sdk',0x35214,24),('success_ring',0x3522c,32),('success_sdk',0x3524c,24)]
def main():
 vp=OUT/'verification.json';vp.unlink(missing_ok=True);rp=OUT/'report.json';r=json.loads(rp.read_text());obj=OUT/'native_device_checks.o';assert sha(obj)==r['units'][0]['object_sha256']
 for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';layout=ROOT/'r1/source-config/runtime/native_device_checks_verification.ld';rng=random.Random(0x3510c);states={};digest=hashlib.sha256();counts={'yhm':0,'void_adapter':0,'gxt':0};callbacks=0;delay_calls=0;write_calls=0
 with tempfile.TemporaryDirectory() as tmp:
  d=Path(tmp);elf=d/'test.elf';subprocess.run(['arm-none-eabi-ld','-T',str(layout),str(obj),'-o',str(elf)],check=True);symbols={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3};sections=[]
  for name,a,n in [('text',0x1000000,None),*REGIONS,('delay',0x35264,4)]:
   path=d/(name+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j','.'+name,'-O','binary',str(elf),str(path)],check=True);data=path.read_bytes();sections.append((a,data))
   if n is not None:
    assert len(data)==n
    if name=='delay':assert struct.unpack('<I',data)[0]==symbols['r1_rtt_delay_cycles']
    else:assert data==raw[a-0x27000:a-0x27000+n]
  native={a:i for i,(_,a) in enumerate(CALLS)};compiled={symbols[n]&~1:i for i,(n,_) in enumerate(CALLS)}
  def hook(u,address,size,_):
   st=states[id(u)];index=(compiled if st['source'] else native).get(address)
   if index is None:assert not st['source'] or not 0x27000<=address<0xc4d08;return
   args=[u.reg_read(reg) for reg in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2]];args_used=[]
   if index==0:value=st['chip']
   elif index==1:
    assert args[1]==1;pointer=args[2];args_used=[args[0],args[1],u.mem_read(pointer,1)[0]];st['pointers'].append(pointer);u.mem_write(pointer,b'\xe7');value=st['writes'][st['write_index']];st['write_index']+=1
   elif index==2:assert args[0]==64000;args_used=[args[0]];value=0xdadadada
   elif index==3:value=st['modes'][st['mode_index']];st['mode_index']+=1
   elif index in [4,5]:args_used=args[:3 if index==4 else 2];value=0x55aa55aa
   elif index==8:value=st['ids'][0]
   elif index==9:value=st['ids'][1]
   else:value=st['leaf_status'][index-6]
   st['events'].append([index,args_used,value]);slot=0x20006000+4*index;new=(struct.unpack('<I',u.mem_read(slot,4))[0]+index+1)&0xffffffff;u.mem_write(slot,struct.pack('<I',new));st['cells'][index]=new
   for i,reg in enumerate([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_R12]):u.reg_write(reg,(0xabcdef01+i*0x11111111)&0xffffffff)
   u.reg_write(UC_ARM_REG_R0,value);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  machines=[]
  for candidate in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,raw);u.mem_map(0x1000000,0x10000);u.mem_map(0x20000000,0x40000)
   if candidate:
    for address,data in sections:u.mem_write(address,data)
   u.hook_add(UC_HOOK_CODE,hook);machines.append(u)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  modes=[list(q) for q in itertools.product(range(8),repeat=3)]+[[rng.getrandbits(32) for _ in range(3)] for _ in range(128)]
  writes=[[0]*5,[1]*5,[0xffffffff]*5,[0,1,0,1,0],[0x80000000,4,5,0,7],[rng.getrandbits(32) for _ in range(5)]]
  cases=[]
  for chip,q,w,fill in itertools.product([0xa0,0,0xa1,0x100a0,0xffffffff],modes,writes,[0,0x96]):cases.append(('yhm',chip,(0,0),q,w,[0]*6,fill))
  for chip,q,fill in itertools.product(range(256),[[0]*3,[1]*3,[2]*3,[4]*3],[0,0x96]):cases.append(('yhm',chip,(0,0),q,writes[-1],[0]*6,fill))
  for chip,q,fill in itertools.product([0xa0,0,0xffffffff],modes,[0,0x96]):cases.append(('void_adapter',chip,(0,0),q,writes[-1],[0]*6,fill))
  for id0,id2 in itertools.product(range(256),repeat=2):cases.append(('gxt',0,(id0,id2),[0]*3,[0]*5,[0,1,2,3,4,5],0x96))
  high=[0,1,0x4f,0x50,0x51,0xff,0x100,0x150,0x80000050,0xffffffff]
  for ids,leaf_status,fill in itertools.product(itertools.product(high,repeat=2),[[0]*6,[0xffffffff]*6,[rng.getrandbits(32) for _ in range(6)]],[0,0x96]):cases.append(('gxt',0,ids,[0]*3,[0]*5,leaf_status,fill))
  for kind,chip,ids,q,w,leaf_status,fill in cases:
   results=[]
   for candidate,u in enumerate(machines):
    u.mem_write(0x20000000,bytes([fill])*0x3e000);initial=bytearray(u.mem_read(0x20000000,0x3e000));u.reg_write(UC_ARM_REG_XPSR,0x01000000);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    st=dict(source=candidate,chip=chip,ids=ids,modes=q,mode_index=0,writes=w,write_index=0,leaf_status=leaf_status,events=[],cells={},pointers=[]);states[id(u)]=st
    entry=symbols[{'yhm':'r1_yhm_configure_native','void_adapter':'r1_device_preinitialize_3510c','gxt':'r1_gxt310_self_check'}[kind]] if candidate else 0x50ecc if kind=='gxt' else 0x3510c
    u.emu_start(entry|1,0x20000100,count=10000);assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
    for index,value in st['cells'].items():initial[0x6000+4*index:0x6004+4*index]=struct.pack('<I',value)
    actual=bytes(u.mem_read(0x20000000,0x3e000));assert initial==actual,('nonstack RAM',kind,candidate)
    assert len(set(st['pointers']))<=1
    results.append([st['events'],st['mode_index'],u.reg_read(UC_ARM_REG_R0),hashlib.sha256(actual).hexdigest()])
   expected=int(ids[0]==0x50 and ids[1]==0x50) if kind=='gxt' else 0 if chip==0xa0 else 5
   if results[0]!=results[1] or results[0][2]!=expected:
    fail=dict(kind=kind,chip=chip,ids=ids,modes=q,writes=w,leaf_status=leaf_status,fill=fill,results=results,expected=expected);(OUT/'counterexample.json').write_text(json.dumps(fail,indent=2)+'\n');raise AssertionError(fail)
   counts[kind]+=1;events=results[0][0];callbacks+=len(events);delay_calls+=sum(e[0]==2 for e in events);write_calls+=sum(e[0]==1 for e in events)
   if kind=='gxt':assert [e[0] for e in events]==[6,7,8,9,10,11]
   elif chip==0xa0:assert [e[1] for e in events if e[0]==1]==[[2,1,1],[0,1,0x6a],[1,1,0x4c],[2,1,0xa0],[3,1,2]] and sum(e[0]==2 for e in events)==50
   else:assert not any(e[0] in [1,2] for e in events)
   digest.update(json.dumps([kind,chip,ids,q,w,leaf_status,fill,results[0]],sort_keys=True).encode())
 receipt=dict(comparisons=sum(counts.values()),counts=counts,callback_observations_per_side=callbacks,delay_calls_per_side=delay_calls,write_calls_per_side=write_calls,trace_sha256=digest.hexdigest(),native_yhm_writes_return_values_ignored=True,native_success_delay_fifty_calls_64000=True,failed_chip_has_no_writes_or_delay=True,all_8bit_chip_ids_and_selected_high_values=True,all_8bit_gxt_id_pairs_and_selected_high_values=True,gxt_always_acquires_enables_reads_both_disables_releases=True,write_buffer_reused_and_mutated_by_fixture=True,normalized_write_pointer_private_frame_gate=True,callback_arguments_order_status_state_full_ram_raw_r0_stack_and_callee_integer_checked=True,source_void_adapter_raw_r0_sampled=True,all_leaf_providers_are_named_fixtures=True,actual_delay_body_executed=False,whole_device_graph_executed=False,candidate_native_body_execution_forbidden=True,unicorn_memory_write_hooks_disabled=True,source_constant_data_bytes=120,delay_pointer_is_source_relocation=True,instruction_identity=False,full_raw_abi_verified=False,physical_hardware_verified=False,application_sha256=sha(app),driver_sha256=sha(Path(__file__)),report_sha256=sha(rp),object_sha256=sha(obj),layout=str(layout.relative_to(ROOT)),layout_sha256=sha(layout),limitations=['All chip, write, delay, GXT bus/enable/ID/disable and logging providers are explicit fixtures.','Write data pointer addresses are normalized to typed byte values; raw stack frames and uninitialized padding remain gated.','The older generic yhm2710_configure returns5 on write failure, unlike native; it is not used as this native provider.','Delay pointer is a source function relocation; no raw executable address fallback is admitted.','Full linked device/startup graph, source state/layout, physical timing and byte-identical whole image remain open.'])
 vp.write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
