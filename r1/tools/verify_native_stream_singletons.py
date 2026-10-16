#!/usr/bin/env python3
"""Native sensor factories through actual object core, with hardware gates explicit."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-stream-singletons-runtime';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
SP=0x2003d000;R=0x2001a1b0;D=0x20010000;REGS=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]
def main():
 rp=OUT/'report.json';r=json.loads(rp.read_text());obj=OUT/'stream-singletons-source.o';assert sha(obj)==r['graph_object_sha256']
 for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 evidence={p.name:sha(p) for p in (BASE/'native-stream-singletons').glob('rea-*.json')}
 for p in (BASE/'native-stream-singletons').glob('rea-*.json'):
  n=json.loads(p.read_text())['structuredContent']['normalized_result'];a=int(n['address'],16);assert n['complete'] and bytes.fromhex(n['bytes_hex'])==app.read_bytes()[a-0x27000:a-0x27000+n['returned_bytes']]
 counts=dict(acc=0,temp=0,workflow=0,open=0,close=0,read=0);observations=dict(allocate=0,mode=0,ring=0,sdk=0,calibrated=0);states={};digest=hashlib.sha256()
 with tempfile.TemporaryDirectory(prefix='r1-stream-singletons-') as tmp:
  d=Path(tmp);ld=d/'layout.ld';placements=[('acc_ops',0x9a590,'.r1.stream.acc.ops'),('temp_ops',0x9a5a8,'.r1.stream.temp.ops'),('acc_name',0x89d98,'.r1.stream.acc.name'),('temp_name',0x8a1bc,'.r1.stream.temp.name'),('open',0x918fc,'.text.r1_stream_temperature_open'),('close',0x918f8,'.text.r1_stream_temperature_close'),('read',0x91900,'.text.r1_stream_temperature_read'),('object_ring',0x897b8,'.r1.stream.object_ring'),('object_sdk',0x897d8,'.r1.stream.object_sdk'),('insert_ring',0x89dfc,'.r1.stream.insert_ring'),('insert_sdk',0x89e1c,'.r1.stream.insert_sdk')]
  ld.write_text('SECTIONS { .registry 0x2001a1b0 (NOLOAD) : { *(.bss.r1.stream.object_registry) } '+''.join('.'+name+' '+hex(addr)+' : { *('+section+') } ' for name,addr,section in placements)+'.text 0x1000000 : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }');elf=d/'test.elf';binary=d/'text.bin'
  bindings={'pvPortMalloc':0x1100001,'r1_structured_log_mode_get':0x1100011,'r1_structured_log_format':0x1100021,'nrf_log_frontend_std_0':0x1100031,'r1_motion_initialize_entry':0x6f401,'r1_motion_stream_close_boundary':0x6f301,'r1_motion_thirty_sample_batch_producer':0x6f4a1,'r1_temperature_pair_read_calibrated':0x50e4d};roots=['r1_native_accelerometer_singleton','r1_native_temperature_singleton','r1_stream_temperature_open','r1_stream_temperature_close','r1_stream_temperature_read','r1_stream_object_lookup']
  subprocess.run(['arm-none-eabi-ld','--gc-sections',*[arg for name in roots for arg in ['-u',name]],'-T',str(ld),'-e',roots[0],*[f'--defsym={name}={value}' for name,value in bindings.items()],str(obj),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-j','.text','-O','binary',str(elf),str(binary)],check=True)
  syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3};sections={};table_hashes={}
  for name,addr,_ in placements:
   file=d/(name+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j','.'+name,'-O','binary',str(elf),str(file)],check=True);sections[name]=file.read_bytes()
   if name!='read':assert sections[name]==app.read_bytes()[addr-0x27000:addr-0x27000+len(sections[name])]
   if name.endswith('ops'):assert len(sections[name])==12;table_hashes[name]=sha(file)
  def put(u,a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
  def hook(u,a,size,_):
   st=states[id(u)];args=[u.reg_read(reg) for reg in REGS]
   if a in [0x855a0,0x1100000]:
    kind='allocate';index=st['allocations'];st['allocations']+=1
    if args[0]==56:result=D+st['objects']*128;st['objects']+=1
    else:result=D+0x200+st['nodes']*64;st['nodes']+=1
    if not st['mask']&(1<<index):result=0
    st['trace'].append([kind,args[0],result])
   elif a in [0x914ec,0x1100010]:kind='mode';result=(st['mode']^(st['mode_calls'] if st['mutation'] else 0))&7;st['mode_calls']+=1;st['trace'].append([kind,result])
   elif a in [0x91638,0x1100020]:kind='ring';result=0;st['trace'].append([kind,args[:3]])
   elif a in [0x799c0,0x1100030]:kind='sdk';result=0;st['trace'].append([kind,args[:2]])
   elif a==0x50e4c:
    kind='calibrated';result=st['sample'];st['trace'].append([kind])
    if st['mutation']==1:u.mem_write(st['destination']+2,b'\xbb\xcc')
    elif st['mutation']==2:u.mem_write(st['destination'],b'\xff\xff\xdd\xee')
   elif a in [0x6f400,0x6f300,0x6f4a0]:raise AssertionError('Motion hardware provider executed unexpectedly')
   else:return
   if not st['side']:observations[kind]+=1
   for reg,value in zip(REGS,[result,0x11111111,0x22222222,0x33333333]):u.reg_write(reg,value)
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  machines=[]
  for side in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,0x40000);u.mem_write(0x1000000,binary.read_bytes());u.mem_map(0x1100000,4096);u.mem_map(0x20000000,0x40000);u.hook_add(UC_HOOK_CODE,hook)
   if side:
    for name,addr,_ in placements:u.mem_write(addr,sections[name])
   machines.append(u)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  def invoke(u,entry,args):
   for reg,value in zip(REGS,args):u.reg_write(reg,value)
   for i,reg in enumerate(saved):u.reg_write(reg,0x12340000+i)
   u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,0x20000101);u.emu_start(entry|1,0x20000100,count=200000)
   assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==SP and [u.reg_read(reg) for reg in saved]==[0x12340000+i for i in range(8)]
   return u.reg_read(UC_ARM_REG_R0)
  factories=((kind,mask,old,mode,seed,D,2,0x12345678,mutation) for kind,mask,old,mode,seed,mutation in itertools.product(['acc','temp','workflow'],[0,1,3,5,7,15],range(2),range(8),[0,0xaa],range(2)))
  reads=(('read',15,0,0,seed,destination,length,sample,mutation) for destination,length,sample,mutation,seed in itertools.product([0,D,D+1,D+2],[0,1,2,3,65535,65538],[0,1,65535,0x12345678,0xffffffff],range(3),[0,0xaa]))
  leaves=((kind,15,0,0,seed,D,2,context,mutation) for kind,context,mutation,seed in itertools.product(['open','close'],[0,1,65535,0x12345678,0xffffffff],range(3),[0,0xaa]))
  for kind,mask,old,mode,seed,destination,length,sample,mutation in itertools.chain(factories,reads,leaves):
   results=[]
   for side,u in enumerate(machines):
    u.mem_write(D,bytes([seed])*0x1000);u.mem_write(R,struct.pack('<3I',8 if old else 0,D+0x400 if old else 0,D+0x440 if old else 0));u.mem_write(D+0x400,struct.pack('<4I',0x12345678,D+0x600,0,D+0x440));u.mem_write(D+0x440,struct.pack('<4I',0x87654321,D+0x680,D+0x400,0));u.mem_write(D+0x600,b'acc\0');u.mem_write(D+0x680,b'temp\0');u.mem_write(SP-1024,b'\x96'*2048);states[id(u)]=dict(side=side,trace=[],mask=mask,allocations=0,objects=0,nodes=0,mode=mode,mode_calls=0,mutation=mutation,sample=sample,destination=destination)
    trace=[]
    if kind in ['acc','temp','workflow']:
     for factory in (['acc','temp'] if kind=='workflow' else [kind]):
      entry=syms[roots[0 if factory=='acc' else 1]] if side else 0x89d88 if factory=='acc' else 0x8a1ac
      trace.append(invoke(u,entry,[0x12345678,0x87654321,0x11223344,0xabcdef01]))
      trace.append(invoke(u,syms[roots[5]] if side else 0x89d54,[0x89d98 if factory=='acc' else 0x8a1bc,0x87654321,0x11223344,0xabcdef01]))
    else:
     entry=syms['r1_stream_temperature_'+kind] if side else {'open':0x918fc,'close':0x918f8,'read':0x91900}[kind];trace.append(invoke(u,entry,[destination if kind=='read' else sample,length,0x11223344,0xabcdef01]))
    results.append([trace,states[id(u)]['trace'],bytes(u.mem_read(R,12)).hex(),bytes(u.mem_read(D,0x1000)).hex()])
   assert results[0]==results[1],(kind,mask,old,mode,seed,destination,length,sample,mutation,results[0][:3],results[1][:3])
   counts[kind]+=1;digest.update(json.dumps([kind,mask,old,mode,seed,destination,length,sample,mutation,results[0]],sort_keys=True).encode())
 receipt=dict(comparisons=sum(counts.values()),counts=counts,observation_counts=observations,trace_sha256=digest.hexdigest(),report_sha256=sha(rp),object_sha256=sha(obj),driver_sha256=sha(Path(__file__)),application_sha256=sha(app),evidence=evidence,provider_table_sha256=table_hashes,actual_five_bodies_object_core_memory_strings_lists=True,only_allocation_logging_calibrated_temperature_are_fixtures=True,motion_hardware_providers_not_executed=True,typed_provider_tables_match_native=True,raw_r0_callee_sp_registry_object_and_read_ram_checked=True,full_private_frame_history_verified=False,full_raw_abi_verified=False,real_sensor_provider_execution_proven=False,instruction_identity=False,whole_image_complete=False,hardware_write_executed=False)
 (OUT/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
