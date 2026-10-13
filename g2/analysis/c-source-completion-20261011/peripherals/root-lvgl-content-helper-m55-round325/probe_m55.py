from pathlib import Path
import subprocess,socket,time,xml.etree.ElementTree as ET,struct,json,random,hashlib
from elftools.elf.elffile import ELFFile
from unicorn.arm_const import *
D=Path(__file__).resolve().parent;source=D.parent/'root-lvgl-content-sizing-round322/helpers-unadmitted.c'
with (D/'probe.elf').open('rb') as f:
 e=ELFFile(f);symbols={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()};assert e.get_section_by_name('.native_main').data()==(D/'oracle-data-bound.bin').read_bytes()
names=['audio_uart_lv_style_property_44bdea','audio_uart_lv_obj_has_flag_any_43e11c','audio_uart_lv_obj_parent_44dca2','audio_uart_lv_obj_event_451670']
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
 u=Remote();targets={}
 for name in names:
  targets[symbols[name]&~1]=name;targets[int(name.rsplit('_',1)[1],16)+delta]=name
 for address in targets:assert command('Z1,'+hex(address)[2:]+',2')=='OK'
 stop_address=symbols['probe_stop']&~1;assert command('Z1,'+hex(stop_address)[2:]+',2')=='OK'
 import itertools
 saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11];seeds=[0x12345000+i*0x101 for i in range(8)]
 seen=[];model={};OBJ=0x20003000
 def run(entry,selector=0):
  seen.clear();u.reg_write(UC_ARM_REG_CPSR,0x01000000);u.reg_write(UC_ARM_REG_SP,0x2007ff00);u.reg_write(UC_ARM_REG_LR,stop_address|1);u.reg_write(UC_ARM_REG_R0,OBJ);u.reg_write(UC_ARM_REG_R1,selector);u.reg_write(UC_ARM_REG_PC,entry&~1)
  for r,v in zip(saved,seeds):u.reg_write(r,v)
  u.mem_write(0x2007ff00,b'\xa5'*16)
  for step in range(20):
   stop=command('c');pc=u.reg_read(UC_ARM_REG_PC)
   if pc==stop_address:break
   name=targets.get(pc);assert name,(hex(pc),stop)
   a=u.reg_read(UC_ARM_REG_R0);c=u.reg_read(UC_ARM_REG_R1);v=u.reg_read(UC_ARM_REG_R2)
   if 'style_property_' in name:seen.append(('property',a,c,v));result=model['property']
   elif 'has_flag_any_' in name:seen.append(('flags',a,c));result=model['flags']
   elif 'obj_parent_' in name:seen.append(('parent',a));result=model['parent']
   else:
    initial=struct.unpack('<2I',u.mem_read(v,8));seen.append(('event',a,c,initial));data=list(initial)
    if model['event_mode']&1:data[0]=model['event_values'][0]
    if model['event_mode']&2:data[1]=model['event_values'][1]
    u.mem_write(v,struct.pack('<2I',*data));result=0
   u.reg_write(UC_ARM_REG_R0,result);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR)&~1)
  else:raise AssertionError('Child stop bound')
  assert u.reg_read(UC_ARM_REG_SP)==0x2007ff00
  assert [u.reg_read(r) for r in saved]==seeds
  assert bytes(u.mem_read(0x2007ff00,16))==b'\xa5'*16
  return u.reg_read(UC_ARM_REG_R0),list(seen)
 total=0
 for address,name,property_id,narrow in [(0x43eee2,'audio_uart_lv_style_x_43eee2',8,False),(0x43eeec,'audio_uart_lv_style_y_43eeec',9,False),(0x43eef6,'audio_uart_lv_style_align_43eef6',10,True)]:
  for selector,value in itertools.product([0,1,0x10000,0xffffffff],[0,1,0xff,0x100,0x7fffffff,0x80000000,0xffffffff]):
   model={'property':value};native=run(address+delta,selector);candidate=run(symbols[name],selector);assert candidate==native==(value&255 if narrow else value,[('property',OBJ,selector,property_id)]);total+=1
 for flags,parent,value in itertools.product([0,1,0x60001],[0,0x20004000],[0,1,0xffff,0x10000,0x12345678]):
  model={'property':value,'flags':flags,'parent':parent};native=run(0x43f612+delta);candidate=run(symbols['audio_uart_lv_layout_positioned_43f612']);assert candidate==native
  expected=[('flags',OBJ,0x60001)]
  if not flags:
   expected.append(('parent',OBJ))
   if parent:expected.append(('property',parent,0,22))
  assert native==(int(not flags and bool(parent) and bool(value&0xffff)),expected);total+=1
 for address,name,initial,index in [(0x43ff44,'audio_uart_lv_self_width_43ff44',(0,0xe0000001),0),(0x43ff5e,'audio_uart_lv_self_height_43ff5e',(0xe0000001,0),1)]:
  for mode,v in itertools.product(range(4),[0,1,0x7fffffff,0x80000000,0xffffffff]):
   values=(v,v^0x12345678);model={'event_mode':mode,'event_values':values};native=run(address+delta);candidate=run(symbols[name]);assert candidate==native;result=values[index] if mode&(1<<index) else initial[index];assert native==(result,[('event',OBJ,52,initial)]);total+=1
 receipt={'status':'PASS_ACTUAL_M55_SIX_CONTENT_HELPER_BODIES','native_comparisons':total,'controlled_child_targets':4,'helper_instruction_bytes_unchanged':True,'data_pointer_bindings':'oracle-bindings.json','checks':['R0 bits/narrowing','ordered callee object/selector/property/flags','layout mask/parent/16bit narrowing/boolean branches','event52 initial two-word buffers and zero/one/both-axis mutations','SP/R4-R11/caller guard'],'candidate_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'selected':False,'limits':['Controlled child backends; no actual property/event engine qualification','No invalid-pointer/full-image/hardware claim']};(D/'probe-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
finally:
 p.terminate();p.communicate(timeout=5)
