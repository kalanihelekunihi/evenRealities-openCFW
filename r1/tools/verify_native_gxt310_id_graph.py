#!/usr/bin/env python3
"""Execute actual source GXT self-check, veneers and shared ID bodies together."""
import hashlib,itertools,json,random,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
from verify_native_gxt310_id import REGIONS,CALLS
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-gxt310-id';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
LEAVES=CALLS+[('r1_gxt310_bus_acquire',0x50f28),('r1_gxt310_enable_pair_native',0x50f9c),('r1_gxt310_disable_pair_native',0x50f88),('r1_gxt310_bus_release',0x50efc)]
def main():
 vp=OUT/'graph-verification.json';vp.unlink(missing_ok=True);rp=BASE/'native-gxt310-id-runtime/report.json';report=json.loads(rp.read_text());obj=rp.parent/'gxt-selfcheck-source.o';assert sha(obj)==report['selfcheck_object_sha256']
 for p,h in report['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();layout=ROOT/'r1/source-config/runtime/native_gxt310_id_graph_verification.ld';rng=random.Random(0x50ecc);states={};digest=hashlib.sha256();count=0;callbacks=0
 with tempfile.TemporaryDirectory() as tmp:
  d=Path(tmp);elf=d/'test.elf';subprocess.run(['arm-none-eabi-ld','-T',str(layout),str(obj),'-o',str(elf)],check=True);syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3};sections=[]
  for name,a,n in [('text',0x1000000,None),*[r for r in REGIONS if r[0]!='bounds']]:
   p=d/(name+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j','.'+name,'-O','binary',str(elf),str(p)],check=True);data=p.read_bytes();sections.append((a,data))
   if n is not None:assert len(data)==n and data==raw[a-0x27000:a-0x27000+n]
  native={a:i for i,(_,a) in enumerate(LEAVES)};compiled={syms[n]&~1:i for i,(n,_) in enumerate(LEAVES)}
  def hook(u,address,size,_):
   st=states[id(u)];index=(compiled if st['source'] else native).get(address)
   if index is None:assert not st['source'] or not 0x27000<=address<0xc4d08;return
   args=[u.reg_read(reg) for reg in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]]
   if index==0:
    i=st['read_index'];assert i<2 and args[0]==[0x90,0x94][i] and args[1]==3 and args[3]==2 and bytes(u.mem_read(args[2],4))==b'\0'*4
    if i:st['late_ids'].append(st['late_value'])
    data=st['data'][i];st['pointer']=args[2]
    if data is not None:u.mem_write(args[2],bytes(data))
    st['packed']=int.from_bytes(u.mem_read(args[2],2),'big');st['late_value']=u.mem_read(args[2],1)[0];st['read_index']+=1;used=[args[0],3,2,data];value=st['statuses'][i]
   elif index==1:value=st['modes'][st['mode_index']];st['mode_index']+=1;used=[value]
   elif index in [2,3]:
    used=args+[struct.unpack('<I',u.mem_read(u.reg_read(UC_ARM_REG_SP),4))[0]] if index==2 else args
    assert used[-1]==st['packed'] and (args[3] if index==2 else args[2])==[0x90,0x94][st['read_index']-1];value=0x55aa55aa
   else:
    if index==6:st['late_ids'].append(st['late_value']);assert len(st['late_ids'])==2
    used=[];value=st['leaf_statuses'][index-4]
   if 1<=index<=3 and st['mutations'][index-1] is not None:
    data=st['mutations'][index-1];u.mem_write(st['pointer'],bytes(data));st['late_value']=data[0]
   st['events'].append([index,used,value]);st['cell']=(st['cell']+index+1)&0xffffffff;u.mem_write(0x20006000,st['cell'].to_bytes(4,'little'))
   for i,reg in enumerate([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_R12]):u.reg_write(reg,(0xabcdef01+i*0x11111111)&0xffffffff)
   u.reg_write(UC_ARM_REG_R0,value);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  machines=[]
  for candidate in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,raw);u.mem_map(0x1000000,0x10000);u.mem_map(0x20000000,0x40000)
   if candidate:
    for a,data in sections:u.mem_write(a,data)
   u.hook_add(UC_HOOK_CODE,hook);machines.append(u)
  modes=[list(q)+list(reversed(q)) for q in itertools.product(range(8),repeat=3)]+[[rng.getrandbits(32) for _ in range(6)] for _ in range(128)];data=[None,[0,0],[0x50,0],[0,0x50],[0xff,0xff]];statuses=[[0,0],[1,0xffffffff]];mutations=[[None]*3,[[0x50,0xaa],None,None],[None,[0,0xbb],[0x50,0xcc]]];cases=[]
  for pair,q,status in itertools.product(itertools.product(data,repeat=2),modes,statuses):cases.append((pair,q,status,mutations[0]))
  for pair,q,status,mut in itertools.product(itertools.product(data,repeat=2),modes[::8],statuses,mutations[1:]):cases.append((pair,q,status,mut))
  for _ in range(256):
   pair=[[rng.randrange(256),rng.randrange(256)] for _ in range(2)]
   for q,status,mut in itertools.product([[0]*6,[1]*6,[2]*6,[4]*6],statuses,mutations[1:]):cases.append((pair,q,status,mut))
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  for pair,q,status,mut in cases:
   leaf_statuses=[rng.getrandbits(32) for _ in range(4)];results=[]
   for candidate,u in enumerate(machines):
    u.mem_write(0x20000000,b'\x96'*0x3e000);initial=bytearray(u.mem_read(0x20000000,0x3e000));u.reg_write(UC_ARM_REG_XPSR,0x01000000);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    st=dict(source=candidate,data=pair,statuses=status,modes=q,mode_index=0,mutations=mut,leaf_statuses=leaf_statuses,read_index=0,pointer=None,packed=None,late_value=None,late_ids=[],events=[],cell=0x96969696);states[id(u)]=st
    u.emu_start((syms['r1_gxt310_self_check'] if candidate else 0x50ecc)|1,0x20000100,count=20000);assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
    initial[0x6000:0x6004]=st['cell'].to_bytes(4,'little');actual=bytes(u.mem_read(0x20000000,0x3e000));assert initial==actual;expected=int(st['late_ids']==[0x50,0x50]);assert u.reg_read(UC_ARM_REG_R0)==expected
    order=[e[0] for e in st['events'] if e[0] in [0,4,5,6,7]];assert order==[4,5,0,0,6,7]
    results.append([st['events'],st['mode_index'],st['late_ids'],u.reg_read(UC_ARM_REG_R0),hashlib.sha256(actual).hexdigest()])
   if results[0]!=results[1]:
    fail=dict(pair=pair,modes=q,status=status,mutations=mut,leaf_statuses=leaf_statuses,results=results);(OUT/'graph-counterexample.json').write_text(json.dumps(fail,indent=2)+'\n');raise AssertionError(fail)
   count+=1;callbacks+=len(results[0][0]);digest.update(json.dumps([pair,q,status,mut,leaf_statuses,results[0]],sort_keys=True).encode())
 r=dict(comparisons=count,callback_observations_per_side=callbacks,trace_sha256=digest.hexdigest(),actual_source_selfcheck_both_veneers_and_shared_reader=True,id_providers_are_source_not_fixtures=True,entire_private_word_four_bytes_initial_zero=True,folded_log_bounds_not_selected_graph_data=True,selected_graph_constant_data_bytes=92,bus_enable_disable_read_and_logging_are_fixtures=True,initial_id_log_snapshot_and_late_return_mutations=True,cleanup_order_and_both_reads_checked=True,raw_r0_stack_callee_integer_full_observed_nonstack_ram_and_typed_callback_args_checked=True,read_pointers_private_frame_normalized=True,candidate_native_body_execution_forbidden=True,unicorn_memory_write_hooks_disabled=True,whole_startup_graph_executed=False,physical_sensor_verified=False,instruction_identity=False,application_sha256=sha(app),driver_sha256=sha(Path(__file__)),imported_driver_sha256=sha(ROOT/'r1/tools/verify_native_gxt310_id.py'),runtime_report_sha256=sha(rp),object_sha256=sha(obj),layout=str(layout.relative_to(ROOT)),layout_sha256=sha(layout),limitations=['Source self-check and ID providers execute together; other leaves are named fixtures.','No physical read, power sequencing, full startup, private frame or whole-image identity proof.'])
 vp.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
if __name__=='__main__':main()
