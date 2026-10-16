#!/usr/bin/env python3
"""Native config frames, fresh fields and bounded lifecycle workflows."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-hw-twi-lifecycle-runtime';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
PTRS=[(44,'r1_hw_twi0_irq',0x70778),(80,'r1_hw_twi0_open',0x55278),(84,'r1_hw_twi0_close',0x55180),(88,'r1_hw_twi0_read',0x55414),(92,'r1_hw_twi0_write',0x55ce0),(152,'r1_hw_twi1_irq',0x707cc),(188,'r1_hw_twi1_open',0x552e4),(192,'r1_hw_twi1_close',0x551b4),(196,'r1_hw_twi1_read',0x55448),(200,'r1_hw_twi1_write',0x55d50)]
def main():
 rp=OUT/'report.json';b=json.loads(rp.read_text());obj=OUT/'hw-lifecycle-source.o';assert sha(obj)==b['graph_object_sha256'];app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 layout=ROOT/'r1/source-config/runtime/native_hw_twi_lifecycle_verification.ld';cold=(BASE/'native-scatter-data/observed-initialized-data.bin').read_bytes();assert hashlib.sha256(cold).hexdigest()=='87fdee392022fdbe23dd0daf3e859fb14f3ce26ba3e8403aab56dc9d9a913317'
 counts=dict(open=0,close=0,workflow=0);hits=dict(gpio=0,init=0,error=0,enable=0,disable=0,uninit=0,power_zero=0,power_one=0);states={};digest=hashlib.sha256()
 with tempfile.TemporaryDirectory() as tmp:
  d=Path(tmp);elf=d/'test.elf';cmd=['arm-none-eabi-ld','-T',str(layout),str(obj),'-o',str(elf)]
  for i,n in enumerate(b['graph_undefined_symbols']):cmd+=['--defsym='+n+'='+hex(0x20000401+i*4)]
  subprocess.run(cmd,check=True,capture_output=True);sections={}
  for section in ['text','r1.hw_twi.primary','r1.hw_twi.secondary','r1.hw_twi.template0','r1.hw_twi.template1']:
   p=d/(section+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j','.'+section,'-O','binary',str(elf),str(p)],check=True);sections[section]=p.read_bytes()
  for section,a in [('r1.hw_twi.template0',0x9a600),('r1.hw_twi.template1',0x9a620)]:assert sections[section]==raw[a-0x27000:a-0x27000+8]
  syms={x[2]:int(x[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x:=line.split())==3};config=sections['r1.hw_twi.primary']+sections['r1.hw_twi.secondary'];normalized=bytearray(config)
  for off,n,a in PTRS:assert struct.unpack_from('<I',normalized,off)[0]==syms[n]|1;struct.pack_into('<I',normalized,off,a|1)
  stock=cold[0x20006fe8-0x200064a8:0x20006fe8-0x200064a8+216];assert bytes(normalized)==stock
  lower={'nrf_drv_twi_init':'init','nrfx_twim_enable':'enable','nrfx_twim_disable':'disable','nrfx_twim_uninit':'uninit','r1_adc_error':'error','r1_twi_gpio_output':'gpio'};source_hooks={syms[n]&~1:k for n,k in lower.items()};native_hooks={0x789e4:'init',0x7b268:'enable',0x7b22c:'disable',0x7b3d8:'uninit',0x4e5bc:'error',0x78e1c:'gpio'}
  def hook(u,a,size,_):
   st=states[id(u)];source=st['source'];assert not source or not 0x27000<=a<0xc4d08
   power=struct.unpack('<I',u.mem_read(st['power'],4))[0]
   if power!=st['lastpower']:
    st['events'].append(['power_zero' if power==0 else 'power_one',power]);st['lastpower']=power
   kind=(source_hooks if source else native_hooks).get(a)
   if not kind:assert a<0x20000400 or a>=0x20000500;return
   args=[u.reg_read(reg) for reg in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];base=st['base'];rec=base+12;m=st['mutation'];event=[kind];ret=0
   if kind=='gpio':
    event += [args[0]];st['gpio']+=1
    if not source:assert args[1:]==[1,1,0] and bytes(u.mem_read(u.reg_read(UC_ARM_REG_SP),8))==bytes(8)
    port=0x50000000 if args[0]<32 else 0x50000300;pin=args[0] if args[0]<32 else args[0]&31;u.mem_write(port+0x700+pin*4,struct.pack('<I',3))
    if m==1 and st['gpio']==1:u.mem_write(rec+12,struct.pack('<I',33))
    if m==2:u.mem_write(rec+32,struct.pack('<I',0x20000201))
   elif kind=='init':
    assert args[0]==rec+16 and args[1]==0x2003efe0 and args[3]==0
    callback=args[2];expected=(syms['r1_hw_twi'+str(st['bus'])+'_irq']|1) if source else [0x70779,0x707cd][st['bus']]
    assert callback in [expected,0x20000201]
    event += [args[0],args[1],'alternate' if callback==0x20000201 else st['bus'],args[3],bytes(u.mem_read(args[1],16)).hex()];ret=st['result']
    if m==3:u.mem_write(args[1],bytes([0xa5])*16);u.mem_write(rec+4,b'\xff')
   elif kind=='error':event += [args[0]]
   else:
    assert args[0]==rec+20;event += [args[0]]
    if m==4:u.mem_write(rec+4,b'\xff');u.mem_write(rec+8,struct.pack('<I',47))
   st['events'].append(event)
   for reg,value in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],[ret,0x11223344,0x55667788,0x99aabbcc]):u.reg_write(reg,value)
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  machines=[]
  for source in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,raw);u.mem_map(0x1000000,0x20000);u.mem_write(0x1000000,sections['text']);u.mem_map(0x20000000,0x40000);u.mem_map(0x40003000,0x2000);u.mem_map(0x50000000,4096);u.hook_add(UC_HOOK_CODE,hook);machines.append(u)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  cases=itertools.product(['open','close','workflow'],range(2),[0,1,255],[0,31,32,47,0xffffffff],[0,1,256,0xffffffff],range(5),[0,0x55,0xaa,255])
  for number,case in enumerate(cases):
   kind,bus,opened,pin,result,mutation,seed=case;outputs=[];base=0x20006fe8+bus*108;power=[0x40003ffc,0x40004ffc][bus]
   for source,u in enumerate(machines):
    u.mem_write(0x20000000,bytes([seed])*0x40000);u.mem_write(0x20006fe8,config if source else stock);u.mem_write(base+16,bytes([opened]));u.mem_write(base+20,struct.pack('<II',pin,(pin+1)&0xffffffff));u.mem_write(0x40003000,struct.pack('<I',0xa55a33cc)*2048);u.mem_write(0x50000000,struct.pack('<I',0x5aa5cc33)*1024);states[id(u)]=dict(source=source,events=[],bus=bus,base=base,power=power,lastpower=0xa55a33cc,mutation=mutation,result=result,gpio=0);regs=[]
    for operation in (['open','close','open','close'] if kind=='workflow' else [kind]):
     u.reg_write(UC_ARM_REG_XPSR,0x01000000);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
     for reg,value in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],[0xdeadbeef,0x11223344,0x55667788,0x99aabbcc]):u.reg_write(reg,value)
     for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
     u.emu_start((syms['r1_hw_twi'+str(bus)+'_'+operation] if source else {('open',0):0x55278,('open',1):0x552e4,('close',0):0x55180,('close',1):0x551b4}[operation,bus])|1,0x20000100,count=10000)
     assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)];regs.append(u.reg_read(UC_ARM_REG_R0))
    mem=bytearray(u.mem_read(0x20000000,0x3e000))+bytearray(u.mem_read(0x2003f000,0x1000))
    if source:
     for off,n,a in PTRS:
      word=struct.unpack_from('<I',mem,0x6fe8+off)[0];assert word in [syms[n]|1,0x20000201];struct.pack_into('<I',mem,0x6fe8+off,a|1 if word!=0x20000201 else word)
    outputs.append([regs,states[id(u)]['events'],hashlib.sha256(mem).hexdigest(),hashlib.sha256(bytes(u.mem_read(0x40003000,0x2000))+bytes(u.mem_read(0x50000000,4096))).hexdigest()])
   if outputs[0]!=outputs[1]:(OUT/'counterexample.json').write_text(json.dumps(dict(number=number,case=case,outputs=outputs),indent=2)+'\n');raise AssertionError(number)
   counts[kind]+=1
   for event in outputs[0][1]:hits[event[0]]+=1
   digest.update(json.dumps([number,case,outputs[0]],sort_keys=True).encode())
 assert all(hits.values())
 r=dict(comparisons=sum(counts.values()),counts=counts,observation_counts=hits,trace_sha256=digest.hexdigest(),actual_lifecycle_and_power_register_sequence=True,only_sdk_gpio_error_are_fixtures=True,native_config_pointer_and_full16_bytes_checked=True,fresh_pin_irq_and_opened_after_lower_calls_checked=True,init_errors_log_and_continue_checked=True,repeated_lifecycle_workflows_checked=True,raw_r0_callee_sp_nonstack_ram_mmio_checked=True,no_native_candidate_execution=True,full_raw_abi_verified=False,cross_call_private_frame_history_verified=False,sdk_hardware_initialization_verified=False,metadata_operation_abi_migrated=False,hardware_write_executed=False,instruction_identity=False,whole_image_complete=False,driver_sha256=sha(Path(__file__)),report_sha256=sha(rp),object_sha256=sha(obj),layout_sha256=sha(layout),application_sha256=sha(app))
 (OUT/'verification.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
if __name__=='__main__':main()
