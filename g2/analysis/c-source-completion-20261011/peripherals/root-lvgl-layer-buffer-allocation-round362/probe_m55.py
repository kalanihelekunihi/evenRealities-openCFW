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
 ROOT=FS+0x1000;LAYER=FS+0x500;BUF=FS+0x900;ALT=FS+0xa00;DATA=FS+0x1700;assert symbols['audio_uart_display_lv_root']==ROOT
 def run(entry,kind,initial):
  u.mem_write(FS,initial);u.reg_write(UC_ARM_REG_CPSR,0x01000000);u.reg_write(UC_ARM_REG_SP,0x2007ff00);u.reg_write(UC_ARM_REG_LR,stop_address|1)
  args=[case['width'],case['height'],case['format'],case['stride']] if kind=='wrapper' else [LAYER,0x1234,0xabcdef,0xfedcba]
  for register,value in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],args):u.reg_write(register,value&0xffffffff)
  u.reg_write(UC_ARM_REG_PC,entry&~1)
  for register,value in zip(saved,seeds):u.reg_write(register,value)
  u.mem_write(0x2007ff00,b'\xa5'*32);seen=[]
  for step in range(6):
   response=command('c');pc=u.reg_read(UC_ARM_REG_PC)
   if pc==stop_address:break
   name=targets.get(pc);assert name,(hex(pc),response);a=u.reg_read(UC_ARM_REG_R0);b=u.reg_read(UC_ARM_REG_R1);c=u.reg_read(UC_ARM_REG_R2);d=u.reg_read(UC_ARM_REG_R3);sp=u.reg_read(UC_ARM_REG_SP)
   if name=='audio_uart_font_bitmap_stride':
    assert kind=='layer' and (a,b)==(case['width'],case['format']);args=(a,b);result=case['stride'];u.mem_write(LAYER+20,bytes([case['create_format']]));put(ROOT+324,0x13579bdf)
   elif name=='audio_uart_font_bitmap_allocate':
    stride=word(sp);assert (a,b,c,d,stride)==(ROOT+200,case['width'],case['height'],case['create_format'] if kind=='layer' else case['format']&255,0 if kind=='layer' else case['stride']);args=(a,b,c,d,stride);result=case['allocation'];put(BUF+16,DATA);put(ALT+16,DATA+0x80)
    if kind=='layer':u.mem_write(LAYER+20,bytes([case['alpha_format']]));put(ROOT+324,case['counter_after']);put(LAYER,ALT)
   elif name=='audio_uart_lv_draw_buf_clear_48ac40':
    assert (a,b)==(BUF,0);args=(a,b);result=0xdeadbeef;put(BUF+16,DATA+0x40)
    if case['mutate']:put(LAYER,ALT)
   else:
    assert name=='audio_uart_lvgl_log';args=(a,string(b),c,string(d),string(word(sp)));assert a==2 and c==471;result=0x87654321;put(LAYER+24,0x12345678)
   seen.append((name,args,result));u.reg_write(UC_ARM_REG_R0,result&0xffffffff);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR)&~1)
  else:raise AssertionError('calleebound')
  assert u.reg_read(UC_ARM_REG_SP)==0x2007ff00 and [u.reg_read(r) for r in saved]==seeds
  assert bytes(u.mem_read(0x2007ff00,32))==b'\xa5'*32
  return u.reg_read(UC_ARM_REG_R0),seen,bytes(u.mem_read(FS,8192))
 rng=random.Random(362);counts={}
 def compare(kind,address,name,initial):
  native=run(address+delta,kind,bytes(initial));candidate=run(symbols[name],kind,bytes(initial))
  if native!=candidate:
   (D/'mismatch.json').write_text(json.dumps({'kind':kind,'case':case,'native_result':native[0],'C_result':candidate[0],'native_calls':native[1],'C_calls':candidate[1],'memory_equal':native[2]==candidate[2]},indent=2)+'\n');raise AssertionError('mismatch.json')
  counts[kind]=counts.get(kind,0)+1
 import itertools
 for fmt,dimensions,stride in itertools.product([0,11,12,13,14,15,16,20,21,255,256,0xffffffff],[(1,1),(640,480),(0x80000000,0xffffffff),(0xffffffff,0)],[0,1,0xffffffff]):
  case={'format':fmt,'create_format':fmt&255,'width':dimensions[0],'height':dimensions[1],'stride':stride,'allocation':BUF};initial=bytearray(rng.getrandbits(8) for _ in range(8192));compare('wrapper',0x48affa,'audio_uart_display_surface_alloc',initial)
 for index,(fmt,coords,allocation) in enumerate(itertools.product([0,11,12,13,14,15,16,20,21,255],[[0,0,639,479],[1,2,1,2],[10,10,9,9],[0x80000000,0xffffffff,0x7fffffff,0]],[0,BUF])):
  x1,y1,x2,y2=coords;width=(x2-x1+1)&0xffffffff;height=(y2-y1+1)&0xffffffff;mutate=index%2;after_stride=(fmt^1)&255 if mutate else fmt;after_allocate=(after_stride+1)&255 if mutate else fmt
  case={'format':fmt,'create_format':after_stride,'alpha_format':after_allocate,'width':width,'height':height,'stride':[0,1,40,0x80000000,0xffffffff][index%5],'allocation':allocation,'counter_after':[0,0xffffffff,0x80000000,0x12345678][index%4],'mutate':mutate};initial=bytearray(rng.getrandbits(8) for _ in range(8192));struct.pack_into('<I',initial,LAYER-FS,0)
  for offset,value in zip([4,8,12,16],coords):struct.pack_into('<I',initial,LAYER-FS+offset,value)
  initial[LAYER-FS+20]=fmt;compare('layer',0x484836,'audio_uart_lv_draw_layer_alloc_buf_484836',initial)
 for value in [0,DATA,0x80000000,0xffffffff]:
  case={};initial=bytearray(rng.getrandbits(8) for _ in range(8192));struct.pack_into('<I',initial,LAYER-FS,BUF);struct.pack_into('<I',initial,BUF-FS+16,value);compare('cached',0x484836,'audio_uart_lv_draw_layer_alloc_buf_484836',initial)
 receipt={'status':'PASS_FULL_LAYER_ALLOC_AND_CREATION_WRAPPER_SELECTED_TU_M55','native_comparisons':sum(counts.values()),'per_path':counts,'candidate_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'controlled_lower_backends':4,'actual_helpers_execute':['areaextentwidthheight','coloralphaclassifier','completecreationwrapper'],'checks':['Widthheight32bitwrap/fromsignedextents','FormatUXTB/wrapperfifthstackstride/descriptorroot200','Strideandallocationformatrereads/counterafterbackendmutation/wrappedproductsum','AllocationfailureexactWARNpath471/function/message/return0','Actualalpha/currentformat/clearandre-readbufferdatapointer','Cachedpathnoallocation/log/counter/clear','Whole8KiB/SP/R4-R11/caller32byteguard'],'selected':False,'limits':['Stride/create_ex/clear/loggercontrolled; realextentandalphaclassifierexecute','No max-memorylimit/info-log invented; nativecontainsneither','Syntheticoverflow/mutationfixtures notvalidhardwareconfigproof','No completeimage/layout/byteidentity/hardwareclaim']};(D/'probe-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
finally:
 p.terminate();p.communicate(timeout=5)
