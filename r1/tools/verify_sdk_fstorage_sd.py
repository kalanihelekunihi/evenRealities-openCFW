#!/usr/bin/env python3
"""Complete pinned SoftDevice fstorage state machine with controlled FIFO/SVC boundaries."""
import hashlib,itertools,json,struct,subprocess,tempfile,sys
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_INTR
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();P='r1_sdk_fstorage_sd_'
FIELDS={P+'fifo_inst':(0x2002c3f8,16),P+'fifo_data':(0x2002c408,140),P+'flags':(0x2002c494,20),P+'p_cur_op':(0x200079a8,4),P+'iget_ctx':(0x200079ac,4)}
API={'init':0x710a0,'uninit':0x93ec4,'read':0x87b20,'write':0x96fe0,'erase':0x5d514,'rmap':0x883f8,'wmap':0x96e08,'is_busy':0x72b70}
EXTRA={'event_send':0x5e644,'queue_process':0x87520,'queue_start':0x875dc,'queue_free':0x87468,'nrf_fstorage_sys_evt_handler':0x78d08,'nrf_fstorage_sdh_req_handler':0x78cd0,'nrf_fstorage_sdh_state_handler':0x78ce8}
OBSERVERS={'soc':(0xc45d8,'nrf_fstorage_sys_evt_handler'),'req':(0xc45c8,'nrf_fstorage_sdh_req_handler'),'state':(0xc4608,'nrf_fstorage_sdh_state_handler')}
CALLS={'nrf_atfifo_clear':0x77f30,'nrf_atfifo_init':0x77f40,'nrf_atfifo_item_alloc':0x77f66,'nrf_atfifo_item_free':0x77f7c,'nrf_atfifo_item_get':0x77f92,'nrf_atfifo_item_put':0x77fa8,'nrf_atomic_flag_set_fetch':0x78074,'nrf_sdh_is_enabled':0x7a4d8,'nrf_sdh_request_continue':0x7a4e4}
FLAGS=0x2002c494;CUR=0x200079a8;GET=0x200079ac;FIFO=0x2002c3f8;BUFFER=0x2002c408;NODE=BUFFER;NODE2=BUFFER+28;FS=0x20002000;SRC=0x20003000;DEST=0x20004000

def main():
 facades='--facades' in sys.argv
 out=BASE/'sdk-fstorage-sd';rp=out/'report.json';obj=out/'fstorage-sd.o';r=json.loads(rp.read_text());receipt=out/('facade-integration-verification.json' if facades else 'verification.json');receipt.unlink(missing_ok=True);assert sha(obj)==r['units'][0]['object_sha256']
 for p,d in r['inputs'].items():assert sha(ROOT/p)==d,p
 mr=BASE/'runtime/report.json';memory=BASE/'runtime/memory-runtime.o';assert sha(memory)==json.loads(mr.read_text())['relocatable_sha256']
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';states={};counts={n:0 for n in [*API,*EXTRA]};svcs=0
 facade_path=BASE/'sdk-fstorage/report.json';facade_obj=BASE/'sdk-fstorage/fstorage.o'
 if facades:assert sha(facade_obj)==json.loads(facade_path.read_text())['units'][0]['object_sha256']
 with tempfile.TemporaryDirectory() as directory:
  t=Path(directory);ld=t/'layout.ld';elf=t/'test.elf';binary=t/'text.bin';ld.write_text('SECTIONS { '+''.join('.sdh_'+n+'_observers0 '+hex(a)+' : { *(.sdh_'+n+'_observers0) } ' for n,(a,h) in OBSERVERS.items())+''.join('.bss.'+n+' '+hex(a)+' (NOLOAD) : { *(.bss.'+n+') } ' for n,(a,z) in FIELDS.items())+'.r1.fstorage_sd.fifo_pointer 0x9c85c : { *(.r1.fstorage_sd.fifo_pointer) } .rodata.'+P+'flash_info 0x9c860 : { *(.rodata.'+P+'flash_info) } .rodata.nrf_fstorage_sd 0x9c86c : { *(.rodata.nrf_fstorage_sd) } .text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } /DISCARD/ : { *(.comment) *(.note*) } }')
  defs={n:0x100e001+i*16 for i,n in enumerate(CALLS)}
  if facades:defs.update(__start_fs_data=0x20007dc0,__stop_fs_data=0x20007de8)
  subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--entry=nrf_fstorage_sys_evt_handler',*['--defsym='+n+'='+hex(a) for n,a in defs.items()],str(obj),str(memory),*([str(facade_obj)] if facades else []),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True)
  syms={x.split()[-1]:int(x.split()[0],16) for x in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x.split())==3}
  for n,(a,z) in FIELDS.items():assert syms[n]==a
  stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
  for u in (stock,candidate):u.mem_map(0x20000,0xc0000);u.mem_map(0x1000000,0x10000);u.mem_map(0x20000000,0x40000)
  stock.mem_write(0x27000,app.read_bytes());candidate.mem_write(0x1000000,binary.read_bytes());stock.reg_write(UC_ARM_REG_SP,0x2003f000);stock.emu_start(0x283a1,0x27208,count=2000000);assert stock.reg_read(UC_ARM_REG_PC)==0x27208
  for a,z in FIELDS.values():assert bytes(stock.mem_read(a,z))==bytes(z)
  for sec,a in (('.rodata.'+P+'flash_info',0x9c860),('.rodata.nrf_fstorage_sd',0x9c86c)):
   p=t/(str(a)+'.bin');subprocess.run(['arm-none-eabi-objcopy','--dump-section',sec+'='+str(p),str(elf)],check=True);b=p.read_bytes();candidate.mem_write(a,b)
   if a==0x9c860:assert b==bytes(stock.mem_read(a,len(b))) and len(b)==12
   else:assert struct.unpack('<8I',b)==tuple(syms[P+n]|1 for n in API) and struct.unpack('<8I',bytes(stock.mem_read(a,32)))==tuple(a|1 for a in API.values())
  fifo_pointer=t/'fifo-pointer.bin';subprocess.run(['arm-none-eabi-objcopy','--dump-section','.r1.fstorage_sd.fifo_pointer='+str(fifo_pointer),str(elf)],check=True);assert fifo_pointer.read_bytes()==bytes(stock.mem_read(0x9c85c,4))==struct.pack('<I',FIFO)
  for name,(a,handler) in OBSERVERS.items():
   p=t/(name+'.bin');subprocess.run(['arm-none-eabi-objcopy','--dump-section','.sdh_'+name+'_observers0='+str(p),str(elf)],check=True);b=p.read_bytes();assert len(b)==8 and struct.unpack('<II',b)==(syms[handler]|1,0) and struct.unpack('<II',bytes(stock.mem_read(a,8)))==(EXTRA[handler]|1,0)
  call_names={a:n for n,a in CALLS.items()};call_names.update({defs[n]&~1:n for n in CALLS})
  def ret(u,v):u.reg_write(UC_ARM_REG_R0,v&0xffffffff);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  def hook(u,address,size,user):
   f=states[id(u)]
   if address==0x100ef00:
    ptr=u.reg_read(UC_ARM_REG_R0);f['trace'].append(('event',bytes(u.mem_read(ptr,24)),bytes(u.mem_read(FLAGS,20))));ret(u,0xffffffff);return
   if address not in call_names:return
   name=call_names[address];a=[u.reg_read(reg) for reg in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)];snapshot=bytes(u.mem_read(FLAGS,20));value=0
   if name=='nrf_atomic_flag_set_fetch':
    value=struct.unpack('<I',bytes(u.mem_read(a[0],4)))[0];u.mem_write(a[0],struct.pack('<I',1));args=(a[0],value)
   elif name=='nrf_sdh_is_enabled':value=f['enabled'];args=()
   elif name=='nrf_sdh_request_continue':value=f['callback_result'];args=()
   elif name=='nrf_atfifo_init':
    args=tuple(a);assert a==( [FIFO,BUFFER,140,28] );u.mem_write(FIFO,struct.pack('<IIIHH',BUFFER,0,0,140,28));value=f['callback_result']
   elif name=='nrf_atfifo_item_alloc':
    assert a[0]==FIFO;u.mem_write(a[1],struct.pack('<I',0x12345678));value=NODE if f['allocate'] else 0;args=(a[0],value)
   elif name=='nrf_atfifo_item_put':args=(a[0],struct.unpack('<I',bytes(u.mem_read(a[1],4)))[0]);value=f['put_result']
   elif name=='nrf_atfifo_item_get':
    assert a[:2]==[FIFO,GET];u.mem_write(GET,struct.pack('<I',0x89abcdef));value=f['queue'][f['get_index']] if f['get_index']<len(f['queue']) else 0;f['get_index']+=1;args=(FIFO,GET,value)
   elif name=='nrf_atfifo_item_free':args=(a[0],a[1],bytes(u.mem_read(a[1],4)));value=f['put_result']
   else:args=(a[0],);value=f['callback_result']
   f['trace'].append((name,args,snapshot));ret(u,value)
  def svc(u,number,user):
   nonlocal svcs
   pc=u.reg_read(UC_ARM_REG_PC);op=bytes(u.mem_read(pc-2,2));assert op[1]==0xdf and op[0] in (40,41),op;f=states[id(u)];args=[u.reg_read(reg) for reg in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2)];f['trace'].append(('svc',op[0],args if op[0]==41 else args[:1],bytes(u.mem_read(FLAGS,20))));index=f['svc_index'];f['svc_index']+=1;svcs+=1;u.reg_write(UC_ARM_REG_R0,f['statuses'][min(index,len(f['statuses'])-1)])
  for u in (stock,candidate):u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_INTR,svc)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  seed=bytes((i*37+19)&255 for i in range(1056))
  def run(u,name,initialized=0,running=0,state=0,retries=0,enabled=1,paused=0,allocate=True,queue=True,opcode=0,length=4,offset=0,progress=0,source=SRC,destination=0xd4000,parameter=0x12345678,statuses=(0,),callback_result=0,put_result=1,event=2,handler=True,follow=(),two=False):
   u.mem_write(FLAGS,struct.pack('<IIB3xIBB2x',initialized,running,state,retries,enabled,paused));u.mem_write(FIFO,bytes(16));u.mem_write(BUFFER,bytes([0xa7])*140);u.mem_write(CUR,struct.pack('<I',NODE));u.mem_write(GET,struct.pack('<I',0x76543210));u.mem_write(FS,struct.pack('<5I',0x9c86c,0x9c860 if facades else 0,0x100ef01 if handler else 0,0xd4000,0xf8000));u.mem_write(SRC-4,b'LEFT'+seed+b'RGHT');u.mem_write(DEST-4,b'LEFT'+bytes([0x39])*1056+b'RGHT')
   def node(p,kind,n):
    tail=(source,destination,n,offset) if kind==0 else (destination>>12,progress,n,0)
    u.mem_write(p,struct.pack('<IB3x5I',FS,kind,parameter,*tail))
   node(NODE,opcode,length);node(NODE2,0,8)
   f=dict(trace=[],enabled=enabled,allocate=allocate,callback_result=callback_result,put_result=put_result,queue=(([NODE2] if two else []) if state else ([NODE,NODE2] if two else [NODE])) if queue else [],get_index=0,svc_index=0,statuses=statuses);states[id(u)]=f
   def invoke(which,evt):
    if which=='init' and facades:args=(FS,0x9c86c,parameter)
    elif which=='init' or which=='uninit':args=(FS,parameter)
    elif which=='read':args=(FS,SRC,DEST,length)
    elif which=='write':args=(FS,destination,source,length)
    elif which=='erase':args=(FS,destination,length,parameter)
    elif which in ('rmap','wmap'):args=(FS,destination)
    elif which=='is_busy':args=(FS,)
    elif which=='event_send':args=(NODE,callback_result)
    elif which.startswith('nrf_fstorage_'):args=(evt,parameter)
    else:args=()
    u.reg_write(UC_ARM_REG_SP,0x2003f000);u.mem_write(0x2003f000,struct.pack('<I',parameter));u.reg_write(UC_ARM_REG_LR,0x20000101)
    for reg,v in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),args):u.reg_write(reg,v)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    entry=API.get(which,EXTRA.get(which));symbol=which if which.startswith('nrf_') else P+which
    if facades and which in ('init','erase','write','is_busy'):entry={'init':0x78c78,'erase':0x78c4c,'write':0x78dac,'is_busy':0x78c80}[which];symbol='nrf_fstorage_'+which
    u.emu_start((entry if u is stock else syms[symbol])|1,0x20000100,count=100000)
    assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)],(which,evt,length,enabled,paused,state,running,opcode,hex(u.reg_read(UC_ARM_REG_PC)))
    return u.reg_read(UC_ARM_REG_R0) if which in API or which=='nrf_fstorage_sdh_req_handler' else None
   values=[invoke(name,event)]
   for evt in follow:values.append(invoke('nrf_fstorage_sys_evt_handler',evt))
   for p in (SRC,DEST):assert bytes(u.mem_read(p-4,4))==b'LEFT' and bytes(u.mem_read(p+1056,4))==b'RGHT'
   return values,bytes(u.mem_read(FLAGS,20)),bytes(u.mem_read(FIFO,16)),bytes(u.mem_read(BUFFER,140)),bytes(u.mem_read(CUR,8)),bytes(u.mem_read(FS,20)),bytes(u.mem_read(DEST,1056)),f['trace']
  def compare(name,**kw):
   a=run(stock,name,**kw);b=run(candidate,name,**kw);assert a==b,(name,kw,a,b);counts[name]+=1
  for initialized,enabled,result in itertools.product((0,1),(0,1),(0,8,0xffffffff)):compare('init',initialized=initialized,enabled=enabled,callback_result=result)
  for state,paused,result in itertools.product((0,1,2),(0,1),(0,8,0xffffffff)):compare('uninit',state=state,paused=paused,callback_result=result)
  for n in range(1025):compare('read',length=n)
  for name in ('rmap','wmap'):
   for value in (0,1,0xd4000,0x80000000,0xffffffff):compare(name,destination=value)
  for state in range(256):compare('is_busy',state=state)
  for name in ('write','erase'):
   for allocate,paused,enabled,rc,n,handler in itertools.product((False,True),(0,1),(0,1),(0,17,3,0xffffffff),(1,4,4096,4097),(False,True)):
    if name=='erase' and allocate and not paused and not enabled and rc==0 and n>4:continue
    compare(name,allocate=allocate,paused=paused,enabled=enabled,statuses=(rc,),length=n,handler=handler)
   for running,put_result in itertools.product((0,1),(0,1)):compare(name,running=running,put_result=put_result)
   compare(name,enabled=1,length=0);compare(name,enabled=1,length=0xffffffff)
  for opcode,result,handler in itertools.product((0,1,2,255),(0,3,13,0xffffffff),(False,True)):compare('event_send',opcode=opcode,callback_result=result,handler=handler)
  for name in ('queue_process','queue_start'):
   for state,running,paused,queue,enabled,opcode,rc in itertools.product((0,1,2),(0,1),(0,1),(False,True),(0,1),(0,1,2),(0,17,3)):
    if state and not queue:continue
    compare(name,state=state,running=running,paused=paused,queue=queue,enabled=enabled,opcode=opcode,statuses=(rc,))
  for result in (0,1):compare('queue_free',put_result=result)
  for event,state,paused,retries,opcode in itertools.product((0,1,2,3,4,0xffffffff),(0,1,2),(0,1),(0,7,8,9,0xffffffff),(0,1,2)):compare('nrf_fstorage_sys_evt_handler',event=event,state=state,paused=paused,retries=retries,opcode=opcode)
  for event,state in itertools.product((0,1,2,3,0xffffffff),range(3)):compare('nrf_fstorage_sdh_req_handler',event=event,state=state)
  for event,state,enabled in itertools.product((0,1,2,3,4,0xffffffff),range(3),(0,1)):compare('nrf_fstorage_sdh_state_handler',event=event,state=state,enabled=enabled)
  compare('write',enabled=1,length=8192,follow=(2,2));compare('write',enabled=1,length=4,follow=(3,)*9);compare('erase',enabled=1,length=2,follow=(2,2));compare('write',enabled=1,statuses=(17,0),follow=(2,2));compare('write',enabled=0,two=True)
 receipt.write_text(json.dumps(dict(application_sha256=sha(app),report_sha256=sha(rp),object_sha256=sha(obj),memory_report_sha256=sha(mr),comparisons=sum(counts.values()),actual_public_facades_executed=facades,facade_report_sha256=sha(facade_path) if facades else None,comparisons_by_entry=counts,svc_calls_per_implementation=svcs//2,cold_zero_bytes_compared=sum(z for a,z in FIELDS.values()),flash_info_bytes_compared=12,fifo_pointer_bytes_compared=4,api_table_bytes_pointer_normalized=32,observer_record_bytes_pointer_normalized=24,scope='Complete pinned API and queue/event state machine with controlled atomic/FIFO/SDH boundaries; SVC40/41, sync/asynchronous completion, busy/error handling, retries, exact event payloads, queue chaining, operation records, copy/read/map, cold state and saved registers',limitations=['FIFO/atomic/SDH callbacks and flash SVC results are controlled, not real concurrency, SoftDevice acceptance or persistent flash proof.','Canonical bool flags and bounded completing queue scenarios only; synchronous zero-page erasure/nonterminating huge queues and reentrant callbacks remain unproven.','Observer record bytes/positions are authenticated; complete dispatcher wiring and original instruction/link identity remain gates. Whole image/hardware are not proven.'],instruction_identity_proven=False),indent=2)+'\n');print(sum(counts.values()),'SoftDevice fstorage comparisons passed;',svcs//2,'SVC calls')
if __name__=='__main__':main()
