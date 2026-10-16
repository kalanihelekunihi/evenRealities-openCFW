#!/usr/bin/env python3
"""Real SDK logger initialization and bounded backend-list registration contracts."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
from verify_sdk_logger_frontend import FIELDS,SECTIONS,DATA,SIZE,HEAD
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
INIT_FIELDS={'r1_sdk_logger_push_ringbuf_buf':(0x2002d574,128),'r1_sdk_logger_push_ringbuf_cb':(0x2002d5f4,24)}
INIT_SECTIONS={'.rodata.r1_sdk_logger_push_ringbuf':0x9c9e8}
def main():
 out=BASE/'sdk-logger-frontend';rp=out/'report.json';r=json.loads(rp.read_text());receipt=out/'initialization-verification.json';receipt.unlink(missing_ok=True);app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';objects=[];reports={}
 for name,file,key in [('sdk-logger-frontend','logger.o','selected_object_sha256'),('sdk-memobj','memobj.o','selected_object_sha256'),('sdk-critical','critical-only.o','selected_object_sha256'),('sdk-power-management','nrf_atomic-selected.o',None),('runtime','memory-runtime.o','relocatable_sha256')]:
  p=BASE/name/'report.json';q=json.loads(p.read_text());o=p.parent/file;assert sha(o)==(q[key] if key else next(x['object_sha256'] for x in q['units'] if x['source'].endswith('/nrf_atomic.c')));objects.append(o);reports[name+'/report.json']=sha(p)
 fields={**FIELDS,**INIT_FIELDS};sections={'.nrf_balloc':SECTIONS['.nrf_balloc'],**INIT_SECTIONS};comparisons=0
 with tempfile.TemporaryDirectory() as directory:
  t=Path(directory);ld=t/'layout.ld';elf=t/'test.elf';binary=t/'text.bin';ld.write_text('SECTIONS { '+''.join('.bss.'+n+' '+hex(a)+' (NOLOAD) : { *(.bss.'+n+') } ' for n,(a,z) in fields.items())+''.join(n+' '+hex(a)+' : { *('+n+') } ' for n,a in sections.items())+'.bss.nrf_nvic_state 0x2002c2fc (NOLOAD) : { *(.bss.nrf_nvic_state) } .text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } /DISCARD/ : { *(.comment) *(.note*) } }')
  # Unused unfiltered module-count calculation: fixtures do not claim production metadata.
  subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--gc-sections','--undefined=nrf_log_init','--undefined=nrf_log_backend_add','--undefined=nrf_ringbuf_init','--defsym=__start_log_const_data=0','--defsym=__stop_log_const_data=0',*map(str,objects),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True);syms={x.split()[-1]:int(x.split()[0],16) for x in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x.split())==3}
  stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
  for u in (stock,candidate):u.mem_map(0x20000,0xc0000);u.mem_map(0x1000000,0x10000);u.mem_map(0x20000000,0x40000);u.mem_map(0xe000e000,4096)
  stock.mem_write(0x27000,app.read_bytes());candidate.mem_write(0x1000000,binary.read_bytes());stock.reg_write(UC_ARM_REG_SP,0x2003f000);stock.emu_start(0x283a1,0x27208,count=2000000);assert stock.reg_read(UC_ARM_REG_PC)==0x27208
  for n,(a,z) in fields.items():assert syms[n]==a and bytes(stock.mem_read(a,z))==bytes(candidate.mem_read(a,z))==bytes(z)
  for n,a in sections.items():
   p=t/(str(a)+'.bin');subprocess.run(['arm-none-eabi-objcopy','--dump-section',n+'='+str(p),str(elf)],check=True);payload=p.read_bytes();assert payload==bytes(stock.mem_read(a,len(payload))),(n,payload);candidate.mem_write(a,payload)
  entries={'nrf_log_init':0x79af4,'nrf_log_backend_add':0x79520,'nrf_ringbuf_init':0x79dcc};saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  def compare(name,args):
   nonlocal comparisons
   results=[]
   for u in (stock,candidate):
    u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
    for reg,v in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),args):u.reg_write(reg,v)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    u.emu_start((entries[name] if u is stock else syms[name])|1,0x20000100,count=300000);assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)],name
    results.append((None if name=='nrf_ringbuf_init' else u.reg_read(UC_ARM_REG_R0),tuple(bytes(u.mem_read(a,z)) for a,z in fields.values()),bytes(u.mem_read(0x20002000,2048))))
   assert results[0]==results[1],(name,args,results);comparisons+=1
  for fill,fn,freq in itertools.product((0,1,0x7f,0xff),(0,0x20000101,0xffffffff),(0,1,32768,0xffffffff)):
   for u in (stock,candidate):
    for a,z in fields.values():u.mem_write(a,bytes([fill])*z)
   compare('nrf_log_init',(fn,freq));compare('nrf_log_init',(fn,freq))
  for fill in range(256):
   for u in (stock,candidate):u.mem_write(0x2002d5f4,bytes([fill])*24)
   compare('nrf_ringbuf_init',(0x9c9e8,))
  for ids,severity in itertools.product([[],*[list(range(n)) for n in range(1,11)],list(range(9,-1,-1)),[0,0],[255],[1,3,5],[9,8,7,0]],(0,1,4,255)):
   for u in (stock,candidate):
    u.mem_write(DATA,bytes(SIZE));u.mem_write(0x20002000,bytes([0xa7])*2048);u.mem_write(HEAD,struct.pack('<I',0x20002000 if ids else 0))
    for i,ident in enumerate(ids+[255]):
     ptr=0x20002000+i*32;cb=0x20002400+i*16;u.mem_write(ptr,struct.pack('<4I',0,0,0,cb));u.mem_write(cb,struct.pack('<IB',ptr+32 if i+1<len(ids) else 0,ident))
   new=0x20002000+len(ids)*32;compare('nrf_log_backend_add',(new,severity))
  for u in (stock,candidate):u.mem_write(DATA,bytes(SIZE));u.mem_write(0x20002000,bytes(2048))
  for i in range(11):
   p=0x20002000+i*32
   for u in (stock,candidate):u.mem_write(p,struct.pack('<4I',0,0,0,0x20002400+i*16))
   compare('nrf_log_backend_add',(p,3))
 receipt.write_text(json.dumps(dict(application_sha256=sha(app),report_sha256=sha(rp),provider_reports=reports,comparisons=comparisons,push_ring_cold_zero_bytes=152,push_ring_descriptor_bytes=12,configuration={'NRF_LOG_DEFERRED':0,'NRF_LOG_STR_PUSH_BUFFER_SIZE':128,'NRF_LOG_USES_TIMESTAMP':0,'NRF_LOG_FILTERS_ENABLED':0},limitations=['Backend records are valid synthetic fixtures; production registration callers, records, transport and scheduling remain gates.','Unused log_const_data boundary references from the unoptimized unfiltered source are bound to zero for this test; production metadata remains unresolved.','Original compiler/link identity, whole-image startup and byte equality are unproven.'],instruction_identity_proven=False),indent=2)+'\n');print(comparisons,'logger initialization/registration comparisons')
if __name__=='__main__':main()
