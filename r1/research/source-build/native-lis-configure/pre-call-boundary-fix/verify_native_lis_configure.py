#!/usr/bin/env python3
"""Compare native LIS configuration through actual register/default/bus providers."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-lis-configure';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();SP=0x2003d000;CTX=0x2001e4d8;BUS=0x200076b4;D=0x20010000
REGS=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3];SAVED=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
def main():
 rp=OUT/'report.json';b=json.loads(rp.read_text());obj=OUT/'configure-source.o';assert sha(obj)==b['graph_object_sha256']
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 digest=hashlib.sha256();states={};obs=dict(read=0,write=0,custom_read=0,delay=0,mode=0,ring=0,sdk=0);success=0;counts=dict(id_missing=0,reset_timeout=0,configured=0)
 with tempfile.TemporaryDirectory(prefix='r1-lis-configure-') as tmp:
  d=Path(tmp);ld=d/'layout.ld';ld.write_text('SECTIONS { .context 0x2001e4d8 (NOLOAD) : { *(.bss.r1.lis.context) } .bus 0x200076b4 : { *(.r1.bind.r1_motion_bus_device) } .id_ring 0x75664 : { *(.r1.lis.config.id_ring) } .id_sdk 0x75680 : { *(.r1.lis.config.id_sdk) } .reset_ring 0x75698 : { *(.r1.lis.config.reset_ring) } .reset_sdk 0x756b4 : { *(.r1.lis.config.reset_sdk) } .text 0x1000000 : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }')
  bindings={'nrf_delay_ms':0x1100201,'r1_structured_log_mode_get':0x1100301,'r1_structured_log_format':0x1100501,'nrf_log_frontend_std_0':0x1100601};elf=d/'test.elf';binary=d/'text.bin';subprocess.run(['arm-none-eabi-ld','--gc-sections','-u','r1_lis2dw12_configure_boundary','-T',str(ld),'-e','r1_lis2dw12_configure_boundary',*[f'--defsym={k}={v}' for k,v in bindings.items()],str(obj),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-j','.text','-O','binary',str(elf),str(binary)],check=True);syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
  def put(u,a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
  def hook(u,a,size,_):
   st=states[id(u)];native={0x7f15c:0x1100200,0x914ec:0x1100300,0x91638:0x1100500,0x799c0:0x1100600};target=native.get(a,a)
   if target not in [0x1100000,0x1100100,0x1100200,0x1100300,0x1100400,0x1100500,0x1100600]:return
   args=[u.reg_read(x) for x in REGS];result=0
   if target in [0x1100000,0x1100100,0x1100400]:
    kind='custom_read' if target==0x1100400 else 'read' if target==0x1100000 else 'write'
    if kind=='custom_read':reg,ptr,length=args[1:];record=None
    else:
     record=bytes(u.mem_read(args[2],20));reg=struct.unpack_from('<H',record,2)[0];ptr=struct.unpack_from('<I',record,4 if kind=='write' else 12)[0];length=struct.unpack_from('<H',record,8 if kind=='write' else 16)[0]
    st['trace'].append([kind,args,record.hex() if record else None,bytes(u.mem_read(ptr,length)).hex() if kind=='write' else None]);result=8 if st['transport'] else 0
    if kind=='write':
     if length:st['registers'][reg]=u.mem_read(ptr,1)[0]
     if reg==0x21:st['reset_started']=True
    else:
     if reg==0x0f:value=st['identity']
     elif reg==0x21 and st['reset_started']:value=0x40 if st['polls']<st['busy'] else 0;st['polls']+=1
     elif reg==0x2f:value=st['level']
     else:value=st['registers'].get(reg,0x96)
     if st['transport']!=1 and kind!='custom_read':
      if reg==0x28:u.mem_write(ptr,bytes((i*7+1)&255 for i in range(length)))
      else:u.mem_write(ptr,bytes([value]))
     if reg==0x0f and st['rebind']:put(u,CTX+4,0x1100401);put(u,CTX+12,0x87654321)
     if kind=='custom_read':result=8
   elif target==0x1100200:kind='delay';st['trace'].append([kind,args[0]])
   elif target==0x1100300:
    kind='mode';result=st['modes'][min(st['mode_index'],len(st['modes'])-1)];st['mode_index']+=1;st['trace'].append([kind,result])
   else:kind='ring' if target==0x1100500 else 'sdk';st['trace'].append([kind,args[:3] if kind=='ring' else args[:2]])
   if not st['side']:obs[kind]+=1
   for reg,v in zip(REGS,[result,0x11111111,0x22222222,0x33333333]):u.reg_write(reg,v)
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  machines=[]
  for side in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,0x40000);u.mem_write(0x1000000,binary.read_bytes());u.mem_map(0x1100000,4096);u.mem_map(0x20000000,0x40000);u.hook_add(UC_HOOK_CODE,hook);machines.append(u)
  cases=[]
  for rate,identity,busy,modes,bus,transport,rebind,level,pattern in itertools.product([0,25,50,100,150,200,201,0xffffffff],[0,0x44],[0,1,10,11,12],[[0],[1],[2],[4],[7],[0,4,2]],range(3),range(3),range(2),[0,1,31],[0x96,0xa5]):cases.append(dict(rate=rate,identity=identity,busy=busy,modes=modes,bus=bus,transport=transport,rebind=rebind,level=level,pattern=pattern))
  for case in cases:
   results=[]
   for side,u in enumerate(machines):
    u.mem_write(D,b'\x96'*0x3000);u.mem_write(SP-4096,bytes([case['pattern']])*8192);u.mem_write(CTX,struct.pack('<4I',0x12345679,0xabcdef01,0x13579bdf,0x2468ace0));put(u,BUS,D+0x1000 if case['bus'] else 0);u.mem_write(D+0x1000,struct.pack('<6I',0,D+0x1100,0,0,0,0));u.mem_write(D+0x1100,struct.pack('<6I',0,0,0,0,0x1100001 if case['bus']==2 else 0,0x1100101 if case['bus']==2 else 0));states[id(u)]=dict(case,side=side,trace=[],registers={},polls=0,mode_index=0,reset_started=False)
    for reg,v in zip(REGS,[case['rate'],0x11111111,0x22222222,0x33333333]):u.reg_write(reg,v)
    for i,reg in enumerate(SAVED):u.reg_write(reg,0x12340000+i)
    u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,0x20000101);u.emu_start((syms['r1_lis2dw12_configure_boundary'] if side else 0x75510)|1,0x20000100,count=100000)
    assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==SP and [u.reg_read(x) for x in SAVED]==[0x12340000+i for i in range(8)]
    ctx=list(struct.unpack('<4I',u.mem_read(CTX,16)))
    for slot,name,native in [(0,'r1_lis_default_write',0x7f189),(1,'r1_lis_default_read',0x7f17d)]:
     if ctx[slot]==((syms[name]|1) if side else native):ctx[slot]=name
    results.append([u.reg_read(UC_ARM_REG_R0),states[id(u)]['trace'],ctx,bytes(u.mem_read(SP-64,40)).hex(),states[id(u)]['registers'],states[id(u)]['polls']])
   assert results[0]==results[1],(case,results)
   category='configured' if results[0][0] else 'reset_timeout' if results[0][5]>=12 else 'id_missing';counts[category]+=1;success+=results[0][0];digest.update(json.dumps([case,results[0]],sort_keys=True).encode())
 receipt=dict(comparisons=sum(counts.values()),counts=counts,observation_counts=obs,trace_sha256=digest.hexdigest(),report_sha256=sha(rp),graph_sha256=sha(obj),driver_sha256=sha(Path(__file__)),application_sha256=sha(app),evidence={'rea-configure-bytes.json':sha(OUT/'rea-configure-bytes.json')},actual_configure_register_kernels_fifo_default_transport_and_registry=True,only_bus_custom_read_delay_and_logging_callbacks_are_fixtures=True,reset_boundary_fresh_log_mode_odr_and_fifo_drain_checked=True,raw_r0_callee_sp_context_and_outer_frame_checked=True,full_private_frame_history_verified=False,full_raw_abi_verified=False,real_sensor_bus_execution_proven=False,instruction_identity=False,whole_image_complete=False,hardware_write_executed=False)
 (OUT/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
