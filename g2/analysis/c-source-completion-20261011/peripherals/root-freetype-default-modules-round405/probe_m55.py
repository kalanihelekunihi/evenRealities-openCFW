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

 u=Remote();stop=symbols['probe_stop']&~1;FS=0x20003000;LIB=FS+0x100
 entries=[0x752520,0x6ded34,0x6dcb74,0x758a18,0x758a60,0x758a3c,0x75a3f8,0x718d9c,0x718dd8,0x718e14]
 names=['autofit_module_class','tt_driver_class','cff_driver_class','psaux_module_class','psnames_module_class','pshinter_module_class','sfnt_module_class','ft_smooth_renderer_class','ft_smooth_lcd_renderer_class','ft_smooth_lcdv_renderer_class']
 c_entries=[symbols[n] for n in names]
 targets={0x52729c+delta:'add',symbols['audio_uart_ft_add_module_52729c']&~1:'add'}
 for address in [stop,*targets]:assert command('Z1,'+hex(address)[2:]+',2')=='OK'
 saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11];seeds=[0x12345000+i*0x101 for i in range(8)]
 def run(entry,initial,case):
  u.mem_write(FS,initial);u.reg_write(UC_ARM_REG_CPSR,0x01000000);u.reg_write(UC_ARM_REG_SP,0x2007ff00);u.reg_write(UC_ARM_REG_LR,stop|1)
  library=0 if case['null_library'] else LIB
  for r,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],[library,0x11223344,0x22334455,0x33445566]):u.reg_write(r,v)
  for r,v in zip(saved,seeds):u.reg_write(r,v)
  guard=b'\xa5'*32;u.mem_write(0x2007ff00,guard);u.reg_write(UC_ARM_REG_PC,entry&~1);trace=[]
  for step in range(12):
   response=command('c');pc=u.reg_read(UC_ARM_REG_PC)
   if pc==stop:break
   assert targets.get(pc)=='add',(case,hex(entry),hex(pc),response)
   a=u.reg_read(UC_ARM_REG_R0);b=u.reg_read(UC_ARM_REG_R1);assert a==library
   index=entries.index(b) if b in entries else c_entries.index(b)
   value=case['returns'][index];trace.append((index,a,value));u.reg_write(UC_ARM_REG_R0,value);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR)&~1)
  else:raise AssertionError(('call bound',case,trace))
  assert [x[0] for x in trace]==list(range(10)),(case,trace)
  assert u.reg_read(UC_ARM_REG_SP)==0x2007ff00 and [u.reg_read(r) for r in saved]==seeds and bytes(u.mem_read(0x2007ff00,32))==guard
  return trace,bytes(u.mem_read(FS,4096))
 rng=random.Random(405);cases=[]
 for null_library in [False,True]:
  sequences=[[0]*10,[5]*10,[0,1,5,0x30,0x40,0,2,3,4,0]]
  sequences.extend([[rng.choice([0,0,0,1,5,0x30,0x40]) for _ in range(10)] for j in range(28)])
  for sequence in sequences:cases.append({'null_library':null_library,'returns':sequence})
 count=0
 for case in cases:
  initial=bytearray(rng.getrandbits(8) for _ in range(4096));native=run(0x5242fc+delta,initial,case);candidate=run(symbols['audio_uart_ft_add_default_modules_5242fc'],initial,case)
  assert native==candidate,(case,native[0],candidate[0]);count+=1
 print(json.dumps({'status':'PASS_NATIVE_C_FT_DEFAULT_MODULES','comparisons':count,'native_bytes':28,'module_calls':count*10,'typed_class_order':names},indent=2),flush=True)
finally:
 p.terminate();p.communicate(timeout=5)
