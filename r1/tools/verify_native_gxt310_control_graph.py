#!/usr/bin/env python3
"""Source GXT cache/bus/request/mode/IDs/self-check against native full control flow."""
import hashlib,itertools,json,random,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-gxt310-mode';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
LEAVES=[('r1_stock_registry_find',0x85ce0),('r1_stock_dispatch_08',0x85d1a),('r1_stock_dispatch_0c',0x85cba),('r1_stock_dispatch_10',0x85d2c),('r1_stock_dispatch_14',0x85da8),('r1_structured_log_mode_get',0x914ec),('r1_structured_log_format',0x91638),('nrf_log_frontend_std_0',0x799c0),('nrf_log_frontend_std_1',0x799c8),('nrf_log_frontend_std_2',0x799d6)]
REGIONS=[('mode_error_ring',0x6f6b8,64),('mode_error_sdk',0x6f700,56),('pair0_ring',0x51030,44),('pair0_sdk',0x5105c,40),('pair2_ring',0x51084,44),('pair2_sdk',0x510b0,40),('id_ring',0x6f59c,48),('id_sdk',0x6f5d4,44),('name',0x50f20,8)]
def main():
 vp=OUT/'graph-verification.json';vp.unlink(missing_ok=True);rp=BASE/'native-gxt310-mode-runtime/report.json';r=json.loads(rp.read_text());obj=rp.parent/'gxt-control-source.o';assert sha(obj)==r['control_object_sha256']
 for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';layout=ROOT/'r1/source-config/runtime/native_gxt310_control_graph_verification.ld';states={};rng=random.Random(0x51025);digest=hashlib.sha256();count=0;callbacks=0;raw_pointer_equal=True;pointer_examples=[]
 def normalized(data):
  b=bytearray(data)
  for offset,token in [(8,0xfeed0001),(16,0xfeed0002)]:
   pointer=struct.unpack_from('<I',b,offset)[0]
   if 0x2003e000<=pointer<0x2003f000:struct.pack_into('<I',b,offset,token)
  return bytes(b)
 with tempfile.TemporaryDirectory() as tmp:
  d=Path(tmp);elf=d/'test.elf';subprocess.run(['arm-none-eabi-ld','-T',str(layout),str(obj),'-o',str(elf)],check=True);syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3};assert syms['r1_gxt310_i2c2_state']==0x200076f8;sections=[]
  for name,a,n in [('text',0x1000000,None),*REGIONS]:
   p=d/(name+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j','.'+name,'-O','binary',str(elf),str(p)],check=True);data=p.read_bytes();sections.append((a,data))
   if n is not None:assert len(data)==n and data==raw[a-0x27000:a-0x27000+n]
  state_file=d/'state.bin';subprocess.run(['arm-none-eabi-objcopy','-j','.r1.gxt.bus.state','-O','binary',str(obj),str(state_file)],check=True);initial_state=state_file.read_bytes();assert initial_state.hex()=='000000001200000000000000010000000000000001000000'
  native={a:i for i,(_,a) in enumerate(LEAVES)};compiled={syms[n]&~1:i for i,(n,_) in enumerate(LEAVES)}
  def hook(u,address,size,_):
   st=states[id(u)];index=(compiled if st['source'] else native).get(address)
   if index is None:assert not st['source'] or not 0x27000<=address<0xc4d08;return
   args=[u.reg_read(reg) for reg in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];record=bytes(u.mem_read(0x200076f8,24));observed=[]
   if index==0:assert args[0]==0x50f20;observed=[args[0]];value=st['lookup']
   elif index in [1,2]:observed=[args[0]];value=1 if args[0]==0 else 0
   elif index in [3,4]:
    assert args==[struct.unpack_from('<I',record)[0],0,0x200076fc,0];device=args[0];address_byte=record[4];reg=struct.unpack_from('<H',record,6)[0];observed=args+[normalized(record).hex()]
    if index==4:
     i=st['write_index'];assert i<4 and address_byte==[0x90,0x94,0x90,0x94][i] and reg==1 and struct.unpack_from('<H',record,12)[0]==2;pointer=struct.unpack_from('<I',record,8)[0];word=struct.unpack('<I',u.mem_read(pointer,4))[0];assert word==(0xc200 if i<2 else 0xc201);observed.append(word);value=st['writes'][i] if device else 1;st['write_index']+=1
    else:
     i=st['read_index'];assert i<2 and address_byte==[0x90,0x94][i] and reg==3 and struct.unpack_from('<H',record,20)[0]==2;pointer=struct.unpack_from('<I',record,16)[0];assert bytes(u.mem_read(pointer,4))==b'\0'*4
     data=st['data'][i]
     if device and data is not None:u.mem_write(pointer,bytes(data))
     observed.append(None if data is None or not device else data);value=st['read_status'][i] if device else 1;st['ids'].append(u.mem_read(pointer,1)[0]);st['read_index']+=1
   elif index==5:value=st['modes'][st['mode_index']%len(st['modes'])];st['mode_index']+=1;observed=[value]
   elif index==6:
    arity=5 if args[0]==0xc800000 else 4 if args[0]==0x04400000 else 3;observed=args[:min(arity,4)]
    if arity==5:observed.append(struct.unpack('<I',u.mem_read(u.reg_read(UC_ARM_REG_SP),4))[0])
    value=0x55aa55aa
   else:observed=args[:index-5];value=0x55aa55aa
   st['events'].append([index,observed,value]);st['cell']=(st['cell']+index+1)&0xffffffff;u.mem_write(0x20006000,st['cell'].to_bytes(4,'little'))
   for i,reg in enumerate([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_R12]):u.reg_write(reg,(0xabcdef01+i*0x11111111)&0xffffffff)
   u.reg_write(UC_ARM_REG_R0,value);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  machines=[]
  for candidate in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,raw);u.mem_map(0x1000000,0x10000);u.mem_map(0x20000000,0x40000)
   if candidate:
    for a,data in sections:u.mem_write(a,data)
   u.hook_add(UC_HOOK_CODE,hook);machines.append(u)
  modes=[[v]*64 for v in [0,1,2,4,7]]+[[rng.getrandbits(32) for _ in range(64)] for _ in range(4)];data=[None,[0,0],[0x50,0],[0,0x50],[0xff,0xff]];write_patterns=[[0]*4,[1]*4]+[[int(i==bad) for i in range(4)] for bad in range(4)]+[[rng.getrandbits(32) for _ in range(4)] for _ in range(4)];read_statuses=[[0,0],[1,0xffffffff]];handles=[(0,0),(0,0x20003000),(0x20003000,0)];cases=list(itertools.product(itertools.product(data,repeat=2),write_patterns,read_statuses,modes,handles))
  for _ in range(128):
   pair=[[rng.randrange(256),rng.randrange(256)] for _ in range(2)]
   for writes,read_status,q in itertools.product(write_patterns[:6],read_statuses,modes[:2]):cases.append((pair,writes,read_status,q,handles[1]))
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  for pair,writes,read_status,q,(handle,lookup) in cases:
   results=[];pointer_pairs=[]
   for candidate,u in enumerate(machines):
    u.mem_write(0x20000000,b'\x96'*0x3e000);u.mem_write(0x200076f8,initial_state);u.mem_write(0x200076f8,struct.pack('<I',handle));st=dict(source=candidate,data=pair,writes=writes,read_status=read_status,modes=q,lookup=lookup,mode_index=0,write_index=0,read_index=0,ids=[],events=[],cell=0x96969696);states[id(u)]=st;returns=[]
    for native_entry,source_entry in [(0x50f08,'r1_i2c2_handle_cache'),(0x50ecc,'r1_gxt310_self_check')]:
     u.reg_write(UC_ARM_REG_XPSR,0x01000000);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
     for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
     u.emu_start((syms[source_entry] if candidate else native_entry)|1,0x20000100,count=100000);assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)];returns.append(u.reg_read(UC_ARM_REG_R0))
    assert st['write_index']==4 and st['read_index']==2 and returns[-1]==int(st['ids']==[0x50,0x50]);order=[e[0] for e in st['events'] if e[0] in [1,2,3,4]];assert order==[1,4,4,3,3,4,4,2]
    actual=bytearray(u.mem_read(0x20000000,0x3e000));record=bytes(actual[0x76f8:0x7710]);pointer_pairs.append([struct.unpack_from('<I',record,o)[0] for o in [8,16]]);actual[0x76f8:0x7710]=normalized(record);results.append([st['events'],st['mode_index'],st['ids'],returns,hashlib.sha256(actual).hexdigest()])
   raw_pointer_equal &= pointer_pairs[0]==pointer_pairs[1]
   if pointer_pairs[0]!=pointer_pairs[1] and len(pointer_examples)<3:pointer_examples.append(dict(case_index=count,pair=pair,writes=writes,read_status=read_status,handle=handle,lookup=lookup,native_write_read_pointers=pointer_pairs[0],source_write_read_pointers=pointer_pairs[1]))
   if results[0]!=results[1]:
    fail=dict(pair=pair,writes=writes,read_status=read_status,modes=q,handle=handle,lookup=lookup,raw_pointers=pointer_pairs,results=results);(OUT/'graph-counterexample.json').write_text(json.dumps(fail,indent=2)+'\n');raise AssertionError({k:v for k,v in fail.items() if k!='results'})
   count+=1;callbacks+=len(results[0][0]);digest.update(json.dumps([pair,writes,read_status,q,handle,lookup,results[0]],sort_keys=True).encode())
 r=dict(comparisons=count,callback_observations_per_side=callbacks,trace_sha256=digest.hexdigest(),actual_source_cache_selfcheck_bus_requests_mode_pair_controls_channel_veneers_and_ids=True,only_registry_and_logging_are_named_fixtures=True,all_four_mode_writes_both_reads_and_cleanup_order_checked=True,full_four_byte_mode_words_and_zero_read_words_checked=True,cold_c_state_used=True,registry_null_device_status_fixture_is_one=True,raw_r0_callee_integer_stack_and_typed_callback_args_checked=True,full_observed_nonstack_ram_compared_with_two_pointer_words_normalized=True,normalized_pointer_fields=['state+8 write_pointer','state+16 read_pointer'],raw_persistent_pointer_values_equal=raw_pointer_equal,raw_persistent_pointer_counterexamples=pointer_examples,source_selected_strings_and_name_bytes=388,source_state_bytes=24,candidate_native_body_execution_forbidden=True,unicorn_memory_write_hooks_disabled=True,whole_startup_graph_executed=False,physical_sensor_verified=False,instruction_identity=False,full_raw_abi_verified=False,application_sha256=sha(app),driver_sha256=sha(Path(__file__)),runtime_report_sha256=sha(rp),object_sha256=sha(obj),layout=str(layout.relative_to(ROOT)),layout_sha256=sha(layout),limitations=['Registry lookup/dispatch and logger bodies are fixtures; all intervening GXT providers execute source.','Two persistent request-pointer words refer to native/source private stack frames and are explicitly normalized after their typed buffer effects are checked.','Raw persistent pointer equality, private stack frames, full startup, physical I2C/sensors and byte-identical firmware remain unproven.'])
 vp.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
if __name__=='__main__':main()
