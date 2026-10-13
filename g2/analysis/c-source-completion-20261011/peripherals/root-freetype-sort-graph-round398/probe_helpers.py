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

 u=Remote();stop=symbols['probe_stop']&~1;FS=0x20003000
 assert command('Z1,'+hex(stop)[2:]+',2')=='OK'
 saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
 seeds=[0x12345000+i*0x101 for i in range(8)]
 def run(entry,args,initial):
  u.mem_write(FS,initial);u.reg_write(UC_ARM_REG_CPSR,0x01000000);u.reg_write(UC_ARM_REG_SP,0x2007ff00);u.reg_write(UC_ARM_REG_LR,stop|1)
  for r,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],args[:4]):u.reg_write(r,v)
  for r,v in zip(saved,seeds):u.reg_write(r,v)
  guard=struct.pack('<I',args[4] if len(args)>4 else 0)+b'\xa5'*28;u.mem_write(0x2007ff00,guard)
  u.reg_write(UC_ARM_REG_PC,entry&~1);response=command('c');pc=u.reg_read(UC_ARM_REG_PC)
  assert pc==stop,(hex(entry),hex(pc),response)
  assert u.reg_read(UC_ARM_REG_SP)==0x2007ff00,(hex(entry),hex(u.reg_read(UC_ARM_REG_SP)))
  assert [u.reg_read(r) for r in saved]==seeds
  assert bytes(u.mem_read(0x2007ff00,32))==guard
  return bytes(u.mem_read(FS,4096)),u.reg_read(UC_ARM_REG_R0)
 rng=random.Random(398);cases=[];cmp=symbols['probe_compare']
 for width in [0,1,4,15,63,64,65,128,129,257]:
  a,b,c=FS+128,FS+768,FS+1408
  for role,entry,args in [('swap',0x5677a8,[a,b,width,0]),('rotate',0x5677fe,[a,b,c,width]),('insert',0x56786c,[a,b,width,0])]:
   cases.append((role,entry,args))
 for perm in [(1,2,3),(3,2,1),(2,2,1),(1,1,1),(3,1,2),(2,3,1)]:
  a,b,c=FS+128,FS+768,FS+1408;cases.append(('median',0x5678b6,[a,b,c,4,cmp],perm))
 for count in [1,2,3,8,16,31]:
  for start in [0,count//3]:cases.append(('sift',0x567906,[FS+128,start,count,4,cmp]))
 comparisons={role:0 for role in ['swap','rotate','insert','median','sift']}
 for case in cases:
  role,entry,args=case[:3];initial=bytearray(rng.getrandbits(8) for _ in range(4096))
  initial[0xc00:0xc04]=bytes(4)
  if role=='median':
   for a,v in zip(args[:3],case[3]):struct.pack_into('<i',initial,a-FS,v)
  if role=='sift':
   for j in range(32):struct.pack_into('<i',initial,128+4*j,rng.randrange(-20,21))
  c_entry=symbols[{'swap':'audio_uart_ft_sort_swap_5677a8','rotate':'audio_uart_ft_sort_rotate_5677fe','insert':'audio_uart_ft_sort_insert_56786c','median':'audio_uart_ft_sort_median_5678b6','sift':'audio_uart_ft_sort_heap_sift_567906'}[role]]
  native=run(entry+delta,args,initial);candidate=run(c_entry,args,initial)
  assert native[0]==candidate[0],(role,args,[(i,x,y) for i,(x,y) in enumerate(zip(native[0],candidate[0])) if x!=y][:12])
  if role=='sift':assert native[1]==candidate[1],(role,args,native[1],candidate[1])
  comparisons[role]+=1
 print(json.dumps({'status':'PASS_NATIVE_C_SORT_HELPERS','comparisons':comparisons,'native_bytes':484,'limits':['sort core not qualified','comparison covers defined disjoint helper inputs and valid insertion ranges','full firmware images remain unaccepted']},indent=2),flush=True)
finally:
 p.terminate();p.communicate(timeout=5)
