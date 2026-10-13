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
 u=Remote();targets={}
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
 def run(entry,kind,initial):
  u.mem_write(FS,initial);u.reg_write(UC_ARM_REG_CPSR,0x01000000);u.reg_write(UC_ARM_REG_SP,0x2007ff00);u.reg_write(UC_ARM_REG_LR,stop_address|1);u.reg_write(UC_ARM_REG_R0,FS);u.reg_write(UC_ARM_REG_R1,FILE);u.reg_write(UC_ARM_REG_R2,PATH if kind=='dir_open' else INFO if kind=='dir_read' else BUFFER);u.reg_write(UC_ARM_REG_R3,case['size']);u.reg_write(UC_ARM_REG_PC,entry&~1)
  for r,v in zip(saved,seeds):u.reg_write(r,v)
  u.mem_write(0x2007ff00,b'\xa5'*16);seen=[]
  for step in range(8):
   response=command('c');pc=u.reg_read(UC_ARM_REG_PC)
   if pc==stop_address:break
   name=targets.get(pc);assert name,(hex(pc),response);a=u.reg_read(UC_ARM_REG_R0);b=u.reg_read(UC_ARM_REG_R1);c=u.reg_read(UC_ARM_REG_R2);e=u.reg_read(UC_ARM_REG_R3)
   if name=='g2_file_close_error':
    args=(string(a),string(b),c);seen.append((name,args));assert bytes(u.mem_read(0x2007ff00,16))==b'\xa5'*16
    return 'assert-boundary',seen,bytes(u.mem_read(FS,0x1000))
   if name=='g2_lfs_mlist_isopen':
    args=(a,b);assert args==(HEAD,FILE);result=case['membership'];put(FS+40,FS+0x380)
   else:
    assert (a,b)==(FS,FILE);args=(a,b,c,e) if kind=='write' else (a,b,string(c)) if kind=='dir_open' else (a,b,c) if kind=='dir_read' else (a,b)
    if kind=='write':assert (c,e)==(BUFFER,case['size'])
    if kind=='dir_open':assert c==PATH
    if kind=='dir_read':assert c==INFO;u.mem_write(INFO,b'\x47'*16)
    if name=='g2_lfs_mlist_remove':put(FS+40,0);result=0xdeadbeef
    else:result=case['return'];put(FILE+4,result)
   seen.append((name,args,result));u.reg_write(UC_ARM_REG_R0,result);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR)&~1)
  else:raise AssertionError('callee bound')
  assert u.reg_read(UC_ARM_REG_SP)==0x2007ff00 and [u.reg_read(r) for r in saved]==seeds
  assert bytes(u.mem_read(0x2007ff00,16))==b'\xa5'*16
  return u.reg_read(UC_ARM_REG_R0),seen,bytes(u.mem_read(FS,0x1000))
 import itertools
 entries={'close':(0x4cfad0,'audio_file_lfs_close_4cfad0'),'write':(0x4cfb7c,'audio_file_lfs_write_4cfb7c'),'dir_open':(0x4cfc66,'audio_file_lfs_dir_open_4cfc66'),'dir_close':(0x4cfcf8,'audio_file_lfs_dir_close_4cfcf8'),'dir_read':(0x4cfd02,'audio_file_lfs_dir_read_4cfd02'),'dir_close_core':(0x4cd604,'audio_file_lfs_dir_close_core_4cd604')};rng=random.Random(347);counts={};assertions=0
 for kind,(address,name) in entries.items():
  for membership,result,size in itertools.product([0,1,255,256,0xffffffff],[0,1,0x7fffffff,0x80000000,0xffffffff],[0,1,0xffffffff]):
   case={'membership':membership,'return':result,'size':size};initial=bytearray(rng.getrandbits(8) for _ in range(0x1000));struct.pack_into('<I',initial,40,HEAD);initial[PATH-FS:PATH-FS+12]=b'folder/file\0';n=run(address+delta,kind,bytes(initial));c=run(symbols[name],kind,bytes(initial))
   if n!=c:
    (D/'mismatch.json').write_text(json.dumps({'kind':kind,'case':case,'native_result':n[0],'C_result':c[0],'native_calls':n[1],'C_calls':c[1],'memory_equal':n[2]==c[2]},indent=2)+'\n');raise AssertionError((kind,'mismatch.json'))
   is_assert=kind in ['close','write'] and membership==0 or kind=='dir_open' and membership!=0
   if is_assert:
    assert n[0]=='assert-boundary';line={'close':6155,'write':6207,'dir_open':6318}[kind];assert n[1][-1][1][2]==line;assertions+=1
   else:assert n[0]==(0 if kind in ['dir_close','dir_close_core'] else result)
   counts[kind]=counts.get(kind,0)+1
  print(json.dumps({'kind':kind,'passed':counts[kind]}),flush=True)
 receipt={'status':'PASS_ACTUAL_SELECTED_TU_M55_FIVE_LITTLEFS_PUBLIC_ENTRIES_AND_DIR_CLOSE_CORE','native_comparisons':sum(counts.values()),'per_function':counts,'assertion_boundary_cases':assertions,'candidate_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'controlled_lower_backends':7,'actual_dir_close_core_executes':True,'instruction_bytes_unchanged':True,'ordinary_pointer_bindings':'oracle-bindings.json','checks':['Live mlist40 pointer/membership zero/nonzero branching','Exact assertion expression/source/line boundary before error helper execution','Core argument forwarding/full32bit return','Directory unlink delegation andconstant0 return','Entire4KiB fixture/mutating membership/core callbacks','SP/R4-R11/caller guard onreturning paths'],'selected':False,'limits':['Seven lower membership/error/core backends controlled; actual filesystem engine not qualified here','Assertions stopaterror-helper boundary; no fatal helper/hardware claim','No full-image/layout/source completeness claim']};(D/'probe-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
finally:
 p.terminate();p.communicate(timeout=5)
