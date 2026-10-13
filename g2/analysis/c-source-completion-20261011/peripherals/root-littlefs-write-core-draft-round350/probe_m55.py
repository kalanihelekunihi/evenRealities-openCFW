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
 FS=0x20003000;FILE=FS+0x100;HEAD=FS+0x300;BUFFER=FS+0x500;PATH=FS+0x700;INFO=FS+0x900;case={}
 saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11];seeds=[0x12345000+i*0x101 for i in range(8)]
 def word(a):return struct.unpack('<I',u.mem_read(a,4))[0]
 def put(a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
 def string(a):
  out=bytearray()
  for offset in range(0,512,64):
   block=bytes(u.mem_read(a+offset,64));out.extend(block.split(b'\0',1)[0])
   if b'\0' in block:return out.decode('utf-8')
  raise AssertionError('unbounded string')
 def run(entry,initial):
  u.mem_write(FS,initial);u.reg_write(UC_ARM_REG_CPSR,0x01000000);u.reg_write(UC_ARM_REG_SP,0x2007ff00);u.reg_write(UC_ARM_REG_LR,stop_address|1)
  for register,value in [(UC_ARM_REG_R0,FS),(UC_ARM_REG_R1,FILE),(UC_ARM_REG_R2,BUFFER),(UC_ARM_REG_R3,case['size']),(UC_ARM_REG_PC,entry&~1)]:u.reg_write(register,value)
  for register,value in zip(saved,seeds):u.reg_write(register,value)
  u.mem_write(0x2007ff00,b'\xa5'*16);seen=[];gaps=0
  for step in range(16):
   response=command('c');pc=u.reg_read(UC_ARM_REG_PC)
   if pc==stop_address:break
   name=targets.get(pc);assert name,(hex(pc),response)
   a=u.reg_read(UC_ARM_REG_R0);b=u.reg_read(UC_ARM_REG_R1);c=u.reg_read(UC_ARM_REG_R2);d=u.reg_read(UC_ARM_REG_R3)
   if name=='g2_file_close_error':
    args=(string(a),string(b),c);seen.append((name,args));assert c==3659
    return 'assert-boundary',seen,bytes(u.mem_read(FS,4096))
   assert (a,b)==(FS,FILE)
   if name=='g2_lfs_file_flush':
    result=case['flush'];put(FILE+48,word(FILE+48)&~0x40000);put(FILE+60,0x13579);args=(a,b)
   else:
    isgap=c!=BUFFER
    if isgap:
     assert d==1 and bytes(u.mem_read(c,4))==struct.pack('<I',BUFFER&0xffffff00)
     gaps+=1;result=0xffffffff if gaps==case['gap_error'] else 1;args=(a,b,'zero-fill',d)
     if result<0x80000000:put(FILE+52,word(FILE+52)+1)
    else:
     assert d==case['size'];result=case['result'];args=(a,b,BUFFER,d);put(FILE+52,word(FILE+52)+d)
    put(FILE+48,word(FILE+48)|0x80000);put(FILE+60,result)
   seen.append((name,args,result));u.reg_write(UC_ARM_REG_R0,result);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR)&~1)
  else:raise AssertionError('loopbound')
  assert u.reg_read(UC_ARM_REG_SP)==0x2007ff00 and [u.reg_read(r) for r in saved]==seeds
  assert bytes(u.mem_read(0x2007ff00,16))==b'\xa5'*16
  return u.reg_read(UC_ARM_REG_R0),seen,bytes(u.mem_read(FS,4096))
 import itertools
 rng=random.Random(350);count=0;assertions=0
 # Pairwise branch scenarios, includingwrapped sum andgap-fill aborts.
 scenarios=[]
 for flags,pos,stored,size,maximum in itertools.product([2,0x20002,0x802,0x40002,0x80002,0xa0802],[0,7],[0,3],[0,1,0xffffffff],[8,0xffffffff]):
  scenarios.append((flags,pos,stored,size,maximum))
 scenarios.extend((flags,7,3,1,0xffffffff) for flags in [0,1,0x20000,0x80000])
 for index,(flags,pos,stored,size,maximum) in enumerate(scenarios):
  case={'size':size,'flush':[0,1,0xffffffff][index%3],'result':[0,1,0x7fffffff,0x80000000,0xffffffff][index%5],'gap_error':[0,1,2][index%3]}
  initial=bytearray(rng.getrandbits(8) for _ in range(4096))
  for offset,value in [(116,maximum),(FILE-FS+48,flags),(FILE-FS+52,pos),(FILE-FS+44,stored)]:struct.pack_into('<I',initial,offset,value)
  native=run(0x4ce308+delta,bytes(initial));candidate=run(symbols['audio_file_lfs_write_core_4ce308'],bytes(initial))
  if native!=candidate:
   (D/'mismatch.json').write_text(json.dumps({'scenario':[flags,pos,stored,size,maximum],'case':case,'native_result':native[0],'C_result':candidate[0],'native_calls':native[1],'C_calls':candidate[1],'memory_equal':native[2]==candidate[2]},indent=2)+'\n');raise AssertionError('mismatch.json')
  count+=1;assertions+=native[0]=='assert-boundary'
  if count%100==0:print(json.dumps({'passed':count}),flush=True)
 receipt={'status':'PASS_ENTIRE_SELECTED_TU_WRITE_CORE_M55_CONTROLLED_BACKENDS','native_comparisons':count,'assertion_boundary_cases':assertions,'candidate_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'controlled_lower_backends':3,'checks':['Fullwritecore/flagreads/appendposition/filemax/wrappedaddition','Flush0/nonzeroandsignedwriteerrors/ERREDclearing','Gapzerobyteandremainingbufferpointerword/positionadvance/abort','Exactasserttext/source/3659boundary','Entire4KiBfixture/SP/R4-R11/caller16byteguard'],'selected':False,'limits':['Flush/flushedwrite/errorhelpercontrolled;connectedfilesystemengineunqualified','Assertionsstoppedbeforeerrorhelperexecution','No completeimage/layout/hardwareclaim']};(D/'probe-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
finally:
 p.terminate();p.communicate(timeout=5)
