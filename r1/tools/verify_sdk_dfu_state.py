#!/usr/bin/env python3
"""Compare the pinned example state callback with native GPREGRET2/shutdown ordering."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=BASE/'sdk-dfu-state';rp=out/'report.json';r=json.loads(rp.read_text());obj=out/'dfu-state.o';receipt=out/'verification.json';receipt.unlink(missing_ok=True);assert sha(obj)==r['selected_object_sha256']
 for p,d in r['inputs'].items():assert sha(ROOT/p)==d,p
 source=ROOT/r['units'][0]['source'];x=r['extraction'];assert hashlib.sha256(source.read_bytes()[x['offset']:x['offset']+x['length']]).hexdigest()==x['sha256'] and sha(ROOT/x['generated_source'])==x['generated_sha256']
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';ep=out/'evidence.json';e=json.loads(ep.read_text());assert e['application_sha256']==sha(app)
 for row in e['functions']:
  p=out/row['ghidra_file'];assert sha(p)==row['ghidra_sha256'];a=int(row['entry'],16);assert bytes(json.loads(p.read_text())['data'])==app.read_bytes()[a-0x27000:a-0x27000+row['body_bytes']]
 states={};comparisons=0;calls=0
 with tempfile.TemporaryDirectory() as directory:
  t=Path(directory);ld=t/'layout.ld';elf=t/'test.elf';binary=t/'text.bin';ld.write_text('SECTIONS { .text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } /DISCARD/ : { *(.comment) *(.note*) } }');subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--entry=r1_sdh_state_observer_567ac','--defsym=nrf_pwr_mgmt_shutdown=0x100ed01',str(obj),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True);syms={v.split()[-1]:int(v.split()[0],16) for v in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v.split())==3};assert 'r1_dfu_state_compile_anchor' not in syms
  stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
  for u in (stock,candidate):u.mem_map(0x20000,0xc0000);u.mem_map(0x1000000,0x10000);u.mem_map(0x20000000,0x40000);u.mem_map(0x40000000,4096)
  stock.mem_write(0x27000,app.read_bytes());candidate.mem_write(0x1000000,binary.read_bytes())
  def hook(u,a,size,user):
   nonlocal calls
   if a not in (0x79d50,0x100ed00):return
   f=states[id(u)];calls+=1;value=u.reg_read(UC_ARM_REG_R0);assert value==0;f['trace'].append(('shutdown',value,struct.unpack('<I',bytes(u.mem_read(0x40000520,4)))[0]))
   if f['mutate']:u.mem_write(0x40000520,struct.pack('<I',0x12345678))
   u.reg_write(UC_ARM_REG_R0,0xffffffff);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  def write(u,access,a,size,value,user):
   if 0x40000000<=a<0x40001000:states[id(u)]['trace'].append(('mmio',a,size,value))
  for u in (stock,candidate):u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_WRITE,write)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  def run(u,state,context,initial,mutate):
   states[id(u)]=dict(trace=[],mutate=mutate);u.mem_write(0x40000000,bytes([0x6d])*4096);u.mem_write(0x40000520,struct.pack('<I',initial));u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101);u.reg_write(UC_ARM_REG_R0,state);u.reg_write(UC_ARM_REG_R1,context)
   for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
   u.emu_start((0x567ac if u is stock else syms['r1_sdh_state_observer_567ac'])|1,0x20000100,count=10000);assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
   return states[id(u)]['trace'],bytes(u.mem_read(0x40000000,4096))
  for args in itertools.product(range(256),(0,0x20002000,0xffffffff),(0,1,0xa9,0xffffffff),(False,True)):
   a=run(stock,*args);b=run(candidate,*args);assert a==b,(args,a,b);comparisons+=1
 receipt.write_text(json.dumps(dict(application_sha256=sha(app),report_sha256=sha(rp),native_evidence_sha256=sha(ep),comparisons=comparisons,shutdown_calls_per_implementation=calls//2,scope='Exact authenticated SDK example callback slice, all zero-extended byte enum values, ignored contexts, retention initial values and lower-shutdown mutations; native GPREGRET2 write precedes SYSOFF request',limitations=['Power-management shutdown body is a fixture here; no actual system-off, reset, bootloader CRC decision or hardware retention proof.','Full-width values outside the short-enum caller ABI, complete startup/linking and original compiler/image identity remain gates.'],instruction_identity_proven=False),indent=2)+'\n');print(comparisons,'DFU state comparisons;',calls//2,'shutdown requests')
if __name__=='__main__':main()
