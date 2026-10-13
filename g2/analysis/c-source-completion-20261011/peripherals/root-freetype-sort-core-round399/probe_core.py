from pathlib import Path
import subprocess,socket,time,xml.etree.ElementTree as ET,struct,json,random,hashlib
from elftools.elf.elffile import ELFFile
from unicorn.arm_const import *
D=Path(__file__).resolve().parent
with (D/'probe-core.elf').open('rb') as f:
 e=ELFFile(f);symbols={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
mapping={};names=[]
delta=0x28100000-0x438000
reserve=socket.socket();reserve.bind(('127.0.0.1',0));port=reserve.getsockname()[1];reserve.close()
p=subprocess.Popen(['qemu-system-arm','-M','mps3-an547','-cpu','cortex-m55','-display','none','-monitor','none','-serial','none','-kernel',str(D/'probe-core.elf'),'-S','-gdb','tcp:127.0.0.1:'+str(port)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
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
  guard=struct.pack('<I',args[4])+b'\xa5'*28;u.mem_write(0x2007ff00,guard)
  u.reg_write(UC_ARM_REG_PC,entry&~1);response=command('c');pc=u.reg_read(UC_ARM_REG_PC)
  assert pc==stop,(hex(entry),hex(pc),response)
  assert u.reg_read(UC_ARM_REG_SP)==0x2007ff00,(hex(entry),hex(u.reg_read(UC_ARM_REG_SP)))
  assert [u.reg_read(r) for r in saved]==seeds
  assert bytes(u.mem_read(0x2007ff00,32))==guard
  return bytes(u.mem_read(FS,4096))
 rng=random.Random(399);cmp=symbols['probe_compare'];BASE=FS+128
 cases=[]
 for count in [0,1,2,3,4,5,8,16,31,32,33,40,41,42,64]:
  for pattern in ['sorted','reversed','equal','random']:
   cases.append((count,4,count,pattern))
 for count in [2,8,32,33,41]:
  for width in [8,16,63,64,65,128,129]:
   if count*width<2600:cases.append((count,width,count,'random'))
 for count in [33,40,41,42,64]:cases.append((count,4,0,'random'))
 for j in range(300):
  width=rng.choice([4,8,12,16,31,32,63,64,65,128,129])
  count=rng.randrange(0,min(112,2500//width)+1)
  budget=rng.choice([0,1,2,count,max(0,count//2),count+3])
  pattern=rng.choice(['sorted','reversed','equal','random','alternating','few_keys'])
  cases.append((count,width,budget,pattern))
 comparisons={};total=0
 for count,width,budget,pattern in cases:
  initial=bytearray(rng.getrandbits(8) for _ in range(4096));initial[0xc00:0xc04]=bytes(4)
  if pattern=='sorted':keys=list(range(count))
  elif pattern=='reversed':keys=list(range(count,0,-1))
  elif pattern=='equal':keys=[3]*count
  elif pattern=='alternating':keys=[(1000 if j%2 else -1000) for j in range(count)]
  elif pattern=='few_keys':keys=[rng.randrange(-2,3) for _ in range(count)]
  else:keys=[rng.randrange(-13,14) for _ in range(count)]
  for j,key in enumerate(keys):struct.pack_into('<i',initial,128+j*width,key)
  args=[BASE,count,budget,width,cmp]
  native=run(0x56798c+delta,args,initial);candidate=run(symbols['audio_uart_ft_sort_core_56798c'],args,initial)
  if native!=candidate:
   diff=[(i,x,y) for i,(x,y) in enumerate(zip(native,candidate)) if x!=y]
   print(json.dumps({'mismatch':{'count':count,'width':width,'budget':budget,'pattern':pattern,'native_trace_count':struct.unpack_from('<I',native,0xc00)[0],'candidate_trace_count':struct.unpack_from('<I',candidate,0xc00)[0],'first_differences':diff[:18]}}),flush=True)
   raise AssertionError('native/C core mismatch')
  total+=1;comparisons[pattern]=comparisons.get(pattern,0)+1
  if total%20==0:print('comparisons',total,flush=True)
 print(json.dumps({'status':'PASS_NATIVE_C_SORT_CORE','comparisons':total,'patterns':comparisons,'native_bytes':704},indent=2),flush=True)
finally:
 p.terminate();p.communicate(timeout=5)
