#!/usr/bin/env python3
"""Actual source CRC16 and retained byte/word getters versus native record contracts."""
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
ENTRIES={'byte':('r1_reset_trace_byte_read',0x7edfc),'lr':('r1_reset_trace_return_address_read',0x7ee7c),'pc':('r1_reset_trace_program_counter_read',0x7ef4c)}
def main():
 vp=OUT/'verification.json';vp.unlink(missing_ok=True);rp=OUT/'report.json';r=json.loads(rp.read_text());obj=OUT/'reset-retained-source.o';assert sha(obj)==r['linked_sha256']
 for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';layout=ROOT/'r1/source-config/runtime/native_reset_retained_verification.ld';states={};rng=random.Random(0x7edfc);digest=hashlib.sha256();counts={'byte':0,'lr':0,'pc':0,'persistent_alias_sequence':0};crc_calls=0;byte_calls=0
 with tempfile.TemporaryDirectory() as tmp:
  d=Path(tmp);elf=d/'test.elf';binary=d/'text.bin';subprocess.run(['arm-none-eabi-ld','-T',str(layout),str(obj),'-o',str(elf)],check=True);subprocess.run(['arm-none-eabi-objcopy','-j','.text','-O','binary',str(elf),str(binary)],check=True);syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3};assert syms['r1_reset_trace_context']==0x20007a34
  def hook(u,address,size,_):
   st=states[id(u)]
   if address==(syms['r1_reset_trace_byte_read'] if st['source'] else 0x7edfc):st['byte_calls'].append(u.reg_read(UC_ARM_REG_R0))
   if address==(syms['r1_stock_crc16_modbus'] if st['source'] else 0x5d87c):
    pointer=u.reg_read(UC_ARM_REG_R0);assert u.reg_read(UC_ARM_REG_R1)==14 and pointer in st['records'];i=st['crc_index'];st['crc_index']+=1;st['crc_calls'].append([pointer,bytes(u.mem_read(pointer,16)).hex()])
    if i==0:
     mode=st['mutation']
     if mode==1:u.mem_write(0x20007a48,struct.pack('<I',st['records'][1]))
     elif mode==2:
      u.mem_write(pointer,b'\x01');u.mem_write(pointer+14,struct.pack('<H',crc(u.mem_read(pointer,14))))
     elif mode==3:
      u.mem_write(pointer+4,bytes([u.mem_read(pointer+4,1)[0]^0x80]));u.mem_write(pointer+14,struct.pack('<H',crc(u.mem_read(pointer,14))))
     elif mode==4:u.mem_write(pointer+14,struct.pack('<H',crc(u.mem_read(pointer,14))^1))
     elif mode==5:u.mem_write(pointer+14,struct.pack('<H',crc(u.mem_read(pointer,14))))
   assert not st['source'] or not 0x27000<=address<0xc4d08
  machines=[]
  for _ in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,raw);u.mem_map(0x1000000,0x10000);u.mem_write(0x1000000,binary.read_bytes());u.mem_map(0x20000000,0x40000);u.hook_add(UC_HOOK_CODE,hook);machines.append(u)
  patterns=[bytes(13),bytes([0xff])*13,bytes(range(13)),bytes(reversed(range(13)))]+[bytes(rng.randrange(256) for _ in range(13)) for _ in range(28)];cases=[]
  indexes=list(range(15))+[0x100,0x80000000,0xffffffff];destinations=[0,0x20003000,0x20003001,0x20002000,0x2000200e]
  for index,data,busy,bad,out,mutation in itertools.product(indexes,patterns,[0,1,0xff],[0,1],destinations,range(6)):cases.append(('byte',index,data,busy,bad,out,mutation,0x20002000))
  for kind,data,busy,bad,out,mutation in itertools.product(['lr','pc'],patterns,[0,1,0xff],[0,1],destinations,range(6)):cases.append((kind,0,data,busy,bad,out,mutation,0x20002000))
  for kind,data,bad,mutation in itertools.product(['byte','lr','pc'],patterns,[0,1],range(6)):cases.append((kind,2,data,0,bad,0x20003000,mutation,0x2003ffb0))
  for kind,index in itertools.product(['byte','lr','pc'],indexes):cases.append((kind,index,patterns[0],0,0,0,0,0))
  for data,bad,mutation in itertools.product(patterns,[0,1],range(6)):cases.append(('persistent_alias_sequence',0,data,0,bad,0x20002000,mutation,0x20002000))
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  for kind,index,data,busy,bad,out,mutation,record in cases:
   results=[]
   for candidate,u in enumerate(machines):
    u.mem_write(0x20000000,b'\x96'*0x40000);record_b=0x20002200 if record!=0x2003ffb0 else 0x2003ff80;payload=bytes([busy])+data;payload+=struct.pack('<H',crc(payload)^bad);other=bytes([0])+bytes(x^0x55 for x in data);other+=struct.pack('<H',crc(other));u.mem_write(record_b,other)
    if record:u.mem_write(record,payload)
    u.mem_write(0x20007a34,struct.pack('<6I',0,0x2003f000,0x2003f010,0x2003f3f0,0,record));st=dict(source=candidate,records=[record,record_b],mutation=mutation,crc_index=0,crc_calls=[],byte_calls=[]);states[id(u)]=st;returns=[]
    steps=[('byte',0,out),('byte',1,out),('lr',0,out),('pc',0,out)] if kind=='persistent_alias_sequence' else [(kind,index,out)]
    for entry,key,destination in steps:
     u.reg_write(UC_ARM_REG_XPSR,0x01000000);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
     for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
     u.reg_write(UC_ARM_REG_R0,key if entry=='byte' else destination);u.reg_write(UC_ARM_REG_R1,destination);u.reg_write(UC_ARM_REG_R2,0x55667788);u.reg_write(UC_ARM_REG_R3,0x99aabbcc)
     u.emu_start((syms[ENTRIES[entry][0]] if candidate else ENTRIES[entry][1])|1,0x20000100,count=100000);assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)];returns.append(u.reg_read(UC_ARM_REG_R0));assert returns[-1] in [0,1]
    memory=bytes(u.mem_read(0x20000000,0x3e000))+bytes(u.mem_read(0x2003f000,0x1000));results.append([st['crc_calls'],st['byte_calls'],returns,hashlib.sha256(memory).hexdigest()])
   if results[0]!=results[1]:
    fail=dict(kind=kind,index=index,data=data.hex(),busy=busy,bad=bad,out=out,mutation=mutation,record=record,results=results);(OUT/'counterexample.json').write_text(json.dumps(fail,indent=2)+'\n');raise AssertionError({k:v for k,v in fail.items() if k!='results'})
   counts[kind]+=1;crc_calls+=len(results[0][0]);byte_calls+=len(results[0][1]);digest.update(json.dumps([kind,index,data.hex(),busy,bad,out,mutation,record,results[0]],sort_keys=True).encode())
 receipt=dict(comparisons=sum(counts.values()),counts=counts,crc_calls_per_side=crc_calls,byte_calls_per_side=byte_calls,trace_sha256=digest.hexdigest(),actual_source_crc16_executed_not_fixture=True,all_three_retained_getters_execute_source=True,index_0_through12_boundary_and_unsigned_rejection=True,null_destinations_do_not_read_context=True,busy_header_and_crc_validation_checked=True,output_aliasing_and_persistent_record_sequences=True,unaligned_word_destinations_checked=True,crc_entry_record_context_mutations_are_explicit_fixtures=True,byte_getter_captures_record_pointer_before_crc=True,crc_callback_header_not_rechecked_stored_crc_reloaded=True,word_reads_revalidate_each_byte_and_publish_after_all_success=True,raw_r0_callee_integer_stack_and_full_observed_nonstack_low_and_high_retained_ram_checked=True,record_not_consumed_or_cleared=True,canonical_retained_record_address_exercised=True,candidate_native_body_execution_forbidden=True,unicorn_memory_write_hooks_disabled=True,source_context_bytes=24,retained_record_has_no_cold_initializer=True,whole_startup_graph_executed=False,physical_retention_verified=False,instruction_identity=False,full_raw_abi_verified=False,application_sha256=sha(app),driver_sha256=sha(Path(__file__)),report_sha256=sha(rp),object_sha256=sha(obj),layout=str(layout.relative_to(ROOT)),layout_sha256=sha(layout),limitations=['CRC entry mutations are explicit controlled interleavings; physical concurrency/retention are unverified.','Getters and CRC run as actual source; no getter/CRC executable fixtures substitute their bodies.','Private byte slots use native four-byte stride; their initial scratch seed bytes, private addresses/frames and other raw ABI remain open.','Only the cold24-byte context view is source-initialized; retained record bytes remain external retained RAM, with writer/capture and whole-image placement unresolved.'])
 vp.write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
