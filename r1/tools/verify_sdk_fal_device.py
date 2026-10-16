#!/usr/bin/env python3
"""Pinned FAL device initialization/lookup including terminal assertions."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();DEVICE=0x200077c4;QUERY=0x20001000

def main():
 out=BASE/'sdk-fal-device';rp=out/'report.json';obj=out/'fal-device.o';r=json.loads(rp.read_text());receipt=out/'verification.json';receipt.unlink(missing_ok=True);assert sha(obj)==r['units'][0]['object_sha256']
 for p,d in r['inputs'].items():assert sha(ROOT/p)==d,p
 sr=BASE/'runtime-strncmp/report.json';so=BASE/'runtime-strncmp/strncmp.o';assert sha(so)==json.loads(sr.read_text())['units'][0]['object_sha256']
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';states={};count=0;assertions=0
 with tempfile.TemporaryDirectory() as directory:
  t=Path(directory);ld=t/'layout.ld';elf=t/'test.elf';binary=t/'text.bin';ld.write_text('SECTIONS { .bss.r1_fal_device_initialized 0x200077b2 (NOLOAD) : { *(.bss.r1_fal_device_initialized) } .rodata.device_table 0x9c224 : { *(.rodata.device_table) } .text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } /DISCARD/ : { *(.comment) *(.note*) } }')
  subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--entry=fal_flash_init','--defsym=r1_fal_flash_device='+hex(DEVICE),'--defsym=printf=0x100e021',str(obj),str(so),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True)
  syms={x.split()[-1]:int(x.split()[0],16) for x in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x.split())==3};assert syms['r1_fal_device_initialized']==0x200077b2
  stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
  for u in (stock,candidate):u.mem_map(0x20000,0xc0000);u.mem_map(0x1000000,0x10000);u.mem_map(0x20000000,0x40000)
  stock.mem_write(0x27000,app.read_bytes());candidate.mem_write(0x1000000,binary.read_bytes());assert bytes(stock.mem_read(0x9c224,4))==struct.pack('<I',DEVICE)
  stock.reg_write(UC_ARM_REG_SP,0x2003f000);stock.emu_start(0x283a1,0x27208,count=2000000);assert stock.reg_read(UC_ARM_REG_PC)==0x27208 and bytes(stock.mem_read(0x200077b2,1))==b'\0'
  def string(u,a):
   b=bytearray()
   while True:
    x=bytes(u.mem_read(a+len(b),1))
    if x==b'\0':return b.decode()
    b+=x;assert len(b)<256
  def hook(u,address,size,user):
   f=states[id(u)]
   if f['asserted']:
    if address==f['last_pc']:f['repeats']+=1
    else:f['last_pc']=address;f['repeats']=0
    if f['repeats']==8:u.emu_stop();return
   if address==0x100e100:
    f['trace'].append(('init',bytes(u.mem_read(0x200077b2,1))[0]));u.mem_write(0x200077b2,bytes([f['mutation']]));u.reg_write(UC_ARM_REG_R0,f['callback_result']);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
   elif address in (0x38060,0x100e020):
    fmt=string(u,u.reg_read(UC_ARM_REG_R0));assert fmt=='(%s) has assert failed at %s.\n';f['trace'].append(('assert',fmt,string(u,u.reg_read(UC_ARM_REG_R1)),string(u,u.reg_read(UC_ARM_REG_R2)),bytes(u.mem_read(0x200077b2,1))[0]));f['asserted']=True;u.reg_write(UC_ARM_REG_R0,0xffffffff);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  for u in (stock,candidate):u.hook_add(UC_HOOK_CODE,hook)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  def run(u,name,initial=0,callbacks=15,callback_result=0,mutation=0,query=b'device_flash\0',device_name=b'device_flash\0',null=False):
   u.mem_write(0x200077b1,bytes([0x57,initial,0x93]));u.mem_write(DEVICE,device_name.ljust(24,b'\0')[:24]+bytes(12)+struct.pack('<4I',*[0x100e101 if callbacks&(1<<i) else 0 for i in range(4)])+struct.pack('<I',32));u.mem_write(QUERY,query.ljust(64,b'\x7f'));f=dict(trace=[],asserted=False,last_pc=0,repeats=0,callback_result=callback_result,mutation=mutation);states[id(u)]=f
   u.reg_write(UC_ARM_REG_R0,0 if null else QUERY);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
   for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
   entry={'fal_flash_init':0x62e68,'fal_flash_device_find':0x62df4}[name] if u is stock else syms[name];u.emu_start(entry|1,0x20000100,count=10000)
   if f['asserted']:assert f['repeats']==8 and u.reg_read(UC_ARM_REG_PC)!=0x20000100
   else:assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
   state=bytes(u.mem_read(0x200077b1,3));assert state[0]==0x57 and state[2]==0x93
   return None if f['asserted'] else u.reg_read(UC_ARM_REG_R0),state,f['trace'],f['asserted']
  def compare(name,**kw):
   nonlocal count,assertions
   a=run(stock,name,**kw);b=run(candidate,name,**kw);assert a==b,(name,kw,a,b);count+=1;assertions+=a[-1]
  for initial,callbacks in itertools.product(range(256),range(16)):compare('fal_flash_init',initial=initial,callbacks=callbacks)
  for callback_result,mutation in itertools.product((0,1,8,0x80000000,0xffffffff),range(256)):compare('fal_flash_init',callback_result=callback_result,mutation=mutation)
  for initial,null in itertools.product(range(256),(False,True)):compare('fal_flash_device_find',initial=initial,null=null)
  for i in range(25):
   for value in range(256):
    query=bytearray(b'device_flash\0'.ljust(25,b'X'));query[i]=value;compare('fal_flash_device_find',initial=1,query=bytes(query))
  for n in range(25):
   name=bytes(range(0x80,0x80+n));compare('fal_flash_device_find',initial=1,query=name+b'\0',device_name=name+b'\0');compare('fal_flash_device_find',initial=1,query=name+b'X\0',device_name=name+b'\0')
 receipt.write_text(json.dumps(dict(application_sha256=sha(app),report_sha256=sha(rp),object_sha256=sha(obj),strncmp_report_sha256=sha(sr),comparisons=count,terminal_assertion_comparisons=assertions,cold_zero_bytes_compared=1,native_device_table_pointer_bytes_authenticated=4,compiled_table_emitted=False,scope='Unchanged pinned FAL device init/find, all readiness bytes and callback-presence masks, ignored init returns and post-callback state, bounded names/NUL/high bytes, actual compiled musl strncmp, exact terminal assertion printf and nonreturning loops, state/guards/registers',limitations=['Device record and callback bodies are controlled fixtures; production R1 flash-device provider remains unresolved.','Assertions prove printf invocation and nonreturning behavior; runtime output and physical faults remain unproven.','No original Arm strncmp source or exact instructions, full image linking or hardware proof is claimed.'],instruction_identity_proven=False),indent=2)+'\n');print(count,'FAL device comparisons passed;',assertions,'terminal assertions')
if __name__=='__main__':main()
