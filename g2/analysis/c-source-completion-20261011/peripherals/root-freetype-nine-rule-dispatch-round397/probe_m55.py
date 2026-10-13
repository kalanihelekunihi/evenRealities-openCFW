from pathlib import Path
import subprocess,socket,time,xml.etree.ElementTree as ET,struct,json,random,hashlib
from elftools.elf.elffile import ELFFile
from unicorn.arm_const import *
D=Path(__file__).resolve().parent;source=D/'combined-unadmitted.c'
with (D/'probe.elf').open('rb') as f:
 e=ELFFile(f);symbols={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()};assert e.get_section_by_name('.native_main').data()==(D/'oracle-data-bound.bin').read_bytes()
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

 u=Remote();u.mem_write(0xe000ed88,struct.pack('<I',0x00f00000));stop_address=symbols['probe_stop']&~1;seek=symbols['probe_seek']&~1
 entries=['528508','528524','528540','5285d4','52857e','52862c','528650','528674','5286b2'];targets={seek:('seek',-1)}
 for i,n in enumerate(entries):targets[symbols['audio_uart_ft_mac_rule_'+n]&~1]=('handler',i);targets[int(n,16)+delta]=('handler',i)
 for address in [stop_address,*targets]:assert command('Z1,'+hex(address)[2:]+',2')=='OK'
 FS=0x20003000;LIB=FS+0x100;STREAM=FS+0x200;BASE=FS+0x300;NAMES=FS+0x400;OFFSETS=FS+0x500;ERRORS=FS+0x600;NAMEVAL=FS+0x800
 saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11];seeds=[0x12345000+i*0x101 for i in range(8)]
 def word(a):return struct.unpack('<I',u.mem_read(a,4))[0]
 def put(a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
 def run(entry,initial,case):
  u.mem_write(FS,initial);u.reg_write(UC_ARM_REG_CPSR,0x01000000);u.reg_write(UC_ARM_REG_SP,0x2007ff00);u.reg_write(UC_ARM_REG_LR,stop_address|1)
  stream=0 if case['mode']=='null' else STREAM
  for r,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],[LIB,stream,BASE,NAMES]):u.reg_write(r,v)
  for r,v in zip(saved,seeds):u.reg_write(r,v)
  guard=struct.pack('<II',OFFSETS,ERRORS)+b'\xa5'*24;u.mem_write(0x2007ff00,guard);u.reg_write(UC_ARM_REG_PC,entry&~1);seen=[];seek_i=0
  for step in range(32):
   response=command('c');pc=u.reg_read(UC_ARM_REG_PC)
   if pc==stop_address:break
   target=targets.get(pc);assert target,(case,hex(pc),response);kind,i=target;a,b,c,d=[u.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]]
   if kind=='seek':
    assert a==STREAM and b==0 and c==0 and d==0,(case,a,b,c,d);i=seek_i;seek_i+=1;result=case['seek_fail'][i];seen.append(('seek',i,result))
   else:
    assert a==LIB and b==stream and c==BASE and d==NAMES+i*4,(case,a,b,c,d,i);assert word(u.reg_read(UC_ARM_REG_SP))==OFFSETS+i*4
    ptr=NAMEVAL+i*32 if case['has_name'][i] else 0;put(d,ptr);put(OFFSETS+i*4,0x100+i);result=case['handler_status'][i];seen.append(('handler',i,result,ptr))
   u.reg_write(UC_ARM_REG_R0,result);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR)&~1)
  else:raise AssertionError(('step bound',case))
  assert u.reg_read(UC_ARM_REG_SP)==0x2007ff00 and [u.reg_read(r) for r in saved]==seeds and bytes(u.mem_read(0x2007ff00,32))==guard,(case,hex(u.reg_read(UC_ARM_REG_SP)))
  return seen,bytes(u.mem_read(FS,4096))
 import random
 rng=random.Random(397);cases=[]
 for j in range(120):
  mode=['null','memory','callback'][j%3]
  seek_fail=[rng.choice([0,0,0,1]) for _ in range(9)] if mode=='callback' else [0]*9
  handler_status=[rng.choice([0,2,85]) for _ in range(9)];has_name=[rng.choice([False,True]) for _ in range(9)]
  if j<3:seek_fail=[0]*9;handler_status=[0]*9;has_name=[True]*9
  cases.append({'mode':mode,'seek_fail':seek_fail,'handler_status':handler_status,'has_name':has_name})
 count=0
 for case in cases:
  initial=bytearray(rng.getrandbits(8) for _ in range(4096));initial[BASE-FS:BASE-FS+40]=b'fonts/main.ttf\0'+bytes(25)
  for i in range(9):
   name=('candidate_'+str(i)).encode();addr=NAMEVAL+i*32;initial[addr-FS:addr-FS+32]=bytes(32);initial[addr-FS:addr-FS+len(name)+1]=name+b'\0'
  for a,v in [(STREAM+4,128),(STREAM+8,7),(STREAM+20,symbols['probe_seek'] if case['mode']=='callback' else 0)]:struct.pack_into('<I',initial,a-FS,v)
  n=run(0x528470+delta,initial,case);c=run(symbols['audio_uart_ft_raccess_guess_528470'],initial,case);assert n==c,(case,n[0],c[0],[(i,x,y) for i,(x,y) in enumerate(zip(n[1],c[1])) if x!=y][:16]);count+=1
  if count%40==0:print('comparisons',count,flush=True)
 receipt={'status':'PASS_NINE_RULE_DISPATCHER_CONTRACT','comparisons':count,'native_bytes':110,'native_entry':'0x528470','actual_helpers':['selected stream seek','typed nine-rule table'],'controlled_boundaries':['nine handler return/name/offset','stream seek callback'],'checks':['null/memory/callback stream','seek error filtering','all nine handler slots','name reset and offset/error writes','whole4KiB/SP/R4-R11/two stacked args/caller guard'],'limits':['Handler graph qualification is separately bounded','Runtime/layout/byte/hardware unproven'],'selected':False};(D/'probe-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
finally:
 p.terminate();p.communicate(timeout=5)
