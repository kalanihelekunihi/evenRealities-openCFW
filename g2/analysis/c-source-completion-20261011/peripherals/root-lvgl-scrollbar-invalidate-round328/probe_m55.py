from pathlib import Path
import subprocess,socket,time,xml.etree.ElementTree as ET,struct,json,random,hashlib
from elftools.elf.elffile import ELFFile
from unicorn.arm_const import *
D=Path(__file__).resolve().parent;source=D/'combined-unadmitted.c'
with (D/'probe.elf').open('rb') as f:
 e=ELFFile(f);symbols={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()};assert e.get_section_by_name('.native_main').data()==Path('/tmp/opencfw-main-native.bin').read_bytes()
names=['audio_uart_lv_get_scrollbar_areas_44eb28','audio_uart_display_invalidate_area']
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
 u=Remote();targets={symbols[names[0]]&~1:'areas',0x44eb28+delta:'areas',symbols[names[1]]&~1:'invalidate',0x4405d4+delta:'invalidate'}
 for address in targets:assert command('Z1,'+hex(address)[2:]+',2')=='OK'
 stop_address=symbols['probe_stop']&~1;assert command('Z1,'+hex(stop_address)[2:]+',2')=='OK'
 import itertools
 saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11];seeds=[0x12345000+i*0x101 for i in range(8)]
 OBJ=0x20003000;seen=[];model={}
 def pack(row):return struct.pack('<4I',*(v&0xffffffff for v in row))
 def words(a):return struct.unpack('<4I',u.mem_read(a,16))
 def run(entry,area=None):
  seen.clear();u.reg_write(UC_ARM_REG_CPSR,0x01000000);u.reg_write(UC_ARM_REG_SP,0x2007ff00);u.reg_write(UC_ARM_REG_LR,stop_address|1);u.reg_write(UC_ARM_REG_R0,OBJ);u.reg_write(UC_ARM_REG_PC,entry&~1)
  for r,v in zip(saved,seeds):u.reg_write(r,v)
  u.mem_write(0x2007ff00,b'\xa5'*16);u.mem_write(OBJ,pack(area) if area is not None else b'\x5a'*16);pointers={};invalidations=0
  for step in range(12):
   stop=command('c');pc=u.reg_read(UC_ARM_REG_PC)
   if pc==stop_address:break
   role=targets.get(pc);assert role,(hex(pc),stop)
   a=u.reg_read(UC_ARM_REG_R0);h=u.reg_read(UC_ARM_REG_R1);v=u.reg_read(UC_ARM_REG_R2);assert a==OBJ
   if role=='areas':
    assert h%4==v%4==0 and abs(h-v)>=16
    pointers={h:'h',v:'v'};seen.append(('areas',a));u.mem_write(h,pack(model['h']));u.mem_write(v,pack(model['v']));vertical=v
   else:
    assert h in pointers;axis=pointers[h];seen.append(('invalidate',a,axis,words(h)));invalidations+=1
    if axis=='h' and model['mutation']:
     u.mem_write(vertical,pack([0,0,-1,-1] if model['mutation']==1 else [0,0,1,1]))
   u.reg_write(UC_ARM_REG_R0,0xdeadbeef);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR)&~1)
  else:raise AssertionError('Child stop bound')
  assert u.reg_read(UC_ARM_REG_SP)==0x2007ff00
  assert [u.reg_read(r) for r in saved]==seeds
  assert bytes(u.mem_read(0x2007ff00,16))==b'\xa5'*16
  if area is not None:
   assert bytes(u.mem_read(OBJ,16))==pack(area)
   return u.reg_read(UC_ARM_REG_R0)
  assert bytes(u.mem_read(OBJ,16))==b'\x5a'*16
  return list(seen)
 rng=random.Random(328);size_cases=list(itertools.product([0,1,0x7fffffff,0xffffffff],repeat=4))+[tuple(rng.getrandbits(32) for _ in range(4)) for _ in range(256)]
 for row in size_cases:
  n=run(0x450b80+delta,row);c=run(symbols['audio_uart_lv_area_size_450b80'],row);expected=((row[2]-row[0]+1)*(row[3]-row[1]+1))&0xffffffff;assert n==c==expected
 pool=[(0,0,-1,-1),(0,0,0,0),(0,0,65535,65535),(0,0,0x7fffffff,1),(-2,-3,5,7),(0x7fffffff,0xffffffff,0x80000000,0),(0,0,-2,-2),(0,0,1,-1)]
 cases=[(h,v,m) for h,v,m in itertools.product(pool,pool,range(3))]+[(tuple(rng.getrandbits(32) for _ in range(4)),tuple(rng.getrandbits(32) for _ in range(4)),rng.randrange(3)) for _ in range(64)]
 traces={}
 for i,(h,v,mutation) in enumerate(cases):
  model={'h':h,'v':v,'mutation':mutation};n=run(0x44f2ca+delta);c=run(symbols['audio_uart_lv_scrollbar_invalidate_44f2ca']);assert n==c,(i,model,n,c);key=tuple(t[2] for t in n if t[0]=='invalidate');traces[str(key)]=traces.get(str(key),0)+1
 receipt={'status':'PASS_ACTUAL_SELECTED_TU_M55_AREA_SIZE_AND_SCROLLBAR_INVALIDATION','area_size_comparisons':len(size_cases),'scrollbar_comparisons':len(cases),'candidate_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'native_payload_bytes_unchanged':True,'controlled_child_targets':2,'actual_area_size_executes':True,'invalidate_axis_trace_counts':traces,'checks':['Inclusive 32bit extents/product wrap','Ordered getareas/invalidate calls and area values','Post-horizontal-invalidation vertical buffer mutations','SP/R4-R11/caller guard/object preservation'],'limits':['Getareas and invalidate bodies controlled, not qualified here','No invalid pointer/full-image/hardware claim'],'selected':False};(D/'probe-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
finally:
 p.terminate();p.communicate(timeout=5)
