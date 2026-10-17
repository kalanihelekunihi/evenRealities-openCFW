#!/usr/bin/env python3
"""Compare attributed route logic and native frames, including all ctrl4/ctrl5 pairs."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_INVALID
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-lis-aux';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();SP=0x2003d000;CTX=0x2001e4d8;D=0x20010000
REGS=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3];SAVED=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
def main():
 rp=OUT/'report.json';b=json.loads(rp.read_text());obj=OUT/'native-lis-aux-runtime.o';assert sha(obj)==b['linked_sha256']
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';states={};digest=hashlib.sha256();counts=dict(exhaustive_set=0,matrix_set=0,get=0);obs=dict(read=0,write=0);faults=0
 with tempfile.TemporaryDirectory(prefix='r1-lis-route-') as tmp:
  d=Path(tmp);ld=d/'layout.ld';ld.write_text('SECTIONS { .text 0x1000000 : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }');elf=d/'test.elf';binary=d/'text.bin';roots=['lis2dw12_pin_int1_route_set','lis2dw12_pin_int1_route_get'];subprocess.run(['arm-none-eabi-ld','--gc-sections',*[v for x in roots for v in ['-u',x]],'-T',str(ld),'-e',roots[0],str(obj),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-j','.text','-O','binary',str(elf),str(binary)],check=True);syms={v[2]:int(v[0],16) for l in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=l.split())==3}
  def put(u,a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
  def hook(u,a,size,_):
   if a not in [0x1100000,0x1100100,0x1100200]:return
   st=states[id(u)];args=[u.reg_read(x) for x in REGS];kind='read' if a==0x1100000 else 'write';step=len(st['trace']);st['trace'].append([kind,a,args,bytes(u.mem_read(args[2],1)).hex() if kind=='write' else None]);result=st['statuses'][step]
   if kind=='read':
    if st['written']:u.mem_write(args[2],bytes([st['ctrl5'] if args[1]==0x24 else st['ctrl7'] if args[1]==0x3f else st['ctrl4']]))
    if st['mutation']==1:u.mem_write(st['pointer'],bytes([st['ctrl4']^0xff]))
    if st['mutation']==2:put(u,CTX,0x1100201);put(u,CTX+12,0x87654321)
   if not st['side']:obs[kind]+=1
   for reg,v in zip(REGS,[result,0x11111111,0x22222222,0x33333333]):u.reg_write(reg,v)
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  def invalid(u,access,a,size,value,_):states[id(u)]['fault']=[access,a,size,value];return False
  machines=[]
  for side in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,0x40000);u.mem_write(0x1000000,binary.read_bytes());u.mem_map(0x1100000,4096);u.mem_map(0x20000000,0x40000);u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_INVALID,invalid);machines.append(u)
  defaults=dict(kind='exhaustive_set',ctrl4=0,ctrl5=0,ctrl7=0,statuses=[0,0,0,0],written=1,mutation=0,pointer=D,seed2=0x12345678,seed3=0xabcdef01);cases=[]
  for c4,c5 in itertools.product(range(256),repeat=2):cases.append(dict(defaults,ctrl4=c4,ctrl5=c5,ctrl7=(c4^(c5*3))&255))
  for statuses,written,mutation,pointer,seed in itertools.product(itertools.product([0,8,0xffffffff],repeat=4),range(2),range(3),[D,D+1,SP-24,SP-20,0],[0,0xabcdef01]):cases.append(dict(defaults,kind='matrix_set',ctrl4=0x55,ctrl5=0xaa,ctrl7=0x96,statuses=list(statuses),written=written,mutation=mutation,pointer=pointer,seed2=seed^0xffffffff,seed3=seed))
  for c4,status,written,pointer in itertools.product(range(256),[0,8,0xffffffff],range(2),[D,D+1]):cases.append(dict(defaults,kind='get',ctrl4=c4,statuses=[status]*4,written=written,pointer=pointer))
  for case in cases:
   results=[]
   for side,u in enumerate(machines):
    u.mem_write(D,b'\x96'*64);u.mem_write(SP-2048,b'\x96'*4096);u.mem_write(CTX,struct.pack('<4I',0x1100101,0x1100001,0,0x12345678));
    if case['pointer']:u.mem_write(case['pointer'],bytes([case['ctrl4']]))
    states[id(u)]=dict(case,side=side,trace=[],fault=None)
    for reg,v in zip(REGS,[CTX,case['pointer'],case['seed2'],case['seed3']]):u.reg_write(reg,v)
    for i,reg in enumerate(SAVED):u.reg_write(reg,0x12340000+i)
    u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,0x20000101);name=roots[1] if case['kind']=='get' else roots[0]
    try:u.emu_start((syms[name] if side else 0x756cc if case['kind']=='get' else 0x756da)|1,0x20000100,count=10000)
    except UcError as error:
     if not states[id(u)]['fault']:states[id(u)]['fault']=['cpu',str(error),u.reg_read(UC_ARM_REG_PC)]
    st=states[id(u)]
    if not st['fault']:assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==SP and [u.reg_read(x) for x in SAVED]==[0x12340000+i for i in range(8)]
    results.append([None if st['fault'] else u.reg_read(UC_ARM_REG_R0),None if st['fault'] or case['kind']=='get' else [u.reg_read(UC_ARM_REG_R2),u.reg_read(UC_ARM_REG_R3)],st['trace'],st['fault'],bytes(u.mem_read(D,32)).hex(),bytes(u.mem_read(CTX,16)).hex()])
   assert results[0]==results[1],(case,results)
   if case['kind']=='exhaustive_set':
    expected=(case['ctrl7']&0xdf)|(0x20 if (case['ctrl4']&0xf8 or case['ctrl5']&0xc0) else 0);assert results[0][2][-1][-1]==bytes([expected]).hex()
   counts[case['kind']]+=1;faults+=bool(results[0][3]);digest.update(json.dumps([case,results[0]],sort_keys=True).encode())
 receipt=dict(comparisons=sum(counts.values()),counts=counts,matching_faults=faults,observation_counts=obs,trace_sha256=digest.hexdigest(),report_sha256=sha(rp),object_sha256=sha(obj),driver_sha256=sha(Path(__file__)),application_sha256=sha(app),actual_route_get_set_pure_st_condition_and_read_write_proxies=True,only_transport_callbacks_are_fixtures=True,all_65536_ctrl4_ctrl5_pairs_against_independent_mask_oracle=True,scratch_status_saved_r2_r3_callee_sp_context_data_and_aliases_checked=True,full_private_frame_history_verified=False,full_raw_abi_verified=False,real_sensor_bus_execution_proven=False,instruction_identity=False,whole_image_complete=False,hardware_write_executed=False)
 (OUT/'route-verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
