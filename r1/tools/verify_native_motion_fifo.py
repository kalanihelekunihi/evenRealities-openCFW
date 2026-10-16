#!/usr/bin/env python3
"""Exhaustive signed16 normalization and bounded callback/fault comparisons."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_INVALID
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-motion-fifo-runtime';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
SP=0x2003d000;BUS=0x200076b4;D=0x20010000;END=0x20040000;REGS=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]
def main():
 rp=OUT/'report.json';r=json.loads(rp.read_text());obj=OUT/'motion-fifo-source.o';assert sha(obj)==r['graph_object_sha256']
 for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 evidence={p.name:sha(p) for p in (BASE/'native-motion-fifo').glob('rea-*.json')}
 for p in (BASE/'native-motion-fifo').glob('rea-*.json'):
  n=json.loads(p.read_text())['structuredContent']['normalized_result'];a=int(n['address'],16);assert n['complete'] and bytes.fromhex(n['bytes_hex'])==app.read_bytes()[a-0x27000:a-0x27000+n['returned_bytes']]
 states={};counts=dict(lis=0,bma=0,qma=0);observations=dict(acquire=0,release=0,read=0);faults=0;exhaustive=0;partial_fault_cases=0;digest=hashlib.sha256()
 with tempfile.TemporaryDirectory(prefix='r1-motion-fifo-') as tmp:
  d=Path(tmp);ld=d/'layout.ld';ld.write_text('SECTIONS { .bus 0x200076b4 : { *(.r1.bind.r1_motion_bus_device) } .text 0x1000000 : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }');elf=d/'test.elf';binary=d/'text.bin'
  roots=['r1_lis2dw12_fifo_normalized','r1_bma456w_fifo_normalized','r1_qma6100_fifo_normalized'];bindings={'r1_lis2dw12_fifo_read':0x750e9,'r1_bma456w_fifo_read':0x541a9,'r1_qma6100_bounded_fifo_read':0x86ff5}
  subprocess.run(['arm-none-eabi-ld','--gc-sections',*[arg for name in roots for arg in ['-u',name]],'-T',str(ld),'-e',roots[0],*[f'--defsym={name}={value}' for name,value in bindings.items()],str(obj),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-j','.text','-O','binary',str(elf),str(binary)],check=True)
  syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
  def put(u,a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
  def bounded_write(u,a,data):
   if 0x20000000<=a<END:u.mem_write(a,data[:min(len(data),END-a)])
  def hook(u,a,size,_):
   st=states[id(u)];args=[u.reg_read(reg) for reg in REGS]
   if a in [0x750e8,0x541a8,0x86ff4]:
    kind='read';st['trace'].append([kind,args[:2]]);bounded_write(u,args[0],st['payload']);result=st['returned']
    if st['mutation']==2:put(u,BUS,D+0x2040)
   elif a in [0x1100000,0x1100100]:kind='acquire';st['trace'].append([kind,args[0]]);result=0x89abcdef
   elif a in [0x1100010,0x1100110]:
    kind='release';st['trace'].append([kind,args[0]]);result=0xfedcba98
    if st['mutation']==1:bounded_write(u,st['destination'],struct.pack('<3H',0xfff9,3,0xffff))
   else:return
   if not st['side']:observations[kind]+=1
   for reg,value in zip(REGS,[result,0x11111111,0x22222222,0x33333333]):u.reg_write(reg,value)
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  def invalid(u,access,address,size,value,_):states[id(u)]['fault']=[access,address,size,value];return False
  machines=[]
  for i in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,0x40000);u.mem_write(0x1000000,binary.read_bytes());u.mem_map(0x1100000,4096);u.mem_map(0x20000000,0x40000);u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_INVALID,invalid);machines.append(u)
  entries={'lis':(0x6f3b4,roots[0]),'bma':(0x6f1dc,roots[1]),'qma':(0x6f448,roots[2])};saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  def oracle(value):return ((value if value<32768 else value-65536)//4)&65535
  exhaustive_cases=((kind,32,31,2,0,0,D,block) for kind,block in itertools.product(entries,range(0,65536,32)))
  matrix=((kind,returned,requested,bus,mutation,seed,destination,None) for kind,returned,requested,bus,mutation,seed,destination in itertools.product(entries,[0xffffffff,0x80000000,0,1,2,29,30,31,32,63,64,127],[0,1,30,31,0xffffffff],range(3),range(3),[0,0xaa],[D,D+1,0,END-2]))
  patterns=[0x7fff,0x8000,0x8001,0xfffb,0xfffc,0xfffd,0xfffe,0xffff,0,1,2,3,4,5,0x7ffe]
  for kind,returned,requested,bus,mutation,seed,destination,block in itertools.chain(exhaustive_cases,matrix):
   payload=b''.join(struct.pack('<3H',v,v,v) for v in range(block,block+32)) if block is not None else b''.join(struct.pack('<3H',patterns[i%15],patterns[(i+1)%15],patterns[(i+2)%15]) for i in range(128));results=[]
   for side,u in enumerate(machines):
    u.mem_write(D,bytes([seed])*1024);u.mem_write(END-16,bytes([seed])*16);u.mem_write(SP-1024,b'\x96'*2048);put(u,BUS,D+0x2000 if bus else 0)
    for i in range(2):u.mem_write(D+0x2000+i*64,struct.pack('<6I',0,D+0x2100+i*32,0,0,0,0));u.mem_write(D+0x2100+i*32,struct.pack('<4I',0,0,0x1100001+i*256 if bus==2 else 0,0x1100011+i*256 if bus==2 else 0))
    for reg,value in zip(REGS,[destination,requested,0x12345678,0xabcdef01]):u.reg_write(reg,value)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12340000+i)
    u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,0x20000101);st=dict(side=side,trace=[],fault=None,payload=payload,returned=returned,mutation=mutation,destination=destination);states[id(u)]=st
    try:u.emu_start((syms[entries[kind][1]] if side else entries[kind][0])|1,0x20000100,count=200000)
    except UcError:assert st['fault'],(kind,returned,hex(u.reg_read(UC_ARM_REG_PC)))
    if not st['fault']:assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==SP and [u.reg_read(reg) for reg in saved]==[0x12340000+i for i in range(8)]
    results.append([None if st['fault'] else u.reg_read(UC_ARM_REG_R0),st['trace'],st['fault'],bytes(u.mem_read(D,1024)).hex(),bytes(u.mem_read(END-16,16)).hex(),bytes(u.mem_read(BUS,4)).hex()])
    if block is not None:assert bytes(u.mem_read(D,192))==b''.join(struct.pack('<3H',oracle(v),oracle(v),oracle(v)) for v in range(block,block+32))
    if destination==END-2 and 0<returned<0x80000000:
     value=0xfff9 if mutation==1 and bus==2 else payload[0]|payload[1]<<8
     expected=value if kind=='qma' else oracle(value);assert bytes(u.mem_read(END-2,2))==struct.pack('<H',expected),(kind,returned,mutation,bus,results[-1])
   assert results[0]==results[1],(kind,returned,requested,bus,mutation,seed,destination,block,results)
   counts[kind]+=1;faults+=bool(results[0][2]);exhaustive+=block is not None;partial_fault_cases+=destination==END-2 and 0<returned<0x80000000;digest.update(json.dumps([kind,returned,requested,bus,mutation,seed,destination,block,results[0]],sort_keys=True).encode())
 receipt=dict(comparisons=sum(counts.values()),counts=counts,observation_counts=observations,matching_faults=faults,exhaustive_blocks=exhaustive,exhaustive_values_per_axis_per_family=65536,partial_triple_fault_cases=partial_fault_cases,trace_sha256=digest.hexdigest(),report_sha256=sha(rp),object_sha256=sha(obj),driver_sha256=sha(Path(__file__)),application_sha256=sha(app),evidence=evidence,actual_three_normalizers_bus_wrappers_and_registry_dispatch=True,only_raw_fifo_and_bus_operations_are_fixtures=True,unclamped_counts_signed_returns_asr_rounding_and_qma_preload_checked=True,raw_r0_callee_sp_and_partial_fault_ram_checked=True,full_private_frame_history_verified=False,full_raw_abi_verified=False,real_sensor_fifo_bus_execution_proven=False,instruction_identity=False,whole_image_complete=False,hardware_write_executed=False)
 (OUT/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
