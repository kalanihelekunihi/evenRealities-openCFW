#!/usr/bin/env python3
"""Compare native task creation/termination, attributes and failure faults."""
import hashlib,json,struct,subprocess,tempfile,itertools
from pathlib import Path
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_WRITE_UNMAPPED
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_BASEPRI,UC_ARM_REG_IPSR
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 receipt=BASE/'native-task-lifecycle/verification.json';receipt.unlink(missing_ok=True);app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 report=BASE/'native-task-lifecycle/report.json';data=json.loads(report.read_text());obj=BASE/'native-task-lifecycle/native_task_lifecycle.o';assert sha(obj)==data['units'][0]['object_sha256']
 for path,digest in data['inputs'].items():assert sha(ROOT/path)==digest,path
 configuration=BASE/'native-task-lifecycle/configuration-evidence.json';rows=json.loads(configuration.read_text())['rows'];providers={};others=[]
 for name,object_name in (('native-events','native_events.o'),('native-tx','native_tx.o')):
  path=BASE/(name+'/report.json');r=json.loads(path.read_text());object_path=BASE/(name+'/'+object_name);assert sha(object_path)==r['units'][0]['object_sha256'];others.append(object_path);providers[name+'/report.json']=sha(path)
 creators={'a':0x43b8c,'f':0x46924,'g':0x46a44,'b':0x44ef0,'e':0x4509c};stoppers={'a':0x43b74,'f':0x4690c,'g':0x46a2c,'b':0x44ed8,'e':0x45084};contexts={'a':0x2000668c,'f':0x20006608,'g':0x200066d8,'b':0x200065e0,'e':0x200065bc}
 with tempfile.TemporaryDirectory() as directory:
  tmp=Path(directory);ld=tmp/'layout.ld';elf=tmp/'test.elf';binary=tmp/'test.bin';sections=' .r1.event.sensor 0x2000668c : { *(.r1.event.sensor) } .r1.event.system 0x20006608 : { *(.r1.event.system) } .r1.event.storage 0x200066d8 : { *(.r1.event.storage) } .r1.tx.channel1 0x200065bc : { *(.r1.tx.channel1) } .r1.tx.shared 0x200065e0 : { *(.r1.tx.shared) } '
  for row in rows:
   for suffix,key in (('tcb','control_block'),('stack','stack')):sections+=' .r1.task.'+row['letter']+'.'+suffix+' '+row[key]+' (NOLOAD) : { *(.r1.task.'+row['letter']+'.'+suffix+') } '
  ld.write_text('SECTIONS { .text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } '+sections+'/DISCARD/ : { *(.comment) *(.note*) } }')
  roots=[name for row in rows for name in ('r1_thread_create_'+row['letter'],'r1_task_stop_'+row['stop_id'])]
  subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--gc-sections','--entry='+roots[0],*['--undefined='+n for n in roots],'--defsym=osThreadNew=0x100e001','--defsym=osThreadTerminate=0x100e011',*['--defsym='+row['task_symbol']+'='+hex(int(row['task_entry'],16)|1) for row in rows],str(obj),*map(str,others),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True)
  syms={x.split()[-1]:int(x.split()[0],16) for x in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x.split())==3}
  stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);stock.mem_map(0x20000,0xc0000);stock.mem_write(0x27000,app.read_bytes());events={id(stock):[],id(candidate):[]};faults={id(stock):[],id(candidate):[]};fixture=[None]
  for uc in (stock,candidate):uc.mem_map(0x1000000,0x10000);uc.mem_map(0x20000000,0x40000)
  candidate.mem_write(0x1000000,binary.read_bytes())
  def string(uc,address):
   out=bytearray()
   while True:
    b=uc.mem_read(address+len(out),1)[0]
    if not b:return out.decode()
    out.append(b);assert len(out)<32
  def hook(uc,address,size,user):
   if address not in (0x7d818,0x7d8d6,0x100e000,0x100e010):return
   f=fixture[0];r=[uc.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2)]
   if address in (0x7d818,0x100e000):
    fields=struct.unpack('<9I',bytes(uc.mem_read(r[2],36)));events[id(uc)].append(('new',r[0],r[1],string(uc,fields[0]),fields[1:]));value=f['new']
   else:events[id(uc)].append(('terminate',r[0]));value=f['status']&0xffffffff
   uc.mem_write(f['context']+8,struct.pack('<I',0xdeadbeef));uc.reg_write(UC_ARM_REG_R0,value);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  def fault(uc,access,address,size,value,user):faults[id(uc)].append((address,size,value));return False
  for uc in (stock,candidate):uc.hook_add(UC_HOOK_CODE,hook);uc.hook_add(UC_HOOK_MEM_WRITE_UNMAPPED,fault)
  stock.reg_write(UC_ARM_REG_SP,0x2003f000);stock.emu_start(0x283a1,0x27208,count=2000000);assert stock.reg_read(UC_ARM_REG_PC)==0x27208;zero_bytes=0
  for row in rows:
   for suffix,key,size in (('tcb','control_block',112),('stack','stack',row['stack_bytes'])):
    address=int(row[key],16);assert syms['r1_task_'+row['letter']+'_'+suffix]==address;assert bytes(stock.mem_read(address,size))==bytes(candidate.mem_read(address,size))==bytes(size);zero_bytes+=size
  def run(uc,entry,context,handle,new,status,basepri,ipsr):
   fixture[0]={'context':context,'new':new,'status':status};events[id(uc)].clear();faults[id(uc)].clear();uc.mem_write(context+8,struct.pack('<2I',handle,0x12345678));uc.reg_write(UC_ARM_REG_BASEPRI,basepri);uc.reg_write(UC_ARM_REG_IPSR,ipsr);uc.reg_write(UC_ARM_REG_SP,0x2003f000);uc.reg_write(UC_ARM_REG_LR,0x20000101)
   try:uc.emu_start(entry|1,0x20000100,count=10000)
   except UcError:assert faults[id(uc)]
   else:assert uc.reg_read(UC_ARM_REG_PC)==0x20000100
   return list(events[id(uc)]),list(faults[id(uc)]),uc.reg_read(UC_ARM_REG_BASEPRI),bytes(uc.mem_read(context+8,8))
  comparisons=0;assertions=0
  for row in rows:
   letter=row['letter'];context=contexts[letter]
   for handle,new,basepri,ipsr in itertools.product((0,1,0x20012340,0xffffffff),(0,1,0x20012340),(0,32,128),(0,15,20)):
    args=(context,handle,new,0,basepri,ipsr);a=run(stock,creators[letter],*args);b=run(candidate,syms['r1_thread_create_'+letter],*args);assert a==b,(letter,args,a,b);comparisons+=1
    if not new:assert a[1]==[(0xffffffff,4,0)] and a[2]==64;assertions+=1
   for handle,status,basepri,ipsr in itertools.product((0,1,0x20012340,0xffffffff),(0,-1,-3),(0,32,128),(0,15,20)):
    args=(context,handle,0,status,basepri,ipsr);a=run(stock,stoppers[letter],*args);b=run(candidate,syms['r1_task_stop_'+row['stop_id']],*args);assert a==b,(letter,args,a,b);comparisons+=1
 receipt.write_text(json.dumps(dict(application_sha256=sha(app),report_sha256=sha(report),object_sha256=sha(obj),provider_reports=providers,configuration_sha256=sha(configuration),comparisons=comparisons,assertion_fault_comparisons=assertions,source_owned_zero_bytes_compared=zero_bytes,attribute_records=5,scope='Ten creator/stopper bodies, all five native CMSIS attribute records, zeroed TCB/stack reservations, repeated creation, failed termination and exact creation assertion faults',limitations=['CMSIS create/terminate are intercepted and task-entry symbols are reference-only test bindings.','112-byte TCB reservations do not prove the complete kernel TCB configuration.','Actual task execution, scheduling, physical faults and original compiler output remain open.'],instruction_identity_proven=False),indent=2)+'\n');print(f'{comparisons} lifecycle comparisons passed, including {assertions} creation faults; {zero_bytes} zero-initialized source bytes matched')
if __name__=='__main__':main()
