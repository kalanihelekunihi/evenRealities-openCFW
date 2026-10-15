#!/usr/bin/env python3
"""Stock differential for error logging, volatile mode reads and delay work."""
import hashlib,json,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_MEM_READ
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 receipt=BASE/'board-seams/verification.json';receipt.unlink(missing_ok=True);app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 report=json.loads((BASE/'board-seams/report.json').read_text());obj=BASE/'board-seams/stock_seams.o';assert sha(obj)==report['units'][0]['object_sha256']
 for path,digest in report['inputs'].items():assert sha(ROOT/path)==digest,path
 gpio=BASE/'software-twi/sdk_gpio.o';assert sha(gpio)==json.loads((BASE/'software-twi/gpio-report.json').read_text())['units'][0]['object_sha256']
 roots={'r1_adc_error':0x4e5bc,'r1_structured_log_mode_get':0x914ec,'r1_st25_delay_ms':0x784f0};counts={name:0 for name in roots}
 with tempfile.TemporaryDirectory() as directory:
  tmp=Path(directory);ld=tmp/'layout.ld';elf=tmp/'test.elf';binary=tmp/'text.bin';data=tmp/'mode.bin'
  ld.write_text('SECTIONS { .text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } .r1.log.mode 0x200068ec : { *(.r1.log.mode) } /DISCARD/ : { *(.comment) *(.note*) } }')
  subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--gc-sections','--entry=r1_adc_error',*['--undefined='+n for n in roots],'--defsym=r1_structured_log_format=0x100e001','--defsym=nrf_log_frontend_std_1=0x100e011',str(obj),str(gpio),'-o',str(elf)],check=True,capture_output=True)
  subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True);subprocess.run(['arm-none-eabi-objcopy','--dump-section','.r1.log.mode='+str(data),str(elf)],check=True);assert data.read_bytes()==b'\1'
  syms={x.split()[-1]:int(x.split()[0],16) for x in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x.split())==3}
  stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB);stock.mem_map(0x20000,0xc0000);stock.mem_write(0x27000,app.read_bytes());events={id(stock):[],id(candidate):[]};mutation=[0]
  for uc in (stock,candidate):uc.mem_map(0x1000000,0x10000);uc.mem_map(0x20000000,0x40000)
  candidate.mem_write(0x1000000,binary.read_bytes());stock.reg_write(UC_ARM_REG_SP,0x2003f000);stock.emu_start(0x283a1,0x27208,count=2000000);assert bytes(stock.mem_read(0x200068ec,1))==data.read_bytes()
  def string(uc,p):return bytes(uc.mem_read(p,64)).split(b'\0')[0].decode()
  def hook(uc,address,size,user):
   if address in (0x91638,0x100e000):
    events[id(uc)].append(('r1_log',uc.reg_read(UC_ARM_REG_R0),string(uc,uc.reg_read(UC_ARM_REG_R1)),string(uc,uc.reg_read(UC_ARM_REG_R2)),uc.reg_read(UC_ARM_REG_R3)));uc.mem_write(0x200068ec,bytes([mutation[0]]))
   elif address in (0x799c8,0x100e010):events[id(uc)].append(('sdk_log',uc.reg_read(UC_ARM_REG_R0),string(uc,uc.reg_read(UC_ARM_REG_R1)),uc.reg_read(UC_ARM_REG_R2)))
   elif address in (0x99cd0,syms['r1_twi_delay_busy']):events[id(uc)].append(('delay_work',uc.reg_read(UC_ARM_REG_R0)*(64 if uc is candidate else 1)))
   else:return
   uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  def read(uc,access,address,size,value,user):events[id(uc)].append(('mode_read',bytes(uc.mem_read(address,size))))
  for uc in (stock,candidate):uc.hook_add(UC_HOOK_CODE,hook);uc.hook_add(UC_HOOK_MEM_READ,read,begin=0x200068ec,end=0x200068ec)
  def run(uc,entry,arg,mode,returns):
   events[id(uc)].clear();uc.mem_write(0x200068ec,bytes([mode]));uc.reg_write(UC_ARM_REG_R0,arg);uc.reg_write(UC_ARM_REG_SP,0x2003f000);uc.reg_write(UC_ARM_REG_LR,0x20000101);uc.emu_start(entry|1,0x20000100,count=100000);assert uc.reg_read(UC_ARM_REG_PC)==0x20000100
   return (uc.reg_read(UC_ARM_REG_R0) if returns else None,list(events[id(uc)]),bytes(uc.mem_read(0x200068ec,1)))
  for name,entry in roots.items():
   if name=='r1_adc_error':cases=((error,mode,after) for mode in range(256) for error in (0,7,0xffffffff) for after in (0,2))
   elif name=='r1_structured_log_mode_get':cases=((0,mode,0) for mode in range(256))
   else:cases=((ms,1,0) for ms in (0,1,2,10,255,1000))
   for arg,mode,after in cases:
    mutation[0]=after;a=run(stock,entry,arg,mode,name.endswith('_get'));b=run(candidate,syms[name],arg,mode,name.endswith('_get'));assert a==b,(name,arg,mode,after,a,b);counts[name]+=1
 result=dict(application_sha256=sha(app),report_sha256=sha(BASE/'board-seams/report.json'),object_sha256=sha(obj),gpio_report_sha256=sha(BASE/'software-twi/gpio-report.json'),comparisons=sum(counts.values()),comparisons_by_entry=counts,scope='Original log flags/getter/error routing and millisecond work-unit ordering; includes all 256 flags, backend flag mutation, exact format/packed IDs and zero delay',limitations=['Logging backends and raw delay kernels are intercepted to compare calls; backend runtime and cycle timing remain unproven.','Error wrapper returns in stock; no reset/halt is added.','Large nonzero millisecond counts beyond tested values are not executed.'],instruction_identity_proven=False)
 receipt.write_text(json.dumps(result,indent=2)+'\n');print(f'{sum(counts.values())} board seam comparisons passed')
if __name__=='__main__':main()
