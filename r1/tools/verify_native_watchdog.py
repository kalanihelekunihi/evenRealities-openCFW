#!/usr/bin/env python3
"""Exercise native watchdog/list code with real source runtime and task getter."""
import hashlib,json,struct,subprocess,tempfile,itertools
from pathlib import Path
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_MEM_READ_UNMAPPED,UC_HOOK_MEM_FETCH_UNMAPPED
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
REG=0x20015404;LIST=REG+4;POOL=0x20010000;A=POOL;B=POOL+0x200;NEW=POOL+0x400;MUTEX=0x20006738
ENTRIES={'r1_native_watchdog_register':0x5db14,'r1_native_watchdog_arm':0x5dbea,'r1_native_watchdog_disarm':0x5dbbc,'r1_native_watchdog_feed':0x5da00,'r1_native_watchdog_lock':0x97730,'r1_native_watchdog_unlock':0x97748,'r1_native_list_head':0x5d8e6,'r1_native_list_tail':0x5d8f6,'r1_native_list_next':0x5d8ee,'r1_native_list_set_next':0x77e30,'r1_native_list_set_previous':0x77e3c,'r1_native_list_initialize':0x5d8fe,'r1_native_list_empty':0x5d986,'r1_native_list_append':0x5d94a,'r1_native_list_prepend':0x5d90e,'xTaskGetCurrentTaskHandle':0x9879c}
def main():
 receipt=BASE/'native-watchdog/verification.json';receipt.unlink(missing_ok=True);app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';report=BASE/'native-watchdog/report.json';data=json.loads(report.read_text());obj=BASE/'native-watchdog/native_watchdog.o';assert sha(obj)==data['units'][0]['object_sha256']
 for path,digest in data['inputs'].items():assert sha(ROOT/path)==digest,path
 selected=BASE/'native-watchdog/current-task-only.o';assert sha(selected)==data['selected_current_task_sha256'];assert sha(BASE/'rtos-ticks/report.json')==data['upstream_report_sha256']
 runtime=BASE/'runtime/memory-runtime.o';runtime_report=BASE/'runtime/report.json';assert sha(runtime)==json.loads(runtime_report.read_text())['relocatable_sha256']
 with tempfile.TemporaryDirectory() as directory:
  tmp=Path(directory);ld=tmp/'layout.ld';elf=tmp/'test.elf';binary=tmp/'test.bin';ld.write_text('SECTIONS { .text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } .r1.watchdog.enabled 0x20006730 (NOLOAD) : { *(.r1.watchdog.enabled) } .r1.watchdog.mutex 0x20006738 (NOLOAD) : { *(.r1.watchdog.mutex) } .r1.watchdog.registry 0x20015404 (NOLOAD) : { *(.r1.watchdog.registry) } .bss.pxCurrentTCB 0x2000781c (NOLOAD) : { *(.bss.pxCurrentTCB) } /DISCARD/ : { *(.comment) *(.note*) } }');subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--defsym=pvPortMalloc=0x100e001','--defsym=osMutexAcquire=0x100e011','--defsym=osMutexRelease=0x100e021',str(obj),str(selected),str(runtime),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True)
  syms={x.split()[-1]:int(x.split()[0],16) for x in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x.split())==3}
  for name,address in (('r1_native_watchdog_enabled',0x20006730),('r1_native_watchdog_mutex',MUTEX),('r1_native_watchdog_registry',REG),('pxCurrentTCB',0x2000781c)):assert syms[name]==address
  stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB);stock.mem_map(0x20000,0xc0000);stock.mem_write(0x27000,app.read_bytes())
  for uc in (stock,candidate):uc.mem_map(0x1000000,0x10000);uc.mem_map(0x20000000,0x40000)
  candidate.mem_write(0x1000000,binary.read_bytes());stock.reg_write(UC_ARM_REG_SP,0x2003f000);stock.emu_start(0x283a1,0x27208,count=2000000);assert stock.reg_read(UC_ARM_REG_PC)==0x27208
  for address,size in ((0x20006730,1),(MUTEX,4),(REG,16),(0x2000781c,4)):assert bytes(stock.mem_read(address,size))==bytes(candidate.mem_read(address,size))==bytes(size)
  states={};faults={id(stock):[],id(candidate):[]};port0=0x2001e000;port1=0x2001e020;owner1=0x2001e100
  def hook(uc,address,size,user):
   if address not in (0x855a0,0x7d488,0x7d536,0x100e000,0x100e010,0x100e020,0x100e100,0x100e110):return
   f=states[id(uc)];r=[uc.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2)];value=0
   if address in (0x855a0,0x100e000):event=('malloc',r[0]);value=NEW+f['allocations']*0x100 if f['allocate'] else 0;f['allocations']+=bool(value)
   elif address in (0x7d488,0x100e010):
    event=('acquire',r[0],r[1]);value=f['status']&0xffffffff
    if f['mutate']:uc.mem_write(MUTEX,struct.pack('<I',0x2001f040))
   elif address in (0x7d536,0x100e020):event=('release',r[0]);value=f['status']&0xffffffff
   else:
    event=('sample',0 if address==0x100e100 else 1,r[0],r[1],struct.unpack('<I',bytes(uc.mem_read(r[1],4)))[0] if r[1] else None)
    if r[0] and r[1]:uc.mem_write(r[1],struct.pack('<I',0x87654321))
    if f['mutate']:uc.mem_write(REG,struct.pack('<I',port1))
   f['events'].append(event);uc.reg_write(UC_ARM_REG_R0,value);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  def fault(uc,access,address,size,value,user):faults[id(uc)].append((access,address,size));return False
  for uc in (stock,candidate):uc.hook_add(UC_HOOK_CODE,hook);uc.hook_add(UC_HOOK_MEM_READ_UNMAPPED,fault);uc.hook_add(UC_HOOK_MEM_FETCH_UNMAPPED,fault)
  blank=bytes([0xa5])*0x1000
  def setup(uc,nodes=0,enabled=1,mutex=0x2001f000,current=0x20012340,stride=28,allocate=True,status=0,mutate=False):
   states[id(uc)]={'events':[],'allocations':0,'allocate':allocate,'status':status,'mutate':mutate};faults[id(uc)].clear();uc.mem_write(POOL,blank);uc.mem_write(0x20006730,bytes([enabled]));uc.mem_write(MUTEX,struct.pack('<I',mutex));uc.mem_write(0x2000781c,struct.pack('<I',current));uc.mem_write(REG,struct.pack('<4I',port0,stride,A if nodes else 0,B if nodes==2 else A if nodes else 0));uc.mem_write(port0,struct.pack('<3I',0,0,0x100e101));uc.mem_write(port1,struct.pack('<3I',0,0,0x100e111));uc.mem_write(owner1,struct.pack('<I',port1))
   for i,address in enumerate((A,B)[:nodes]):
    name=b'alpha' if not i else b'beta';uc.mem_write(address,struct.pack('<2I',REG,0x20016000+i*16)+name+b'\0'*(8-len(name))+struct.pack('<3I',0x1234567b,0xdeadbeef,10000));uc.mem_write(address+stride,struct.pack('<2I',A if i else 0,B if nodes==2 and i==0 else 0))
  def run(uc,entry,args):
   for reg,value in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2),args):uc.reg_write(reg,value)
   uc.reg_write(UC_ARM_REG_SP,0x2003f000);uc.reg_write(UC_ARM_REG_LR,0x20000101)
   try:uc.emu_start(entry|1,0x20000100,count=200000)
   except UcError:assert faults[id(uc)],hex(uc.reg_read(UC_ARM_REG_PC))
   else:assert uc.reg_read(UC_ARM_REG_PC)==0x20000100
   return uc.reg_read(UC_ARM_REG_R0),list(states[id(uc)]['events']),list(faults[id(uc)]),bytes(uc.mem_read(REG,16)),bytes(uc.mem_read(POOL,0x1000)),bytes(uc.mem_read(MUTEX,4))
  def compare(name,args,void=False):
   a=run(stock,ENTRIES[name],args);b=run(candidate,syms[name],args);assert (a[1:] if void else a)==(b[1:] if void else b),(name,args,a[:4],b[:4]);return a
  register_cases=0
  names=(None,'','alpha','beta','ALPHA','abcdefgh','abcdefghX','x'*255,'x'*256,'x'*257,'x'*260)
  for name,nodes,enabled,allocate,mutex,current,interval,mutate in itertools.product(names,(0,1,2),(0,1,2,128),(False,True),(0,0x2001f000),(0,0x20012340,0xffffffff),(0,10000,0xffffffff),(False,True)):
   for uc in (stock,candidate):
    setup(uc,nodes,enabled,mutex,current,allocate=allocate,status=-1,mutate=mutate)
    if name is not None:uc.mem_write(0x20002000,name.encode()+b'\0')
   compare('r1_native_watchdog_register',(0x20002000 if name is not None else 0,interval,0));register_cases+=1
  registration_sequence_cases=0
  for sequence in (('abcdefg','abcdefg'),('abcdefgh','abcdefgh'),('abcdefgh','abcdefg'),('x'*256,''),('x'*256,'x'*256),('x'*257,'x')):
   for uc in (stock,candidate):setup(uc)
   for text in sequence:
    for uc in (stock,candidate):uc.mem_write(0x20002000,text.encode()+b'\0')
    compare('r1_native_watchdog_register',(0x20002000,10000,0));registration_sequence_cases+=1
  record_cases=0;record_faults=0
  for name,handle,flags,owner,port,mutex,mutate in itertools.product(('r1_native_watchdog_arm','r1_native_watchdog_disarm','r1_native_watchdog_feed'),(0,A),(0,1,2,3,0xffffffff),(REG,owner1,0),(port0,port1,0),(0,0x2001f000),(False,True)):
   for uc in (stock,candidate):
    setup(uc,1,mutex=mutex,mutate=mutate);uc.mem_write(A,struct.pack('<I',owner));uc.mem_write(A+16,struct.pack('<2I',flags,0xdeadbeef));uc.mem_write(REG,struct.pack('<I',port))
   a=compare(name,(handle,0,0),True);record_cases+=1;record_faults+=bool(a[2])
  list_cases=0
  for name in ('r1_native_list_head','r1_native_list_tail','r1_native_list_empty'):
   for nodes,null in itertools.product((0,1,2),(False,True)):
    for uc in (stock,candidate):setup(uc,nodes)
    compare(name,(0 if null else LIST,0,0));list_cases+=1
  for payload in (0,1,3,4,7,28,255,0xfffffffd,0xfffffffe,0xffffffff):
   for uc in (stock,candidate):setup(uc,2)
   compare('r1_native_list_initialize',(LIST,payload,0),True);list_cases+=1
  for stride,nodes,allocate in itertools.product((0,4,28,32,256),(0,1,2),(False,True)):
   for name in ('r1_native_list_append','r1_native_list_prepend'):
    for uc in (stock,candidate):setup(uc,nodes,stride=stride,allocate=allocate)
    compare(name,(LIST,0,0));list_cases+=1
  for stride,nodes in itertools.product((0,4,28,32,256),(1,2)):
   for uc in (stock,candidate):setup(uc,nodes,stride=stride)
   compare('r1_native_list_next',(LIST,A,0));list_cases+=1
   for name in ('r1_native_list_set_next','r1_native_list_set_previous'):
    for node in (0,A,B):
     for uc in (stock,candidate):setup(uc,nodes,stride=stride)
     compare(name,(LIST,node,NEW),True);list_cases+=1
  kernel_cases=0
  for current in (0,1,0x20012340,0x7fffffff,0x80000000,0xffffffff):
   for uc in (stock,candidate):setup(uc,current=current)
   compare('xTaskGetCurrentTaskHandle',(0,0,0));kernel_cases+=1
 receipt.write_text(json.dumps(dict(application_sha256=sha(app),report_sha256=sha(report),object_sha256=sha(obj),selected_current_task_sha256=sha(selected),runtime_report_sha256=sha(runtime_report),register_comparisons=register_cases,registration_sequence_comparisons=registration_sequence_cases,record_comparisons=record_cases,record_fault_comparisons=record_faults,list_comparisons=list_cases,kernel_getter_comparisons=kernel_cases,initial_owned_bytes_compared=25,scope='Actual mutex adapters, offset-list allocation/walk/stores, watchdog registration/flags/port calls and pinned FreeRTOS current-task getter with actual source memory/string functions',limitations=['Heap allocation, CMSIS mutex operations and final watchdog sample callbacks are intercepted.','Manager initialization, actual time/sample backend, full kernel layout, scheduler concurrency and physical watchdog behavior remain open.','Native register stores only seven name bytes after uint8 strlen truncation and rejects exact duplicate names; these quirks are preserved.','Original instruction identity and whole-image source completeness remain open.'],instruction_identity_proven=False),indent=2)+'\n');print(f'{register_cases} registration, {record_cases} record ({record_faults} faults), {list_cases} list and {kernel_cases} current-task comparisons passed')
if __name__=='__main__':main()
