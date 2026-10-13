from pathlib import Path
import subprocess,socket,time,xml.etree.ElementTree as ET,struct,json,random,hashlib
from elftools.elf.elffile import ELFFile
from unicorn.arm_const import *
D=Path(__file__).resolve().parent;source=D/'combined-unadmitted.c'
with (D/'callback-probe.elf').open('rb') as f:
 e=ELFFile(f);symbols={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()};assert e.get_section_by_name('.native_main').data()==(D/'oracle-data-bound.bin').read_bytes()
mapping={};names=[]
delta=0x28100000-0x438000
reserve=socket.socket();reserve.bind(('127.0.0.1',0));port=reserve.getsockname()[1];reserve.close()
p=subprocess.Popen(['qemu-system-arm','-M','mps3-an547','-cpu','cortex-m55','-display','none','-monitor','none','-serial','none','-kernel',str(D/'callback-probe.elf'),'-S','-gdb','tcp:127.0.0.1:'+str(port)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
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


 u=Remote();u.mem_write(0xe000ed88,struct.pack('<I',0x00f00000));stop_address=symbols['probe_stop']&~1;stub=symbols['probe_read']&~1
 for address in [stop_address,stub]:assert command('Z1,'+hex(address)[2:]+',2')=='OK'
 FS=0x20003000;LIB=FS+0x100;STREAM=FS+0x200;OUT=FS+0x300;NAME=FS+0x400;BASE=FS+0x500
 saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11];seeds=[0x12345000+i*0x101 for i in range(8)]
 def run(entry,initial,case):
  u.mem_write(FS,initial);u.reg_write(UC_ARM_REG_CPSR,0x01000000);u.reg_write(UC_ARM_REG_SP,0x2007ff00);u.reg_write(UC_ARM_REG_LR,stop_address|1)
  for r,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],[LIB,STREAM,NAME,case['magic']]):u.reg_write(r,v)
  for r,v in zip(saved,seeds):u.reg_write(r,v)
  guard=struct.pack('<I',OUT)+b'\xa5'*28;u.mem_write(0x2007ff00,guard);u.reg_write(UC_ARM_REG_PC,entry&~1);seen=[]
  for step in range(64):
   response=command('c');pc=u.reg_read(UC_ARM_REG_PC)
   if pc==stop_address:break
   assert pc==stub,(case,hex(pc),response)
   a,offset,buffer,n=[u.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];assert a==STREAM and offset<128 and n in [0,2,4],(case,a,offset,buffer,n)
   if buffer==0:
    assert n==0;result=1 if case['seek_fail'] else 0;seen.append(('seek',offset,result))
   else:
    actual=n-1 if case['short'] else n
    if actual>0:u.mem_write(buffer,u.mem_read(BASE+offset,actual))
    result=actual;seen.append(('read',offset,n,actual))
   u.reg_write(UC_ARM_REG_R0,result);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR)&~1)
  else:raise AssertionError(('step bound',case))
  assert u.reg_read(UC_ARM_REG_SP)==0x2007ff00 and [u.reg_read(r) for r in saved]==seeds and bytes(u.mem_read(0x2007ff00,32))==guard,(case,hex(u.reg_read(UC_ARM_REG_SP)))
  return u.reg_read(UC_ARM_REG_R0),seen,bytes(u.mem_read(FS,4096))
 import itertools
 rng=random.Random(3931);count=0
 for magic,match,n,count_decl,pattern,short,seek_fail in itertools.product([0x51607,0x51600],[True,False],[8,26,34,50,128],[0,1,2],[0,1,2],[False,True],[False,True]):
  if not match and (n not in [8,128] or count_decl!=1 or pattern!=0 or short or seek_fail):continue
  if short and (n not in [34,128] or pattern!=1 or count_decl!=1 or seek_fail):continue
  if seek_fail and (n not in [34,128] or pattern!=1 or count_decl!=1):continue
  initial=bytearray(rng.getrandbits(8) for _ in range(4096));initial[BASE-FS:BASE-FS+128]=bytes(128)
  struct.pack_into('>II',initial,BASE-FS,magic if match else 0x12345678,0x12345678);struct.pack_into('>H',initial,BASE-FS+24,count_decl)
  for j in range(2):
   id_value=2 if ((pattern==1 and j==0) or (pattern==2 and j==1)) else 1;struct.pack_into('>III',initial,BASE-FS+26+12*j,id_value,0x1000+j*17,0x20+j)
  for a,v in [(STREAM,BASE),(STREAM+4,n),(STREAM+8,0),(STREAM+20,symbols['probe_read']),(OUT,0xfeedcafe)]:struct.pack_into('<I',initial,a-FS,v)
  case={'magic':magic,'match':match,'size':n,'count':count_decl,'pattern':pattern,'short':short,'seek_fail':seek_fail}
  a=run(0x528720+delta,initial,case);c=run(symbols['audio_uart_ft_mac_apple_generic_528720'],initial,case);assert a==c,(case,a[:2],c[:2],[(i,x,y) for i,(x,y) in enumerate(zip(a[2],c[2])) if x!=y][:16]);count+=1
 receipt={'status':'PASS_APPLE_GENERIC_PARSER_CALLBACK_STREAM','comparisons':count,'native_bytes':226,'native_entry':'0x528720','actual_helpers':['selected stream callback BE16/BE32 and skip','native stream callback BE16/BE32 and skip'],'controlled_boundaries':['read/seek callback responses'],'checks':['callback full and short reads','callback seek failure','entry id/offset logic','whole4KiB/R0/SP/R4-R11/caller guard'],'limits':['Parent path search and remaining three table handlers unqualified','Runtime/layout/byte/hardware unproven'],'selected':False};(D/'callback-probe-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
finally:
 p.terminate();p.communicate(timeout=5)
