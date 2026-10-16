#!/usr/bin/env python3
"""Differential SDH polling/continuation with real section traversal; controlled boundaries."""
import hashlib,itertools,json,struct,subprocess,tempfile,sys
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_INTR,UC_MODE_MCLASS,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 real_irq='--real-irq' in sys.argv;out=BASE/'sdk-sdh';receipt=out/('irq-integration-verification.json' if real_irq else 'verification.json');receipt.unlink(missing_ok=True);rp=out/'report.json';r=json.loads(rp.read_text());obj=out/'sdh.o';assert sha(obj)==r['selected_object_sha256']
 for p,d in r['inputs'].items():assert sha(ROOT/p)==d,p
 iterator=BASE/'sdk-ble-dispatch/nrf_section_iter.o';ir=BASE/'sdk-ble-dispatch/report.json';assert sha(iterator)==next(x['object_sha256'] for x in json.loads(ir.read_text())['units'] if x['source'].endswith('/nrf_section_iter.c'))
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';blob=app.read_bytes();evidence_path=out/'evidence.json';evidence=json.loads(evidence_path.read_text());assert evidence['application_sha256']==sha(app)
 for row in evidence['functions']:
  p=out/('ghidra-'+row['symbol']+'-body.json');assert sha(p)==row['ghidra_sha256'];a=int(row['entry'],16);assert bytes(json.loads(p.read_text())['data'])==blob[a-0x27000:a-0x27000+row['body_bytes']]
 critical_obj=BASE/'sdk-critical/critical-only.o';critical_report=BASE/'sdk-critical/report.json'
 if real_irq:assert sha(critical_obj)==json.loads(critical_report.read_text())['selected_object_sha256']
 states={};comparisons=0;svcs=0
 entries={'nrf_sdh_evts_poll':0x7a4b4,'nrf_sdh_is_enabled':0x7a4d8,'nrf_sdh_request_continue':0x7a4e4,'nrf_sdh_enable_request':0x7a440,'nrf_sdh_disable_request':0x7a3ec}
 if real_irq:entries.update(softdevice_evt_irq_disable=0x90814,softdevices_evt_irq_enable=0x90854)
 record_sections={'.r1.sdh.stack.records':0xc45e8,'.r1.sdh.state.records':0xc45f8}
 sections={'sdh_req_observers_array':0x9ca18,'sdh_req_observers':0x9ca2c,'sdh_state_observers_array':0x9ca50,'sdh_state_observers':0x9ca38,'sdh_stack_observers_array':0x9ca60,'sdh_stack_observers':0x9ca44}
 boundaries={}
 for kind,start,stop in [('req',0xc45c8,0xc45d0),('state',0xc45f8,0xc4610),('stack',0xc45e8,0xc45f8)]:
  for i in (0,1):boundaries['__start_sdh_'+kind+'_observers'+str(i)]=start if i==0 else 0;boundaries['__stop_sdh_'+kind+'_observers'+str(i)]=stop if i==0 else 0
 bindings={**boundaries,'app_error_fault_handler':0x4e521,'r1_adc_error':0x100e001,'app_util_critical_region_enter':0x100e011,'app_util_critical_region_exit':0x100e021,'nrf_nvic_state':0x20001000,'r1_sdk_ble_events_poll':0x7a38d,'r1_sdk_soc_events_poll':0x7a501,'r1_sdh_state_observer_567ac':0x567ad,'r1_sdh_state_observer_890f0':0x890f1}
 if real_irq:
  for n in ('app_util_critical_region_enter','app_util_critical_region_exit','nrf_nvic_state'):bindings.pop(n)
 with tempfile.TemporaryDirectory() as directory:
  t=Path(directory);ld=t/'layout.ld';elf=t/'test.elf';binary=t/'text.bin'
  ld.write_text('SECTIONS { '+''.join(n+' '+hex(a)+' : { *('+n+') } ' for n,a in record_sections.items())+('.bss.nrf_nvic_state 0x2002c2fc (NOLOAD) : { *(.bss.nrf_nvic_state) } ' if real_irq else '')+''.join('.rodata.'+n+' '+hex(a)+' : { *(.rodata.'+n+') } ' for n,a in sections.items())+''.join('.bss.'+n+' '+hex(0x20007a18+i)+' (NOLOAD) : { *(.bss.'+n+') } ' for i,n in enumerate(('m_nrf_sdh_enabled','m_nrf_sdh_suspended','m_nrf_sdh_continue')))+'.text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } /DISCARD/ : { *(.comment) *(.note*) } }')
  subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--entry=nrf_sdh_evts_poll',*['--defsym='+n+'='+hex(a) for n,a in bindings.items()],str(obj),str(iterator),*([str(critical_obj)] if real_irq else []),'-o',str(elf)],check=True,capture_output=True)
  subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True);syms={x.split()[-1]:int(x.split()[0],16) for x in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x.split())==3}
  stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
  for u in (stock,candidate):u.mem_map(0x20000,0xc0000);u.mem_map(0x1000000,0x10000);u.mem_map(0x20000000,0x40000);u.mem_write(0x27000,blob)
  
  for u in (stock,candidate):u.mem_map(0xe000e000,4096)
  candidate.mem_write(0x1000000,binary.read_bytes());stock.reg_write(UC_ARM_REG_SP,0x2003f000);stock.emu_start(0x283a1,0x27208,count=2000000);assert stock.reg_read(UC_ARM_REG_PC)==0x27208 and bytes(stock.mem_read(0x20007a18,3))==bytes(3)
  for n,a in {**{'.rodata.'+n:a for n,a in sections.items()},**record_sections}.items():
   f=t/(n+'.bin');subprocess.run(['arm-none-eabi-objcopy','--dump-section',n+'='+str(f),str(elf)],check=True);data=f.read_bytes();assert data==blob[a-0x27000:a-0x27000+len(data)],n;candidate.mem_write(a,data)
  observers={0x78cd0:'req',0x567ac:'state0',0x890f0:'state1',0x78ce8:'state2',0x7a38c:'ble',0x7a500:'soc'}
  def ret(u,v=0):u.reg_write(UC_ARM_REG_R0,v);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  def hook(u,a,size,user):
   f=states[id(u)];r0=u.reg_read(UC_ARM_REG_R0)
   if a in observers:
    kind=observers[a];f['trace'].append((kind,r0,u.reg_read(UC_ARM_REG_R1) if kind.startswith('state') or kind=='req' else None,bytes(u.mem_read(0x20007a18,3))));ret(u,f['ready'] if kind=='req' else 0)
   elif not real_irq and a in (0x4ebec,0x100e010):f['trace'].append(('enter',));u.mem_write(r0,b'\x01');ret(u)
   elif not real_irq and a in (0x4ec34,0x100e020):f['trace'].append(('exit',r0));ret(u)
   elif not real_irq and a in (0x90814,syms['softdevice_evt_irq_disable']):f['trace'].append(('irq_disable',));ret(u)
   elif not real_irq and a in (0x90854,syms['softdevices_evt_irq_enable']):f['trace'].append(('irq_enable',));ret(u)
   elif a in (0x100e000,0x4e5bc):
    assert real_irq,('unexpected_error',r0);f['trace'].append(('error',r0));ret(u)
  def svc(u,number,user):
   nonlocal svcs
   pc=u.reg_read(UC_ARM_REG_PC);op=u.mem_read(pc-2,2)[0];f=states[id(u)];assert op in (16,17),op;svcs+=1
   f['trace'].append(('svc',op,bytes(u.mem_read(u.reg_read(UC_ARM_REG_R0),4)) if op==16 else None,u.reg_read(UC_ARM_REG_R1) if op==16 else None,bytes(u.mem_read(0x20007a18,3))));u.reg_write(UC_ARM_REG_R0,f['status'])
  def mmio(u,access,a,size,value,user):
   if real_irq and 0xe000e000<=a<0xe000f000:states[id(u)]['trace'].append(('mmio',a,size,value))
  for u in (stock,candidate):u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_INTR,svc);u.hook_add(UC_HOOK_MEM_WRITE,mmio)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  def run(u,name,flags,ready,status,mask,priority=2,nesting=0,primask=0):
   states[id(u)]=dict(trace=[],ready=ready,status=status);u.mem_write(0x2002c2fc,struct.pack('<3I',0x193a527d,0x9856abcd,nesting));u.mem_write(0xe000e000,bytes(4096));u.mem_write(0xe000e414,bytes([0,0,priority<<5,0]));u.reg_write(UC_ARM_REG_PRIMASK,primask);u.mem_write(0x20007a17,b'\xa7'+bytes(flags)+b'\xb8')
   for j,(kind,a) in enumerate((('req',0x9ca18),('state',0x9ca50),('stack',0x9ca60))):
    first=boundaries['__start_sdh_'+kind+'_observers0'];last=boundaries['__stop_sdh_'+kind+'_observers0'];u.mem_write(a,struct.pack('<2I',first,first if mask&(1<<j) else last))
   u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101);u.reg_write(UC_ARM_REG_R0,0xabcdef01)
   for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
   u.emu_start((entries[name] if u is stock else syms[name])|1,0x20000100,count=100000)
   assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
   return (None if name=='nrf_sdh_evts_poll' or name.startswith('softdevice') else u.reg_read(UC_ARM_REG_R0)),bytes(u.mem_read(0x20007a17,5)),states[id(u)]['trace'],(bytes(u.mem_read(0x2002c2fc,12)),bytes(u.mem_read(0xe000e000,4096)),u.reg_read(UC_ARM_REG_PRIMASK)) if real_irq else None
  for name,flags,ready,status,mask in itertools.product(entries,itertools.product((0,1),repeat=3),(0,1),(0,1,8,17,0xffffffff),range(8)):
   a=run(stock,name,flags,ready,status,mask);b=run(candidate,name,flags,ready,status,mask);assert a==b,(name,flags,ready,status,mask,a,b);comparisons+=1
  if real_irq:
   for name,priority,nesting,primask in itertools.product(entries,range(8),(0,1),(0,1)):
    args=(name,(1,1,1),1,0,0,priority,nesting,primask);a=run(stock,*args);b=run(candidate,*args);assert a==b,(args,a,b);comparisons+=1
 receipt.write_text(json.dumps(dict(application_sha256=sha(app),report_sha256=sha(rp),native_evidence_sha256=sha(evidence_path),iterator_report_sha256=sha(ir),comparisons=comparisons,svc_calls_per_implementation=svcs//2,section_table_bytes_compared=84,typed_observer_record_bytes_pointer_normalized=32,source_state_cold_zero_bytes_compared=3,critical_report_sha256=sha(critical_report) if real_irq else None,real_irq_and_critical=real_irq,scope='Five public SDH APIs with actual legacy section iterator and native-matching range sets; canonical three bool bytes, empty ranges, observer allow/block and SVC success/errors',limitations=[('Observer handler bodies and SVC replies are fixtures; actual SDK critical/NVIC instructions execute with emulated MMIO.' if real_irq else 'Observer handler bodies, critical boundaries, IRQ enable/disable and SVC replies are fixtures.'),'Typed stack/state observer records are source-owned; unresolved callback bodies and final production allocation remain gates.','No real asynchronous scheduling, flash persistence, original instructions or full-image linkage proof.'],instruction_identity_proven=False),indent=2)+'\n');print(comparisons,'SDH comparisons;',svcs//2,'SVC calls per implementation')
if __name__=='__main__':main()
