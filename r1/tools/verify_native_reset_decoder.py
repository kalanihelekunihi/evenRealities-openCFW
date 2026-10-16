#!/usr/bin/env python3
"""Native reset mask/diagnostic/log order, fresh value reloads and raw seed bridge."""
import hashlib,itertools,json,random,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-reset-decoder';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
CALLS=[('r1_structured_log_mode_get',0x914ec),('r1_structured_log_format',0x91638),('nrf_log_frontend_std_0',0x799c0),('nrf_log_frontend_std_1',0x799c8),('r1_reset_trace_program_counter_read',0x7ef4c),('r1_reset_trace_return_address_read',0x7ee7c),('r1_reset_trace_byte_read',0x7edfc)]
def main():
 vp=OUT/'verification.json';vp.unlink(missing_ok=True);rp=OUT/'report.json';report=json.loads(rp.read_text());obj=OUT/'native_reset_decoder.o';assert sha(obj)==report['units'][0]['object_sha256']
 for p,h in report['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw_bytes=app.read_bytes();assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';layout=ROOT/'r1/source-config/runtime/reset-decoder/verification.ld';config=ROOT/'r1/source-config/runtime/reset-decoder/data-regions.json';regions=json.loads(config.read_text());states={};rng=random.Random(0x8198c);digest=hashlib.sha256();count=0;callbacks=0;diagnostics=0;byte_calls=0
 with tempfile.TemporaryDirectory() as tmp:
  d=Path(tmp);elf=d/'test.elf';subprocess.run(['arm-none-eabi-ld','-T',str(layout),str(obj),'-o',str(elf)],check=True);syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3};sections=[]
  for name,a,n in [('text',0x1000000,None),*regions]:
   p=d/(name+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j','.'+name,'-O','binary',str(elf),str(p)],check=True);data=p.read_bytes();sections.append((a,data))
   if n is not None:assert len(data)==n and data==raw_bytes[a-0x27000:a-0x27000+n],name
  native={a:i for i,(_,a) in enumerate(CALLS)};compiled={syms[n]&~1:i for i,(n,_) in enumerate(CALLS)}
  def mutate(u,st):
   if st['mutation']==1:
    for name in ['pc','lr']:
     if name in st['pointers']:
      pointer=st['pointers'][name];value=struct.unpack('<I',u.mem_read(pointer,4))[0];u.mem_write(pointer,struct.pack('<I',value^0x01020304))
   if st['mutation'] in [2,3] and 'tag' in st['pointers']:u.mem_write(st['pointers']['tag'],bytes([2 if st['mutation']==2 else 0]))
   if st['mutation']==3 and 'caller' in st['pointers']:u.mem_write(st['pointers']['caller'],b'\xa5')
  def hook(u,address,size,_):
   st=states[id(u)];index=(compiled if st['source'] else native).get(address)
   if index is None:assert not st['source'] or not 0x27000<=address<0xc4d08;return
   args=[u.reg_read(reg) for reg in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]]
   if index==0:value=st['modes'][st['mode_index']%len(st['modes'])];st['mode_index']+=1;used=[value]
   elif index in [1,2,3]:used=args[:4 if index==1 and args[0]==0xc400000 else 3 if index in [1,3] else 2];value=0x55aa55aa
   else:
    name='pc' if index==4 else 'lr' if index==5 else 'tag' if args[0]==0 else 'caller';pointer=args[0] if index in [4,5] else args[1]
    initial=struct.unpack('<I',u.mem_read(pointer,4))[0];expected=0 if name in ['pc','lr'] else st['raw']&0xffffff00 if name=='tag' else st['incoming_r3']&0xffffff00;assert initial==expected,(name,hex(initial),hex(expected))
    if name=='caller':assert args[0]==1 and 'tag' in st['pointers'] and u.mem_read(st['pointers']['tag'],1)[0]==2
    st['pointers'][name]=pointer;which=['pc','lr','tag','caller'].index(name);value=st['statuses'][which];datum=st['data'][which]
    if datum is not None:u.mem_write(pointer,struct.pack('<I',datum) if which<2 else bytes([datum]))
    used=[name,initial,datum]
   if index<4:mutate(u,st)
   st['events'].append([index,used,value]);st['cell']=(st['cell']+index+1)&0xffffffff;u.mem_write(0x20006000,st['cell'].to_bytes(4,'little'))
   for i,reg in enumerate([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_R12]):u.reg_write(reg,(0xabcdef01+i*0x11111111)&0xffffffff)
   u.reg_write(UC_ARM_REG_R0,value);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  machines=[]
  for candidate in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,raw_bytes);u.mem_map(0x1000000,0x20000);u.mem_map(0x20000000,0x40000)
   if candidate:
    for a,data in sections:u.mem_write(a,data)
   u.hook_add(UC_HOOK_CODE,hook);machines.append(u)
  flags=[sum((1<<bit) for j,bit in enumerate([0,1,2,3,16,17,18]) if mask&(1<<j)) for mask in range(128)];uniform=[[v]*64 for v in range(8)];queues=uniform+[[rng.randrange(8) for _ in range(64)] for _ in range(4)]+[[rng.getrandbits(32) for _ in range(64)] for _ in range(4)]
  profiles=[([0]*4,[None]*4),([1]*4,[0x12345678,0x9abcdef0,0,0x42]),([1]*4,[0x12345678,0x9abcdef0,2,0x42]),([0,1,1,1],[None,0xffffffff,2,0xff]),([1,0,1,1],[0x80000000,None,2,0]),([1,1,0,1],[1,2,2,3]),([1,1,1,0],[1,2,2,None]),([0xffffffff]*4,[0xffffffff,0xffffffff,2,0xff])];cases=[]
  for raw,profile,q,fill in itertools.product(flags,profiles,queues,[0,0x96]):cases.append((raw,*profile,q,0,fill))
  unknown=[1<<b for b in range(32) if b not in [0,1,2,3,16,17,18]]+[rng.getrandbits(32) for _ in range(32)]+[0xffffffff]
  for raw,profile,q,fill in itertools.product(unknown,profiles,uniform[:4],[0,0x96]):cases.append((raw,*profile,q,0,fill))
  values=[(0,0),(1,0xffffffff),(0xffffffff,0x80000000),(0x12345678,0x9abcdef0)]
  for statuses,tag,words,q,mutation,fill in itertools.product(itertools.product([0,1,0xffffffff],repeat=4),[0,1,2,3,255],values,[queues[i] for i in [0,1,2,4,7,15]],range(4),[0,0x96]):cases.append((4,statuses,[*words,tag,0x42],q,mutation,fill))
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  for raw,statuses,data,q,mutation,fill in cases:
   incoming_r3=0xa1b2c300|(count&255);results=[]
   for candidate,u in enumerate(machines):
    u.mem_write(0x20000000,bytes([fill])*0x3e000);initial=bytearray(u.mem_read(0x20000000,0x3e000));u.reg_write(UC_ARM_REG_XPSR,0x01000000);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
    for value,reg in zip([raw,0x11223344,0x55667788,incoming_r3],[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]):u.reg_write(reg,value)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    st=dict(source=candidate,raw=raw,incoming_r3=incoming_r3,statuses=statuses,data=data,modes=q,mode_index=0,mutation=mutation,pointers={},events=[],cell=int.from_bytes(bytes([fill])*4,'little'));states[id(u)]=st
    u.emu_start((syms['r1_reset_reason_decode_and_report'] if candidate else 0x8198c)|1,0x20000100,count=100000);assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)];assert u.reg_read(UC_ARM_REG_R0)==raw&0x7000f
    initial[0x6000:0x6004]=st['cell'].to_bytes(4,'little');actual=bytes(u.mem_read(0x20000000,0x3e000));assert initial==actual
    if not raw&4:assert not st['pointers']
    results.append([st['events'],st['mode_index'],u.reg_read(UC_ARM_REG_R0),hashlib.sha256(actual).hexdigest()])
   if results[0]!=results[1]:
    fail=dict(raw=raw,statuses=statuses,data=data,modes=q,mutation=mutation,fill=fill,incoming_r3=incoming_r3,results=results);(OUT/'counterexample.json').write_text(json.dumps(fail,indent=2)+'\n');raise AssertionError({k:v for k,v in fail.items() if k!='results'})
   count+=1;callbacks+=len(results[0][0]);diagnostics+=sum(e[0]>=4 for e in results[0][0]);byte_calls+=sum(e[0]==6 for e in results[0][0]);digest.update(json.dumps([raw,statuses,data,q,mutation,fill,incoming_r3,results[0]],sort_keys=True).encode())
 r=dict(comparisons=count,callback_observations_per_side=callbacks,diagnostic_provider_calls_per_side=diagnostics,byte_provider_calls_per_side=byte_calls,trace_sha256=digest.hexdigest(),all_128_recognized_flag_combinations=True,unknown_bits_and_zero_reason_distinguished=True,recognized_mask_0x7000f_checked=True,full_width_getter_statuses_and_values=True,fresh_pc_lr_and_tag_value_reloads_after_callback_mutations=True,tag_retested_after_logging_before_conditional_caller_query=True,four_byte_diagnostic_initial_words_and_incoming_r3_seed_checked=True,raw_r0_stack_callee_integer_full_observed_nonstack_ram_and_typed_callback_order_args_checked=True,diagnostic_pointer_addresses_normalized_private_frame_gate=True,diagnostic_and_logging_bodies_are_named_fixtures=True,source_constant_data_bytes=sum(n for _,_,n in regions),source_raw_seed_bridge_to_c_kernel=True,candidate_native_body_execution_forbidden=True,unicorn_memory_write_hooks_disabled=True,whole_startup_graph_executed=False,physical_reset_or_retention_verified=False,instruction_identity=False,full_raw_abi_verified=False,application_sha256=sha(app),driver_sha256=sha(Path(__file__)),report_sha256=sha(rp),object_sha256=sha(obj),layout=str(layout.relative_to(ROOT)),layout_sha256=sha(layout),data_regions=str(config.relative_to(ROOT)),data_regions_sha256=sha(config),limitations=['Retained diagnostic and logger bodies are named fixtures; full startup/physical reset/retention are unverified.','Raw incoming R3 seeds the upper caller-word bytes through a naked forwarding bridge; the C kernel contains the decoder behavior.','Diagnostic private addresses/frame placement and other raw scratch/padding remain gated.','DIF string overlaps25 bytes of the prior ctype source window; final shared read-only placement/ownership and whole-image identity remain open.'])
 vp.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
if __name__=='__main__':main()
