from pathlib import Path
import subprocess,socket,time,xml.etree.ElementTree as ET,struct,json,random,hashlib
from elftools.elf.elffile import ELFFile
from unicorn.arm_const import *
D=Path(__file__).resolve().parent;source=D/'combined-unadmitted.c'
with (D/'probe.elf').open('rb') as f:
 e=ELFFile(f);symbols={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()};assert e.get_section_by_name('.native_main').data()==Path('/tmp/opencfw-main-native.bin').read_bytes()
names=['audio_uart_display_default_get']
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
 u=Remote();targets={symbols['audio_uart_display_default_get']&~1,0x44fa1a+delta}
 for address in targets:assert command('Z1,'+hex(address)[2:]+',2')=='OK'
 stop_address=symbols['probe_stop']&~1;assert command('Z1,'+hex(stop_address)[2:]+',2')=='OK'
 saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11];seeds=[0x12345000+i*0x101 for i in range(8)]
 OBJ=0x20003000;SPEC=0x20004000;default=0
 def run(entry,arg,object_bytes,spec_bytes):
  u.reg_write(UC_ARM_REG_CPSR,0x01000000);u.reg_write(UC_ARM_REG_SP,0x2007ff00);u.reg_write(UC_ARM_REG_LR,stop_address|1);u.reg_write(UC_ARM_REG_R0,arg);u.reg_write(UC_ARM_REG_PC,entry&~1)
  for r,v in zip(saved,seeds):u.reg_write(r,v)
  u.mem_write(0x2007ff00,b'\xa5'*16);u.mem_write(OBJ,object_bytes);u.mem_write(SPEC,spec_bytes);seen=[]
  for _ in range(3):
   result=command('c');pc=u.reg_read(UC_ARM_REG_PC)
   if pc==stop_address:break
   assert pc in targets,(hex(pc),result);seen.append('default_display');u.reg_write(UC_ARM_REG_R0,default);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR)&~1)
  else:raise AssertionError('stop bound')
  assert u.reg_read(UC_ARM_REG_SP)==0x2007ff00 and [u.reg_read(r) for r in saved]==seeds
  assert bytes(u.mem_read(0x2007ff00,16))==b'\xa5'*16
  assert bytes(u.mem_read(OBJ,64))==object_bytes and bytes(u.mem_read(SPEC,64))==spec_bytes
  return u.reg_read(UC_ARM_REG_R0),seen
 rng=random.Random(331);field_count=0
 for address,name,mask,shift,fallback in [(0x44e42c,'audio_uart_lv_get_scrollbar_mode_44e42c',3,0,3),(0x44e442,'audio_uart_lv_get_scroll_dir_44e442',15,6,15)]:
  for i in range(257):
   ob=bytearray(rng.getrandbits(8) for _ in range(64));sp=bytearray(rng.getrandbits(8) for _ in range(64));value=(i&255)|(rng.getrandbits(8)<<8);struct.pack_into('<I',ob,8,0 if i==256 else SPEC);struct.pack_into('<H',sp,50,value);n=run(address+delta,OBJ,bytes(ob),bytes(sp));c=run(symbols[name],OBJ,bytes(ob),bytes(sp));assert n==c==(fallback if i==256 else (value>>shift)&mask,[]);field_count+=1
 dpi_count=0
 for value in [0,1,130,160,0x7fffffff,0x80000000,0xffffffff]:
  for arg,default in [(OBJ,0),(0,0),(0,SPEC)]:
   ob=bytearray(rng.getrandbits(8) for _ in range(64));sp=bytearray(rng.getrandbits(8) for _ in range(64));struct.pack_into('<I',ob,24,value);struct.pack_into('<I',sp,24,value);n=run(0x44fbe6+delta,arg,bytes(ob),bytes(sp));c=run(symbols['audio_uart_lv_display_dpi_44fbe6'],arg,bytes(ob),bytes(sp));assert n==c==(130 if arg==0 and default==0 else value,[] if arg else ['default_display']);dpi_count+=1
 receipt={'status':'PASS_ACTUAL_SELECTED_TU_M55_SCROLL_FIELDS_AND_DPI','field_comparisons':field_count,'dpi_comparisons':dpi_count,'candidate_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'native_payload_bytes_unchanged':True,'controlled_child_targets':1,'checks':['Byte50 low2/default3','Halfword50 bits6..9/default15','DPI word24/explicit-default-null display/default130','Ordered default-display calls','SP/R4-R11/caller guard/object-spec preservation'],'selected':False,'limits':['Default-display backend controlled','No own null-object/invalid-pointer/full-image/hardware claim']};(D/'probe-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
finally:
 p.terminate();p.communicate(timeout=5)
