#!/usr/bin/env python3
"""Native Bosch interface/setup/callback comparisons with explicit bus/cycle fixtures."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_INVALID
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-bma-interface';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();SP=0x2003d000;CTX=0x2001e4e8;ADDRESS=0x200076c0;BUS=0x200076b4;D=0x20010000
REGS=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3];SAVED=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
def main():
 rp=OUT/'report.json';b=json.loads(rp.read_text());obj=OUT/'interface-source.o';assert sha(obj)==b['graph_object_sha256']
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';states={};digest=hashlib.sha256();counts=dict(init=0,read=0,write=0,delay=0,check=0);obs=dict(read=0,write=0,cycles=0);faults=0
 with tempfile.TemporaryDirectory(prefix='r1-bma-interface-') as tmp:
  d=Path(tmp);ld=d/'layout.ld';ld.write_text('SECTIONS { .context 0x2001e4e8 (NOLOAD) : { *(.bss.r1.bma.context) } .address 0x200076c0 : { *(.r1.bma.bus_address) } .bus 0x200076b4 : { *(.r1.bind.r1_motion_bus_device) } .text 0x1000000 : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }');elf=d/'test.elf';binary=d/'text.bin';roots=b['roots'];subprocess.run(['arm-none-eabi-ld','--gc-sections',*[v for x in roots for v in ['-u',x]],'-T',str(ld),'-e',roots[0],'--defsym=r1_rtt_delay_cycles=0x1100301',str(obj),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-j','.text','-O','binary',str(elf),str(binary)],check=True);syms={v[2]:int(v[0],16) for l in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=l.split())==3};assert syms['r1_bma_context']==CTX and syms['r1_bma_bus_address']==ADDRESS
  def put(u,a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
  def hook(u,a,size,_):
   if a not in [0x1100000,0x1100100,0x1100300,0x9a760]:return
   st=states[id(u)];args=[u.reg_read(x) for x in REGS]
   if a in [0x1100300,0x9a760]:kind='cycles';st['trace'].append([kind,args[0]]);result=0x12345678
   else:
    kind='read' if a==0x1100000 else 'write';record=bytes(u.mem_read(args[2],20));st['trace'].append([kind,args,record.hex()]);ptr=struct.unpack_from('<I',record,12 if kind=='read' else 4)[0];length=struct.unpack_from('<H',record,16 if kind=='read' else 8)[0]
    if kind=='read' and ptr and length:u.mem_write(ptr,b'\x44')
    result=st['status']
   if not st['side']:obs[kind]+=1
   for reg,v in zip(REGS,[result,0x11111111,0x22222222,0x33333333]):u.reg_write(reg,v)
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  def invalid(u,access,a,size,value,_):states[id(u)]['fault']=[access,a,size,value];return False
  machines=[]
  for side in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,0x40000);u.mem_write(0x1000000,binary.read_bytes());u.mem_map(0x1100000,4096);u.mem_map(0x20000000,0x40000);u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_INVALID,invalid);machines.append(u)
  defaults=dict(kind='init',context=CTX,reg=0,length=1,intf=ADDRESS,bus=2,status=0,pattern=0x96,mask=7,delay=0);cases=[]
  for context,pattern in itertools.product([0,CTX,D,D+1],[0,0x96,0xff]):cases.append(dict(defaults,kind='init',context=context,pattern=pattern))
  for kind,reg,length,intf,bus,status,pattern in itertools.product(['read','write'],[0,0x26,0x80,255,256,0xffffffff],[0,1,65535,65536,0xffffffff],[ADDRESS,D+0x100,D+0x101,0],range(3),[0,8,0xffffffff],[0x18,0x96]):cases.append(dict(defaults,kind=kind,reg=reg,length=length,intf=intf,bus=bus,status=status,pattern=pattern))
  for delay in [0,1,2,3,450,1000,0x4000000,0x4000001,0xffffffff]:cases.append(dict(defaults,kind='delay',delay=delay))
  for context,mask,pattern in itertools.product([0,CTX,D,D+1],range(8),[0,0x96,0xff]):cases.append(dict(defaults,kind='check',context=context,mask=mask,pattern=pattern))
  entries=dict(init=(0x53aec,'r1_bma_interface_initialize'),read=(0x53ab4,'r1_bma_default_read'),write=(0x53ad0,'r1_bma_default_write'),delay=(0x53aa4,'r1_bma_delay_us'),check=(0x7b61c,'r1_bma4_null_pointer_check'))
  for case in cases:
   results=[];kind=case['kind']
   for side,u in enumerate(machines):
    u.mem_write(D,bytes([case['pattern']])*0x3000);u.mem_write(SP-2048,b'\x96'*4096);u.mem_write(CTX,bytes([case['pattern']])*52);put(u,ADDRESS,0x18);put(u,BUS,D+0x2000 if case['bus'] else 0);u.mem_write(D+0x2000,struct.pack('<6I',0,D+0x2100,0,0,0,0));u.mem_write(D+0x2100,struct.pack('<6I',0,0,0,0,0x1100001 if case['bus']==2 else 0,0x1100101 if case['bus']==2 else 0));states[id(u)]=dict(case,side=side,trace=[],fault=None)
    if kind=='check' and case['context']:
     for i,offset in enumerate([36,40,44]):put(u,case['context']+offset,0x1100001 if case['mask']&(1<<i) else 0)
    args=[case['context'],0x11111111,0x22222222,0x33333333]
    if kind in ['read','write']:args=[case['reg'],D,case['length'],case['intf']]
    elif kind=='delay':args=[case['delay'],0x11111111,0x22222222,0x33333333]
    for reg,v in zip(REGS,args):u.reg_write(reg,v)
    for i,reg in enumerate(SAVED):u.reg_write(reg,0x12340000+i)
    u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,0x20000101)
    try:u.emu_start((syms[entries[kind][1]] if side else entries[kind][0])|1,0x20000100,count=10000)
    except UcError as error:
     if not states[id(u)]['fault']:states[id(u)]['fault']=['cpu',str(error),u.reg_read(UC_ARM_REG_PC)]
    st=states[id(u)]
    if not st['fault']:assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==SP and [u.reg_read(x) for x in SAVED]==[0x12340000+i for i in range(8)]
    def normalized(a,size):
     block=bytearray(u.mem_read(a,size))
     if kind=='init' and case['context'] and a<=case['context'] and case['context']+52<=a+size:
      for off,name,native in [(36,'r1_bma_default_read',0x53ab5),(40,'r1_bma_default_write',0x53ad1),(44,'r1_bma_delay_us',0x53aa5)]:
       pos=case['context']-a+off;assert struct.unpack_from('<I',block,pos)[0]==((syms[name]|1) if side else native);struct.pack_into('<I',block,pos,native)
     return block.hex()
    results.append([None if st['fault'] else u.reg_read(UC_ARM_REG_R0),st['trace'],st['fault'],normalized(CTX,52),normalized(D,0x200)])
   assert results[0]==results[1],(case,results)
   counts[kind]+=1;faults+=bool(results[0][2]);digest.update(json.dumps([case,results[0]],sort_keys=True).encode())
 receipt=dict(comparisons=sum(counts.values()),counts=counts,matching_faults=faults,observation_counts=obs,trace_sha256=digest.hexdigest(),report_sha256=sha(rp),object_sha256=sha(obj),driver_sha256=sha(Path(__file__)),application_sha256=sha(app),evidence={p.name:sha(p) for p in OUT.glob('rea-*.json')},actual_four_native_entries_attributed_null_check_requests_and_registry=True,only_bus_and_cycle_callbacks_are_fixtures=True,raw_status_callee_sp_context_bytes_and_request_coordinates_checked=True,relocated_callback_function_identity_only_normalized=True,source_context_candidate_bytes=52,source_initialized_address_bytes=4,full_native_context_extent_proven=False,full_private_frame_history_verified=False,full_raw_abi_verified=False,real_sensor_bus_execution_proven=False,instruction_identity=False,whole_image_complete=False,hardware_write_executed=False)
 (OUT/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
