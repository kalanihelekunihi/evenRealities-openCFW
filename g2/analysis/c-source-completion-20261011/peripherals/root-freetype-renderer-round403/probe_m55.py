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

 u=Remote();stop=symbols['probe_stop']&~1;FS=0x20003000;LIB=FS+0x100;MEM=FS+0x200;MODULE=FS+0x300;CLASS=FS+0x400;RASTERCLASS=FS+0x500;NODE=FS+0x600;RASTER=FS+0x700;LIST=LIB+0x94
 targets={}
 for kind,address,name in [('alloc',0x529148,'audio_uart_font_mem_alloc'),('free',0x529256,'audio_uart_font_mem_free'),('list_add',0x529304,'audio_uart_ft_list_add_529304'),('list_find',0x5292e6,'audio_uart_ft_list_find_5292e6'),('list_remove',0x529324,'audio_uart_ft_list_remove_529324'),('lookup',0x52705a,'audio_uart_font_lookup_renderer')]:targets[address+delta]=kind;targets[symbols[name]&~1]=kind
 for kind,name in [('raster_new','probe_raster_new'),('raster_done','probe_raster_done')]:targets[symbols[name]&~1]=kind
 for address in [stop,*targets]:assert command('Z1,'+hex(address)[2:]+',2')=='OK'
 saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11];seeds=[0x12345000+i*0x101 for i in range(8)]
 def put(a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
 def run(entry,initial,case):
  u.mem_write(FS,initial);u.reg_write(UC_ARM_REG_CPSR,0x01000000);u.reg_write(UC_ARM_REG_SP,0x2007ff00);u.reg_write(UC_ARM_REG_LR,stop|1)
  arg=LIB if case['kind']=='set' else MODULE
  for r,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],[arg,0x11223344,0x22334455,0x33445566]):u.reg_write(r,v)
  for r,v in zip(saved,seeds):u.reg_write(r,v)
  guard=b'\xa5'*32;u.mem_write(0x2007ff00,guard);u.reg_write(UC_ARM_REG_PC,entry&~1);trace=[]
  for step in range(16):
   response=command('c');pc=u.reg_read(UC_ARM_REG_PC)
   if pc==stop:break
   kind=targets.get(pc);assert kind,(case,hex(entry),hex(pc),response)
   a,b,c=[u.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2]]
   if kind=='alloc':
    assert a==MEM and b==12;put(c,case['alloc_error']);u.mem_write(NODE,bytes(12));value=0 if case['alloc_error'] else NODE;trace.append((kind,a,b,case['alloc_error']))
   elif kind=='free':assert a==MEM and b==NODE;value=0;trace.append((kind,a,b))
   elif kind=='list_add':assert a==LIST and b==NODE;put(LIST,NODE);put(LIST+4,NODE);value=0;trace.append((kind,a,b))
   elif kind=='list_find':assert a==LIST and b==MODULE;value=NODE if case['found'] else 0;trace.append((kind,a,b,value))
   elif kind=='list_remove':assert a==LIST and b==NODE;put(LIST,0);put(LIST+4,0);value=0;trace.append((kind,a,b))
   elif kind=='lookup':assert a==LIB and b==0x6f75746c and c==0;value=MODULE if case['lookup'] else 0;trace.append((kind,a,b,value))
   elif kind=='raster_new':assert a==MEM and b==MODULE+52;put(b,RASTER);value=case['raster_error'];trace.append((kind,a,b,value))
   elif kind=='raster_done':assert a==RASTER;value=0;trace.append((kind,a))
   u.reg_write(UC_ARM_REG_R0,value&0xffffffff);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR)&~1)
  else:raise AssertionError(('call bound',case,trace))
  assert u.reg_read(UC_ARM_REG_SP)==0x2007ff00,(case,hex(entry),hex(u.reg_read(UC_ARM_REG_SP)))
  assert [u.reg_read(r) for r in saved]==seeds and bytes(u.mem_read(0x2007ff00,32))==guard
  return u.reg_read(UC_ARM_REG_R0),trace,bytes(u.mem_read(FS,4096))
 rng=random.Random(403);cases=[]
 for lookup in [False,True]:cases.append({'kind':'set','lookup':lookup,'alloc_error':0,'raster_error':0,'found':False,'library':True,'outline':True,'has_new':True,'has_raster':True})
 for outline in [False,True]:
  for has_new in [False,True]:
   for alloc_error in [0,0x40]:
    for raster_error in [0,7]:
     for lookup in [False,True]:cases.append({'kind':'add','outline':outline,'has_new':has_new,'alloc_error':alloc_error,'raster_error':raster_error,'lookup':lookup,'found':False,'library':True,'has_raster':True})
 for library in [False,True]:
  for found in [False,True]:
   for outline in [False,True]:
    for has_raster in [False,True]:
     for lookup in [False,True]:cases.append({'kind':'remove','outline':outline,'has_new':True,'alloc_error':0,'raster_error':0,'lookup':lookup,'found':found,'library':library,'has_raster':has_raster})
 total=0;by_kind={}
 for case in cases:
  initial=bytearray(rng.getrandbits(8) for _ in range(4096))
  def pack(a,v):struct.pack_into('<I',initial,a-FS,v&0xffffffff)
  for a,v in [(LIB,MEM),(MODULE,CLASS),(MODULE+4,LIB if case['library'] else 0),(MODULE+12,CLASS),(MODULE+52,RASTER if case['has_raster'] else 0),(CLASS+36,0x6f75746c if case['outline'] else 0x62697473),(CLASS+40,0xaaaa5555),(CLASS+56,RASTERCLASS),(RASTERCLASS+4,symbols['probe_raster_new'] if case['has_new'] else 0),(RASTERCLASS+16,0x99887766),(RASTERCLASS+20,symbols['probe_raster_done'])]:pack(a,v)
  n_entry={'set':0x5270bc,'add':0x5270d2,'remove':0x52716c}[case['kind']];c_name={'set':'audio_uart_ft_set_current_renderer_5270bc','add':'audio_uart_ft_add_renderer_5270d2','remove':'audio_uart_ft_remove_renderer_52716c'}[case['kind']]
  native=run(n_entry+delta,initial,case);candidate=run(symbols[c_name],initial,case)
  equal=(native[1:]==candidate[1:]) if case['kind']!='add' else native==candidate
  if not equal:
   diff=[(i,a,b) for i,(a,b) in enumerate(zip(native[2],candidate[2])) if a!=b]
   print(json.dumps({'case':case,'native_status':native[0],'candidate_status':candidate[0],'native_trace':native[1],'candidate_trace':candidate[1],'diff':diff[:16]}),flush=True)
   raise AssertionError('native/C renderer mismatch')
  total+=1;by_kind[case['kind']]=by_kind.get(case['kind'],0)+1
 print(json.dumps({'status':'PASS_NATIVE_C_FT_RENDERER_GRAPH','comparisons':total,'by_kind':by_kind,'native_bytes':260},indent=2),flush=True)
finally:
 p.terminate();p.communicate(timeout=5)
