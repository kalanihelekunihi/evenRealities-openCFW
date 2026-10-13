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






 FS=0x20003000;FACE=FS+0x100;INTERNAL=FS+0x200;DRIVER=FS+0x300;MEM=FS+0x400;NODES=[FS+0x500,FS+0x520,FS+0x540];PATH=FS+0x600;OUT=FS+0x700
 targets[symbols['probe_free']&~1]='probe_free';assert command('Z1,'+hex(symbols['probe_free']&~1)[2:]+',2')=='OK'
 saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11];seeds=[0x12345000+i*0x101 for i in range(8)]
 def word(a):return struct.unpack('<I',u.mem_read(a,4))[0]
 def put(a,v):u.mem_write(a,struct.pack('<I',v))
 def run(entry,kind,initial,case):
  u.mem_write(FS,initial);u.reg_write(UC_ARM_REG_CPSR,0x01000000);u.reg_write(UC_ARM_REG_SP,0x2007ff00);u.reg_write(UC_ARM_REG_LR,stop_address|1)
  args=[case['library'],case['path'],case['index'],case['out']] if kind=='new' else [case['list'],case['data'],0xabcdef,0x87654321] if kind in ['find','remove'] else [case['face'],0x12345678,0xabcdef,0x87654321]
  for register,value in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],args):u.reg_write(register,value)
  for register,value in zip(saved,seeds):u.reg_write(register,value)
  u.mem_write(0x2007ff00,b'\xa5'*32);u.reg_write(UC_ARM_REG_PC,entry&~1);seen=[]
  for step in range(4):
   response=command('c');pc=u.reg_read(UC_ARM_REG_PC)
   if pc==stop_address:break
   name=targets.get(pc);assert name,(hex(pc),response);a,b,c,d=[u.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];result=0xdeadbeef
   if name=='audio_uart_ft_open_face_internal_5264a6':
    assert (a,c,d)==(case['library'],case['index'],case['out']);assert word(u.reg_read(UC_ARM_REG_SP))==1;fields=(word(b),word(b+12),word(b+16));assert fields==(4,PATH,0);call=(a,fields,c,d,1);result=case['error']
    if d:put(d,FACE)
   elif name=='probe_free':
    assert a==MEM and b==NODES[case['position']];call=(a,b);put(b+8,0xabcddcba)
   else:
    assert name=='audio_uart_ft_destroy_face_5258a8' and (a,b,c)==(MEM,FACE,DRIVER);call=(a,b,c);put(FACE+8,0x76543210)
   seen.append((name,call,result));u.reg_write(UC_ARM_REG_R0,result);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR)&~1)
  else:raise AssertionError('bound')
  assert u.reg_read(UC_ARM_REG_SP)==0x2007ff00 and [u.reg_read(r) for r in saved]==seeds;assert bytes(u.mem_read(0x2007ff00,32))==b'\xa5'*32
  return (None if kind=='remove' else u.reg_read(UC_ARM_REG_R0)),seen,bytes(u.mem_read(FS,2048))
 rng=random.Random(371);cases=[]
 import itertools
 for library,path,index,out,error in itertools.product([0,MEM],[0,PATH],[0,1,0x80000000,0xffffffff],[0,OUT],[0,6,0xffffffff]):cases.append(('new',{'library':library,'path':path,'index':index,'out':out,'error':error}))
 for face,driver,count,position in itertools.product([0,FACE],[0,DRIVER],[0,1,2,0x80000000,0xffffffff],[-1,0,1,2]):cases.append(('done',{'face':face,'driver':driver,'count':count,'position':position}))
 for listptr,data in itertools.product([0,DRIVER+16],[0,FACE,0xabc000,0xabc001,0xabc002,0xffffffff]):cases.append(('find',{'list':listptr,'data':data,'position':1}))
 for listptr,node in itertools.product([0,DRIVER+16],[0,*NODES]):cases.append(('remove',{'list':listptr,'data':node,'position':1}))
 counts={}
 for kind,case in cases:
  initial=bytearray(rng.getrandbits(8) for _ in range(2048));struct.pack_into('<I',initial,FACE-FS+96,case.get('driver',DRIVER));struct.pack_into('<I',initial,FACE-FS+128,INTERNAL);struct.pack_into('<I',initial,INTERNAL-FS+64,case.get('count',1));struct.pack_into('<I',initial,DRIVER-FS+8,MEM);struct.pack_into('<II',initial,DRIVER-FS+16,NODES[0],NODES[-1]);struct.pack_into('<I',initial,MEM-FS+8,symbols['probe_free'])
  for i,node in enumerate(NODES):struct.pack_into('<III',initial,node-FS,NODES[i-1] if i else 0,NODES[i+1] if i<2 else 0,FACE if i==case.get('position',-1) else 0xabc000+i)
  initial[PATH-FS:PATH-FS+9]=b'font.ttf\0';address,name={'new':(0x525ade,'audio_uart_ft_new_face_525ade'),'done':(0x526814,'audio_uart_ft_done_face_526814'),'find':(0x5292e6,'audio_uart_ft_list_find_5292e6'),'remove':(0x529324,'audio_uart_ft_list_remove_529324')}[kind];native=run(address+delta,kind,initial,case);candidate=run(symbols[name],kind,initial,case);assert native==candidate,(kind,case,native[:2],candidate[:2]);counts[kind]=counts.get(kind,0)+1
 receipt={'status':'PASS_FOUR_FACE_LIFECYCLE_BODIES_CONNECTED','comparisons':sum(counts.values()),'per_path':counts,'actual_helpers':['list find','list remove','FT memory free'],'controlled_boundaries':['internal face opener','face destructor','memory free callback'],'checks':['NULL pathname/library/output forwarding and stackedtestmac1','only flags/pathname/stream initialized and semantically consumed','signed faceindex/error propagation','invalid face/driver/refcount decrement signedwrap','head/middle/tail/absent list node','remove-before-free-before-destroy','whole2KiB/SP/R4-R11/caller guard'],'limits':['Unused uninitialized OpenArgs fields excluded from comparison; flags select pathname source contract','Deeper opener/destructor/free callback controlled','No image/layout/hardware proof'],'selected':False};(D/'probe-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
finally:
 p.terminate();p.communicate(timeout=5)
