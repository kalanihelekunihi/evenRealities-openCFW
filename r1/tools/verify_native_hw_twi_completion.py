#!/usr/bin/env python3
"""Actual product IRQ and unchanged CMSIS state query; scheduler/release seams."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-hw-twi-completion-runtime';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
PTRS=[(44,'r1_hw_twi0_irq',0x70778),(80,'r1_hw_twi0_open',0x55278),(84,'r1_hw_twi0_close',0x55180),(88,'r1_hw_twi0_read',0x55414),(92,'r1_hw_twi0_write',0x55ce0),(152,'r1_hw_twi1_irq',0x707cc),(188,'r1_hw_twi1_open',0x552e4),(192,'r1_hw_twi1_close',0x551b4),(196,'r1_hw_twi1_read',0x55448),(200,'r1_hw_twi1_write',0x55d50)]
def main():
 rp=OUT/'report.json';b=json.loads(rp.read_text());obj=OUT/'hw-completion-source.o';assert sha(obj)==b['graph_object_sha256']
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 layout=ROOT/'r1/source-config/runtime/native_hw_twi_completion_verification.ld';cold=(BASE/'native-scatter-data/observed-initialized-data.bin').read_bytes();assert hashlib.sha256(cold).hexdigest()=='87fdee392022fdbe23dd0daf3e859fb14f3ce26ba3e8403aab56dc9d9a913317' and cold[0x20007870-0x200064a8:0x20007874-0x200064a8]==bytes(4)
 counts=dict(matrix=0,mutation=0);hits=dict(scheduler=0,release=0,null_release=0);states={};digest=hashlib.sha256()
 with tempfile.TemporaryDirectory() as tmp:
  d=Path(tmp);elf=d/'test.elf';cmd=['arm-none-eabi-ld','-T',str(layout),str(obj),'-o',str(elf)]
  for i,n in enumerate(b['graph_undefined_symbols']):cmd+=['--defsym='+n+'='+hex(0x20000401+i*4)]
  subprocess.run(cmd,check=True,capture_output=True);sections={}
  for section in ['text','r1.hw_twi.primary','r1.hw_twi.secondary']:
   p=d/(section+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j','.'+section,'-O','binary',str(elf),str(p)],check=True);sections[section]=p.read_bytes()
  syms={x[2]:int(x[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x:=line.split())==3};config=sections['r1.hw_twi.primary']+sections['r1.hw_twi.secondary'];normalized=bytearray(config)
  assert syms['KernelState']==0x20007870
  for off,n,a in PTRS:assert struct.unpack_from('<I',normalized,off)[0]==syms[n]|1;struct.pack_into('<I',normalized,off,a|1)
  stock=cold[0x20006fe8-0x200064a8:0x20006fe8-0x200064a8+216];assert bytes(normalized)==stock
  def hook(u,a,size,_):
   st=states[id(u)];source=st['source'];assert not source or not 0x27000<=a<0xc4d08
   kind=({syms['xTaskGetSchedulerState']&~1:'scheduler',syms['osSemaphoreRelease']&~1:'release'} if source else {0x987a8:'scheduler',0x7d698:'release'}).get(a)
   if not kind:assert a<0x20000400 or a>=0x20000500;return
   ret=st['scheduler'] if kind=='scheduler' else st['result'];event=[kind]
   if kind=='scheduler':
    if st['mutation']==1:u.mem_write(0x20007870,struct.pack('<I',1))
    if st['mutation']==2:u.mem_write(st['base']+4,struct.pack('<I',0x20005000))
    if st['mutation']==3:u.mem_write(st['base']+4,bytes(4));u.mem_write(st['base']+st['readyoff'],b'\x00')
    event+=[ret]
   else:event+=[u.reg_read(UC_ARM_REG_R0)]
   st['events'].append(event)
   for reg,value in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],[ret,0x11223344,0x55667788,0x99aabbcc]):u.reg_write(reg,value)
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  machines=[]
  for source in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,raw);u.mem_map(0x1000000,0x10000);u.mem_write(0x1000000,sections['text']);u.mem_map(0x20000000,0x40000);u.hook_add(UC_HOOK_CODE,hook);machines.append(u)
  cases=[]
  for bus,event,ready,sem,scheduler,seed in itertools.product(range(2),range(256),[0,1,255],[0,0x20004000],[0,1,2,3,0xffffffff],[0,0x55,0xaa,255]):cases.append(('matrix',bus,event,ready,sem,scheduler,[0,1,2,0xffffffff][seed%3],0,seed))
  for bus,event,ready,sem,scheduler,kernel,mutation,seed in itertools.product(range(2),[0,1,2,255],[0,1,255],[0,0x20004000],[0,1,2],[0,1,0xffffffff],[1,2,3],[0,0x55,0xaa,255]):cases.append(('mutation',bus,event,ready,sem,scheduler,kernel,mutation,seed))
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  for number,case in enumerate(cases):
   kind,bus,event,ready,sem,scheduler,kernel,mutation,seed=case;outputs=[];base=0x20006fe8+bus*108;readyoff=1 if bus else 2
   for source,u in enumerate(machines):
    u.mem_write(0x20000000,bytes([seed])*0x40000);u.mem_write(0x20006fe8,config if source else stock);u.mem_write(0x20003000,bytes([event]));u.mem_write(base,bytes([seed,seed,seed,seed]));u.mem_write(base+readyoff,bytes([ready]));u.mem_write(base+4,struct.pack('<II',sem,0xa55a33cc));u.mem_write(0x20007870,struct.pack('<I',kernel))
    states[id(u)]=dict(source=source,events=[],scheduler=scheduler,result=[0,1,0xffffffff,0x80000000][[0,0x55,0xaa,255].index(seed)],mutation=mutation,base=base,readyoff=readyoff);regs=[]
    for iteration in range(2):
     u.reg_write(UC_ARM_REG_XPSR,0x01000000);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
     for reg,value in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],[0x20003000,0x11223344,0x55667788,0x99aabbcc]):u.reg_write(reg,value)
     for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
     u.emu_start((syms['r1_hw_twi'+str(bus)+'_irq'] if source else [0x70778,0x707cc][bus])|1,0x20000100,count=10000)
     assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)];regs.append(u.reg_read(UC_ARM_REG_R0))
    mem=bytearray(u.mem_read(0x20000000,0x3e000))+bytearray(u.mem_read(0x2003f000,0x1000))
    if source:
     for off,n,a in PTRS:assert struct.unpack_from('<I',mem,0x6fe8+off)[0]==syms[n]|1;struct.pack_into('<I',mem,0x6fe8+off,a|1)
    outputs.append([regs,states[id(u)]['events'],hashlib.sha256(mem).hexdigest()])
   if outputs[0]!=outputs[1]:(OUT/'counterexample.json').write_text(json.dumps(dict(number=number,case=case,outputs=outputs),indent=2)+'\n');raise AssertionError(number)
   counts[kind]+=1
   for event in outputs[0][1]:hits[event[0]]+=1;hits['null_release']+=int(event[0]=='release' and event[1]==0)
   digest.update(json.dumps([number,case,outputs[0]],sort_keys=True).encode())
 assert all(hits.values())
 receipt=dict(comparisons=sum(counts.values()),counts=counts,observation_counts=hits,trace_sha256=digest.hexdigest(),actual_irq_and_pinned_cmsis_kernel_query=True,only_scheduler_and_semaphore_release_are_fixtures=True,all_event_bytes_and_bus_flag_asymmetry_checked=True,fresh_handle_after_state_query_checked=True,repeated_event_calls_checked=True,raw_r0_callee_sp_nonstack_ram_checked=True,no_native_candidate_execution=True,full_raw_abi_verified=False,cross_call_private_frame_history_verified=False,physical_irq_and_semaphore_delivery_proven=False,metadata_callback_abi_migrated=False,hardware_write_executed=False,instruction_identity=False,whole_image_complete=False,driver_sha256=sha(Path(__file__)),report_sha256=sha(rp),object_sha256=sha(obj),layout_sha256=sha(layout),application_sha256=sha(app))
 (OUT/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
