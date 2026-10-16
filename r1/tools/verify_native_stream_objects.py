#!/usr/bin/env python3
"""Native stream object/registry graphs with allocation and logging fixtures."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_INVALID
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-stream-objects-runtime';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
SP=0x2003d000;R=0x2001a1b0;D=0x20010000;F=D+0x1000;REGS=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]
def main():
 rp=OUT/'report.json';r=json.loads(rp.read_text());obj=OUT/'stream-objects-source.o';assert sha(obj)==r['graph_object_sha256']
 for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 evidence={p.name:sha(p) for p in (BASE/'native-stream-objects').glob('rea-*.json')}
 for p in (BASE/'native-stream-objects').glob('rea-*.json'):
  n=json.loads(p.read_text())['structuredContent']['normalized_result'];a=int(n['address'],16);assert n['complete'] and bytes.fromhex(n['bytes_hex'])==app.read_bytes()[a-0x27000:a-0x27000+n['returned_bytes']]
 counts=dict(create=0,insert=0,lookup=0,flag=0);observations=dict(allocate=0,mode=0,ring=0,sdk=0);faults=0;states={};digest=hashlib.sha256()
 with tempfile.TemporaryDirectory(prefix='r1-stream-objects-') as tmp:
  d=Path(tmp);ld=d/'layout.ld';ld.write_text('SECTIONS { .registry 0x2001a1b0 (NOLOAD) : { *(.bss.r1.stream.object_registry) } .object_ring 0x897b8 : { *(.r1.stream.object_ring) } .object_sdk 0x897d8 : { *(.r1.stream.object_sdk) } .insert_ring 0x89dfc : { *(.r1.stream.insert_ring) } .insert_sdk 0x89e1c : { *(.r1.stream.insert_sdk) } .text 0x1000000 : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }');elf=d/'test.elf';binary=d/'text.bin'
  bindings={'pvPortMalloc':0x1100001,'r1_structured_log_mode_get':0x1100011,'r1_structured_log_format':0x1100021,'nrf_log_frontend_std_0':0x1100031};roots=['r1_stream_object_create','r1_stream_object_insert','r1_stream_object_lookup','r1_stream_object_flag_set']
  subprocess.run(['arm-none-eabi-ld','--gc-sections',*[arg for name in roots for arg in ['-u',name]],'-T',str(ld),'-e',roots[0],*[f'--defsym={name}={value}' for name,value in bindings.items()],str(obj),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-j','.text','-O','binary',str(elf),str(binary)],check=True)
  syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
  for section,addr,name in [('object_ring',0x897b8,'object_ring'),('object_sdk',0x897d8,'object_sdk'),('insert_ring',0x89dfc,'insert_ring'),('insert_sdk',0x89e1c,'insert_sdk')]:
   file=d/(section+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j','.'+section,'-O','binary',str(elf),str(file)],check=True);assert file.read_bytes()==app.read_bytes()[addr-0x27000:addr-0x27000+file.stat().st_size] and syms['r1_stream_'+name]==addr
  def hook(u,a,size,_):
   st=states[id(u)];args=[u.reg_read(reg) for reg in REGS]
   if a in [0x855a0,0x1100000]:
    kind='allocate';index=st['allocations'];result=(D if args[0]==56 else D+0x200) if st['mask']&(1<<index) else 0;st['allocations']+=1;st['trace'].append([kind,args[0],result])
   elif a in [0x914ec,0x1100010]:
    kind='mode';result=(st['mode']^(st['mode_calls'] if st['mutate'] else 0))&7;st['mode_calls']+=1;st['trace'].append([kind,result])
   elif a in [0x91638,0x1100020]:kind='ring';st['trace'].append([kind,args[:3]]);result=0x87654321
   elif a in [0x799c0,0x1100030]:kind='sdk';st['trace'].append([kind,args[:2]]);result=0xabcdef01
   else:return
   if not st['side']:observations[kind]+=1
   for reg,value in zip(REGS,[result,0x11111111,0x22222222,0x33333333]):u.reg_write(reg,value)
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  def invalid(u,access,address,size,value,_):states[id(u)]['fault']=[access,address,size,value,u.reg_read(UC_ARM_REG_BASEPRI)];return False
  machines=[]
  for i in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,0x40000);u.mem_write(0x1000000,binary.read_bytes());u.mem_map(0x1100000,4096);u.mem_map(0x20000000,0x40000);u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_INVALID,invalid);machines.append(u)
  entries={'create':(0x896f0,roots[0]),'insert':(0x89d9c,roots[1]),'lookup':(0x89d54,roots[2]),'flag':(0x8a5c0,roots[3])};saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  def invoke(u,entry,args):
   for reg,value in zip(REGS,args):u.reg_write(reg,value)
   for i,reg in enumerate(saved):u.reg_write(reg,0x12340000+i)
   u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,0x20000101)
   try:u.emu_start(entry|1,0x20000100,count=200000)
   except UcError:assert states[id(u)]['fault'],hex(u.reg_read(UC_ARM_REG_PC))
   if not states[id(u)]['fault']:assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==SP and [u.reg_read(reg) for reg in saved]==[0x12340000+i for i in range(8)]
   return None if states[id(u)]['fault'] else u.reg_read(UC_ARM_REG_R0)
  for kind,length,sample,mask,stride,old,mode,seed in itertools.product(entries,[0,1,7,8,9,255,256,257,511,512],[0,1,0x10000,0xffffffff],range(4),[0,8],[0,2],range(8),[0,0xaa]):
   results=[]
   for side,u in enumerate(machines):
    u.mem_write(D,bytes([seed])*0x2000);u.mem_write(F,b'a'*length+b'\0');u.mem_write(SP-1024,b'\x96'*2048);u.mem_write(R,struct.pack('<3I',stride,D+0x400 if old else 0,D+0x440 if old else 0));u.reg_write(UC_ARM_REG_BASEPRI,0)
    u.mem_write(D+0x400,struct.pack('<4I',0x12345678,D+0x600,0,D+0x440));u.mem_write(D+0x440,struct.pack('<4I',0x87654321,D+0x680,D+0x400,0));u.mem_write(D+0x600,b'a'*7+b'\0');u.mem_write(D+0x680,b'a'*8+b'\0')
    states[id(u)]=dict(side=side,trace=[],fault=None,mask=mask,allocations=0,mode=mode,mode_calls=0,mutate=seed!=0)
    if kind=='create':args=[0 if length==512 else F,sample,0 if mode==7 else D+0x1800,0 if seed==0 else 0xabcdef01]
    elif kind=='insert':args=[D,0x12345678,0x87654321,0xabcdef01]
    elif kind=='lookup':args=[F,0x12345678,0x87654321,0xabcdef01]
    else:args=[D if old else 0,sample,0x87654321,0xabcdef01]
    raw=invoke(u,syms[entries[kind][1]] if side else entries[kind][0],args);workflow=None
    if kind=='create' and raw:workflow=invoke(u,syms[roots[2]] if side else 0x89d54,[F,0x12345678,0x87654321,0xabcdef01])
    st=states[id(u)];results.append([raw,workflow,st['trace'],st['fault'],bytes(u.mem_read(R,12)).hex(),bytes(u.mem_read(D,0x2000)).hex()])
   assert results[0]==results[1],(kind,length,sample,mask,stride,old,mode,seed,results[0][:5],results[1][:5])
   counts[kind]+=1;faults+=bool(results[0][3]);digest.update(json.dumps([kind,length,sample,mask,stride,old,mode,seed,results[0]],sort_keys=True).encode())
 receipt=dict(comparisons=sum(counts.values()),counts=counts,observation_counts=observations,matching_fatal_faults=faults,trace_sha256=digest.hexdigest(),report_sha256=sha(rp),object_sha256=sha(obj),driver_sha256=sha(Path(__file__)),application_sha256=sha(app),evidence=evidence,actual_four_bodies_memory_strings_and_lists=True,only_allocator_and_logging_are_fixtures=True,low8_name_length_full_sample_guard_node_failure_and_lookup_checked=True,raw_r0_callee_sp_registry_and_object_ram_checked=True,source_zero_registry_bytes=12,full_private_frame_history_verified=False,full_raw_abi_verified=False,real_heap_logging_sensor_execution_proven=False,instruction_identity=False,whole_image_complete=False,hardware_write_executed=False)
 (OUT/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
