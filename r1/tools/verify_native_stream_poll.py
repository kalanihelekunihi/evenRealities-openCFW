#!/usr/bin/env python3
"""Native poll/expiry/release graphs with explicit clock, callback and free ports."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_INVALID
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-stream-poll-runtime';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
SP=0x2003d000;H=0x2001a2bc;TICK=0x2001a2b4;D=0x20010000;REGS=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]
def main():
 rp=OUT/'report.json';r=json.loads(rp.read_text());obj=OUT/'stream-poll-source.o';assert sha(obj)==r['graph_object_sha256']
 for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 evidence={p.name:sha(p) for p in (BASE/'native-stream-poll').glob('rea-*.json')}
 for p in (BASE/'native-stream-poll').glob('rea-*.json'):
  n=json.loads(p.read_text())['structuredContent']['normalized_result'];a=int(n['address'],16);assert n['complete'] and bytes.fromhex(n['bytes_hex'])==app.read_bytes()[a-0x27000:a-0x27000+n['returned_bytes']]
 counts={k:0 for k in ['poll','expire','remaining','stop','release','elapsed']};observations=dict(tick=0,callback=0,free=0);faults=0;digest=hashlib.sha256();states={}
 with tempfile.TemporaryDirectory(prefix='r1-stream-poll-') as tmp:
  d=Path(tmp);ld=d/'layout.ld';ld.write_text('SECTIONS { .housekeeping 0x2001a2bc (NOLOAD) : { *(.bss.r1.stream.housekeeping) } .tick_getter 0x2001a2b4 (NOLOAD) : { *(.bss.r1.stream.tick_getter) } .text 0x1000000 : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }');elf=d/'test.elf';binary=d/'text.bin'
  subprocess.run(['arm-none-eabi-ld','-T',str(ld),'-e','r1_native_sensor_timer_poll',str(obj),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-j','.text','-O','binary',str(elf),str(binary)],check=True)
  syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
  def put(u,a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
  def word(u,a):return struct.unpack('<I',u.mem_read(a,4))[0]
  def hook(u,a,size,_):
   st=states[id(u)]
   if a==0x1100000:
    kind='tick';result=(st['base']+st['ticks']*st['step'])&0xffffffff;st['ticks']+=1;assert st['ticks']<200;st['trace'].append([kind,result])
    if st['mode']==1 and st['ticks']==2:put(u,D,3)
   elif a==0x1100010:
    kind='callback';timer=u.reg_read(UC_ARM_REG_R0);st['trace'].append([kind,timer]);result=0x87654321
    if st['mode']==1 and not st['mutated']:u.mem_write(H+15,b'\x01');put(u,timer+20,word(u,timer+20)|1);st['mutated']=True
    elif st['mode']==2:put(u,timer+16,0)
   elif a in [0x95d48,syms['vPortFree']]:
    kind='free';timer=u.reg_read(UC_ARM_REG_R0);st['trace'].append([kind,timer]);result=0x89abcdef;u.mem_write(timer,b'\xdd'*32)
   else:return
   if not st['side']:observations[kind]+=1
   for reg,value in zip(REGS,[result,0x11111111,0x22222222,0x33333333]):u.reg_write(reg,value)
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  def invalid(u,access,address,size,value,_):states[id(u)]['fault']=[access,address,size,value,u.reg_read(UC_ARM_REG_BASEPRI)];return False
  machines=[]
  for i in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,0x40000);u.mem_write(0x1000000,binary.read_bytes());u.mem_map(0x1100000,4096);u.mem_map(0x20000000,0x40000);u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_INVALID,invalid);machines.append(u)
  entries={'poll':(0x8a45c,'r1_native_sensor_timer_poll'),'expire':(0x8a404,'r1_stream_timer_expire'),'remaining':(0x8a5e4,'r1_stream_timer_remaining'),'stop':(0x8a584,'r1_stream_timer_stop'),'release':(0x8a3c0,'r1_stream_timer_release'),'elapsed':(0x8a1c4,'r1_stream_ticks_elapsed')};saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  for kind,base,period,repeat,flags,nodes,mode,seed in itertools.product(entries,[0,499,500,0xffffffff],[0,5,0xffffffff],[0,1,0xffffffff],range(4),[0,1,3],range(3),[0,0xaa]):
   configs=range(4) if kind=='poll' else [0]
   for config in configs:
    results=[]
    for side,u in enumerate(machines):
     u.mem_write(H,bytes(48));u.mem_write(D,bytes([seed])*1024);u.mem_write(SP-2048,b'\x96'*4096);put(u,H,24);put(u,H+4,D if nodes else 0);put(u,H+8,D+(nodes-1)*64 if nodes else 0);u.mem_write(H+12,bytes([0 if config==1 else 1]));u.mem_write(H+20,bytes([1 if config==2 else 255 if config==3 else 0]));put(u,H+28,0 if seed==0 else 0xffffffff);put(u,H+32,0 if seed==0 else (base-500)&0xffffffff);put(u,H+36,100 if seed==0 else 0xffffffff);put(u,TICK,0x1100001);u.reg_write(UC_ARM_REG_BASEPRI,0)
     for i in range(nodes):u.mem_write(D+i*64,struct.pack('<8I',period,(base-5)&0xffffffff,0x1100011,0x12345678,repeat,flags,D+(i-1)*64 if i else 0,D+(i+1)*64 if i+1<nodes else 0))
     first=(base-5)&0xffffffff if kind=='elapsed' else D if nodes else 0
     for reg,v in zip(REGS,[first,0x12345678,0x87654321,0xabcdef01]):u.reg_write(reg,v)
     for i,reg in enumerate(saved):u.reg_write(reg,0x12340000+i)
     u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,0x20000101);st=dict(side=side,trace=[],fault=None,base=base,step=0 if seed==0 else 1,ticks=0,mode=mode,mutated=False);states[id(u)]=st
     try:u.emu_start((syms[entries[kind][1]] if side else entries[kind][0])|1,0x20000100,count=200000)
     except UcError:assert st['fault'],(kind,base,period,side,hex(u.reg_read(UC_ARM_REG_PC)))
     if not st['fault']:assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==SP and [u.reg_read(reg) for reg in saved]==[0x12340000+i for i in range(8)]
     results.append([None if st['fault'] else u.reg_read(UC_ARM_REG_R0),st['trace'],st['fault'],bytes(u.mem_read(H,48)).hex(),bytes(u.mem_read(D,1024)).hex()])
    assert results[0]==results[1],(kind,base,period,repeat,flags,nodes,mode,seed,config,results)
    counts[kind]+=1;faults+=bool(results[0][2]);digest.update(json.dumps([kind,base,period,repeat,flags,nodes,mode,seed,config,results[0]],sort_keys=True).encode())
 receipt=dict(comparisons=sum(counts.values()),counts=counts,observation_counts=observations,matching_faults=faults,trace_sha256=digest.hexdigest(),report_sha256=sha(rp),object_sha256=sha(obj),driver_sha256=sha(Path(__file__)),application_sha256=sha(app),evidence=evidence,actual_poll_expire_remaining_stop_release_elapsed_unlink_and_lists=True,only_clock_timer_callback_free_are_fixtures=True,restart_fresh_flags_signed_repeat_wrap_and_500_boundary_checked=True,raw_r0_callee_sp_housekeeping_list_ram_checked=True,full_private_frame_history_verified=False,full_raw_abi_verified=False,real_clock_allocator_scheduler_proven=False,instruction_identity=False,whole_image_complete=False,hardware_write_executed=False)
 (OUT/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
