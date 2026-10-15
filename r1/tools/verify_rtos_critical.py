#!/usr/bin/env python3
"""Compare actual source-compiled critical nesting and assertion faults."""
import hashlib,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_MEM_WRITE_UNMAPPED
from unicorn.arm_const import UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_BASEPRI
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 receipt=BASE/'rtos-critical/verification.json';receipt.unlink(missing_ok=True);app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 report=json.loads((BASE/'rtos-critical/report.json').read_text());obj=BASE/'rtos-critical/critical-only.o';assert sha(obj)==report['selected_object_sha256']
 for path,digest in report['inputs'].items():assert sha(ROOT/path)==digest,path
 calls=0;fault_count=0
 with tempfile.TemporaryDirectory() as directory:
  tmp=Path(directory);ld=tmp/'layout.ld';elf=tmp/'test.elf';binary=tmp/'test.bin';ld.write_text('SECTIONS { .text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } .bss 0x20007814 (NOLOAD) : { *(.bss*) } /DISCARD/ : { *(.comment) *(.note*) } }')
  subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--entry=vPortEnterCritical',str(obj),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True)
  syms={x.split()[-1]:int(x.split()[0],16) for x in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x.split())==3};assert syms['uxCriticalNesting']==0x20007814
  stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);stock.mem_map(0x20000,0xc0000);stock.mem_write(0x27000,app.read_bytes());faults={id(stock):[],id(candidate):[]}
  def fault(uc,access,address,size,value,data):faults[id(uc)].append((address,size,value));return False
  for uc in (stock,candidate):uc.mem_map(0x1000000,0x10000);uc.mem_map(0x20000000,0x40000);uc.mem_map(0xe000e000,0x1000);uc.hook_add(UC_HOOK_MEM_WRITE_UNMAPPED,fault)
  candidate.mem_write(0x1000000,binary.read_bytes())
  def call(uc,entry):
   faults[id(uc)].clear();uc.reg_write(UC_ARM_REG_SP,0x2003f000);uc.reg_write(UC_ARM_REG_LR,0x20000101)
   try:uc.emu_start(entry|1,0x20000100,count=10000)
   except UcError:assert faults[id(uc)]
   else:assert uc.reg_read(UC_ARM_REG_PC)==0x20000100
   return (bytes(uc.mem_read(0x20007814,4)),uc.reg_read(UC_ARM_REG_BASEPRI),list(faults[id(uc)]))
  for nesting in (0,1,2,3,1000,0xfffffffe,0xffffffff):
   for active in (0,1,0x1ff,0x200,0x10000):
    for basepri in (0,32,128,255):
     for sequence in (('enter',),('exit',),('enter','enter','exit','exit'),('exit','enter')):
      for uc in (stock,candidate):uc.mem_write(0x20007814,struct.pack('<I',nesting));uc.mem_write(0xe000ed04,struct.pack('<I',active));uc.reg_write(UC_ARM_REG_BASEPRI,basepri)
      for role in sequence:
       a=call(stock,0x95cf4 if role=='enter' else 0x95d24);b=call(candidate,syms['vPortEnterCritical' if role=='enter' else 'vPortExitCritical']);assert a==b,(nesting,active,basepri,sequence,role,a,b);calls+=1
       if a[2]:assert a[2]==[(0xffffffff,4,0)];fault_count+=1;break
 result=dict(application_sha256=sha(app),report_sha256=sha(BASE/'rtos-critical/report.json'),selected_object_sha256=sha(obj),comparisons=calls,assertion_fault_comparisons=fault_count,scope='Actual pinned Nordic port bodies versus stock: nesting, overflow, BASEPRI, active-exception checks and exact invalid assertion write',limitations=['Unmapped-write emulation does not prove physical exception state.','Whole scheduler startup, task switching and other port functions remain open.','Original instruction identity remains unproven.'],instruction_identity_proven=False)
 receipt.write_text(json.dumps(result,indent=2)+'\n');print(f'{calls} critical-section comparisons passed, including {fault_count} assertion faults')
if __name__=='__main__':main()
