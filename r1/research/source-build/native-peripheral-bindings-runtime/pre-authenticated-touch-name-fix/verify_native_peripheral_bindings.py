#!/usr/bin/env python3
"""Actual registry/strcmp/slot08; repeated cached binders and callback effects."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-peripheral-bindings-runtime';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
CELLS=[('r1_motion_irq_device',0x200076b0),('r1_motion_bus_device',0x200076b4),('r1_led_enable_device',0x20007688),('r1_touch_ldo_device',0x2000768c),('r1_ppg_bus_device',0x200076cc),('r1_ppg_irq_device',0x200076d0),('r1_ppg_reset_device',0x200076d8),('r1_touch_bus_device',0x200067fc),('r1_touch_input_device',0x20006800),('r1_touch_output_device',0x20006804)]
NAMES=[(0x50144,'acc_int_1'),(0x50168,'i2c_1'),(0x502e8,'ppg_led_en'),(0x502f4,'touch_ldo_en'),(0x50978,'i2c_4'),(0x50980,'ppg_int'),(0x50988,'ppg_reset_en'),(0x51340,'i2c_0'),(0x51348,'touch_rdy_in'),(0x51358,'touch_rdy_out')]
FUNCTIONS={'r1_led_ldo_device_bind':(0x502c4,[2,3]),'r1_motion_bus_device_bind':(0x50150,[1]),'r1_motion_interrupt_input_lookup':(0x50128,[1,0]),'r1_ppg_device_bind':(0x50944,[4,5,6]),'r1_touch_device_bind':(0x51310,[7,8,9])}
def main():
 rp=OUT/'report.json';b=json.loads(rp.read_text());obj=OUT/'peripheral-bindings-source.o';assert sha(obj)==b['graph_object_sha256'] and b['graph_undefined_symbols']==[]
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 cold=(BASE/'native-scatter-data/observed-initialized-data.bin').read_bytes();assert hashlib.sha256(cold).hexdigest()=='87fdee392022fdbe23dd0daf3e859fb14f3ce26ba3e8403aab56dc9d9a913317'
 for n,a in CELLS:assert cold[a-0x200064a8:a-0x200064a8+4]==bytes(4)
 layout=ROOT/'r1/source-config/runtime/native_peripheral_bindings_verification.ld';counts={n:0 for n in FUNCTIONS};hits=dict(find=0,dispatch=0,open=0);states={};digest=hashlib.sha256()
 with tempfile.TemporaryDirectory() as tmp:
  d=Path(tmp);elf=d/'test.elf';subprocess.run(['arm-none-eabi-ld','-T',str(layout),str(obj),'-o',str(elf)],check=True,capture_output=True);sections={}
  for section in ['text']+['r1.bind.name'+str(i) for i in range(10)]:
   p=d/(section+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j','.'+section,'-O','binary',str(elf),str(p)],check=True);sections[section]=p.read_bytes()
  syms={x[2]:int(x[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x:=line.split())==3}
  for i,(a,n) in enumerate(NAMES):assert sections['r1.bind.name'+str(i)]==n.encode()+b'\0'==raw[a-0x27000:a-0x27000+len(n)+1]
  def hook(u,a,size,_):
   st=states[id(u)];source=st['source'];assert not source or not 0x27000<=a<0xc4d08
   if a==st['after_find']:
    st['after_find']=None;st['events'].append(['found',u.reg_read(UC_ARM_REG_R0)])
    if st['mutation']==1:
     for j,(_,addr) in enumerate(CELLS):u.mem_write(addr,struct.pack('<I',0x20002000+j*24))
    if st['mutation']==4:u.mem_write(0x20007680,bytes(4))
   if a==(syms['r1_stock_registry_find'] if source else 0x85ce0):
    st['events'].append(['find',u.reg_read(UC_ARM_REG_R0)]);st['after_find']=u.reg_read(UC_ARM_REG_LR)&~1
    if st['mutation']==2:u.mem_write(0x20007680,bytes(4))
   if a==(syms['r1_stock_dispatch_08'] if source else 0x85d1a):st['events'].append(['dispatch',u.reg_read(UC_ARM_REG_R0)])
   if a==0x20000200:
    st['events'].append(['open',u.reg_read(UC_ARM_REG_R0)])
    if st['mutation']==3:
     for n,addr in CELLS:u.mem_write(addr,bytes(4))
    for reg,value in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],[st['result'],0x11223344,0x55667788,0x99aabbcc]):u.reg_write(reg,value)
    u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  machines=[]
  for source in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,raw);u.mem_map(0x1000000,0x10000);u.mem_write(0x1000000,sections['text']);u.mem_map(0x20000000,0x40000);u.hook_add(UC_HOOK_CODE,hook);machines.append(u)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11];number=0
  for name,(native,indices) in FUNCTIONS.items():
   for available,cached,mutation,seed,operation in itertools.product(range(1<<len(indices)),range(1<<len(indices)),range(5),[0,0x55,0xaa,255],[0,1]):
    outputs=[]
    for source,u in enumerate(machines):
     u.mem_write(0x20000000,bytes([seed])*0x40000)
     for n,a in CELLS:u.mem_write(a,bytes(4))
     chain=[j for j in range(10) if j not in indices or available&(1<<indices.index(j))]
     for j,(a,n) in enumerate(NAMES):u.mem_write(0x20002000+j*24,struct.pack('<6I',a,0x20004000,0,0,0,0))
     for k,j in enumerate(chain):u.mem_write(0x20002000+j*24+20,struct.pack('<I',0x20002000+chain[k+1]*24 if k+1<len(chain) else 0))
     u.mem_write(0x20007680,struct.pack('<I',0x20002000+chain[0]*24 if chain else 0));u.mem_write(0x20004000,bytes(36));u.mem_write(0x20004008,struct.pack('<I',0x20000201 if operation else 0))
     for k,j in enumerate(indices):u.mem_write(CELLS[j][1],struct.pack('<I',0x20002000+j*24 if cached&(1<<k) else 0))
     states[id(u)]=dict(source=source,after_find=None,events=[],mutation=mutation,result=[0,1,0xffffffff,0x80000000][[0,0x55,0xaa,255].index(seed)]);regs=[]
     for iteration in range(2):
      u.reg_write(UC_ARM_REG_XPSR,0x01000000);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
      for reg,value in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],[0x12345678,0x11223344,0x55667788,0x99aabbcc]):u.reg_write(reg,value)
      for k,reg in enumerate(saved):u.reg_write(reg,0x12345600+k)
      u.emu_start((syms[name] if source else native)|1,0x20000100,count=20000)
      assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+k for k in range(8)];regs.append(u.reg_read(UC_ARM_REG_R0))
     mem=bytes(u.mem_read(0x20000000,0x3e000))+bytes(u.mem_read(0x2003f000,0x1000));outputs.append([regs,states[id(u)]['events'],hashlib.sha256(mem).hexdigest()])
    if outputs[0]!=outputs[1]:(OUT/'counterexample.json').write_text(json.dumps(dict(number=number,case=[name,available,cached,mutation,seed,operation],outputs=outputs),indent=2)+'\n');raise AssertionError(number)
    counts[name]+=1
    for event in outputs[0][1]:
     if event[0] in hits:hits[event[0]]+=1
    digest.update(json.dumps([number,name,available,cached,mutation,seed,operation,outputs[0]],sort_keys=True).encode());number+=1
 assert all(hits.values())
 receipt=dict(comparisons=sum(counts.values()),counts=counts,observation_counts=hits,trace_sha256=digest.hexdigest(),actual_registry_strcmp_and_dispatch=True,only_open_operation_is_fixture=True,all_local_presence_cache_masks_checked=True,repeated_calls_and_mutating_lookup_open_checked=True,raw_r0_callee_sp_nonstack_ram_checked=True,no_native_candidate_execution=True,new_zero_handle_bytes=40,new_owned_string_bytes=sum(len(n)+1 for a,n in NAMES),full_raw_abi_verified=False,cross_call_private_frame_history_verified=False,whole_context_owned=False,hardware_write_executed=False,instruction_identity=False,whole_image_complete=False,driver_sha256=sha(Path(__file__)),report_sha256=sha(rp),object_sha256=sha(obj),layout_sha256=sha(layout),application_sha256=sha(app))
 (OUT/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
