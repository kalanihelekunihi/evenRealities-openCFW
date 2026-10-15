#!/usr/bin/env python3
"""Actual CMSIS/kernel tick and priority-assert differential."""
import hashlib,json,struct,subprocess,tempfile,itertools
from pathlib import Path
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_WRITE_UNMAPPED
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_IPSR,UC_ARM_REG_BASEPRI,UC_ARM_REG_PRIMASK
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 receipt=BASE/'rtos-ticks/verification.json';receipt.unlink(missing_ok=True);app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 report=json.loads((BASE/'rtos-ticks/report.json').read_text());obj=BASE/'rtos-ticks/ticks-only.o';assert sha(obj)==report['selected_object_sha256']
 for path,digest in report['inputs'].items():assert sha(ROOT/path)==digest,path
 comparisons=0;fault_count=0;isr_paths=0
 with tempfile.TemporaryDirectory() as directory:
  tmp=Path(directory);ld=tmp/'layout.ld';elf=tmp/'test.elf';binary=tmp/'test.bin'
  variables={'ucMaxSysCallPriority':0x20007810,'ulMaxPRIGROUPValue':0x20007818,'xTickCount':0x20007828,'xSchedulerRunning':0x20007830,'uxSchedulerSuspended':0x20007850}
  ld.write_text('SECTIONS { .text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } '+''.join('.bss.'+name+' '+hex(address)+' (NOLOAD) : { *(.bss.'+name+') } ' for name,address in variables.items())+'/DISCARD/ : { *(.comment) *(.note*) } }')
  subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--entry=osKernelGetTickCount',str(obj),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True)
  syms={x.split()[-1]:int(x.split()[0],16) for x in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x.split())==3}
  for name,address in variables.items():assert syms[name]==address,(name,syms[name],address)
  stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);stock.mem_map(0x20000,0xc0000);stock.mem_write(0x27000,app.read_bytes());faults={id(stock):[],id(candidate):[]};paths={id(stock):[],id(candidate):[]}
  def fault(uc,access,address,size,value,data):faults[id(uc)].append((address,size,value));return False
  def observe(uc,address,size,data):
   if address==(0x95f18 if uc is stock else syms['vPortValidateInterruptPriority']):paths[id(uc)].append('validate')
  for uc in (stock,candidate):uc.mem_map(0x1000000,0x10000);uc.mem_map(0x20000000,0x40000);uc.mem_map(0xe000e000,0x1000);uc.hook_add(UC_HOOK_MEM_WRITE_UNMAPPED,fault);uc.hook_add(UC_HOOK_CODE,observe)
  candidate.mem_write(0x1000000,binary.read_bytes())
  def run(uc,entry,case):
   tick,running,suspended,ipsr,primask,basepri,priority,threshold,group,maxgroup=case
   for address,value in ((0x20007818,maxgroup),(0x20007828,tick),(0x20007830,running),(0x20007850,suspended),(0xe000ed0c,group<<8)):uc.mem_write(address,struct.pack('<I',value))
   uc.mem_write(0x20007810,bytes([threshold]));uc.mem_write(0xe000e400,bytes([priority])*240);uc.reg_write(UC_ARM_REG_IPSR,ipsr);uc.reg_write(UC_ARM_REG_PRIMASK,primask);uc.reg_write(UC_ARM_REG_BASEPRI,basepri);uc.reg_write(UC_ARM_REG_SP,0x2003f000);uc.reg_write(UC_ARM_REG_LR,0x20000101);faults[id(uc)].clear();paths[id(uc)].clear()
   try:uc.emu_start(entry|1,0x20000100,count=10000)
   except UcError:assert faults[id(uc)]
   else:assert uc.reg_read(UC_ARM_REG_PC)==0x20000100
   return (None if faults[id(uc)] else uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_BASEPRI),uc.reg_read(UC_ARM_REG_PRIMASK),list(paths[id(uc)]),list(faults[id(uc)]))
  for case in itertools.product((0,1,0x7fffffff,0x80000000,0xffffffff),(0,1),(0,1),(0,15,16,20),(0,1),(0,32,128),(0,64,192),(0,64),(0,4,7),(0,4)):
   a=run(stock,0x7d28c,case);b=run(candidate,syms['osKernelGetTickCount'],case);assert a==b,(case,a,b);comparisons+=1
   if a[4]:assert a[4]==[(0xffffffff,4,0)];fault_count+=1
   else:assert a[0]==case[0]
   if a[3]:isr_paths+=1
 result=dict(application_sha256=sha(app),report_sha256=sha(BASE/'rtos-ticks/report.json'),selected_object_sha256=sha(obj),comparisons=comparisons,assertion_fault_comparisons=fault_count,interrupt_tick_paths=isr_paths,scope='Actual CMSIS IRQ-context selection, scheduler/tick reads and Nordic priority/group assertions versus stock with no provider interception',limitations=['Kernel state and NVIC registers are explicit fixtures, not an executing scheduler or physical interrupt controller.','Physical fault registers, scheduler startup and whole-image identity remain open.'],instruction_identity_proven=False)
 receipt.write_text(json.dumps(result,indent=2)+'\n');print(f'{comparisons} tick/context comparisons passed, including {fault_count} priority faults')
if __name__=='__main__':main()
