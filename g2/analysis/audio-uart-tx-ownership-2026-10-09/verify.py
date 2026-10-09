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
bind={'write_transaction_save':0x58def2,'am_hal_uart_fifo_write':0x58e31e,'tx_queue_update':0x58e3a0,'nonblocking_write_sm':0x58e534,'nonblocking_write':0x58e4e8,'blocking_write':0x58e454,'am_hal_queue_item_add':0x530084,'am_hal_queue_item_get':0x5300e2,'am_hal_uart_buffer_configure':0x58ddd6,'am_hal_queue_init':0x53006c,'am_hal_uart_initialize':0x58dae4}
STATE=0x20040000;TX=0x20041000;SRC=0x20042000;QBUF=0x20043000;OUT=0x20044000

def run(name,f,native):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x438000,0x360000);u.mem_write(0x438000,raw);u.mem_map(0x100000,0x10000)
 for a,b in sections:u.mem_write(a,b)
 u.mem_map(0x20000000,0x100000);u.mem_map(0x40039000,0x1000)
 def w(a,v):u.mem_write(a,struct.pack('<I',v))
 data=bytes((i*17+3)&255 for i in range(f.get('length',3)));u.mem_write(SRC,data+bytes(256-len(data)));u.mem_write(QBUF,b'\xa5'*512)
 w(STATE,0x1ea9e06);w(STATE+0x28,0);q=[f.get('write_index',0),f.get('read_index',0),f.get('occupied',0),f.get('capacity',8),f.get('item_size',1),QBUF]
 u.mem_write(STATE+0x34,struct.pack('<6I',*q));w(OUT,0xeeeeeeee)
 fields=[SRC,len(data),OUT,f.get('timeout',0),0x10ff11 if f.get('callback',0) else 0,0x12345678,0]+[0]*6
 u.mem_write(TX,struct.pack('<13I',*fields)+bytes([f.get('type',0),0,0,0]));u.mem_write(STATE+0xa0,bytes(u.mem_read(TX,56)));w(STATE+0xd8,f.get('written',0));u.mem_write(STATE+0xdc,bytes([f.get('queued',0)]));u.mem_write(STATE+0x119,bytes([f.get('writing',1 if name=='nonblocking_write_sm' else 0)]))
 budget=f.get('fifo_budget',1000);remaining=[budget];w(0x40039018,0x20 if budget==0 else 0)
 args=[STATE,TX]
 if name=='am_hal_uart_initialize':
  w(OUT,STATE if f.get('existing',0) else 0);w(STATE,f.get('prefix',0));args=[f.get('module',0),OUT if f.get('outptr',1) else 0]
 if name=='am_hal_uart_buffer_configure':
  args=[STATE if f.get('valid',1) else 0,QBUF if f.get('txptr',1) else 0,f.get('txsize',8),QBUF+256 if f.get('rxptr',1) else 0];w(0x200ff000,f.get('rxsize',8))
 if name=='am_hal_queue_init':args=[STATE+0x34,QBUF,f.get('item_size',1),f.get('capacity',8)]
 if name=='am_hal_uart_fifo_write':args=[STATE,SRC,len(data),OUT]
 elif name.startswith('am_hal_queue_item'):args=[STATE+0x34,SRC,f.get('items',len(data))]
 for reg,val in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],args):u.reg_write(reg,val)
 u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x10ff01);u.reg_write(UC_ARM_REG_PRIMASK,f.get('primask',0));writes=[];callbacks=[];delays=[];stop=[];nativepcs=set()
 def memhook(uc,access,a,size,value,user):
  if a==0x40039000:
   writes.append(value&255);remaining[0]-=1
   if remaining[0]==0:w(0x40039018,0x20)
 def hook(uc,pc,size,user):
  if pc==0x4807a0:
   delays.append(uc.reg_read(UC_ARM_REG_R0))
   if f.get('stall_cut') and len(delays)>=f['stall_cut']:stop.append('stalled-before-delay');uc.emu_stop();return
   if f.get('release_on_delay'):remaining[0]=f.get('release_budget',1000);w(0x40039018,0)
   uc.reg_write(UC_ARM_REG_R0,0);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
  if pc==0x10ff10:
   callbacks.append({'status':uc.reg_read(UC_ARM_REG_R0),'context':uc.reg_read(UC_ARM_REG_R1),'primask':uc.reg_read(UC_ARM_REG_PRIMASK)})
   uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
  if pc==0x10ff00:stop.append('return');uc.emu_stop();return
  if native:assert 0x100000<=pc<0x101000,hex(pc);nativepcs.add(pc)
 u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_WRITE,memhook);u.emu_start((syms[name] if native else bind[name])|1,0,count=1000000)
 assert stop,(name,f,native)
 return {'stop':stop,'return':None if name in ('nonblocking_write_sm','am_hal_queue_init') else u.reg_read(UC_ARM_REG_R0),'all_uart_states_hex':bytes(u.mem_read(0x2006a02c,4*284)).hex(),'state_hex':bytes(u.mem_read(STATE,284)).hex(),'queue_bytes_hex':bytes(u.mem_read(QBUF,512)).hex(),'out':int.from_bytes(u.mem_read(OUT,4),'little'),'source_hex':bytes(u.mem_read(SRC,256)).hex(),'fifo_bytes':writes,'callbacks':callbacks,'delay_arguments':delays,'primask':u.reg_read(UC_ARM_REG_PRIMASK)},nativepcs
if __name__=='__main__':
 cases=[]
 for name in ['nonblocking_write','blocking_write','nonblocking_write_sm']:
  for n,queued,cap,budget,cb in itertools.product([0,1,3,32,65,205],[0,1],[8,256],[0,2,1000],[0,1]):
   f={'length':n,'queued':queued,'capacity':cap,'fifo_budget':budget,'callback':cb,'writing':1 if name=='nonblocking_write_sm' else 0}
   if name=='blocking_write':f.update(release_on_delay=True,release_budget=1000)
   cases.append((name,f))
 for timeout,queued,release in itertools.product([0,1,2,0xffffffff],[0,1],[False,True]):cases.append(('blocking_write',{'length':65,'queued':queued,'capacity':8,'fifo_budget':0,'timeout':timeout,'release_on_delay':release,'stall_cut':5 if not release and timeout in (0,0xffffffff) else 0}))
 for writing,cb,mask in itertools.product([0,1],[0,1],[0,1]):cases.append(('write_transaction_save',{'writing':writing,'callback':cb,'primask':mask,'length':205}))
 for n,budget in itertools.product([0,1,32,205],[0,2,1000]):cases.append(('am_hal_uart_fifo_write',{'length':n,'fifo_budget':budget}))
 for name in ['am_hal_queue_item_add','am_hal_queue_item_get']:
  for capacity,occupied,index,n in itertools.product([8,32],[0,4,8],[0,5],[0,1,4,8]):cases.append((name,{'capacity':capacity,'occupied':occupied,'write_index':index,'read_index':index,'length':n}))
 for valid,txptr,txsize,rxptr,rxsize in itertools.product([0,1],[0,1],[0,8],[0,1],[0,16]):cases.append(('am_hal_uart_buffer_configure',{'valid':valid,'txptr':txptr,'txsize':txsize,'rxptr':rxptr,'rxsize':rxsize}))
 for capacity,item in itertools.product([0,8,32],[1,4]):cases.append(('am_hal_queue_init',{'capacity':capacity,'item_size':item}))
 for module,outptr,existing,prefix in itertools.product([0,1,3,4],[0,1],[0,1],[0,0xea9e06,0x1ea9e06]):cases.append(('am_hal_uart_initialize',{'module':module,'outptr':outptr,'existing':existing,'prefix':prefix}))
 rows=[];pcs=set()
 for name,fixture in cases:
  a,_=run(name,fixture,False);b,seen=run(name,fixture,True);assert a==b,(name,fixture,{k:(a[k],b[k]) for k in a if a[k]!=b[k]});rows.append({'function':name,'fixture':fixture,'observed':a});pcs|=seen
 (D/'results.json').write_text(json.dumps({'status':'PASS','cases':len(rows),'elf_sha256':hashlib.sha256(elf.read_bytes()).hexdigest(),'raw_sha256':hashlib.sha256(raw).hexdigest(),'bindings':{k:hex(v) for k,v in bind.items()},'comparisons':rows,'reached_native_addresses':sorted(map(hex,pcs)),'limits':'Actual original vs unchanged selected SDK text under stock-layout adapter. Synthetic FIFO full/release timing, callback returns and delay. No UART waveform, concurrency, device state or scheduling proof.'},indent=2)+'\n');print('PASS',len(rows),'PCs',len(pcs))
