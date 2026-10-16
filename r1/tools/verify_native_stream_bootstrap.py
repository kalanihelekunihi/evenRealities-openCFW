#!/usr/bin/env python3
"""Stream bootstrap with real list/CMSIS dispatch and explicit external fixtures."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_INVALID
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-stream-bootstrap-runtime';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
SP=0x2003d000;H=0x2001a2bc;TICK=0x2001a2b4;D=0x20010000;OLD=D+256;REGS=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]
def main():
 rp=OUT/'report.json';r=json.loads(rp.read_text());obj=OUT/'stream-bootstrap-source.o';assert sha(obj)==r['graph_object_sha256']
 for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 evidence={p.name:sha(p) for p in (BASE/'native-stream-bootstrap').glob('rea-*.json')}
 for p in (BASE/'native-stream-bootstrap').glob('rea-*.json'):
  n=json.loads(p.read_text())['structuredContent']['normalized_result'];a=int(n['address'],16);assert n['complete'] and bytes.fromhex(n['bytes_hex'])==app.read_bytes()[a-0x27000:a-0x27000+n['returned_bytes']]
 counts={k:0 for k in ['initialize','create','wake','enable','tick','keepalive']};observations=dict(allocate=0,tick=0,wake=0);faults=0;digest=hashlib.sha256();states={}
 with tempfile.TemporaryDirectory(prefix='r1-stream-bootstrap-') as tmp:
  d=Path(tmp);ld=d/'layout.ld';ld.write_text('SECTIONS { .housekeeping 0x2001a2bc (NOLOAD) : { *(.bss.r1.stream.housekeeping) } .tick_getter 0x2001a2b4 (NOLOAD) : { *(.bss.r1.stream.tick_getter) } .keepalive 0x8a558 : { *(.text.r1_stream_keepalive) } .text 0x1000000 : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }');elf=d/'test.elf';binary=d/'text.bin';keep=d/'keep.bin'
  subprocess.run(['arm-none-eabi-ld','-T',str(ld),'-e','r1_native_stream_initialize',str(obj),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-j','.text','-O','binary',str(elf),str(binary)],check=True);subprocess.run(['arm-none-eabi-objcopy','-j','.keepalive','-O','binary',str(elf),str(keep)],check=True);assert keep.read_bytes()==app.read_bytes()[0x8a558-0x27000:0x8a55a-0x27000]
  syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
  def put(u,a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
  def hook(u,a,size,_):
   st=states[id(u)];args=[u.reg_read(reg) for reg in REGS]
   if a in [0x855a0,syms['pvPortMalloc']]:
    st['trace'].append(['allocate',args[0]]);result=D if st['allocate'] else 0;kind='allocate'
    if st['mode']==1:put(u,H+16,0x12345678)
   elif a in [0x987c4,0x987d0,syms['xTaskGetTickCount'],syms['xTaskGetTickCountFromISR'],0x1100000]:
    st['trace'].append(['tick',args[0] if a==0x1100000 else None]);result=st['tick'];kind='tick'
    if st['mode']==1:put(u,D+20,0xfffffff1);put(u,H+40,0);put(u,H+44,0xabcdef01)
   elif a==0x1100010:
    st['trace'].append(['wake',args[0],args[1]]);result=0x87654321;kind='wake'
    if st['mode']==2:put(u,H+16,0x12345678);u.mem_write(H+15,b'\xff');put(u,H+44,0xabcdef01)
   else:return
   if not st['side']:observations[kind]+=1
   for reg,value in zip(REGS,[result,0x11111111,0x22222222,0x33333333]):u.reg_write(reg,value)
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  def invalid(u,access,address,size,value,_):states[id(u)]['fault']=[access,address,size,value,u.reg_read(UC_ARM_REG_BASEPRI)];return False
  machines=[]
  for i in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,0x40000);u.mem_write(0x1000000,binary.read_bytes());u.mem_map(0x1100000,4096);u.mem_map(0x20000000,0x40000);u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_INVALID,invalid);machines.append(u)
  entries={'initialize':(0x8a55c,'r1_native_stream_initialize'),'create':(0x8a310,'r1_stream_timer_create_front'),'wake':(0x8a540,'r1_stream_wake'),'enable':(0x8a3f0,'r1_stream_enable'),'tick':(0x8a1d0,'r1_stream_tick_now'),'keepalive':(0x8a558,'r1_stream_keepalive')};saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  for kind,value,custom,wake,allocate,mode,old,seed in itertools.product(entries,[0,1,255,256,0xffffffff],range(2),range(2),range(2),range(3),range(2),[0,0xaa]):
   results=[]
   for side,u in enumerate(machines):
    u.mem_write(H,bytes([seed])*48);u.mem_write(D,bytes([seed])*512);u.mem_write(SP-1024,b'\x96'*2048);put(u,H,24);put(u,H+4,OLD if old else 0);put(u,H+8,OLD if old else 0);put(u,OLD+24,0);put(u,OLD+28,0);put(u,H+40,0x1100011 if wake else 0);put(u,H+44,D+0x180);put(u,TICK,0x1100001 if custom else 0);u.reg_write(UC_ARM_REG_BASEPRI,0)
    args=[value,0x12345678,0x87654321,0xabcdef01]
    if kind=='create':args=[0x1100101,value,0x87654321,0xabcdef01]
    for reg,v in zip(REGS,args):u.reg_write(reg,v)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12340000+i)
    u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,0x20000101);st=dict(side=side,trace=[],fault=None,tick=value,mode=mode,allocate=allocate);states[id(u)]=st
    try:u.emu_start((syms[entries[kind][1]] if side else entries[kind][0])|1,0x20000100,count=100000)
    except UcError:assert st['fault'],(kind,value,side,hex(u.reg_read(UC_ARM_REG_PC)))
    if not st['fault']:assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==SP and [u.reg_read(reg) for reg in saved]==[0x12340000+i for i in range(8)]
    results.append([None if st['fault'] else u.reg_read(UC_ARM_REG_R0),st['trace'],st['fault'],bytes(u.mem_read(H,48)).hex(),bytes(u.mem_read(D,512)).hex()])
   assert results[0]==results[1],(kind,value,custom,wake,allocate,mode,old,seed,results)
   counts[kind]+=1;faults+=bool(results[0][2]);digest.update(json.dumps([kind,value,custom,wake,allocate,mode,old,seed,results[0]],sort_keys=True).encode())
 receipt=dict(comparisons=sum(counts.values()),counts=counts,observation_counts=observations,matching_fatal_faults=faults,trace_sha256=digest.hexdigest(),report_sha256=sha(rp),object_sha256=sha(obj),driver_sha256=sha(Path(__file__)),application_sha256=sha(app),evidence=evidence,keepalive_instruction_bytes=2,actual_six_bodies_lists_and_cmsis_dispatch=True,allocator_clock_leaf_wake_callbacks_are_fixtures=True,raw_r0_callee_sp_housekeeping_list_ram_checked=True,source_zero_bytes=52,full_private_frame_history_verified=False,full_raw_abi_verified=False,actual_allocator_clock_scheduler_execution_proven=False,instruction_identity=False,whole_image_complete=False,hardware_write_executed=False)
 (OUT/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
