from pathlib import Path
import json,struct,subprocess,itertools,hashlib,zlib
from unicorn import *
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
D=Path(__file__).resolve().parent;R=D.parents[2];rec=json.loads((D/'reproduction-receipt.json').read_text());elf=Path(rec['elf']);raw=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];syms={l.split()[2]:int(l.split()[0],16) for l in subprocess.check_output([str(Path(rec['gcc']).with_name('arm-none-eabi-nm')),str(elf)],text=True).splitlines() if len(l.split())==3};sections=[]
with elf.open('rb') as f:
 for s in ELFFile(f).iter_sections():
  if s['sh_flags']&2 and s['sh_size']:sections.append((s['sh_addr'],s.data()))
SRC=0x20042000;WIRE=0x20041000;LEN=0x20044000;STATE=0x20040000;QBUF=0x20043000;SEQ=0x20075013;SEND=0x2007399c
bind={'codec_pack':0x57bb0a,'codec_send':0x57c0d6,'codec_uart_tx':0x58fb38,'codec_channel_tx':0x55e7fa,'codec_roundtrip':0x57bb0a}
allowed=[]
for line in (R/'g2/research/corpus/apollo-main/ghidra/open-2026-09-29/functions-000.jsonl').read_text().splitlines():
 d=json.loads(line)
 if d['entry'] in {'0055e7fa','0048949c','0058e3f8','00491102'}:allowed.extend((int(a,16),int(b,16)+1) for a,b in d['ranges'])
allowed.append((0x4d555c,0x4d558e))
def run(name,f,native):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x438000,0x360000);u.mem_write(0x438000,raw);u.mem_map(0x100000,0x10000)
 for a,b in sections:u.mem_write(a,b)
 u.mem_map(0x20000000,0x100000);u.mem_map(0x40039000,0x4000)
 def w(a,v):u.mem_write(a,struct.pack('<I',v))
 payload=bytes(range(min(f['length'],32)));u.mem_write(SRC,payload+b'\xcc'*(64-len(payload)));u.mem_write(WIRE,b'\xa5'*64);u.mem_write(SEND,b'\xa5'*64);u.mem_write(LEN,b'\xee\xee');u.mem_write(SEQ,bytes([f.get('sequence',0)]))
 sp=0x200ff000;args=[0x12ab,0xcd34,0 if f.get('nullbody') else SRC,f['length']];u.mem_write(sp,struct.pack('<3I',f['flag'],0 if f.get('nullwire') else WIRE,0 if f.get('nulllen') else LEN))
 if name=='codec_send':u.mem_write(sp,struct.pack('<I',f['flag']))
 if name=='codec_channel_tx':args=[f.get('channel',3),WIRE,f['length']]
 if name=='codec_uart_tx':args=[WIRE,f['length']];u.mem_write(WIRE,payload+b'\xa5'*(64-len(payload)))
 if name not in ('codec_pack','codec_roundtrip'):
  w(0x4003c018,0x20 if f.get('fifo_full') else 0)
  w(STATE,0 if f.get('invalid_handle') else 0x1ea9e06);w(STATE+0x28,3);w(0x20000d2c+3*28+4,STATE);u.mem_write(0x20000d2c+3*28+24,bytes([f.get('enabled',1)]));w(STATE+0x34+12,1024);w(STATE+0x34+16,1);w(STATE+0x34+20,QBUF);u.mem_write(STATE+0xdc,bytes([f.get('queued',1)]));u.mem_write(STATE+0x119,bytes([f.get('busy',0)]))
 for reg,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],args):u.reg_write(reg,v)
 u.reg_write(UC_ARM_REG_SP,sp);u.reg_write(UC_ARM_REG_LR,0x10ff01);u.reg_write(UC_ARM_REG_PRIMASK,f.get('primask',0));stop=[];fifo=[];delay=[];trace=[];submitted=[];heap_events=[]
 def ret(v=0):u.reg_write(UC_ARM_REG_R0,v);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
 def mem(uc,access,a,n,v,user):
  if a==0x4003c000:fifo.append(v&255)
  if 0x40039000<=a<0x4003d000:trace.append(['W' if access==UC_MEM_WRITE else 'R',hex(a),n,v if access==UC_MEM_WRITE else int.from_bytes(uc.mem_read(a,n),'little')])
 def hook(uc,pc,n,user):
  if pc==0x474cd2:
   heap_events.append(['allocate',uc.reg_read(UC_ARM_REG_R0)]);ret(0 if f.get('allocfail') else 0x20046000);return
  if pc==0x474d16:heap_events.append(['free',uc.reg_read(UC_ARM_REG_R0)]);ret();return
  if pc==0x43d0ce:ret();return
  if pc==0x43dacc:ret();return
  if native and pc==0x58e454:uc.reg_write(UC_ARM_REG_PC,syms['blocking_write']|1);return
  if pc==0x4807a0:
   delay.append(uc.reg_read(UC_ARM_REG_R0))
   if f.get('completion') and delay[-1]==10:uc.mem_write(0x20000d2c+3*28+25,b'\1')
   ret();return
  if f.get('copycut'):
   dst=uc.reg_read(UC_ARM_REG_R0);count=uc.reg_read(UC_ARM_REG_R2)
   if pc==(syms['copy'] if native else 0x439be4) and dst==WIRE+14 and count==f['length']:stop.append('before-oversize-payload-copy');uc.emu_stop();return
  if pc==0x10ff00:
   if f.get('mutate'):
    submitted.append(bytes(uc.mem_read(SEND,64)).hex());uc.mem_write(SEND,b'\x33'*64)
   stop.append('return');uc.emu_stop();return
  if native:assert 0x100000<=pc<0x110000,hex(pc)
 u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_READ|UC_HOOK_MEM_WRITE,mem);u.reg_write(UC_ARM_REG_PC,(syms['codec_pack' if name=='codec_roundtrip' else name] if native else bind[name])|1)
 for _ in range(250000):
  if stop:break
  u.emu_start(u.reg_read(UC_ARM_REG_PC)|1,0,count=1)
 assert stop,(name,f,native,hex(u.reg_read(UC_ARM_REG_PC)))
 roundtrip=[]
 if name=='codec_roundtrip':
  packed=u.reg_read(UC_ARM_REG_R0);roundtrip.append({'pack_return':packed,'packed':bytes(u.mem_read(WIRE,64)).hex()})
  if packed==0:
   if f.get('corrupt')=='header':u.mem_write(WIRE+10,bytes([u.mem_read(WIRE+10,1)[0]^1]))
   if f.get('corrupt')=='body':u.mem_write(WIRE+14,bytes([u.mem_read(WIRE+14,1)[0]^1]))
   stop.clear();u.mem_write(0x20045000,b'\xee'*26);u.mem_write(0x20046000,b'\xdd'*32);u.reg_write(UC_ARM_REG_R0,WIRE);u.reg_write(UC_ARM_REG_R1,int.from_bytes(u.mem_read(LEN,2),'little'));u.reg_write(UC_ARM_REG_R2,0x20045000);u.reg_write(UC_ARM_REG_SP,sp);u.reg_write(UC_ARM_REG_LR,0x10ff01);u.reg_write(UC_ARM_REG_PC,(syms['codec_unpack'] if native else 0x57bd06)|1)
   for _ in range(25000):
    if stop:break
    u.emu_start(u.reg_read(UC_ARM_REG_PC)|1,0,count=1)
   assert stop
   roundtrip.append({'unpack_return':u.reg_read(UC_ARM_REG_R0),'message':bytes(u.mem_read(0x20045000,26)).hex(),'owned_body':bytes(u.mem_read(0x20046000,32)).hex(),'heap_events':heap_events})
 return {'roundtrip':roundtrip,'stop':stop,'return':u.reg_read(UC_ARM_REG_R0) if stop==['return'] else None,'wire':bytes(u.mem_read(WIRE,64)).hex(),'send_buffer':bytes(u.mem_read(SEND,64)).hex(),'length':bytes(u.mem_read(LEN,2)).hex(),'sequence':u.mem_read(SEQ,1)[0],'state':bytes(u.mem_read(STATE,284)).hex(),'queue':bytes(u.mem_read(QBUF,64)).hex(),'completion':u.mem_read(0x20000d2c+3*28+25,1)[0],'fifo':fifo,'delays':delay,'mmio':trace,'submitted_before_mutation':submitted,'primask':u.reg_read(UC_ARM_REG_PRIMASK)}
cases=[]
for n,flag,body,seq in itertools.product([0,1,12,13,16,17],[0,1,2],[0,1],[0,255]):cases.append(('codec_pack',dict(length=n,flag=flag,nullbody=not body,sequence=seq)))
for nw,nl in [(1,0),(0,1)]:cases.append(('codec_pack',dict(length=1,flag=0,nullwire=nw,nulllen=nl)))
for n in [65531,65532,65533,65535]:cases.append(('codec_pack',dict(length=n,flag=1,nullbody=True)))
for n in [65532,65535]:cases.append(('codec_pack',dict(length=n,flag=1,copycut=True)))
for n,flag,enabled,busy,completion,queued in itertools.product([0,12,13,16,17],[0,1],[0,1],[0,1],[0,1],[0,1]):cases.append(('codec_send',dict(length=n,flag=flag,enabled=enabled,busy=busy,completion=completion,queued=queued)))
for n,flag,completion in itertools.product([1,12],[0,1],[0,1]):cases.append(('codec_send',dict(length=n,flag=flag,enabled=1,busy=0,queued=1,fifo_full=True,completion=completion,mutate=True)))
for channel,enabled,invalid in itertools.product([0,3,4,259],[0,1],[0,1]):cases.append(('codec_channel_tx',dict(length=3,flag=0,channel=channel,enabled=enabled,invalid_handle=invalid,queued=1,completion=True)))
for n,flag,nullbody,allocfail,corrupt in itertools.product([0,1,12,16],[0,1],[0,1],[0,1],['valid','header','body']):cases.append(('codec_roundtrip',dict(length=n,flag=flag,nullbody=nullbody,allocfail=allocfail,corrupt=corrupt)))
rows=[];diff=[]
for name,f in cases:
 a=run(name,f,False);b=run(name,f,True)
 if a!=b:diff.append({'function':name,'fixture':f,'differences':{k:{'stock':a[k],'source':b[k]} for k in a if a[k]!=b[k]}})
 if f.get('mutate'):
  prior=bytes.fromhex(a['submitted_before_mutation'][0]);length=14+int.from_bytes(prior[8:10],'little');assert bytes.fromhex(a['queue'])[:length]==prior[:length] and not a['fifo'] and bytes.fromhex(a['send_buffer'])==b'\x33'*64
 rows.append({'function':name,'fixture':f,'observed':a,'matches':a==b})
(D/'results.json').write_text(json.dumps({'status':'PASS' if not diff else 'DIFFERENCES','cases':len(rows),'elf_sha256':hashlib.sha256(elf.read_bytes()).hexdigest(),'raw_sha256':hashlib.sha256(raw).hexdigest(),'comparisons':rows,'differences':diff,'limits':'Logging/diagnostic disabled. Original channel/type wrappers retained; native HAL blocking/FIFO/queue text. Synthetic always-ready UART3 FIFO/delay/marker; oversized-copy cases stop before copy.'},indent=2)+'\n');print('CASES',len(rows),'DIFFERENCES',len(diff))
