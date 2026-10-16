#!/usr/bin/env python3
"""Execute unchanged SDK SOC polling/iterator against locked native code."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_INTR
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
BOUNDARIES={'__start_sdh_soc_observers0':0xc45d0,'__stop_sdh_soc_observers0':0xc45e0,'__start_sdh_soc_observers1':0xc45e0,'__stop_sdh_soc_observers1':0xc45e8}
SECTIONS={'.rodata.sdh_soc_observers_array':0x9caa0,'.rodata.sdh_soc_observers':0x9cab0,'.r1.soc.observer0':0xc45d0,'.sdh_soc_observers1':0xc45e0}
def main():
 out=BASE/'sdk-soc';rp=out/'report.json';r=json.loads(rp.read_text());obj=out/'soc.o';receipt=out/'verification.json';receipt.unlink(missing_ok=True);assert sha(obj)==r['selected_object_sha256']
 for p,d in r['inputs'].items():assert sha(ROOT/p)==d,p
 ir=BASE/'sdk-ble-dispatch/report.json';iterator=BASE/'sdk-ble-dispatch/nrf_section_iter.o';assert sha(iterator)==next(x['object_sha256'] for x in json.loads(ir.read_text())['units'] if x['source'].endswith('/nrf_section_iter.c'))
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';blob=app.read_bytes();ep=out/'evidence.json';e=json.loads(ep.read_text());assert e['application_sha256']==sha(app)
 for row in e['rows']:p=out/row['file'];assert sha(p)==row['sha256'];a=int(row['address'],16);assert bytes(json.loads(p.read_text())['data'])==blob[a-0x27000:a-0x27000+row['bytes']]
 comparisons=0;svcs=0;callbacks=0;states={}
 with tempfile.TemporaryDirectory() as directory:
  t=Path(directory);ld=t/'layout.ld';elf=t/'test.elf';binary=t/'text.bin';ld.write_text('SECTIONS { '+''.join(n+' '+hex(a)+' : { *('+n+') } ' for n,a in SECTIONS.items())+'.text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } /DISCARD/ : { *(.comment) *(.note*) } }')
  bindings={**BOUNDARIES,'r1_adc_error':0x4e5bd,'r1_soc_observer_907fc':0x907fd,'ble_dfu_buttonless_on_sys_evt':0x52279}
  subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--entry=r1_sdk_soc_events_poll',*['--defsym='+n+'='+hex(a) for n,a in bindings.items()],str(obj),str(iterator),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True);syms={x.split()[-1]:int(x.split()[0],16) for x in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x.split())==3}
  stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
  for u in (stock,candidate):u.mem_map(0x20000,0xc0000);u.mem_map(0x1000000,0x10000);u.mem_map(0x20000000,0x40000);u.mem_write(0x27000,blob)
  candidate.mem_write(0x1000000,binary.read_bytes())
  for n,a in SECTIONS.items():
   p=t/(str(a)+'.bin');subprocess.run(['arm-none-eabi-objcopy','--dump-section',n+'='+str(p),str(elf)],check=True);data=p.read_bytes();assert data==blob[a-0x27000:a-0x27000+len(data)];candidate.mem_write(a,data)
  handlers={0x907fc:0,0x78d08:1,0x52278:2}
  def ret(u):u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  def hook(u,a,size,user):
   nonlocal callbacks
   f=states[id(u)]
   if a==0x4e5bc:f['trace'].append(('error',u.reg_read(UC_ARM_REG_R0)));ret(u)
   elif a in handlers:
    callbacks+=1;i=handlers[a];f['trace'].append(('callback',i,u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1)))
    if f['mutate'] and i==0:u.mem_write(0x9caa4,struct.pack('<I',0xc45d8))
    ret(u)
  def svc(u,number,user):
   nonlocal svcs
   f=states[id(u)];pc=u.reg_read(UC_ARM_REG_PC);assert bytes(u.mem_read(pc-2,2))==b'\x4b\xdf';svcs+=1;i=f['index'];f['index']+=1;items=f['items'];status,event=items[i] if i<len(items) else (5,0);ptr=u.reg_read(UC_ARM_REG_R0);assert ptr%4==0
   if status==0:u.mem_write(ptr,struct.pack('<I',event))
   f['trace'].append(('svc75',status,event if status==0 else None));u.reg_write(UC_ARM_REG_R0,status)
  for u in (stock,candidate):u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_INTR,svc)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  def run(u,items,mask,mutate):
   states[id(u)]=dict(trace=[],items=items,index=0,mutate=mutate);u.mem_write(0x20002000,bytes([0x9a])*1024)
   for i,(first,last) in enumerate(((0xc45d0,0xc45e0),(0xc45e0,0xc45e8))):u.mem_write(0x9caa0+i*8,struct.pack('<2I',first,first if mask&(1<<i) else last))
   u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101);u.reg_write(UC_ARM_REG_R0,0xabcdef01)
   for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
   u.emu_start((0x7a500 if u is stock else syms['r1_sdk_soc_events_poll'])|1,0x20000100,count=500000)
   assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
   return states[id(u)]['trace'],bytes(u.mem_read(0x9caa0,16)),bytes(u.mem_read(0x20002000,1024))
  sequences=[[]]+[[(s,0)] for s in (1,2,3,4,5,8,17,0xffffffff)]
  for n in range(1,33):sequences.append([(0,(i*0x1234567+n)&0xffffffff) for i in range(n)])
  for v in [*range(256),0xffff,0x10000,0x7fffffff,0x80000000,0xffffffff]:sequences.append([(0,v)])
  for end in (1,3,5,17,0xffffffff):sequences.append([(0,2),(0,3),(end,0),(0,0xdeadbeef)])
  for items,mask,mutate in itertools.product(sequences,range(4),(False,True)):
   a=run(stock,items,mask,mutate);b=run(candidate,items,mask,mutate);assert a==b,(items,mask,mutate,a,b);comparisons+=1
 receipt.write_text(json.dumps(dict(application_sha256=sha(app),report_sha256=sha(rp),native_evidence_sha256=sha(ep),iterator_report_sha256=sha(ir),comparisons=comparisons,svc_calls_per_implementation=svcs//2,callback_calls_per_implementation=callbacks//2,range_set_bytes_compared=28,typed_observer_bytes_compared=16,scope='Actual pinned SOC poll, legacy iterator, two-priority ranges, full-width events, empty/early-mutated ranges, draining and error termination',limitations=['Observer bodies and SVC75 replies are fixtures; selected code contains no ROM function bindings.','Storage event completion, physical interrupts, persistence, original instruction identity and whole-image linkage are not proven by this receipt.'],instruction_identity_proven=False),indent=2)+'\n');print(comparisons,'SOC comparisons;',svcs//2,'SVC calls')
if __name__=='__main__':main()
