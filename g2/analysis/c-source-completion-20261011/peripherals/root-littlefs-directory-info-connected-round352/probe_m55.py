from pathlib import Path
import subprocess,socket,time,xml.etree.ElementTree as ET,struct,json,random,hashlib
from elftools.elf.elffile import ELFFile
from unicorn.arm_const import *
D=Path(__file__).resolve().parent;source=D/'combined-unadmitted.c'
with (D/'probe.elf').open('rb') as f:
 e=ELFFile(f);symbols={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()};assert e.get_section_by_name('.native_main').data()==(D/'native.bin').read_bytes()
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
 def run(entry,initial):
  u.mem_write(FS,initial);u.reg_write(UC_ARM_REG_CPSR,0x01000000);u.reg_write(UC_ARM_REG_SP,0x2007ff00);u.reg_write(UC_ARM_REG_LR,stop_address|1)
  for register,value in [(UC_ARM_REG_R0,FS),(UC_ARM_REG_R1,FILE+8),(UC_ARM_REG_R2,case['identifier']),(UC_ARM_REG_R3,INFO),(UC_ARM_REG_PC,entry&~1)]:u.reg_write(register,value)
  for register,value in zip(saved,seeds):u.reg_write(register,value)
  u.mem_write(0x2007ff00,b'\xa5'*16);seen=[]
  for step in range(3):
   response=command('c');pc=u.reg_read(UC_ARM_REG_PC)
   if pc==stop_address:break
   assert targets.get(pc)=='g2_lfs_dir_getslice',(hex(pc),response)
   a=u.reg_read(UC_ARM_REG_R0);b=u.reg_read(UC_ARM_REG_R1);mask=u.reg_read(UC_ARM_REG_R2);tag=u.reg_read(UC_ARM_REG_R3);sp=u.reg_read(UC_ARM_REG_SP);offset=word(sp);buffer=word(sp+4);size=word(sp+8);assert (a,b,offset)==(FS,FILE+8,0);assert size==(tag&0x3ff)
   identifier=case['identifier']&0xffff
   if not seen:
    assert mask==0x780ffc00 and tag==(((word(FS+112)+1)&0xffffffff)|(identifier<<10)) and buffer==INFO+8
    result=case['name_tag'];u.mem_write(buffer,b'filename\0'[:min(size,9)]);put(FS+112,0x76543210);args=(a,b,mask,tag,offset,INFO+8,size)
   else:
    assert mask==0x700ffc00 and tag==(0x20000008|(identifier<<10)) and size==8
    assert bytes(u.mem_read(buffer,8))==struct.pack('<II',case['identifier'],INFO)
    result=case['struct_tag'];put(buffer,0x12345678);put(buffer+4,case['stored_size']);args=(a,b,mask,tag,offset,'pair',size)
   seen.append((args,result));u.reg_write(UC_ARM_REG_R0,result);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR)&~1)
  else:raise AssertionError('calleebound')
  assert u.reg_read(UC_ARM_REG_SP)==0x2007ff00 and [u.reg_read(r) for r in saved]==seeds
  assert bytes(u.mem_read(0x2007ff00,16))==b'\xa5'*16
  return u.reg_read(UC_ARM_REG_R0),seen,bytes(u.mem_read(FS,4096))
 import itertools
 rng=random.Random(352);count=0
 for index,(identifier,name_max,name_tag,struct_tag) in enumerate(itertools.product([0,1,0x3ff,0x103ff,0xffff,0xffffffff,0x80010001],[0,15,255,0x3ff,0xffffffff],[0x00100007,0x00200000,0x7ff000ff,0xffffffff],[0x20200008,0x20100000,0x201003ff,0x20300008,0xffffffff])):
  case={'identifier':identifier,'name_tag':name_tag,'struct_tag':struct_tag,'stored_size':[0,0xffffffff,0x80000000,0x12345678][index%4]}
  initial=bytearray(rng.getrandbits(8) for _ in range(4096));struct.pack_into('<I',initial,112,name_max)
  native=run(0x4cbf38+delta,bytes(initial));candidate=run(symbols['audio_file_lfs_dir_getinfo_4cbf38'],bytes(initial))
  if native!=candidate:
   (D/'mismatch.json').write_text(json.dumps({'case':case,'name_max':name_max,'native_result':native[0],'C_result':candidate[0],'native_calls':native[1],'C_calls':candidate[1],'memory_equal':native[2]==candidate[2]},indent=2)+'\n');raise AssertionError('mismatch.json')
  count+=1
  if count%200==0:print(json.dumps({'passed':count}),flush=True)
 receipt={'status':'PASS_ENTIRE_DIRECTORY_INFO_ACTUAL_SELECTED_TU_M55','native_comparisons':count,'candidate_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'controlled_lower_backends':1,'actual_selected_and_native_helpers_execute':['directorygetwrapper','endianpairconversion'],'checks':['UXTHidandrootlow16bits/rootpreservessize','Name_maxunsignedwrapand16bitidtagpacking','Nameerrorandstructerror/noinventedclearing','Typelowbyte/CTZsize/inline10bitsize/otherpreservessize','Originalsavedwordpairinitialization/exact8bytesliceABI','Whole4KiBfixture/SP/R4-R11/caller16byteguard'],'selected':False,'limits':['Slicereadcontrolled;diskengineunqualified','Syntheticname_maxboundariesarenotvalidfilesystemconfigproof','Distinctvalidinformationobject;invalidaliasesunqualified','No completeimage/layout/byteidentity/hardwareclaim']};(D/'probe-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
finally:
 p.terminate();p.communicate(timeout=5)
