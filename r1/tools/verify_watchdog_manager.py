#!/usr/bin/env python3
"""Compare recovered watchdog startup, deadline scan and expired-task getter."""
import hashlib,json,struct,subprocess,tempfile,itertools
from pathlib import Path
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_WRITE_UNMAPPED,UC_HOOK_MEM_READ_UNMAPPED
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_BASEPRI
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();REG=0x20015404;FAULT=0x20006734;MUTEX=0x20006738;A=0x20018000;B=A+64;C=A+128
ROOTS={'r1_native_watchdog_initialize':0x5dab4,'r1_native_watchdog_check':0x5da4c,'r1_native_watchdog_expired_task':0x5da30}
def main():
 receipt=BASE/'watchdog-startup/manager-verification.json';receipt.unlink(missing_ok=True);app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';report=BASE/'watchdog-startup/report.json';data=json.loads(report.read_text());row=next(r for r in data['units'] if r['source'].endswith('/native_watchdog_manager.c'));obj=Path(row['command'][-1]);assert sha(obj)==row['object_sha256']
 for path,digest in data['inputs'].items():assert sha(ROOT/path)==digest,path
 watch_report=BASE/'native-watchdog/report.json';watch=json.loads(watch_report.read_text());watch_obj=BASE/'native-watchdog/native_watchdog.o';assert sha(watch_obj)==watch['units'][0]['object_sha256']
 with tempfile.TemporaryDirectory() as directory:
  tmp=Path(directory);ld=tmp/'layout.ld';elf=tmp/'test.elf';binary=tmp/'test.bin';attributes=tmp/'attributes.bin';ld.write_text('SECTIONS { .text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } .r1.watchdog.mutex_attributes 0x993c0 : { *(.r1.watchdog.mutex_attributes) } .r1.watchdog.enabled 0x20006730 (NOLOAD) : { *(.r1.watchdog.enabled) } .r1.watchdog.fault_record 0x20006734 (NOLOAD) : { *(.r1.watchdog.fault_record) } .r1.watchdog.mutex 0x20006738 (NOLOAD) : { *(.r1.watchdog.mutex) } .r1.watchdog.registry 0x20015404 (NOLOAD) : { *(.r1.watchdog.registry) } .r1.watchdog.mutex_storage 0x20015414 (NOLOAD) : { *(.r1.watchdog.mutex_storage) } /DISCARD/ : { *(.comment) *(.note*) } }')
  providers={'r1_native_watchdog_port_get':0x6625c,'osMutexNew':0x7d4d6,'osMutexAcquire':0x7d488,'osMutexRelease':0x7d536};subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--gc-sections','--entry='+next(iter(ROOTS)),*['--undefined='+n for n in ROOTS],*['--defsym='+n+'='+hex(0x100e001+i*16) for i,n in enumerate(providers)],str(obj),str(watch_obj),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True);subprocess.run(['arm-none-eabi-objcopy','--dump-section','.r1.watchdog.mutex_attributes='+str(attributes),str(elf)],check=True)
  syms={x.split()[-1]:int(x.split()[0],16) for x in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x.split())==3};assert syms['r1_native_watchdog_fault_record']==FAULT and syms['r1_native_watchdog_mutex_storage']==0x20015414
  stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);stock.mem_map(0x20000,0xc0000);stock.mem_write(0x27000,app.read_bytes());candidate.mem_map(0x90000,0x10000)
  for uc in (stock,candidate):uc.mem_map(0x1000000,0x10000);uc.mem_map(0x20000000,0x40000)
  candidate.mem_write(0x1000000,binary.read_bytes());candidate.mem_write(0x993c0,attributes.read_bytes());stock.reg_write(UC_ARM_REG_SP,0x2003f000);stock.emu_start(0x283a1,0x27208,count=2000000);assert stock.reg_read(UC_ARM_REG_PC)==0x27208
  for address,size in ((FAULT,4),(0x20015414,80)):assert bytes(stock.mem_read(address,size))==bytes(candidate.mem_read(address,size))==bytes(size)
  def string(uc,address):
   out=bytearray()
   while True:
    value=uc.mem_read(address+len(out),1)[0]
    if not value:return out.decode()
    out.append(value);assert len(out)<32
  original=struct.unpack('<4I',bytes(stock.mem_read(0x993c0,16)));compiled=struct.unpack('<4I',attributes.read_bytes());assert original[1:]==compiled[1:]==(0,0x20015414,80);assert string(stock,original[0])==string(candidate,compiled[0])=='fw_wtd';states={};faults={id(stock):[],id(candidate):[]};seams={a:n for n,a in providers.items()};seams.update({0x100e000+i*16:n for i,n in enumerate(providers)})
  def hook(uc,address,size,user):
   if address not in seams and address not in (0x100e100,0x100e110):return
   f=states[id(uc)];name=seams.get(address);r0=uc.reg_read(UC_ARM_REG_R0);r1=uc.reg_read(UC_ARM_REG_R1);value=0
   if name=='r1_native_watchdog_port_get':event=(name,);value=0x2001e000 if f['port'] else 0
   elif name=='osMutexNew':
    fields=struct.unpack('<4I',bytes(uc.mem_read(r0,16)));event=(name,string(uc,fields[0]),fields[1:]);value=f['new_mutex']
   elif name=='osMutexAcquire':event=(name,r0,r1);value=0xfffffffc
   elif name=='osMutexRelease':event=(name,r0);value=0xfffffffc
   elif address==0x100e100:event=('port_start',r0);value=f['start']
   else:event=('sample',r0,'time_output');uc.mem_write(r1,struct.pack('<I',f['now']));value=0
   f['events'].append(event);uc.reg_write(UC_ARM_REG_R0,value);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  def fault(uc,access,address,size,value,user):faults[id(uc)].append((access,address,size,value));return False
  for uc in (stock,candidate):uc.hook_add(UC_HOOK_CODE,hook);uc.hook_add(UC_HOOK_MEM_WRITE_UNMAPPED,fault);uc.hook_add(UC_HOOK_MEM_READ_UNMAPPED,fault)
  def setup(uc,enabled=0,mutex=0,port=True,new_mutex=0x20019000,start=1,now=0,nodes=0,flags=0,timestamp=0,interval=10000):
   states[id(uc)]={'events':[],'port':port,'new_mutex':new_mutex,'start':start,'now':now};faults[id(uc)].clear();uc.mem_write(0x20006730,bytes([enabled]));uc.mem_write(FAULT,struct.pack('<2I',B,mutex));uc.mem_write(REG,struct.pack('<4I',0x2001e000 if port else 0,28,A if nodes else 0,(A,B,C)[nodes-1] if nodes else 0));uc.mem_write(0x2001e000,struct.pack('<3I',0x100e101,0,0x100e111));uc.mem_write(A,bytes([0x55])*192)
   for i,address in enumerate((A,B,C)[:nodes]):
    uc.mem_write(address,struct.pack('<2I',REG,0x2001a000+i*16)+bytes(8)+struct.pack('<3I',(flags if i!=1 else flags^2)&0xffffffff,(timestamp+i*16)&0xffffffff,(interval+i*25)&0xffffffff));uc.mem_write(address+28,struct.pack('<2I',(A,B,C)[i-1] if i else 0,(A,B,C)[i+1] if i+1<nodes else 0))
   uc.reg_write(UC_ARM_REG_BASEPRI,32)
  def run(uc,entry):
   uc.reg_write(UC_ARM_REG_SP,0x2003f000);uc.reg_write(UC_ARM_REG_LR,0x20000101)
   try:uc.emu_start(entry|1,0x20000100,count=10000)
   except UcError:assert faults[id(uc)],hex(uc.reg_read(UC_ARM_REG_PC))
   else:assert uc.reg_read(UC_ARM_REG_PC)==0x20000100
   return uc.reg_read(UC_ARM_REG_R0),list(states[id(uc)]['events']),list(faults[id(uc)]),uc.reg_read(UC_ARM_REG_BASEPRI),bytes(uc.mem_read(0x20006730,12)),bytes(uc.mem_read(REG,16)),bytes(uc.mem_read(A,192))
  init_cases=0
  for enabled,mutex,port,new_mutex,start in itertools.product((0,1,2,128),(0,0x20019000),(False,True),(0,0x20019100),(0,1,2,0xffffffff)):
   for uc in (stock,candidate):setup(uc,enabled,mutex,port,new_mutex,start,nodes=2)
   a=run(stock,ROOTS['r1_native_watchdog_initialize']);b=run(candidate,syms['r1_native_watchdog_initialize']);assert a==b,((enabled,mutex,port,new_mutex,start),a,b);init_cases+=1
  poll_cases=0;expiry_faults=0;null_port_faults=0
  for enabled,mutex,port,nodes,flags,now,timestamp,interval in itertools.product((0,1,128),(0,0x20019000),(False,True),(0,1,3),(0,1,2,3,0xffffffff),(0,16,0x7fffffff,0xffffffff),(0,0xfffffff0),(0,1,32,33,10000,0xffffffff)):
   for uc in (stock,candidate):setup(uc,enabled,mutex,port,now=now,nodes=nodes,flags=flags,timestamp=timestamp,interval=interval)
   a=run(stock,ROOTS['r1_native_watchdog_check']);b=run(candidate,syms['r1_native_watchdog_check']);assert a[1:]==b[1:],((enabled,mutex,port,nodes,flags,now,timestamp,interval),a[1:],b[1:]);poll_cases+=1
   if a[2]:
    if a[2][0][1]==0xffffffff:assert a[3]==64 and a[2][0][2:]==(4,0);expiry_faults+=1
    else:assert a[2][0][1]==8;null_port_faults+=1
  getter_cases=0
  for record,flags,task in itertools.product((0,A,B),(0,1,2,3,0xffffffff),(0,1,0x20012340,0xffffffff)):
   for uc in (stock,candidate):setup(uc,nodes=2);uc.mem_write(FAULT,struct.pack('<I',record));uc.mem_write(A+4,struct.pack('<I',task));uc.mem_write(B+4,struct.pack('<I',task));uc.mem_write(A+16,struct.pack('<I',flags));uc.mem_write(B+16,struct.pack('<I',flags))
   a=run(stock,ROOTS['r1_native_watchdog_expired_task']);b=run(candidate,syms['r1_native_watchdog_expired_task']);assert a==b,(record,flags,task,a,b);getter_cases+=1
 receipt.write_text(json.dumps(dict(application_sha256=sha(app),report_sha256=sha(report),object_sha256=sha(obj),watchdog_report_sha256=sha(watch_report),initialize_comparisons=init_cases,poll_comparisons=poll_cases,expiry_fault_comparisons=expiry_faults,null_port_fault_comparisons=null_port_faults,getter_comparisons=getter_cases,initial_owned_zero_bytes_compared=84,mutex_attribute_bytes_compared=16,scope='Actual manager startup/list reset, CMSIS mutex attributes, reuse/failure paths, unsigned wrapping deadlines, armed-node skips, first expired record and exact assertion side effects',limitations=['Port getter/start/sample and CMSIS mutex calls are intercepted; sample always writes the time output.','Unwritten sample output, actual RTOS object behavior, hardware timing and whole-image identity remain open.','Initialize/check entries were omitted by the ownership ledger and do not inflate its tested-function count.'],instruction_identity_proven=False),indent=2)+'\n');print(f'{init_cases} initialization, {poll_cases} poll ({expiry_faults} expiry/{null_port_faults} null-port faults) and {getter_cases} getter comparisons passed')
if __name__=='__main__':main()
