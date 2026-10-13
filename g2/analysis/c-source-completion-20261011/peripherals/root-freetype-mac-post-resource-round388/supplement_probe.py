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







 FS=0x20003000;LIB=FS+0x100;MEM=FS+0x200;STREAM=FS+0x300;TABLE=FS+0x400;BUFFER=FS+0x500;NEW=FS+0x700;OUT=FS+0x800;FACE=FS+0x900;MODT=FS+0xa00;MODC=FS+0xa40;CLST=FS+0xb00;CLSC=FS+0xb40;NAMET=FS+0xc00;NAMEC=FS+0xc40;BASE=FS+0xd00
 saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11];seeds=[0x12345000+i*0x101 for i in range(8)]
 def word(a):return struct.unpack('<I',u.mem_read(a,4))[0]
 def put(a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
 def run(entry,initial,case):
  u.mem_write(FS,initial);u.reg_write(UC_ARM_REG_CPSR,0x01000000);u.reg_write(UC_ARM_REG_SP,0x2007ff00);u.reg_write(UC_ARM_REG_LR,stop_address|1)
  for r,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],[LIB,STREAM,TABLE,case['count']]):u.reg_write(r,v&0xffffffff)
  for r,v in zip(saved,seeds):u.reg_write(r,v)
  guard=struct.pack('<II',case['index']&0xffffffff,OUT)+b'\xa5'*24;u.mem_write(0x2007ff00,guard);u.reg_write(UC_ARM_REG_PC,entry&~1);seen=[];allocs=0
  for step in range(32):
   response=command('c');pc=u.reg_read(UC_ARM_REG_PC)
   if pc==stop_address:break
   n=targets.get(pc);assert n,(hex(pc),response,case);a,b,c,d=[u.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];result=0
   if n=='probe_alloc':
    assert a==MEM;allocs+=1;result=0 if allocs==case['oom'] else (BUFFER if allocs==1 else NEW);seen.append(('alloc',b,result))
   elif n=='probe_free':assert a==MEM and b in [BUFFER,NEW];seen.append(('free',b));put(b,0xdeadbeef)
   else:
    assert n=='audio_uart_ft_open_face_internal_5264a6' and a==LIB and c==0 and d==OUT;assert word(u.reg_read(UC_ARM_REG_SP))==0;assert word(b+16)==NEW;module=word(b+20);assert module in [MODT,MODC];seen.append(('face',module,word(b),case['face_error']));put(NEW+28,MEM);result=case['face_error']
    if result==0:put(OUT,FACE)
   u.reg_write(UC_ARM_REG_R0,result);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR)&~1)
  else:raise AssertionError('call bound')
  assert u.reg_read(UC_ARM_REG_SP)==0x2007ff00 and [u.reg_read(r) for r in saved]==seeds,(case,hex(u.reg_read(UC_ARM_REG_PC)),hex(u.reg_read(UC_ARM_REG_SP)),[u.reg_read(r) for r in saved]);assert bytes(u.mem_read(0x2007ff04,28))==guard[4:]
  snapshot=bytearray(u.mem_read(FS,4096));close=struct.unpack_from('<I',snapshot,NEW-FS+24)[0]
  if close in [0x525b03+delta,symbols['audio_uart_ft_memory_stream_close_525b02']]:struct.pack_into('<I',snapshot,NEW-FS+24,0x525b03)
  return u.reg_read(UC_ARM_REG_R0),seen,bytes(snapshot)

 import itertools
 rng=random.Random(3881);count=0
 for index,n,rawlen,size,offset,flag,oom in itertools.product([-1,0,1],[0,1,2], [0,1,2,3,4,8,0x1000000,0x80000000,0xffffffff], [3,4,5,6,7,8,16,32,128], [0,1,64,120], [0,0x100,0x200,0x500], [0,1]):
  if count>=1000:break
  if n==0 and (rawlen!=0 or size!=128 or offset!=0 or flag!=0 or oom!=0):continue
  if index==1 and (n!=1 or rawlen!=3 or size!=16 or offset!=0 or flag!=0x100 or oom!=0):continue
  if n==2 and (rawlen not in [0,3,8,0xffffffff] or size not in [8,32,128] or flag not in [0x100,0x500]):continue
  if rawlen>0xffffff and (size not in [8,32] or offset not in [0,64] or flag not in [0x100,0x500]):continue
  initial=bytearray(rng.getrandbits(8) for _ in range(4096));initial[BASE-FS:BASE-FS+160]=bytes(160)
  struct.pack_into('>IH',initial,BASE-FS+offset,rawlen,flag)
  struct.pack_into('>IH',initial,BASE-FS+64,3,0x200)
  initial[BASE-FS+offset+6:BASE-FS+offset+10]=b'ABCD'
  initial[NAMET-FS:NAMET-FS+6]=b'type1\0'
  for a,v in [(LIB,MEM),(LIB+16,1),(LIB+20,MODT),(MODT,CLST),(CLST+8,NAMET),(MEM+4,symbols['probe_alloc']),(MEM+8,symbols['probe_free']),(STREAM,BASE),(STREAM+4,size),(STREAM+8,0),(STREAM+20,0),(TABLE,offset),(TABLE+4,64)]:struct.pack_into('<I',initial,a-FS,v)
  case={'index':index,'count':n,'oom':oom,'face_error':0,'open_length':0}
  native=run(0x525e16+delta,initial,case);candidate=run(symbols['audio_uart_ft_mac_read_post_525e16'],initial,case)
  assert native==candidate,(case,rawlen,size,offset,flag,native[:2],candidate[:2],[(i,a,b) for i,(a,b) in enumerate(zip(native[2],candidate[2])) if a!=b][:16]);count+=1
  if count%200==0:print('comparisons',count,flush=True)
 receipt={'status':'PASS_POST_RESOURCE_MALFORMED_AND_SHORT_STREAM','comparisons':count,'native_bytes':646,'checks':['zero/one/two resource counts','malformed lengths and signed limits','first/second pass short stream','offset and index gates','whole4KiB/SP/R4-R11/stack arguments'],'selected':False};(D/'supplement-probe-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
finally:
 p.terminate();p.communicate(timeout=5)
