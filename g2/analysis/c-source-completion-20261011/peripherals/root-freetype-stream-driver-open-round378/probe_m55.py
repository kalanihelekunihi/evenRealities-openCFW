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







 FS=0x20003000;LIB=FS+0x100;ARGS=FS+0x200;MEM=FS+0x300;DRIVER=FS+0x400;CLASS=FS+0x500;STREAM=FS+0x600;EXT=FS+0x680;ALTSTREAM=FS+0x6c0;FACE=FS+0x800;INTERNAL=FS+0x900;PARAMS=FS+0xa00;OUT=FS+0xb00;CELL=FS+0xc00;PATH=FS+0xd00;PATH2=FS+0xd40;BASE=FS+0xe00
 for n in ['probe_alloc','probe_free','probe_init_face','probe_done_face']:
  targets[symbols[n]&~1]=n;assert command('Z1,'+hex(symbols[n]&~1)[2:]+',2')=='OK'
 saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11];seeds=[0x12345000+i*0x101 for i in range(8)]
 def word(a):return struct.unpack('<I',u.mem_read(a,4))[0]
 def put(a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
 def run(entry,kind,initial,case):
  u.mem_write(FS,initial);u.reg_write(UC_ARM_REG_CPSR,0x01000000);u.reg_write(UC_ARM_REG_SP,0x2007ff00);u.reg_write(UC_ARM_REG_LR,stop_address|1)
  if kind=='stream':args=[case['library'],case['args'],OUT,0x12345678];stack=b'\xa5'*32
  elif kind=='memory':args=[STREAM,BASE,case['size'],0x12345678];stack=b'\xa5'*32
  else:args=[DRIVER,CELL,case['external'],case['index']&0xffffffff];stack=struct.pack('<III',case['count']&0xffffffff,PARAMS,OUT)+b'\xa5'*20
  for register,value in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],args):u.reg_write(register,value)
  for register,value in zip(saved,seeds):u.reg_write(register,value)
  u.mem_write(0x2007ff00,stack);u.reg_write(UC_ARM_REG_PC,entry&~1);seen=[];allocations=0
  for step in range(12):
   response=command('c');pc=u.reg_read(UC_ARM_REG_PC)
   if pc==stop_address:break
   n=targets.get(pc);assert n,(hex(pc),response);a,b,c,d=[u.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];result=0x87654321
   if n=='probe_alloc':
    allocations+=1;expected=40 if kind=='stream' else 140 if allocations==1 else 68;assert (a,b)==(MEM,expected);call=(a,b);result=0 if case['fail_alloc']==allocations else STREAM if kind=='stream' else FACE if allocations==1 else INTERNAL
   elif n=='audio_uart_ft_stream_open_path_5675e8':assert (a,b)==(STREAM,PATH);call=(a,b);result=case['path_error'];put(ARGS+12,PATH2)
   elif n=='probe_free':
    assert a==MEM and b in [STREAM,FACE,INTERNAL];call=(a,b);put(b,0xdeadbeef)
    if kind=='stream' and case['mutate']:put(ARGS+16,ALTSTREAM)
   elif n=='probe_init_face':
    sp=u.reg_read(UC_ARM_REG_SP);call=(a,b,c,d,word(sp));assert call==(EXT,FACE,case['index']&0xffffffff,case['count']&0xffffffff,PARAMS)
    expected_increment=0x12345678 if case['count']>=3 else 0;assert word(INTERNAL+52)==expected_increment and word(INTERNAL+60)==0xffffffff
    put(FACE+104,ALTSTREAM);result=case['init_error']
   elif n=='audio_uart_ft_find_unicode_charmap_52594a':assert a==FACE;call=(a,);result=case['lookup_error']
   else:
    assert n=='probe_done_face' and a in [0,FACE];call=(a,)
    if a:put(a+8,0x12345678)
   seen.append((n,call,result));u.reg_write(UC_ARM_REG_R0,result);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR)&~1)
  else:raise AssertionError('bound')
  assert u.reg_read(UC_ARM_REG_SP)==0x2007ff00 and [u.reg_read(r) for r in saved]==seeds;assert bytes(u.mem_read(0x2007ff00,32))==stack
  return (None if kind=='memory' else u.reg_read(UC_ARM_REG_R0)),seen,bytes(u.mem_read(FS,4096))
 import itertools
 rng=random.Random(378);cases=[]
 for library,args,flags,existing,fail,patherror,mutate in itertools.product([0,LIB],[0,ARGS],[0,1,2,4,7],[0,EXT],[0,1],[0,6],[0,1]):
  cases.append(('stream',{'library':library,'args':args,'flags':flags,'existing':existing,'fail_alloc':fail,'path_error':patherror,'mutate':mutate}))
 for fail,external,count,callback,done,initerror,lookup in itertools.product([0,1,2],[0,1,256],[-1,0,3],[0,1],[0,1],[0,6],[0,38,0x10026,6]):
  cases.append(('driver',{'fail_alloc':fail,'external':external,'count':count,'callback':callback,'done':done,'init_error':initerror,'lookup_error':lookup,'index':0x80000000,'mutate':0}))
 for size in [0,1,0xffffffff]:cases.append(('memory',{'size':size}))
 counts={}
 for kind,case in cases:
  initial=bytearray(rng.getrandbits(8) for _ in range(4096))
  def pack(a,v):struct.pack_into('<I',initial,a-FS,v&0xffffffff)
  for a,v in [(LIB,MEM),(MEM+4,symbols['probe_alloc']),(MEM+8,symbols['probe_free']),(ARGS,case.get('flags',0)),(ARGS+4,BASE),(ARGS+8,0xffffffff),(ARGS+12,PATH),(ARGS+16,case.get('existing',EXT)),(DRIVER+12,CLASS),(DRIVER+8,MEM),(CLASS+36,140),(CLASS+48,symbols['probe_init_face'] if case.get('callback') else 0),(CLASS+52,symbols['probe_done_face'] if case.get('done') else 0),(CELL,EXT)]:pack(a,v)
  for i,(tag,value) in enumerate([(0,9),(0x696e6372,0),(0x696e6372,0x12345678)]):pack(PARAMS+i*8,tag);pack(PARAMS+i*8+4,value)
  address,name={'stream':(0x524f96,'audio_uart_ft_stream_new_524f96'),'driver':(0x5259be,'audio_uart_ft_open_driver_face_5259be'),'memory':(0x5288b8,'audio_uart_ft_stream_open_memory_5288b8')}[kind];native=run(address+delta,kind,initial,case);candidate=run(symbols[name],kind,initial,case)
  if native!=candidate:
   (D/'mismatch.json').write_text(json.dumps({'kind':kind,'case':case,'native_result':native[0],'C_result':candidate[0],'native_calls':native[1],'C_calls':candidate[1],'memory_equal':native[2]==candidate[2]},indent=2)+'\n');raise AssertionError('mismatch.json')
  counts[kind]=counts.get(kind,0)+1
  if sum(counts.values())%200==0:print('comparisons',sum(counts.values()),flush=True)
 receipt={'status':'PASS_THREE_STREAM_DRIVER_BODIES_CONNECTED','comparisons':sum(counts.values()),'per_path':counts,'actual_helpers':['FT allocator','zero','memoryfree','memory-stream initializer','charmap cleanup'],'controlled_boundaries':['path open','unicode lookup','allocator/free callbacks','class init/done callbacks'],'checks':['output zero before validation/allocation','sourceflag precedence/memory/path/external/invalid','path reread and external stream replacement after callback','face/internal alloc failures cleanup','lowbyte externalflag','incremental tag scan/zero-value retry/signed count','fiveargument class-init ABI and stream replacement','unicode missing38 accepted without error;othererrorscleanup','whole4KiB/SP/R4-R11/caller guard'],'limits':['Filesystem/driver/unicode and allocator callbacks controlled; runtime/config gates open','No image/layout/hardware proof'],'selected':False};(D/'probe-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
finally:
 p.terminate();p.communicate(timeout=5)
