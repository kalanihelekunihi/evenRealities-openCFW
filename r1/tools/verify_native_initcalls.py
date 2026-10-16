#!/usr/bin/env python3
"""Native initcall bounds, order, discarded statuses and PRIMASK behavior."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UcError
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
CALLS=[('r1_named_adc_register_all',0x5493c),('r1_internal_flash_device_registration',0x54a8c),('r1_twi_primary_device_binding_configuration',0x54f90),('r1_twi_secondary_device_binding_configuration',0x54fc4),('r1_named_gpio_register_all',0x54c24),('r1_native_output_gpio_registration',0x54e78),('r1_native_rtc_register',0x563c4),('r1_stock_i2c2_register',0x56508),('r1_stock_i2c3_register',0x56520),('r1_stock_i2c4_register',0x56538),('r1_stock_i2c5_register',0x56550),('r1_yhm2710_stacmd_binding_configuration',0x565f4),('r1_native_named_wdt_register',0x56694)]
ENTRIES={'r1_module_init_table_run':0x5cb6c,'r1_module_post_init_run':0x5cb4c,'r1_native_boot_initcall_dispatch':0x4e1e4}
def main():
 out=BASE/'native-initcalls';rp=out/'report.json';r=json.loads(rp.read_text());obj=out/'initcalls.o';assert sha(obj)==r['selected_object_sha256']
 for p,d in r['inputs'].items():assert sha(ROOT/p)==d,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';states={};count=0;callbacks=0
 with tempfile.TemporaryDirectory() as directory:
  t=Path(directory);ld=t/'layout.ld';elf=t/'test.elf';binary=t/'text.bin';ld.write_text('SECTIONS { .r1.init.devices 0xc4534 : { *(.r1.init.devices) } .text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } /DISCARD/ : { *(.comment) *(.note*) } }');subprocess.run(['arm-none-eabi-ld','-T',str(ld),*['--defsym='+n+'='+hex(0x100ef01+i*16) for i,(n,_) in enumerate(CALLS)],str(obj),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True);syms={x.split()[-1]:int(x.split()[0],16) for x in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x.split())==3};assert syms['r1_device_initcalls']==0xc4534
  assert all(syms[n]==0 for n in ('r1_init_early_start','r1_init_early_stop','r1_init_board_start','r1_init_board_stop','r1_init_post_start','r1_init_post_stop'))
  stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
  for u in (stock,candidate):u.mem_map(0x20000,0xc0000);u.mem_map(0x1000000,0x10000);u.mem_map(0x20000000,0x40000)
  stock.mem_write(0x27000,app.read_bytes());candidate.mem_write(0x1000000,binary.read_bytes());data=t/'table.bin';subprocess.run(['arm-none-eabi-objcopy','--dump-section','.r1.init.devices='+str(data),str(elf)],check=True);table=data.read_bytes();assert len(table)==52
  for i,(name,a) in enumerate(CALLS):assert struct.unpack_from('<I',table,i*4)[0]==0x100ef01+i*16 and struct.unpack('<I',bytes(stock.mem_read(0xc4534+i*4,4)))[0]==a|1
  candidate.mem_write(0xc4534,table)
  for a in (0x5cb64,0x5cb68,0x5cba8,0x5cbac,0x5cbb0,0x5cbb4):assert bytes(stock.mem_read(a,4))==bytes(4)
  assert struct.unpack('<2I',bytes(stock.mem_read(0x5cbb8,8)))==(0xc4534,0xc4568)
  kinds={a:i for i,(_,a) in enumerate(CALLS)};kinds.update({0x100ef00+i*16:i for i in range(13)})
  def hook(u,a,size,user):
   nonlocal callbacks
   if a not in kinds:return
   f=states[id(u)];index=kinds[a];f['trace'].append((index,u.reg_read(UC_ARM_REG_PRIMASK)));callbacks+=1
   if not index and f['action']:u.reg_write(UC_ARM_REG_PRIMASK,f['action']-1)
   u.reg_write(UC_ARM_REG_R0,f['status']);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  for u in (stock,candidate):u.hook_add(UC_HOOK_CODE,hook)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  for name,mask,status,action in itertools.product(ENTRIES,(0,1),(0,1,0xdeadbeef),range(3)):
   results=[]
   for u in (stock,candidate):
    states[id(u)]={'trace':[],'status':status,'action':action};u.reg_write(UC_ARM_REG_PRIMASK,mask);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    u.emu_start((ENTRIES[name] if u is stock else syms[name])|1,0x20000100,count=100000);assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)];results.append((states[id(u)]['trace'],u.reg_read(UC_ARM_REG_PRIMASK)))
   assert results[0]==results[1],(name,mask,status,action,results)
   assert [x[0] for x in results[0][0]]==([] if name=='r1_module_post_init_run' else list(range(13)))
   if name=='r1_native_boot_initcall_dispatch':assert results[0][1]==0 and results[0][0][0][1]==1
   count+=1
  faults=0
  for name,index,mask in itertools.product(('r1_module_init_table_run','r1_native_boot_initcall_dispatch'),(0,6,12),(0,1)):
   results=[]
   for u in (stock,candidate):
    original=struct.pack('<13I',*[(a|1) for _,a in CALLS]) if u is stock else table;u.mem_write(0xc4534,original);u.mem_write(0xc4534+index*4,bytes(4));states[id(u)]={'trace':[],'status':0,'action':0};u.reg_write(UC_ARM_REG_PRIMASK,mask);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
    try:u.emu_start((ENTRIES[name] if u is stock else syms[name])|1,0x20000100,count=100000)
    except UcError as error:results.append((error.errno,u.reg_read(UC_ARM_REG_PC),list(states[id(u)]['trace']),u.reg_read(UC_ARM_REG_PRIMASK)))
    else:raise AssertionError('null initcall did not fault')
   assert results[0]==results[1] and results[0][1]==0 and [x[0] for x in results[0][2]]==list(range(index)),(name,index,mask,results);faults+=1
 (out/'verification.json').write_text(json.dumps(dict(application_sha256=sha(app),report_sha256=sha(rp),comparisons=count,null_target_fault_comparisons=faults,callbacks_per_implementation=callbacks//2,device_table_bytes_pointer_normalized=52,device_entries=13,empty_ranges=3,scope='Actual native/source init walkers and boot critical wrapper, exact ranges/order, discarded statuses and callback PRIMASK changes; all registrar bodies are fixtures',limitations=['Boot wrapper original ownership size40 versus18 code bytes remains held; post-init is a supplemental22-byte body. Only the main58-byte runner row is promoted.','Callback argument-register residue, actual registrar bodies and physical interrupt behavior remain unproven; injected null targets only establish emulated faults, not physical exception state. Original linker symbol identities are unknown; recovered range values are explicit source-owned boundaries.']),indent=2)+'\n');print(count,'initcall comparisons;',callbacks//2,'callbacks')
if __name__=='__main__':main()
