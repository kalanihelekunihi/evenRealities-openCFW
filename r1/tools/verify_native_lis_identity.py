#!/usr/bin/env python3
"""Compare native LIS identity and bus request graph with callback fixtures."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-lis-identity';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
SP=0x2003d000;CTX=0x2001e4d8;BUS=0x200076b4;D=0x20010000;REGS=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3];SAVED=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
def main():
 rp=OUT/'report.json';r=json.loads(rp.read_text());obj=OUT/'identity-source.o';assert sha(obj)==r['graph_object_sha256']
 for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 evidence={p.name:sha(p) for p in OUT.glob('rea-*.json')};states={};digest=hashlib.sha256();counts={name:0 for name in r['roots']};obs=dict(bus_read=0,bus_write=0,custom_read=0)
 with tempfile.TemporaryDirectory(prefix='r1-lis-identity-') as tmp:
  d=Path(tmp);ld=d/'layout.ld';ld.write_text('SECTIONS { .context 0x2001e4d8 (NOLOAD) : { *(.bss.r1.lis.context) } .bus 0x200076b4 : { *(.r1.bind.r1_motion_bus_device) } .text 0x1000000 : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }');elf=d/'test.elf';binary=d/'text.bin';subprocess.run(['arm-none-eabi-ld','--gc-sections',*[v for name in r['roots'] for v in ['-u',name]],'-T',str(ld),'-e',r['roots'][0],str(obj),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-j','.text','-O','binary',str(elf),str(binary)],check=True);syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
  def put(u,a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
  def norm(v,side):
   for name,native in [('r1_lis_default_read',0x7f17d),('r1_lis_default_write',0x7f189)]:
    if v==((syms[name]|1) if side else native):return name
   return v
  def hook(u,a,size,_):
   if a not in [0x1100000,0x1100100,0x1100200]:return
   st=states[id(u)];args=[u.reg_read(x) for x in REGS]
   if a==0x1100200:
    kind='custom_read';st['trace'].append([kind,args]);ptr=args[2]
   else:
    kind='bus_read' if a==0x1100000 else 'bus_write';record=bytes(u.mem_read(args[2],20));st['trace'].append([kind,args,record.hex()]);ptr=struct.unpack_from('<I',record,12 if kind=='bus_read' else 4)[0]
   if not st['side']:obs[kind]+=1
   if st['write'] and kind!='bus_write' and ptr:u.mem_write(ptr,bytes([st['value']]))
   for reg,v in zip(REGS,[st['status'],0x11111111,0x22222222,0x33333333]):u.reg_write(reg,v)
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  machines=[]
  for side in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,0x40000);u.mem_write(0x1000000,binary.read_bytes());u.mem_map(0x1100000,4096);u.mem_map(0x20000000,0x40000);u.hook_add(UC_HOOK_CODE,hook);machines.append(u)
  entries=dict(zip(r['roots'],[0x754dc,0x7517c,0x7f17c,0x7f188,0x50188,0x501c8]));cases=[]
  for name,callbacks,bus,status,write,value,seed in itertools.product(r['roots'],range(4),range(3),[0,8,0xffffffff],range(2),[0,0x44,255],[0,0xabcdef01]):cases.append(dict(name=name,callbacks=callbacks,bus=bus,status=status,write=write,value=value,seed=seed))
  for case in cases:
   results=[]
   for side,u in enumerate(machines):
    u.mem_write(D,b'\x96'*0x3000);u.mem_write(SP-2048,b'\x96'*4096)
    w=((syms['r1_lis_default_write']|1) if side else 0x7f189) if case['callbacks']&1 else 0;read=0x1100201 if case['callbacks']&2 else 0
    u.mem_write(CTX,struct.pack('<4I',w,read,0x12345678,0x87654321));put(u,BUS,D+0x1000 if case['bus'] else 0);u.mem_write(D+0x1000,struct.pack('<6I',0,D+0x1100,0,0,0,0));u.mem_write(D+0x1100,struct.pack('<6I',0,0,0,0,0x1100001 if case['bus']==2 else 0,0x1100101 if case['bus']==2 else 0));states[id(u)]=dict(case,side=side,trace=[])
    name=case['name']
    if name=='r1_lis_device_id_get':
     if not read:put(u,CTX+4,(syms['r1_lis_default_read']|1) if side else 0x7f17d)
     args=[CTX,D,0x12345678,case['seed']]
    elif name=='r1_lis2dw12_identity_probe':args=[0x12345678,0x87654321,D,case['seed']]
    else:args=[0x12345678,0x1234000f,D,case['seed']]
    for reg,v in zip(REGS,args):u.reg_write(reg,v)
    for i,reg in enumerate(SAVED):u.reg_write(reg,0x12340000+i)
    u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,0x20000101);u.emu_start((syms[name] if side else entries[name])|1,0x20000100,count=10000)
    assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==SP and [u.reg_read(x) for x in SAVED]==[0x12340000+i for i in range(8)]
    ctx=[norm(x,side) for x in struct.unpack('<4I',u.mem_read(CTX,16))];results.append([u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R3) if name=='r1_lis2dw12_identity_probe' else None,ctx,states[id(u)]['trace'],bytes(u.mem_read(D,32)).hex()])
   assert results[0]==results[1],(case,results)
   counts[name]+=1;digest.update(json.dumps([case,results[0]],sort_keys=True).encode())
 receipt=dict(comparisons=sum(counts.values()),counts=counts,observation_counts=obs,trace_sha256=digest.hexdigest(),report_sha256=sha(rp),graph_sha256=sha(obj),driver_sha256=sha(Path(__file__)),application_sha256=sha(app),evidence=evidence,actual_identity_device_id_defaults_requests_registry_and_memclr=True,only_bus_and_custom_register_callbacks_are_fixtures=True,request_record_bytes_and_pointer_checked=True,callee_sp_context_ram_and_identity_saved_r3_checked=True,full_private_frame_history_verified=False,full_raw_abi_verified=False,real_sensor_bus_execution_proven=False,instruction_identity=False,whole_image_complete=False,hardware_write_executed=False)
 (OUT/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
