#!/usr/bin/env python3
"""Native YHM chip read/log/late byte return with scoped callback mutations."""
import hashlib,itertools,json,random,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-yhm-chip-id';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
REGIONS=[('bounds',0x35394,8),('success_ring',0x3539c,32),('success_sdk',0x353bc,24),('error_ring',0x353d4,32),('error_sdk',0x353f4,24)]
CALLS=[('r1_yhm_register_read_native',0x3540c),('r1_structured_log_mode_get',0x914ec),('r1_structured_log_format',0x91638),('nrf_log_frontend_std_0',0x799c0)]
def main():
 vp=OUT/'verification.json';vp.unlink(missing_ok=True);rp=OUT/'report.json';r=json.loads(rp.read_text());obj=OUT/'native_yhm_chip_id.o';assert sha(obj)==r['units'][0]['object_sha256']
 for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';layout=ROOT/'r1/source-config/runtime/native_yhm_chip_id_verification.ld';states={};digest=hashlib.sha256();count=0;callbacks=0;rng=random.Random(0x3530c)
 with tempfile.TemporaryDirectory() as tmp:
  d=Path(tmp);elf=d/'test.elf';subprocess.run(['arm-none-eabi-ld','-T',str(layout),str(obj),'-o',str(elf)],check=True);symbols={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3};sections=[]
  for name,a,n in [('text',0x1000000,None),*REGIONS]:
   p=d/(name+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j','.'+name,'-O','binary',str(elf),str(p)],check=True);data=p.read_bytes();sections.append((a,data))
   if n is not None:assert len(data)==n and data==raw[a-0x27000:a-0x27000+n]
  native={a:i for i,(_,a) in enumerate(CALLS)};compiled={symbols[n]&~1:i for i,(n,_) in enumerate(CALLS)}
  def hook(u,address,size,_):
   st=states[id(u)];index=(compiled if st['source'] else native).get(address)
   if index is None:assert not st['source'] or not 0x27000<=address<0xc4d08;return
   args=[u.reg_read(reg) for reg in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2]]
   if index==0:
    assert args[:2]==[8,1];st['pointer']=args[2];assert u.mem_read(st['pointer'],1)[0]==0
    if st['byte'] is not None:u.mem_write(st['pointer'],bytes([st['byte']]))
    st['value']=st['byte'] or 0;observed=[8,1,0,st['byte']];value=st['status']
   elif index==1:
    value=st['modes'][st['mode_index']];st['mode_index']+=1;observed=[value]
   else:observed=args[:3 if index==2 else 2];value=0x55aa55aa
   if index:
    mutation=st['mutations'][index-1]
    if mutation is not None:u.mem_write(st['pointer'],bytes([mutation]));st['value']=mutation
   st['events'].append([index,observed,value]);st['cell']=(st['cell']+index+1)&0xffffffff;u.mem_write(0x20006000,st['cell'].to_bytes(4,'little'))
   for i,reg in enumerate([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_R12]):u.reg_write(reg,(0xabcdef01+i*0x11111111)&0xffffffff)
   u.reg_write(UC_ARM_REG_R0,value);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  machines=[]
  for candidate in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,raw);u.mem_map(0x1000000,0x10000);u.mem_map(0x20000000,0x40000)
   if candidate:
    for address,data in sections:u.mem_write(address,data)
   u.hook_add(UC_HOOK_CODE,hook);machines.append(u)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11];modes=[list(q) for q in itertools.product(range(8),repeat=3)]+[[rng.getrandbits(32) for _ in range(3)] for _ in range(128)];statuses=[0,1,0xffffffff];mutations=[[None]*3,[0xa0,None,None],[None,0,0xff],[0,0xa0,1]]
  cases=list(itertools.product([None,0,0x50,0xa0,0xa1,0xff],modes,statuses,mutations,[0,0x96]))
  cases.extend(itertools.product(range(256),[[0]*3,[1]*3,[2]*3,[4]*3],statuses,[[None]*3],[0,0x96]))
  for byte,q,status,mut,fill in cases:
   results=[]
   for candidate,u in enumerate(machines):
    u.mem_write(0x20000000,bytes([fill])*0x3e000);initial=bytearray(u.mem_read(0x20000000,0x3e000));u.reg_write(UC_ARM_REG_XPSR,0x01000000);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    st=dict(source=candidate,byte=byte,status=status,modes=q,mode_index=0,mutations=mut,pointer=None,value=None,events=[],cell=int.from_bytes(bytes([fill])*4,'little'));states[id(u)]=st
    u.emu_start((symbols['r1_yhm_chip_id_native'] if candidate else 0x3530c)|1,0x20000100,count=10000);assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
    initial[0x6000:0x6004]=st['cell'].to_bytes(4,'little');actual=bytes(u.mem_read(0x20000000,0x3e000));assert initial==actual;assert u.reg_read(UC_ARM_REG_R0)==st['value']
    results.append([st['events'],st['mode_index'],u.reg_read(UC_ARM_REG_R0),hashlib.sha256(actual).hexdigest()])
   if results[0]!=results[1]:
    fail=dict(byte=byte,modes=q,status=status,mutations=mut,fill=fill,results=results);(OUT/'counterexample.json').write_text(json.dumps(fail,indent=2)+'\n');raise AssertionError(fail)
   count+=1;callbacks+=len(results[0][0]);digest.update(json.dumps([byte,q,status,mut,fill,results[0]],sort_keys=True).encode())
 receipt=dict(comparisons=count,callback_observations_per_side=callbacks,trace_sha256=digest.hexdigest(),read_register8_length1_initial_zero=True,read_status_ignored_and_no_write_result_supported=True,all_byte_ids_and_mode_triples=True,seeded_full_width_modes=True,callback_mutations_of_scoped_read_byte=True,initial_id_selects_log_strings_late_byte_is_returned=True,raw_r0_stack_callee_integer_full_nonstack_ram_and_callback_order_args_checked=True,read_pointer_normalized_private_frame_gate=True,read_and_logging_bodies_are_named_fixtures=True,source_data_bytes=120,actual_source_transport_executed=False,whole_startup_graph_executed=False,candidate_native_body_execution_forbidden=True,unicorn_memory_write_hooks_disabled=True,instruction_identity=False,full_raw_abi_verified=False,physical_hardware_verified=False,application_sha256=sha(app),driver_sha256=sha(Path(__file__)),report_sha256=sha(rp),object_sha256=sha(obj),layout=str(layout.relative_to(ROOT)),layout_sha256=sha(layout),limitations=['Read/log providers are fixtures; read status is ignored and an unwritten byte remains initialized zero.','Callback byte mutations occur while the read byte is live; private pointer/frame addresses are normalized.','Existing source read transport is linked separately but not executed here; full startup, physical bus, source state/layout and image equality remain open.'])
 vp.write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
