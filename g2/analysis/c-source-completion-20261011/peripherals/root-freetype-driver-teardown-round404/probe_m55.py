from pathlib import Path
import subprocess,socket,time,xml.etree.ElementTree as ET,struct,json,random,hashlib
from elftools.elf.elffile import ELFFile
from unicorn.arm_const import *
D=Path(__file__).resolve().parent
with (D/'probe.elf').open('rb') as f:
 e=ELFFile(f);symbols={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
mapping={};names=[]
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

 u=Remote();stop=symbols['probe_stop']&~1;FS=0x20003000;DRIVER=FS+0x100;MEM=FS+0x300
 targets={0x529378+delta:'finalize',symbols['audio_uart_ft_list_finalize_529378']&~1:'finalize'}
 for address in [stop,*targets]:assert command('Z1,'+hex(address)[2:]+',2')=='OK'
 saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11];seeds=[0x12345000+i*0x101 for i in range(8)]
 def run(entry,initial):
  u.mem_write(FS,initial);u.reg_write(UC_ARM_REG_CPSR,0x01000000);u.reg_write(UC_ARM_REG_SP,0x2007ff00);u.reg_write(UC_ARM_REG_LR,stop|1)
  for r,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],[DRIVER,0x11223344,0x22334455,0x33445566]):u.reg_write(r,v)
  for r,v in zip(saved,seeds):u.reg_write(r,v)
  guard=b'\xa5'*32;u.mem_write(0x2007ff00,guard);u.reg_write(UC_ARM_REG_PC,entry&~1);trace=[]
  for step in range(3):
   response=command('c');pc=u.reg_read(UC_ARM_REG_PC)
   if pc==stop:break
   assert targets.get(pc)=='finalize',(hex(entry),hex(pc),response)
   a,b,c,d=[u.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]]
   assert a==DRIVER+16 and d==DRIVER and b in [0x5258a9,symbols['audio_uart_ft_destroy_face_5258a8']];trace.append((a,'destroy_face',c,d))
   u.reg_write(UC_ARM_REG_R0,0);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR)&~1)
  else:raise AssertionError(('call bound',hex(entry)))
  assert u.reg_read(UC_ARM_REG_SP)==0x2007ff00 and [u.reg_read(r) for r in saved]==seeds and bytes(u.mem_read(0x2007ff00,32))==guard
  return trace,bytes(u.mem_read(FS,4096))
 rng=random.Random(404);count=0
 for memory in [0,MEM,FS+0x3fc,0x12345678]:
  for j in range(16):
   initial=bytearray(rng.getrandbits(8) for _ in range(4096));struct.pack_into('<I',initial,DRIVER+8-FS,memory)
   native=run(0x525936+delta,initial);candidate=run(symbols['audio_uart_ft_destroy_driver_525936'],initial)
   assert native==candidate,(memory,j,native[0],candidate[0]);count+=1
 print(json.dumps({'status':'PASS_NATIVE_C_FT_DRIVER_TEARDOWN','comparisons':count,'native_bytes':20,'callback_pointer':'native literal at0x5262a0 resolves to0x5258a9'},indent=2),flush=True)
finally:
 p.terminate();p.communicate(timeout=5)
