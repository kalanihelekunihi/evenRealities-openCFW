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
 RAM=FS;FORMAT=FS+0x100;TEXT=FS+0x400;OUTPUT=FS+0x800;VA=FS+0xd00
 def fp_context():
  return [bytes(reg('d'+str(i))) for i in range(8,16)] if 'd8' in registers else [bytes(reg('s'+str(i))) for i in range(16,32)]
 def seed_fp():
  names=['d'+str(i) for i in range(8,16)] if 'd8' in registers else ['s'+str(i) for i in range(16,32)]
  for i,name in enumerate(names):
   width=8 if name.startswith('d') else 4;value=(0x1234567887654321+i*0x101)&((1<<(8*width))-1);assert command('P'+hex(registers[name])[2:]+'='+value.to_bytes(width,'little').hex())=='OK'
  if 'fpscr' in registers:assert command('P'+hex(registers['fpscr'])[2:]+'=00000000')=='OK'
 def encode(kind,spec):
  start=0x2007fefc if kind=='snprintf' else VA;words=[];cursor=start
  for type,value in spec:
   if type=='u64':
    if cursor&7:words.append(0xa55aa55a);cursor+=4
    words.extend([value&0xffffffff,(value>>32)&0xffffffff]);cursor+=8
   else:words.append(value&0xffffffff);cursor+=4
  return words
 def run(entry,kind,initial,destination,capacity,args):
  u.mem_write(FS,initial);u.reg_write(UC_ARM_REG_CPSR,0x01000000);u.reg_write(UC_ARM_REG_SP,0x2007ff00);u.reg_write(UC_ARM_REG_LR,stop_address|1);seed_fp();fp_seed=fp_context();caller=bytearray(b'\xa5'*96)
  if kind=='snprintf':
   first=args[0] if args else 0xdeadbeef
   for index,value in enumerate(args[1:]):struct.pack_into('<I',caller,index*4,value)
  else:first=VA
  for register,value in [(UC_ARM_REG_R0,destination),(UC_ARM_REG_R1,capacity),(UC_ARM_REG_R2,FORMAT),(UC_ARM_REG_R3,first),(UC_ARM_REG_PC,entry&~1)]:u.reg_write(register,value)
  for register,value in zip(saved,seeds):u.reg_write(register,value)
  u.mem_write(0x2007ff00,caller);response=command('c');pc=u.reg_read(UC_ARM_REG_PC);assert pc==stop_address,(hex(pc),response)
  assert u.reg_read(UC_ARM_REG_SP)==0x2007ff00 and [u.reg_read(r) for r in saved]==seeds,('faultorABI',fmt,capacity,spec,hex(entry),hex(u.reg_read(UC_ARM_REG_SP)),bytes(u.mem_read(0xe000ed28,20)).hex(),bytes(u.mem_read(u.reg_read(UC_ARM_REG_SP),48)).hex())
  assert fp_context()==fp_seed,'D8-D15changed';assert bytes(u.mem_read(0x2007ff00,96))==caller
  return u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(FS,4096))
 def bits(value):return struct.unpack('<Q',struct.pack('<d',value))[0]
 formats=[]
 for value in [0,1,0x100000000,0x7fffffffffffffff,0x8000000000000000,0xffffffffffffffff]:
  for fmt in ['%lld','%llu','%#llx','%020llu']:formats.append((fmt,[('u64',value)]))
 for value in [0.0,-0.0,1.0,-1.25,0.125,42.5,999999999.5,1e10,1e-10]:
  for fmt in ['%f','%.0f','%.3f','%+012.4f','%e','%.5g','%G']:formats.append((fmt,[('u64',bits(value))]))
 for value in [0x7ff0000000000000,0xfff0000000000000,0x7ff8000000001234]:
  for fmt in ['%f','%+f','%e','%g']:formats.append((fmt,[('u64',value)]))
 formats.extend([('%d:%f:%u',[('u32',42),('u64',bits(-1.25)),('u32',0xffffffff)]),('%*.*f',[('u32',16),('u32',3),('u64',bits(42.5))]),('%llu:%d:%llu',[('u64',0xffffffffffffffff),('u32',42),('u64',0x100000000)])])
 counts={};rng=random.Random(355)
 for kind,address,name in [('snprintf',0x483fd0,'audio_uart_lv_snprintf_483fd0'),('vsnprintf',0x483fea,'audio_uart_lv_vsnprintf_483fea')]:
  for fmt,spec in formats:
   for capacity in [0,1,8,64]:
    args=encode(kind,spec);initial=bytearray(rng.getrandbits(8) for _ in range(4096));encoded=fmt.encode()+b'\0';initial[FORMAT-FS:FORMAT-FS+len(encoded)]=encoded
    for index,value in enumerate(args):struct.pack_into('<I',initial,VA-FS+index*4,value)
    native=run(address+delta,kind,bytes(initial),OUTPUT,capacity,args);candidate=run(symbols[name],kind,bytes(initial),OUTPUT,capacity,args)
    if native!=candidate:
     first_difference=next((i for i,(a,b) in enumerate(zip(native[1],candidate[1])) if a!=b),None)
     (D/'mismatch.json').write_text(json.dumps({'kind':kind,'format':fmt,'spec':spec,'capacity':capacity,'native_result':native[0],'C_result':candidate[0],'memory_equal':native[1]==candidate[1],'first_difference':first_difference,'native_output':native[1][OUTPUT-FS:OUTPUT-FS+64].hex(),'C_output':candidate[1][OUTPUT-FS:OUTPUT-FS+64].hex()},indent=2)+'\n');raise AssertionError('mismatch.json')
    counts[kind]=counts.get(kind,0)+1
   if counts[kind]%80==0:print(json.dumps({'kind':kind,'passed':counts[kind]}),flush=True)
  print(json.dumps({'kind':kind,'passed':counts[kind]}),flush=True)
 receipt={'status':'PASS_COMPLETE_SELECTED_TU_CONNECTED_EXISTING_DIVIDER_FORMATTER_AND_NUMERICAL_PROVIDERS_M55','native_comparisons':sum(counts.values()),'per_entry':counts,'format_fixtures':len(formats),'candidate_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'controlled_backends_executed':0,'actual_compiler_rt_arithmetic_executes':True,'ordinary_pointer_bindings':'oracle-bindings.json:two code/three literal-datapointers; instructionbytesunchanged','checks':['Signed/unsigned64includingextremes/alignedvarargsandmixed32/64','Fixed/exponential/general/upper/defaultandexplicitprecision','Zero/signedzero/negative/small/large/inf/nan','Capacity0/1/8/64andwhole4KiBfixture','SP/R4-R11/D8-D15/caller96byteargsandguard'],'selected':False,'limits':['DefaultFPSCR input0; exceptionflags/otherroundingmodesunqualified','Compiler-rt is not original IAR arithmetic identity orbyteequality','No completeimage/layout/hardwareclaim']};(D/'probe-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
finally:
 p.terminate();p.communicate(timeout=5)
