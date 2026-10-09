from pathlib import Path
import json,struct,subprocess,itertools,hashlib
from unicorn import *
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
D=Path(__file__).resolve().parent;R=D.parents[2];rec=json.loads((D/'reproduction-receipt.json').read_text());elf=Path(rec['elf']);raw=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
syms={l.split()[2]:int(l.split()[0],16) for l in subprocess.check_output([str(Path(rec['gcc']).with_name('arm-none-eabi-nm')),str(elf)],text=True).splitlines() if len(l.split())==3};sections=[]
with elf.open('rb') as f:
 for s in ELFFile(f).iter_sections():
  if s['sh_flags']&2 and s['sh_size']:sections.append((s['sh_addr'],s.data()))
DESC=0x20000d2c;HANDLE=0x20044000;RX=0x20045000;STAGING=0x20045100;Q=0x20073ed4;BUF=0x200731b0
def run(f,native):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x438000,0x360000);u.mem_write(0x438000,raw);u.mem_map(0x100000,0x10000)
 for a,b in sections:u.mem_write(a,b)
 u.mem_map(0x20000000,0x100000)
 def w(a,*v):u.mem_write(a,struct.pack('<'+'I'*len(v),*v))
 d=DESC+3*28;w(d+4,HANDLE);w(d+16,RX);w(d+20,(syms['codec_rx_callback']|1) if native and f['callback'] else 0x58fb1d if f['callback'] else 0);u.mem_write(d+24,b'\1\0')
 w(RX+8,f['initial']);w(RX+12,STAGING);u.mem_write(STAGING,bytes(range(0x80,0x80+64)));w(Q,BUF,63,0,0);u.mem_write(BUF,b'\xa5'*64);w(HANDLE,0x1ea9e06);w(HANDLE+40,3)
 u.reg_write(UC_ARM_REG_R0,3);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x10ff01);events=[];stop=[];fifo_call=[0]
 def ret(v=0):u.reg_write(UC_ARM_REG_R0,v);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
 def hook(uc,pc,n,user):
  if pc==0x58e80e:
   out=uc.reg_read(UC_ARM_REG_R1);w(out,f['status']);events.append(['status',uc.reg_read(UC_ARM_REG_R0),f['status'],uc.reg_read(UC_ARM_REG_R2)]);ret(0);return
  if pc==0x58e7e4:events.append(['clear',uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1)]);ret(0);return
  if pc==0x58e860:events.append(['service',uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1)]);ret(1);return
  if pc==0x58e2d8:
   dst=uc.reg_read(UC_ARM_REG_R1);requested=uc.reg_read(UC_ARM_REG_R2);out=uc.reg_read(UC_ARM_REG_R3);count=min(requested,f['fifo_count']);data=bytes((0x30+fifo_call[0]*0x10+i)&255 for i in range(count));u.mem_write(dst,data);w(out,count);events.append(['fifo',dst,requested,count,data.hex()]);fifo_call[0]+=1;ret(0);return
  if pc==0x10ff00:stop.append(1);uc.emu_stop();return
  if native:assert 0x100000<=pc<0x110000,hex(pc)
 u.hook_add(UC_HOOK_CODE,hook);u.reg_write(UC_ARM_REG_PC,(syms['codec_uart_irq'] if native else 0x55e2ce)|1)
 for _ in range(30000):
  if stop:break
  try:u.emu_start(u.reg_read(UC_ARM_REG_PC)|1,0,count=1)
  except UcError as e:
   raise RuntimeError({'native':native,'fixture':f,'pc':hex(u.reg_read(UC_ARM_REG_PC)),'lr':hex(u.reg_read(UC_ARM_REG_LR)),'sp':hex(u.reg_read(UC_ARM_REG_SP)),'events':events}) from e
 assert stop
 callback=struct.unpack_from('<I',u.mem_read(d+20,4))[0]
 return {'return':u.reg_read(UC_ARM_REG_R0),'events':events,'completion':u.mem_read(d+25,1)[0],'rx_count':int.from_bytes(u.mem_read(RX+8,4),'little'),'staging':bytes(u.mem_read(STAGING,64)).hex(),'ring':bytes(u.mem_read(Q,16)).hex(),'ring_bytes':bytes(u.mem_read(BUF,64)).hex(),'callback':'codec-rx' if callback else None}
rows=[];diff=[]
for status,count,initial,callback in itertools.product([0,1,0x10,0x40,0x41,0x50,0x51],[0,1,3,16],[0,2],[0,1]):
 f=dict(status=status,fifo_count=count,initial=initial,callback=callback);a=run(f,False);b=run(f,True)
 if a!=b:diff.append({'fixture':f,'differences':{k:{'stock':a[k],'source':b[k]} for k in a if a[k]!=b[k]}})
 rows.append({'fixture':f,'observed':a,'matches':a==b})
(D/'results.json').write_text(json.dumps({'status':'PASS' if not diff else 'DIFFERENCES','cases':len(rows),'elf_sha256':hashlib.sha256(elf.read_bytes()).hexdigest(),'raw_sha256':hashlib.sha256(raw).hexdigest(),'comparisons':rows,'differences':diff,'limits':'Direct wrapper entry; HAL status/clear/service/FIFO supplied boundaries. Callback executes original/native ring path. No vector/NVIC/physical IRQ delivery.'},indent=2)+'\n');print('CASES',len(rows),'DIFFERENCES',len(diff))
