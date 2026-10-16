#!/usr/bin/env python3
"""Unchanged SDK interrupt-priority validator versus native MMIO/assert behavior."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_MEM_INVALID
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=BASE/'rtos-interrupt-priority';vp=out/'verification.json';vp.unlink(missing_ok=True);rp=out/'report.json';r=json.loads(rp.read_text());obj=out/'interrupt-priority.o';assert sha(obj)==r['selected_object_sha256']
 for path,digest in r['inputs'].items():assert sha(ROOT/path)==digest,path
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';comparisons=0;faults=0;states={}
 with tempfile.TemporaryDirectory() as directory:
  t=Path(directory);ld=t/'layout.ld';elf=t/'test.elf';binary=t/'text.bin';ld.write_text('SECTIONS { .text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } /DISCARD/ : { *(.comment) *(.note*) } }');subprocess.run(['arm-none-eabi-ld','-T',str(ld),str(obj),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True);syms={x.split()[-1]:int(x.split()[0],16) for x in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x.split())==3};stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
  for u in (stock,candidate):u.mem_map(0x20000,0xc0000);u.mem_map(0x1000000,0x10000);u.mem_map(0x20000000,0x40000);u.mem_map(0xe000e000,4096)
  stock.mem_write(0x27000,app.read_bytes());candidate.mem_write(0x1000000,binary.read_bytes())
  def invalid(u,access,a,size,value,user):
   if a==0xffffffff and value==0:states[id(u)]=True
   return False
  for u in (stock,candidate):u.hook_add(UC_HOOK_MEM_INVALID,invalid)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  for ipsr,priority,maximum,group,maxgroup,mask in itertools.product((0,15,16,17,255,511),(0,1,63,64,128,224,255),(0,2,64,224,255),range(8),(0,4,7,0xffffffff),(0,64)):
   results=[]
   for u in (stock,candidate):
    states[id(u)]=False;u.mem_write(0x20007810,struct.pack('<3I',maximum,0,maxgroup));u.mem_write(0xe000e000,bytes(4096));u.mem_write(0xe000ed0c,struct.pack('<I',0xa5000000|(group<<8)))
    if ipsr>=16:u.mem_write(0xe000e3f0+ipsr,bytes([priority]))
    u.reg_write(UC_ARM_REG_IPSR,ipsr);u.reg_write(UC_ARM_REG_BASEPRI,mask);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    try:u.emu_start((0x95f18 if u is stock else syms['vPortValidateInterruptPriority'])|1,0x20000100,count=10000)
    except UcError:assert states[id(u)],(ipsr,priority,maximum,group,maxgroup,u is stock,hex(u.reg_read(UC_ARM_REG_PC)))
    if not states[id(u)]:assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
    results.append((states[id(u)],u.reg_read(UC_ARM_REG_BASEPRI),bytes(u.mem_read(0x20007810,12)),bytes(u.mem_read(0xe000e000,4096))))
   assert results[0]==results[1],(ipsr,priority,maximum,group,maxgroup,mask);comparisons+=1;faults+=results[0][0]
 vp.write_text(json.dumps(dict(application_sha256=sha(app),report_sha256=sha(rp),driver_sha256=sha(Path(__file__)),comparisons=comparisons,assertion_comparisons=faults,provider_interception=False,scope='Actual SDK ISR priority validator, native IPSR0..511 boundaries, priority/max-syscall bytes, AIRCR grouping/max-group state and fatal assertion masking/write',limitations=['IPSR and NVIC/AIRCR registers are controlled emulator inputs. No actual interrupt dispatch, physical NVIC implementation or instruction identity proof.']),indent=2)+'\n');print(comparisons,'interrupt priority comparisons;',faults,'assertions')
if __name__=='__main__':main()
