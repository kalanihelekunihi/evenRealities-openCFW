#!/usr/bin/env python3
"""Native GXT ID snapshot/log/late low-byte return plus both channel veneers."""
import hashlib,itertools,json,random,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-gxt310-id';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
REGIONS=[('ring',0x6f59c,48),('bounds',0x6f5cc,8),('sdk',0x6f5d4,44)]
CALLS=[('r1_gxt310_register_read_native',0x6f640),('r1_structured_log_mode_get',0x914ec),('r1_structured_log_format',0x91638),('nrf_log_frontend_std_2',0x799d6)]
def main():
 vp=OUT/'verification.json';vp.unlink(missing_ok=True);rp=OUT/'report.json';r=json.loads(rp.read_text());obj=OUT/'native_gxt310_id.o';assert sha(obj)==r['units'][0]['object_sha256']
 for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';layout=ROOT/'r1/source-config/runtime/native_gxt310_id_verification.ld';states={};digest=hashlib.sha256();counts={'shared':0,'channel0':0,'channel2':0};callbacks=0;rng=random.Random(0x6f53c)
 with tempfile.TemporaryDirectory() as tmp:
  d=Path(tmp);elf=d/'test.elf';subprocess.run(['arm-none-eabi-ld','-T',str(layout),str(obj),'-o',str(elf)],check=True);symbols={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3};sections=[]
  for name,a,n in [('text',0x1000000,None),*REGIONS]:
   p=d/(name+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j','.'+name,'-O','binary',str(elf),str(p)],check=True);data=p.read_bytes();sections.append((a,data))
   if n is not None:assert len(data)==n and data==raw[a-0x27000:a-0x27000+n]
  native={a:i for i,(_,a) in enumerate(CALLS)};compiled={symbols[n]&~1:i for i,(n,_) in enumerate(CALLS)}
  def hook(u,address,size,_):
   st=states[id(u)];index=(compiled if st['source'] else native).get(address)
   if index is None:assert not st['source'] or not 0x27000<=address<0xc4d08;return
   args=[u.reg_read(reg) for reg in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]]
   if index==0:
    assert args[0]==st['address'] and args[1]==3 and args[3]==2;st['pointer']=args[2];assert bytes(u.mem_read(args[2],4))==b'\0'*4
    if st['data'] is not None:u.mem_write(args[2],bytes(st['data']))
    st['packed']=int.from_bytes(u.mem_read(args[2],2),'big');observed=[args[0],3,2,None if st['data'] is None else list(st['data'])];value=st['status']
   elif index==1:value=st['modes'][st['mode_index']];st['mode_index']+=1;observed=[value]
   elif index==2:
    packed=struct.unpack('<I',u.mem_read(u.reg_read(UC_ARM_REG_SP),4))[0];assert args[0]==0xc800000 and args[3]==st['address'] and packed==st['packed'];observed=args+[packed];value=0x55aa55aa
   else:assert args[2]==st['address'] and args[3]==st['packed'];observed=args;value=0x55aa55aa
   if index and st['mutations'][index-1] is not None:u.mem_write(st['pointer'],bytes(st['mutations'][index-1]))
   st['events'].append([index,observed,value]);st['cell']=(st['cell']+index+1)&0xffffffff;u.mem_write(0x20006000,st['cell'].to_bytes(4,'little'))
   for i,reg in enumerate([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_R12]):u.reg_write(reg,(0xabcdef01+i*0x11111111)&0xffffffff)
   u.reg_write(UC_ARM_REG_R0,value);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  machines=[]
  for candidate in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,raw);u.mem_map(0x1000000,0x10000);u.mem_map(0x20000000,0x40000)
   if candidate:
    for address,data in sections:u.mem_write(address,data)
   u.hook_add(UC_HOOK_CODE,hook);machines.append(u)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11];modes=[list(q) for q in itertools.product(range(8),repeat=3)]+[[rng.getrandbits(32) for _ in range(3)] for _ in range(128)];statuses=[0,1,0xffffffff];mutations=[[None]*3,[[0xa0,0x55],None,None],[None,[0,0xff],[1,2]]];cases=[]
  for word in range(65536):cases.append(('shared',0x90,list(word.to_bytes(2,'big')),modes[word%len(modes)],statuses[word%3],mutations[0],0x96))
  for kind in ['shared','channel0','channel2']:
   selected_modes=modes if kind=='shared' else modes[::8]
   for i,(data,q,status,mut,fill) in enumerate(itertools.product([None,[0,0],[0x50,0],[0,0x50],[0xff,0xff]],selected_modes,statuses,mutations,[0,0x96])):
    address=[0,1,0x90,0x94,0x10090,0xffffffff][i%6] if kind=='shared' else 0x90 if kind=='channel0' else 0x94
    cases.append((kind,address,data,q,status,mut,fill))
  for kind,address,data,q,status,mut,fill in cases:
   results=[]
   for candidate,u in enumerate(machines):
    u.mem_write(0x20000000,bytes([fill])*0x3e000);initial=bytearray(u.mem_read(0x20000000,0x3e000));u.reg_write(UC_ARM_REG_XPSR,0x01000000);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101);u.reg_write(UC_ARM_REG_R0,address)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    st=dict(source=candidate,address=address,data=data,status=status,modes=q,mode_index=0,mutations=mut,pointer=None,packed=None,events=[],cell=int.from_bytes(bytes([fill])*4,'little'));states[id(u)]=st
    entry=symbols[{'shared':'r1_gxt310_chip_id_native','channel0':'r1_gxt310_chip_id_channel0','channel2':'r1_gxt310_chip_id_channel2'}[kind]] if candidate else {'shared':0x6f53c,'channel0':0x6f812,'channel2':0x6f82c}[kind]
    u.emu_start(entry|1,0x20000100,count=10000);assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
    initial[0x6000:0x6004]=st['cell'].to_bytes(4,'little');actual=bytes(u.mem_read(0x20000000,0x3e000));assert initial==actual;assert u.reg_read(UC_ARM_REG_R0)==u.mem_read(st['pointer'],1)[0]
    results.append([st['events'],st['mode_index'],u.reg_read(UC_ARM_REG_R0),hashlib.sha256(actual).hexdigest()])
   if results[0]!=results[1]:
    fail=dict(kind=kind,address=address,data=data,modes=q,status=status,mutations=mut,fill=fill,results=results);(OUT/'counterexample.json').write_text(json.dumps(fail,indent=2)+'\n');raise AssertionError(fail)
   counts[kind]+=1;callbacks+=len(results[0][0]);digest.update(json.dumps([kind,address,data,q,status,mut,fill,results[0]],sort_keys=True).encode())
 receipt=dict(comparisons=sum(counts.values()),counts=counts,callback_observations_per_side=callbacks,trace_sha256=digest.hexdigest(),all_65536_read_words=True,shared_and_both_channel_veneers_executed=True,read_reg3_length2_initial_zero=True,entire_private_word_four_bytes_initial_zero=True,read_result_ignored_and_no_write_result_supported=True,full_width_addresses_and_seeded_modes=True,scoped_callback_buffer_mutations=True,log_value_is_initial_big_endian_16bit_snapshot=True,ring_fifth_stack_argument_checked=True,return_reloads_late_first_byte=True,raw_r0_stack_callee_integer_full_observed_nonstack_ram_and_callback_args_order_checked=True,private_read_pointer_normalized=True,read_and_logging_bodies_are_fixtures=True,source_data_bytes=100,candidate_native_body_execution_forbidden=True,unicorn_memory_write_hooks_disabled=True,actual_source_read_transport_executed=False,whole_startup_graph_executed=False,instruction_identity=False,full_raw_abi_verified=False,physical_hardware_verified=False,application_sha256=sha(app),driver_sha256=sha(Path(__file__)),report_sha256=sha(rp),object_sha256=sha(obj),layout=str(layout.relative_to(ROOT)),layout_sha256=sha(layout),limitations=['Register read and logger bodies are fixtures; no actual sensor or bus execution is proven.','Source and native initialize a four-byte private word; private frame addresses, saved registers and padding outside that word remain open.','Read pointers are normalized; typed byte effects, log snapshot/stack argument, late return and sampled boundary registers/RAM match.','Both veneers call source shared code; complete startup, source initialization/layout, original compiler and whole-image equality remain open.'])
 vp.write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
