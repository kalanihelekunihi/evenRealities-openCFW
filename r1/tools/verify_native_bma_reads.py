#!/usr/bin/env python3
"""Native BMA read graph with explicit raw/bus/log and unresolved feature fixtures."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_INVALID
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-bma-reads';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();SP=0x2003d000;CTX=0x2001e4e8;ADDRESS=0x200076c0;BUS=0x200076b4;D=0x20010000
REGS=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3];SAVED=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
def main():
 rp=OUT/'report.json';b=json.loads(rp.read_text());obj=OUT/'native-bma-reads-runtime.o';assert sha(obj)==b['linked_sha256']
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';states={};digest=hashlib.sha256();counts=dict(direct=0,dispatch=0,power=0,identity=0);obs=dict(raw=0,bus=0,aps=0,chunk=0,mode=0,ring=0,sdk=0);faults=0
 with tempfile.TemporaryDirectory(prefix='r1-bma-reads-') as tmp:
  d=Path(tmp);ld=d/'layout.ld';ld.write_text('SECTIONS { .context 0x2001e4e8 (NOLOAD) : { *(.bss.r1.bma.context) } .address 0x200076c0 : { *(.r1.bma.bus_address) } .bus 0x200076b4 : { *(.r1.bind.r1_motion_bus_device) } .init_ring 0x53bd8 : { *(.r1.bma.id.init_ring) } .init_sdk 0x53c00 : { *(.r1.bma.id.init_sdk) } .id_ring 0x53c24 : { *(.r1.bma.id.id_ring) } .id_sdk 0x53c4c : { *(.r1.bma.id.id_sdk) } .text 0x1000000 : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }');elf=d/'test.elf';binary=d/'text.bin';bindings={'r1_bma4_set_advance_power_save_boundary':0x1100401,'r1_bma4_feature_chunk_read_boundary':0x1100501,'r1_structured_log_mode_get':0x1100601,'r1_structured_log_format':0x1100701,'nrf_log_frontend_std_1':0x1100801};subprocess.run(['arm-none-eabi-ld','--gc-sections',*[v for x in b['roots'] for v in ['-u',x]],'-T',str(ld),'-e',b['roots'][0],*[f'--defsym={k}={v}' for k,v in bindings.items()],str(obj),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-j','.text','-O','binary',str(elf),str(binary)],check=True);syms={v[2]:int(v[0],16) for l in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=l.split())==3}
  def put(u,a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
  def hook(u,a,size,_):
   native={0x5468e:0x1100400,0x87e58:0x1100500,0x914ec:0x1100600,0x91638:0x1100700,0x799c8:0x1100800};a=native.get(a,a)
   if a not in [0x1100000,0x1100200,0x1100400,0x1100500,0x1100600,0x1100700,0x1100800]:return
   st=states[id(u)];args=[u.reg_read(x) for x in REGS];result=st['status']
   if a in [0x1100000,0x1100200]:
    kind='raw' if a==0x1100000 else 'bus'
    if kind=='bus':rec=bytes(u.mem_read(args[2],20));ptr=struct.unpack_from('<I',rec,12)[0];length=struct.unpack_from('<H',rec,16)[0];st['trace'].append([kind,args,rec.hex()])
    else:ptr=args[1];length=args[2];st['trace'].append([kind,args])
    if st['written'] and length:u.mem_write(ptr,bytes([st['byte']])*min(length,128))
    if st['mutation']==1:u.mem_write(CTX+11,bytes([st['byte']&3]))
    if st['mutation']==2:put(u,CTX+36,0x1100001);put(u,CTX+4,0x87654321)
   elif a==0x1100400:kind='aps';st['trace'].append([kind,args[:2]]);result=st['aps_status']
   elif a==0x1100500:kind='chunk';st['trace'].append([kind,args[:3]]);result=st['chunk_status']
   elif a==0x1100600:kind='mode';result=st['modes'][min(st['mode_index'],len(st['modes'])-1)];st['mode_index']+=1;st['trace'].append([kind,result])
   else:kind='ring' if a==0x1100700 else 'sdk';st['trace'].append([kind,args if kind=='ring' else args[:3]]);result=0
   if not st['side']:obs[kind]+=1
   for reg,v in zip(REGS,[result,0x11111111,0x22222222,0x33333333]):u.reg_write(reg,v)
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  def invalid(u,access,a,size,value,_):states[id(u)]['fault']=[access,a,size,value];return False
  machines=[]
  for side in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,0x40000);u.mem_write(0x1000000,binary.read_bytes());u.mem_map(0x1100000,4096);u.mem_map(0x20000000,0x40000);u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_INVALID,invalid);machines.append(u)
  default=dict(kind='direct',reg=0,destination=D,length=1,dummy=0,intf=1,status=0,written=1,byte=0x16,mask=7,context=CTX,mutation=0,feature_len=32,rwlen=16,aps_status=0,chunk_status=0,modes=[0],seed=0xabcdef01,bus=2);cases=[]
  for length,dummy,intf,status,written,destination,mutation in itertools.product([0,1,2,126,128,129],[0,1,2],[0,1],[0,8,0xffffffff,256],range(2),[D,D+1,0,CTX+11,0x2003ffff],range(3)):cases.append(dict(default,kind='direct',length=length,dummy=dummy,intf=intf,status=status,written=written,destination=destination,mutation=mutation))
  for kind,mask,context in itertools.product(['direct','dispatch','power'],range(8),[0,CTX]):cases.append(dict(default,kind=kind,mask=mask,context=context))
  for length,dummy,status in itertools.product([65535,65536,0xffffffff],[0,255],[0,8]):cases.append(dict(default,length=length,dummy=dummy,status=status))
  for reg,length,feature_len,rwlen,aps_status,chunk_status,status,byte in itertools.product([0,0x5e,0x15e],[0,1,2,16,18,32,33],[0,32],[0,16],[0,8],[0,8],[0,8],[0,1]):cases.append(dict(default,kind='dispatch',reg=reg,length=length,feature_len=feature_len,rwlen=rwlen,aps_status=aps_status,chunk_status=chunk_status,status=status,byte=byte))
  for status,written,byte,destination in itertools.product([0,8,0xffffffff],range(2),range(4),[D,D+1,0]):cases.append(dict(default,kind='power',status=status,written=written,byte=byte,destination=destination))
  for mask,status,written,byte,modes,bus in itertools.product([0,1,3,7],[0,8,0xffffffff],range(2),[0,0x16,255],[[0],[1],[2],[4],[7],[0,4,2]],range(3)):cases.append(dict(default,kind='identity',mask=mask,status=status,written=written,byte=byte,modes=modes,bus=bus))
  entries=dict(direct=(0x87bbc,'r1_bma4_read_regs_direct'),dispatch=(0x54534,'r1_bma4_read_regs_boundary'),power=(0x54408,'r1_bma4_get_advance_power_save'),identity=(0x53b2c,'r1_bma456w_identity_probe'))
  for case in cases:
   results=[];kind=case['kind']
   for side,u in enumerate(machines):
    u.mem_write(D,b'\x96'*0x3000);u.mem_write(SP-4096,b'\x96'*8192);u.mem_write(CTX,b'\x96'*52);put(u,ADDRESS,0x18);put(u,CTX+4,ADDRESS);u.mem_write(CTX+8,bytes([case['intf'],0,0,case['dummy']]));u.mem_write(CTX+20,struct.pack('<HB',case['rwlen'],case['feature_len']));put(u,CTX+36,0x1100001 if case['mask']&1 else 0);put(u,CTX+40,0x1100901 if case['mask']&2 else 0);put(u,CTX+44,0x1100a01 if case['mask']&4 else 0);put(u,BUS,D+0x2000 if case['bus'] else 0);u.mem_write(D+0x2000,struct.pack('<6I',0,D+0x2100,0,0,0,0));u.mem_write(D+0x2100,struct.pack('<6I',0,0,0,0,0x1100201 if case['bus']==2 else 0,0));states[id(u)]=dict(case,side=side,trace=[],fault=None,mode_index=0)
    args=[case['reg'],case['destination'],case['length'],case['context']]
    if kind=='power':args=[case['destination'],case['context'],0x12345678,case['seed']]
    elif kind=='identity':args=[0x12345678,0x11111111,0x22222222,case['seed']]
    for reg,v in zip(REGS,args):u.reg_write(reg,v)
    for i,reg in enumerate(SAVED):u.reg_write(reg,0x12340000+i)
    u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,0x20000101)
    try:u.emu_start((syms[entries[kind][1]] if side else entries[kind][0])|1,0x20000100,count=200000)
    except UcError as error:
     if not states[id(u)]['fault']:states[id(u)]['fault']=['cpu',str(error),u.reg_read(UC_ARM_REG_PC)]
    st=states[id(u)]
    if not st['fault']:assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==SP and [u.reg_read(x) for x in SAVED]==[0x12340000+i for i in range(8)]
    context=bytearray(u.mem_read(CTX,52))
    for off,name,native in [(36,'r1_bma_default_read',0x53ab5),(40,'r1_bma_default_write',0x53ad1),(44,'r1_bma_delay_us',0x53aa5)]:
     if struct.unpack_from('<I',context,off)[0]==((syms[name]|1) if side else native):struct.pack_into('<I',context,off,native)
    results.append([None if st['fault'] else u.reg_read(UC_ARM_REG_R0),None if st['fault'] or kind=='direct' else u.reg_read(UC_ARM_REG_R3),st['trace'],st['fault'],context.hex(),bytes(u.mem_read(D,512)).hex(),bytes(u.mem_read(0x2003fff0,16)).hex()])
   assert results[0]==results[1],(case,results)
   counts[kind]+=1;faults+=bool(results[0][3]);digest.update(json.dumps([case,results[0]],sort_keys=True).encode())
 receipt=dict(comparisons=sum(counts.values()),counts=counts,matching_faults=faults,observation_counts=obs,trace_sha256=digest.hexdigest(),report_sha256=sha(rp),object_sha256=sha(obj),driver_sha256=sha(Path(__file__)),application_sha256=sha(app),evidence={p.name:sha(p) for p in OUT.glob('rea-*.json')},actual_identity_dispatch_direct_copy_nullcheck_interface_requests_registry_and_power_get=True,only_transport_log_and_two_unresolved_feature_leaves_are_fixtures=True,raw_callback_status_full_word_check_and_low_byte_store_preserved=True,feature_register_full_word_comparison_and_error_gates_checked=True,native_callback_scratch_pointer_callee_sp_context_ram_checked=True,full_private_frame_history_verified=False,full_raw_abi_verified=False,real_sensor_bus_execution_proven=False,instruction_identity=False,whole_image_complete=False,hardware_write_executed=False)
 (OUT/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
