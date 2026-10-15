#!/usr/bin/env python3
"""Native timestamp adapter/backend/offset differential, including unbound fault."""
import hashlib,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_MEM_READ_UNMAPPED
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 receipt=BASE/'structured-time/verification.json';receipt.unlink(missing_ok=True);app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 report=json.loads((BASE/'structured-time/report.json').read_text());obj=BASE/'structured-time/structured_time.o';assert sha(obj)==report['units'][0]['object_sha256']
 for path,digest in report['inputs'].items():assert sha(ROOT/path)==digest,path
 registry=BASE/'i2c5/stock_registry.o';r=json.loads((BASE/'i2c5/report.json').read_text());assert sha(registry)==next(x['object_sha256'] for x in r['units'] if x['source'].endswith('stock_registry.c'))
 runtime=BASE/'runtime/memory-runtime.o';assert sha(runtime)==json.loads((BASE/'runtime/report.json').read_text())['relocatable_sha256']
 roots={'r1_structured_log_timestamp_adapter':0x514bc,'r1_time_backend_timestamp':0x8ada4,'r1_structured_log_local_timestamp':0x8ad40};counts={n:0 for n in roots};fault_count=0;state=[0,0]
 with tempfile.TemporaryDirectory() as directory:
  tmp=Path(directory);ld=tmp/'test.ld';elf=tmp/'test.elf';binary=tmp/'test.bin'
  ld.write_text('SECTIONS { .text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } .r1.time.registration 0x20006820 (NOLOAD) : { *(.r1.time.registration) } .r1.time.rtc 0x20007690 (NOLOAD) : { *(.r1.time.rtc) } .r1.time.state 0x20016ac4 (NOLOAD) : { *(.r1.time.state) } /DISCARD/ : { *(.comment) *(.note*) } }')
  subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--gc-sections','--entry=r1_structured_log_timestamp_adapter',*['--undefined='+n for n in roots],str(obj),str(registry),str(runtime),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True)
  syms={x.split()[-1]:int(x.split()[0],16) for x in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x.split())==3}
  stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB);stock.mem_map(0x20000,0xc0000);stock.mem_write(0x27000,app.read_bytes());events={id(stock):[],id(candidate):[]};faults={id(stock):[],id(candidate):[]}
  for uc in (stock,candidate):uc.mem_map(0x1000000,0x10000);uc.mem_map(0x20000000,0x40000)
  candidate.mem_write(0x1000000,binary.read_bytes())
  def hook(uc,address,size,data):
   if address==0x100e000:
    pointer=uc.reg_read(UC_ARM_REG_R2);events[id(uc)].append(('rtc_read',uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1),uc.reg_read(UC_ARM_REG_R3),bytes(uc.mem_read(pointer,64))));uc.mem_write(pointer+44,struct.pack('<I',state[0]));uc.reg_write(UC_ARM_REG_R0,state[1])
   elif address==0x100e010:events[id(uc)].append(('backend_get',uc.reg_read(UC_ARM_REG_R0)));uc.reg_write(UC_ARM_REG_R0,state[0])
   else:return
   uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  def fault(uc,access,address,size,value,data):faults[id(uc)].append((address,size));return False
  for uc in (stock,candidate):uc.hook_add(UC_HOOK_CODE,hook);uc.hook_add(UC_HOOK_MEM_READ_UNMAPPED,fault)
  def run(uc,entry):
   events[id(uc)].clear();faults[id(uc)].clear();uc.reg_write(UC_ARM_REG_SP,0x2003f000);uc.reg_write(UC_ARM_REG_LR,0x20000101)
   try:uc.emu_start(entry|1,0x20000100,count=10000)
   except UcError:assert faults[id(uc)]
   else:assert uc.reg_read(UC_ARM_REG_PC)==0x20000100
   return (None if faults[id(uc)] else uc.reg_read(UC_ARM_REG_R0),list(events[id(uc)]),list(faults[id(uc)]))
  for name,entry in roots.items():
   if name.endswith('_adapter'):cases=((mode,value,0,status) for mode in (0,1,2) for value in (0,1,0x7fffffff,0x80000000,0xffffffff) for status in (0,1,0x87654321))
   else:cases=((mode,value,offset,0) for mode in (0,1) for value in (0,1,0x7fffffff,0x80000000,0xffffffff) for offset in (-32768,-720,-1,0,1,840,32767))
   for mode,value,offset,status in cases:
    state[:]=[value,status]
    for uc in (stock,candidate):
     uc.mem_write(0x20007690,struct.pack('<I',0x20002100 if mode else 0));uc.mem_write(0x20002100,struct.pack('<6I',0,0x20002200,0,0,0,0));ops=[0]*9;ops[4]=0x100e001 if mode==2 else 0;uc.mem_write(0x20002200,struct.pack('<9I',*ops))
     uc.mem_write(0x20006820,bytes(24));uc.mem_write(0x20006828,struct.pack('<I',0x20002300 if mode else 0));uc.mem_write(0x20002300,struct.pack('<5I',0,0,0x100e011,0,0));uc.mem_write(0x20016ac4,bytes(32));uc.mem_write(0x20016acc,struct.pack('<h',offset))
    a=run(stock,entry);b=run(candidate,syms[name]);assert a==b,(name,mode,value,offset,status,a,b)
    if a[2]:assert a[2]==[(8,4)];fault_count+=1
    else:
     expected=(value if mode==2 else 0) if name.endswith('_adapter') else ((value+(offset*60 if name.endswith('local_timestamp') else 0))&0xffffffff)
     assert a[0]==expected
    counts[name]+=1
 result=dict(application_sha256=sha(app),report_sha256=sha(BASE/'structured-time/report.json'),object_sha256=sha(obj),registry_report_sha256=sha(BASE/'i2c5/report.json'),runtime_report_sha256=sha(BASE/'runtime/report.json'),comparisons=sum(counts.values()),comparisons_by_entry=counts,unbound_fault_comparisons=fault_count,scope='Actual native registry dispatch, zeroed 64-byte RTC request, ignored status, backend NULL context, signed offsets and wraparound versus stock',limitations=['Final RTC/backend operations are intercepted. Actual clock/calendar providers and RTC registration remain open.','Unmapped reads establish emulated fault address/width, not physical exception state.','Initial native roots are unbound; callers must install the actual providers.'],instruction_identity_proven=False)
 receipt.write_text(json.dumps(result,indent=2)+'\n');print(f'{sum(counts.values())} native timestamp comparisons passed, including {fault_count} unbound faults')
if __name__=='__main__':main()
