from pathlib import Path
import json,struct,subprocess,itertools,hashlib,zlib
from unicorn import *
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
D=Path(__file__).resolve().parent;R=D.parents[2];rec=json.loads((D/'reproduction-receipt.json').read_text());elf=Path(rec['elf']);raw=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];syms={l.split()[2]:int(l.split()[0],16) for l in subprocess.check_output([str(Path(rec['gcc']).with_name('arm-none-eabi-nm')),str(elf)],text=True).splitlines() if len(l.split())==3}
with elf.open('rb') as f:
 e=ELFFile(f);sections=[(s['sh_addr'],s.data()) for s in e.iter_sections() if s['sh_flags']&2 and s['sh_size']]
DST=0x20040000;MSG=DST+0x100;HEAP=DST+0x200;Q=0x20073ed4;BUF=0x200731b0
bind={'codec_unpack':0x57bd06,'codec_crc32':0x4d34c4,'codec_message_free':0x57c640,'codec_response_read':0x57c1fc,'codec_read_uart_data':0x57c442,'codec_sendwait_composition':0x57c512}
def frame(body=b'',flag=0,declared=None,magic=b'BUXX',badhead=False,badbody=False):
 trailer=struct.pack('<I',zlib.crc32(body)^(1 if badbody else 0)) if flag&1 else b''
 n=len(body)+len(trailer) if declared is None else declared
 h=magic+struct.pack('<HBBH',0x1234,7,flag,n)
 return h+struct.pack('<I',zlib.crc32(h)^(1 if badhead else 0))+body+trailer

def run(name,f,native):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x438000,0x360000);u.mem_write(0x438000,raw);u.mem_map(0x100000,0x10000)
 for a,b in sections:u.mem_write(a,b)
 u.mem_map(0x20000000,0x100000);wire=bytes.fromhex(f.get('wire',''));u.mem_write(DST,b'\xcc'*256);u.mem_write(MSG,b'\xa5'*26);u.mem_write(HEAP,b'\xdd'*32)
 if wire:u.mem_write(DST,wire)
 args=[DST,f.get('available',len(wire)),MSG]
 if name=='codec_crc32':
  u.mem_write(MSG,struct.pack('<I',f.get('previous',0)));args=[DST,len(wire),MSG if 'previous' in f else 0]
 if name=='codec_message_free':
  m=bytearray(b'\xa5'*26);struct.pack_into('<I',m,14,HEAP if f.get('owned',True) else 0);u.mem_write(MSG,bytes(m));args=[0 if f.get('null') else MSG]
 if name=='codec_unpack':args=[0 if f.get('nullwire') else DST,f.get('available',len(wire)),0 if f.get('nullmessage') else MSG]
 if name in ('codec_response_read','codec_read_uart_data'):
  u.mem_write(DST,b'\xcc'*256);u.mem_write(BUF,wire);u.mem_write(Q,struct.pack('<4I',BUF,63,0,len(wire) if f['arrival']==0 else 0));args=[0 if f.get('null') else DST,f['capacity'],f['timeout']]
  if name=='codec_read_uart_data':args=[args[0],args[1],0 if f.get('null_length') else MSG,f['timeout']]
 if name=='codec_sendwait_composition':
  u.mem_write(0x2007397c,b'\xcc'*64);u.mem_write(BUF,wire);u.mem_write(Q,struct.pack('<4I',BUF,63,0,len(wire) if f['arrival']==0 else 0));args=[0x12,0x34,0,0];u.mem_write(0x200ff000,struct.pack('<3I',0,MSG,f['timeout']))
 for reg,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],args):u.reg_write(reg,v)
 u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x10ff01);tick=[f.get('start',0)];reads=[];delays=[];heap=[];stop=[];crc=[];transport=[]
 def ret(v=None):
  if v is not None:u.reg_write(UC_ARM_REG_R0,v)
  u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
 def hook(uc,pc,size,user):
  if name=='codec_sendwait_composition':
   if pc in (0x57ba88,0x57c0d6,0x57baec):
    transport.append({0x57ba88:'host-init',0x57c0d6:'send',0x57baec:'cleanup'}[pc]);ret(f.get('sendfail',0) if pc==0x57c0d6 else 0);return
   if native and pc in (0x57c442,0x57bd06):
    uc.reg_write(UC_ARM_REG_PC,syms['codec_read_uart_data' if pc==0x57c442 else 'codec_unpack']|1);return
  if pc==0x43d0ce:ret(0);return
  if pc==0x43dacc:ret();return # disabled diagnostic sink, not validation
  if pc==0x474cd2:
   heap.append(['allocate',uc.reg_read(UC_ARM_REG_R0)]);ret(0 if f.get('allocfail') else HEAP);return
  if pc==0x474d16:heap.append(['free',uc.reg_read(UC_ARM_REG_R0)]);ret();return
  if pc==0x4490cc:reads.append(tick[0]);uc.reg_write(UC_ARM_REG_R1,0xbadbad);ret(tick[0]);return
  if pc==0x449376:
   delays.append(uc.reg_read(UC_ARM_REG_R0));assert delays[-1]==1
   if len(delays)>=8:stop.append('before-delay-budget-cut');uc.emu_stop();return
   tick[0]=(tick[0]+1)&0xffffffff
   if len(delays)==f['arrival']:uc.mem_write(Q+12,struct.pack('<I',len(wire)))
   ret(0);return
  if pc==0x10ff00:stop.append('return');uc.emu_stop();return
  if native:assert 0x100000<=pc<0x110000 or 0x58fac8<=pc<0x58fad2 or (name=='codec_sendwait_composition' and 0x57c512<=pc<0x57c618),hex(pc)
 u.hook_add(UC_HOOK_CODE,hook);u.reg_write(UC_ARM_REG_PC,(syms[name] if native and name!='codec_sendwait_composition' else bind[name])|1)
 for _ in range(25000):
  if stop:break
  u.emu_start(u.reg_read(UC_ARM_REG_PC)|1,0,count=1)
 assert stop,(name,f,native,hex(u.reg_read(UC_ARM_REG_PC)))
 return {'stop':stop,'return':u.reg_read(UC_ARM_REG_R0) if stop==['return'] and name!='codec_message_free' else None,'message':bytes(u.mem_read(MSG,26)).hex(),'destination':bytes(u.mem_read(DST,64)).hex(),'heap':bytes(u.mem_read(HEAP,32)).hex(),'heap_events':heap,'tick_reads':reads,'delays':delays,'ring':bytes(u.mem_read(Q,16)).hex(),'transport_events':transport,'response_store':bytes(u.mem_read(0x2007397c,64)).hex()}
cases=[]
for n,flag,mutation in itertools.product([0,1,2,16,17],[0,1],['valid','magic','header','body','short','allocfail']):
 wire=frame(bytes(range(n)),flag,magic=b'BUXY' if mutation=='magic' else b'BUXX',badhead=mutation=='header',badbody=mutation=='body')
 cases.append(('codec_unpack',dict(wire=wire.hex(),available=len(wire)-(1 if mutation=='short' else 0),allocfail=mutation=='allocfail')))
for n in [0,1,2,3,65522,65535]:cases.append(('codec_unpack',dict(wire=frame(flag=1,declared=n).hex(),available=64)))
for nullwire,nullmessage in [(True,False),(False,True)]:cases.append(('codec_unpack',dict(wire=frame().hex(),nullwire=nullwire,nullmessage=nullmessage)))
for data in [b'',b'123456789',bytes(range(256)),b'\xff'*31]:
 for previous in [None,0,0x12345678,0xffffffff]:
  f={'wire':data.hex()}
  if previous is not None:f['previous']=previous
  cases.append(('codec_crc32',f))
for owned,null in itertools.product([False,True],[False,True]):cases.append(('codec_message_free',dict(owned=owned,null=null)))
for body,start,timeout,arrival,capacity in itertools.product([b'',b'\x01\x02',bytes(range(16))],[0,0xfffffffe],[0,1,5],[-1,0,1,3],[1,14,30]):
 cases.append(('codec_response_read',dict(wire=frame(body).hex(),start=start,timeout=timeout,arrival=arrival,capacity=capacity)))
for declared,capacity in itertools.product([2,65535],[0,1,14,30]):
 cases.append(('codec_response_read',dict(wire=frame(declared=declared).hex(),start=0,timeout=3,arrival=0,capacity=capacity)))
for null,null_length,arrival in itertools.product([False,True],[False,True],[-1,0,1]):
 cases.append(('codec_read_uart_data',dict(wire=frame(b'AB').hex(),start=0,timeout=3,arrival=arrival,capacity=30,null=null,null_length=null_length)))
for flag,mutation,arrival,sendfail in itertools.product([0,1],['valid','header','body'],[0,1,-1],[0,-1]):
 cases.append(('codec_sendwait_composition',dict(wire=frame(b'AB',flag,badhead=mutation=='header',badbody=mutation=='body').hex(),start=0,timeout=3,arrival=arrival,sendfail=sendfail)))
rows=[];diff=[]
for name,f in cases:
 a=run(name,f,False);b=run(name,f,True)
 if a!=b:diff.append({'function':name,'fixture':f,'differences':{k:{'stock':a[k],'source':b[k]} for k in a if a[k]!=b[k]}})
 if name=='codec_crc32':assert a['return']==zlib.crc32(bytes.fromhex(f['wire']),f.get('previous',0))
 rows.append({'function':name,'fixture':f,'observed':a,'matches':a==b})
(D/'results.json').write_text(json.dumps({'status':'PASS' if not diff else 'DIFFERENCES','cases':len(rows),'elf_sha256':hashlib.sha256(elf.read_bytes()).hexdigest(),'raw_sha256':hashlib.sha256(raw).hexdigest(),'bindings':{k:hex(v) for k,v in bind.items()},'comparisons':rows,'differences':diff,'limits':'Actual CRC/magic/copy original instructions. Logging disabled; diagnostics/heap/kernel tick/delay/arrival synthetic. Caller buffers deliberately large even when advertised capacity small. No actual allocator or scheduler/device response.'},indent=2)+'\n');print('CASES',len(rows),'DIFFERENCES',len(diff))
