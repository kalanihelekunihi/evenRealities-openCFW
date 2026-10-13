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







 FS=0x20003000;LIB=FS+0x100;ARGS=FS+0x200;MEM=FS+0x300;D1=FS+0x400;D2=FS+0x440;NON=FS+0x480;C1=FS+0x500;C2=FS+0x540;CN=FS+0x580;NAME1=FS+0x600;NAME2=FS+0x620;FACE=FS+0x800;INTERNAL=FS+0x900;STRIKES=FS+0xa00;STREAM=FS+0xb00;NODE=FS+0xc00;SIZE=FS+0xd00;OUT=FS+0xe00;PARAMS=FS+0xf00
 targets[symbols['probe_alloc']&~1]='probe_alloc';assert command('Z1,'+hex(symbols['probe_alloc']&~1)[2:]+',2')=='OK'
 saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11];seeds=[0x12345000+i*0x101 for i in range(8)]
 def word(a):return struct.unpack('<I',u.mem_read(a,4))[0]
 def put(a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
 def run(entry,initial,case):
  u.mem_write(FS,initial);u.reg_write(UC_ARM_REG_CPSR,0x01000000);u.reg_write(UC_ARM_REG_SP,0x2007ff00);u.reg_write(UC_ARM_REG_LR,stop_address|1)
  for register,value in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],[LIB,ARGS if case['args'] else 0,case['index']&0xffffffff,OUT if case['out'] else 0]):u.reg_write(register,value)
  for register,value in zip(saved,seeds):u.reg_write(register,value)
  u.mem_write(0x2007ff00,struct.pack('<I',case['mac'])+b'\xa5'*28);guard=bytes(u.mem_read(0x2007ff00,32));u.reg_write(UC_ARM_REG_PC,entry&~1);seen=[];drivercalls=0
  for step in range(16):
   response=command('c');pc=u.reg_read(UC_ARM_REG_PC)
   if pc==stop_address:break
   n=targets.get(pc);assert n,(hex(pc),response);a,b,c,d=[u.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];sp=u.reg_read(UC_ARM_REG_SP);result=0x87654321
   if n=='probe_alloc':
    assert (a,b)==(MEM,12);call=(a,b);result=NODE if not case['alloc_error'] else 0
   elif n=='audio_uart_ft_stream_new_524f96':
    assert (a,b)==(LIB,ARGS);put(c,STREAM if not case['stream_error'] else 0);call=(a,b,'stream_out');result=case['stream_error']
   elif n=='audio_uart_ft_open_driver_face_5259be':
    assert a in [D1,D2] and word(b)==STREAM and c==case['external'] and d==case['index']&0xffffffff
    count,params,faceout=word(sp),word(sp+4),word(sp+8);assert (count,params)==(0x80000000,PARAMS) if case['params'] else (count,params)==(0,0)
    call=(a,'streamcell',c,d,count,params,'face_out');result=case['open_errors'][drivercalls];drivercalls+=1
    if result==0 or case['face_on_error']:put(faceout,FACE)
   elif n=='audio_uart_font_mem_alloc':assert (a,b)==(MEM,12);put(c,case['alloc_error']);call=(a,b,'error_out');result=NODE if not case['alloc_error'] else 0
   elif n=='audio_uart_ft_list_add_529304':assert (a,b)==(D2+16,NODE) and word(NODE+8)==FACE;call=(a,b);put(D2+16,NODE)
   elif n=='audio_uart_ft_new_glyph_slot_525386':assert (a,b)==(FACE,0);call=(a,b);result=case['glyph_error']
   elif n=='audio_uart_ft_new_size_52687e':assert a==FACE;put(b,SIZE);call=(a,'size_out');result=case['size_error']
   elif n=='audio_uart_ft_stream_seek_5288e0':assert (a,b)==(STREAM,0);call=(a,b);result=case['seek_error']
   elif n=='audio_uart_ft_open_ps_sfnt_525d32':
    call=(a,b,c,d,word(sp),word(sp+4));assert call==(LIB,STREAM,case['index']&0xffffffff,0x80000000 if case['params'] else 0,PARAMS if case['params'] else 0,OUT if case['out'] else 0);result=case['ps_error']
   elif n=='audio_uart_ft_load_mac_face_526452':
    call=(a,b,c,d,word(sp));assert call==(LIB,STREAM if not case['stream_error'] else 0,case['index']&0xffffffff,OUT if case['out'] else 0,ARGS);result=case['mac_error']
   elif n=='audio_uart_ft_stream_free_52502a':call=(a,b);assert b==case['external']
   elif n=='audio_uart_ft_done_face_526814':assert a==FACE;call=(a,)
   else:assert n=='audio_uart_ft_destroy_face_5258a8' and (a,b)==(MEM,FACE);call=(a,b,c)
   seen.append((n,call,result));u.reg_write(UC_ARM_REG_R0,result);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR)&~1)
  else:raise AssertionError('bound')
  assert u.reg_read(UC_ARM_REG_SP)==0x2007ff00 and [u.reg_read(r) for r in saved]==seeds;assert bytes(u.mem_read(0x2007ff00,32))==guard
  return u.reg_read(UC_ARM_REG_R0),seen,bytes(u.mem_read(FS,4096))
 default={'args':1,'out':1,'index':0,'mac':0,'external':0,'params':0,'explicit':0,'module_count':3,'stream_error':0,'open_errors':[0,0],'face_on_error':0,'alloc_error':0,'glyph_error':0,'size_error':0,'seek_error':0,'ps_error':2,'mac_error':2,'faceflags':0,'height':0xfff6,'strikes':0}
 cases=[]
 def add(**kw):cases.append(dict(default,**kw))
 import itertools
 for args,out,index in itertools.product([0,1],[0,1],[0,-1,0x7fffffff,-0x80000000]):add(args=args,out=out,index=index)
 for explicit,params,external,err in itertools.product([0,1,2],[0,1],[0,1],[0,2,6]):add(explicit=explicit,params=params,external=external,open_errors=[err,0],face_on_error=int(err==6))
 for err,mac,macerr in itertools.product([81,2,85,6,0x10002],[0,1],[0,2,6]):add(stream_error=err,mac=mac,mac_error=macerr)
 for mac,seek,ps,params in itertools.product([0,1],[0,6],[0,2,6],[0,1]):add(open_errors=[142,2],mac=mac,seek_error=seek,ps_error=ps,params=params)
 for alloc,glyph,size in [(64,0,0),(0,6,0),(0,0,6)]:add(alloc_error=alloc,glyph_error=glyph,size_error=size)
 for flags,height,index in itertools.product([0,1,2,3,33],[0xfff6,0x8000],[0,-1]):add(faceflags=flags,height=height,index=index,strikes=2)
 add(module_count=0);add(open_errors=[2,2],mac=1,mac_error=0);add(open_errors=[2,2],mac=0);add(mac=256,open_errors=[142,2])
 rng=random.Random(377);count=0
 for case in cases:
  initial=bytearray(rng.getrandbits(8) for _ in range(4096))
  def pack(a,v):struct.pack_into('<I',initial,a-FS,v&0xffffffff)
  for a,v in [(LIB,MEM),(MEM+4,symbols['probe_alloc']),(LIB+16,case['module_count']),(LIB+20,NON),(LIB+24,D1),(LIB+28,D2),(ARGS,4|case['external']*2|case['params']*16|(8 if case['explicit'] else 0)),(ARGS+16,STREAM),(ARGS+20,D1 if case['explicit']==1 else NON),(ARGS+24,0x80000000),(ARGS+28,PARAMS),(D1,C1),(D2,C2),(NON,CN),(C1,1),(C2,1),(CN,0),(C1+8,NAME1),(C2+8,NAME2),(FACE+96,D2),(FACE+128,INTERNAL),(FACE+8,case['faceflags']),(FACE+28,case['strikes']),(FACE+32,STRIKES)]:pack(a,v)
  initial[NAME1-FS:NAME1-FS+9]=b'truetype\0';initial[NAME2-FS:NAME2-FS+4]=b'cff\0';struct.pack_into('<H',initial,FACE-FS+74,case['height'])
  struct.pack_into('<4I',initial,STRIKES-FS,0x1234fff6,12,0xfffffff0,0x80000000);struct.pack_into('<4I',initial,STRIKES-FS+16,0x12348000,12,10,20)
  native=run(0x5264a6+delta,initial,case);candidate=run(symbols['audio_uart_ft_open_face_internal_5264a6'],initial,case)
  if native!=candidate:
   (D/'mismatch.json').write_text(json.dumps({'case':case,'native_result':native[0],'C_result':candidate[0],'native_calls':native[1],'C_calls':candidate[1],'memory_equal':native[2]==candidate[2]},indent=2)+'\n');raise AssertionError('mismatch.json')
  count+=1
  if count%50==0:print('comparisons',count,flush=True)
 receipt={'status':'PASS_FULL_INTERNAL_OPENER_CONNECTED_REAL_MEMORY_ALLOC_AND_ZERO','comparisons':count,'controlled_boundaries':list(mapping),'actual_helpers':['pathname compare','FT memory allocation','compiler memory zero'],'checks':['invalidargs/nulloutput/indexqueries','explicit and scanned drivers','seven/six/five parameter stacked ABI','externalstream ownership','Mac/PS fallbacks and error normalization','node/glyphslot/size failure cleanup','scalable height/vertical/fixed-strike overflow normalization','internal defaults/output/release','whole4KiB/SP/R4-R11/caller guard'],'limits':['Eleven child providers plus allocation callback controlled; deeper driver/fallback/runtime obligations remain','No image/layout/hardware proof'],'selected':False};(D/'connected-probe-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
finally:
 p.terminate();p.communicate(timeout=5)
