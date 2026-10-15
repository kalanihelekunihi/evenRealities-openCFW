#!/usr/bin/env python3
"""Compare actual native publisher/queue adapter with authenticated Thumb."""
import hashlib,json,struct,subprocess,tempfile,itertools
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 receipt=BASE/'native-events/verification.json';receipt.unlink(missing_ok=True);app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 report=BASE/'native-events/report.json';data=json.loads(report.read_text());obj=BASE/'native-events/native_events.o';assert sha(obj)==data['units'][0]['object_sha256']
 for path,digest in data['inputs'].items():assert sha(ROOT/path)==digest,path
 runtime=BASE/'runtime/memory-runtime.o';runtime_report=BASE/'runtime/report.json';assert sha(runtime)==json.loads(runtime_report.read_text())['relocatable_sha256']
 contexts={'r1_event_sensor':0x2000668c,'r1_event_system':0x20006608,'r1_event_storage':0x200066d8};callbacks={'r1_thread_create_a':0x43b8d,'r1_task_stop_668c':0x43b75,'r1_thread_create_f':0x46925,'r1_task_stop_6608':0x4690d,'r1_thread_create_g':0x46a45,'r1_task_stop_66d8':0x46a2d}
 names=('pvPortMalloc','vPortFree','osMessageQueuePut','osThreadFlagsSet','r1_structured_log_mode_get','r1_structured_log_format','nrf_log_frontend_std_2');addresses=(0x855a0,0x95d48,0x7d40c,0x7d6f4,0x914ec,0x91638,0x799d6)
 with tempfile.TemporaryDirectory() as directory:
  tmp=Path(directory);ld=tmp/'layout.ld';elf=tmp/'test.elf';binary=tmp/'test.bin';ld.write_text('SECTIONS { .text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } '+''.join('.r1.event.'+n.split('_')[-1]+' '+hex(a)+' : { *(.r1.event.'+n.split('_')[-1]+') } ' for n,a in contexts.items())+'/DISCARD/ : { *(.comment) *(.note*) } }')
  subprocess.run(['arm-none-eabi-ld','-T',str(ld),*['--defsym='+n+'='+hex(0x100e001+i*16) for i,n in enumerate(names)],*['--defsym='+n+'='+hex(a) for n,a in callbacks.items()],str(obj),str(runtime),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True)
  syms={x.split()[-1]:int(x.split()[0],16) for x in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x.split())==3}
  stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB);stock.mem_map(0x20000,0xc0000);stock.mem_write(0x27000,app.read_bytes());events={id(stock):[],id(candidate):[]};fixture=[None];reads={id(stock):0,id(candidate):0}
  for uc in (stock,candidate):uc.mem_map(0x1000000,0x10000);uc.mem_map(0x20000000,0x40000)
  stock.reg_write(UC_ARM_REG_SP,0x2003f000);stock.emu_start(0x283a1,0x27208,count=2000000);assert stock.reg_read(UC_ARM_REG_PC)==0x27208
  candidate.mem_write(0x1000000,binary.read_bytes())
  for name,address in contexts.items():
   assert syms[name]==address;section='.r1.event.'+name.split('_')[-1];path=tmp/(name+'.bin');subprocess.run(['arm-none-eabi-objcopy','--dump-section',section+'='+str(path),str(elf)],check=True);candidate.mem_write(address,path.read_bytes());assert bytes(candidate.mem_read(address,16))==bytes(stock.mem_read(address,16))
  seams=dict(zip(addresses,names));seams.update({0x100e000+i*16:n for i,n in enumerate(names)})
  def string(uc,address):
   out=bytearray()
   while True:
    b=uc.mem_read(address+len(out),1)[0]
    if not b:return out.decode()
    out.append(b);assert len(out)<200
  def hook(uc,address,size,user):
   if address not in seams:return
   name=seams[address];r=[uc.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)];f=fixture[0];value=0
   if name=='pvPortMalloc':events[id(uc)].append((name,r[0]));value=0x20014000 if f['malloc'] else 0
   elif name=='vPortFree':events[id(uc)].append((name,r[0]))
   elif name=='osMessageQueuePut':
    # Publisher leaves record word zero uninitialized; compare the defined tail.
    record=bytes(uc.mem_read(r[1]+4,12));event_id,length,payload=struct.unpack('<3I',record);body=bytes(uc.mem_read(payload,length)) if length>4 else record[8:8+length];events[id(uc)].append((name,r[0],event_id,length,payload,body,r[2],r[3]));value=f['status']&0xffffffff
   elif name=='osThreadFlagsSet':events[id(uc)].append((name,r[0],r[1]));value=0xfffffffc
   elif name=='r1_structured_log_mode_get':
    index=reads[id(uc)];value=f['modes'][min(index,len(f['modes'])-1)];reads[id(uc)]+=1;events[id(uc)].append((name,value))
   elif name=='r1_structured_log_format':events[id(uc)].append((name,r[0],string(uc,r[1]),string(uc,r[2]),r[3],struct.unpack('<I',bytes(uc.mem_read(uc.reg_read(UC_ARM_REG_SP),4)))[0]))
   else:events[id(uc)].append((name,r[0],string(uc,r[1]),r[2],r[3]))
   uc.reg_write(UC_ARM_REG_R0,value);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  for uc in (stock,candidate):uc.hook_add(UC_HOOK_CODE,hook)
  pattern=bytes((i*17+3)&255 for i in range(4096))
  def run(uc,entry,event_id,length,malloc,handles,status,modes):
   fixture[0]={'malloc':malloc,'status':status,'modes':modes};events[id(uc)].clear();reads[id(uc)]=0
   for i,address in enumerate(contexts.values()):uc.mem_write(address+8,struct.pack('<2I',0x20011000+i*32 if handles&1 else 0,0x20012000+i*32 if handles&2 else 0))
   uc.mem_write(0x20002000,pattern);uc.mem_write(0x20014000,bytes(4096));uc.reg_write(UC_ARM_REG_R0,event_id);uc.reg_write(UC_ARM_REG_R1,0x20002000 if length else 0);uc.reg_write(UC_ARM_REG_R2,length);uc.reg_write(UC_ARM_REG_SP,0x2003f000);uc.reg_write(UC_ARM_REG_LR,0x20000101);uc.emu_start(entry|1,0x20000100,count=200000);assert uc.reg_read(UC_ARM_REG_PC)==0x20000100
   return uc.reg_read(UC_ARM_REG_R0),list(events[id(uc)]),bytes(uc.mem_read(0x20014000,1024))
  comparisons=0
  for case in itertools.product((0,1,0xffe,0xfff,0x1000,0x1ffe,0x1fff,0x2000,0x2fff,0x3000,0xffffffff,0x80000000),(0,1,2,3,4,5,16,65,73,128,1024),(0,1),range(4),(0,1,-1),tuple((x,) for x in range(8))):
   a=run(stock,0x8d8fc,*case);b=run(candidate,syms['r1_event_publish'],*case);assert a==b,(case,a[:2],b[:2]);comparisons+=1
  for modes in ((0,4,2),(1,2,0),(0,0,2),(4,0,0),(2,1,4)):
   case=(0x2003,65,0,3,0,modes);assert run(stock,0x8d8fc,*case)==run(candidate,syms['r1_event_publish'],*case);comparisons+=1
  adapter_comparisons=0
  for null_context,handles,null_record,status in itertools.product((False,True),range(4),(False,True),(0,1,-1)):
   outcomes=[]
   for uc,entry in ((stock,0x924c0),(candidate,syms['r1_event_bus_enqueue'])):
    fixture[0]={'malloc':1,'status':status,'modes':(0,)};events[id(uc)].clear();uc.mem_write(0x20006694,struct.pack('<2I',0x20011000 if handles&1 else 0,0x20012000 if handles&2 else 0));uc.mem_write(0x20003000,struct.pack('<4I',0xdeadbeef,0x2003,3,0x00030201));uc.reg_write(UC_ARM_REG_R0,0 if null_context else 0x2000668c);uc.reg_write(UC_ARM_REG_R1,0 if null_record else 0x20003000);uc.reg_write(UC_ARM_REG_SP,0x2003f000);uc.reg_write(UC_ARM_REG_LR,0x20000101);uc.emu_start(entry|1,0x20000100,count=10000);assert uc.reg_read(UC_ARM_REG_PC)==0x20000100;outcomes.append((uc.reg_read(UC_ARM_REG_R0),list(events[id(uc)])))
   assert outcomes[0]==outcomes[1],(null_context,handles,null_record,status,outcomes);adapter_comparisons+=1
 receipt.write_text(json.dumps(dict(application_sha256=sha(app),report_sha256=sha(report),object_sha256=sha(obj),runtime_report_sha256=sha(runtime_report),comparisons=comparisons,adapter_comparisons=adapter_comparisons,context_prefix_initial_bytes_compared=48,record_bytes=16,uninitialized_leading_record_bytes=4,scope='Publisher ID windows, inline/heap payload bytes, allocation failure logs, cleanup and real enqueue-adapter queue/wake calls; initial task-context prefixes match scatter',limitations=['Heap allocation, CMSIS queue/flags and logging backends are intercepted.','The leading record word is intentionally uninitialized and excluded from byte comparison; its provenance and downstream meaning remain open.','Only 16-byte task-context prefixes are owned; complete task-state layouts and creator/stopper bodies remain open.','Physical queue concurrency, transport and original instruction identity remain unproven.'],instruction_identity_proven=False),indent=2)+'\n');print(f'{comparisons} native event comparisons passed')
if __name__=='__main__':main()
