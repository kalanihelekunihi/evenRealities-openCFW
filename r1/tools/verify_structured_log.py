#!/usr/bin/env python3
"""Original-code oracle for native structured-log routing and Arm varargs."""
import hashlib,json,struct,subprocess,tempfile,sys
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_IPSR,UC_ARM_REG_BASEPRI
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 real_critical='--real-critical' in sys.argv
 receipt=BASE/('structured-log/critical-integration-verification.json' if real_critical else 'structured-log/verification.json');receipt.unlink(missing_ok=True);app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 report=json.loads((BASE/'structured-log/report.json').read_text());obj=BASE/'structured-log/structured_log.o';assert sha(obj)==report['units'][0]['object_sha256']
 for path,digest in report['inputs'].items():assert sha(ROOT/path)==digest,path
 seams=BASE/'board-seams/stock_seams.o';assert sha(seams)==json.loads((BASE/'board-seams/report.json').read_text())['units'][0]['object_sha256']
 critical=BASE/'rtos-critical/critical-only.o';critical_report=BASE/'rtos-critical/report.json'
 if real_critical:assert sha(critical)==json.loads(critical_report.read_text())['selected_object_sha256']
 roots={'r1_structured_log_format':0x91638,'r1_structured_log_clock_available':0x91864,'r1_structured_log_export_active':0x590a0};counts={n:0 for n in roots}
 with tempfile.TemporaryDirectory() as directory:
  tmp=Path(directory);ld=tmp/'layout.ld';elf=tmp/'test.elf';binary=tmp/'test.bin'
  ld.write_text('SECTIONS { .text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } .r1.log.clock 0x2000653c (NOLOAD) : { *(.r1.log.clock) } .r1.log.mode 0x200068ec : { *(.r1.log.mode) } .r1.log.export 0x20006906 (NOLOAD) : { *(.r1.log.export) } .bss 0x20007814 (NOLOAD) : { *(.bss*) } /DISCARD/ : { *(.comment) *(.note*) } }')
  subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--gc-sections','--entry=r1_structured_log_format',*['--undefined='+n for n in roots],*([str(critical)] if real_critical else ['--defsym=vPortEnterCritical=0x100e001','--defsym=vPortExitCritical=0x100e011']),'--defsym=r1_structured_log_encode_format=0x100e021',str(obj),str(seams),'-o',str(elf)],check=True,capture_output=True)
  subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True)
  syms={x.split()[-1]:int(x.split()[0],16) for x in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x.split())==3}
  stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);stock.mem_map(0x20000,0xc0000);stock.mem_write(0x27000,app.read_bytes());events={id(stock):[],id(candidate):[]}
  for uc in (stock,candidate):uc.mem_map(0x1000000,0x10000);uc.mem_map(0x20000000,0x40000);uc.mem_map(0xe000e000,0x1000)
  candidate.mem_write(0x1000000,binary.read_bytes())
  def hook(uc,address,size,user):
   if real_critical and address in (0x95cf4,0x95d24):return
   if address in (0x95cf4,0x100e000):events[id(uc)].append(('enter',uc.reg_read(UC_ARM_REG_BASEPRI)))
   elif address in (0x95d24,0x100e010):events[id(uc)].append(('exit',uc.reg_read(UC_ARM_REG_BASEPRI)))
   elif address in (0x46fd4,0x100e020):
    pointer=uc.reg_read(UC_ARM_REG_R1);fmt=bytes(uc.mem_read(pointer,64)).split(b'\0')[0]
    args=struct.unpack('<3I',bytes(uc.mem_read(uc.reg_read(UC_ARM_REG_R2),12)))
    events[id(uc)].append(('encode',uc.reg_read(UC_ARM_REG_R0),fmt,args,uc.reg_read(UC_ARM_REG_BASEPRI)))
   else:return
   uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  for uc in (stock,candidate):uc.hook_add(UC_HOOK_CODE,hook)
  def run(uc,entry,mode,clock,export,ipsr,basepri,marker,descriptor):
   for address,value in ((0x200068ec,mode),(0x2000653c,clock),(0x20006906,export)):uc.mem_write(address,bytes([value]))
   events[id(uc)].clear();uc.mem_write(0x20002000,b'%08x %u %x\0');uc.mem_write(0x2003f000,struct.pack('<2I',0x87654321,0xdeadbeef));uc.reg_write(UC_ARM_REG_SP,0x2003f000);uc.reg_write(UC_ARM_REG_LR,0x20000101);uc.reg_write(UC_ARM_REG_IPSR,ipsr);uc.reg_write(UC_ARM_REG_BASEPRI,basepri)
   for reg,value in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),(marker,descriptor,0x20002000,0x12345678)):uc.reg_write(reg,value)
   uc.emu_start(entry|1,0x20000100,count=10000);assert uc.reg_read(UC_ARM_REG_PC)==0x20000100
   return (uc.reg_read(UC_ARM_REG_R0),list(events[id(uc)]),uc.reg_read(UC_ARM_REG_BASEPRI))
  for name,entry in roots.items():
   if name=='r1_structured_log_format':cases=((mode,clock,export,ipsr,basepri,marker,descriptor) for mode in range(256) for clock,export in ((0,0),(0,1),(1,0),(1,1)) for ipsr,basepri in ((0,0),(16,32),(16,255)) for marker,descriptor in ((0x04400000,0x20002100),(0xffffffff,0x20003fff)))
   else:cases=((0,value,value,0,0,0,0) for value in range(256))
   for args in cases:
    a=run(stock,entry,*args);b=run(candidate,syms[name],*args);assert a==b,(name,args,a,b);counts[name]+=1
 result=dict(application_sha256=sha(app),report_sha256=sha(BASE/'structured-log/report.json'),object_sha256=sha(obj),seam_report_sha256=sha(BASE/'board-seams/report.json'),comparisons=sum(counts.values()),comparisons_by_entry=counts,actual_critical_functions=real_critical,critical_report_sha256=sha(critical_report) if real_critical else None,scope='All mode bits and clock/export gates, task/ISR routing, BASEPRI restoration, header packing and three variadic words versus original Thumb',limitations=[('Only final encoding is intercepted; actual critical functions execute.' if real_critical else 'FreeRTOS critical entry/exit and final encoding are intercepted to compare calls.'),'No scheduler, transport output or asynchronous exception delivery is proven.','Descriptor-address relocation and original instruction identity remain open.'],instruction_identity_proven=False)
 receipt.write_text(json.dumps(result,indent=2)+'\n');print(f'{sum(counts.values())} structured-log comparisons passed')
if __name__=='__main__':main()
