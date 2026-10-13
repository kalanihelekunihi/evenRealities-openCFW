from pathlib import Path
import subprocess,socket,time,xml.etree.ElementTree as ET,struct,json,random,hashlib
from elftools.elf.elffile import ELFFile
from unicorn.arm_const import *
D=Path(__file__).resolve().parent;source=D/'combined-unadmitted.c'
with (D/'fatal-probe.elf').open('rb') as f:
 e=ELFFile(f);symbols={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()};assert e.get_section_by_name('.native_main').data()==(D/'fatal-oracle.bin').read_bytes()
mapping=json.loads((D/'controlled-callees.json').read_text());names=list(mapping)
delta=0x28100000-0x438000
reserve=socket.socket();reserve.bind(('127.0.0.1',0));port=reserve.getsockname()[1];reserve.close()
p=subprocess.Popen(['qemu-system-arm','-M','mps3-an547','-cpu','cortex-m55','-display','none','-monitor','none','-serial','none','-kernel',str(D/'fatal-probe.elf'),'-S','-gdb','tcp:127.0.0.1:'+str(port)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
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


 from capstone import Cs,CS_ARCH_ARM,CS_MODE_THUMB,CS_MODE_MCLASS
 decoder=Cs(CS_ARCH_ARM,CS_MODE_THUMB|CS_MODE_MCLASS)
 def word(a):return struct.unpack('<I',u.mem_read(a,4))[0]
 def string(a):
  out=bytearray()
  for offset in range(0,512,64):
   block=bytes(u.mem_read(a+offset,64));out.extend(block.split(b'\0',1)[0])
   if b'\0' in block:return out.decode()
  raise AssertionError('string')
 results=[]
 for entry in [0x48ac40+delta,symbols['audio_uart_lv_draw_buf_clear_48ac40']]:
  u.reg_write(UC_ARM_REG_CPSR,0x01000000);u.reg_write(UC_ARM_REG_SP,0x2007ff00);u.reg_write(UC_ARM_REG_LR,stop_address|1);u.reg_write(UC_ARM_REG_R0,0);u.reg_write(UC_ARM_REG_R1,0);u.reg_write(UC_ARM_REG_PC,entry&~1)
  response=command('c');pc=u.reg_read(UC_ARM_REG_PC);assert targets.get(pc)=='audio_uart_lvgl_log',(hex(pc),response)
  sp=u.reg_read(UC_ARM_REG_SP);args=(u.reg_read(UC_ARM_REG_R0),string(u.reg_read(UC_ARM_REG_R1)),u.reg_read(UC_ARM_REG_R2),string(u.reg_read(UC_ARM_REG_R3)),string(word(sp)),string(word(sp+4)),string(word(sp+8)))
  u.reg_write(UC_ARM_REG_R0,0x12345678);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR)&~1)
  fatal=None
  for step in range(30):
   pc=u.reg_read(UC_ARM_REG_PC);ins=next(decoder.disasm(bytes(u.mem_read(pc,4)),pc,count=1))
   if ins.mnemonic.startswith('str') and '[' in ins.op_str:
    value_name,addr=ins.op_str.split(', ',1);base_name=addr.strip('[]');
    if base_name in registers and value_name in registers:
     address=int.from_bytes(reg(base_name),'little');value=int.from_bytes(reg(value_name),'little')
     if address==0xffffffff:fatal=(address,value);break
   command('s')
  assert fatal==(0xffffffff,0),(args,fatal);results.append({'logger':args,'fatal_store':fatal,'scope':'execution stopped immediately before native-fatal store'})
 assert results[0]==results[1],results
 receipt={'status':'PASS_NULL_ASSERT_LOG_AND_FATAL_STORE_BOUNDARY','comparisons':1,'results':results,'ordinary_pointer_words_rebound':5,'instructions_unchanged':True,'limits':['Stops before invalid-address store; no hardware fault recovery claim']};(D/'fatal-probe-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
finally:
 p.terminate();p.communicate(timeout=5)
