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







 FS=0x20003000;LIB=FS+0x100;MEM=FS+0x180;STREAM=FS+0x200;OUT=FS+0x280;LIST=FS+0x500;FACE=FS+0x600;ALT=FS+0x640
 saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11];seeds=[0x12345000+i*0x101 for i in range(8)]
 def put(a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
 def run(entry,initial,case):
  u.mem_write(FS,initial);u.reg_write(UC_ARM_REG_CPSR,0x01000000);u.reg_write(UC_ARM_REG_SP,0x2007ff00);u.reg_write(UC_ARM_REG_LR,stop_address|1)
  for r,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],[LIB,STREAM,0x345,case['index']&0xffffffff]):u.reg_write(r,v)
  for r,v in zip(saved,seeds):u.reg_write(r,v)
  guard=struct.pack('<I',OUT)+b'\xa5'*28;u.mem_write(0x2007ff00,guard);u.reg_write(UC_ARM_REG_PC,entry&~1);seen=[];countptr=None
  for step in range(12):
   response=command('c');pc=u.reg_read(UC_ARM_REG_PC)
   if pc==stop_address:break
   n=targets.get(pc);assert n,(hex(pc),response);a,b,c,d=[u.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];stack=struct.unpack('<4I',u.mem_read(u.reg_read(UC_ARM_REG_SP),16));result=0
   if n=='probe_free':
    assert a==MEM and b==(0 if case['null_list'] else LIST);seen.append(('free',a,b))
    if case['mutate']:put(countptr,7);put(OUT,ALT)
   elif n=='audio_uart_ft_raccess_header_528064':
    assert (a,b,c)==(LIB,STREAM,0x345);put(d,0x123);put(stack[0],0x234);put(LIB,FS+0x1c0);result=case['header'];seen.append(('header',result))
   elif n=='audio_uart_ft_raccess_offsets_528298':
    assert (a,b,c,d)==(LIB,STREAM,0x123,0x234);tag,sort,offsetptr,countptr=stack;assert (tag,sort) in [(0x504f5354,1),(0x73666e74,0)];put(offsetptr,0 if case['null_list'] else LIST);put(countptr,case['count']);result=case['post_offsets'] if sort else case['sfnt_offsets'];seen.append(('offsets',tag,sort,result))
   else:
    assert (a,b,c)==(LIB,STREAM,0 if case['null_list'] else LIST) and d==case['count']&0xffffffff and stack[1]==OUT;seen.append(('post' if n.endswith('525e16') else 'sfnt',d,stack[0],case['child']));put(OUT,FACE);result=case['child']
   u.reg_write(UC_ARM_REG_R0,result);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR)&~1)
  else:raise AssertionError('call bound')
  assert u.reg_read(UC_ARM_REG_SP)==0x2007ff00 and [u.reg_read(r) for r in saved]==seeds;assert bytes(u.mem_read(0x2007ff00,32))==guard
  return u.reg_read(UC_ARM_REG_R0),seen,bytes(u.mem_read(FS,2048))
 import itertools
 rng=random.Random(384);cases=[]
 for route,count,index,child,null_list,mutate in itertools.product(['post','sfnt'],[0,1,3,-1,-2147483648],[-1,0,3,-2147483648],[0,2,0x10002],[False,True],[False,True]):cases.append(dict(header=0,post_offsets=0 if route=='post' else 85,sfnt_offsets=0,count=count,index=index,child=child,null_list=null_list,mutate=mutate))
 for header,post,sfnt in [(2,0,0),(85,0,0),(0x10002,0,0),(0,85,6),(0,2,0x10002)]:cases.append(dict(header=header,post_offsets=post,sfnt_offsets=sfnt,count=1,index=2,child=0,null_list=False,mutate=False))
 for case in cases:
  initial=bytearray(rng.getrandbits(8) for _ in range(2048));struct.pack_into('<I',initial,LIB-FS,MEM);struct.pack_into('<I',initial,MEM-FS+8,symbols['probe_free']);struct.pack_into('<I',initial,OUT-FS,FACE);native=run(0x5261ac+delta,initial,case);candidate=run(symbols['audio_uart_ft_read_mac_resource_5261ac'],initial,case);assert native==candidate,(case,native[:2],candidate[:2],[(i,a,b) for i,(a,b) in enumerate(zip(native[2],candidate[2])) if a!=b][:12])
 receipt={'status':'PASS_COMPLETE_MAC_RESOURCE_DISPATCH','comparisons':len(cases),'native_bytes':222,'actual_helpers':['selected memory free including NULL suppression'],'controlled_boundaries':['resource header parser','resource offsets parser','POST/SFNT parser','memory free callback'],'checks':['cached allocator despite library replacement','NULL offsets versus actual free','signed index modulo including dividezero/INT_MIN','POST/SFNT count writes','free callback mutates escaped count and face pointer','whole2KiB/SP/R4-R11/fifth arg/caller guard'],'limits':['Child resource parsers controlled; no initialized runtime/layout/hardware proof'],'selected':False};(D/'probe-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
finally:
 p.terminate();p.communicate(timeout=5)
