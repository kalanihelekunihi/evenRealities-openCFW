#!/usr/bin/env python3
"""Native DFU entry/shared tail against upstream entry plus recovered source tail."""
import hashlib,itertools,json,random,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-dfu-svci-init';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
PROVIDERS=[('nrf_dfu_svci_vector_table_set',0x78590),('r1_structured_log_mode_get',0x914ec),('r1_structured_log_format',0x91638),('nrf_log_frontend_std_0',0x799c0),('nrf_log_frontend_std_1',0x799c8)]
REGIONS=[('app_start',0x787f0,4),('info_ring',0x787f4,48),('bounds',0x78824,8),('info_sdk',0x7882c,44),('error_ring',0x78858,60),('error_sdk',0x78894,52)]
def main():
 vp=OUT/'verification.json';vp.unlink(missing_ok=True);report=OUT/'report.json';r=json.loads(report.read_text());obj=OUT/'native-dfu-svci-init.o';assert sha(obj)==r['linked_sha256']
 for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';layout=ROOT/'r1/source-config/runtime/native_dfu_svci_verification.ld';states={};counts={'entry':0,'restore':0};observations=0;svc_counts={0:0,19:0};digest=hashlib.sha256();rng=random.Random(0x52018)
 with tempfile.TemporaryDirectory() as tmp:
  d=Path(tmp);elf=d/'test.elf';subprocess.run(['arm-none-eabi-ld','-T',str(layout),str(obj),'-o',str(elf)],check=True)
  symbols={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3};assert symbols['nrf_dfu_set_adv_name_svci_async_def']==0x2002c12c
  sections=[]
  for name,a,n in [('text',0x1000000,None),*REGIONS]:
   b=d/(name+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j','.'+name,'-O','binary',str(elf),str(b)],check=True);content=b.read_bytes();sections.append((a,content))
   if n is not None:assert len(content)==n and content==raw[a-0x27000:a-0x27000+n],name
  native={a:i for i,(_,a) in enumerate(PROVIDERS)};compiled={symbols[n]&~1:i for i,(n,_) in enumerate(PROVIDERS)}
  def poison(u,value,keep=()):
   for i,reg in enumerate([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_R12]):
    if reg not in keep:u.reg_write(reg,(value+i*0x11111111)&0xffffffff)
  def hook(u,address,size,_):
   st=states[id(u)];index=(compiled if st['source'] else native).get(address)
   if index is not None:
    regs=[u.reg_read(reg) for reg in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]]
    if index==0:st['events'].append(['set']);value=st['status'][0]
    elif index==1:
     i=st['mode_index'];assert i<len(st['modes']);value=st['modes'][i];st['mode_index']+=1;st['events'].append(['mode',value])
    else:
     arity=4 if index==2 and regs[0]==0xc400000 else 3 if index in [2,4] else 2
     st['events'].append(['log',index,regs[:arity]]);value=0x55aa55aa
    poison(u,0xabcdef01);u.reg_write(UC_ARM_REG_R0,value);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR));return
   assert not st['source'] or not 0x27000<=address<0xc4d08
   opcode=struct.unpack('<H',u.mem_read(address,2))[0]
   if opcode&0xff00==0xdf00:
    imm=opcode&255
    if imm==0:
     pointer=u.reg_read(UC_ARM_REG_R0);assert pointer==0x2002c12c and u.reg_read(UC_ARM_REG_R12)==3
     before=bytes(u.mem_read(pointer,12));st['events'].append(['svc0',pointer,3,before.hex()]);u.mem_write(pointer,st['mutation']);value=st['status'][1]
    elif imm==19:
     base=u.reg_read(UC_ARM_REG_R0);assert base==0x27000;st['events'].append(['svc19',base]);value=st['status'][2]
    else:raise AssertionError(imm)
    poison(u,0x13579bdf);u.reg_write(UC_ARM_REG_R0,value);u.reg_write(UC_ARM_REG_PC,(address+2)|1)
  machines=[]
  for candidate in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,raw);u.mem_map(0x1000000,0x10000);u.mem_map(0x20000000,0x40000)
   if candidate:
    for address,data in sections:u.mem_write(address,data)
   u.hook_add(UC_HOOK_CODE,hook);machines.append(u)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11];statuses=[0,1,4,0x12345678,0x80000000,0xffffffff]
  mode_queues=[list(q)+list(reversed(q)) for q in itertools.product(range(8),repeat=3)]+[[rng.randrange(8) for _ in range(6)] for _ in range(128)]
  cases=[]
  # Exhaustive first/error logging triples plus independent seeded six-read queues.
  for q,status,fill in itertools.product(mode_queues,statuses,[0,0x96]):cases.append(('restore',(0,0,status),q,fill))
  # Exhaustive early/provider error combinations, with deterministic mode variation.
  for i,status in enumerate(itertools.product(statuses,repeat=3)):
   for q in [mode_queues[(i*13)%len(mode_queues)], [0]*6,[7]*6]:
    for fill in [0,0x96]:cases.append(('entry',status,q,fill))
  # Every logging queue also runs through the reused upstream entry and SVC bridge.
  for q,status in itertools.product(mode_queues,[0,1,0xffffffff]):cases.append(('entry',(0,0,status),q,0x96))
  for kind,status,modes,fill in cases:
   mutation=bytes(rng.randrange(256) for _ in range(12));results=[]
   for candidate,u in enumerate(machines):
    u.mem_write(0x20000000,bytes([fill])*0x3e000);initial=bytearray(u.mem_read(0x20000000,0x3e000));u.reg_write(UC_ARM_REG_XPSR,0x01000000);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    poison(u,0x11223344);st=dict(source=candidate,status=status,modes=modes,mode_index=0,events=[],mutation=mutation);states[id(u)]=st
    entry=symbols['ble_dfu_buttonless_async_svci_init' if kind=='entry' else 'nrf_dfu_svci_vector_table_unset'] if candidate else 0x52018 if kind=='entry' else 0x7876c
    try:u.emu_start(entry|1,0x20000100,count=10000)
    except Exception as err:raise RuntimeError((kind,status,modes,candidate,hex(u.reg_read(UC_ARM_REG_PC)))) from err
    assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
    svc0=any(e[0]=='svc0' for e in st['events'])
    if svc0:initial[0x2c12c:0x2c138]=mutation
    actual=bytes(u.mem_read(0x20000000,0x3e000));assert initial==actual,('unexpected RAM writes',kind,status,candidate)
    result=[st['events'],st['mode_index'],u.reg_read(UC_ARM_REG_R0),hashlib.sha256(actual).hexdigest()];results.append(result)
   expected=status[0] if kind=='entry' and status[0] else status[1] if kind=='entry' and status[1] else status[2]
   if results[0]!=results[1] or results[0][2]!=expected:
    fail=dict(kind=kind,status=status,modes=modes,fill=fill,results=results,expected=expected);(OUT/'counterexample.json').write_text(json.dumps(fail,indent=2)+'\n');raise AssertionError(fail)
   counts[kind]+=1;observations+=len(results[0][0]);svc_counts[0]+=sum(e[0]=='svc0' for e in results[0][0]);svc_counts[19]+=sum(e[0]=='svc19' for e in results[0][0]);digest.update(json.dumps([kind,status,modes,fill,mutation.hex(),results[0]],sort_keys=True).encode())
 receipt=dict(comparisons=sum(counts.values()),counts=counts,callback_observations_per_side=observations,supervisor_calls_per_side=svc_counts,trace_sha256=digest.hexdigest(),upstream_entry_and_source_restore_executed=True,actual_svc0_bridge_executed=True,supervisor_behavior_is_fixture=True,vector_set_and_logging_bodies_are_named_fixtures=True,all_entry_raw_r0_compared=True,callee_integer_stack_and_full_nonstack_ram_checked=True,all_three_mode_values_exhaustive_per_log_group=True,independent_seeded_six_mode_queues=True,early_error_and_state_mutation_paths=True,source_constant_data_bytes=sum(n for _,_,n in REGIONS),source_data_at_native_verification_addresses=True,candidate_native_body_execution_forbidden=True,unicorn_memory_write_hooks_disabled=True,instruction_identity=False,full_raw_abi_verified=False,physical_svc_verified=False,application_sha256=sha(app),driver_sha256=sha(Path(__file__)),report_sha256=sha(report),object_sha256=sha(obj),layout=str(layout.relative_to(ROOT)),layout_sha256=sha(layout),limitations=['SVC0/SVC19 handlers, bootloader vector setter and logging are explicit fixtures, not source or physical provider proof.','Native verification data/state addresses do not establish whole-image linker placement or startup ownership.','Typed supervisor args, log calls, raw R0/callee/SP and full RAM match; other raw scratch/APSR/private frame and original instructions remain open.'])
 vp.write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
