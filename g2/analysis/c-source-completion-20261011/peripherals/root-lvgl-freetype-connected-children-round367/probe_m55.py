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




 FS=0x20003000;OBJECT=FS+0x100;VTABLE=FS+0x300;ALT=FS+0x400;MEM=FS+0x500;USER=FS+0x600
 targets[symbols['probe_cache_destroy']&~1]='probe_cache_destroy';assert command('Z1,'+hex(symbols['probe_cache_destroy']&~1)[2:]+',2')=='OK'
 saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11];seeds=[0x12345000+i*0x101 for i in range(8)]
 def word(a):return struct.unpack('<I',u.mem_read(a,4))[0]
 def put(a,v):u.mem_write(a,struct.pack('<I',v))
 def run(entry,kind,initial,case):
  u.mem_write(FS,initial);u.reg_write(UC_ARM_REG_CPSR,0x01000000);u.reg_write(UC_ARM_REG_SP,0x2007ff00);u.reg_write(UC_ARM_REG_LR,stop_address|1);u.reg_write(UC_ARM_REG_R0,OBJECT);u.reg_write(UC_ARM_REG_R1,USER);u.reg_write(UC_ARM_REG_PC,entry&~1)
  for register,value in zip(saved,seeds):u.reg_write(register,value)
  u.mem_write(0x2007ff00,b'\xa5'*32);seen=[]
  for step in range(12):
   response=command('c');pc=u.reg_read(UC_ARM_REG_PC)
   if pc==stop_address:break
   name=targets.get(pc);assert name,(hex(pc),response);a,b,c=[u.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2]];result=0xabcdef
   if name=='audio_uart_ft_new_memory_5676a0':args=();result=case['memory']
   elif name=='audio_uart_ft_new_library_5274b2':assert (a,b)==(MEM,OBJECT);args=(a,b);put(OBJECT,0x12345678);result=case['error']
   elif name=='audio_uart_ft_done_memory_5676c6':assert a==MEM;args=(a,);put(OBJECT,0x87654321)
   elif name=='audio_uart_ft_add_default_modules_5242fc':assert a==0x12345678;args=(a,);put(OBJECT,0x55555555)
   elif name=='audio_uart_ft_set_transform_525444':
    assert a==OBJECT and c==0;matrix=struct.unpack('<4i',u.mem_read(b,16));assert matrix==(65536,13930,0,65536);args=(a,matrix,c);put(OBJECT+16,0x99999999)
   elif name=='audio_uart_lv_lock_core':assert a==OBJECT+28;args=(a,);put(OBJECT,ALT);result=case['lock_return']
   elif name=='probe_cache_destroy':assert (a,b)==(OBJECT,USER) and word(OBJECT)==ALT;args=(a,b);put(OBJECT+28,case['mutex_after'])
   elif name=='audio_uart_lv_unlock_core':assert a==OBJECT+28;args=(a,);result=case['unlock_return']
   elif name=='audio_queue_delete':assert a==0x778899 and word(OBJECT+28)==1;args=(a,)
   elif name=='audio_uart_lv_heap_free':assert a==OBJECT and word(OBJECT+28)==0;args=(a,);put(OBJECT+40,0xdead1234)
   else:raise AssertionError(name)
   seen.append((name,args,result));u.reg_write(UC_ARM_REG_R0,result);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR)&~1)
  else:raise AssertionError('bound')
  assert u.reg_read(UC_ARM_REG_SP)==0x2007ff00 and [u.reg_read(r) for r in saved]==seeds;assert bytes(u.mem_read(0x2007ff00,32))==b'\xa5'*32
  return (u.reg_read(UC_ARM_REG_R0) if kind=='init' else None),seen,bytes(u.mem_read(FS,2048))
 rng=random.Random(367);cases=[]
 import itertools
 for memory,error in itertools.product([0,MEM],[0,1,7,0x80000000,0xffffffff]):cases.append(('init',{'memory':memory,'error':error}))
 for mutex,lock,unlock in itertools.product([0,1],[0,1,0xffffffff],[0,1,0xffffffff]):cases.append(('destroy',{'mutex_after':mutex,'lock_return':lock,'unlock_return':unlock}))
 for i in range(8):cases.append(('italic',{}))
 counts={}
 for kind,case in cases:
  initial=bytearray(rng.getrandbits(8) for _ in range(2048));struct.pack_into('<I',initial,OBJECT-FS,VTABLE);struct.pack_into('<I',initial,VTABLE-FS+8,0);struct.pack_into('<I',initial,ALT-FS+8,symbols['probe_cache_destroy']);struct.pack_into('<II',initial,OBJECT-FS+28,1,0x778899)
  address,name={'init':(0x52431c,'audio_uart_ft_init_freetype_52431c'),'italic':(0x4b1fd4,'audio_uart_ft_italic_transform_4b1fd4'),'destroy':(0x4d4d6a,'audio_uart_lv_cache_destroy_4d4d6a')}[kind]
  native=run(address+delta,kind,initial,case);candidate=run(symbols[name],kind,initial,case);assert native==candidate,(kind,case,native[:2],candidate[:2]);counts[kind]=counts.get(kind,0)+1
 receipt={'status':'PASS_THREE_FULL_CONNECTED_CHILDREN_NON_NULL','comparisons':sum(counts.values()),'per_path':counts,'actual_helpers':['mutex delete wrapper'],'controlled_boundaries':list(mapping)+['destroy callback'],'checks':['memory null returns7','library errors free memory; success loads library and adds modules','italic exact16byte matrix and null vector','cache class reread after lock mutation','destroy/unlock/delete/free order; lock errors do not skip destruction','whole2KiB/SP/R4-R11/caller guards'],'limits':['Fatal null boundaries pending','FT allocator/library/modules/transform and lower locking/backends controlled','No image/layout/hardware proof'],'selected':False};(D/'probe-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
finally:
 p.terminate();p.communicate(timeout=5)
