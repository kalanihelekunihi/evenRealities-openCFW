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

 u=Remote();stop=symbols['probe_stop']&~1;FS=0x20003000;LIB=FS+0x100;MEM=FS+0x200;CLASS=FS+0x300;OLDCLASS=FS+0x340;EXISTING=FS+0x380;MODULE=FS+0x500;NAME1=FS+0x700;NAME2=FS+0x720;RASTERCLASS=FS+0x900;RASTER=FS+0x980
 targets={}
 pairs=[('strcmp',0x46cacc,'audio_uart_font_path_compare'),('alloc',0x529148,'audio_uart_font_mem_alloc'),('free',0x529256,'audio_uart_font_mem_free'),('remove',0x527466,'audio_uart_ft_remove_module_527466'),('renderer',0x5270d2,'audio_uart_ft_add_renderer_5270d2')]
 for kind,address,name in pairs:
  targets[address+delta]=kind;targets[symbols[name]&~1]=kind
 for kind,name in [('init','probe_module_init'),('raster_done','probe_raster_done')]:targets[symbols[name]&~1]=kind
 for address in [stop,*targets]:assert command('Z1,'+hex(address)[2:]+',2')=='OK'
 saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11];seeds=[0x12345000+i*0x101 for i in range(8)]
 def readword(addr):return struct.unpack('<I',u.mem_read(addr,4))[0]
 def put(addr,value):u.mem_write(addr,struct.pack('<I',value&0xffffffff))
 def cstring(addr):
  out=bytearray()
  for i in range(40):
   q=u.mem_read(addr+i,1)[0]
   if q==0:break
   out.append(q)
  return bytes(out)
 def run(entry,initial,case):
  u.mem_write(FS,initial);u.reg_write(UC_ARM_REG_CPSR,0x01000000);u.reg_write(UC_ARM_REG_SP,0x2007ff00);u.reg_write(UC_ARM_REG_LR,stop|1)
  for r,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],[0 if case['null_library'] else LIB,0 if case['null_class'] else CLASS,0x22334455,0x33445566]):u.reg_write(r,v)
  for r,v in zip(saved,seeds):u.reg_write(r,v)
  guard=b'\xa5'*32;u.mem_write(0x2007ff00,guard);u.reg_write(UC_ARM_REG_PC,entry&~1);trace=[]
  for step in range(90):
   response=command('c');pc=u.reg_read(UC_ARM_REG_PC)
   if pc==stop:break
   kind=targets.get(pc);assert kind,(case,hex(entry),hex(pc),response)
   a,b,c=[u.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2]]
   if kind=='strcmp':
    left,right=cstring(a),cstring(b);value=(left>right)-(left<right);trace.append((kind,left.decode(),right.decode(),value))
   elif kind=='remove':
    assert a==LIB and b==EXISTING;(trace.append((kind,a,b)));put(LIB+16,0);put(LIB+20,0);value=0
   elif kind=='alloc':
    assert a==MEM and b==64;value=0 if case['alloc_error'] else MODULE;put(c,case['alloc_error']);u.mem_write(MODULE,bytes(64));trace.append((kind,a,b,case['alloc_error']))
   elif kind=='renderer':
    assert a==MODULE;value=case['renderer_error'];trace.append((kind,a,value));put(MODULE+12,CLASS);put(MODULE+52,RASTER if case['has_raster'] else 0)
   elif kind=='init':
    assert a==MODULE;value=case['init_error'];trace.append((kind,a,value))
   elif kind=='raster_done':
    assert a==RASTER;value=0;trace.append((kind,a))
   elif kind=='free':
    assert a==MEM and b==MODULE;value=0;trace.append((kind,a,b))
   u.reg_write(UC_ARM_REG_R0,value&0xffffffff);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR)&~1)
  else:raise AssertionError(('call bound',case,trace))
  assert u.reg_read(UC_ARM_REG_SP)==0x2007ff00,(case,hex(entry),hex(u.reg_read(UC_ARM_REG_SP)))
  assert [u.reg_read(r) for r in saved]==seeds and bytes(u.mem_read(0x2007ff00,32))==guard
  return u.reg_read(UC_ARM_REG_R0),trace,bytes(u.mem_read(FS,4096))
 rng=random.Random(401);cases=[]
 for null_library,null_class,requires in [(True,False,0x20000),(False,True,0x20000),(False,False,0x2000a),(False,False,0x20009)]:cases.append({'null_library':null_library,'null_class':null_class,'requires':requires,'count':0,'same_name':False,'new_version':2,'old_version':1,'flags':0,'alloc_error':0,'renderer_error':0,'init_error':0,'has_init':False,'raster_outline':False,'has_raster':False})
 for count in [0,1,32]:
  for same in [False,True]:
   for version in [1,2]:
    for flags in [0,1,2,4,7]:
     for error_stage in ['none','alloc','renderer','init']:
      case={'null_library':False,'null_class':False,'requires':0x20000,'count':count,'same_name':same,'new_version':version,'old_version':1,'flags':flags,'alloc_error':0x40 if error_stage=='alloc' else 0,'renderer_error':9 if error_stage=='renderer' else 0,'init_error':6 if error_stage=='init' else 0,'has_init':error_stage=='init' or error_stage=='none','raster_outline':True,'has_raster':True}
      cases.append(case)
 for flags in [2,3,6,7]:
  for raster_outline in [False,True]:
   for has_raster in [False,True]:
    for error_stage in ['renderer','init']:
     cases.append({'null_library':False,'null_class':False,'requires':0x20000,'count':0,'same_name':False,'new_version':2,'old_version':1,'flags':flags,'alloc_error':0,'renderer_error':9 if error_stage=='renderer' else 0,'init_error':6 if error_stage=='init' else 0,'has_init':True,'raster_outline':raster_outline,'has_raster':has_raster})
 total=0
 for case in cases:
  initial=bytearray(rng.getrandbits(8) for _ in range(4096))
  def pack(address,value):struct.pack_into('<I',initial,address-FS,value&0xffffffff)
  for address,value in [(LIB,MEM),(LIB+16,case['count']),(CLASS,case['flags']),(CLASS+4,64),(CLASS+8,NAME2),(CLASS+12,case['new_version']),(CLASS+16,case['requires']),(CLASS+24,symbols['probe_module_init'] if case['has_init'] else 0),(CLASS+36,0x6f75746c if case['raster_outline'] else 0),(CLASS+56,RASTERCLASS),(OLDCLASS+8,NAME1),(OLDCLASS+12,case['old_version']),(EXISTING,OLDCLASS),(MODULE+12,CLASS),(MODULE+52,RASTER if case['has_raster'] else 0),(RASTERCLASS+20,symbols['probe_raster_done'])]:pack(address,value)
  for j in range(case['count']):pack(LIB+20+j*4,EXISTING)
  left=b'moduleA\0' if case['same_name'] else b'moduleZ\0';right=b'moduleA\0'
  initial[NAME1-FS:NAME1-FS+len(left)]=left;initial[NAME2-FS:NAME2-FS+len(right)]=right
  native=run(0x52729c+delta,initial,case);candidate=run(symbols['audio_uart_ft_add_module_52729c'],initial,case)
  if native!=candidate:
   diff=[(i,a,b) for i,(a,b) in enumerate(zip(native[2],candidate[2])) if a!=b]
   print(json.dumps({'case':case,'native_status':native[0],'candidate_status':candidate[0],'native_trace':native[1],'candidate_trace':candidate[1],'diff':diff[:16]}),flush=True)
   raise AssertionError('native/C module mismatch')
  total+=1
  if total%50==0:print('comparisons',total,flush=True)
 print(json.dumps({'status':'PASS_NATIVE_C_FT_ADD_MODULE','comparisons':total,'native_bytes':278},indent=2),flush=True)
finally:
 p.terminate();p.communicate(timeout=5)
