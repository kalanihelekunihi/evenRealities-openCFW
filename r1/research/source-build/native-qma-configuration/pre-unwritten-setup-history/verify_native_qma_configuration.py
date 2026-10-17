#!/usr/bin/env python3
"""Compare actual QMA setup graph, with only bus and cycle callback fixtures."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'r1/research/source-build/native-qma-configuration';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
SP=0x2003d000;D=0x20010000;Q=0x20007698;S=0x2001e4b0;BUS=0x200076b4
REGS=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3];SAVED=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
ENTRIES={'configure':(0x86e68,'r1_qma6100_configure_boundary'),'setup':(0x86ee4,'r1_qma_setup'),'motion':(0x86d40,'r1_qma_any_motion'),'range':(0x87188,'r1_qma_range'),'reset':(0x871c4,'r1_qma_reset'),'steps':(0x87250,'r1_qma_steps'),'tap':(0x872e4,'r1_qma_tap')}
def main():
 b=json.loads((OUT/'report.json').read_text());obj=OUT/'native-qma-configuration-runtime.o';assert sha(obj)==b['linked_sha256']
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';binary=app.read_bytes();states={};digest=hashlib.sha256();counts=dict.fromkeys(ENTRIES,0);observations=dict(read=0,write=0,cycles=0);machines=[]
 with tempfile.TemporaryDirectory(prefix='r1-qma-config-') as tmp:
  d=Path(tmp);ld=d/'layout.ld';ld.write_text('SECTIONS { .runtime 0x20007698 : { *(.r1.qma.runtime) } .bus 0x200076b4 : { *(.r1.bind.r1_motion_bus_device) } .sensor 0x2001e4b0 : { *(.r1.qma.sensor) } .axis 0x9a6a6 : { *(.r1.qma.axis) } .text 0x1000000 : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }');elf=d/'test.elf';text=d/'text.bin'
  subprocess.run(['arm-none-eabi-ld','--gc-sections',*[v for x in b['roots'] for v in ['-u',x]],'-T',str(ld),'-e',b['roots'][0],'--defsym=r1_rtt_delay_cycles=0x1100201',str(obj),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-j','.text','-O','binary',str(elf),str(text)],check=True);syms={v[2]:int(v[0],16) for l in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=l.split())==3};assert syms['r1_qma_sensor_state']==S and syms['r1_qma_axis_defaults']==0x9a6a6
  def put(u,a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
  def hook(u,a,size,_):
   if a==0x9a6a0:a=0x1100200
   if a not in [0x1100000,0x1100100,0x1100200]:return
   st=states[id(u)];args=[u.reg_read(x) for x in REGS];result=0;case=st['case']
   if a==0x1100200:kind='cycles';st['trace'].append([kind,args[0]]);result=0x12345678
   else:
    kind='read' if a==0x1100000 else 'write';rec=bytes(u.mem_read(args[2],20));reg=struct.unpack_from('<H',rec,2)[0];ptr=struct.unpack_from('<I',rec,12 if kind=='read' else 4)[0];length=struct.unpack_from('<H',rec,16 if kind=='read' else 8)[0];key=(kind,reg);index=st['attempts'].get(key,0);st['attempts'][key]=index+1
    failed=case['failure']=='all' or case['failure']=='read' and kind=='read' or case['failure']=='write' and kind=='write' or case['failure']=='four' and index%5<4
    result=8 if failed else 0;data=bytes(u.mem_read(ptr,min(length,4))).hex() if kind=='write' else None
    st['trace'].append([kind,args,rec.hex(),data,result])
    if kind=='read' and case['written']:
     value=case['chip'] if reg==0 else (0x80 if index>=case['ready'] else 0) if reg==0x11 else (5 if index>=case['ready'] else 0) if reg==0x33 else case['byte'];u.mem_write(ptr,bytes([value])*length)
    if case['mutation']:
     u.mem_write(Q,bytes([(u.mem_read(Q,1)[0]+1)&255]));u.mem_write(S+1,bytes([(u.mem_read(S+1,1)[0]+1)&255]))
   if not st['side']:observations[kind]+=1
   for reg,v in zip(REGS,[result,0x11111111,0x22222222,0x33333333]):u.reg_write(reg,v)
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  for side in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,binary);u.mem_map(0x1000000,0x40000);u.mem_write(0x1000000,text.read_bytes());u.mem_map(0x1100000,4096);u.mem_map(0x20000000,0x40000);u.hook_add(UC_HOOK_CODE,hook);machines.append(u)
  default=dict(kind='configure',args=[25,0x12345678,0xabcdef01,0x98765432],chip=0x90,byte=0xa5,ready=0,failure='none',written=1,mutation=0,bus=2,seed=0x96);cases=[]
  for kind,rate,chip,failure,mutation in itertools.product(['configure','setup'],[0,25,50,100,150,200,255,0x119,0xffffffff],[0,0x8f,0x90,0x9f,0xfa,255],['none','read','write','four','all'],range(2)):cases.append(dict(default,kind=kind,args=[rate,0x12345678,0xabcdef01,0x98765432],chip=chip,failure=failure,mutation=mutation))
  for kind,args,byte,failure,mutation in itertools.product(['motion','steps','tap'],[[0,0,0],[0,1,1],[1,1,1],[2,1,1],[0x131,0,1],[0xffffffff,1,0],[0x100,2,2]],range(0,256,17),['none','read','write','four','all'],range(2)):cases.append(dict(default,kind=kind,args=args+[0x98765432],byte=byte,failure=failure,mutation=mutation))
  for value,failure in itertools.product(list(range(256))+[0x102,0x104,0xffffffff],['none','write','four','all']):cases.append(dict(default,kind='range',args=[value,0x12345678,0xabcdef01,0x98765432],failure=failure))
  for ready,failure,written,seed in itertools.product([0,1,99,100,101,102,103],['none','read','write','four','all'],range(2),[0,0x96,255]):cases.append(dict(default,kind='reset',ready=ready,failure=failure,written=written,seed=seed))
  for kind,bus,written,seed in itertools.product(ENTRIES,range(3),range(2),[0,0x96,255]):cases.append(dict(default,kind=kind,bus=bus,written=written,seed=seed))
  for case in cases:
   results=[];kind=case['kind']
   for side,u in enumerate(machines):
    u.mem_write(D,b'\x96'*0x4000);u.mem_write(SP-4096,bytes([case['seed']])*8192);u.mem_write(S,bytes([case['seed']])*24);u.mem_write(S+1,bytes([case['chip']]));u.mem_write(Q,struct.pack('<3I',0x12,0,0));put(u,BUS,D+0x2000 if case['bus'] else 0);u.mem_write(D+0x2000,struct.pack('<6I',0,D+0x2100,0,0,0,0));u.mem_write(D+0x2100,struct.pack('<6I',0,0,0,0,0x1100001 if case['bus']==2 else 0,0x1100101 if case['bus']==2 else 0));states[id(u)]=dict(case=case,side=side,trace=[],attempts={})
    for reg,v in zip(REGS,case['args']):u.reg_write(reg,v)
    for i,reg in enumerate(SAVED):u.reg_write(reg,0x12340000+i)
    u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,0x20000101);u.emu_start((syms[ENTRIES[kind][1]] if side else ENTRIES[kind][0])|1,0x20000100,count=4000000)
    assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==SP and [u.reg_read(x) for x in SAVED]==[0x12340000+i for i in range(8)],(case,side,hex(u.reg_read(UC_ARM_REG_PC)))
    results.append([u.reg_read(UC_ARM_REG_R0),[u.reg_read(x) for x in REGS[2:]] if kind in ['configure','motion','reset'] else [],states[id(u)]['trace'],bytes(u.mem_read(S,24)).hex(),bytes(u.mem_read(Q,12)).hex()])
   assert results[0]==results[1],(case,results)
   counts[kind]+=1;digest.update(json.dumps([case,results[0]],sort_keys=True).encode())
 receipt=dict(comparisons=sum(counts.values()),counts=counts,observation_counts=observations,trace_sha256=digest.hexdigest(),report_sha256=sha(OUT/'report.json'),object_sha256=sha(obj),driver_sha256=sha(Path(__file__)),application_sha256=sha(app),evidence={p.name:sha(p) for p in OUT.glob('rea-*.json')},actual_seven_qma_bodies_transports_requests_and_registry=True,only_bus_and_cycle_callbacks_are_fixtures=True,raw_returns_saved_registers_sp_state_and_request_records_checked=True,full_private_frame_history_verified=False,full_raw_abi_verified=False,real_sensor_bus_execution_proven=False,instruction_identity=False,whole_image_complete=False,hardware_write_executed=False)
 (OUT/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
