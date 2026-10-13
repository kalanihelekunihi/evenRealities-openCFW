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

 u=Remote();u.mem_write(0xe000ed88,struct.pack('<I',0x00f00000));stop_address=symbols['probe_stop']&~1
 native={'guess':0x528470+delta,'new':0x524f96+delta,'read':0x5261ac+delta,'close':0x52502a+delta}
 candidate={'guess':symbols['audio_uart_ft_raccess_guess_528470']&~1,'new':symbols['audio_uart_ft_stream_new_524f96']&~1,'read':symbols['audio_uart_ft_read_mac_resource_5261ac']&~1,'close':symbols['audio_uart_ft_stream_free_52502a']&~1,'free':symbols['probe_free']&~1}
 targets={v:k for k,v in [*native.items(),*candidate.items()]}
 for address in [stop_address,*targets]:assert command('Z1,'+hex(address)[2:]+',2')=='OK'
 FS=0x20003000;LIB=FS+0x100;MEM=FS+0x200;STREAM=FS+0x300;OPENED=FS+0x340;FACE=FS+0x400;BASE=FS+0x500;ARGS=FS+0x600;NAME0=FS+0x800
 saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11];seeds=[0x12345000+i*0x101 for i in range(8)]
 def word(a):return struct.unpack('<I',u.mem_read(a,4))[0]
 def put(a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
 def run(entry,initial,case):
  u.mem_write(FS,initial);u.reg_write(UC_ARM_REG_CPSR,0x01000000);u.reg_write(UC_ARM_REG_SP,0x2007ff00);u.reg_write(UC_ARM_REG_LR,stop_address|1)
  for r,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],[LIB,STREAM,case['index'],FACE]):u.reg_write(r,v&0xffffffff)
  for r,v in zip(saved,seeds):u.reg_write(r,v)
  guard=struct.pack('<I',ARGS)+b'\xa5'*28;u.mem_write(0x2007ff00,guard);u.reg_write(UC_ARM_REG_PC,entry&~1);seen=[]
  for step in range(80):
   response=command('c');pc=u.reg_read(UC_ARM_REG_PC)
   if pc==stop_address:break
   kind=targets.get(pc);assert kind,(case,hex(pc),response);a,b,c,d=[u.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];result=0
   if kind=='guess':
    assert a==LIB and b==STREAM and c==BASE,(case,a,b,c)
    stack=u.reg_read(UC_ARM_REG_SP);offsets=word(stack);errors=word(stack+4)
    for i in range(9):
     ptr=0 if i==case['fallback'] else NAME0+i*32;put(d+i*4,ptr);put(offsets+i*4,0x100+i);put(errors+i*4,case['guess_errors'][i])
    seen.append(('guess',))
   elif kind=='new':
    assert a==LIB and word(b)==4,(case,hex(a),hex(b));path=word(b+12);i=case['fallback'] if path==BASE else (path-NAME0)//32;assert (path==BASE or path==NAME0+i*32) and 0<=i<9,(case,hex(path));result=case['new_status'][i];put(c,OPENED if result==0 else 0);seen.append(('new',i,result))
   elif kind=='read':
    assert a==LIB and b==OPENED and 0x100<=c<0x109 and d==(case['index']&0xffffffff),(case,a,b,c,d);i=c-0x100;assert word(u.reg_read(UC_ARM_REG_SP))==FACE;result=case['read_status'][i];seen.append(('read',i,result));
    if result==0:put(FACE,0x1234abcd)
   elif kind=='close':
    assert a==OPENED and b==0,(case,a,b);seen.append(('close',))
   else:
    assert kind=='free' and a==MEM and NAME0<=b<NAME0+9*32,(case,a,b);i=(b-NAME0)//32;assert b==NAME0+i*32;seen.append(('free',i));put(b,0xdeadbeef)
   u.reg_write(UC_ARM_REG_R0,result);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR)&~1)
  else:raise AssertionError(('step bound',case))
  assert u.reg_read(UC_ARM_REG_SP)==0x2007ff00 and [u.reg_read(r) for r in saved]==seeds and bytes(u.mem_read(0x2007ff00,32))==guard,(case,hex(u.reg_read(UC_ARM_REG_SP)))
  return u.reg_read(UC_ARM_REG_R0),seen,bytes(u.mem_read(FS,4096))
 import random
 rng=random.Random(396);cases=[]
 for mode in range(120):
  guess=[0]*9;new=[6]*9;read=[2]*9;fallback=-1;index=[-1,0,1,0x80000000][mode%4]
  if mode==0:read[0]=0;new[0]=0
  elif mode==1:new=[0]*9;read[8]=0
  elif mode==2:new[3]=0x51;new[4]=0;read[4]=0;new[5]=0;read[5]=0
  elif mode==3:new[3]=0;read[3]=2;new[4]=0;read[4]=0;new[5]=0;read[5]=0
  elif mode==4:new[3]=6;new[4]=0;read[4]=0
  else:
   for i in range(9):
    guess[i]=rng.choice([0,0,0,85]);new[i]=rng.choice([0,0,6,0x51]);read[i]=rng.choice([0,2,85])
   fallback=rng.randrange(9) if mode%8==0 else -1
  cases.append({'mode':mode,'index':index,'guess_errors':guess,'new_status':new,'read_status':read,'fallback':fallback})
 count=0
 for case in cases:
  initial=bytearray(rng.getrandbits(8) for _ in range(4096));base_name=b'fonts/main.ttf\0';initial[BASE-FS:BASE-FS+40]=base_name+bytes(40-len(base_name))
  for i in range(9):
   name=('candidate_'+str(i)+'.ttf').encode();candidate_addr=NAME0+i*32;initial[candidate_addr-FS:candidate_addr-FS+32]=bytes(32);initial[candidate_addr-FS:candidate_addr-FS+len(name)+1]=name+b'\0'
  for a,v in [(LIB,MEM),(MEM+8,symbols['probe_free']),(ARGS+12,BASE),(FACE,0xfeedcafe)]:struct.pack_into('<I',initial,a-FS,v)
  n=run(0x526356+delta,initial,case);c=run(symbols['audio_uart_ft_mac_path_search_526356'],initial,case);assert n==c,(case,n[:2],c[:2],[(i,x,y) for i,(x,y) in enumerate(zip(n[2],c[2])) if x!=y][:16]);count+=1
  if count%40==0:print('comparisons',count,flush=True)
 receipt={'status':'PASS_MAC_PATH_SEARCH_RULE_TRAVERSAL','comparisons':count,'native_bytes':252,'native_entry':'0x526356','actual_helpers':['selected typed nine-rule classifier','native nine-rule classifier','selected FT memory free'],'controlled_boundaries':['nine-rule candidate generation','stream new/read-resource/close','memory free callback'],'checks':['all nine rules and fallback pathname','guess error filtering','special rule 3/4 suppression after 0x51 or read failure','early success/all failure','candidate cleanup','whole4KiB/R0/SP/R4-R11/stack arg'],'limits':['Connected candidate generation and path-open/read graph not yet qualified','Sort core and initialized runtime/layout/byte/hardware unproven'],'selected':False};(D/'probe-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
finally:
 p.terminate();p.communicate(timeout=5)
