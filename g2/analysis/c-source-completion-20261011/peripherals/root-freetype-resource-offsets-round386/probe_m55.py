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







 FS=0x20003000;LIB=FS+0x100;MEM=FS+0x180;STREAM=FS+0x200;OUT=FS+0x280;COUNT=FS+0x284;BASE=FS+0x300;REFS=FS+0x800;OFFSETS=FS+0xa00
 saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11];seeds=[0x12345000+i*0x101 for i in range(8)]
 def run(entry,initial,args,stackargs,case,scalar=True):
  u.mem_write(FS,initial);u.reg_write(UC_ARM_REG_CPSR,0x01000000);u.reg_write(UC_ARM_REG_SP,0x2007ff00);u.reg_write(UC_ARM_REG_LR,stop_address|1)
  for r,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],args):u.reg_write(r,v&0xffffffff)
  for r,v in zip(saved,seeds):u.reg_write(r,v)
  guard=b''.join(struct.pack('<I',v&0xffffffff) for v in stackargs);guard+=b'\xa5'*(32-len(guard));u.mem_write(0x2007ff00,guard);u.reg_write(UC_ARM_REG_PC,entry&~1);seen=[];allocs=0
  for step in range(12):
   response=command('c');pc=u.reg_read(UC_ARM_REG_PC)
   if pc==stop_address:break
   n=targets.get(pc);assert n,(hex(pc),response);a,b=[u.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1]];assert a==MEM
   if n=='probe_alloc':
    allocs+=1;result=0 if allocs==case['oom'] or b>256 else (REFS if allocs==1 else OFFSETS);seen.append(('alloc',b,result));u.reg_write(UC_ARM_REG_R0,result)
   else:
    assert b==REFS;seen.append(('free',b))
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR)&~1)
  else:raise AssertionError('call bound')
  assert u.reg_read(UC_ARM_REG_SP)==0x2007ff00 and [u.reg_read(r) for r in saved]==seeds;assert bytes(u.mem_read(0x2007ff00,32))==guard
  return u.reg_read(UC_ARM_REG_R0) if scalar else None,seen,bytes(u.mem_read(FS,4096))
 import itertools
 rng=random.Random(386);cases=[];counts={}
 for types,subcount,tag,relative,size,sort,oom,negative_attributes,data in itertools.product([-32768,-1,0,1,4079],[-1,0,2,2726,2727],[0x504f5354,0x73666e74],[-1,32],[2,10,38,46,68,512],[0,1,256],[0,1,2],[False,True],[0,0xfffffff0]):
  # Orthogonal expensive dimensions only on ordinary valid records.
  if types!=0 and (subcount!=0 or relative!=32 or sort!=0 or oom!=0 or negative_attributes or data!=0):continue
  if subcount not in [0,2] and (sort!=0 or oom!=0 or negative_attributes or data!=0):continue
  cases.append(dict(types=types,subcount=subcount,tag=tag,relative=relative,size=size,sort=sort,oom=oom,negative=negative_attributes,data=data))
 for case in cases:
  initial=bytearray(rng.getrandbits(8) for _ in range(4096));initial[BASE-FS:BASE-FS+512]=bytes(512);struct.pack_into('>hIhh',initial,BASE-FS,case['types'],case['tag'],case['subcount'],case['relative'])
  if case['types']==1:struct.pack_into('>Ihh',initial,BASE-FS+10,0x504f5354,case['subcount'],32)
  for i,id in enumerate([3,-2,3]):struct.pack_into('>hHI4x',initial,BASE-FS+32+12*i,id,0,(0x80000000 if case['negative'] else 0x12000000)+[0x31,0x12,0x23][i])
  for a,v in [(LIB,MEM),(MEM+4,symbols['probe_alloc']),(MEM+8,symbols['probe_free']),(STREAM,BASE),(STREAM+4,case['size']),(STREAM+8,31),(STREAM+20,0)]:struct.pack_into('<I',initial,a-FS,v)
  args=[LIB,STREAM,0,case['data']];stack=[0x504f5354,case['sort'],OUT,COUNT];native=run(0x528298+delta,initial,args,stack,case);candidate=run(symbols['audio_uart_ft_raccess_offsets_528298'],initial,args,stack,case);assert native==candidate,(case,native[:2],candidate[:2],[(i,a,b) for i,(a,b) in enumerate(zip(native[2],candidate[2])) if a!=b][:16]);counts['offsets']=counts.get('offsets',0)+1
  if counts['offsets']%500==0:print('offsets',counts['offsets'],flush=True)
 for left,right in itertools.product([-32768,-2,-1,0,1,3,32767],repeat=2):
  initial=bytearray(rng.getrandbits(8) for _ in range(4096));struct.pack_into('<h',initial,REFS-FS,left);struct.pack_into('<h',initial,OFFSETS-FS,right);args=[REFS,OFFSETS,0,0];native=run(0x528272+delta,initial,args,[],{'oom':0});candidate=run(symbols['audio_uart_ft_resource_ref_compare_528272'],initial,args,[],{'oom':0});assert native==candidate;counts['comparator']=counts.get('comparator',0)+1
 for nullbase,nullcallback,count in itertools.product([False,True],[False,True],[0,1,3]):
  initial=bytearray(rng.getrandbits(8) for _ in range(4096))
  for i,id in enumerate([3,-2,3]):struct.pack_into('<h',initial,REFS-FS+8*i,id)
  native=run(0x567c4c+delta,initial,[0 if nullbase else REFS,count,8,0 if nullcallback else 0x528273+delta],[],{'oom':0},False);candidate=run(symbols['audio_uart_ft_qsort_567c4c'],initial,[0 if nullbase else REFS,count,8,0 if nullcallback else symbols['audio_uart_ft_resource_ref_compare_528272']],[],{'oom':0},False);assert native==candidate;counts['wrapper']=counts.get('wrapper',0)+1
 receipt={'status':'PASS_OFFSETS_COMPARATOR_SORT_WRAPPER','comparisons':sum(counts.values()),'by_component':counts,'native_sizes':[472,38,24],'actual_helpers':['stream seek/skip/BE16/BE32','selected realloc/zero/free','native sort core and swap graph in analysis only','C comparator used by native core in candidate path'],'controlled_boundaries':['allocation/free callbacks','sort core remains native oracle dependency; not production C source'],'checks':['type/resource count bounds','absent/present tags and signed relative offsets','short read/skip rollback','first/second allocation OOM and free','attribute signed rejection/24-bit masking/wrapped data offsets','signed duplicate resource IDs and sort flag low byte','comparator NULL sort-wrapper guards','whole4KiB/SP/R4-R11/four stacked args/caller guard'],'limits':['704-byte sort core not reduced to C; production import stays unresolved','Native sort instructions only in analysis ELF, not production','No initialized runtime/layout/hardware proof'],'selected':False};(D/'probe-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
finally:
 p.terminate();p.communicate(timeout=5)
