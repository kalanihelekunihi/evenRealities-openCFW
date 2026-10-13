from pathlib import Path
import subprocess,socket,time,xml.etree.ElementTree as ET,struct,json,random,hashlib
from elftools.elf.elffile import ELFFile
from unicorn.arm_const import *
D=Path(__file__).resolve().parent;source=D/'combined-unadmitted.c'
with (D/'probe.elf').open('rb') as f:
 e=ELFFile(f);symbols={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()};assert e.get_section_by_name('.native_main').data()==(D/'native.bin').read_bytes()
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
 u=Remote();u.mem_write(0xe000ed88,struct.pack('<I',0x00f00000));stop_address=symbols['probe_stop']&~1;assert command('Z1,'+hex(stop_address)[2:]+',2')=='OK'
 RAM=0x20003000;saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11];seeds=[0x12345000+i*0x101 for i in range(8)]
 def run(entry,initial,destination,source,capacity):
  u.mem_write(RAM,initial);u.reg_write(UC_ARM_REG_CPSR,0x01000000);u.reg_write(UC_ARM_REG_SP,0x2007ff00);u.reg_write(UC_ARM_REG_LR,stop_address|1)
  for register,value in [(UC_ARM_REG_R0,destination),(UC_ARM_REG_R1,source),(UC_ARM_REG_R2,capacity),(UC_ARM_REG_PC,entry&~1)]:u.reg_write(register,value)
  for register,value in zip(saved,seeds):u.reg_write(register,value)
  u.mem_write(0x2007ff00,b'\xa5'*16);response=command('c');assert u.reg_read(UC_ARM_REG_PC)==stop_address,(response,hex(u.reg_read(UC_ARM_REG_PC)))
  assert u.reg_read(UC_ARM_REG_SP)==0x2007ff00 and [u.reg_read(r) for r in saved]==seeds,(hex(entry),hex(u.reg_read(UC_ARM_REG_SP)),[hex(u.reg_read(r)) for r in saved])
  assert bytes(u.mem_read(0x2007ff00,16))==b'\xa5'*16
  return u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(RAM,0x1000))
 rng=random.Random(349);count=0
 for length in [0,1,3,4,15,63,255]:
  for sa in range(4):
   for da in range(4):
    for capacity in sorted(set([0,1,length,length+1,length+7,0xffffffff])):
     initial=bytearray(rng.getrandbits(8) for _ in range(4096));src=RAM+0x100+sa;dst=RAM+0x700+da
     initial[src-RAM:src-RAM+length+1]=bytes(1+rng.randrange(255) for _ in range(length))+b'\0'
     expected=bytearray(initial)
     if capacity:
      amount=min(length,capacity-1);expected[dst-RAM:dst-RAM+amount]=initial[src-RAM:src-RAM+amount];expected[dst-RAM+amount]=0
     native=run(0x454778+delta,bytes(initial),dst,src,capacity);candidate=run(symbols['audio_uart_lv_strlcpy_454778'],bytes(initial),dst,src,capacity)
     assert native==candidate,(length,sa,da,capacity,'source/native mismatch')
     assert native==(length,bytes(expected)),(length,sa,da,capacity,'contract mismatch');count+=1
  print(json.dumps({'length':length,'cumulative_pass':count}),flush=True)
 receipt={'status':'PASS_ACTUAL_SELECTED_TU_CONNECTED_BOUNDED_COPY_M55','native_comparisons':count,'controlled_lower_backends':0,'actual_native_and_selected_strlen_copy_execute':True,'candidate_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'checks':['Seven lengths0..255/allsourceanddestinationalignments','Zero/one/exact/truncated/oversize/UINT32_MAXcapacity','Originalfullstringlengthreturn/exactnulplacement','Entire4KiBfixtureandindependentexpectedcontract','SP/R4-R11/caller16byteguard'],'selected':False,'limits':['Validnulterminatedsource/disjointregionsonly;overlapandinvalidpointersunqualified','No completeimage/layout/byteidentity/hardwareclaim']};(D/'probe-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
finally:
 p.terminate();p.communicate(timeout=5)
