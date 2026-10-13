from pathlib import Path
import subprocess,socket,time,xml.etree.ElementTree as ET,struct,json,random,hashlib
from elftools.elf.elffile import ELFFile
from unicorn.arm_const import *
D=Path(__file__).resolve().parent;source=D/'combined-unadmitted.c'
with (D/'probe.elf').open('rb') as f:
 e=ELFFile(f);symbols={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()};assert e.get_section_by_name('.native_main').data()==(D/'oracle-data-bound.bin').read_bytes()
mapping=json.loads((D/'controlled-callees.json').read_text());names=list(mapping)
delta=0x28100000-0x438000
reserve=socket.socket();reserve.bind(('127.0.0.1',0));port=reserve.getsockname()[1];reserve.close()
p=subprocess.Popen(['qemu-system-arm','-M','mps3-an547','-cpu','cortex-m55','-display','none','-monitor','none','-serial','none','-kernel',str(D/'probe.elf'),'-S','-gdb','tcp:127.0.0.1:'+str(port)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
try:
 conn=None
 for _ in range(50):
  try:conn=socket.create_connection(('127.0.0.1',port),timeout=1);break
  except OSError:time.sleep(.05)
 assert conn;conn.settimeout(20)
 def expand(data):
  out=bytearray();i=0
  while i<len(data):
   if data[i]==ord('}'):
    i+=1;out.append(data[i]^32)
   elif data[i]==ord('*'):
    i+=1;out.extend(bytes([out[-1]])*(data[i]-29))
   else:out.append(data[i])
   i+=1
  return out.decode()
 def receive():
  while conn.recv(1)!=b'$':pass
  data=bytearray()
  while True:
   c=conn.recv(1)
   if c==b'#':break
   data.extend(c)
  conn.recv(2);conn.sendall(b'+');return expand(data)
 def command(x):
  data=x.encode();conn.sendall(b'$'+data+b'#'+f'{sum(data)%256:02x}'.encode());return receive()
 def xml(name):
  out='';offset=0
  while True:
   part=command('qXfer:features:read:'+name+':'+hex(offset)[2:]+',1000');assert part[0] in 'ml',part;out+=part[1:];offset+=len(part[1:])
   if part[0]=='l':break
  return ET.fromstring(out.replace("xi:",""))
 registers={};counter=0
 def walk(e):
  global counter
  for child in e:
   tag=child.tag.split('}')[-1]
   if tag=='include':walk(xml(child.attrib['href']))
   elif tag=='reg':
    counter=int(child.attrib.get('regnum',str(counter)));registers[child.attrib['name']]=counter;counter+=1
   else:walk(child)
 walk(xml('target.xml'))
 def reg(name):return bytes.fromhex(command('p'+hex(registers[name])[2:]))
 def sreg(i):
  name='s'+str(i)
  return int.from_bytes(reg(name),'little') if name in registers else int.from_bytes(reg('d'+str(i//2))[4*(i%2):4*(i%2)+4],'little')
 aliases={UC_ARM_REG_R0:'r0',UC_ARM_REG_R1:'r1',UC_ARM_REG_R2:'r2',UC_ARM_REG_R3:'r3',UC_ARM_REG_R4:'r4',UC_ARM_REG_R5:'r5',UC_ARM_REG_R6:'r6',UC_ARM_REG_R7:'r7',UC_ARM_REG_R8:'r8',UC_ARM_REG_R9:'r9',UC_ARM_REG_R10:'r10',UC_ARM_REG_R11:'r11',UC_ARM_REG_SP:'sp',UC_ARM_REG_LR:'lr',UC_ARM_REG_PC:'pc',UC_ARM_REG_CPSR:'xpsr' if 'xpsr' in registers else 'cpsr'}
 class Remote:
  def reg_read(self,r):return int.from_bytes(reg(aliases[r]),'little')
  def reg_write(self,r,v):assert command('P'+hex(registers[aliases[r]])[2:]+'='+int(v).to_bytes(4,'little').hex())=='OK'
  def mem_read(self,address,length):
   data=bytearray()
   for offset in range(0,length,1024):data.extend(bytes.fromhex(command('m'+hex(address+offset)[2:]+','+hex(min(1024,length-offset))[2:])))
   return data
  def mem_write(self,address,data):
   for offset in range(0,len(data),1024):
    part=data[offset:offset+1024];assert command('M'+hex(address+offset)[2:]+','+hex(len(part))[2:]+':'+part.hex())=='OK'
 u=Remote();u.mem_write(0xe000ed88,struct.pack('<I',0x00f00000));targets={}
 for name,address in mapping.items():targets[symbols[name]&~1]=name;targets[address+delta]=name
 for address in targets:assert command('Z1,'+hex(address)[2:]+',2')=='OK'
 stop_address=symbols['probe_stop']&~1;assert command('Z1,'+hex(stop_address)[2:]+',2')=='OK'







 FS=0x20003000;LIB=FS+0x100;MEM=FS+0x200;STREAM=FS+0x300;TABLE=FS+0x400;BUFFER=FS+0x500;NEW=FS+0x700;OUT=FS+0x800;FACE=FS+0x900;MODT=FS+0xa00;MODC=FS+0xa40;MODE1=FS+0xa80;MODCID=FS+0xac0;CLST=FS+0xb00;CLSC=FS+0xb40;CLSE1=FS+0xb80;CLSCID=FS+0xbc0;NAMET=FS+0xc00;NAMEC=FS+0xc40;NAMEE1=FS+0xc80;NAMECID=FS+0xcc0;BASE=FS+0xd00
 saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11];seeds=[0x12345000+i*0x101 for i in range(8)]
 def word(a):return struct.unpack('<I',u.mem_read(a,4))[0]
 def put(a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
 def run(entry,initial,case):
  u.mem_write(FS,initial);u.reg_write(UC_ARM_REG_CPSR,0x01000000);u.reg_write(UC_ARM_REG_SP,0x2007ff00);u.reg_write(UC_ARM_REG_LR,stop_address|1)
  for r,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],[LIB,STREAM,TABLE,case['count']]):u.reg_write(r,v&0xffffffff)
  for r,v in zip(saved,seeds):u.reg_write(r,v)
  guard=struct.pack('<II',case['index']&0xffffffff,OUT)+b'\xa5'*24;u.mem_write(0x2007ff00,guard);u.reg_write(UC_ARM_REG_PC,entry&~1);seen=[];allocs=0
  for step in range(16):
   response=command('c');pc=u.reg_read(UC_ARM_REG_PC)
   if pc==stop_address:break
   n=targets.get(pc);assert n,(hex(pc),response);a,b,c,d=[u.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];result=0
   if n=='probe_alloc':
    assert a==MEM;allocs+=1;result=0 if allocs==case['oom'] else (NEW if b==40 else BUFFER);seen.append(('alloc',b,result))
   elif n=='probe_free':assert a==MEM and b in [BUFFER,NEW];seen.append(('free',b));put(b,0xdeadbeef)
   else:
    assert n=='audio_uart_ft_open_face_internal_5264a6' and a==LIB and c==0 and d==OUT;assert word(u.reg_read(UC_ARM_REG_SP))==0;assert word(b)==10 and word(b+16)==NEW;module=word(b+20);assert module in [MODT,MODC,MODE1,MODCID];seen.append(('face',module,case['face_error']));put(NEW+28,MEM);result=case['face_error']
    if result==0:put(OUT,FACE)
   u.reg_write(UC_ARM_REG_R0,result);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR)&~1)
  else:raise AssertionError('call bound')
  assert u.reg_read(UC_ARM_REG_SP)==0x2007ff00 and [u.reg_read(r) for r in saved]==seeds;assert bytes(u.mem_read(0x2007ff00,32))==guard
  snapshot=bytearray(u.mem_read(FS,4096));close=struct.unpack_from('<I',snapshot,NEW-FS+24)[0]
  if close in [0x525b03+delta,symbols['audio_uart_ft_memory_stream_close_525b02']]:struct.pack_into('<I',snapshot,NEW-FS+24,0x525b03)
  return u.reg_read(UC_ARM_REG_R0),seen,bytes(snapshot)
 import itertools
 rng=random.Random(387);count=0
 for index,offset,tag,oom,face_error in itertools.product([0,1],[0,8],[0x54595031,0x43494420],[0,1,2,3,4],[0,2]):
  faces=2;length=32;size=128;otto=False
  initial=bytearray(rng.getrandbits(8) for _ in range(4096));initial[BASE-FS:BASE-FS+128]=bytes(128);struct.pack_into('>I',initial,BASE-FS+offset,length);initial[BASE-FS+offset+4:BASE-FS+offset+8]=b'OTTO' if otto else b'junk';initial[NAMET-FS:NAMET-FS+9]=b'truetype\0';initial[NAMEC-FS:NAMEC-FS+4]=b'cff\0';initial[NAMEE1-FS:NAMEE1-FS+6]=b'type1\0';initial[NAMECID-FS:NAMECID-FS+4]=b'cid\0';container=struct.pack('>IH',0x74797031,1)+bytes(6)+struct.pack('>4I',tag,0,32,32);initial[BASE-FS+offset+4:BASE-FS+offset+4+len(container)]=container
  for a,v in [(LIB,MEM),(LIB+16,4),(LIB+20,MODT),(LIB+24,MODC),(LIB+28,MODE1),(LIB+32,MODCID),(MODE1,CLSE1),(MODCID,CLSCID),(CLSE1+8,NAMEE1),(CLSCID+8,NAMECID),(MODT,CLST),(MODC,CLSC),(CLST+8,NAMET),(CLSC+8,NAMEC),(MEM+4,symbols['probe_alloc']),(MEM+8,symbols['probe_free']),(STREAM,BASE),(STREAM+4,size),(STREAM+8,31),(STREAM+20,0),(TABLE,offset),(TABLE+4,offset)]:struct.pack_into('<I',initial,a-FS,v)
  case={'index':index,'count':faces,'length':length,'size':size,'offset':offset,'otto':otto,'oom':oom,'face_error':face_error};native=run(0x5260a4+delta,initial,case);candidate=run(symbols['audio_uart_ft_mac_read_sfnt_5260a4'],initial,case);assert native==candidate,(case,native[:2],candidate[:2],[(i,a,b) for i,(a,b) in enumerate(zip(native[2],candidate[2])) if a!=b][:16]);count+=1
  if count%500==0:print('comparisons',count,flush=True)
 receipt={'status':'PASS_SFNT_RESOURCE_CONNECTED_PS_SUCCESS_AND_FALLBACK','comparisons':count,'native_bytes':260,'actual_helpers':['stream seek/read/BE32','PS/SFNT fallback locator/wrapper','module lookup/path compare','selected allocate/zero/free/memcmp','buffer/new-memory/open-memory/close ownership'],'controlled_boundaries':['allocation/free callbacks','main internal face opener'],'checks':['negative complement and index/count bounds','length signed and16MiB limits','PS fallback rewind and short stream','first/second allocation OOM','length>=5 OTTO/cff versus truetype','failed buffer read frees buffer','failed face open closes buffer+stream','whole4KiB/SP/R4-R11/two stacked args/caller guard'],'limits':['Main opener modeled valid FT_Stream_New allocator ownership assignment','Driver parser and initialized runtime/layout/hardware unproven'],'selected':False};(D/'supplement-probe-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
finally:
 p.terminate();p.communicate(timeout=5)
