#!/usr/bin/env python3
"""Command dispatcher with actual strcmp; explicit driver/delay boundaries."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-output-gpio-command-runtime';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 rp=OUT/'report.json';b=json.loads(rp.read_text());obj=OUT/'output-command-source.o';assert sha(obj)==b['graph_object_sha256']
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 layout=ROOT/'r1/source-config/runtime/native_output_gpio_command_verification.ld';cold=(BASE/'native-scatter-data/observed-initialized-data.bin').read_bytes();assert hashlib.sha256(cold).hexdigest()=='87fdee392022fdbe23dd0daf3e859fb14f3ce26ba3e8403aab56dc9d9a913317'
 ptrs=[(280,'r1_output_gpio_low',0x54f42),(284,'r1_output_gpio_high',0x54f3c),(288,'r1_output_gpio_toggle',0x54f8a),(292,'r1_output_gpio_driver0c',0x54d92),(296,'r1_output_gpio_driver10',0x54d8c),(300,'r1_output_gpio_driver14',0x54ea8),(312,'r1_output_gpio_open',0x54d98),(316,'r1_output_gpio_close',0x54c58),(320,'r1_output_gpio_slot10',0x54e20),(328,'r1_output_gpio_slot18',0x54d20),(332,'r1_output_gpio_slot1c',0x54cd0)]
 counts=dict(reject=0,missing=0,unopened=0,direct=0,delayed=0);hits=dict(compare=0,driver=0,delay=0);digest=hashlib.sha256();states={}
 with tempfile.TemporaryDirectory() as tmp:
  d=Path(tmp);elf=d/'test.elf';cmd=['arm-none-eabi-ld','-T',str(layout),str(obj),'-o',str(elf)]
  for i,n in enumerate(b['graph_undefined_symbols']):cmd+=['--defsym='+n+'='+hex(0x20000201+i*4)]
  subprocess.run(cmd,check=True,capture_output=True);p=d/'text.bin';subprocess.run(['arm-none-eabi-objcopy','-j','.text','-O','binary',str(elf),str(p)],check=True);text=p.read_bytes()
  syms={x[2]:int(x[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x:=line.split())==3}
  drivers={n:a for off,n,a in ptrs[:6]};native_hooks={a:n for n,a in drivers.items()};source_hooks={syms[n]:n for n in drivers};native_hooks[0x9a630]='delay';source_hooks[syms['r1_rtt_delay_cycles']]='delay'
  def hook(u,a,size,_):
   st=states[id(u)];source=st['source'];assert not source or not 0x27000<=a<0xc4d08
   assert a not in [0x20000200,0x20000204]
   if a==(syms['strcmp'] if source else 0x277fe):
    st['events'].append(['compare',u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1)]);st['after']=u.reg_read(UC_ARM_REG_LR)&~1
   elif a==st['after']:
    st['after']=None
    if st['mutate']==1:u.mem_write(0x20002000,struct.pack('<I',0xc0790))
   name=(source_hooks if source else native_hooks).get(a)
   if not name:return
   arg=u.reg_read(UC_ARM_REG_R0);kind='delay' if name=='delay' else 'driver';st['events'].append([kind,name,arg])
   if kind=='delay':assert arg==64000
   else:
    assert arg in [0x20007228+i*56 for i in range(5)]
    if st['mutate']==2:u.mem_write(arg+13,b'\x00')
    if st['mutate']==3:u.mem_write(arg+4,b'\x00');u.mem_write(arg+8,struct.pack('<I',0xffffffff))
   for reg,value in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],[st['result'],0x11223344,0x55667788,0x99aabbcc]):u.reg_write(reg,value)
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  machines=[]
  for source in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,raw);u.mem_map(0x1000000,0x40000);u.mem_write(0x1000000,text);u.mem_map(0x20000000,0x40000);u.hook_add(UC_HOOK_CODE,hook);machines.append(u)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11];names=[0xc0754,0xc0770,0xc0780,0xc0760,0xc0790,0x20003000]
  commands=[0,1,2,3,255,0x7fffffff,0x80000000,0x80000001,0xffffffff,0xfffffffe,0xfffffffd,0xfffffffc,0xfffffff8]
  for number,(index,opened,mode,command,mutation,seed) in enumerate(itertools.product(range(6),[0,1,255],[0,1,255],commands,range(4),[0,0x55,0xaa,255])):
   outputs=[]
   for source,u in enumerate(machines):
    u.mem_write(0x20000000,bytes([seed])*0x40000);u.mem_write(0x20007228,cold[0x20007228-0x200064a8:0x20007228-0x200064a8+340]);u.mem_write(0x20002000,struct.pack('<I',names[index]));u.mem_write(0x20003000,b'missing\0')
    patches={0x20007228+off:(syms[n]|1 if source else a|1,a|1) for off,n,a in ptrs}
    # Mapped negative indices get an explicit test target. Their real arbitrary
    # targets/fault behavior remain a separate gate; no production clamp exists.
    if command>=0x80000000:
     addr=(0x20007228+280+(12 if mode else 0)+((command<<2)&0xffffffff))&0xffffffff
     patches[addr]=(syms['r1_output_gpio_driver0c']|1 if source else 0x54d93,0x54d93)
    for j in range(5):u.mem_write(0x20007228+j*56+4,bytes([opened]));u.mem_write(0x20007228+j*56+13,bytes([mode]))
    for addr,(value,native) in patches.items():u.mem_write(addr,struct.pack('<I',value))
    states[id(u)]=dict(source=source,events=[],after=None,mutate=mutation,result=[0,1,0xffffffff,0x80000000][seed%3])
    u.reg_write(UC_ARM_REG_XPSR,0x01000000);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
    for reg,value in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],[0x20002000,command,0x55667788,0x99aabbcc]):u.reg_write(reg,value)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    u.emu_start((syms['r1_output_gpio_slot18'] if source else 0x54d20)|1,0x20000100,count=10000)
    assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
    mem=bytearray(u.mem_read(0x20000000,0x3e000))+bytearray(u.mem_read(0x2003f000,0x1000))
    if source:
     for addr,(value,native) in patches.items():assert struct.unpack_from('<I',mem,addr-0x20000000)[0]==value;struct.pack_into('<I',mem,addr-0x20000000,native)
    outputs.append([u.reg_read(UC_ARM_REG_R0),states[id(u)]['events'],hashlib.sha256(mem).hexdigest()])
   if outputs[0]!=outputs[1]:(OUT/'counterexample.json').write_text(json.dumps(dict(number=number,case=[index,opened,mode,command,mutation,seed],outputs=outputs),indent=2)+'\n');raise AssertionError(number)
   events=outputs[0][1];kinds=[e[0] for e in events]
   kind='reject' if command<0x80000000 and command>=3 else 'delayed' if 'delay' in kinds else 'direct' if 'driver' in kinds else 'unopened' if outputs[0][0]==27 else 'missing';counts[kind]+=1
   for event in events:hits[event[0]]+=1
   digest.update(json.dumps([number,index,opened,mode,command,mutation,seed,outputs[0]],sort_keys=True).encode())
 assert all(counts.values()) and all(hits.values())
 receipt=dict(comparisons=sum(counts.values()),counts=counts,observation_counts=hits,trace_sha256=digest.hexdigest(),actual_strcmp=True,only_driver_delay_are_fixtures=True,mapped_negative_and_wrapping_indices_checked=True,fresh_name_and_callback_mutations_checked=True,raw_r0_callee_sp_nonstack_ram_checked=True,no_native_candidate_execution=True,arbitrary_negative_targets_verified=False,full_raw_abi_verified=False,cross_call_private_frame_history_verified=False,hardware_write_executed=False,instruction_identity=False,whole_image_complete=False,driver_sha256=sha(Path(__file__)),report_sha256=sha(rp),object_sha256=sha(obj),layout_sha256=sha(layout),application_sha256=sha(app))
 (OUT/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
