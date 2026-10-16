#!/usr/bin/env python3
"""Pinned legacy clock logic/native observer differential contracts."""
import hashlib,itertools,json,struct,subprocess,tempfile,sys
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();CONTROL=0x2002c154;NODES=0x20003000
ENTRIES={'r1_soc_observer_907fc':(0x907fc,18),'r1_sdh_state_observer_890f0':(0x890f0,84),'r1_sdk_clock_notify':(0x584ac,34),'r1_sdk_clock_irq_handler':(0x584d4,24),'r1_sdk_clock_item_enqueue':(0x72bca,22),'nrf_drv_clock_init':(0x788c8,98),'nrf_drv_clock_lfclk_request':(0x78990,78),'nrf_drv_clock_lfclk_release':(0x7895c,48)}
def main():
 real_hw='--real-hardware' in sys.argv;real='--real-critical' in sys.argv or real_hw;out=BASE/'sdk-clock';rp=out/'report.json';r=json.loads(rp.read_text());obj=out/'clock.o';receipt=out/('hardware-integration-verification.json' if real_hw else 'critical-integration-verification.json' if real else 'verification.json');receipt.unlink(missing_ok=True);assert sha(obj)==r['selected_object_sha256']
 for p,d in r['inputs'].items():assert sha(ROOT/p)==d,p
 cr=BASE/'sdk-critical/report.json';co=BASE/'sdk-critical/critical-only.o'
 if real:assert sha(co)==json.loads(cr.read_text())['selected_object_sha256']
 hr=BASE/'sdk-nrfx-clock/report.json';ho=BASE/'sdk-nrfx-clock/nrfx-clock.o'
 if real_hw:
  hardware=json.loads(hr.read_text());assert sha(ho)==hardware['selected_object_sha256']
  for p,d in hardware['inputs'].items():assert sha(ROOT/p)==d,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';blob=app.read_bytes();ep=out/'evidence.json';e=json.loads(ep.read_text());assert e['application_sha256']==sha(app)
 for row in e['functions']:
  p=out/row['ghidra_file'];assert sha(p)==row['ghidra_sha256'];a=int(row['entry'],16);assert bytes(json.loads(p.read_text())['data'])==blob[a-0x27000:a-0x27000+row['body_bytes']]
 rr=out/e['rea_notify_receipt']['file'];assert sha(rr)==e['rea_notify_receipt']['sha256'];rea=json.loads(rr.read_text());assert rea['subject']['digest']['sha256']==sha(BASE/'i2c5/stock-analysis-exec.elf') and rea['normalized_result']['procedure']['body']['total_bytes']==34
 states={};comparisons=0;callback_calls=0
 bindings={'nrfx_clock_init':0x100e001,'nrfx_clock_enable':0x100e011,'nrfx_clock_lfclk_start':0x100e021,'nrfx_clock_lfclk_stop':0x100e031,'nrf_sdh_is_enabled':0x100e041,'r1_structured_log_mode_get':0x100e051,'r1_structured_log_format':0x100e061,'nrf_strerror_get':0x100e071}
 if real_hw:
  for n in ('nrfx_clock_init','nrfx_clock_enable','nrfx_clock_lfclk_start','nrfx_clock_lfclk_stop'):bindings.pop(n)
 if not real:bindings.update(app_util_critical_region_enter=0x100e081,app_util_critical_region_exit=0x100e091)
 with tempfile.TemporaryDirectory() as directory:
  t=Path(directory);ld=t/'layout.ld';elf=t/'test.elf';binary=t/'text.bin';ld.write_text('SECTIONS { .bss.r1_sdk_nrfx_clock_control 0x20007938 (NOLOAD) : { *(.bss.r1_sdk_nrfx_clock_control) } .bss.r1_sdk_clock_control 0x2002c154 (NOLOAD) : { *(.bss.r1_sdk_clock_control) } .bss.nrf_nvic_state 0x2002c2fc (NOLOAD) : { *(.bss.nrf_nvic_state) } .text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } /DISCARD/ : { *(.comment) *(.note*) } }')
  subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--entry=nrf_drv_clock_init',*['--defsym='+n+'='+hex(a) for n,a in bindings.items()],str(obj),*([str(co)] if real else []),*([str(ho)] if real_hw else []),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True);syms={x.split()[-1]:int(x.split()[0],16) for x in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x.split())==3};assert syms['r1_sdk_clock_control']==CONTROL
  stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
  for u in (stock,candidate):u.mem_map(0x20000,0xc0000);u.mem_map(0x1000000,0x10000);u.mem_map(0x20000000,0x40000);u.mem_map(0x40010000,0x2000);u.mem_map(0x40000000,4096);u.mem_map(0xe000e000,4096);u.mem_write(0x27000,blob)
  candidate.mem_write(0x1000000,binary.read_bytes());stock.reg_write(UC_ARM_REG_SP,0x2003f000);stock.emu_start(0x283a1,0x27208,count=2000000);assert stock.reg_read(UC_ARM_REG_PC)==0x27208 and bytes(stock.mem_read(CONTROL,20))==bytes(candidate.mem_read(CONTROL,20))==bytes(20)
  calls={0x7a66c:'init',0x7a640:'enable',0x7a68c:'lf_start',0x7a6ac:'lf_stop',0x7a4d8:'sd_enabled',0x914ec:'mode',0x91638:'log',0x7a5cc:'strerror'};calls.update({bindings[n]&~1:k for n,k in [('nrfx_clock_init','init'),('nrfx_clock_enable','enable'),('nrfx_clock_lfclk_start','lf_start'),('nrfx_clock_lfclk_stop','lf_stop'),('nrf_sdh_is_enabled','sd_enabled'),('r1_structured_log_mode_get','mode'),('r1_structured_log_format','log'),('nrf_strerror_get','strerror')] if n in bindings})
  if real_hw:calls={a:k for a,k in calls.items() if k not in ('init','enable','lf_start','lf_stop')}
  if not real:calls.update({0x4ebec:'enter',0x4ec34:'exit',0x100e080:'enter',0x100e090:'exit'})
  def ret(u,v=0):u.reg_write(UC_ARM_REG_R0,v&0xffffffff);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  def string(u,a):
   data=bytearray()
   for i in range(256):
    v=u.mem_read(a+i,1)[0]
    if not v:return data.decode()
    data.append(v)
   raise AssertionError('unterminated')
  def hook(u,a,size,user):
   nonlocal callback_calls
   f=states[id(u)];x=u.reg_read(UC_ARM_REG_R0)
   if a in (0x100ed00,0x100ed10,0x100ed20,0x100ed30,0x100ed40):
    callback_calls+=1;f['trace'].append(('callback',(a-0x100ed00)//16,x,bytes(u.mem_read(CONTROL,20))))
    if f['mutate'] and not f['mutated']:
     f['mutated']=True;head=CONTROL+(8 if x==0 else 16);old=struct.unpack('<I',bytes(u.mem_read(head,4)))[0];u.mem_write(NODES+32,struct.pack('<2I',old,0x100ed41));u.mem_write(head,struct.pack('<I',NODES+32))
    ret(u,0xfefefefe);return
   kind=calls.get(a)
   if not kind:return
   value=0
   if kind=='init':assert x==(0x584d5 if u is stock else syms['r1_sdk_clock_irq_handler']|1);value=f['init_status'];args=()
   elif kind=='sd_enabled':value=f['enabled'];args=()
   elif kind=='mode':i=f['mode_index'];f['mode_index']+=1;value=f['modes'][min(i,len(f['modes'])-1)];args=(value,)
   elif kind=='strerror':args=(x,);value=0x20004000
   elif kind=='log':
    err=struct.unpack('<I',bytes(u.mem_read(u.reg_read(UC_ARM_REG_SP),4)))[0];args=(x,string(u,u.reg_read(UC_ARM_REG_R1)),string(u,u.reg_read(UC_ARM_REG_R2)),string(u,u.reg_read(UC_ARM_REG_R3)),string(u,err))
   elif kind=='enter':u.mem_write(x,b'\x01');args=()
   elif kind=='exit':args=(x,)
   else:args=()
   f['trace'].append((kind,args,bytes(u.mem_read(CONTROL,20))));ret(u,value)
  def mmio(u,access,a,size,value,user):
   if 0xe000e000<=a<0xe000f000 or 0x40000000<=a<0x40001000:states[id(u)]['trace'].append(('mmio',a,size,value))
  for u in (stock,candidate):u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_WRITE,mmio)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  def run(u,name,args,flags=(1,0,0),counts=(0,0),heads=(0,0),chain=(),enabled=0,wdt=0,status=0,modes=(0,),mutate=False,nesting=0):
   u.mem_write(0x40000000,bytes(4096));u.mem_write(0x20007938,struct.pack('<I4B',0x100ed01,int(bool(status)),1,255,0xc9))
   states[id(u)]=dict(trace=[],enabled=enabled,init_status=status,modes=modes,mode_index=0,mutate=mutate,mutated=False);payload=struct.pack('<3Bx4I',*flags,counts[0],heads[0],counts[1],heads[1]);u.mem_write(CONTROL-4,b'\xa7'*4+payload+b'\xb8'*4);u.mem_write(NODES,bytes([0xc9])*80);u.mem_write(0x20004000,b'ERROR_DESCRIPTION\0');u.mem_write(0x40010400,struct.pack('<I',wdt));u.mem_write(0xe000e000,bytes(4096));u.mem_write(0x2002c2fc,struct.pack('<3I',0x12345678,0xabcdef01,nesting));u.reg_write(UC_ARM_REG_PRIMASK,0)
   for i,next_index in enumerate(chain):u.mem_write(NODES+i*8,struct.pack('<2I',NODES+next_index*8 if next_index is not None else 0,0x100ed01+i*16))
   u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
   for reg,v in zip((UC_ARM_REG_R0,UC_ARM_REG_R1),args):u.reg_write(reg,v)
   for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
   u.emu_start((ENTRIES[name][0] if u is stock else syms[name])|1,0x20000100,count=100000)
   assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
   hw_state=bytearray(u.mem_read(0x20007938,8))
   if real_hw and struct.unpack_from('<I',hw_state)[0]==(0x584d5 if u is stock else syms['r1_sdk_clock_irq_handler']|1):struct.pack_into('<I',hw_state,0,0xf0f0f0f1)
   return u.reg_read(UC_ARM_REG_R0) if name=='nrf_drv_clock_init' else None,bytes(u.mem_read(CONTROL-4,28)),bytes(u.mem_read(NODES,80)),states[id(u)]['trace'],(bytes(u.mem_read(0x2002c2fc,12)),bytes(u.mem_read(0xe000e000,4096)),u.reg_read(UC_ARM_REG_PRIMASK)) if real else None,bytes(hw_state) if real_hw else None,bytes(u.mem_read(0x40000000,4096)) if real_hw else None
  def compare(name,args,**kw):
   nonlocal comparisons
   a=run(stock,name,args,**kw);b=run(candidate,name,args,**kw);assert a==b,(name,args,kw,a,b);comparisons+=1
  for flags,enabled,wdt,status,modes in itertools.product(itertools.product((0,1),repeat=3),(0,1),(0,1,0xffffffff),(0,1,133,0xffffffff),((0,),(1,),(2,),(4,),(7,),(0,4,2),(1,0),(4,1))):compare('nrf_drv_clock_init',(0,0),flags=flags,counts=(0x12345678,0xffffffff),heads=(NODES,NODES+8),enabled=enabled,wdt=wdt,status=status,modes=modes)
  for name,ev,chain,mutate in itertools.product(('r1_sdk_clock_notify','r1_sdk_clock_irq_handler','r1_soc_observer_907fc'),range(4),((),(None,),(1,None),(2,None,1),(1,2,3,None)),(False,True)):
   if name=='r1_sdk_clock_notify' and ev>1:continue
   head=NODES if chain else 0;compare(name,(ev,0),heads=(head,head),chain=chain,mutate=mutate)
  for ev,flags,count,enabled,wdt,status in itertools.product(range(4),itertools.product((0,1),repeat=3),(0,1,2,0xffffffff),(0,1),(0,1),(0,133)):compare('r1_sdh_state_observer_890f0',(ev,0),flags=flags,counts=(7,count),enabled=enabled,wdt=wdt,status=status)
  for name,flags,count,ptr,enabled,wdt in itertools.product(('nrf_drv_clock_lfclk_request','nrf_drv_clock_lfclk_release'),itertools.product((0,1),repeat=3),(0,1,2,0xffffffff),(0,NODES,NODES+8),(0,1),(0,1)):
   compare(name,(ptr,0),flags=flags,counts=(5,count),heads=(NODES,NODES),chain=(1,None),enabled=enabled,wdt=wdt)
  for chain,ptr in itertools.product(((),(None,),(1,None),(1,2,None)),range(4)):
   head=NODES if chain else 0;compare('r1_sdk_clock_item_enqueue',(CONTROL+8,NODES+ptr*8),heads=(head,0),chain=chain)
  if real:
   for name,ev,nesting in itertools.product(('r1_sdh_state_observer_890f0','nrf_drv_clock_lfclk_request','nrf_drv_clock_lfclk_release'),range(4),(0,1)):compare(name,(ev if name.startswith('r1_') else 0,0),counts=(0,2),nesting=nesting)
 receipt.write_text(json.dumps(dict(application_sha256=sha(app),report_sha256=sha(rp),native_evidence_sha256=sha(ep),comparisons=comparisons,callback_calls_per_implementation=callback_calls//2,source_owned_cold_zero_bytes=20,critical_report_sha256=sha(cr) if real else None,real_critical=real,real_nrfx_hardware=real_hw,nrfx_hardware_report_sha256=sha(hr) if real_hw else None,hardware_context_pointer_bytes_normalized=4 if real_hw else 0,scope='Clock SOC/SDH observers, notification/IRQ/enqueue helpers, init and LF request/release; canonical flags/enum states, wraparound counters, callback list mutation and dynamic native logging modes',limitations=[('nrfx hardware and critical instructions execute against emulated MMIO; SDH-enabled replies, structured logging outputs and callback replies remain fixtures.' if real_hw else 'nrfx hardware calls, SDH-enabled replies, structured logging outputs and callback replies are fixtures. Actual WDT register reads execute against emulated MMIO.'),'Notify native span34 differs from manual ledger32; ledger is retained and that inventory row is not promoted.','Invalid/cyclic lists, noncanonical bool/enum inputs, physical IRQ timing, full startup/linking and byte identity remain unproven.'],instruction_identity_proven=False),indent=2)+'\n');print(comparisons,'clock comparisons;',callback_calls//2,'callback invocations')
if __name__=='__main__':main()
