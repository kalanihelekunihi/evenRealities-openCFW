#!/usr/bin/env python3
"""Compare all three original BLE transmit veneers and common producer."""
import hashlib,json,struct,subprocess,tempfile,itertools
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 receipt=BASE/'native-tx/verification.json';receipt.unlink(missing_ok=True);app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 report=BASE/'native-tx/report.json';data=json.loads(report.read_text());obj=BASE/'native-tx/native_tx.o';assert sha(obj)==data['units'][0]['object_sha256']
 for path,digest in data['inputs'].items():assert sha(ROOT/path)==digest,path
 providers={};others=[]
 for name,object_name,field in (('runtime','memory-runtime.o','relocatable_sha256'),('connection-handle','connection_handle.o','unit')):
  path=BASE/(name+'/report.json');r=json.loads(path.read_text());object_path=BASE/(name+'/'+object_name);assert sha(object_path)==(r['units'][0]['object_sha256'] if field=='unit' else r[field]);others.append(object_path);providers[name+'/report.json']=sha(path)
 contexts={'r1_tx_channel1':0x200065bc,'r1_tx_shared':0x200065e0};callbacks={'r1_thread_create_e':0x4509d,'r1_task_stop_65bc':0x45085,'r1_thread_create_b':0x44ef1,'r1_task_stop_65e0':0x44ed9}
 names=('pvPortMalloc','vPortFree','osMessageQueueGetCount','osMessageQueueGetCapacity','osMessageQueuePut','osThreadFlagsSet','r1_structured_log_mode_get','r1_structured_log_format','nrf_log_frontend_std_0','nrf_log_frontend_std_2','nrf_log_frontend_std_3');addresses=(0x855a0,0x95d48,0x7d390,0x7d388,0x7d40c,0x7d6f4,0x914ec,0x91638,0x799c0,0x799d6,0x799e6)
 with tempfile.TemporaryDirectory() as directory:
  tmp=Path(directory);ld=tmp/'layout.ld';elf=tmp/'test.elf';binary=tmp/'test.bin';ld.write_text('SECTIONS { .text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } .r1.tx.channel1 0x200065bc : { *(.r1.tx.channel1) } .r1.tx.shared 0x200065e0 : { *(.r1.tx.shared) } .r1.connection.field6 0x200064b8 : { *(.r1.connection.field6) } .r1.connection.field8 0x200064ba : { *(.r1.connection.field8) } .r1.connection.field10 0x200064bc : { *(.r1.connection.field10) } /DISCARD/ : { *(.comment) *(.note*) } }')
  subprocess.run(['arm-none-eabi-ld','-T',str(ld),*['--defsym='+n+'='+hex(0x100e001+i*16) for i,n in enumerate(names)],*['--defsym='+n+'='+hex(a) for n,a in callbacks.items()],str(obj),*map(str,others),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True)
  syms={x.split()[-1]:int(x.split()[0],16) for x in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x.split())==3}
  stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB);stock.mem_map(0x20000,0xc0000);stock.mem_write(0x27000,app.read_bytes());events={id(stock):[],id(candidate):[]};fixture=[None];reads={id(stock):0,id(candidate):0}
  for uc in (stock,candidate):uc.mem_map(0x1000000,0x10000);uc.mem_map(0x20000000,0x40000)
  stock.reg_write(UC_ARM_REG_SP,0x2003f000);stock.emu_start(0x283a1,0x27208,count=2000000);assert stock.reg_read(UC_ARM_REG_PC)==0x27208;candidate.mem_write(0x1000000,binary.read_bytes())
  for name,address in contexts.items():
   assert syms[name]==address;section='.r1.tx.'+name.split('_')[-1];path=tmp/(name+'.bin');subprocess.run(['arm-none-eabi-objcopy','--dump-section',section+'='+str(path),str(elf)],check=True);candidate.mem_write(address,path.read_bytes());assert bytes(candidate.mem_read(address,16))==bytes(stock.mem_read(address,16))
  seams=dict(zip(addresses,names));seams.update({0x100e000+i*16:n for i,n in enumerate(names)})
  def string(uc,address):
   out=bytearray()
   while True:
    b=uc.mem_read(address+len(out),1)[0]
    if not b:return out.decode()
    out.append(b);assert len(out)<200
  def hook(uc,address,size,user):
   if address not in seams:return
   name=seams[address];r=[uc.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)];f=fixture[0];value=0;event=None
   if name=='pvPortMalloc':event=(name,r[0]);value=0x20014000 if f['malloc'] else 0
   elif name=='vPortFree':event=(name,r[0])
   elif name=='osMessageQueueGetCount':
    event=(name,r[0]);value=f['count']
    if f['mutate']:uc.mem_write(f['context']+12,struct.pack('<I',0x20013000))
   elif name=='osMessageQueueGetCapacity':event=(name,r[0]);value=f['capacity']
   elif name=='osMessageQueuePut':
    pointer=struct.unpack('<I',bytes(uc.mem_read(r[1],4)))[0];header=struct.unpack('<3I',bytes(uc.mem_read(pointer,12)));event=(name,r[0],header,bytes(uc.mem_read(pointer+12,header[2])),r[2],r[3]);value=f['status']&0xffffffff
    if f['mutate']:uc.mem_write(f['context']+8,struct.pack('<I',0x20015000))
   elif name=='osThreadFlagsSet':event=(name,r[0],r[1]);value=0xfffffffc
   elif name=='r1_structured_log_mode_get':
    index=reads[id(uc)];value=f['modes'][min(index,len(f['modes'])-1)];reads[id(uc)]+=1;event=(name,value)
   elif name=='r1_structured_log_format':
    fmt=string(uc,r[2]);count=fmt.count('%d');args=([r[3]]+list(struct.unpack('<2I',bytes(uc.mem_read(uc.reg_read(UC_ARM_REG_SP),8)))))[:count];event=(name,r[0],string(uc,r[1]),fmt,args)
   else:
    count={'nrf_log_frontend_std_0':0,'nrf_log_frontend_std_2':2,'nrf_log_frontend_std_3':3}[name];args=(r[2:4]+[struct.unpack('<I',bytes(uc.mem_read(uc.reg_read(UC_ARM_REG_SP),4)))[0]])[:count];event=(name,r[0],string(uc,r[1]),args)
   events[id(uc)].append(event);uc.reg_write(UC_ARM_REG_R0,value);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  for uc in (stock,candidate):uc.hook_add(UC_HOOK_CODE,hook)
  pattern=bytes((i*17+3)&255 for i in range(4096));heap=bytes([0xa5])*4096
  def run(uc,entry,type,null,queue,malloc,status,length,handle,occupancy,modes,mutate=False,thread=0x20011000):
   fixture[0]={'malloc':malloc,'status':status,'modes':modes,'count':occupancy[0],'capacity':occupancy[1],'mutate':mutate,'context':0x200065e0 if type==0 else 0x200065bc};events[id(uc)].clear();reads[id(uc)]=0
   for i,address in enumerate(contexts.values()):uc.mem_write(address+8,struct.pack('<2I',thread+i*32 if thread else 0,0x20012000+i*32 if queue else 0))
   uc.mem_write(0x200064ba,struct.pack('<2H',handle,handle));uc.mem_write(0x20002000,pattern);uc.mem_write(0x20014000,heap);uc.reg_write(UC_ARM_REG_R0,0x89abcdef);uc.reg_write(UC_ARM_REG_R1,0 if null else 0x20002000);uc.reg_write(UC_ARM_REG_R2,length);uc.reg_write(UC_ARM_REG_SP,0x2003f000);uc.reg_write(UC_ARM_REG_LR,0x20000101);uc.emu_start(entry|1,0x20000100,count=200000);assert uc.reg_read(UC_ARM_REG_PC)==0x20000100
   return uc.reg_read(UC_ARM_REG_R0),list(events[id(uc)]),bytes(uc.mem_read(0x20014000,1024))
  comparisons=0;stock_entries=(0x34064,0x3407c,0x34070);candidate_entries=[syms['r1_ble_tx_queue_dispatch_type'+str(i)] for i in range(3)]
  for case in itertools.product(range(3),(False,True),(0,1),(0,1),(0,-3),(0,1,4,65,236),(0,0xffff),((0,20),(17,20),(18,20),(20,20),(0xffffffff,0xffffffff),(0x80000000,0x80000000),(0,0)),tuple((x,) for x in range(8))):
   type=case[0];a=run(stock,stock_entries[type],*case);b=run(candidate,candidate_entries[type],*case);assert a==b,(case,a[:2],b[:2]);comparisons+=1
  for type,modes,status in itertools.product(range(3),((0,4,2),(1,2,0),(0,0,2),(4,0,0),(2,1,4)),(0,-1)):
   case=(type,False,1,1,status,65,0,(18,20),modes,True);assert run(stock,stock_entries[type],*case)==run(candidate,candidate_entries[type],*case);comparisons+=1
  for type,length in itertools.product(range(3),(0x7fffffff,0x80000000,0xfffffff0,0xfffffff1,0xfffffff8,0xffffffff)):
   case=(type,False,1,0,0,length,0,(0,20),(7,));assert run(stock,stock_entries[type],*case)==run(candidate,candidate_entries[type],*case);comparisons+=1
  for type in range(3):
   case=(type,False,1,1,0,0,0,(0,20),(0,),False,0);assert run(stock,stock_entries[type],*case)==run(candidate,candidate_entries[type],*case);comparisons+=1
 receipt.write_text(json.dumps(dict(application_sha256=sha(app),report_sha256=sha(report),object_sha256=sha(obj),provider_reports=providers,comparisons=comparisons,context_prefix_initial_bytes_compared=32,scope='Three real veneers/common producer, actual C connection getters and memcpy; envelope bytes, allocation rounding/overflow requests, unsigned occupancy arithmetic, logs, mutable queue/thread handles, timeout, wake and cleanup',limitations=['Heap, CMSIS queue/flags and log providers are intercepted; no BLE worker executes.','Large length overflow cases force allocation failure; successful oversized copies are not exercised.','Only 16-byte task-context prefixes are owned; task creator/stopper bodies and complete private state remain open.','Original instruction identity and physical transport remain unproven.'],instruction_identity_proven=False),indent=2)+'\n');print(f'{comparisons} native transmit comparisons passed')
if __name__=='__main__':main()
