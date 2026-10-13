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

 u=Remote();stop=symbols['probe_stop']&~1;FS=0x20003000;LIB=FS+0x100;MEM=FS+0x200;CLASS=FS+0x300;MODULE=FS+0x400;OTHER1=FS+0x500;OTHER2=FS+0x580
 targets={}
 for kind,address,name in [('free',0x529256,'audio_uart_font_mem_free'),('renderer',0x52716c,'audio_uart_ft_remove_renderer_52716c'),('driver',0x525936,'audio_uart_ft_destroy_driver_525936')]:targets[address+delta]=kind;targets[symbols[name]&~1]=kind
 targets[symbols['probe_module_done']&~1]='done'
 for address in [stop,*targets]:assert command('Z1,'+hex(address)[2:]+',2')=='OK'
 saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11];seeds=[0x12345000+i*0x101 for i in range(8)]
 def put(a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
 def run(entry,initial,case):
  u.mem_write(FS,initial);u.reg_write(UC_ARM_REG_CPSR,0x01000000);u.reg_write(UC_ARM_REG_SP,0x2007ff00);u.reg_write(UC_ARM_REG_LR,stop|1)
  args=[0 if case['null_library'] else LIB,0 if case['null_module'] else MODULE] if case['kind']=='remove' else [MODULE,0x11223344]
  for r,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],args+[0x22334455,0x33445566]):u.reg_write(r,v)
  for r,v in zip(saved,seeds):u.reg_write(r,v)
  guard=b'\xa5'*32;u.mem_write(0x2007ff00,guard);u.reg_write(UC_ARM_REG_PC,entry&~1);trace=[]
  for step in range(14):
   response=command('c');pc=u.reg_read(UC_ARM_REG_PC)
   if pc==stop:break
   kind=targets.get(pc);assert kind,(case,hex(entry),hex(pc),response)
   a=u.reg_read(UC_ARM_REG_R0);b=u.reg_read(UC_ARM_REG_R1)
   if kind=='free':assert a==MEM and b==MODULE;trace.append((kind,a,b))
   else:
    assert a==MODULE;trace.append((kind,a))
    if case['mutate_done'] and kind in ['renderer','driver']:put(CLASS+28,0)
   u.reg_write(UC_ARM_REG_R0,0);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR)&~1)
  else:raise AssertionError(('call bound',case,trace))
  assert u.reg_read(UC_ARM_REG_SP)==0x2007ff00,(case,hex(entry),hex(u.reg_read(UC_ARM_REG_SP)))
  assert [u.reg_read(r) for r in saved]==seeds and bytes(u.mem_read(0x2007ff00,32))==guard
  return u.reg_read(UC_ARM_REG_R0),trace,bytes(u.mem_read(FS,4096))
 rng=random.Random(402);cases=[]
 for flags in [0,1,2,3,4,5,6,7]:
  for library_mode in ['null','match','other']:
   for has_done in [False,True]:
    for mutate in [False,True]:cases.append({'kind':'done','flags':flags,'library_mode':library_mode,'has_done':has_done,'mutate_done':mutate,'null_library':False,'null_module':False,'count':0,'position':-1})
 for flags in [0,1,2,3,7]:
  for count in [0,1,2,3]:
   for position in [-1,0,1,2]:
    for null_library,null_module in [(False,False),(True,False),(False,True)]:
     cases.append({'kind':'remove','flags':flags,'library_mode':'match','has_done':True,'mutate_done':False,'null_library':null_library,'null_module':null_module,'count':count,'position':position})
 total=0;by_kind={}
 for case in cases:
  initial=bytearray(rng.getrandbits(8) for _ in range(4096))
  def pack(a,v):struct.pack_into('<I',initial,a-FS,v&0xffffffff)
  library=0 if case['library_mode']=='null' else LIB
  for a,v in [(MODULE,CLASS),(MODULE+4,library),(MODULE+8,MEM),(CLASS,case['flags']),(CLASS+28,symbols['probe_module_done'] if case['has_done'] else 0),(LIB+16,case['count']),(LIB+0xa0,MODULE if case['library_mode']=='match' else OTHER1)]:pack(a,v)
  for j in range(case['count']):pack(LIB+20+4*j,MODULE if j==case['position'] else (OTHER1 if j%2==0 else OTHER2))
  n_entry=0x527466 if case['kind']=='remove' else 0x52724c;c_name='audio_uart_ft_remove_module_527466' if case['kind']=='remove' else 'audio_uart_ft_done_module_52724c'
  native=run(n_entry+delta,initial,case);candidate=run(symbols[c_name],initial,case)
  if native!=candidate:
   diff=[(i,a,b) for i,(a,b) in enumerate(zip(native[2],candidate[2])) if a!=b]
   print(json.dumps({'case':case,'native_status':native[0],'candidate_status':candidate[0],'native_trace':native[1],'candidate_trace':candidate[1],'diff':diff[:16]}),flush=True)
   raise AssertionError('native/C removal mismatch')
  total+=1;by_kind[case['kind']]=by_kind.get(case['kind'],0)+1
  if total%100==0:print('comparisons',total,flush=True)
 print(json.dumps({'status':'PASS_NATIVE_C_FT_REMOVE_DONE_MODULE','comparisons':total,'by_kind':by_kind,'native_bytes':156},indent=2),flush=True)
finally:
 p.terminate();p.communicate(timeout=5)
