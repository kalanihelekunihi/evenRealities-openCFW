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

 u=Remote();stop=symbols['probe_stop']&~1
 assert hashlib.sha256(Path('/tmp/opencfw-main-native.bin').read_bytes()).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
 assert all('d'+str(i) in registers for i in range(8,16))
 delta=0x28100000-0x438000
 assert command('Z1,'+hex(stop)[2:]+',2')=='OK'
 BUF=0x20003100;FS=0x20003000;TOP=0x2007ff00
 core=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
 def put_register(name,value,width):
  assert command('P'+hex(registers[name])[2:]+'='+int(value).to_bytes(width,'little').hex())=='OK'
 def read_fp():return [int.from_bytes(reg('d'+str(i)),'little') for i in range(8,16)]
 def init(case,blob):
  u.mem_write(0xe000ed88,struct.pack('<I',0x00f00000))
  u.mem_write(FS,blob);u.reg_write(UC_ARM_REG_CPSR,0x01000000)
  u.reg_write(UC_ARM_REG_SP,TOP);u.reg_write(UC_ARM_REG_LR,stop|1)
  for r,v in zip(core,case['core']):u.reg_write(r,v)
  for i,v in enumerate(case['fp']):put_register('d'+str(i+8),v,8)
  u.mem_write(TOP,b'\xa5'*32)
 def snapshot():
  return {'r0':u.reg_read(UC_ARM_REG_R0),'sp':u.reg_read(UC_ARM_REG_SP),
          'core':[u.reg_read(r) for r in core],'fp':read_fp(),
          'buffer':bytes(u.mem_read(BUF,128)),
          'guard':bytes(u.mem_read(TOP,32))}
 def run_setjmp(entry,case,blob):
  init(case,blob);u.reg_write(UC_ARM_REG_R0,BUF);u.reg_write(UC_ARM_REG_PC,entry&~1)
  response=command('c');assert u.reg_read(UC_ARM_REG_PC)==stop,(hex(entry),response)
  out=snapshot();checks=(out['r0']==0,out['sp']==TOP,out['core']==case['core'],out['fp']==case['fp'],out['guard']==b'\xa5'*32)
  assert all(checks),(hex(entry),checks,hex(out['r0']),hex(out['sp']),out['fp'][:2],case['fp'][:2])
  return out
 def run_longjmp(entry,case,blob,buffer,value):
  init(case,blob);u.mem_write(BUF,buffer)
  u.reg_write(UC_ARM_REG_SP,TOP+128);u.reg_write(UC_ARM_REG_LR,0x12345001)
  for r,v in zip(core,case['mutated_core']):u.reg_write(r,v)
  for i,v in enumerate(case['mutated_fp']):put_register('d'+str(i+8),v,8)
  u.reg_write(UC_ARM_REG_R0,BUF);u.reg_write(UC_ARM_REG_R1,value);u.reg_write(UC_ARM_REG_PC,entry&~1)
  response=command('c');assert u.reg_read(UC_ARM_REG_PC)==stop,(hex(entry),response)
  out=snapshot();assert out['r0']==(value or 1) and out['sp']==TOP and out['core']==case['core'] and out['fp']==case['fp'] and out['guard']==b'\xa5'*32
  return out
 rng=random.Random(409);count=0
 for j in range(20):
  case={'core':[rng.getrandbits(32) for _ in range(8)],'fp':[rng.getrandbits(64) for _ in range(8)],
        'mutated_core':[rng.getrandbits(32) for _ in range(8)],'mutated_fp':[rng.getrandbits(64) for _ in range(8)]}
  blob=bytes(rng.getrandbits(8) for _ in range(4096))
  native=run_setjmp(0x56777c+delta,case,blob)
  candidate=run_setjmp(symbols['setjmp'],case,blob)
  assert native==candidate,(j,'setjmp');count+=1
  for value in [0,1,5]:
   n=run_longjmp(0x567790+delta,case,blob,native['buffer'],value)
   c=run_longjmp(symbols['longjmp'],case,blob,candidate['buffer'],value)
   assert n==c,(j,value,'longjmp');count+=1
 receipt={'status':'PASS_NATIVE_NEWLIB_ARM_JUMP_REGISTER_AND_BUFFER_COMPARISON','comparisons':count,'native_entries':['0x56777c','0x567790'],'candidate_source':'pinned Newlib ARM setjmp.S','buffer_written_bytes':104,'native_gray_worker_next_field_offset':128,'analysis_header_buffer_bytes':128,'newlib_default_header_buffer_bytes':160,'checks':['r4-r11,SP,LR,d8-d15 save/restore','zero and nonzero longjmp return','128-byte buffer and untouched tail','stack guard'],'limits':['QEMU Cortex-M55 samples are not initialized product runtime proof','Newlib header size differs from native FreeType layout; use native 128-byte overlay for analysis','Production provider admission and image layout remain open']}
 (D/'probe-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
 print(json.dumps(receipt),flush=True)
finally:
 p.terminate();p.communicate(timeout=5)

