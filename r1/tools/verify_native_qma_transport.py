#!/usr/bin/env python3
"""Native QMA retry/identity/IRQ/FIFO graph with bus/cycle/log/event fixtures."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_INVALID
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-qma-transport';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();SP=0x2003d000;Q=0x20007698;BUS=0x200076b4;D=0x20010000
REGS=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3];SAVED=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
def main():
 rp=OUT/'report.json';b=json.loads(rp.read_text());obj=OUT/'native-qma-transport-runtime.o';assert sha(obj)==b['linked_sha256']
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';states={};digest=hashlib.sha256();counts=dict(read=0,write=0,delay=0,chip=0,irq=0,fifo=0,normalized=0);obs=dict(read=0,write=0,cycles=0,mode=0,ring=0,sdk=0,any_motion=0,double_tap=0,acquire=0,release=0);faults=0
 with tempfile.TemporaryDirectory(prefix='r1-qma-') as tmp:
  d=Path(tmp);spans=json.loads((OUT/'fifo-text-spans.json').read_text());rom=''.join(' .s'+x['address'][2:]+' '+x['address']+' : { *('+x['section']+') } ' for x in spans);ld=d/'layout.ld';ld.write_text('SECTIONS { .runtime 0x20007698 : { *(.r1.qma.runtime) } .bus 0x200076b4 : { *(.r1.bind.r1_motion_bus_device) } '+rom+' .text 0x1000000 : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }');elf=d/'test.elf';binary=d/'text.bin';bindings={'r1_rtt_delay_cycles':0x1100201,'r1_structured_log_mode_get':0x1100601,'r1_structured_log_format':0x1100701,'nrf_log_frontend_std_0':0x1100801,'nrf_log_frontend_std_1':0x1100901};subprocess.run(['arm-none-eabi-ld','--gc-sections',*[v for x in b['roots'] for v in ['-u',x]],'-T',str(ld),'-e',b['roots'][0],*[f'--defsym={k}={v}' for k,v in bindings.items()],str(obj),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-j','.text','-O','binary',str(elf),str(binary)],check=True);syms={v[2]:int(v[0],16) for l in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=l.split())==3};assert syms['r1_qma_runtime']==Q
  def put(u,a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
  def hook(u,a,size,_):
   a={0x9a6a0:0x1100200,0x914ec:0x1100600,0x91638:0x1100700,0x799c0:0x1100800,0x799c8:0x1100900}.get(a,a)
   if a not in [0x1100000,0x1100100,0x1100200,0x1100300,0x1100400,0x1100500,0x1100600,0x1100700,0x1100800,0x1100900,0x1100a00,0x1100b00]:return
   st=states[id(u)];args=[u.reg_read(x) for x in REGS];result=0
   if a in [0x1100000,0x1100100]:
    kind='read' if a==0x1100000 else 'write';rec=bytes(u.mem_read(args[2],20));reg=struct.unpack_from('<H',rec,2)[0];ptr=struct.unpack_from('<I',rec,12 if kind=='read' else 4)[0];length=struct.unpack_from('<H',rec,16 if kind=='read' else 8)[0];index=st['attempts'];st['attempts']+=1;phase='level' if reg==14 else 'payload' if reg==63 else 'reset' if reg==62 else 'normal';failed=index<st['failures'] if st['kind'] not in ['fifo','normalized'] else st['phase_fail']==phase;result=st['error'] if failed else 0;payload=bytes(u.mem_read(ptr,min(length,4))).hex() if kind=='write' else None;st['trace'].append([kind,args,rec.hex(),payload,result])
    if kind=='read' and st['written'] and ptr and length:
     data=struct.pack('<I',st['irq_bits']) if reg==9 else bytes([st['depth']]) if reg==14 else struct.pack('<3H',0xfffd,0x8000,0x7fff)*64 if reg==63 else bytes([st['byte']])*128;u.mem_write(ptr,data[:min(length,len(data))]);
     if reg==9:st['irq_pointer']=ptr
    if st['mutation']==1:u.mem_write(Q,bytes([(u.mem_read(Q,1)[0]+1)&255]))
    if st['mutation']==2 and kind=='write':u.mem_write(ptr,bytes.fromhex('aabbccdd'))
   elif a==0x1100200:kind='cycles';st['trace'].append([kind,args[0]]);result=0x12345678
   elif a in [0x1100300,0x1100400,0x1100500]:
    kind='any_motion' if a==0x1100300 else 'double_tap';st['trace'].append([kind,a,args[0]]);result=0x87654321
    if kind=='any_motion' and st['irq_mutation']:put(u,Q+4,0x1100501);u.mem_write(st['irq_pointer']+1,b'\x20')
   elif a==0x1100600:kind='mode';result=st['modes'][min(st['mode_index'],len(st['modes'])-1)];st['mode_index']+=1;st['trace'].append([kind,result])
   elif a in [0x1100a00,0x1100b00]:kind='acquire' if a==0x1100a00 else 'release';st['trace'].append([kind,args[0]])
   else:kind='ring' if a==0x1100700 else 'sdk';st['trace'].append([kind,args if kind=='ring' else args[:3] if a==0x1100900 else args[:2]])
   if not st['side']:obs[kind]+=1
   for reg,v in zip(REGS,[result,0x11111111,0x22222222,0x33333333]):u.reg_write(reg,v)
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  def invalid(u,access,a,size,value,_):states[id(u)]['fault']=[access,a,size,value];return False
  machines=[]
  for side in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,0x40000);u.mem_write(0x1000000,binary.read_bytes());u.mem_map(0x1100000,4096);u.mem_map(0x20000000,0x40000);u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_INVALID,invalid);machines.append(u)
  default=dict(kind='read',reg=0,length=1,value=0x87,units=5,destination=D,bus=2,failures=0,error=8,written=1,byte=0x90,seed=0xabcdef01,mutation=0,irq_bits=0,event_mask=3,irq_mutation=0,depth=31,requested=30,phase_fail='none',modes=[0]);cases=[]
  for reg,length,failures,bus,written,mutation in itertools.product([0,9,14,63,256,0xffffffff],[0,1,4,384,65536,0xffffffff],range(7),range(3),range(2),range(2)):cases.append(dict(default,reg=reg,length=length,failures=failures,bus=bus,written=written,mutation=mutation))
  for reg,value,failures,bus,error,mutation in itertools.product([0,62,256,0xffffffff],[0,0x87,255,0x12345678],range(7),range(3),[1,8,0xffffffff,256],range(3)):cases.append(dict(default,kind='write',reg=reg,value=value,failures=failures,bus=bus,error=error,mutation=mutation))
  for units in [0,1,5,100]:cases.append(dict(default,kind='delay',units=units))
  for seed,failures,bus,written,mutation,byte in itertools.product([0,1,0xabcdef01,0xffffffff],range(7),range(3),range(2),range(2),[0,0x90,0xfa,255]):cases.append(dict(default,kind='chip',seed=seed,failures=failures,bus=bus,written=written,mutation=mutation,byte=byte))
  for bits0,bits1,failures,event_mask,irq_mutation in itertools.product(range(8),[0,0x20],[0,1,4,5,6,9,49,50],range(4),range(2)):cases.append(dict(default,kind='irq',irq_bits=bits0|(bits1<<8),failures=failures,event_mask=event_mask,irq_mutation=irq_mutation))
  for depth,requested,phase_fail in itertools.product(range(256),[0,1,30,64,0xffffffff],['none','level','payload','reset']):cases.append(dict(default,kind='fifo',depth=depth,requested=requested,phase_fail=phase_fail))
  for kind,depth,requested,phase_fail,bus,modes in itertools.product(['fifo','normalized'],[0,1,31,64,65,127,255],[0,1,30,64,0xffffffff],['none','level','payload','reset'],range(3),[[0],[7],[0,4,2]]):cases.append(dict(default,kind=kind,depth=depth,requested=requested,phase_fail=phase_fail,bus=bus,modes=modes))
  for kind in ['read','fifo','normalized']:cases.append(dict(default,kind=kind,destination=0));cases.append(dict(default,kind=kind,destination=0x2003ffff))
  entries=dict(read=(0x8714c,'r1_qma_read_retry'),write=(0x873f4,'r1_qma_write_retry'),delay=(0x86e48,'r1_qma_delay_units'),chip=(0x86e34,'r1_qma6100_chip_id'),irq=(0x86fa8,'r1_qma6100_irq_boundary'),fifo=(0x86ff4,'r1_qma6100_bounded_fifo_read'),normalized=(0x6f448,'r1_qma6100_fifo_normalized'))
  for case in cases:
   results=[];kind=case['kind']
   for side,u in enumerate(machines):
    u.mem_write(D,b'\x96'*0x4000);u.mem_write(SP-4096,b'\x96'*8192);u.mem_write(Q,struct.pack('<3I',0x12,0x1100401 if case['event_mask']&1 else 0,0x1100301 if case['event_mask']&2 else 0));put(u,BUS,D+0x2000 if case['bus'] else 0);u.mem_write(D+0x2000,struct.pack('<6I',0,D+0x2100,0,0,0,0));u.mem_write(D+0x2100,struct.pack('<6I',0,0,0x1100a01,0x1100b01,0x1100001 if case['bus']==2 else 0,0x1100101 if case['bus']==2 else 0));states[id(u)]=dict(case,side=side,trace=[],fault=None,attempts=0,mode_index=0,irq_pointer=None)
    if kind=='read':args=[case['reg'],case['destination'],case['length'],case['seed']]
    elif kind=='write':args=[case['reg'],case['value'],0x12345678,case['seed']]
    elif kind=='delay':args=[case['units'],0x11111111,0x12345678,case['seed']]
    elif kind in ['fifo','normalized']:args=[case['destination'],case['requested'],0x12345678,case['seed']]
    else:args=[0x12345678,0x11111111,0x22222222,case['seed']]
    for reg,v in zip(REGS,args):u.reg_write(reg,v)
    for i,reg in enumerate(SAVED):u.reg_write(reg,0x12340000+i)
    u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,0x20000101)
    try:u.emu_start((syms[entries[kind][1]] if side else entries[kind][0])|1,0x20000100,count=400000)
    except UcError as error:
     if not states[id(u)]['fault']:states[id(u)]['fault']=['cpu',str(error),u.reg_read(UC_ARM_REG_PC)]
    st=states[id(u)]
    if not st['fault']:assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==SP and [u.reg_read(x) for x in SAVED]==[0x12340000+i for i in range(8)],(case,side,hex(u.reg_read(UC_ARM_REG_PC)),hex(u.reg_read(UC_ARM_REG_SP)),[hex(u.reg_read(x)) for x in SAVED],st['trace'][-8:])
    results.append([None if st['fault'] else u.reg_read(UC_ARM_REG_R0),None if st['fault'] or kind not in ['write','chip','irq','fifo'] else u.reg_read(UC_ARM_REG_R3),None if st['fault'] or kind!='write' else u.reg_read(UC_ARM_REG_R2),st['trace'],st['fault'],bytes(u.mem_read(Q,12)).hex(),bytes(u.mem_read(D,512)).hex(),bytes(u.mem_read(0x2003fff0,16)).hex()])
   assert results[0]==results[1],(case,results)
   counts[kind]+=1;faults+=bool(results[0][4]);digest.update(json.dumps([case,results[0]],sort_keys=True).encode())
 receipt=dict(comparisons=sum(counts.values()),counts=counts,matching_faults=faults,observation_counts=obs,trace_sha256=digest.hexdigest(),report_sha256=sha(rp),object_sha256=sha(obj),driver_sha256=sha(Path(__file__)),application_sha256=sha(app),evidence={p.name:sha(p) for p in OUT.glob('rea-*.json')},actual_six_qma_bodies_normalizer_motion_requests_and_registry=True,only_bus_cycle_log_and_event_callbacks_are_fixtures=True,retry_bound_last_failure_delay_fresh_address_and_irq_rebinding_checked=True,zero_length_fifo_payload_reset_ignored_errors_and_unwritten_id_checked=True,raw_r0_saved_r2_r3_callee_sp_runtime_data_and_request_pointers_checked=True,full_private_frame_history_verified=False,full_raw_abi_verified=False,real_sensor_bus_execution_proven=False,instruction_identity=False,whole_image_complete=False,hardware_write_executed=False)
 (OUT/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
