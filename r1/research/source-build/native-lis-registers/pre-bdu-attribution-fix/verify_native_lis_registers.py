#!/usr/bin/env python3
"""Native/register-kernel comparisons with explicit transport callback fixtures."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
from build_native_lis_registers import FUNCTIONS
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-lis-registers';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();SP=0x2003d000;CTX=0x2001e4d8;D=0x20010000
REGS=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3];SAVED=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
def main():
 rp=OUT/'report.json';b=json.loads(rp.read_text());obj=OUT/'registers-source.o';assert sha(obj)==b['graph_object_sha256']
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 evidence={p.name:sha(p) for p in OUT.glob('rea-*.json')};states={};counts={name:0 for name in b['roots']};obs=dict(read=0,write=0);digest=hashlib.sha256()
 with tempfile.TemporaryDirectory(prefix='r1-lis-registers-') as tmp:
  d=Path(tmp);ld=d/'layout.ld';ld.write_text('SECTIONS { .text 0x1000000 : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }');elf=d/'test.elf';binary=d/'text.bin';subprocess.run(['arm-none-eabi-ld','--gc-sections',*[v for x in b['roots'] for v in ['-u',x]],'-T',str(ld),'-e',b['roots'][0],str(obj),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-j','.text','-O','binary',str(elf),str(binary)],check=True);syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
  def put(u,a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
  def hook(u,a,size,_):
   if a not in [0x1100000,0x1100100,0x1100200]:return
   st=states[id(u)];args=[u.reg_read(x) for x in REGS];kind='read' if a==0x1100000 else 'write';st['trace'].append([kind,a,args,bytes(u.mem_read(args[2],min(args[3],4))).hex() if kind=='write' else None]);result=st['read_status'] if kind=='read' else st['write_status']
   if kind=='read':
    if st['written']:u.mem_write(args[2],struct.pack('<I',0xaabbcc00|st['old']) if st['mutation']==2 else bytes([st['old']]))
    if st['mutation']==1:put(u,CTX,0x1100201);put(u,CTX+12,0xfedcba98)
   if not st['side']:obs[kind]+=1
   for reg,v in zip(REGS,[result,0x11111111,0x22222222,0x33333333]):u.reg_write(reg,v)
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  machines=[]
  for side in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,0x40000);u.mem_write(0x1000000,binary.read_bytes());u.mem_map(0x1100000,4096);u.mem_map(0x20000000,0x40000);u.hook_add(UC_HOOK_CODE,hook);machines.append(u)
  entries={('lis2dw12_'+suffix):a for a,suffix in FUNCTIONS.items()};entries['lis2dw12_write_reg']=0x759e6
  defaults=dict(val=1,old=0x96,read_status=0,write_status=0,written=1,mutation=0,seed=0xabcdef01);cases=[]
  for name in counts:
   if name=='lis2dw12_write_reg':
    for reg,length,status in itertools.product([0,1,255,256,0xffffffff],[0,1,4,65535,65536],[0,8,0xffffffff]):cases.append(dict(defaults,name=name,val=reg,length=length,write_status=status))
    continue
   for val,old in itertools.product(range(256),[0,0x55,0xaa,255]):cases.append(dict(defaults,name=name,val=val,old=old))
   for val,old in itertools.product([0,1,3,31,255],range(256)):cases.append(dict(defaults,name=name,val=val,old=old))
   for val,old,rs,ws,written,mutation,seed in itertools.product([0,255,0xffffffff],[0,0x96,255],[0,8,0xffffffff],[0,8,0xffffffff],range(2),range(3),[0,0xabcdef01]):cases.append(dict(defaults,name=name,val=val,old=old,read_status=rs,write_status=ws,written=written,mutation=mutation,seed=seed))
  for case in cases:
   results=[];name=case['name']
   for side,u in enumerate(machines):
    u.mem_write(D,b'\x96'*64);u.mem_write(SP-2048,b'\x96'*4096);u.mem_write(CTX,struct.pack('<4I',0x1100101,0x1100001,0,0x12345678));states[id(u)]=dict(case,side=side,trace=[])
    args=[CTX,D if name=='lis2dw12_reset_get' else case['val'],D,case['seed']]
    if name=='lis2dw12_write_reg':args=[CTX,case['val'],D,case['length']]
    for reg,v in zip(REGS,args):u.reg_write(reg,v)
    for i,reg in enumerate(SAVED):u.reg_write(reg,0x12340000+i)
    u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,0x20000101);u.emu_start((syms[name] if side else entries[name])|1,0x20000100,count=10000)
    assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==SP and [u.reg_read(x) for x in SAVED]==[0x12340000+i for i in range(8)]
    results.append([u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R3) if name!='lis2dw12_write_reg' else None,states[id(u)]['trace'],bytes(u.mem_read(CTX,16)).hex(),bytes(u.mem_read(D,64)).hex()])
   assert results[0]==results[1],(case,results)
   counts[name]+=1;digest.update(json.dumps([case,results[0]],sort_keys=True).encode())
 r=dict(comparisons=sum(counts.values()),counts=counts,observation_counts=obs,trace_sha256=digest.hexdigest(),report_sha256=sha(rp),graph_sha256=sha(obj),driver_sha256=sha(Path(__file__)),application_sha256=sha(app),evidence=evidence,actual_17_attributed_bodies_native_write_proxy_and_read_proxy=True,only_transport_callbacks_are_fixtures=True,scratch_pointer_status_saved_r3_callee_sp_context_and_data_ram_checked=True,all_byte_values_and_old_register_values_tested=True,full_private_frame_history_verified=False,full_raw_abi_verified=False,real_sensor_bus_execution_proven=False,exact_vendor_checkout_proven=False,instruction_identity=False,whole_image_complete=False,hardware_write_executed=False)
 (OUT/'verification.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
if __name__=='__main__':main()
