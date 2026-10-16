#!/usr/bin/env python3
"""Native LIS FIFO plus attributed ST kernel through register callback fixtures."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_INVALID
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-lis-fifo-runtime';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
SP=0x2003d000;CTX=0x2001e4d8;BUS=0x200076b4;D=0x20010000;REGS=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]
def main():
 rp=OUT/'report.json';r=json.loads(rp.read_text());obj=OUT/'lis-fifo-source.o';assert sha(obj)==r['graph_object_sha256']
 for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 evidence={p.name:sha(p) for p in (BASE/'native-lis-fifo').glob('rea-*.json')}
 for p in (BASE/'native-lis-fifo').glob('rea-*.json'):
  n=json.loads(p.read_text())['structuredContent']['normalized_result'];a=int(n['address'],16);assert n['complete'] and bytes.fromhex(n['bytes_hex'])==app.read_bytes()[a-0x27000:a-0x27000+n['returned_bytes']]
 states={};counts=dict(proxy=0,level=0,burst=0,fifo=0,normalized=0);observations=dict(read=0,acquire=0,release=0);faults=0;digest=hashlib.sha256()
 with tempfile.TemporaryDirectory(prefix='r1-lis-fifo-') as tmp:
  d=Path(tmp);ld=d/'layout.ld';ld.write_text('SECTIONS { .context 0x2001e4d8 (NOLOAD) : { *(.bss.r1.lis.context) } .bus 0x200076b4 : { *(.r1.bind.r1_motion_bus_device) } .text 0x1000000 : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }');elf=d/'test.elf';binary=d/'text.bin'
  roots=['lis2dw12_read_reg','lis2dw12_fifo_data_level_get','r1_lis2dw12_fifo_burst_read','r1_lis2dw12_fifo_read','r1_lis2dw12_fifo_normalized'];subprocess.run(['arm-none-eabi-ld','--gc-sections',*[arg for name in roots for arg in ['-u',name]],'-T',str(ld),'-e',roots[0],str(obj),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-j','.text','-O','binary',str(elf),str(binary)],check=True)
  syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3};assert syms['r1_lis_context']==CTX
  def put(u,a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
  def hook(u,a,size,_):
   if a not in [0x1100000,0x1100100,0x1100200,0x1100210]:return
   st=states[id(u)];args=[u.reg_read(reg) for reg in REGS]
   if a in [0x1100000,0x1100100]:
    kind='read';st['trace'].append([kind,args]);result=st['status']
    if args[1]==0x2f:
     if st['read_mode']==0 and args[2]:
      if st['mutation']==2:u.mem_write(args[2],struct.pack('<I',0xaabbcc00|st['level']))
      else:u.mem_write(args[2],bytes([st['level']]))
     if st['mutation']==1:put(u,st['context']+4,0x1100101);put(u,st['context']+12,0x87654321)
    elif args[2] and args[3]:
     payload=(struct.pack('<3H',0xfffd,0x8000,0x7fff)*86)[:min(args[3],512)];u.mem_write(args[2],payload)
   else:kind='acquire' if a==0x1100200 else 'release';st['trace'].append([kind,args[0]]);result=0x12345678
   if not st['side']:observations[kind]+=1
   for reg,value in zip(REGS,[result,0x11111111,0x22222222,0x33333333]):u.reg_write(reg,value)
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  def invalid(u,access,address,size,value,_):states[id(u)]['fault']=['memory',access,address,size,value];return False
  machines=[]
  for i in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,0x40000);u.mem_write(0x1000000,binary.read_bytes());u.mem_map(0x1100000,4096);u.mem_map(0x20000000,0x40000);u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_INVALID,invalid);machines.append(u)
  defaults=dict(context_case=0,destination=D,requested=30,level=31,status=0,read_mode=0,mutation=0,bus=2,seed=0xabcdef01,reg=0x2f);cases=[]
  for value in range(256):cases.append(dict(defaults,kind='level',level=value))
  for context_case,destination,seed,level,status,read_mode in itertools.product(range(4),[D,D+1,0],[0,1,255,0xabcdef01],[0,1,63,64,255],[0,8,0xffffffff],range(2)):cases.append(dict(defaults,kind='level',context_case=context_case,destination=destination,seed=seed,level=level,status=status,read_mode=read_mode))
  for kind,level,requested,status,read_mode,mutation,bus,seed in itertools.product(['fifo','normalized'],[0,1,31,63,64,255],[0,1,2,30,31,63,256,0xffffffff],[0,8,0xffffffff],range(2),range(3),range(3),[0,0xabcdef01]):cases.append(dict(defaults,kind=kind,level=level,requested=requested,status=status,read_mode=read_mode,mutation=mutation,bus=bus,seed=seed))
  for context_case,samples,status,mutation in itertools.product(range(4),[0,1,2,30,31,32,65536,0xffffffff],[0,8,0xffffffff],range(3)):cases.append(dict(defaults,kind='burst',context_case=context_case,requested=samples,status=status,mutation=mutation))
  for context_case,reg,length,status in itertools.product(range(4),[0,0x28,0x2f,255,256],[0,1,6,65535,65536],[0,8,0xffffffff]):cases.append(dict(defaults,kind='proxy',context_case=context_case,reg=reg,requested=length,status=status))
  entries=dict(zip(counts,zip([0x757c4,0x753ac,0x750a0,0x750e8,0x6f3b4],roots)));saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  for case in cases:
   kind=case['kind'];results=[]
   for side,u in enumerate(machines):
    u.mem_write(D,b'\x96'*0x4000);u.mem_write(SP-2048,b'\x96'*4096);context=0 if case['context_case']==2 else D+0x3000 if case['context_case']==1 else CTX;u.mem_write(CTX,struct.pack('<4I',0,0 if case['context_case']==3 else 0x1100001,0,0x13579bdf));u.mem_write(D+0x3000,struct.pack('<4I',0,0x1100101,0,0x2468ace0));put(u,BUS,D+0x2000 if case['bus'] else 0);u.mem_write(D+0x2000,struct.pack('<6I',0,D+0x2100,0,0,0,0));u.mem_write(D+0x2100,struct.pack('<4I',0,0,0x1100201 if case['bus']==2 else 0,0x1100211 if case['bus']==2 else 0));states[id(u)]=dict(case,context=context,side=side,trace=[],fault=None)
    if kind=='proxy':args=[context,case['reg'],case['destination'],case['requested']]
    elif kind=='level':args=[context,case['destination'],0x12345678,case['seed']]
    elif kind=='burst':args=[context,case['destination'],case['requested'],case['seed']]
    else:args=[case['destination'],case['requested'],0x12345678,case['seed']]
    for reg,value in zip(REGS,args):u.reg_write(reg,value)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12340000+i)
    u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,0x20000101)
    try:u.emu_start((syms[entries[kind][1]] if side else entries[kind][0])|1,0x20000100,count=200000)
    except UcError as error:
     if not states[id(u)]['fault']:states[id(u)]['fault']=['cpu',str(error),u.reg_read(UC_ARM_REG_PC)]
    st=states[id(u)]
    if not st['fault']:assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==SP and [u.reg_read(reg) for reg in saved]==[0x12340000+i for i in range(8)]
    results.append([None if st['fault'] else u.reg_read(UC_ARM_REG_R0),None if st['fault'] or kind=='normalized' else u.reg_read(UC_ARM_REG_R3),st['trace'],st['fault'],bytes(u.mem_read(CTX,16)).hex(),bytes(u.mem_read(D,0x400)).hex(),bytes(u.mem_read(D+0x3000,16)).hex()])
   assert results[0]==results[1],(case,results)
   counts[kind]+=1;faults+=bool(results[0][3]);digest.update(json.dumps([case,results[0]],sort_keys=True).encode())
 receipt=dict(comparisons=sum(counts.values()),counts=counts,observation_counts=observations,matching_faults=faults,trace_sha256=digest.hexdigest(),report_sha256=sha(rp),object_sha256=sha(obj),driver_sha256=sha(Path(__file__)),application_sha256=sha(app),evidence=evidence,actual_four_entries_attributed_st_kernel_and_composed_normalizer=True,only_register_callback_and_bus_operations_are_fixtures=True,exact_register_scratch_pointer_length_status_and_saved_r3_checked=True,raw_r0_callee_sp_context_and_buffer_ram_checked=True,source_zero_context_prefix_bytes=16,full_context_size_proven=False,full_private_frame_history_verified=False,full_raw_abi_verified=False,real_context_initialization_sensor_bus_execution_proven=False,instruction_identity=False,whole_image_complete=False,hardware_write_executed=False)
 (OUT/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
