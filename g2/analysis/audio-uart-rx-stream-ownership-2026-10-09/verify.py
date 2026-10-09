from pathlib import Path
import json,subprocess,hashlib,itertools,struct
from elftools.elf.elffile import ELFFile
from unicorn import *
from unicorn.arm_const import *
D=Path(__file__).resolve().parent;R=D.parents[2];rec=json.loads((D/'reproduction-receipt.json').read_text());elf=Path(rec['elf']);raw=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];syms={l.split()[2]:int(l.split()[0],16) for l in subprocess.check_output([str(Path(rec['gcc']).with_name('arm-none-eabi-nm')),str(elf)],text=True).splitlines() if len(l.split())==3};sections=[]
with elf.open('rb') as f:
 e=ELFFile(f)
 for s in e.iter_sections():
  if s['sh_flags']&2 and s['sh_size']:sections.append((s['sh_addr'],s.data()))
bind={'xStreamBufferSendFromISR':0x57e05e,'xStreamBufferSpacesAvailable':0x57e028,'prvWriteMessageToBuffer':0x57e0f0,'prvWriteBytesToBuffer':0x57e268,'prvBytesInBuffer':0x57e38c,'xStreamBufferGenericCreate':0x57deea,'prvInitialiseNewStreamBuffer':0x57e3a4,'am_hal_uart_fifo_read':0x58e2d8}
SB=0x20040000;DATA=0x20041000;SRC=0x20042000;OUT=0x20043000;UART=0x20044000

def run(name,f,native):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x438000,0x360000);u.mem_write(0x438000,raw);u.mem_map(0x100000,0x10000)
 for a,b in sections:u.mem_write(a,b)
 u.mem_map(0x20000000,0x100000);u.mem_map(0x40039000,0x2000)
 def w(a,x):u.mem_write(a,struct.pack('<I',x))
 u.mem_write(DATA,b'\xa5'*8192);u.mem_write(SRC,bytes((i*17+3)&255 for i in range(f.get('n',3)))+bytes(256));u.mem_write(SB,struct.pack('<7I',f.get('tail',0),f.get('head',0),f.get('length',32),f.get('trigger',1),f.get('waiter',0),0,DATA)+bytes([f.get('message',0),0,0,0])+bytes(4));w(OUT,0);w(UART+40,1)
 u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x10ff01);u.reg_write(UC_ARM_REG_BASEPRI,f.get('basepri',0));u.reg_write(UC_ARM_REG_PRIMASK,0)
 args=[SB,SRC,f.get('n',3),OUT if f.get('woken_pointer',1) else 0]
 if name=='xStreamBufferSpacesAvailable' or name=='prvBytesInBuffer':args=[SB]
 if name=='xStreamBufferGenericCreate':args=[f['size'],f.get('trigger',1),f.get('message',0),0];w(0x200ff000,0)
 if name=='prvWriteBytesToBuffer':args=[SB,SRC,f.get('n',3),f.get('head',0)]
 if name=='am_hal_uart_fifo_read':args=[UART,SRC if f.get('dest',1) else 0,f.get('n',3),OUT]
 for r,a in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],args):u.reg_write(r,a)
 stop=[];calls=[];nativepcs=set();rx=iter(f.get('fifo',[65,66,67]));current=[None];reads=[]
 def readhook(uc,access,a,size,value,user):
  if a==0x4003a018:
   if current[0] is None:current[0]=next(rx,None)
   w(a,0x10 if current[0] is None else 0)
  elif a==0x4003a000:
   x=current[0];w(a,0 if x is None else x);reads.append(x);current[0]=None
 def hook(uc,pc,size,user):
  if pc==0x456110:
   count=uc.reg_read(UC_ARM_REG_R0);calls.append({'malloc':count})
   if f.get('cut_malloc'):stop.append('malloc-boundary');uc.emu_stop();return
   uc.reg_write(UC_ARM_REG_R0,SB);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
  if pc==0x455dc0:
   sp=uc.reg_read(UC_ARM_REG_SP);previous=int.from_bytes(uc.mem_read(sp,4),'little');woken=int.from_bytes(uc.mem_read(sp+4,4),'little');calls.append({'notify':{'task':hex(uc.reg_read(UC_ARM_REG_R0)),'index':uc.reg_read(UC_ARM_REG_R1),'value':uc.reg_read(UC_ARM_REG_R2),'action':uc.reg_read(UC_ARM_REG_R3),'previous':previous,'woken_nonnull':bool(woken)},'basepri':uc.reg_read(UC_ARM_REG_BASEPRI)})
   if f.get('cut_notify'):stop.append('notify-boundary');uc.emu_stop();return
   if woken:w(woken,1)
   uc.reg_write(UC_ARM_REG_R0,1);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
  if pc==0x10fff0:stop.append('assert-boundary');uc.emu_stop();return
  if pc==0x10ff00:stop.append('return');uc.emu_stop();return
  if native:assert 0x100000<=pc<0x102000,hex(pc);nativepcs.add(pc)
 u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_READ,readhook);u.reg_write(UC_ARM_REG_PC,(syms[name] if native else bind[name])|1);steps=0
 while not stop:
  u.emu_start(u.reg_read(UC_ARM_REG_PC)|1,0,count=1);steps+=1;assert steps<200000
 return {'stop':stop,'return':u.reg_read(UC_ARM_REG_R0) if stop==['return'] else None,'control_hex':bytes(u.mem_read(SB,36)).hex(),'data_hex':bytes(u.mem_read(DATA,128)).hex(),'allocated_following_control_hex':bytes(u.mem_read(SB+36,min(f.get('size',0)+1,4096))).hex() if name=='xStreamBufferGenericCreate' else None,'source_hex':bytes(u.mem_read(SRC,256)).hex(),'out':int.from_bytes(u.mem_read(OUT,4),'little'),'basepri':u.reg_read(UC_ARM_REG_BASEPRI),'calls':calls,'fifo_reads':reads},nativepcs
if __name__=='__main__':
 cases=[]
 for head,tail,n,message,waiter,trigger in itertools.product([0,1,31],[0,1,17,31],[0,1,3,20,40],[0,1],[0,0x20039000],[1,16]):cases.append(('xStreamBufferSendFromISR',{'head':head,'tail':tail,'n':n,'message':message,'waiter':waiter,'trigger':trigger}))
 for head,tail in itertools.product([0,1,31],[0,1,17,31]):
  cases.append(('xStreamBufferSpacesAvailable',{'head':head,'tail':tail}));cases.append(('prvBytesInBuffer',{'head':head,'tail':tail}))
 for n,head in itertools.product([1,3,20,32],[0,1,31]):cases.append(('prvWriteBytesToBuffer',{'n':n,'head':head}))
 for size,message,trigger in itertools.product([1,4,8,2048],[0,1],[0,1]):
  if message and size<=4:continue
  cases.append(('xStreamBufferGenericCreate',{'size':size,'message':message,'trigger':trigger}))
 for size in [0xffffffdb,0xffffffff]:cases.append(('xStreamBufferGenericCreate',{'size':size}))
 cases.append(('xStreamBufferSendFromISR',{'waiter':0x20039000,'cut_notify':True,'n':3}));cases.append(('xStreamBufferGenericCreate',{'size':2048,'cut_malloc':True}))
 for fifo,n,dest in itertools.product([[],[65],[65,66,67],[65,0x141,66]],[0,1,3,16],[0,1]):cases.append(('am_hal_uart_fifo_read',{'fifo':fifo,'n':n,'dest':dest}))
 rows=[];pcs=set()
 for name,f in cases:
  a,_=run(name,f,False);b,seen=run(name,f,True);assert a==b,(name,f,{k:(a[k],b[k]) for k in a if a[k]!=b[k]});rows.append({'function':name,'fixture':f,'observed':a});pcs|=seen
 (D/'results.json').write_text(json.dumps({'status':'PASS','cases':len(rows),'elf_sha256':hashlib.sha256(elf.read_bytes()).hexdigest(),'raw_sha256':hashlib.sha256(raw).hexdigest(),'bindings':{k:hex(a) for k,a in bind.items()},'comparisons':rows,'native_addresses':sorted(map(hex,pcs)),'limits':'Instruction-stepped original versus selected source. Heap provider and task notification cut or explicitly stubbed; synthetic FIFO byte/status reads. No task handover/ISR vector/hardware RX proof.'},indent=2)+'\n');print('PASS',len(rows),'nativePCs',len(pcs))
