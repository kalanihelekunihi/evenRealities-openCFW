#!/usr/bin/env python3
"""Compare unchanged FAL core, shared readiness and native error printf contract."""
import hashlib,itertools,json,struct,subprocess,tempfile,sys
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 real_device='--real-device' in sys.argv
 out=BASE/'sdk-fal-core';rp=out/'report.json';obj=out/'fal-core.o';r=json.loads(rp.read_text());receipt=out/('device-integration-verification.json' if real_device else 'verification.json');receipt.unlink(missing_ok=True);assert sha(obj)==r['units'][0]['object_sha256']
 for p,d in r['inputs'].items():assert sha(ROOT/p)==d,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';states={};count=0;printf_count=0
 device=BASE/'sdk-fal-device/fal-device.o';device_rp=BASE/'sdk-fal-device/report.json';strncmp=BASE/'runtime-strncmp/strncmp.o';strncmp_rp=BASE/'runtime-strncmp/report.json'
 if real_device:assert sha(device)==json.loads(device_rp.read_text())['units'][0]['object_sha256'] and sha(strncmp)==json.loads(strncmp_rp.read_text())['units'][0]['object_sha256']
 with tempfile.TemporaryDirectory() as directory:
  t=Path(directory);ld=t/'layout.ld';elf=t/'test.elf';binary=t/'text.bin';ld.write_text('SECTIONS { .bss.r1_fal_device_initialized 0x200077b2 (NOLOAD) : { *(.bss.r1_fal_device_initialized) } .bss.r1_fal_initialized 0x200077b1 (NOLOAD) : { *(.bss.r1_fal_initialized) } .text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } /DISCARD/ : { *(.comment) *(.note*) } }')
  subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--entry=fal_init',*(['--defsym=r1_fal_flash_device=0x200077c4'] if real_device else ['--defsym=fal_flash_init=0x100e001']),'--defsym=fal_partition_init=0x100e011','--defsym=printf=0x100e021',str(obj),*([str(device),str(strncmp)] if real_device else []),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True)
  syms={x.split()[-1]:int(x.split()[0],16) for x in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x.split())==3};assert syms['r1_fal_initialized']==0x200077b1 and syms['r1_fal_is_initialized']==syms['fal_init_check']
  stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
  for u in (stock,candidate):u.mem_map(0x20000,0xc0000);u.mem_map(0x1000000,0x10000);u.mem_map(0x20000000,0x40000)
  stock.mem_write(0x27000,app.read_bytes());candidate.mem_write(0x1000000,binary.read_bytes());stock.reg_write(UC_ARM_REG_SP,0x2003f000);stock.emu_start(0x283a1,0x27208,count=2000000);assert stock.reg_read(UC_ARM_REG_PC)==0x27208 and bytes(stock.mem_read(0x200077b1,1))==b'\0'
  def string(u,a):
   b=bytearray()
   while True:
    x=bytes(u.mem_read(a+len(b),1))
    if x==b'\0':return b.decode()
    b+=x;assert len(b)<256
  def hook(u,address,size,user):
   nonlocal printf_count
   if real_device and address==0x100e100:
    f=states[id(u)]
    if f['mutation']&1:u.mem_write(0x200077b1,b'\x73')
    u.reg_write(UC_ARM_REG_R0,f['flash']);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR));return
   if address not in (0x62e68,0x631c0,0x38060,0x100e000,0x100e010,0x100e020,syms.get('fal_flash_init',0) if real_device else 0):return
   f=states[id(u)];before=bytes(u.mem_read(0x200077b1,1))[0]
   if address in (0x62e68,0x100e000,syms.get('fal_flash_init',0) if real_device else 0):
    f['trace'].append(('flash',before))
    if real_device:return
    result=f['flash']
    if f['mutation']&1:u.mem_write(0x200077b1,b'\x73')
   elif address in (0x631c0,0x100e010):
    f['trace'].append(('partition',before));result=f['partition']
    if f['mutation']&2:u.mem_write(0x200077b1,b'\x00')
   else:
    fmt=string(u,u.reg_read(UC_ARM_REG_R0));args=[]
    if '%s:%d' in fmt:args=[string(u,u.reg_read(UC_ARM_REG_R1)),u.reg_read(UC_ARM_REG_R2)]
    elif '%s' in fmt:args=[string(u,u.reg_read(UC_ARM_REG_R1))]
    f['trace'].append(('printf',fmt,args,before));printf_count+=1;result=f['printf_result']
   u.reg_write(UC_ARM_REG_R0,result);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  for u in (stock,candidate):u.hook_add(UC_HOOK_CODE,hook)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  def run(u,initial,flash,partition,mutation,printf_result):
   u.mem_write(0x200077b2,b'\0');u.mem_write(0x200077c4,b'device_flash'.ljust(24,b'\0')+bytes(12)+struct.pack('<4I',0x100e101,0x100e111,0x100e121,0x100e131)+struct.pack('<I',32))
   u.mem_write(0x200077b0,bytes([0x57,initial,0 if real_device else 0x93]));f=dict(trace=[],flash=flash,partition=partition,mutation=mutation,printf_result=printf_result);states[id(u)]=f
   u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
   for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
   u.emu_start((0x62f40 if u is stock else syms['fal_init'])|1,0x20000100,count=1000)
   assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
   result=u.reg_read(UC_ARM_REG_R0);state=bytes(u.mem_read(0x200077b0,3));assert state[0]==0x57 and state[2]==(1 if real_device else 0x93)
   u.reg_write(UC_ARM_REG_LR,0x20000101);u.emu_start((0x62fe8 if u is stock else syms['r1_fal_is_initialized'])|1,0x20000100,count=100);assert u.reg_read(UC_ARM_REG_R0)==state[1]
   return result,state,f['trace']
  values=(0,1,7,0x7fffffff,0x80000000,0xffffffff)
  for initial,flash,partition in itertools.product(range(256),values,values):
   a=run(stock,initial,flash,partition,0,0);b=run(candidate,initial,flash,partition,0,0);assert a==b,(initial,flash,partition,a,b);count+=1
  for initial,flash,partition,mutation,result in itertools.product((0,1,255),values,values,range(4),(0,8,0xffffffff)):
   a=run(stock,initial,flash,partition,mutation,result);b=run(candidate,initial,flash,partition,mutation,result);assert a==b,(initial,flash,partition,mutation,result,a,b);count+=1
 receipt.write_text(json.dumps(dict(application_sha256=sha(app),report_sha256=sha(rp),object_sha256=sha(obj),comparisons=count,actual_fal_device_initializer_executed=real_device,device_report_sha256=sha(device_rp) if real_device else None,strncmp_report_sha256=sha(strncmp_rp) if real_device else None,printf_calls_per_implementation=printf_count//2,shared_readiness_checks=count,cold_zero_bytes_compared=1,scope='Unchanged pinned FAL core init: signed flash/partition replies, all initial readiness bytes, shared getter after every call, callback state mutation, exact printf formats/arguments/order, ignored printf results, guards/registers/stack',limitations=['Partition initialization, device record/callbacks and printf are controlled fixtures; flash initialization executes actual upstream C only in device integration mode. Runtime output remains unresolved.','Shared readiness is proven within this module; duplicate upstream fal.c objects must not be linked beside it.','Instruction identity, complete image linking and hardware remain unresolved.'],instruction_identity_proven=False),indent=2)+'\n');print(count,'FAL core comparisons passed')
if __name__=='__main__':main()
