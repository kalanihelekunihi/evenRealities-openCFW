#!/usr/bin/env python3
"""Actual lifecycle/helpers/strcmp/HAL; explicit SDK and returning-log seams."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-output-gpio-lifecycle-runtime';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 rp=OUT/'report.json';b=json.loads(rp.read_text());obj=OUT/'output-lifecycle-source.o';assert sha(obj)==b['graph_object_sha256']
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 layout=ROOT/'r1/source-config/runtime/native_output_gpio_lifecycle_verification.ld';cold=(BASE/'native-scatter-data/observed-initialized-data.bin').read_bytes();assert hashlib.sha256(cold).hexdigest()=='87fdee392022fdbe23dd0daf3e859fb14f3ce26ba3e8403aab56dc9d9a913317'
 meta=[(280,'r1_output_gpio_low',0x54f42),(284,'r1_output_gpio_high',0x54f3c),(288,'r1_output_gpio_toggle',0x54f8a),(292,'r1_output_gpio_driver0c',0x54d92),(296,'r1_output_gpio_driver10',0x54d8c),(300,'r1_output_gpio_driver14',0x54ea8),(312,'r1_output_gpio_open',0x54d98),(316,'r1_output_gpio_close',0x54c58),(320,'r1_output_gpio_slot10',0x54e20),(328,'r1_output_gpio_slot18',0x54d20),(332,'r1_output_gpio_slot1c',0x54cd0)]
 helpers={'r1_output_gpio_task_initialize':0x54f48,'r1_output_gpio_direct_initialize':0x54df0,'r1_output_gpio_task_release':0x54f28,'r1_output_gpio_direct_release':0x54cbc}
 lower={'nrfx_gpiote_is_init':0x7aa18,'nrfx_gpiote_init':0x7a94c,'nrfx_gpiote_out_init':0x7aa30,'nrfx_gpiote_out_task_enable':0x7ab64,'nrfx_gpiote_out_task_disable':0x7ab40,'nrfx_gpiote_out_uninit':0x7abac,'nrfx_gpiote_out_set':0x7ab3c,'nrfx_gpiote_out_clear':0x7aa2c,'r1_adc_error':0x4e5bc}
 counts=dict(open=0,close=0,workflow=0);hits={n:0 for n in [*helpers,*lower,'compare','open_callback','close_callback']};digest=hashlib.sha256();states={}
 with tempfile.TemporaryDirectory() as tmp:
  d=Path(tmp);elf=d/'test.elf';cmd=['arm-none-eabi-ld','-T',str(layout),str(obj),'-o',str(elf)]
  for i,n in enumerate(b['graph_undefined_symbols']):cmd+=['--defsym='+n+'='+hex(0x20000401+i*4)]
  subprocess.run(cmd,check=True,capture_output=True);sections={}
  for section in ['text','r1.output_gpio.configuration','r1.output_gpio.lifecycle']:
   p=d/(section+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j','.'+section,'-O','binary',str(elf),str(p)],check=True);sections[section]=p.read_bytes()
  syms={x[2]:int(x[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x:=line.split())==3}
  normalized=bytearray(sections['r1.output_gpio.configuration']);ptrs=[(0x20007228+off,n,a) for off,n,a in meta]+[(0x20007218+i*4,n,a) for i,(n,a) in enumerate(helpers.items())]
  for off,n,a in meta:assert struct.unpack_from('<I',normalized,off)[0]==syms[n]|1;struct.pack_into('<I',normalized,off,a|1)
  assert bytes(normalized)==cold[0x20007228-0x200064a8:0x20007228-0x200064a8+340]
  normalized=bytearray(sections['r1.output_gpio.lifecycle'])
  for i,(n,a) in enumerate(helpers.items()):assert struct.unpack_from('<I',normalized,i*4)[0]==syms[n]|1;struct.pack_into('<I',normalized,i*4,a|1)
  assert bytes(normalized)==cold[0x20007218-0x200064a8:0x20007228-0x200064a8]
  native_lower={a:n for n,a in lower.items()};source_lower={syms[n]&~1:n for n in lower};native_helpers={a:n for n,a in helpers.items()};source_helpers={syms[n]:n for n in helpers}
  def hook(u,a,size,_):
   st=states[id(u)];source=st['source'];assert not source or not 0x27000<=a<0xc4d08
   if a==st['after_compare']:
    st['after_compare']=None
    if st['mutation']==1:u.mem_write(0x20002000,struct.pack('<I',0xc0790))
   if a==st['after_helper']:
    st['after_helper']=None
    if st['mutation']==4 and st['helper'].endswith('release'):u.mem_write(st['record']+28,struct.pack('<I',0x2000021d));u.mem_write(st['record']+20,b'\x00')
   if a==(syms['strcmp'] if source else 0x277fe):st['events'].append(['compare',u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1)]);st['after_compare']=u.reg_read(UC_ARM_REG_LR)&~1
   helper=(source_helpers if source else native_helpers).get(a)
   if helper:
    st['helper']=helper;st['record']=u.reg_read(UC_ARM_REG_R0);st['after_helper']=u.reg_read(UC_ARM_REG_LR)&~1;st['events'].append([helper,st['record']]);return
   callback={0x20000210:'open_callback',0x20000214:'open_callback',0x20000218:'close_callback',0x2000021c:'close_callback'}.get(a)
   name=(source_lower if source else native_lower).get(a)
   if not name and not callback:
    assert a<0x20000400 or a>=0x20000500
    return
   r0=u.reg_read(UC_ARM_REG_R0);r1=u.reg_read(UC_ARM_REG_R1);ret=st['status'];event=[callback or name,r0]
   record=st['record'] if st['record'] is not None else st['selected']
   if callback:
    assert r0==a|1
    if st['mutation']==2 and callback=='open_callback':u.mem_write(record+13,bytes([1-st['selector']]));u.mem_write(record+12,b'\xff');u.mem_write(record+8,struct.pack('<I',33))
    if st['mutation']==5:u.mem_write(record+4,b'\xff')
   elif name=='nrfx_gpiote_is_init':ret=st['initialized']
   elif name=='nrfx_gpiote_out_init':
    assert r1==record+14;event += [r1,bytes(u.mem_read(r1,3)).hex()]
    if st['mutation']==3:u.mem_write(record+8,struct.pack('<I',47));u.mem_write(record+12,b'\xff')
   if name=='nrfx_gpiote_init':event=[name]
   if name=='nrfx_gpiote_is_init':event=[name,ret]
   st['events'].append(event)
   for reg,value in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],[ret,0x11223344,0x55667788,0x99aabbcc]):u.reg_write(reg,value)
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  machines=[]
  for source in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,raw);u.mem_map(0x1000000,0x40000);u.mem_write(0x1000000,sections['text']);u.mem_map(0x20000000,0x40000);u.mem_map(0x50000000,4096);u.hook_add(UC_HOOK_CODE,hook);machines.append(u)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11];names=[0xc0754,0xc0770,0xc0780,0xc0760,0xc0790,0x20003000]
  cases=itertools.product(['open','close','workflow'],range(6),[0,1,255],[0,1],[0,1,255],range(4),range(6),[0,0x55,0xaa,255])
  for number,(kind,index,opened,selector,enable,callbacks,mutation,seed) in enumerate(cases):
   outputs=[]
   for source,u in enumerate(machines):
    u.mem_write(0x20000000,bytes([seed])*0x40000);u.mem_write(0x20007218,cold[0x20007218-0x200064a8:0x20007228-0x200064a8+340]);u.mem_write(0x20002000,struct.pack('<I',names[index]));u.mem_write(0x20003000,b'missing\0');u.mem_write(0x50000000,struct.pack('<I',0xa55a33cc)*1024)
    if source:
     for a,n,v in ptrs:u.mem_write(a,struct.pack('<I',syms[n]|1))
    for j in range(5):
     rec=0x20007228+j*56;u.mem_write(rec+4,bytes([opened]));u.mem_write(rec+13,bytes([selector]));u.mem_write(rec+20,bytes([enable]));u.mem_write(rec+24,struct.pack('<II',0x20000211 if callbacks&1 else 0,0x20000219 if callbacks&2 else 0))
    st=dict(source=source,events=[],after_compare=None,after_helper=None,record=None,helper='',selected=0x20007228+min(index,4)*56,selector=selector,mutation=mutation,status=[0,1,0xffffffff][(number//4)%3],initialized=(number//12)%2);states[id(u)]=st;regs=[]
    for operation in (['open','close','open','close'] if kind=='workflow' else [kind]):
     st['record']=None;st['after_helper']=None;st['after_compare']=None
     u.reg_write(UC_ARM_REG_XPSR,0x01000000);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
     for reg,value in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],[0x20002000,0x11223344,0x55667788,0x99aabbcc]):u.reg_write(reg,value)
     for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
     u.emu_start((syms['r1_output_gpio_'+operation] if source else {'open':0x54d98,'close':0x54c58}[operation])|1,0x20000100,count=10000)
     assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)];regs.append(u.reg_read(UC_ARM_REG_R0))
    mem=bytearray(u.mem_read(0x20000000,0x3e000))+bytearray(u.mem_read(0x2003f000,0x1000))
    if source:
     for a,n,v in ptrs:assert struct.unpack_from('<I',mem,a-0x20000000)[0]==syms[n]|1;struct.pack_into('<I',mem,a-0x20000000,v|1)
    outputs.append([regs,st['events'],hashlib.sha256(mem).hexdigest(),bytes(u.mem_read(0x50000000,4096)).hex()])
   if outputs[0]!=outputs[1]:(OUT/'counterexample.json').write_text(json.dumps(dict(number=number,case=[kind,index,opened,selector,enable,callbacks,mutation,seed],outputs=outputs),indent=2)+'\n');raise AssertionError(number)
   counts[kind]+=1
   for event in outputs[0][1]:hits[event[0]]+=1
   digest.update(json.dumps([number,kind,index,opened,selector,enable,callbacks,mutation,seed,outputs[0]],sort_keys=True).encode())
 assert all(hits.values()),hits
 receipt=dict(comparisons=sum(counts.values()),counts=counts,observation_counts=hits,trace_sha256=digest.hexdigest(),actual_four_helpers_strcmp_and_inline_hal=True,only_sdk_and_returning_error_logger_are_fixtures=True,cold_lifecycle_table_bytes_pointer_normalized=16,callback_self_r0_order_and_fresh_close_target_checked=True,fresh_selector_pin_level_after_callbacks_checked=True,repeated_open_close_workflows_checked=True,raw_r0_callee_sp_nonstack_ram_mmio_checked=True,no_native_candidate_execution=True,full_raw_abi_verified=False,arbitrary_selector_targets_verified=False,cross_call_private_frame_history_verified=False,metadata_callback_abi_migrated=False,hardware_write_executed=False,instruction_identity=False,whole_image_complete=False,driver_sha256=sha(Path(__file__)),report_sha256=sha(rp),object_sha256=sha(obj),layout_sha256=sha(layout),application_sha256=sha(app))
 (OUT/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
