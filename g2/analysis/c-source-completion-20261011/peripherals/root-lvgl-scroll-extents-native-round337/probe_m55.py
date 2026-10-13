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
 faults={0x44e4ee+delta:(UC_ARM_REG_R1,UC_ARM_REG_R0),0x44e5b8+delta:(UC_ARM_REG_R1,UC_ARM_REG_R0),0x44e6ac+delta:(UC_ARM_REG_R1,UC_ARM_REG_R0),0x28000310:(UC_ARM_REG_R0,UC_ARM_REG_R1)}
 for address in faults:assert command('Z1,'+hex(address)[2:]+',2')=='OK'
 OBJ=0x20005000;SPEC=0x20006000;ARRAY=0x20007000;CHILD=0x20008000
 saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11];seeds=[0x12345000+i*0x101 for i in range(8)];case={};seen=[]
 def word(a):return struct.unpack('<I',u.mem_read(a,4))[0]
 def put(a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
 def text_at(a):
  out=bytearray()
  for offset in range(0,512,64):
   block=bytes(u.mem_read(a+offset,64));out.extend(block.split(b'\0',1)[0])
   if b'\0' in block:return out.decode('utf-8')
  raise AssertionError('unbounded string')
 def run(entry,initial,null=False):
  seen.clear();u.mem_write(OBJ,initial);u.reg_write(UC_ARM_REG_CPSR,0x01000000);u.reg_write(UC_ARM_REG_SP,0x2007ff00);u.reg_write(UC_ARM_REG_LR,stop_address|1);u.reg_write(UC_ARM_REG_R0,0 if null else OBJ);u.reg_write(UC_ARM_REG_PC,entry&~1)
  for r,v in zip(saved,seeds):u.reg_write(r,v)
  u.mem_write(0x2007ff00,b'\xa5'*16)
  for step in range(128):
   response=command('c');pc=u.reg_read(UC_ARM_REG_PC)
   if pc==stop_address:break
   if pc in faults:
    assert null;address_reg,value_reg=faults[pc];assert u.reg_read(address_reg)==0xffffffff and u.reg_read(value_reg)==0
    assert bytes(u.mem_read(0x2007ff00,16))==b'\xa5'*16
    return ('pre-store',0xffffffff,0,4),list(seen)
   name=targets.get(pc);assert name,(hex(pc),response)
   a=u.reg_read(UC_ARM_REG_R0);b=u.reg_read(UC_ARM_REG_R1);c=u.reg_read(UC_ARM_REG_R2);index=(a-CHILD)//256 if CHILD<=a<CHILD+8*256 else -1;row=case['children'][index] if index>=0 else None;args=(a,);result=0
   if 'child_count_' in name:result=len(case['children'])
   elif 'has_flag_any_' in name:args=(a,b);assert b==0x40001;result=int(bool(row['flags']&b))
   elif 'style_property_' in name:
    args=(a,b,c);assert b==0
    if c==39:result=case['rtl']
    else:
     key={25:'bottom',26:'left',27:'right'}[c];result=row['margins'][key];coordinate={25:32,26:20,27:28}[c];put(a+coordinate,word(a+coordinate)+case['margin_mutation'])
   elif 'obj_event_' in name:
    initial_buffer=struct.unpack('<2I',u.mem_read(c,8));args=(a,b,initial_buffer);assert b==52 and initial_buffer in [(0,0xe0000001),(0xe0000001,0)];u.mem_write(c,struct.pack('<2I',*case['self']))
    for offset in [20,28,32]:put(OBJ+offset,word(OBJ+offset)+case['event_mutation'])
   elif 'obj_width_' in name:result=case['width']
   elif 'obj_height_' in name:result=case['height']
   elif 'obj_x_' in name:result=(0-word(SPEC+32))&0xffffffff if word(OBJ+8) else 0
   elif 'obj_y_' in name:result=(0-word(SPEC+36))&0xffffffff if word(OBJ+8) else 0
   elif 'style_pad_' in name:
    args=(a,b);assert args==(OBJ,0);key=next(k for k in ['left','right','top','bottom'] if '_'+k+'_' in name);result=case['spaces'][key]
    for offset in [20,28,32]:put(OBJ+offset,word(OBJ+offset)+case['space_mutation'])
   elif name=='audio_uart_lvgl_log':
    sp=u.reg_read(UC_ARM_REG_SP);ptrs=[b,u.reg_read(UC_ARM_REG_R3),word(sp),word(sp+4),word(sp+8)];args=(a,text_at(ptrs[0]),c,*[text_at(v) for v in ptrs[1:]]);assert null
   else:raise AssertionError(name)
   result&=0xffffffff;seen.append((name,args,result,tuple(word(OBJ+x) for x in [20,28,32]),word(SPEC+32),word(SPEC+36)));u.reg_write(UC_ARM_REG_R0,result);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR)&~1)
  else:raise AssertionError('callee stop bound')
  assert not null
  assert u.reg_read(UC_ARM_REG_SP)==0x2007ff00 and [u.reg_read(r) for r in saved]==seeds
  assert bytes(u.mem_read(0x2007ff00,16))==b'\xa5'*16
  return u.reg_read(UC_ARM_REG_R0),list(seen),bytes(u.mem_read(OBJ,0x4000))
 entries=[(0x44e4bc,'audio_uart_lv_scroll_bottom_44e4bc'),(0x44e586,'audio_uart_lv_scroll_left_44e586'),(0x44e67a,'audio_uart_lv_scroll_right_44e67a')]
 rng=random.Random(337);total=0
 for trial in range(384):
  count=[0,1,2,4,8][trial%5];case={'rtl':[0,1,2,255,256,0xffffffff][trial%6],'spaces':{k:rng.getrandbits(32) for k in ['top','bottom','left','right']},'self':[rng.getrandbits(32),rng.getrandbits(32)],'width':rng.getrandbits(32),'height':rng.getrandbits(32),'margin_mutation':[0,1,0x7fffffff][trial%3],'space_mutation':[0,1,0xffffffff][trial//3%3],'event_mutation':[0,1,0x80000000][trial//9%3],'children':[]};initial=bytearray(rng.getrandbits(8) for _ in range(0x4000))
  def initialize(a,v):struct.pack_into('<I',initial,a-OBJ,v&0xffffffff)
  initialize(OBJ+8,0 if count==0 and trial%2==0 else SPEC);initialize(SPEC,ARRAY)
  for i in range(count):
   child=CHILD+i*256;initialize(ARRAY+i*4,child);case['children'].append({'flags':[0,1,0x40000,0x20000][rng.randrange(4)],'margins':{k:rng.getrandbits(32) for k in ['bottom','left','right']}})
   if trial%11==0:
    case['children'][-1]['margins']={'bottom':0,'left':0,'right':0};initialize(child+20,0x1fffffff);initialize(child+28,0xe0000001);initialize(child+32,0xe0000001);case['margin_mutation']=0
  for address,name in entries:
   native=run(address+delta,bytes(initial));candidate=run(symbols[name],bytes(initial))
   if native!=candidate:
    (D/'mismatch.json').write_text(json.dumps({'trial':trial,'entry':hex(address),'case':case,'native_result':native[0],'C_result':candidate[0],'native_calls':native[1],'C_calls':candidate[1],'memory_equal':native[2]==candidate[2]},indent=2)+'\n');raise AssertionError((trial,name,'see mismatch.json'))
   total+=1
  if (trial+1)%32==0:print(json.dumps({'positive_comparisons':total,'target':1152}),flush=True)
 null_receipts=[];initial=bytes(0x4000)
 for (address,name),line,function in zip(entries,[138,166,209],['lv_obj_get_scroll_bottom','lv_obj_get_scroll_left','lv_obj_get_scroll_right']):
  native=run(address+delta,initial,True);candidate=run(symbols[name],initial,True);assert native==candidate;assert len(native[1])==1;args=native[1][0][1];assert args[0]==3 and args[2]==line and args[3:]==(function,'Asserted at expression: %s (%s)','obj != NULL','NULL pointer');null_receipts.append({'native':hex(address),'line':line,'function':function,'fault_context':native[0],'path':args[1]})
 receipt={'status':'PASS_ACTUAL_SELECTED_TU_M55_THREE_SCROLL_EXTENTS','positive_native_comparisons':total,'null_native_comparisons':len(null_receipts),'candidate_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'controlled_child_targets':13,'actual_helpers':['base direction and margin properties via real native/selected C wrappers','self-size initializers/event-buffer return axes'],'instruction_bytes_unchanged':True,'ordinary_pointer_bindings':'oracle-bindings.json','checks':['R0bits','Ordered callees/property IDs/event initializers','Per-call coordinate/scroll snapshots','Mutating margin/space/event backends expose coordinate-read ordering','Entire16KiB fixture region','SP/R4-R11/caller guard onreturning paths','Null diagnostics and pre-store fault address/value/width'],'null_receipts':null_receipts,'selected':False,'limits':['Thirteen lower backends controlled; full property/event/space engine not qualified here','Null stores stopped immediately before execution; no physical fault orhardware claim','No complete branch/access/full-image claim']};(D/'probe-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
finally:
 p.terminate();p.communicate(timeout=5)
