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







 FS=0x20003000;MEM=FS+0x100;FACE=FS+0x200;DRIVER=FS+0x300;CLASS=FS+0x400;ALTCLASS=FS+0x480;INTERNAL=FS+0x500;STREAM=FS+0x600;SLOTS=[FS+0x700,FS+0x720]
 for name in ['probe_autohint','probe_generic','probe_class','probe_free']:
  targets[symbols[name]&~1]=name;assert command('Z1,'+hex(symbols[name]&~1)[2:]+',2')=='OK'
 saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11];seeds=[0x12345000+i*0x101 for i in range(8)]
 def word(a):return struct.unpack('<I',u.mem_read(a,4))[0]
 def put(a,v):u.mem_write(a,struct.pack('<I',v))
 def run(entry,initial,case):
  u.mem_write(FS,initial);u.reg_write(UC_ARM_REG_CPSR,0x01000000);u.reg_write(UC_ARM_REG_SP,0x2007ff00);u.reg_write(UC_ARM_REG_LR,stop_address|1)
  for register,value in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2],[MEM,FACE,DRIVER]):u.reg_write(register,value)
  for register,value in zip(saved,seeds):u.reg_write(register,value)
  u.mem_write(0x2007ff00,b'\xa5'*32);u.reg_write(UC_ARM_REG_PC,entry&~1);seen=[]
  for step in range(16):
   response=command('c');pc=u.reg_read(UC_ARM_REG_PC)
   if pc==stop_address:break
   name=targets.get(pc);assert name,(hex(pc),response);a,b,c,d=[u.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];args=(a,)
   if name=='probe_autohint':assert a==0x12345678;put(DRIVER+12,ALTCLASS)
   elif name=='audio_uart_ft_done_glyph_slot_5253f4':
    assert a in SLOTS;put(FACE+84,SLOTS[1] if a==SLOTS[0] and case['slots']==2 else 0)
   elif name=='audio_uart_ft_list_finalize_529378':
    assert (a,b,c,d)==(FACE+108,symbols['audio_uart_ft_destroy_size_525832'],MEM,DRIVER);args=(a,b,c,d);put(FACE+88,0xabcdef);put(DRIVER+12,ALTCLASS)
   elif name=='probe_generic':assert a==FACE and word(FACE+88)==0;put(FACE+8,case['flags_after'])
   elif name=='audio_uart_ft_destroy_charmaps_52586e':assert (a,b)==(FACE,MEM);args=(a,b);put(FACE+36,0)
   elif name=='probe_class':assert a==FACE;put(FACE+8,case['flags_after']);put(FACE+104,STREAM)
   elif name=='audio_uart_ft_stream_free_52502a':
    expected_flags=case['flags_after'] if case['generic'] or case['clazz'] else case['flags'];assert (a,b)==(STREAM,(expected_flags>>10)&1);args=(a,b);put(FACE+128,INTERNAL if case['internal'] else 0)
   else:
    assert name=='probe_free' and a==MEM and b in [INTERNAL,FACE] and word(FACE+104)==0;args=(a,b)
    if b==FACE:assert word(FACE+128)==0
    put(b,0xdeadbeef)
   seen.append((name,args));u.reg_write(UC_ARM_REG_R0,0x1234abcd);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR)&~1)
  else:raise AssertionError('bound')
  assert u.reg_read(UC_ARM_REG_SP)==0x2007ff00 and [u.reg_read(r) for r in saved]==seeds;assert bytes(u.mem_read(0x2007ff00,32))==b'\xa5'*32
  return seen,bytes(u.mem_read(FS,2048))
 rng=random.Random(372);count=0
 import itertools
 for auto,generic,clazz,slots,flags,internal in itertools.product([0,1],[0,1],[0,1],[0,1,2],[0,1024],[0,1]):
  case={'generic':generic,'clazz':clazz,'slots':slots,'flags':flags,'flags_after':flags^1024,'internal':internal};initial=bytearray(rng.getrandbits(8) for _ in range(2048))
  def pack(address,value):struct.pack_into('<I',initial,address-FS,value)
  for a,v in [(MEM+8,symbols['probe_free']),(DRIVER+12,CLASS),(CLASS+52,symbols['probe_class'] if clazz else 0),(ALTCLASS+52,0),(FACE+116,0x12345678),(FACE+120,symbols['probe_autohint'] if auto else 0),(FACE+48,symbols['probe_generic'] if generic else 0),(FACE+84,SLOTS[0] if slots else 0),(FACE+8,flags),(FACE+104,STREAM),(FACE+128,INTERNAL)]:pack(a,v)
  native=run(0x5258a8+delta,initial,case);candidate=run(symbols['audio_uart_ft_destroy_face_5258a8'],initial,case);assert native==candidate,case;count+=1
 receipt={'status':'PASS_FULL_DESTROY_FACE_CONNECTED_REAL_MEMORY_FREE','comparisons':count,'actual_helpers':['FT memory free'],'controlled_boundaries':list(mapping)+['autohint/generic/class finalizers','memory free callback'],'checks':['cached class survives driverclass mutations','glyph chain0/1/2 and fresh rereads','list finalize typed destroy-size ABI','size clear before generic','charmap then class then stream cleanup','fresh externalstream flag after callbacks','internal/freeface ordering and cleared pointers','whole2KiB/SP/R4-R11/caller guard'],'limits':['Five cleanup child providers/finalizers and memory backend controlled','No image/layout/hardware proof'],'selected':False};(D/'probe-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
finally:
 p.terminate();p.communicate(timeout=5)
