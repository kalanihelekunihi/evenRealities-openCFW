#!/usr/bin/env python3
"""Native decoder through real retained getters/CRC versus the linked C source graph."""
import hashlib,itertools,json,random,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-reset-retained';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def crc(data):
 value=0xffff
 for byte in data:
  value^=byte
  for _ in range(8):value=(value>>1)^(0xa001 if value&1 else 0)
 return value
CALLS=[('r1_structured_log_mode_get',0x914ec),('r1_structured_log_format',0x91638),('nrf_log_frontend_std_0',0x799c0),('nrf_log_frontend_std_1',0x799c8)]
def main():
 vp=OUT/'graph-verification.json';vp.unlink(missing_ok=True);rp=BASE/'native-reset-retained-runtime/report.json';r=json.loads(rp.read_text());obj=rp.parent/'reset-diagnostic-source.o';assert sha(obj)==r['diagnostic_object_sha256']
 for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw_bytes=app.read_bytes();assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';layout=ROOT/'r1/source-config/runtime/native_reset_diagnostic_graph_verification.ld';config=ROOT/'r1/source-config/runtime/reset-decoder/data-regions.json';regions=json.loads(config.read_text());states={};rng=random.Random(0x7ef4c);digest=hashlib.sha256();count=0;callbacks=0;crc_calls=0;getter_calls=0
 with tempfile.TemporaryDirectory() as tmp:
  d=Path(tmp);elf=d/'test.elf';subprocess.run(['arm-none-eabi-ld','-T',str(layout),str(obj),'-o',str(elf)],check=True);syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3};sections=[]
  for name,a,n in [('text',0x1000000,None),*[region for region in regions if region[0] not in ['bounds','lr_pointer','dif_pointer']]]:
   p=d/(name+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j','.'+name,'-O','binary',str(elf),str(p)],check=True);data=p.read_bytes();sections.append((a,data))
   if n is not None:assert len(data)==n and data==raw_bytes[a-0x27000:a-0x27000+n]
  native={a:i for i,(_,a) in enumerate(CALLS)};compiled={syms[n]&~1:i for i,(n,_) in enumerate(CALLS)};getters_native={0x7edfc:0,0x7ee7c:1,0x7ef4c:2};getters_source={syms[n]:i for i,n in enumerate(['r1_reset_trace_byte_read','r1_reset_trace_return_address_read','r1_reset_trace_program_counter_read'])}
  def hook(u,address,size,_):
   st=states[id(u)];getter=(getters_source if st['source'] else getters_native).get(address)
   if getter is not None:st['getters'].append([getter,u.reg_read(UC_ARM_REG_R0) if getter==0 else 'word_out'])
   if address==(syms['r1_stock_crc16_modbus'] if st['source'] else 0x5d87c):
    pointer=u.reg_read(UC_ARM_REG_R0);assert u.reg_read(UC_ARM_REG_R1)==14;st['crcs'].append([pointer,bytes(u.mem_read(pointer,16)).hex()])
   index=(compiled if st['source'] else native).get(address)
   if index is None:assert not st['source'] or not 0x27000<=address<0xc4d08;return
   args=[u.reg_read(reg) for reg in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]]
   if index==0:value=st['modes'][st['mode_index']%len(st['modes'])];st['mode_index']+=1;used=[value]
   else:
    used=args[:4 if index==1 and args[0]==0xc400000 else 3 if index in [1,3] else 2];value=0x55aa55aa
    if not st['mutated']:
     if st['mutation']==1:u.mem_write(0x20007a48,struct.pack('<I',0x2003ff80))
     if st['mutation']==2:u.mem_write(0x2003ffbe,struct.pack('<H',crc(u.mem_read(0x2003ffb0,14))^1))
     st['mutated']=True
   st['events'].append([index,used,value]);st['cell']=(st['cell']+index+1)&0xffffffff;u.mem_write(0x20006000,st['cell'].to_bytes(4,'little'))
   for i,reg in enumerate([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_R12]):u.reg_write(reg,(0xabcdef01+i*0x11111111)&0xffffffff)
   u.reg_write(UC_ARM_REG_R0,value);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  machines=[]
  for candidate in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,raw_bytes);u.mem_map(0x1000000,0x20000);u.mem_map(0x20000000,0x40000)
   if candidate:
    for address,data in sections:u.mem_write(address,data)
   u.hook_add(UC_HOOK_CODE,hook);machines.append(u)
  flags=[sum(1<<b for i,b in enumerate([0,1,2,3,16,17,18]) if mask&(1<<i)) for mask in range(128)];queues=[[v]*64 for v in [0,1,2,4,7]]+[[rng.getrandbits(32) for _ in range(64)] for _ in range(8)];cases=list(itertools.product(flags,[0,1],[0,1],[0,2,255],queues,range(3)));saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  for raw,busy,bad,tag,q,mutation in cases:
   data=bytearray(rng.randrange(256) for _ in range(13));data[0]=tag;payload=bytes([busy])+data;payload+=struct.pack('<H',crc(payload)^bad);other=bytes([0])+bytes(x^0x55 for x in data);other+=struct.pack('<H',crc(other));results=[]
   for candidate,u in enumerate(machines):
    u.mem_write(0x20000000,b'\x96'*0x40000);u.mem_write(0x20007a34,struct.pack('<6I',0,0x2003f000,0x2003f010,0x2003f3f0,0,0x2003ffb0));u.mem_write(0x2003ffb0,payload);u.mem_write(0x2003ff80,other);u.reg_write(UC_ARM_REG_XPSR,0x01000000);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
    for value,reg in zip([raw,0x11223344,0x55667788,0xa1b2c3d4],[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]):u.reg_write(reg,value)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    st=dict(source=candidate,modes=q,mutation=mutation,mutated=False,mode_index=0,events=[],getters=[],crcs=[],cell=0x96969696);states[id(u)]=st
    try:u.emu_start((syms['r1_reset_reason_decode_and_report'] if candidate else 0x8198c)|1,0x20000100,count=100000)
    except Exception as error:raise RuntimeError(dict(raw=raw,busy=busy,bad=bad,tag=tag,mutation=mutation,candidate=candidate,pc=hex(u.reg_read(UC_ARM_REG_PC)),lr=hex(u.reg_read(UC_ARM_REG_LR)),sp=hex(u.reg_read(UC_ARM_REG_SP)),events=st['events'][-3:],getters=st['getters'][-5:],crcs=st['crcs'][-2:])) from error
    assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)] and u.reg_read(UC_ARM_REG_R0)==raw&0x7000f
    memory=bytes(u.mem_read(0x20000000,0x3e000))+bytes(u.mem_read(0x2003f000,0x1000));results.append([st['events'],st['getters'],st['crcs'],st['mode_index'],u.reg_read(UC_ARM_REG_R0),hashlib.sha256(memory).hexdigest()])
   if results[0]!=results[1]:
    fail=dict(raw=raw,busy=busy,bad=bad,tag=tag,modes=q,mutation=mutation,payload=payload.hex(),other=other.hex(),results=results);(OUT/'graph-counterexample.json').write_text(json.dumps(fail,indent=2)+'\n');raise AssertionError({k:v for k,v in fail.items() if k!='results'})
   count+=1;callbacks+=len(results[0][0]);getter_calls+=len(results[0][1]);crc_calls+=len(results[0][2]);digest.update(json.dumps([raw,busy,bad,tag,q,mutation,payload.hex(),other.hex(),results[0]],sort_keys=True).encode())
 r=dict(comparisons=count,logging_observations_per_side=callbacks,getter_calls_per_side=getter_calls,crc_calls_per_side=crc_calls,trace_sha256=digest.hexdigest(),actual_source_decoder_all_getters_and_crc_execute=True,only_logger_bodies_are_named_fixtures=True,record_bytes_are_explicit_retention_fixtures=True,logger_record_context_mutations_are_controlled_interleavings=True,all_128_flag_combinations_busy_corrupt_and_tag_cases=True,raw_r0_callee_integer_stack_and_full_observed_nonstack_low_and_high_retained_ram_compared=True,no_persistent_pointer_word_normalization=True,source_raw_decoder_data_bytes=1396,source_selected_decoder_data_bytes=1380,source_crc16_table_bytes=512,folded_bounds_and_pointer_cells_not_selected=True,source_context_bytes=24,candidate_native_body_execution_forbidden=True,unicorn_memory_write_hooks_disabled=True,whole_startup_graph_executed=False,physical_retention_verified=False,instruction_identity=False,full_raw_abi_verified=False,application_sha256=sha(app),driver_sha256=sha(Path(__file__)),runtime_report_sha256=sha(rp),object_sha256=sha(obj),layout=str(layout.relative_to(ROOT)),layout_sha256=sha(layout),data_regions_sha256=sha(config),limitations=['Actual source decoder/getters/CRC execute together; logger bodies and retained input records remain fixtures.','Controlled logger interleavings are not physical retention/concurrency proof.','Raw private frames, shared read-only placement, prior GXT pointer alias gate, full startup and byte-identical firmware remain open.'])
 vp.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
if __name__=='__main__':main()
