#!/usr/bin/env python3
"""Execute native cache reads with real memory and critical providers."""
import hashlib,json,struct,subprocess,tempfile,itertools
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_IPSR,UC_ARM_REG_BASEPRI
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 receipt=BASE/'structured-cache-copy/verification.json';receipt.unlink(missing_ok=True);app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 report=BASE/'structured-cache-copy/report.json';data=json.loads(report.read_text());obj=BASE/'structured-cache-copy/structured_cache_copy.o';assert sha(obj)==data['units'][0]['object_sha256']
 for path,digest in data['inputs'].items():assert sha(ROOT/path)==digest,path
 provider_reports={};others=[]
 for relative,object_name,field in (('runtime/report.json','runtime/memory-runtime.o','relocatable_sha256'),('rtos-critical/report.json','rtos-critical/critical-only.o','selected_object_sha256'),('structured-cache/report.json','structured-cache/structured_cache.o','unit')):
  r=json.loads((BASE/relative).read_text());path=BASE/object_name;assert sha(path)==(r['units'][0]['object_sha256'] if field=='unit' else r[field]);others.append(path);provider_reports[relative]=sha(BASE/relative)
 with tempfile.TemporaryDirectory() as directory:
  tmp=Path(directory);ld=tmp/'layout.ld';elf=tmp/'test.elf';binary=tmp/'test.bin';ld.write_text('SECTIONS { .text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } .r1.log.cache 0x200068f4 (NOLOAD) : { *(.r1.log.cache) } .bss.uxCriticalNesting 0x20007814 (NOLOAD) : { *(.bss.uxCriticalNesting) } /DISCARD/ : { *(.comment) *(.note*) } }')
  subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--gc-sections','--entry=r1_structured_log_cache_copy',str(obj),*map(str,others),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True)
  syms={x.split()[-1]:int(x.split()[0],16) for x in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x.split())==3};assert syms['uxCriticalNesting']==0x20007814
  stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);stock.mem_map(0x20000,0xc0000);stock.mem_write(0x27000,app.read_bytes())
  for uc in (stock,candidate):uc.mem_map(0x1000000,0x10000);uc.mem_map(0x20000000,0x40000);uc.mem_map(0xe000e000,0x1000)
  candidate.mem_write(0x1000000,binary.read_bytes());pattern=bytes((i*17+3)&255 for i in range(8192));blank=bytes([0x55])*4096
  def run(uc,entry,case):
   capacity,read,write,length,peek,ipsr,basepri,nesting=case
   uc.mem_write(0x200068f4,struct.pack('<4I',0x20010000,capacity,read,write));uc.mem_write(0x20010000,pattern);uc.mem_write(0x20002000,blank);uc.mem_write(0x20007814,struct.pack('<I',nesting));uc.reg_write(UC_ARM_REG_IPSR,ipsr);uc.reg_write(UC_ARM_REG_BASEPRI,basepri)
   uc.reg_write(UC_ARM_REG_R0,peek);uc.reg_write(UC_ARM_REG_R1,0x20002000);uc.reg_write(UC_ARM_REG_R2,length);uc.reg_write(UC_ARM_REG_SP,0x2003f000);uc.reg_write(UC_ARM_REG_LR,0x20000101);uc.emu_start(entry|1,0x20000100,count=200000);assert uc.reg_read(UC_ARM_REG_PC)==0x20000100
   return uc.reg_read(UC_ARM_REG_R0),bytes(uc.mem_read(0x200068f4,16)),bytes(uc.mem_read(0x20002000,4096)),uc.reg_read(UC_ARM_REG_BASEPRI),bytes(uc.mem_read(0x20007814,4))
  comparisons=0
  for capacity in (0,1,2,8,236,4096):
   positions=sorted({0,1,max(0,capacity-1),capacity,capacity+1})
   for case in itertools.product((capacity,),positions,positions,(0,1,2,7,235,236),(0,1,0xffffffff),(0,15,20),(0,32,128),(0,2)):
    a=run(stock,0x41c5c,case);b=run(candidate,syms['r1_structured_log_cache_copy'],case);assert a==b,(case,a[0:2],b[0:2],a[3:],b[3:]);comparisons+=1
 receipt.write_text(json.dumps(dict(application_sha256=sha(app),report_sha256=sha(report),object_sha256=sha(obj),provider_reports=provider_reports,comparisons=comparisons,scope='Exact copied bytes, consume/peek cursor, success result, invalid indexes, wrapping and task/ISR critical state with real compiled memcpy and critical bodies; no provider interception',limitations=['Ring initialization, concurrent mutation, physical exceptions and original compiler output remain open.','Aliasing and invalid data pointers are not exercised.'],instruction_identity_proven=False),indent=2)+'\n');print(f'{comparisons} structured cache-copy comparisons passed')
if __name__=='__main__':main()
