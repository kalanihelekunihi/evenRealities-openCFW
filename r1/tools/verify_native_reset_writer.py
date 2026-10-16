#!/usr/bin/env python3
"""Source reset writers, actual CRC and attributable clear versus authenticated native."""
import hashlib,itertools,json,random,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
from verify_native_reset_retained import crc
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-reset-writer';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ENTRIES={'byte':('r1_reset_trace_byte_write',0x7ee30),'lr':('r1_reset_trace_return_address_write',0x7eeda),'clear':('r1_reset_trace_addresses_clear',0x7ef06),'pc':('r1_reset_trace_program_counter_write',0x7efaa),'caller':('r1_reset_trace_reboot_caller_write',0x7efd6),'tag':('r1_reset_trace_persist_tag_write',0x7effe),'capture':('r1_reset_trace_capture_site_adapter',0x58a9a),'current':('r1_reset_trace_current_site_capture',0x7efea),'probe':('r1_reset_trace_program_counter_probe',0x27484)}
def main():
 rp=BASE/'native-reset-writer-runtime/report.json';report=json.loads(rp.read_text());obj=rp.parent/'reset-writer-source.o';assert sha(obj)==report['writer_object_sha256']
 for p,h in report['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';layout=ROOT/'r1/source-config/runtime/native_reset_writer_verification.ld';states={};digest=hashlib.sha256();counts={k:0 for k in ENTRIES};events=0
 with tempfile.TemporaryDirectory() as tmp:
  d=Path(tmp);elf=d/'test.elf';text=d/'text.bin';probe=d/'probe.bin';subprocess.run(['arm-none-eabi-ld','-T',str(layout),str(obj),'-o',str(elf)],check=True)
  for section,path in [('.text',text),('.probe',probe)]:subprocess.run(['arm-none-eabi-objcopy','-j',section,'-O','binary',str(elf),str(path)],check=True)
  syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3};assert syms['r1_reset_trace_program_counter_probe']==0x27484 and probe.read_bytes()==raw[0x27484-0x27000:0x27488-0x27000]
  def hook(u,address,size,_):
   st=states[id(u)];source=st['source']
   if source:assert not 0x27000<=address<0xc4d08 or 0x27484<=address<0x27488
   byte=syms['r1_reset_trace_byte_write'] if source else 0x7ee30
   if address==byte:st['events'].append(['write',u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1)])
   if address==(syms['r1_stock_crc16_modbus'] if source else 0x5d87c):
    pointer=u.reg_read(UC_ARM_REG_R0);assert u.reg_read(UC_ARM_REG_R1)==14;st['events'].append(['crc',pointer,bytes(u.mem_read(pointer,16)).hex()]);i=st['crc'];st['crc']+=1
    if i==0:
     mode=st['mutation']
     if mode==1:u.mem_write(0x20007a48,struct.pack('<I',0x20002200))
     elif mode==2:
      u.mem_write(pointer,b'\x01');u.mem_write(pointer+14,struct.pack('<H',crc(u.mem_read(pointer,14))))
     elif mode==3:u.mem_write(pointer+14,struct.pack('<H',crc(u.mem_read(pointer,14))^1))
     elif mode==4:u.mem_write(pointer+14,struct.pack('<H',crc(u.mem_read(pointer,14))))
   if address==(syms['__aeabi_memclr'] if source else 0x277aa):
    pointer=u.reg_read(UC_ARM_REG_R0);assert u.reg_read(UC_ARM_REG_R1)==16;st['events'].append(['clear',pointer,bytes(u.mem_read(pointer,16)).hex()])
    if st['mutation']==5:u.mem_write(0x20007a48,struct.pack('<I',0x20002200))
  machines=[]
  for source in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,raw);u.mem_map(0x1000000,0x20000);u.mem_write(0x1000000,text.read_bytes());u.mem_map(0x20000000,0x40000)
   if source:u.mem_write(0x27484,probe.read_bytes())
   u.hook_add(UC_HOOK_CODE,hook);machines.append(u)
  rng=random.Random(0x7ee30);patterns=[bytes(13),bytes([255])*13,bytes(range(13))]+[rng.randbytes(13) for _ in range(5)];values=[0,1,2,7,0x107,0xff,0x12345678,0xffffffff];cases=[]
  for index,value,data,busy,bad,mutation in itertools.product(list(range(15))+[0xffffffff],values,patterns,[0,1],[0,1],range(6)):cases.append(('byte',index,value,data,busy,bad,mutation))
  for kind,value,data,busy,bad,mutation in itertools.product([k for k in ENTRIES if k!='byte'],values,patterns,[0,1],[0,1],range(6)):cases.append((kind,0,value,data,busy,bad,mutation))
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  for kind,index,value,data,busy,bad,mutation in cases:
   results=[]
   for source,u in enumerate(machines):
    u.mem_write(0x20000000,b'\x96'*0x40000);payload=bytes([busy])+data;payload+=struct.pack('<H',crc(payload)^bad);other=bytes([0])+bytes(x^0x55 for x in data);other+=struct.pack('<H',crc(other));u.mem_write(0x20002000,payload);u.mem_write(0x20002200,other);u.mem_write(0x20007a34,struct.pack('<6I',0,0x2003f000,0x2003f010,0x2003f3f0,0,0x20002000));states[id(u)]=dict(source=source,events=[],crc=0,mutation=mutation)
    u.reg_write(UC_ARM_REG_XPSR,0x01000000);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    u.reg_write(UC_ARM_REG_R0,index if kind=='byte' else value);u.reg_write(UC_ARM_REG_R1,value);u.reg_write(UC_ARM_REG_R2,0x55667788);u.reg_write(UC_ARM_REG_R3,0x99aabbcc)
    u.emu_start((syms[ENTRIES[kind][0]] if source else ENTRIES[kind][1])|1,0x20000100,count=200000);assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
    memory=bytes(u.mem_read(0x20000000,0x3e000))+bytes(u.mem_read(0x2003f000,0x1000));results.append([u.reg_read(UC_ARM_REG_R0),states[id(u)]['events'],hashlib.sha256(memory).hexdigest()])
   if results[0]!=results[1]:
    failure=dict(kind=kind,index=index,value=value,data=data.hex(),busy=busy,bad=bad,mutation=mutation,results=results);(OUT/'counterexample.json').write_text(json.dumps(failure,indent=2)+'\n');raise AssertionError({k:v for k,v in failure.items() if k!='results'})
   counts[kind]+=1;events+=len(results[0][1]);digest.update(json.dumps([kind,index,value,data.hex(),busy,bad,mutation,results[0]],sort_keys=True).encode())
 receipt=dict(comparisons=sum(counts.values()),counts=counts,events_per_side=events,trace_sha256=digest.hexdigest(),actual_source_crc_and_attributable_clear=True,probe_source_bytes_match=True,candidate_native_execution_forbidden_except_source_probe=True,controlled_context_and_record_mutation_fixtures=True,raw_r0_callee_registers_stack_and_observed_ram_checked=True,application_sha256=sha(app),driver_sha256=sha(Path(__file__)),report_sha256=sha(rp),object_sha256=sha(obj),layout_sha256=sha(layout),instruction_identity=False,full_image_complete=False,limitations=['Probe source is linked at recovered address for sampled PC equality.','Clear call order, arguments and RAM effects checked; provider internal store granularity is not required equal.','Private stack bytes excluded; physical concurrency, retention and full firmware placement remain gated.'])
 (OUT/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
