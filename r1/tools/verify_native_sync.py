#!/usr/bin/env python3
"""Compare exact native task barriers, ARM shift semantics and park loop."""
import hashlib,json,struct,subprocess,tempfile,itertools
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 receipt=BASE/'native-sync/verification.json';receipt.unlink(missing_ok=True);app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';report=BASE/'native-sync/report.json';data=json.loads(report.read_text());obj=BASE/'native-sync/native_sync.o';assert sha(obj)==data['units'][0]['object_sha256']
 for path,digest in data['inputs'].items():assert sha(ROOT/path)==digest,path
 names=('osEventFlagsSet','osThreadFlagsWait','osDelay','r1_structured_log_mode_get','r1_structured_log_format','nrf_log_frontend_std_1','r1_native_watchdog_arm');addresses=(0x7d1a0,0x7d780,0x7d154,0x914ec,0x91638,0x799c8,0x5dbea)
 with tempfile.TemporaryDirectory() as directory:
  tmp=Path(directory);ld=tmp/'layout.ld';elf=tmp/'test.elf';binary=tmp/'test.bin';ld.write_text('SECTIONS { .text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } .r1.sync.flags 0x2000655c (NOLOAD) : { *(.r1.sync.flags) } /DISCARD/ : { *(.comment) *(.note*) } }');subprocess.run(['arm-none-eabi-ld','-T',str(ld),*['--defsym='+n+'='+hex(0x100e001+i*16) for i,n in enumerate(names)],str(obj),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True)
  syms={x.split()[-1]:int(x.split()[0],16) for x in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x.split())==3};assert syms['r1_native_sync_event_flags']==0x2000655c
  stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB);stock.mem_map(0x20000,0xc0000);stock.mem_write(0x27000,app.read_bytes())
  for uc in (stock,candidate):uc.mem_map(0x1000000,0x10000);uc.mem_map(0x20000000,0x40000)
  candidate.mem_write(0x1000000,binary.read_bytes());stock.reg_write(UC_ARM_REG_SP,0x2003f000);stock.emu_start(0x283a1,0x27208,count=2000000);assert stock.reg_read(UC_ARM_REG_PC)==0x27208;assert bytes(stock.mem_read(0x2000655c,4))==bytes(candidate.mem_read(0x2000655c,4))==bytes(4);state={};seams=dict(zip(addresses,names));seams.update({0x100e000+i*16:n for i,n in enumerate(names)})
  def string(uc,address):
   out=bytearray()
   while True:
    b=uc.mem_read(address+len(out),1)[0]
    if not b:return out.decode()
    out.append(b);assert len(out)<100
  def hook(uc,address,size,user):
   if address not in seams:return
   f=state[id(uc)];name=seams[address];r=[uc.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)];value=0
   if name=='osEventFlagsSet':event=(name,r[0],r[1]);value=0xfffffffc
   elif name=='osThreadFlagsWait':event=(name,tuple(r[:3]));assert f['wait']<len(f['waits']);value=f['waits'][f['wait']];f['wait']+=1
   elif name=='osDelay':
    event=(name,r[0]);f['delay']+=1
    if f['delay']==3:f['events'].append(event);f['stopped']=True;uc.emu_stop();return
    value=0xfffffffc
   elif name=='r1_structured_log_mode_get':index=f['read'];value=f['modes'][min(index,len(f['modes'])-1)];f['read']+=1;event=(name,value)
   elif name=='r1_structured_log_format':event=(name,r[0],string(uc,r[1]),string(uc,r[2]),r[3]);uc.mem_write(0x2000655c,struct.pack('<I',0x20013000))
   elif name=='nrf_log_frontend_std_1':event=(name,r[0],string(uc,r[1]),r[2]);uc.mem_write(0x2000655c,struct.pack('<I',0x20014000))
   else:event=(name,r[0]);uc.mem_write(0x2000655c,struct.pack('<I',0x20015000))
   f['events'].append(event);uc.reg_write(UC_ARM_REG_R0,value);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  for uc in (stock,candidate):uc.hook_add(UC_HOOK_CODE,hook)
  def run(uc,entry,group,modes,waits,handle):
   f={'events':[],'modes':modes,'waits':waits,'read':0,'wait':0,'delay':0,'stopped':False};state[id(uc)]=f;uc.mem_write(0x2000655c,struct.pack('<I',handle));uc.reg_write(UC_ARM_REG_R0,group);uc.reg_write(UC_ARM_REG_R1,0x89abcdef);uc.reg_write(UC_ARM_REG_SP,0x2003f000);uc.reg_write(UC_ARM_REG_LR,0x20000101);uc.emu_start(entry|1,0x20000100,count=10000);assert f['stopped'] or uc.reg_read(UC_ARM_REG_PC)==0x20000100
   return list(f['events']),bytes(uc.mem_read(0x2000655c,4)),f['stopped']
  comparisons=0;groups=tuple(range(256))+(256,257,511,512,0x80000000,0xffffffff);modes=tuple((x,) for x in range(8))+((0,4,2),(1,2,0),(0,0,2),(4,0,0));waits=((0x800000,),(0,0,0x800000),(0xffffffff,),(0x80000000,0x80800000))
  for stock_entry,name in ((0x923a4,'r1_native_suspend_signal'),(0x923b4,'r1_native_sync_wait'),(0x92440,'r1_native_sync_signal'),(0x45c20,'r1_native_worker_park')):
   for group,mode,wait,handle in itertools.product(groups,modes,waits if stock_entry==0x923b4 else waits[:1],(0,0x20011000,0xffffffff)):
    a=run(stock,stock_entry,group,mode,wait,handle);b=run(candidate,syms[name],group,mode,wait,handle);assert a==b,(name,group,mode,wait,handle,a,b);comparisons+=1
 receipt.write_text(json.dumps(dict(application_sha256=sha(app),report_sha256=sha(report),object_sha256=sha(obj),comparisons=comparisons,initial_event_field_bytes_compared=4,scope='Actual four barrier/park bodies; all low-byte ARM shift counts, upper group bits, repeated startup waits including high-bit errors, dynamic mode/handle logging, event flags and three indefinite-delay attempts',limitations=['CMSIS flag/wait/delay, log backends and watchdog arm are intercepted.','Only the manager event-handle field is source-owned; complete manager startup/object allocation and physical synchronization remain open.','Original instruction identity and whole-image source completeness remain open.'],instruction_identity_proven=False),indent=2)+'\n');print(f'{comparisons} native synchronization comparisons passed')
if __name__=='__main__':main()
