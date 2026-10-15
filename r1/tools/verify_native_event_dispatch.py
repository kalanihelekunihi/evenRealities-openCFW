#!/usr/bin/env python3
"""Check native dispatch indexing, halfword truncation and payload ownership."""
import hashlib,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
TABLES={'r1_native_event_table_sensor':0x20006750,'r1_native_event_table_system':0x20006e54,'r1_native_event_table_storage':0x200066fc}
def main():
 receipt=BASE/'native-event-dispatch/verification.json';receipt.unlink(missing_ok=True);app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';report=BASE/'native-event-dispatch/report.json';data=json.loads(report.read_text());obj=BASE/'native-event-dispatch/native_event_dispatch.o';assert sha(obj)==data['units'][0]['object_sha256']
 for path,digest in data['inputs'].items():assert sha(ROOT/path)==digest,path
 runtime=BASE/'runtime/memory-runtime.o';runtime_report=BASE/'runtime/report.json';assert sha(runtime)==json.loads(runtime_report.read_text())['relocatable_sha256']
 with tempfile.TemporaryDirectory() as directory:
  tmp=Path(directory);ld=tmp/'layout.ld';elf=tmp/'test.elf';binary=tmp/'test.bin';ld.write_text('SECTIONS { .text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } /DISCARD/ : { *(.comment) *(.note*) } }');subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--defsym=vPortFree=0x100e001',*['--defsym='+n+'='+hex(a) for n,a in TABLES.items()],str(obj),str(runtime),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True)
  syms={x.split()[-1]:int(x.split()[0],16) for x in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x.split())==3};stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB);stock.mem_map(0x20000,0xc0000);stock.mem_write(0x27000,app.read_bytes());events={id(stock):[],id(candidate):[]}
  for uc in (stock,candidate):uc.mem_map(0x1000000,0x10000);uc.mem_map(0x20000000,0x40000)
  candidate.mem_write(0x1000000,binary.read_bytes());pattern=b''.join(struct.pack('<I',0 if i%5==0 else 0x100e101 if i%2 else 0x100e111) for i in range(0x5000//4))
  # Broad table fixtures deliberately overlap as the original address ranges do.
  for uc in (stock,candidate):uc.mem_write(0x20006000,pattern)
  def hook(uc,address,size,user):
   if address in (0x100e100,0x100e110):
    events[id(uc)].append(('callback',0 if address==0x100e100 else 1,uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1)));uc.mem_write(0x20002004,struct.pack('<3I',0xffffffff,0,0xdeadbeef))
   elif address in (0x95d48,0x100e000):events[id(uc)].append(('free',uc.reg_read(UC_ARM_REG_R0)))
   else:return
   uc.reg_write(UC_ARM_REG_R0,0x87654321);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  for uc in (stock,candidate):uc.hook_add(UC_HOOK_CODE,hook)
  def run(uc,entry,id,length,payload):
   events[id_builtin(uc)].clear();uc.mem_write(0x20002000,struct.pack('<4I',0x12345678,id,length,payload));uc.reg_write(UC_ARM_REG_R0,0x20002000);uc.reg_write(UC_ARM_REG_SP,0x2003f000);uc.reg_write(UC_ARM_REG_LR,0x20000101);uc.emu_start(entry|1,0x20000100,count=10000);assert uc.reg_read(UC_ARM_REG_PC)==0x20000100;return list(events[id_builtin(uc)]),bytes(uc.mem_read(0x20002000,16))
  id_builtin=id
  comparisons=0
  for low_id in range(65536):
   full_id=low_id|((low_id^0xabcd)<<16)
   for length in (0xbeef0000,0xbeef0004,0xbeef0005):
    payload=0x89abcdef^low_id;a=run(stock,0x8d888,full_id,length,payload);b=run(candidate,syms['r1_native_event_dispatch'],full_id,length,payload);assert a==b,(hex(full_id),hex(length),a,b);comparisons+=1
  boundary_comparisons=0
  for event_id in (0,1,2,0xffe,0xfff,0x1000,0x1ffe,0x1fff,0x2000,0x2ffe,0x2fff,0xffff,0xffffffff):
   for length in (1,2,3,5,0xffff,0x10000,0x10001,0x10005,0xffffffff):
    for payload in (0,1,0x20010000,0xffffffff):
     assert run(stock,0x8d888,event_id,length,payload)==run(candidate,syms['r1_native_event_dispatch'],event_id,length,payload);boundary_comparisons+=1
 receipt.write_text(json.dumps(dict(application_sha256=sha(app),report_sha256=sha(report),object_sha256=sha(obj),runtime_report_sha256=sha(runtime_report),comparisons=comparisons,boundary_comparisons=boundary_comparisons,table_anchor_addresses={n:hex(a) for n,a in TABLES.items()},scope='Every 16-bit ID across three callback/free length classes; nonzero high ID/length words, exact physical table indexing, callback arguments, cached payload/length after callback mutation and unconditional ownership release',limitations=['Callback tables are broad overlapping RAM fixtures and callbacks/free are intercepted; complete stock callback configuration and actual handlers remain gates.','Lookup ranges can access words outside known table prefixes; no unsupported bounds guards or fabricated array extent are added.','Invalid record pointers and physical execution are not exercised; original instruction identity and whole-image source completeness remain open.'],instruction_identity_proven=False),indent=2)+'\n');print(f'{comparisons} exhaustive-ID and {boundary_comparisons} boundary dispatch comparisons passed')
if __name__=='__main__':main()
