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







 FS=0x20003000;FACE=FS+0x100;MEM=FS+0x200;DRIVER=FS+0x300;CLASS=FS+0x400;SLOT=FS+0x500;INTERNAL=FS+0x600;LOADER=FS+0x700;SIZE=FS+0x800;NODE=FS+0x900;SIZEINT=FS+0xa00;OUT=FS+0xb00;TAIL=FS+0xc00;ALTTAIL=FS+0xc40;LIST=FS+0xd00
 for n in ['probe_alloc','probe_free','probe_init_slot','probe_done_slot','probe_init_size']:
  targets[symbols[n]&~1]=n;assert command('Z1,'+hex(symbols[n]&~1)[2:]+',2')=='OK'
 saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11];seeds=[0x12345000+i*0x101 for i in range(8)]
 def put(a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
 def word(a):return struct.unpack('<I',u.mem_read(a,4))[0]
 def run(entry,kind,initial,case):
  u.mem_write(FS,initial);u.reg_write(UC_ARM_REG_CPSR,0x01000000);u.reg_write(UC_ARM_REG_SP,0x2007ff00);u.reg_write(UC_ARM_REG_LR,stop_address|1)
  args={'loader':[MEM,OUT],'init':[SLOT,0],'glyph':[case['face'],case['out']],'size':[case['face'],case['out']],'list':[case.get('list',0),case.get('node',0)]}[kind]
  for register,value in zip([UC_ARM_REG_R0,UC_ARM_REG_R1],args):u.reg_write(register,value)
  for register,value in zip(saved,seeds):u.reg_write(register,value)
  u.mem_write(0x2007ff00,b'\xa5'*32);u.reg_write(UC_ARM_REG_PC,entry&~1);seen=[];allocations=0
  for step in range(10):
   response=command('c');pc=u.reg_read(UC_ARM_REG_PC)
   if pc==stop_address:break
   n=targets.get(pc);assert n,(hex(pc),response);a,b=[u.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1]];result=0x87654321
   if n=='probe_alloc':
    allocations+=1;plan={'loader':[(96,LOADER)],'init':[(40,INTERNAL),(96,LOADER)],'glyph':[(176,SLOT),(40,INTERNAL),(96,LOADER)],'size':[(44,SIZE),(12,NODE),(36,SIZEINT)]}[kind];expected,address=plan[allocations-1];assert (a,b)==(MEM,expected);call=(a,b);result=0 if case['fail']==allocations else address
   elif n=='probe_free':assert a==MEM and b in [SLOT,INTERNAL,LOADER,SIZE,NODE];call=(a,b);put(b,0xdeadbeef)
   elif n=='probe_init_slot':
    assert a==SLOT and word(SLOT+156)==INTERNAL;call=(a,);result=case['callback_error']
    if case['mutate']:put(FACE+84,ALTTAIL)
   elif n=='probe_init_size':
    assert a==SIZE and word(SIZE+40)==SIZEINT;call=(a,);result=case['callback_error']
    if case['mutate']:put(FACE+108,ALTTAIL);put(FACE+112,ALTTAIL)
   else:assert n=='probe_done_slot' and a==SLOT;call=(a,)
   seen.append((n,call,result));u.reg_write(UC_ARM_REG_R0,result);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR)&~1)
  else:raise AssertionError('bound')
  assert u.reg_read(UC_ARM_REG_SP)==0x2007ff00 and [u.reg_read(r) for r in saved]==seeds;assert bytes(u.mem_read(0x2007ff00,32))==b'\xa5'*32
  return (None if kind=='list' else u.reg_read(UC_ARM_REG_R0)),seen,bytes(u.mem_read(FS,4096))
 import itertools
 rng=random.Random(379);cases=[]
 defaults={'fail':0,'flags':0,'callback':0,'callback_error':0,'mutate':0,'face':FACE,'out':OUT,'driver':DRIVER,'tail':TAIL}
 def add(kind,**kw):cases.append((kind,dict(defaults,**kw)))
 for fail in [0,1]:add('loader',fail=fail)
 for fail,flags,callback,error,mutate in itertools.product([0,1,2],[0,512],[0,1],[0,6],[0,1]):add('init',fail=fail,flags=flags,callback=callback,callback_error=error,mutate=mutate)
 for kind,face,out,driver,fail,flags,callback,error,mutate in itertools.product(['glyph','size'],[0,FACE],[0,OUT],[0,DRIVER],[0,1,2,3],[0,512],[0,1],[0,6],[0,1]):add(kind,face=face,out=out,driver=driver,fail=fail,flags=flags,callback=callback,callback_error=error,mutate=mutate)
 for listptr,node,tail in itertools.product([0,LIST],[0,NODE],[0,TAIL]):add('list',list=listptr,node=node,tail=tail)
 counts={}
 for kind,case in cases:
  initial=bytearray(rng.getrandbits(8) for _ in range(4096))
  def pack(a,v):struct.pack_into('<I',initial,a-FS,v&0xffffffff)
  for a,v in [(MEM+4,symbols['probe_alloc']),(MEM+8,symbols['probe_free']),(FACE+96,case['driver']),(FACE+100,MEM),(FACE+84,TAIL),(FACE+108,TAIL),(FACE+112,TAIL),(DRIVER,CLASS),(DRIVER+4,0x12345678),(DRIVER+8,MEM),(DRIVER+12,CLASS),(CLASS,case['flags']),(CLASS+40,44),(CLASS+44,176),(CLASS+64,symbols['probe_init_slot'] if case['callback'] else 0),(CLASS+68,symbols['probe_done_slot']),(CLASS+56,symbols['probe_init_size'] if case['callback'] else 0),(SLOT+4,FACE),(SLOT+156,0),(SLOT+88,0),(TAIL+4,0),(TAIL+8,0),(ALTTAIL+4,0),(ALTTAIL+8,0),(LIST,case['tail']),(LIST+4,case['tail'])]:pack(a,v)
  address,name={'loader':(0x524b88,'audio_uart_ft_glyph_loader_new_524b88'),'init':(0x52504c,'audio_uart_ft_glyph_slot_init_52504c'),'glyph':(0x525386,'audio_uart_ft_new_glyph_slot_525386'),'size':(0x52687e,'audio_uart_ft_new_size_52687e'),'list':(0x529304,'audio_uart_ft_list_add_529304')}[kind];native=run(address+delta,kind,initial,case);candidate=run(symbols[name],kind,initial,case)
  if native!=candidate:
   (D/'mismatch.json').write_text(json.dumps({'kind':kind,'case':case,'native_result':native[0],'C_result':candidate[0],'native_calls':native[1],'C_calls':candidate[1],'memory_equal':native[2]==candidate[2]},indent=2)+'\n');raise AssertionError('mismatch.json')
  counts[kind]=counts.get(kind,0)+1
  if sum(counts.values())%200==0:print('comparisons',sum(counts.values()),flush=True)
 receipt={'status':'PASS_FIVE_CREATION_BODIES_CONNECTED_REAL_ROLLBACK','comparisons':sum(counts.values()),'per_path':counts,'actual_helpers':['FT allocation/zero/free','slot init/cleanup and bitmap repair','loader new/done/reset/rewind','staged copy','list add'],'controlled_boundaries':['allocator/free callbacks','driver init-slot/done-slot/init-size callbacks'],'checks':['each allocationfailure stage','invalidface/driver/out return and outputtiming','outlineflag skips loader allocation','hidden loaderoutput ABI','classcallback error rollback/output preservation','currentglyph/currentlist after callback mutations','size callbackerror native cleanup only node/size','NULL/empty/nonempty direct list append','whole4KiB/SP/R4-R11/caller guard'],'limits':['Callbacks controlled; actual allocator/module/runtime gates open','No image/layout/hardware proof'],'selected':False};(D/'probe-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
finally:
 p.terminate();p.communicate(timeout=5)
