#!/usr/bin/env python3
"""Native Bosch FIFO count/data/product/normalizer graph with transport/log fixtures."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_INVALID
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-bma-fifo';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();SP=0x2003d000;CTX=0x2001e4e8;ADDRESS=0x200076c0;BUS=0x200076b4;D=0x20010000
REGS=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3];SAVED=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
def main():
 rp=OUT/'report.json';b=json.loads(rp.read_text());obj=OUT/'native-bma-fifo-runtime.o';assert sha(obj)==b['linked_sha256']
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';states={};digest=hashlib.sha256();counts=dict(length=0,bytes=0,fifo=0,normalized=0);obs=dict(read=0,write=0,delay=0,cycles=0,mode=0,ring=0,sdk=0,acquire=0,release=0);faults=0
 with tempfile.TemporaryDirectory(prefix='r1-bma-fifo-') as tmp:
  d=Path(tmp);ld=d/'layout.ld';ld.write_text('SECTIONS { .context 0x2001e4e8 (NOLOAD) : { *(.bss.r1.bma.context) } .address 0x200076c0 : { *(.r1.bma.bus_address) } .bus 0x200076b4 : { *(.r1.bind.r1_motion_bus_device) } .disable_ring 0x542b4 : { *(.r1.bma.fifo.disable_ring) } .disable_sdk 0x542e8 : { *(.r1.bma.fifo.disable_sdk) } .read_ring 0x54318 : { *(.r1.bma.fifo.read_ring) } .read_sdk 0x54340 : { *(.r1.bma.fifo.read_sdk) } .enable_ring 0x54364 : { *(.r1.bma.fifo.enable_ring) } .enable_sdk 0x54398 : { *(.r1.bma.fifo.enable_sdk) } .text 0x1000000 : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }');elf=d/'test.elf';binary=d/'text.bin';bindings={'r1_rtt_delay_cycles':0x1100301,'r1_structured_log_mode_get':0x1100601,'r1_structured_log_format':0x1100701,'nrf_log_frontend_std_1':0x1100801};roots=b['roots']+['r1_bma_default_read','r1_bma_default_write'];subprocess.run(['arm-none-eabi-ld','--gc-sections',*[v for x in roots for v in ['-u',x]],'-T',str(ld),'-e',roots[0],*[f'--defsym={k}={v}' for k,v in bindings.items()],str(obj),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-j','.text','-O','binary',str(elf),str(binary)],check=True);syms={v[2]:int(v[0],16) for l in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=l.split())==3}
  def put(u,a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
  def hook(u,a,size,_):
   a={0x9a760:0x1100300,0x914ec:0x1100600,0x91638:0x1100700,0x799c8:0x1100800}.get(a,a)
   if a not in [0x1100000,0x1100100,0x1100200,0x1100300,0x1100400,0x1100500,0x1100600,0x1100700,0x1100800,0x1100900,0x1100a00]:return
   st=states[id(u)];args=[u.reg_read(x) for x in REGS];result=0
   if a in [0x1100000,0x1100100,0x1100400,0x1100500]:
    kind='read' if a in [0x1100000,0x1100400] else 'write';record=None
    if a in [0x1100400,0x1100500]:record=bytes(u.mem_read(args[2],20));reg=struct.unpack_from('<H',record,2)[0];ptr=struct.unpack_from('<I',record,12 if kind=='read' else 4)[0];length=struct.unpack_from('<H',record,16 if kind=='read' else 8)[0]
    else:reg,ptr,length=args[:3]
    regbyte=reg&127;index=st['operations'];st['operations']+=1;result=st['status'] if index==st['fail_at'] else 0;st['trace'].append([kind,a,args,record.hex() if record else None,bytes(u.mem_read(ptr,min(length,8))).hex() if kind=='write' else None,result])
    if kind=='read' and st['written']:
     if regbyte==36:data=struct.pack('<H',st['wire'])
     elif regbyte==38:data=b'\xff\xff' if st['alias'] else struct.pack('<3H',0xfffd,0x8000,0x7fff)*86
     else:data=bytes([st['power']])*128
     if regbyte!=38:data=b'\xcc'*st['dummy']+data
     data=data[:min(length,512,1 if st['written']==2 else 512)];u.mem_write(ptr,data)
     if regbyte==36 and st['rebind']:put(u,CTX+36,0x1100001);put(u,CTX+4,0x87654321)
    elif kind=='write' and result==0 and regbyte==124 and length:st['power']=u.mem_read(ptr,1)[0]
   elif a in [0x1100200,0x1100300]:kind='delay' if a==0x1100200 else 'cycles';st['trace'].append([kind,args[0]])
   elif a==0x1100600:kind='mode';result=st['modes'][min(st['mode_index'],len(st['modes'])-1)];st['mode_index']+=1;st['trace'].append([kind,result])
   elif a in [0x1100900,0x1100a00]:kind='acquire' if a==0x1100900 else 'release';st['trace'].append([kind,args[0]])
   else:kind='ring' if a==0x1100700 else 'sdk';st['trace'].append([kind,args if kind=='ring' else args[:3]])
   if not st['side']:obs[kind]+=1
   for reg,v in zip(REGS,[result,0x11111111,0x22222222,0x33333333]):u.reg_write(reg,v)
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  def invalid(u,access,a,size,value,_):states[id(u)]['fault']=[access,a,size,value];return False
  machines=[]
  for side in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,0x40000);u.mem_write(0x1000000,binary.read_bytes());u.mem_map(0x1100000,4096);u.mem_map(0x20000000,0x40000);u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_INVALID,invalid);machines.append(u)
  default=dict(kind='length',wire=180,requested=30,destination=D,context=CTX,mask=7,intf=1,dummy=0,transport=0,written=1,fail_at=-1,status=8,power=1,modes=[0],rebind=0,alias=0);cases=[]
  for wire in range(65536):cases.append(dict(default,wire=wire))
  for kind,wire,requested,fail_at,status,transport,modes in itertools.product(['bytes','fifo','normalized'],[0,1,7,180,255],[0,1,2,30,31],[-1,0,1,2,3,4,5],[8,0xffffffff,256],range(2),[[0],[7],[0,4,2]]):cases.append(dict(default,kind=kind,wire=wire,requested=requested,fail_at=fail_at,status=status,transport=transport,modes=modes))
  for kind,mask,context,destination in itertools.product(counts,range(8),[0,CTX],[0,D,D+1,0x2003ffff]):cases.append(dict(default,kind=kind,mask=mask,context=context,destination=destination))
  for kind,wire,requested,intf,dummy,written,rebind in itertools.product(['length','bytes','fifo'],[0,7,16383,65535],[0,1,65536,0xffffffff],[0,1],[0,1],[0,1,2],range(2)):cases.append(dict(default,kind=kind,wire=wire,requested=requested,intf=intf,dummy=dummy,written=written,rebind=rebind))
  for kind,destination in [('bytes',SP-32),('fifo',SP-64),('normalized',SP-80)]:cases.append(dict(default,kind=kind,wire=7,requested=1,destination=destination,alias=1))
  entries=dict(length=(0x54440,'r1_bma4_get_fifo_length'),bytes=(0x544c8,'r1_bma_fifo_read_bytes'),fifo=(0x541a8,'r1_bma456w_fifo_read'),normalized=(0x6f1dc,'r1_bma456w_fifo_normalized'))
  for case in cases:
   results=[];kind=case['kind']
   for side,u in enumerate(machines):
    u.mem_write(D,b'\x96'*0x5000);u.mem_write(SP-4096,b'\x96'*8192);u.mem_write(CTX,b'\x00'*52);put(u,ADDRESS,24);put(u,CTX+4,ADDRESS);u.mem_write(CTX+8,bytes([case['intf'],0,0,case['dummy']]));u.mem_write(CTX+20,struct.pack('<HB',16,32));read=((syms['r1_bma_default_read']|1) if side else 0x53ab5) if case['transport'] else 0x1100001;write=((syms['r1_bma_default_write']|1) if side else 0x53ad1) if case['transport'] else 0x1100101;put(u,CTX+36,read if case['mask']&1 else 0);put(u,CTX+40,write if case['mask']&2 else 0);put(u,CTX+44,0x1100201 if case['mask']&4 else 0);put(u,BUS,D+0x2000);u.mem_write(D+0x2000,struct.pack('<6I',0,D+0x2100,0,0,0,0));u.mem_write(D+0x2100,struct.pack('<6I',0,0,0x1100901,0x1100a01,0x1100401,0x1100501));states[id(u)]=dict(case,side=side,trace=[],fault=None,operations=0,mode_index=0)
    args=[case['destination'],case['requested'],case['context'],0xabcdef01]
    if kind=='length':args=[case['destination'],case['context'],0x12345678,0xabcdef01]
    for reg,v in zip(REGS,args):u.reg_write(reg,v)
    for i,reg in enumerate(SAVED):u.reg_write(reg,0x12340000+i)
    u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,0x20000101)
    try:u.emu_start((syms[entries[kind][1]] if side else entries[kind][0])|1,0x20000100,count=200000)
    except UcError as error:
     if not states[id(u)]['fault']:states[id(u)]['fault']=['cpu',str(error),u.reg_read(UC_ARM_REG_PC)]
    st=states[id(u)]
    if not st['fault']:assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==SP and [u.reg_read(x) for x in SAVED]==[0x12340000+i for i in range(8)]
    context=bytearray(u.mem_read(CTX,52))
    for off,name,native in [(36,'r1_bma_default_read',0x53ab5),(40,'r1_bma_default_write',0x53ad1)]:
     if struct.unpack_from('<I',context,off)[0]==((syms[name]|1) if side else native):struct.pack_into('<I',context,off,native)
    results.append([None if st['fault'] else u.reg_read(UC_ARM_REG_R0),st['trace'],st['fault'],context.hex(),bytes(u.mem_read(D,512)).hex(),bytes(u.mem_read(0x2003fff0,16)).hex(),st['power']])
   assert results[0]==results[1],(case,results)
   if kind=='length' and case['destination']==D and case['context']==CTX and case['mask']==7 and case['dummy']==0 and case['written']==1:assert struct.unpack('<H',bytes.fromhex(results[0][4])[:2])[0]==case['wire']&16383
   counts[kind]+=1;faults+=bool(results[0][2]);digest.update(json.dumps([case,results[0]],sort_keys=True).encode())
 receipt=dict(comparisons=sum(counts.values()),counts=counts,matching_faults=faults,observation_counts=obs,trace_sha256=digest.hexdigest(),report_sha256=sha(rp),object_sha256=sha(obj),driver_sha256=sha(Path(__file__)),application_sha256=sha(app),evidence={p.name:sha(p) for p in OUT.glob('rea-*.json')},actual_three_fifo_bodies_normalizer_full_read_write_power_graph_and_registry=True,only_transport_delay_cycle_and_logging_callbacks_are_fixtures=True,all_65536_wire_lengths_against_independent_14bit_oracle=True,zero_guard_byte_length_wrap_signed_count_alias_and_failure_asymmetry_checked=True,native_callback_scratch_pointer_callee_sp_context_ram_checked=True,full_private_frame_history_verified=False,full_raw_abi_verified=False,real_sensor_bus_execution_proven=False,instruction_identity=False,whole_image_complete=False,hardware_write_executed=False)
 (OUT/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
