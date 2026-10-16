#!/usr/bin/env python3
"""RTT backend records, retry behavior and real frontend registration."""
import hashlib,itertools,json,struct,subprocess,tempfile,sys
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
FIELDS={'m_host_present':(0x200079b8,1),'m_string_buff':(0x2002c4b4,4096),'r1_sdk_logger_data':(0x2002d60c,4128)}
SECTIONS={'.data.log_backend_cb_rtt_log_backend':0x200079bc,'.log_backends':0xc440c,'.rodata.nrf_log_backend_rtt_api':0x9c9c8,'.r1.rtt.backend_name':0xc4168}
ENTRIES={'nrf_log_default_backends_init':0x7968c,'nrf_log_backend_rtt_init':0x79576,'nrf_log_backend_rtt_put':0x7957c,'nrf_log_backend_rtt_flush':0x79574,'nrf_log_backend_rtt_panic_set':0x7957a,'serial_tx':0x8a5fc}
def main():
 real_delay='--real-delay' in sys.argv
 real_segger='--real-segger' in sys.argv
 out=BASE/'sdk-rtt-backend';rp=out/'report.json';r=json.loads(rp.read_text());obj=out/'rtt-backend.o';assert sha(obj)==r['selected_object_sha256'];receipt=out/('delay-integration-verification.json' if real_delay else 'segger-integration-verification.json' if real_segger else 'verification.json');receipt.unlink(missing_ok=True)
 for p,d in r['inputs'].items():assert sha(ROOT/p)==d,p
 fp=BASE/'sdk-logger-frontend/report.json';frontend=fp.parent/'logger.o';assert sha(frontend)==json.loads(fp.read_text())['selected_object_sha256'];app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';states={};comparisons=0
 with tempfile.TemporaryDirectory() as directory:
  extra=[];segger_sections=''
  if real_delay:
   p=BASE/'native-rtt-delay/report.json';o=p.parent/'rtt-delay.o';assert sha(o)==json.loads(p.read_text())['selected_object_sha256'];extra.append(str(o))
  if real_segger:
   from verify_sdk_segger_rtt import SECTIONS as SG_SECTIONS
   segger_sections=''.join(n+' '+hex(a)+(' (NOLOAD)' if n not in ('.r1.rtt.terminal','.r1.rtt.identifier') else '')+' : { *('+n+') } ' for n,a in SG_SECTIONS.items())
   for name,file,key in [('sdk-segger-rtt','segger-rtt.o','selected_object_sha256'),('runtime','memory-runtime.o','relocatable_sha256')]:
    path=BASE/name/file;assert sha(path)==json.loads((BASE/name/'report.json').read_text())[key];extra.append(str(path))
  t=Path(directory);ld=t/'layout.ld';elf=t/'test.elf';binary=t/'text.bin';ld.write_text('SECTIONS { '+segger_sections+''.join('.bss.'+n+' '+hex(a)+' (NOLOAD) : { *(.bss.'+n+') } ' for n,(a,z) in FIELDS.items())+''.join(n+' '+hex(a)+' : { *('+n+') } ' for n,a in SECTIONS.items())+'.text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } /DISCARD/ : { *(.comment) *(.note*) } }');bindings={n:0x100ee01+i*16 for i,n in enumerate(('SEGGER_RTT_Init','SEGGER_RTT_WriteNoLock','nrf_log_backend_serial_put','r1_rtt_delay_cycles'))};subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--gc-sections','--entry=nrf_log_default_backends_init',*['--undefined='+n for n in ('nrf_log_backend_rtt_init','nrf_log_backend_rtt_api')],*['--defsym='+n+'='+hex(a) for n,a in bindings.items() if (not real_segger or n not in ('SEGGER_RTT_Init','SEGGER_RTT_WriteNoLock')) and (not real_delay or n!='r1_rtt_delay_cycles')],str(obj),str(frontend),*extra,'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True);syms={x.split()[-1]:int(x.split()[0],16) for x in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x.split())==3}
  stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
  for u in (stock,candidate):u.mem_map(0x20000,0xc0000);u.mem_map(0x1000000,0x10000);u.mem_map(0x20000000,0x40000)
  stock.mem_write(0x27000,app.read_bytes());candidate.mem_write(0x1000000,binary.read_bytes());stock.reg_write(UC_ARM_REG_SP,0x2003f000);stock.emu_start(0x283a1,0x27208,count=2000000);assert stock.reg_read(UC_ARM_REG_PC)==0x27208
  for n,(a,z) in FIELDS.items():assert syms[n]==a and bytes(stock.mem_read(a,z))==bytes(candidate.mem_read(a,z))==bytes(z)
  for n,a in SECTIONS.items():
   p=t/(str(a)+'.bin');subprocess.run(['arm-none-eabi-objcopy','--dump-section',n+'='+str(p),str(elf)],check=True);payload=p.read_bytes();native=bytes(stock.mem_read(a,len(payload)))
   if n=='.rodata.nrf_log_backend_rtt_api':
    assert len(payload)==12
    for i,name in enumerate(('nrf_log_backend_rtt_put','nrf_log_backend_rtt_panic_set','nrf_log_backend_rtt_flush')):assert struct.unpack_from('<I',payload,i*4)[0]==syms[name]|1 and struct.unpack_from('<I',native,i*4)[0]==ENTRIES[name]|1
   else:assert payload==native,(n,payload,native)
   candidate.mem_write(a,payload)
  hooks={0x31948:'init',0x31a18:'write',0x79598:'serial',0x9c9e0:'delay',**{bindings[n]&~1:k for n,k in [('SEGGER_RTT_Init','init'),('SEGGER_RTT_WriteNoLock','write'),('nrf_log_backend_serial_put','serial'),('r1_rtt_delay_cycles','delay')]}}
  def hook(u,a,size,user):
   kind=hooks.get(a)
   if not kind:return
   f=states[id(u)];args=[u.reg_read(reg) for reg in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)]
   if kind=='write':
    i=f['i'];f['i']+=1;done=min(args[2],f['writes'][min(i,len(f['writes'])-1)]);f['trace'].append(('write',args[0],bytes(u.mem_read(args[1],args[2])),done));u.reg_write(UC_ARM_REG_R0,done)
   elif kind=='serial':
    fn=struct.unpack('<I',bytes(u.mem_read(u.reg_read(UC_ARM_REG_SP),4)))[0];assert fn==(ENTRIES['serial_tx']|1 if u is stock else syms['serial_tx']|1);f['trace'].append(('serial',*args))
   elif kind=='delay':f['trace'].append(('delay',args[0]))
   else:f['trace'].append(('init',))
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  for u in (stock,candidate):u.hook_add(UC_HOOK_CODE,hook)
  if real_delay:hooks={a:k for a,k in hooks.items() if k!='delay'}
  if real_segger:
   hooks={a:k for a,k in hooks.items() if k not in ('init','write')}
   candidate.mem_write(0x36dbc,b'Terminal\0');candidate.mem_write(0x9ca04,b'\0'*6+b'TTR REGGES')
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  def compare(name,args,host=0,writes=(0,),ids=(),enabled=0):
   nonlocal comparisons
   results=[]
   for u in (stock,candidate):
    states[id(u)]={'i':0,'writes':writes,'trace':[]};u.mem_write(0x200079b8,bytes([host]));u.mem_write(0x200079bc,struct.pack('<IBBH',0,255,enabled,0));u.mem_write(0x2002d60c,bytes(4128));u.mem_write(0x20002000,bytes(range(256))*8);u.mem_write(0x2002e61c,struct.pack('<I',0x20003000 if ids else 0));u.mem_write(0x20003000,bytes(1024))
    for i,ident in enumerate(ids):u.mem_write(0x20003000+i*32,struct.pack('<4I',0,0,0,0x20003200+i*16));u.mem_write(0x20003200+i*16,struct.pack('<IB',0x20003000+(i+1)*32 if i+1<len(ids) else 0,ident))
    if real_segger:
     u.mem_write(0x2002e62c,bytes(696));u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101);u.emu_start((0x36d68 if u is stock else syms['SEGGER_RTT_Init'])|1,0x20000100,count=300000);assert u.reg_read(UC_ARM_REG_PC)==0x20000100
     u.mem_write(0x2002e62c+24+16,struct.pack('<I',(min(writes[0],511)+1)%512))
    u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
    for reg,v in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),args):u.reg_write(reg,v)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    u.emu_start((ENTRIES[name] if u is stock else syms[name])|1,0x20000100,count=300000);assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)],name
    results.append((states[id(u)]['trace'],bytes(u.mem_read(0x200079b8,12)),bytes(u.mem_read(0x2002d60c,4128)),bytes(u.mem_read(0x20003000,1024)),bytes(u.mem_read(0x2002e62c,696)) if real_segger else None))
   assert results[0]==results[1],(name,args,host,writes,results);comparisons+=1
  for host,length,writes in itertools.product((0,1),(0,1,2,7,16,127),((0,),(1,),(4,),(1000,),(0,1),(1,0),(0,0,1),(1,0,0,0,1000))):compare('serial_tx',(0,0x20002000,length),host,writes)
  for ids,enabled in itertools.product([[],*[list(range(n)) for n in range(1,11)],[1,3,9],[255]],(0,1,255)):compare('nrf_log_default_backends_init',(),ids=ids,enabled=enabled)
  for n in ('nrf_log_backend_rtt_init','nrf_log_backend_rtt_flush','nrf_log_backend_rtt_panic_set'):compare(n,(0xc440c,))
  for msg in (0,0x20001000,0xffffffff):compare('nrf_log_backend_rtt_put',(0xc440c,msg))
 receipt.write_text(json.dumps(dict(application_sha256=sha(app),report_sha256=sha(rp),frontend_report_sha256=sha(fp),comparisons=comparisons,actual_delay=real_delay,delay_report_sha256=sha(BASE/'native-rtt-delay/report.json') if real_delay else None,actual_segger=real_segger,segger_report_sha256=sha(BASE/'sdk-segger-rtt/report.json') if real_segger else None,memory_report_sha256=sha(BASE/'runtime/report.json') if real_segger else None,initial_zero_bytes=4097,backend_control_initial_bytes=8,backend_record_bytes=16,backend_name_bytes=16,api_bytes_pointer_normalized=12,scope='Unchanged SDK RTT/default initialization and actual frontend backend-add; typed record/API, staging, retry/host state and wrapper callback contract',limitations=['Serial formatter is a fixture; delay executes only in actual_delay mode. SEGGER init/write execute only in actual_segger mode, using fixed initial ring availability instead of scripted host consumption; physical debugger transport and elapsed delay are unproven.','Private backend callbacks lack ownership rows; serial_tx has a product-specific ownership attribution held pending correction. Neither inflates tested ledger counts.','Whole-image linking/startup, original compiler/link identity and byte equality remain unresolved.'],instruction_identity_proven=False),indent=2)+'\n');print(comparisons,'RTT backend comparisons')
if __name__=='__main__':main()
