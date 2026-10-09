from pathlib import Path
import json,struct,subprocess,itertools,hashlib
from unicorn import *
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
D=Path(__file__).resolve().parent;R=D.parents[2];rec=json.loads((D/'reproduction-receipt.json').read_text());elf=Path(rec['elf']);raw=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];syms={l.split()[2]:int(l.split()[0],16) for l in subprocess.check_output([str(Path(rec['gcc']).with_name('arm-none-eabi-nm')),str(elf)],text=True).splitlines() if len(l.split())==3};sections=[]
with elf.open('rb') as f:
 for s in ELFFile(f).iter_sections():
  if s['sh_flags']&2 and s['sh_size']:sections.append((s['sh_addr'],s.data()))
DESC=0x20000d2c;STATE=0x20040000;PINS=0x20041000;CONFIG=0x20042000;Q=0x20073ed4;BUF=0x200731b0;INIT=0x20075014;OPEN=INIT+1;SRC=0x20044000
bind={'codec_ring_initialize':0x598160,'codec_channel_callback':0x55e8f0,'codec_channel_enable':0x55e5bc,'codec_channel_disable':0x55e630,'codec_channel_baud':0x55e898,'codec_uart_initialize':0x58fb52,'codec_uart_close':0x58fc0c,'codec_uart_baud':0x58fab6,'codec_host_initialize':0x57ba88,'codec_rx_callback':0x58fb1c,'codec_uart_read':0x58fb2a}
def run(f,native):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x438000,0x360000);u.mem_write(0x438000,raw);u.mem_map(0x100000,0x10000)
 for a,b in sections:u.mem_write(a,b)
 u.mem_map(0x20000000,0x100000)
 def w(a,*v):u.mem_write(a,struct.pack('<'+'I'*len(v),*v))
 for ch in range(4):
  d=DESC+28*ch;w(d+4,STATE+ch*0x100);w(d+8,PINS+ch*16);w(d+12,CONFIG+ch*16);w(d+20,0xabcdef01);u.mem_write(d+24,bytes([f.get('active',1),0]));w(PINS+ch*16,10+ch,20+ch,0x11110000+ch,0x22220000+ch);w(CONFIG+ch*16,921600,0x12345678,0x23456789,0x34567890)
 w(Q,BUF,63,2,5);u.mem_write(BUF,b'\xa5'*64);u.mem_write(INIT,bytes([f.get('initialized',1),f.get('open',0)]));u.mem_write(SRC,b'\x10\x20\x30');u.mem_write(0x20045000,b'\xee'*32);events=[];writes=[];stop=[];current=['']
 def logical(v):return 'codec-rx-callback' if v in (0x58fb1d,syms['codec_rx_callback']|1) else v
 def ret(v=0):u.reg_write(UC_ARM_REG_R0,v);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
 def hook(uc,pc,n,user):
  if pc==0x43d0ce:ret();return
  if pc==0x58dbb8:
   args=[uc.reg_read(x) for x in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2]];status=f.get('enable_result',0) if args[1]==0 else f.get('disable_result',0);events.append(['power',*args,'result',status]);ret(status);return
  if pc==0x480f0c:
   args=[uc.reg_read(x) for x in [UC_ARM_REG_R0,UC_ARM_REG_R1]];events.append(['gpio',*args]);ret(f.get('gpio_result',0));return
  if pc==0x58e09e:
   handle=uc.reg_read(UC_ARM_REG_R0);ptr=uc.reg_read(UC_ARM_REG_R1);events.append(['configure',handle,bytes(uc.mem_read(ptr,16)).hex()]);ret(f.get('configure_result',0));return
  if pc==0x10ff00:stop.append('return');uc.emu_stop();return
  if native:assert 0x100000<=pc<0x110000,hex(pc)
 def mem(uc,access,a,n,v,user):
  if Q<=a<Q+16 or INIT<=a<INIT+2 or DESC<=a<DESC+112:writes.append([current[0],hex(a),n,logical(v)])
 u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_WRITE,mem)
 def snapshot():
  desc=[]
  for ch in range(4):
   d=bytearray(u.mem_read(DESC+28*ch,28));cb=struct.unpack_from('<I',d,20)[0];struct.pack_into('<I',d,20,0);desc.append({'bytes_without_callback':d.hex(),'callback':logical(cb)})
  return {'flags':bytes(u.mem_read(INIT,2)).hex(),'ring':bytes(u.mem_read(Q,16)).hex(),'ring_bytes':bytes(u.mem_read(BUF,64)).hex(),'descriptors':desc,'configurations':bytes(u.mem_read(CONFIG,64)).hex(),'read_output':bytes(u.mem_read(0x20045000,32)).hex()}
 phases=[]
 for name in f['sequence']:
  current[0]=name;stop.clear();u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x10ff01)
  args=[]
  if name=='codec_ring_initialize':args=[Q,BUF,f['size']]
  if name=='codec_channel_callback':args=[f['channel'],f['callback']]
  if name in ('codec_channel_enable','codec_channel_disable'):args=[f['channel']]
  if name=='codec_channel_baud':args=[f['channel'],f['baud']]
  if name=='codec_uart_baud':args=[f['baud']]
  if name=='codec_rx_callback':args=[SRC,3]
  if name=='codec_uart_read':args=[0x20045000,32]
  for reg,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2],args):u.reg_write(reg,v)
  u.reg_write(UC_ARM_REG_PC,(syms[name] if native else bind[name])|1)
  for _ in range(20000):
   if stop:break
   u.emu_start(u.reg_read(UC_ARM_REG_PC)|1,0,count=1)
  assert stop,(f,native,name,hex(u.reg_read(UC_ARM_REG_PC)))
  phases.append({'function':name,'return':None if name in ('codec_ring_initialize','codec_channel_callback','codec_rx_callback') else u.reg_read(UC_ARM_REG_R0),'state':snapshot()})
 return {'phases':phases,'provider_events':events,'ordered_state_writes':writes}
cases=[]
for init,op,en,dis,cfg in itertools.product([0,1],[0,1],[0,7],[0,7],[0,7]):
 f=dict(initialized=init,open=op,enable_result=en,disable_result=dis,configure_result=cfg)
 for seq in [['codec_host_initialize'],['codec_uart_close'],['codec_uart_initialize','codec_rx_callback','codec_uart_close','codec_uart_initialize','codec_uart_read'],['codec_host_initialize','codec_uart_close','codec_host_initialize']]:cases.append({**f,'sequence':seq})
for ch,active,result in itertools.product([0,3,4,259],[0,1,2],[0,7]):
 for name in ['codec_channel_enable','codec_channel_disable','codec_channel_baud']:
  cases.append(dict(sequence=[name],channel=ch,active=active,enable_result=result,disable_result=result,configure_result=result,baud=115200,gpio_result=7))
for ch,cb in itertools.product([0,3,4,259],[0,0x58fb1d]):cases.append(dict(sequence=['codec_channel_callback'],channel=ch,callback=cb))
for size in [0,1,2,64,128]:cases.append(dict(sequence=['codec_ring_initialize'],size=size))
rows=[];diff=[]
for f in cases:
 a=run(f,False);b=run(f,True)
 if a!=b:diff.append({'fixture':f,'differences':{k:{'stock':a[k],'source':b[k]} for k in a if a[k]!=b[k]}})
 rows.append({'fixture':f,'observed':a,'matches':a==b})
(D/'results.json').write_text(json.dumps({'status':'PASS' if not diff else 'DIFFERENCES','cases':len(rows),'elf_sha256':hashlib.sha256(elf.read_bytes()).hexdigest(),'raw_sha256':hashlib.sha256(raw).hexdigest(),'bindings':{k:hex(v) for k,v in bind.items()},'comparisons':rows,'differences':diff,'limits':'Native lifecycle/ring source; diagnostic disabled. GPIO/power/configure status providers synthetic. Callback addresses normalized as relocatable interfaces. Callback invocation explicit, not IRQ delivery. No hardware power/quiescence/physical baud proof.'},indent=2)+'\n');print('CASES',len(rows),'DIFFERENCES',len(diff))
