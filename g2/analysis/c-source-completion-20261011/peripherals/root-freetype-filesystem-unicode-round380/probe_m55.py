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







 FS=0x20003000;STREAM=FS+0x100;PATH=FS+0x300;FILE=FS+0x400;BUFFER=FS+0x600;FACE=FS+0x800;ARRAY=FS+0x900;MAPS=[FS+0xa00,FS+0xa20,FS+0xa40]
 saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11];seeds=[0x12345000+i*0x101 for i in range(8)]
 def put(a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
 def word(a):return struct.unpack('<I',u.mem_read(a,4))[0]
 def string(a):
  out=bytearray()
  for off in range(0,512,64):
   data=bytes(u.mem_read(a+off,64));out.extend(data.split(b'\0',1)[0])
   if b'\0' in data:return out.decode()
  raise AssertionError('string')
 def run(entry,native,kind,initial,case):
  u.mem_write(FS,initial);u.reg_write(UC_ARM_REG_CPSR,0x01000000);u.reg_write(UC_ARM_REG_SP,0x2007ff00);u.reg_write(UC_ARM_REG_LR,stop_address|1)
  args=[case['stream'],PATH,0,0] if kind=='open' else [STREAM,case['offset'],BUFFER,case['count']] if kind=='read' else [STREAM,0,0,0] if kind=='close' else [FACE,0,0,0]
  for reg,value in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],args):u.reg_write(reg,value)
  for reg,value in zip(saved,seeds):u.reg_write(reg,value)
  u.mem_write(0x2007ff00,b'\xa5'*32);u.reg_write(UC_ARM_REG_PC,entry&~1);seen=[];fileptr=None
  for step in range(10):
   response=command('c');pc=u.reg_read(UC_ARM_REG_PC)
   if pc==stop_address:break
   n=targets.get(pc);assert n,(hex(pc),response);a,b,c,d=[u.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];result=0x87654321
   if n=='audio_uart_lv_fs_file_open_4c6d9a':assert (b,c)==(PATH,2);fileptr=a;u.mem_write(a,struct.pack('<III',0x11111111,0x22222222,0x33333333));call=('file',b,c);result=case['open']
   elif n=='audio_uart_lv_fs_file_seek_4c6fba':
    assert a==(fileptr if kind=='open' else FILE);call=('file' if kind=='open' else a,b,c);result=case.get('seek',0)
    if kind=='open':put(a+8,0x44444444 if c==2 else 0x55555555)
   elif n=='audio_uart_lv_fs_file_tell_4c7018':assert a==fileptr;call=('file','size_out');put(b,case['size']);result=case['tell']
   elif n=='audio_uart_lv_fs_file_close_4c6ee0':assert a==(fileptr if kind=='open' else FILE);call=('file' if kind=='open' else a,);put(STREAM+12,0xdeadbeef);result=case.get('close',0)
   elif n=='audio_uart_lv_pool_allocate_484180':assert (a,b)==(0x20000354,12);call=(a,b);result=case['allocation'];put(fileptr,0xabcdef01)
   elif n=='audio_uart_lv_pool_free_48429e':assert (a,b)==(0x20000354,FILE);call=(a,b);put(FILE,0x12345678)
   elif n=='audio_uart_lv_fs_file_read_4c6f46':assert (a,b,c)==(FILE,BUFFER,case['count']);call=(a,b,c,'read_out');put(d,case['read_count']);result=case['read_error'];put(BUFFER,0x24681357)
   else:
    assert n=='audio_uart_lvgl_log';sp=u.reg_read(UC_ARM_REG_SP);call=(a,string(b),c,string(d),string(word(sp)),string(word(sp+4)),string(word(sp+8)));assert (a,c)==(3,129);seen.append((n,call));u.reg_write(UC_ARM_REG_R0,0x12345678);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR)&~1)
    from capstone import Cs,CS_ARCH_ARM,CS_MODE_THUMB,CS_MODE_MCLASS
    decoder=Cs(CS_ARCH_ARM,CS_MODE_THUMB|CS_MODE_MCLASS)
    for loop_step in range(20):
     pc=u.reg_read(UC_ARM_REG_PC);ins=next(decoder.disasm(bytes(u.mem_read(pc,4)),pc,count=1))
     if ins.mnemonic=='b' and ins.op_str=='#'+hex(pc):return 'fatal_spin',seen,bytes(u.mem_read(FS,4096))
     command('s')
    raise AssertionError('fatal loop')
   seen.append((n,call,result));u.reg_write(UC_ARM_REG_R0,result);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR)&~1)
  else:raise AssertionError('bound')
  assert u.reg_read(UC_ARM_REG_SP)==0x2007ff00 and [u.reg_read(r) for r in saved]==seeds;assert bytes(u.mem_read(0x2007ff00,32))==b'\xa5'*32
  mem=bytearray(u.mem_read(FS,4096))
  if kind=='open' and case['stream'] and case['allocation'] and case['open']&255==0 and case['tell']&255==0:
   for off,name,address in [(20,'audio_uart_ft_lv_fs_stream_io_567734',0x567735),(24,'audio_uart_ft_lv_fs_stream_close_5676f8',0x5676f9)]:
    expected=address+delta if native else symbols[name];assert struct.unpack_from('<I',mem,STREAM-FS+off)[0]==expected;struct.pack_into('<I',mem,STREAM-FS+off,address)
  return (None if kind=='close' else u.reg_read(UC_ARM_REG_R0)),seen,bytes(mem)
 import itertools
 rng=random.Random(380);cases=[]
 for stream,opened,tell,size,allocation in itertools.product([0,STREAM],[0,1,0x100],[0,1,0x100],[0,640,0xffffffff],[0,FILE]):cases.append(('open',{'stream':stream,'open':opened,'tell':tell,'size':size,'allocation':allocation}))
 for count,offset,size,pos,error in itertools.product([0,1,16],[0,10,0xffffffff],[0,10,0xffffffff],[0,10],[0,1,0x100]):cases.append(('read',{'count':count,'offset':offset,'size':size,'pos':pos,'read_error':error,'read_count':0xffffffff,'seek':6}))
 for close in [0,1,0x100]:cases.append(('close',{'close':close}))
 kinds=[(0x756e6963,3,10),(0x756e6963,0,4),(0x756e6963,3,1),(0x12345678,3,10)]
 for maps in itertools.product(kinds,repeat=3):cases.append(('unicode',{'maps':maps,'count':3,'array':ARRAY}))
 for count,array in itertools.product([0,1,2],[0,ARRAY]):cases.append(('unicode',{'maps':[kinds[0],kinds[1],kinds[2]],'count':count,'array':array}))
 counts={}
 for kind,case in cases:
  initial=bytearray(rng.getrandbits(8) for _ in range(4096))
  def pack(a,v):struct.pack_into('<I',initial,a-FS,v&0xffffffff)
  for a,v in [(STREAM+12,FILE),(STREAM+4,case.get('size',10)),(STREAM+8,case.get('pos',0)),(FACE+40,case.get('array',ARRAY)),(FACE+36,case.get('count',3))]:pack(a,v)
  for i,map in enumerate(MAPS):
   pack(ARRAY+i*4,map);encoding,platform,enc=case.get('maps',[kinds[0]]*3)[i];pack(map+4,encoding);struct.pack_into('<HH',initial,map-FS+8,platform,enc)
  address,name={'open':(0x5675e8,'audio_uart_ft_stream_open_path_5675e8'),'read':(0x567734,'audio_uart_ft_lv_fs_stream_io_567734'),'close':(0x5676f8,'audio_uart_ft_lv_fs_stream_close_5676f8'),'unicode':(0x52594a,'audio_uart_ft_find_unicode_charmap_52594a')}[kind];native=run(address+delta,True,kind,initial,case);candidate=run(symbols[name],False,kind,initial,case)
  if native!=candidate:
   (D/'mismatch.json').write_text(json.dumps({'kind':kind,'case':case,'native':native[:2],'C':candidate[:2],'memory_equal':native[2]==candidate[2]},indent=2)+'\n');raise AssertionError('mismatch.json')
  counts[kind]=counts.get(kind,0)+1
 receipt={'status':'PASS_FOUR_FILESYSTEM_UNICODE_BODIES_NATIVE_CORE','comparisons':sum(counts.values()),'per_path':counts,'controlled_boundaries':list(mapping),'checks':['NULL stream/open/tell lowbyte errors','seek errors ignored by native contract','12byte file copy after allocator mutation','typed callback identities independently asserted then normalized','OOM exact logger/self-loop boundary','zero-count stream bounds and read count/error','close cached file despite backend mutation','backward UCS4/Unicode preference and no-match preservation','whole4KiB/SP/R4-R11/caller guard for returning paths'],'limits':['Filesystem and pool providers controlled; real connected backend pass pending','Fatal loop checked at boundary; no recovery/hardware claim','No completeimage/layout proof'],'selected':False};(D/'probe-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
finally:
 p.terminate();p.communicate(timeout=5)
