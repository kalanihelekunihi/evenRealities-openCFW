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

 u=Remote();stop=symbols['probe_stop']&~1
 oracle=Path('/tmp/opencfw-main-native.bin')
 assert hashlib.sha256(oracle.read_bytes()).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
 delta=0x28100000-0x438000
 FS=0x20003000;LOADER=FS+0x100;MEM=FS+0x600;EXTRA=FS+0x800
 alloc_targets={0x52919c+delta,symbols['audio_uart_ft_mem_qalloc_52919c']&~1}
 for addr in [stop,*alloc_targets]:assert command('Z1,'+hex(addr)[2:]+',2')=='OK'
 saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
 seeds=[0x24514000+i*0x101 for i in range(8)]
 def put32(data,off,value):struct.pack_into('<I',data,off,value&0xffffffff)
 def run(entry,initial,case,create):
  u.mem_write(FS,initial)
  u.reg_write(UC_ARM_REG_CPSR,0x01000000);u.reg_write(UC_ARM_REG_SP,0x2007ff00)
  u.reg_write(UC_ARM_REG_LR,stop|1)
  for r,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],[LOADER,0x11223344,0x22334455,0x33445566]):u.reg_write(r,v)
  for r,v in zip(saved,seeds):u.reg_write(r,v)
  guard=b'\xa5'*32;u.mem_write(0x2007ff00,guard)
  u.reg_write(UC_ARM_REG_PC,entry&~1);trace=[]
  for step in range(3):
   response=command('c');pc=u.reg_read(UC_ARM_REG_PC)
   if pc==stop:break
   assert create and pc in alloc_targets,(case,hex(entry),hex(pc),response)
   sp=u.reg_read(UC_ARM_REG_SP);args=struct.unpack('<2I',bytes(u.mem_read(sp,8)))
   assert (u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1),u.reg_read(UC_ARM_REG_R2),u.reg_read(UC_ARM_REG_R3),args[0])==(MEM,8,0,case['max_points']*2,0),(case,hex(pc),args)
   assert FS<=args[1]<FS+4096 or 0x2007fe00<=args[1]<0x20080000
   u.mem_write(args[1],struct.pack('<I',case['error']))
   u.reg_write(UC_ARM_REG_R0,EXTRA if case['error']==0 else 0)
   trace.append((pc in alloc_targets,case['error'],args[0]))
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR)&~1)
  else:raise AssertionError(('call bound',case,trace))
  assert len(trace)==(1 if create else 0),(case,trace)
  assert u.reg_read(UC_ARM_REG_SP)==0x2007ff00
  assert [u.reg_read(r) for r in saved]==seeds
  assert bytes(u.mem_read(0x2007ff00,32))==guard
  return (u.reg_read(UC_ARM_REG_R0) if create else None,trace,bytes(u.mem_read(FS,4096)))
 rng=random.Random(407);counts={'adjust':0,'create':0}
 for points,contours,extra in [(0,0,False),(1,1,True),(-1,-1,True),(32767,-32768,True),(-32768,32767,False)]+[(rng.randrange(-32768,32768),rng.randrange(-32768,32768),bool(rng.randrange(2))) for _ in range(25)]:
  initial=bytearray(rng.getrandbits(8) for _ in range(4096));o=0x100
  struct.pack_into('<h',initial,o+22,points);struct.pack_into('<h',initial,o+20,contours)
  initial[o+16]=1 if extra else 0
  case={'points':points,'contours':contours,'extra':extra}
  native=run(0x524c3a+delta,initial,case,False)
  candidate=run(symbols['audio_uart_ft_glyph_loader_adjust_points_524c3a'],initial,case,False)
  assert native==candidate,(case,native[:2],candidate[:2]);counts['adjust']+=1
 for max_points,error in [(0,0),(1,0),(8,0),(0,64),(1,64),(0x7fffffff,64)]+[(rng.choice([0,1,2,8,64,1024]),rng.choice([0,0,64])) for _ in range(24)]:
  initial=bytearray(rng.getrandbits(8) for _ in range(4096));o=0x100
  put32(initial,o+0,MEM);put32(initial,o+4,max_points)
  case={'max_points':max_points,'error':error}
  native=run(0x524c88+delta,initial,case,True)
  candidate=run(symbols['audio_uart_ft_glyph_loader_create_extra_524c88'],initial,case,True)
  assert native==candidate,(case,native[:2],candidate[:2]);counts['create']+=1
 receipt={'status':'PASS_TWO_FULL_GLYPH_EXTRA_BODIES_CONNECTED','comparisons':sum(counts.values()),'per_body':counts,'native_extents':['0x524c3a..0x524c88','0x524c88..0x524cc4'],'controlled_child':'FT memory qalloc 0x52919c','checks':['signed counts including limits','extra pointer offsets','allocator success and error','full4KiB/SP/R4-R11/stack guard'],'selected':False,'limits':['Allocator provider still controlled','No image/layout/hardware proof']}
 (D/'probe-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
 print(json.dumps(receipt),flush=True)
finally:
 p.terminate();p.communicate(timeout=5)

