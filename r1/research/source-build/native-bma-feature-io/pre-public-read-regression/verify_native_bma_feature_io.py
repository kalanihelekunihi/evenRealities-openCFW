#!/usr/bin/env python3
"""Native Bosch write/power/feature graph through stateful transport fixtures."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_INVALID
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-bma-feature-io';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();SP=0x2003d000;CTX=0x2001e4e8;ADDRESS=0x200076c0;BUS=0x200076b4;D=0x20010000
REGS=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3];SAVED=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
def main():
 rp=OUT/'report.json';b=json.loads(rp.read_text());obj=OUT/'native-bma-feature-io-runtime.o';assert sha(obj)==b['linked_sha256']
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';states={};digest=hashlib.sha256();counts=dict(write_direct=0,write=0,power=0,reset=0,increment=0,chunk_read=0,chunk_write=0);obs=dict(read=0,write=0,delay=0);faults=0;continued=0
 with tempfile.TemporaryDirectory(prefix='r1-bma-feature-io-') as tmp:
  d=Path(tmp);ld=d/'layout.ld';ld.write_text('SECTIONS { .context 0x2001e4e8 (NOLOAD) : { *(.bss.r1.bma.context) } .address 0x200076c0 : { *(.r1.bma.bus_address) } .bus 0x200076b4 : { *(.r1.bind.r1_motion_bus_device) } .text 0x1000000 : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }');elf=d/'test.elf';binary=d/'text.bin';roots=b['roots']+['r1_bma_default_read','r1_bma_default_write'];subprocess.run(['arm-none-eabi-ld','--gc-sections',*[v for x in roots for v in ['-u',x]],'-T',str(ld),'-e',roots[0],str(obj),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-j','.text','-O','binary',str(elf),str(binary)],check=True);syms={v[2]:int(v[0],16) for l in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=l.split())==3}
  def put(u,a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
  def hook(u,a,size,_):
   if a not in [0x1100000,0x1100100,0x1100200,0x1100300,0x1100400,0x1100500]:return
   st=states[id(u)];args=[u.reg_read(x) for x in REGS]
   if a in [0x1100200,0x1100300]:kind='delay';st['trace'].append([kind,a,args[:2]]);result=0x12345678
   else:
    kind='read' if a in [0x1100000,0x1100400] else 'write';record=None
    if a in [0x1100400,0x1100500]:record=bytes(u.mem_read(args[2],20));reg=struct.unpack_from('<H',record,2)[0];ptr=struct.unpack_from('<I',record,12 if kind=='read' else 4)[0];length=struct.unpack_from('<H',record,16 if kind=='read' else 8)[0]
    else:reg,ptr,length=args[:3]
    index=st['operations'];result=st['status'] if st['fail_at']>=0 and (index==st['fail_at'] or st['persistent'] and index>=st['fail_at']) else 0;st['operations']+=1;regbyte=reg&127
    payload=bytes(u.mem_read(ptr,min(length,64))) if kind=='write' else None
    st['trace'].append([kind,a,args,record.hex() if record else None,payload.hex() if payload else '',result])
    if kind=='read':
     if st['written'] and length:
      if regbyte==94:
       base=((st['registers'][92]<<4)|(st['registers'][91]&15))*2;data=bytes((base+i)&255 for i in range(min(length,128)))
      else:data=bytes([st['registers'].get(regbyte,0x96)])*min(length,128)
      u.mem_write(ptr,data)
    elif length and result==0:st['registers'][regbyte]=u.mem_read(ptr,1)[0]
    if st['mutation']:
     u.mem_write(CTX+50,b'\x01');put(u,CTX+44,0x1100301);put(u,CTX+4,0x87654321)
   if not st['side']:obs[kind]+=1
   for reg,v in zip(REGS,[result,0x11111111,0x22222222,0x33333333]):u.reg_write(reg,v)
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  def invalid(u,access,a,size,value,_):states[id(u)]['fault']=[access,a,size,value];return False
  machines=[]
  for side in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,0x40000);u.mem_write(0x1000000,binary.read_bytes());u.mem_map(0x1100000,4096);u.mem_map(0x20000000,0x40000);u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_INVALID,invalid);machines.append(u)
  entries=dict(zip(counts,zip([0x9756a,0x5475a,0x5468e,0x8edd8,0x70fda,0x87e58,0x976b8],b['roots'])));default=dict(kind='write_direct',reg=0x5e,length=4,val=1,rwlen=2,feature_len=32,power=0,lo=5,hi=10,perf=0,intf=1,transport=0,context=CTX,mask=7,destination=D,fail_at=-1,status=8,persistent=0,written=1,mutation=0);cases=[]
  for kind,reg,length,perf,intf,transport,fail_at,status,mutation in itertools.product(['write_direct','write'],[0,94,0xfe,0x15e],[0,1,2,16],[0,1,255],[0,1],range(2),[-1,0,1],[8,0xffffffff,256],range(2)):cases.append(dict(default,kind=kind,reg=reg,length=length,perf=perf,intf=intf,transport=transport,fail_at=fail_at,status=status,mutation=mutation))
  for kind,rwlen,length,power,fail_at,persistent,transport in itertools.product(['chunk_read','chunk_write','write'],[0,1,2,16],[0,1,2,4,16,18,32],[0,1],[0,1,3,6],range(2),range(2)):cases.append(dict(default,kind=kind,rwlen=rwlen,length=length,power=power,fail_at=fail_at,persistent=persistent,transport=transport))
  for kind,mask,context,destination in itertools.product(counts,range(8),[0,CTX],[D,0]):cases.append(dict(default,kind=kind,mask=mask,context=context,destination=destination))
  for val,power,status,fail_at,written,transport in itertools.product([0,1,2,255,0xffffffff],[0,1,0x96,255],[8,0xffffffff,256],[-1,0,1],range(2),range(2)):cases.append(dict(default,kind='power',val=val,power=power,status=status,fail_at=fail_at,written=written,transport=transport))
  for lo,hi,rwlen,fail_at in itertools.product([0,15,16,255],[0,1,255],[0,1,2,63,64,65535],[-1,0,1,2,3]):cases.append(dict(default,kind='increment',lo=lo,hi=hi,rwlen=rwlen,fail_at=fail_at))
  for length,rwlen in [(65536,32768),(98304,32768),(98305,32768),(131070,65535),(131071,65535),(196606,65535)]:cases.append(dict(default,kind='chunk_write',length=length,rwlen=rwlen,fail_at=-1))
  for case in cases:
   results=[];kind=case['kind']
   for side,u in enumerate(machines):
    u.mem_write(D,bytes(range(256))*32);u.mem_write(SP-4096,b'\x96'*8192);u.mem_write(CTX,b'\x00'*52);put(u,ADDRESS,24);put(u,CTX+4,ADDRESS);u.mem_write(CTX+8,bytes([case['intf'],0,0,0]));u.mem_write(CTX+20,struct.pack('<HBBB',case['rwlen'],case['feature_len'],case['lo'],case['hi']));u.mem_write(CTX+50,bytes([case['perf']]))
    read=((syms['r1_bma_default_read']|1) if side else 0x53ab5) if case['transport'] else 0x1100001;write=((syms['r1_bma_default_write']|1) if side else 0x53ad1) if case['transport'] else 0x1100101
    put(u,CTX+36,read if case['mask']&1 else 0);put(u,CTX+40,write if case['mask']&2 else 0);put(u,CTX+44,0x1100201 if case['mask']&4 else 0);put(u,BUS,D+0x2000);u.mem_write(D+0x2000,struct.pack('<6I',0,D+0x2100,0,0,0,0));u.mem_write(D+0x2100,struct.pack('<6I',0,0,0,0,0x1100401,0x1100501));states[id(u)]=dict(case,side=side,trace=[],fault=None,operations=0,registers={91:case['lo'],92:case['hi'],124:case['power']})
    if kind in ['write_direct','write']:args=[case['reg'],case['destination'],case['length'],case['context']]
    elif kind=='power':args=[case['val'],case['context'],0x12345678,0xabcdef01]
    elif kind in ['reset','increment']:args=[case['context'],0x11111111,0x22222222,0x33333333]
    else:args=[case['destination'],case['length'],case['context'],0xabcdef01]
    for reg,v in zip(REGS,args):u.reg_write(reg,v)
    for i,reg in enumerate(SAVED):u.reg_write(reg,0x12340000+i)
    u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,0x20000101)
    try:u.emu_start((syms[entries[kind][1]] if side else entries[kind][0])|1,0x20000100,count=300000)
    except UcError as error:
     if not states[id(u)]['fault']:states[id(u)]['fault']=['cpu',str(error),u.reg_read(UC_ARM_REG_PC)]
    st=states[id(u)]
    if not st['fault']:assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==SP and [u.reg_read(x) for x in SAVED]==[0x12340000+i for i in range(8)]
    context=bytearray(u.mem_read(CTX,52))
    for off,name,native in [(36,'r1_bma_default_read',0x53ab5),(40,'r1_bma_default_write',0x53ad1)]:
     if struct.unpack_from('<I',context,off)[0]==((syms[name]|1) if side else native):struct.pack_into('<I',context,off,native)
    results.append([None if st['fault'] else u.reg_read(UC_ARM_REG_R0),st['trace'],st['fault'],context.hex(),bytes(u.mem_read(D,512)).hex(),st['registers']])
   assert results[0]==results[1],(case,results)
   if kind=='increment' and case['fail_at']==-1 and results[0][0]==0 and not results[0][2]:
    address=(((case['hi']<<4)|(case['lo']&15))+(case['rwlen']//2));assert results[0][-1][91]==address&15 and results[0][-1][92]==(address>>4)&255
   if kind in ['chunk_read','chunk_write']:
    outcomes=[v[-1] for v in results[0][1] if v[0] in ['read','write']];continued+=any(x!=0 and any(y==0 for y in outcomes[i+1:]) for i,x in enumerate(outcomes))
   counts[kind]+=1;faults+=bool(results[0][2]);digest.update(json.dumps([case,results[0]],sort_keys=True).encode())
 receipt=dict(comparisons=sum(counts.values()),counts=counts,matching_faults=faults,continued_after_error_cases=continued,observation_counts=obs,trace_sha256=digest.hexdigest(),report_sha256=sha(rp),object_sha256=sha(obj),driver_sha256=sha(Path(__file__)),application_sha256=sha(app),evidence={p.name:sha(p) for p in OUT.glob('rea-*.json')},actual_seven_bodies_read_write_graph_helpers_nullcheck_requests_and_registry=True,only_bus_raw_transport_and_delay_callbacks_are_fixtures=True,feature_error_continuation_wrap_index_and_fresh_delay_fields_checked=True,address_updates_against_independent_oracle=True,native_callback_scratch_pointer_callee_sp_context_ram_checked=True,full_private_frame_history_verified=False,full_raw_abi_verified=False,real_sensor_bus_execution_proven=False,instruction_identity=False,whole_image_complete=False,hardware_write_executed=False)
 (OUT/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
