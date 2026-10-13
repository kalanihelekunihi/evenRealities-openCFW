from pathlib import Path
import subprocess,socket,time,xml.etree.ElementTree as ET,struct,json,random,hashlib
from elftools.elf.elffile import ELFFile
from unicorn.arm_const import *
D=Path(__file__).resolve().parent;source=D/'combined-unadmitted.c'
with (D/'connected-probe.elf').open('rb') as f:
 e=ELFFile(f);symbols={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()};assert e.get_section_by_name('.native_main').data()==(D/'connected-oracle.bin').read_bytes()
mapping=json.loads((D/'connected-controlled.json').read_text());names=list(mapping)
delta=0x28100000-0x438000
reserve=socket.socket();reserve.bind(('127.0.0.1',0));port=reserve.getsockname()[1];reserve.close()
p=subprocess.Popen(['qemu-system-arm','-M','mps3-an547','-cpu','cortex-m55','-display','none','-monitor','none','-serial','none','-kernel',str(D/'connected-probe.elf'),'-S','-gdb','tcp:127.0.0.1:'+str(port)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
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







 FS=0x20003000;LIB=FS+0x100;MEM=FS+0x200;STREAM=FS+0x300;BUFFER=FS+0x500;NEW=FS+0x700;OUT=FS+0x800;FACE=FS+0x900;MODULE=FS+0xa00;NAME=FS+0xb00
 for n in ['probe_alloc','probe_free']:
  targets[symbols[n]&~1]=n;assert command('Z1,'+hex(symbols[n]&~1)[2:]+',2')=='OK'
 saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11];seeds=[0x12345000+i*0x101 for i in range(8)]
 def word(a):return struct.unpack('<I',u.mem_read(a,4))[0]
 def put(a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
 def string(a):
  out=bytearray()
  for off in range(0,64):
   c=bytes(u.mem_read(a+off,1))[0]
   if not c:return out.decode()
   out.append(c)
  raise AssertionError('string')
 def run(entry,native,kind,initial,case):
  u.mem_write(FS,initial);u.reg_write(UC_ARM_REG_CPSR,0x01000000);u.reg_write(UC_ARM_REG_SP,0x2007ff00);u.reg_write(UC_ARM_REG_LR,stop_address|1)
  if kind=='ps':args=[LIB,STREAM,case['index']&0xffffffff,123];stack=struct.pack('<II',MODULE,OUT)+b'\xa5'*24
  elif kind=='buffer':args=[LIB,BUFFER,64,case['index']&0xffffffff];stack=struct.pack('<II',NAME if case['driver'] else 0,OUT)+b'\xa5'*24
  elif kind=='new':args=[case['library'],case['base'],64,symbols['audio_uart_ft_memory_stream_close_525b02']];stack=struct.pack('<I',OUT)+b'\xa5'*28
  else:args=[NEW,0,0,0];stack=b'\xa5'*32
  for reg,value in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],args):u.reg_write(reg,value)
  for reg,value in zip(saved,seeds):u.reg_write(reg,value)
  u.mem_write(0x2007ff00,stack);u.reg_write(UC_ARM_REG_PC,entry&~1);seen=[];pos=0;allocs=0;seekcalls=0
  for step in range(40):
   response=command('c');pc=u.reg_read(UC_ARM_REG_PC)
   if pc==stop_address:break
   n=targets.get(pc);assert n,(hex(pc),response);a,b,c,d=[u.reg_read(reg) for reg in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];result=0x87654321
   if n in ['audio_uart_ft_stream_read_ulong_528ba8','audio_uart_ft_stream_read_ushort_528b4a']:
    width=4 if 'ulong' in n else 2;value=int.from_bytes(case['data'][pos:pos+width],'big');assert a==STREAM;put(b,0);pos+=width;put(STREAM+8,16+pos);call=(n,value);result=value
   elif n=='audio_uart_ft_stream_skip_528914':assert a==STREAM;pos+=b;put(STREAM+8,16+pos);call=(n,b);result=0
   elif n=='audio_uart_ft_stream_seek_5288e0':assert a==STREAM;call=(n,a,b);result=case.get('seek_errors',[case['seek']]*3)[seekcalls];seekcalls+=1;put(STREAM+8,b)
   elif n=='audio_uart_ft_stream_read_528928':assert a==STREAM and b==BUFFER;call=(n,a,b,c);result=case['read'];u.mem_write(BUFFER,b'R'*min(c,128))
   elif n=='probe_alloc':
    allocs+=1;call=(n,a,b);assert a==MEM;result=0 if case['fail_alloc']==allocs else BUFFER if kind=='ps' and allocs==1 else NEW
   elif n=='probe_free':assert a==MEM and b in [BUFFER,NEW];call=(n,a,b);put(b,0xdeadbeef)
   elif n=='audio_uart_ft_get_module_5273b8':assert a==LIB;call=(n,a,string(b));result=MODULE
   else:
    assert n=='audio_uart_ft_open_face_internal_5264a6' and a==LIB and d==OUT;sp=u.reg_read(UC_ARM_REG_SP);assert word(sp)==0
    flags=word(b);assert flags in [2,10] and word(b+16)==NEW
    call=(n,a,flags,c,d,word(b+20) if flags&8 else None,0);put(NEW+28,MEM);result=case['face_error']
    if not result:put(OUT,FACE)
   seen.append(call);u.reg_write(UC_ARM_REG_R0,result);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR)&~1)
  else:raise AssertionError('bound')
  assert u.reg_read(UC_ARM_REG_SP)==0x2007ff00 and [u.reg_read(reg) for reg in saved]==seeds;assert bytes(u.mem_read(0x2007ff00,32))==stack
  memory=bytearray(u.mem_read(FS,4096));close=struct.unpack_from('<I',memory,NEW-FS+24)[0]
  if close in [0x525b03+delta,symbols['audio_uart_ft_memory_stream_close_525b02']]:struct.pack_into('<I',memory,NEW-FS+24,0x525b03)
  return (None if kind=='close' else u.reg_read(UC_ARM_REG_R0)),seen,bytes(memory)
 import itertools
 rng=random.Random(381);cases=[]
 defaults={'index':0,'driver':1,'seek':0,'read':0,'face_error':0,'fail_alloc':0,'size':512,'tag':0x43494420,'offset':100,'length':150,'library':LIB,'base':BUFFER}
 def add(kind,**kw):cases.append((kind,dict(defaults,**kw)))
 for tag,index,size,seek,read,face_error,fail in itertools.product([0x43494420,0x54595031,0x12345678],[-1,0,0x10000],[50,512],[0,6],[0,85],[0,2,6],[0,1,2]):add('ps',tag=tag,index=index,size=size,seek=seek,read=read,face_error=face_error,fail_alloc=fail)
 for driver,index,face_error,fail in itertools.product([0,1],[-1,0,2],[0,2,6],[0,1]):add('buffer',driver=driver,index=index,face_error=face_error,fail_alloc=fail)
 for library,base,fail in itertools.product([0,LIB],[0,BUFFER],[0,1]):add('new',library=library,base=base,fail_alloc=fail)
 for error,rewind in itertools.product([2,0x10002],[0,6]):add('ps',face_error=error,seek_errors=[0,rewind])
 for offset,length,index in itertools.product([0xffffffff,490],[0,21,150],[-0x80000000,0x7fffffff]):add('ps',offset=offset,length=length,index=index)
 add('close');counts={}
 for kind,case in cases:
  case['data']=struct.pack('>IH',0x74797031,1)+bytes(6)+struct.pack('>4I',case['tag'],0,case['offset'],case['length']);initial=bytearray(rng.getrandbits(8) for _ in range(4096))
  for a,v in [(LIB,MEM),(MEM+4,symbols['probe_alloc']),(MEM+8,symbols['probe_free']),(STREAM+8,16),(STREAM+4,case['size']),(FACE+8,0xffffffff),(NEW,BUFFER),(NEW+4,64),(NEW+28,MEM),(NEW+24,symbols['audio_uart_ft_memory_stream_close_525b02'])]:struct.pack_into('<I',initial,a-FS,v)
  initial[NAME-FS:NAME-FS+4]=b'cid\0';address,name={'ps':(0x525d32,'audio_uart_ft_open_ps_sfnt_525d32'),'buffer':(0x525b6e,'audio_uart_ft_open_face_from_buffer_525b6e'),'new':(0x525b20,'audio_uart_ft_new_memory_stream_525b20'),'close':(0x525b02,'audio_uart_ft_memory_stream_close_525b02')}[kind];native=run(address+delta,True,kind,initial,case);candidate=run(symbols[name],False,kind,initial,case)
  if native!=candidate:
   (D/'connected-mismatch.json').write_text(json.dumps({'kind':kind,'case':{k:v for k,v in case.items() if k!='data'},'native':native[:2],'C':candidate[:2],'memory_equal':native[2]==candidate[2]},indent=2)+'\n');raise AssertionError('connected-mismatch.json')
  counts[kind]=counts.get(kind,0)+1
  if sum(counts.values())%200==0:print('comparisons',sum(counts.values()),flush=True)
 receipt={'status':'PASS_CONNECTED_SFNT_PS_BUFFER_MEMORY_OWNERSHIP','comparisons':sum(counts.values()),'per_path':counts,'actual_helpers':['SFNT locator','PS wrapper','buffer opener','new memory stream','memory close','FT alloc/zero/free','stream open-memory/close'],'controlled_boundaries':list(mapping)+['allocation/free callbacks'],'limits':['Driver parser/module and stream services controlled; real runtime remains open','Open-face boundary initializes stream allocator as valid FT_Stream_New consumer contract','No image/layout/hardware proof'],'selected':False};(D/'connected-probe-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
finally:
 p.terminate();p.communicate(timeout=5)
