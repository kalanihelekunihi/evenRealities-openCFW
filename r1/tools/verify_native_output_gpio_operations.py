#!/usr/bin/env python3
"""Actual strcmp/Nordic decoder; RAM and MMIO-register differential checks."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-output-gpio-operations-runtime';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 rp=OUT/'report.json';b=json.loads(rp.read_text());obj=OUT/'output-operations-source.o';assert sha(obj)==b['graph_object_sha256']
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 layout=ROOT/'r1/source-config/runtime/native_output_gpio_operations_verification.ld';cold=(BASE/'native-scatter-data/observed-initialized-data.bin').read_bytes();assert hashlib.sha256(cold).hexdigest()=='87fdee392022fdbe23dd0daf3e859fb14f3ce26ba3e8403aab56dc9d9a913317'
 counts=dict(config=0,read=0,toggle=0);digest=hashlib.sha256();observations=0
 with tempfile.TemporaryDirectory() as tmp:
  d=Path(tmp);elf=d/'test.elf';cmd=['arm-none-eabi-ld','-T',str(layout),str(obj),'-o',str(elf)]
  for i,n in enumerate(b['graph_undefined_symbols']):cmd+=['--defsym='+n+'='+hex(0x20000201+i*4)]
  subprocess.run(cmd,check=True,capture_output=True);sections={}
  for section in ['text','r1.output_gpio.configuration']+['r1.output_gpio.name'+str(i) for i in range(5)]:
   p=d/(section+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j','.'+section,'-O','binary',str(elf),str(p)],check=True);sections[section]=p.read_bytes()
  syms={x[2]:int(x[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x:=line.split())==3}
  ptrs=[(280,'r1_output_gpio_low',0x54f42),(284,'r1_output_gpio_high',0x54f3c),(288,'r1_output_gpio_toggle',0x54f8a),(292,'r1_output_gpio_driver0c',0x54d92),(296,'r1_output_gpio_driver10',0x54d8c),(300,'r1_output_gpio_driver14',0x54ea8),(312,'r1_output_gpio_open',0x54d98),(316,'r1_output_gpio_close',0x54c58),(320,'r1_output_gpio_slot10',0x54e20),(328,'r1_output_gpio_slot18',0x54d20),(332,'r1_output_gpio_slot1c',0x54cd0)]
  config=sections['r1.output_gpio.configuration'];stock_config=cold[0x20007228-0x200064a8:0x20007228-0x200064a8+340];normalized=bytearray(config)
  for off,n,a in ptrs:assert struct.unpack_from('<I',config,off)[0]==syms[n]|1;struct.pack_into('<I',normalized,off,a|1)
  assert bytes(normalized)==stock_config
  for i,a in enumerate([0xc0754,0xc0770,0xc0780,0xc0760,0xc0790]):assert sections['r1.output_gpio.name'+str(i)]==raw[a-0x27000:a-0x27000+len(sections['r1.output_gpio.name'+str(i)])]
  machines=[];states={}
  def hook(u,a,size,_):
   st=states[id(u)];source=st['source'];assert not source or not 0x27000<=a<0xc4d08
   assert a not in [0x20000200,0x20000204,0x20000208]
   if a==(syms['strcmp'] if source else 0x277fe):
    p=u.reg_read(UC_ARM_REG_R0);q=u.reg_read(UC_ARM_REG_R1);st['calls'].append([p,q]);st['after']=u.reg_read(UC_ARM_REG_LR)&~1
   elif a==st['after']:
    st['after']=None
    if st['mutate'] and len(st['calls'])==1:u.mem_write(0x20002000,struct.pack('<I',0xc0790))
  for source in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,raw);u.mem_map(0x1000000,0x40000);u.mem_write(0x1000000,sections['text']);u.mem_map(0x20000000,0x40000);u.mem_map(0x50000000,4096);u.hook_add(UC_HOOK_CODE,hook);machines.append(u)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11];names=[0xc0754,0xc0770,0xc0780,0xc0760,0xc0790,0x20003000]
  cases=[]
  for index,opened,alias,seed,mutate in itertools.product(range(6),[0,1,255],[0,1,2,3,4,5], [0,0x55,0xaa,255],[False,True]):cases.append(('config',index,opened,alias,seed,mutate,0,0))
  for index,opened,pin,pattern,alias,mutate in itertools.product(range(6),[0,1,2,255],[0,1,17,31,32,33,47,48,63,255,0x80000000,0xffffffff],[0,0xffffffff,0xa55a33cc],[0,1,2,3],[False,True]):cases.append(('read',index,opened,alias,0x6d,mutate,pin,pattern))
  for pin,pattern,seed in itertools.product([*range(256),256,65535,0x80000000,0xffffffff],[0,0xffffffff,0xa55a33cc,0x5aa5cc33],[0,0x55,0xaa,255]):cases.append(('toggle',0,1,0,seed,False,pin,pattern))
  for number,case in enumerate(cases):
   kind,index,opened,alias,seed,mutate,pin,pattern=case;outputs=[]
   for source,u in enumerate(machines):
    u.mem_write(0x20000000,bytes([seed])*0x40000);u.mem_write(0x20007228,config if source else stock_config);u.mem_write(0x20002000,struct.pack('<I',names[index]));u.mem_write(0x20003000,b'missing\0');u.mem_write(0x20004000,struct.pack('<III',0x123456ab,0x87654321,0xabcdef01));u.mem_write(0x50000000,struct.pack('<I',pattern)*1024)
    for j in range(5):u.mem_write(0x20007228+j*56+4,bytes([opened]));u.mem_write(0x20007228+j*56+8,struct.pack('<I',pin))
    rec=0x20007228+min(index,4)*56
    if kind=='config':args=[0x20002000,[0,0x20004000,rec+20,rec+24,rec+16,rec+28][alias],0x55667788,0x99aabbcc];native=0x54cd0;name='r1_output_gpio_slot1c'
    elif kind=='read':args=[0x20002000,0xdeadbeef,[0x20005000,rec+4,rec+8,rec+12][alias],0x99aabbcc];native=0x54e20;name='r1_output_gpio_slot10'
    else:args=[rec,0x11223344,0x55667788,0x99aabbcc];native=0x54ea8;name='r1_output_gpio_driver14'
    states[id(u)]=dict(source=source,calls=[],after=None,mutate=mutate)
    u.reg_write(UC_ARM_REG_XPSR,0x01000000);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
    for reg,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],args):u.reg_write(reg,v)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    u.emu_start((syms[name] if source else native)|1,0x20000100,count=10000)
    assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
    mem=bytearray(u.mem_read(0x20000000,0x3e000))+bytearray(u.mem_read(0x2003f000,0x1000))
    if source:
     for off,n,a in ptrs:assert struct.unpack_from('<I',mem,0x7228+off)[0]==syms[n]|1;struct.pack_into('<I',mem,0x7228+off,a|1)
    regs=[u.reg_read(UC_ARM_REG_R0)]
    if kind!='config':regs.append(u.reg_read(UC_ARM_REG_R3))
    outputs.append([regs,states[id(u)]['calls'],hashlib.sha256(mem).hexdigest(),bytes(u.mem_read(0x50000000,4096)).hex()])
   if outputs[0]!=outputs[1]:
    (OUT/'counterexample.json').write_text(json.dumps(dict(number=number,case=case,outputs=outputs),indent=2)+'\n');raise AssertionError((number,case))
   counts[kind]+=1;observations+=len(outputs[0][1]);digest.update(json.dumps([number,case,outputs[0]],sort_keys=True).encode())
 r=dict(comparisons=sum(counts.values()),counts=counts,strcmp_calls_per_side=observations,trace_sha256=digest.hexdigest(),actual_strcmp_and_upstream_port_decoder=True,canonical_configuration_pointer_normalized=True,config_overlap_and_fresh_lookup_name_checked=True,saved_r3_read_toggle_and_raw_r0_checked=True,callee_sp_nonstack_ram_mmio_registers_checked=True,no_native_candidate_execution=True,mmio_write_one_hardware_semantics_modeled=False,full_raw_abi_verified=False,cross_call_private_frame_history_verified=False,metadata_callback_abi_migrated=False,hardware_write_executed=False,instruction_identity=False,whole_image_complete=False,driver_sha256=sha(Path(__file__)),report_sha256=sha(rp),object_sha256=sha(obj),layout_sha256=sha(layout),application_sha256=sha(app))
 (OUT/'verification.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
if __name__=='__main__':main()
