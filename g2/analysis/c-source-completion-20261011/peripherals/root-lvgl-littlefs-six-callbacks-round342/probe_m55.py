from pathlib import Path
import subprocess,socket,time,xml.etree.ElementTree as ET,struct,json,random,hashlib
from elftools.elf.elffile import ELFFile
from unicorn.arm_const import *
D=Path(__file__).resolve().parent;source=D/'combined-unadmitted.c'
with (D/'probe.elf').open('rb') as f:
 e=ELFFile(f);symbols={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()};assert e.get_section_by_name('.native_main').data()==Path('/tmp/opencfw-main-native.bin').read_bytes()
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
 u=Remote();targets={}
 for name,address in mapping.items():targets[symbols[name]&~1]=name;targets[address+delta]=name
 for address in targets:assert command('Z1,'+hex(address)[2:]+',2')=='OK'
 stop_address=symbols['probe_stop']&~1;assert command('Z1,'+hex(stop_address)[2:]+',2')=='OK'
 DRIVER=0x20003000;FILE=DRIVER+0x100;BUFFER=DRIVER+0x200;OUT=DRIVER+0x300;CTX=DRIVER+0x500
 saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11];seeds=[0x12345000+i*0x101 for i in range(8)];case={}
 def run(entry,kind,initial,output):
  u.mem_write(DRIVER,initial);u.reg_write(UC_ARM_REG_CPSR,0x01000000);u.reg_write(UC_ARM_REG_SP,0x2007ff00);u.reg_write(UC_ARM_REG_LR,stop_address|1);u.reg_write(UC_ARM_REG_R0,DRIVER);u.reg_write(UC_ARM_REG_R1,FILE);u.reg_write(UC_ARM_REG_R2,output if kind=='tell' else case['position'] if kind=='seek' else BUFFER);u.reg_write(UC_ARM_REG_R3,case['whence'] if kind=='seek' else case['count']);u.reg_write(UC_ARM_REG_PC,entry&~1)
  for r,v in zip(saved,seeds):u.reg_write(r,v)
  guard=struct.pack('<I',output)+b'\xa5'*12;u.mem_write(0x2007ff00,guard);seen=[]
  for step in range(4):
   response=command('c');pc=u.reg_read(UC_ARM_REG_PC)
   if pc==stop_address:break
   name=targets.get(pc);assert name,(hex(pc),response);a=u.reg_read(UC_ARM_REG_R0);b=u.reg_read(UC_ARM_REG_R1);c=u.reg_read(UC_ARM_REG_R2);e=u.reg_read(UC_ARM_REG_R3)
   if name=='audio_uart_lv_heap_free':
    assert a==FILE;args=(a,);u.mem_write(FILE+16,b'\xdd'*16);result=0xa5a5a5a5
   else:
    args=(a,b,c,e) if kind in ['read','write','seek'] else (a,b);assert a==case['context'] and b==FILE
    if kind in ['read','write']:assert (c,e)==(BUFFER,case['count'])
    if kind=='read':u.mem_write(BUFFER,bytes([case['fill']])*min(case['count'],8))
    if kind=='seek':assert c==case['position'] and e==((case['whence']&255) if (case['whence']&255) in [0,1,2] else 0)
    result=case['return'];u.mem_write(FILE+4,struct.pack('<I',result))
   seen.append((name,args,result,bytes(u.mem_read(DRIVER,64)).hex(),bytes(u.mem_read(FILE,64)).hex(),bytes(u.mem_read(BUFFER,16)).hex()));u.reg_write(UC_ARM_REG_R0,result);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR)&~1)
  else:raise AssertionError('callee bound')
  assert u.reg_read(UC_ARM_REG_SP)==0x2007ff00 and [u.reg_read(r) for r in saved]==seeds
  assert bytes(u.mem_read(0x2007ff00,16))==guard
  return u.reg_read(UC_ARM_REG_R0),seen,bytes(u.mem_read(DRIVER,0x1000))
 import itertools
 rng=random.Random(342);counts={};returns=[0,1,0x7fffffff,0x80000000,0xffffffff];contexts=[0,CTX,0x7fffffff,0xffffffff]
 entries={'read':(0x4c8ff0,'audio_uart_lv_fs_read_4c8ff0'),'write':(0x4c900c,'audio_uart_lv_fs_write_4c900c'),'seek':(0x4c9028,'audio_uart_lv_fs_seek_4c9028'),'tell':(0x4c9064,'audio_uart_lv_fs_tell_4c9064'),'close':(0x4c8fd8,'audio_uart_lv_fs_close_4c8fd8'),'dir_close':(0x4c90e4,'audio_uart_lv_fs_dir_close_4c90e4')}
 for kind,(address,name) in entries.items():
  rows=list(itertools.product(contexts,returns,[OUT,DRIVER+48,FILE+52,BUFFER])) if kind in ['read','write','tell'] else list(itertools.product(contexts,returns,[OUT]))
  if kind=='seek':rows=list(itertools.product([CTX],returns,[0,1,2,3,255,256,257,258,0xffffffff]))
  for i,(context,result,third) in enumerate(rows):
   output=OUT if kind=='seek' else third;case={'context':context,'return':result,'whence':third if kind=='seek' else 0,'position':[0,1,0x7fffffff,0x80000000,0xffffffff][i%5],'count':[0,1,4,256,0xffffffff][i%5],'fill':i%256};initial=bytearray(rng.getrandbits(8) for _ in range(0x1000));struct.pack_into('<I',initial,48,context);native=run(address+delta,kind,bytes(initial),output);candidate=run(symbols[name],kind,bytes(initial),output)
   if native!=candidate:
    (D/'mismatch.json').write_text(json.dumps({'kind':kind,'case':case,'output':hex(output),'native_result':native[0],'C_result':candidate[0],'native_calls':native[1],'C_calls':candidate[1],'memory_equal':native[2]==candidate[2]},indent=2)+'\n');raise AssertionError((kind,i,'mismatch.json'))
   expected=0 if kind=='close' or result<0x80000000 else 12;assert native[0]==expected
   if kind in ['read','write','tell']:assert struct.unpack_from('<I',native[2],output-DRIVER)[0]==result
   frees=sum(row[0]=='audio_uart_lv_heap_free' for row in native[1]);assert frees==int(kind=='close' or kind=='dir_close' and result<0x80000000)
   counts[kind]=counts.get(kind,0)+1
  print(json.dumps({'kind':kind,'passed':counts[kind]}),flush=True)
 receipt={'status':'PASS_ACTUAL_SELECTED_TU_M55_SIX_LITTLEFS_CALLBACKS','native_comparisons':sum(counts.values()),'per_function':counts,'candidate_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'native_payload_bytes_unchanged':True,'controlled_child_targets':7,'checks':['Driver userdata48/fifth stack argument/consumed backend arguments','Signed raw results stored andreread before status0/12','Output alias withuserdata/file-position/buffer','Seek whence UXTB/default mapping andfull32bit position','File-close unconditional free vsdir-close nonnegative-only free','Backend buffer/file mutations/orderedcalls/full4KiB fixture','SP/R4-R11/caller argument+guard'],'selected':False,'limits':['LittleFS public methods andheap free controlled; actual filesystem/heap engine not qualified here','No invalid-pointer/full-image/hardware claim']};(D/'probe-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
finally:
 p.terminate();p.communicate(timeout=5)
