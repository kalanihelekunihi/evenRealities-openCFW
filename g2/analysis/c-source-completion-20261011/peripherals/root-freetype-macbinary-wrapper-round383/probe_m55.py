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







 FS=0x20003000;LIB=FS+0x100;STREAM=FS+0x180;OUT=FS+0x200;ARGS=FS+0x220;DATA=FS+0x300
 saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11];seeds=[0x12345000+i*0x101 for i in range(8)]
 def put(a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
 def run(entry,initial,case):
  u.mem_write(FS,initial);u.reg_write(UC_ARM_REG_CPSR,0x01000000);u.reg_write(UC_ARM_REG_SP,0x2007ff00);u.reg_write(UC_ARM_REG_LR,stop_address|1)
  for r,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],[LIB,0 if case['nullstream'] else STREAM,case['index']&0xffffffff,OUT]):u.reg_write(r,v)
  for r,v in zip(saved,seeds):u.reg_write(r,v)
  guard=struct.pack('<I',ARGS)+b'\xa5'*28;u.mem_write(0x2007ff00,guard);u.reg_write(UC_ARM_REG_PC,entry&~1);seen=[];resources=0
  for step in range(8):
   response=command('c');pc=u.reg_read(UC_ARM_REG_PC)
   if pc==stop_address:break
   n=targets.get(pc);assert n,(hex(pc),response);a,b,c,d=[u.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];stackarg=struct.unpack('<I',u.mem_read(u.reg_read(UC_ARM_REG_SP),4))[0];assert a==LIB and b==(0 if case['nullstream'] else STREAM)
   if n=='audio_uart_ft_read_mac_resource_5261ac':
    assert d==case['index']&0xffffffff and stackarg==OUT;result=case['resource'][min(resources,1)];resources+=1;seen.append(('resource',c,d,result));put(OUT,FS+0x600)
   else:
    assert c==case['index']&0xffffffff and d==OUT and stackarg==ARGS;result=case['path'];seen.append(('path',c,result));put(OUT,FS+0x640)
   u.reg_write(UC_ARM_REG_R0,result);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR)&~1)
  else:raise AssertionError('call bound')
  assert u.reg_read(UC_ARM_REG_SP)==0x2007ff00 and [u.reg_read(r) for r in saved]==seeds;assert bytes(u.mem_read(0x2007ff00,32))==guard
  return u.reg_read(UC_ARM_REG_R0),seen,bytes(u.mem_read(FS,2048))
 import itertools
 rng=random.Random(383);counts={}
 headers=[]
 h=bytearray(128);h[1]=3;headers.append(('valid-zero',bytes(h)))
 for length in [1,127,128,0x7fffffff]:
  v=bytearray(h);v[83:87]=length.to_bytes(4,'big');headers.append(('length'+str(length),bytes(v)))
 for offset,value in [(0,1),(74,1),(82,1),(1,0),(1,34),(63,1),(5,1),(83,128)]:
  v=bytearray(h);v[offset]=value;headers.append(('reject'+str((offset,value)),bytes(v)))
 for size,nullstream,index,flags,(label,header),resource,path in itertools.product([127,128],[False,True],[-1,2],[0,4],headers,[(0,0),(2,85),(0x10002,0x10055),(85,2),(0x12345678,0)],[0,0xdeadbeef]):
  initial=bytearray(rng.getrandbits(8) for _ in range(2048));initial[DATA-FS:DATA-FS+128]=header;initial[ARGS-FS]=flags
  for off,v in [(0,DATA),(4,size),(8,31),(20,0)]:struct.pack_into('<I',initial,STREAM-FS+off,v)
  case={'nullstream':nullstream,'index':index,'resource':resource,'path':path}
  for kind,address,name in [('macbinary',0x5262ac,'audio_uart_ft_read_macbinary_5262ac'),('wrapper',0x526452,'audio_uart_ft_load_mac_face_526452')]:
   native=run(address+delta,initial,case);candidate=run(symbols[name],initial,case);assert native==candidate,(kind,label,case,native[:2],candidate[:2]);counts[kind]=counts.get(kind,0)+1
 receipt={'status':'PASS_COMPLETE_MACBINARY_AND_WRAPPER','comparisons':sum(counts.values()),'by_component':counts,'native_sizes':[170,84],'actual_helpers':['stream seek/read/read_at','selected forward copy','MacBinary reader inside wrapper'],'controlled_boundaries':['resource-fork parser222bytes','path reader252bytes'],'checks':['header field/name bounds','big-endian padded resource offsets','NULL/short stream','low-byte branches/full32-bit returned errors','stacked args/output writes/whole2KiB/SP/R4-R11/caller guard'],'limits':['Resource/path parser controls; no initialized runtime/layout/hardware proof'],'selected':False};(D/'probe-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
finally:
 p.terminate();p.communicate(timeout=5)
