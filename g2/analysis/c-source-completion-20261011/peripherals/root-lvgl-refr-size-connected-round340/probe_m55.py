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
 targets[0x44e4aa+delta]='audio_uart_lv_obj_y_44e498'
 for address in targets:assert command('Z1,'+hex(address)[2:]+',2')=='OK'
 stop_address=symbols['probe_stop']&~1;assert command('Z1,'+hex(stop_address)[2:]+',2')=='OK'
 faults={0x43f1d8+delta:(UC_ARM_REG_R1,UC_ARM_REG_R0),0x28001098:(UC_ARM_REG_R0,UC_ARM_REG_R1)}
 for address in faults:assert command('Z1,'+hex(address)[2:]+',2')=='OK'
 OBJ=0x20003000;PARENT=0x20004000;SPEC=OBJ+0x500;PSPEC=OBJ+0x1500;DISPLAY=OBJ+0x1800;ROOTS=[0x2006f548,symbols['audio_uart_display_lv_root']];root_initial=bytearray(512);struct.pack_into('<I',root_initial,0x44,172);root_initial=bytes(root_initial);case={}
 saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11];seeds=[0x12345000+i*0x101 for i in range(8)]
 def word(a):return struct.unpack('<I',u.mem_read(a,4))[0]
 def put(a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
 def flags(a):return struct.unpack('<H',u.mem_read(a+42,2))[0]
 def set_flags(a,v):u.mem_write(a+42,struct.pack('<H',v&0xffff))
 def coords(a):return tuple(word(a+i) for i in [20,24,28,32])
 def rectangle(a):return struct.unpack('<4I',u.mem_read(a,16))
 def signed(v):return v if v<0x80000000 else v-0x100000000
 def resolve(v,ref):
  plain=v&0x9fffffff
  if v&0x60000000==0x20000000 and signed(plain)<0x1fffffff:
   factor=plain if signed(plain)<0x10000000 else (0xfffffff-plain)&0xffffffff;product=signed((factor*ref)&0xffffffff);return int(abs(product)//100)*(1 if product>=0 else -1)
  return signed(v)
 def text_at(a):
  out=bytearray()
  for offset in range(0,512,64):
   block=bytes(u.mem_read(a+offset,64));out.extend(block.split(b'\0',1)[0])
   if b'\0' in block:return out.decode('utf-8')
  raise AssertionError('unterminated string')
 def run(entry,initial,null=False):
  u.mem_write(OBJ,initial);u.reg_write(UC_ARM_REG_CPSR,0x01000000);u.reg_write(UC_ARM_REG_SP,0x2007ff00);u.reg_write(UC_ARM_REG_LR,stop_address|1);u.reg_write(UC_ARM_REG_R0,0 if null else OBJ);u.reg_write(UC_ARM_REG_PC,entry&~1)
  for r,v in zip(saved,seeds):u.reg_write(r,v)
  u.mem_write(0x2007ff00,b'\xa5'*16);seen=[];contain_count=0;dpi_count=0
  for root in ROOTS:u.mem_write(root,root_initial)
  for step in range(1024):
   response=command('c');pc=u.reg_read(UC_ARM_REG_PC)
   if pc==stop_address:break
   if pc in faults:
    assert null;address_reg,value_reg=faults[pc];assert u.reg_read(address_reg)==0xffffffff and u.reg_read(value_reg)==0;assert bytes(u.mem_read(0x2007ff00,16))==b'\xa5'*16;return ('pre-store',0xffffffff,0,4),seen
   name=targets.get(pc);assert name,(hex(pc),response)
   a=u.reg_read(UC_ARM_REG_R0);b=u.reg_read(UC_ARM_REG_R1);c=u.reg_read(UC_ARM_REG_R2);args=(a,);result=0
   if name=='audio_uart_lvgl_log':
    sp=u.reg_read(UC_ARM_REG_SP);args=(a,text_at(b),c,text_at(u.reg_read(UC_ARM_REG_R3)),text_at(word(sp)),text_at(word(sp+4)),text_at(word(sp+8)));assert null
   elif 'obj_parent_' in name:
    result=PARENT if case['has_parent'] else 0;set_flags(OBJ,flags(OBJ)^case['parent_flag_mutation'])
   elif 'obj_content_width_' in name:assert a==PARENT;result=case['reference_w']
   elif 'obj_content_height_' in name:assert a==PARENT;result=case['reference_h']
   elif 'obj_width_' in name:result=(word(a+28)-word(a+20)+1)&0xffffffff
   elif 'obj_height_' in name:result=(word(a+32)-word(a+24)+1)&0xffffffff
   elif 'style_property_' in name:
    args=(a,b,c);assert a in [OBJ,PARENT] and b in [0,0x10000]
    if c==1:result=case['sb_thickness'] if b else case['parent_style_w'] if a==PARENT else case['style_w']
    elif c==2:result=case['parent_style_h'] if a==PARENT else case['style_h']
    elif c==3:result=case['sb_length']
    elif c in [4,5,6,7]:result=case[{4:'minw',5:'maxw',6:'minh',7:'maxh'}[c]]
    elif c in [16,17,18,19]:result=case['spaces'][{16:'top',17:'bottom',18:'left',19:'right'}[c]]
    elif c in [24,25,26,27]:result=case['margins'][{24:'top',25:'bottom',26:'left',27:'right'}[c]]
    elif c==39:result=case['rtl']
    elif c==48:result=case['border']
    elif c==52:result=case['sides']
    elif c in [29,50]:result=case['opacity']
    else:raise AssertionError(('property',c))
   elif 'child_count_' in name:result=0
   elif 'has_flag_any_' in name:raise AssertionError('zero-child fixture unexpectedly queried a child')
   elif 'obj_has_flag_' in name:args=(a,b);assert a==PARENT and b==16;result=case['scrollable']
   elif 'obj_x_' in name or 'obj_y_' in name:
    spec=word(a+8);result=(0-word(spec+(32 if 'obj_x_' in name else 36)))&0xffffffff if spec else 0
   elif name=='audio_uart_display_default_get':
    args=();result=DISPLAY if case['has_display'] else 0
    if result:put(DISPLAY+24,case['dpi']+dpi_count*case['dpi_increment'])
    dpi_count+=1
   elif 'area_width_' in name:result=(word(a+8)-word(a)+1)&0xffffffff
   elif 'area_height_' in name:result=(word(a+12)-word(a+4)+1)&0xffffffff
   elif name=='audio_uart_display_invalidate_area':args=(a,rectangle(b));assert a==PARENT
   elif 'display_size_changed' in name:
    for off in [20,24,28,32]:put(a+off,word(a+off)+case['invalidate_delta'])
   elif 'obj_coords_' in name:
    values=coords(a);assert b%4==0;u.mem_write(b,struct.pack('<4I',*values));args=(a,values)
   elif 'obj_content_coords_' in name:
    assert a==PARENT and b%4==0;values=case['fit'];u.mem_write(b,struct.pack('<4I',*values));args=(a,values)
   elif 'area_contains_' in name:
    args=(rectangle(a),rectangle(b),c);assert c==0;result=case['contains'][contain_count];contain_count+=1
   elif 'scrollbar_invalidate_' in name:assert a==PARENT
   elif 'obj_event_' in name:
    if b==52:
     args=(a,b,struct.unpack('<2I',u.mem_read(c,8)));assert args[2] in [(0,0xe0000001),(0xe0000001,0)];u.mem_write(c,struct.pack('<2I',case['content_w'],case['content_h']))
    elif b==49:
     args=(a,b,rectangle(c));assert a==OBJ;put(c,word(c)+case['event_delta']);set_flags(OBJ,flags(OBJ)|0x1000)
    else:args=(a,b,c);assert args==(PARENT,42,OBJ);set_flags(OBJ,flags(OBJ)^0x8000)
   elif 'refresh_draw_' in name:assert a==OBJ;put(OBJ+48,0x33933933)
   else:raise AssertionError(name)
   result&=0xffffffff;seen.append((name,args,result,coords(OBJ),flags(OBJ),flags(PARENT)));u.reg_write(UC_ARM_REG_R0,result);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR)&~1)
  else:raise AssertionError(('callee stop bound',len(seen),[item[0] for item in seen[-8:]]))
  assert not null
  assert u.reg_read(UC_ARM_REG_SP)==0x2007ff00 and [u.reg_read(r) for r in saved]==seeds
  assert bytes(u.mem_read(0x2007ff00,16))==b'\xa5'*16
  for root in ROOTS:assert bytes(u.mem_read(root,512))==root_initial
  return u.reg_read(UC_ARM_REG_R0),seen,bytes(u.mem_read(OBJ,0x2000))
 rng=random.Random(339);total=0;returns={};styles=[0,1,0x3fffffff,0x20000000,0x20000064,0x30000000,0x30000004,0x3ffffffe,0xa0000001,0xffffffff,0x7fffffff,0x80000000]
 for trial in range(576):
  initial=bytearray(rng.getrandbits(8) for _ in range(0x2000));w=rng.choice([1,25,300,65536,0xffffffff,0x80000000]);h=rng.choice([1,25,300,65536,0xffffffff,0x80000000]);x=rng.getrandbits(32);y=rng.getrandbits(32)
  def initialize(a,v):struct.pack_into('<I',initial,a-OBJ,v&0xffffffff)
  initialize(OBJ+20,x);initialize(OBJ+24,y);initialize(OBJ+28,x+w-1);initialize(OBJ+32,y+h-1);struct.pack_into('<H',initial,42,[0,0x400,0x800,0xc00][trial//144%4]|(rng.getrandbits(4)<<12));struct.pack_into('<H',initial,PARENT-OBJ+42,[0,0x400,0x800,0xc00][trial//6%4])
  case={'has_parent':trial%19!=0,'parent_flag_mutation':0x400 if trial%23==0 else 0,'clamp_flag_mutation':0x400 if trial%29==0 else 0,'reference_w':rng.getrandbits(32),'reference_h':rng.getrandbits(32),'content_w':rng.getrandbits(32),'content_h':rng.getrandbits(32),'style_w':styles[trial%12],'style_h':styles[trial//12%12],'parent_style_w':0x3fffffff if trial%3==0 else 100,'parent_style_h':0x3fffffff if trial%5==0 else 100,'minw':w if trial%7==0 else 0,'maxw':w if trial%7==0 else 0x1fffffff,'minh':h if trial%7==0 else 0,'maxh':h if trial%7==0 else 0x1fffffff,'rtl':[0,1,2,255][trial%4],'spaces':{k:rng.getrandbits(32) for k in ['top','bottom','left','right']},'margins':{k:rng.getrandbits(32) for k in ['top','bottom','left','right']},'fit':tuple(rng.getrandbits(32) for _ in range(4)),'contains':[[0,0],[0,1],[1,0],[1,1],[256,255],[0xffffffff,256]][trial%6],'invalidate_delta':1 if trial%11==0 else 0,'event_delta':trial%3}
  case.update(clamp_flag_mutation=0,scrollable=int(trial%3!=0),sb_thickness=[0,1,5,0xffffffff][trial%4],sb_length=[0,1,10,0xffffffff][trial//4%4],border=[0,1,0xffffffff][trial%3],sides=[0,1,2,4,8,15,255,256,0xffffffff][trial%9],opacity=[0,1,2,255][trial//8%4],has_display=trial%13!=0,dpi=[0,130,160,300,0xffffffff][trial%5],dpi_increment=[0,1,17][trial//5%3])
  initialize(OBJ+8,SPEC if trial%2==0 else 0);initialize(PARENT+8,PSPEC if trial%7!=0 else 0);struct.pack_into('<H',initial,PSPEC-OBJ+50,(trial%4)|(15<<6))
  native=run(0x43f1a4+delta,bytes(initial));candidate=run(symbols['audio_uart_lv_basic_invalidate_43f1a4'],bytes(initial))
  if native!=candidate:
   (D/'mismatch.json').write_text(json.dumps({'trial':trial,'case':case,'native_result':native[0],'C_result':candidate[0],'native_calls':native[1],'C_calls':candidate[1],'memory_equal':native[2]==candidate[2]},indent=2)+'\n');raise AssertionError((trial,'see mismatch.json'))
  total+=1;returns[str(native[0])]=returns.get(str(native[0]),0)+1
  if total%32==0:print(json.dumps({'passed':total,'target':576}),flush=True)
 native=run(0x43f1a4+delta,bytes(0x2000),True);candidate=run(symbols['audio_uart_lv_basic_invalidate_43f1a4'],bytes(0x2000),True);assert native==candidate;assert len(native[1])==1;args=native[1][0][1];assert args[0]==3 and args[2:]==(89,'lv_obj_refr_size','Asserted at expression: %s (%s)','obj != NULL','NULL pointer')
 receipt={'status':'PASS_ACTUAL_SELECTED_TU_M55_CONNECTED_SIZE_REFRESH','positive_native_comparisons':total,'null_pre_store_comparisons':1,'return_histogram':returns,'candidate_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'controlled_lower_backends':len(mapping),'actual_helpers':['width-height clamps','raw style/margin/base direction wrappers','content sizing andself-size initializers','object/content coordinate/copy','four padding-space providers','scrollbar invalidate/size/areas/three extents/mode/dir/DPI/input-list'],'instruction_bytes_unchanged':True,'ordinary_string_pointer_bindings':'oracle-bindings.json','checks':['R0bits andordered lower backend inputs/outputs','Signed percentage encodings/product wrap/divide100/margins/clamp inputs','Live own/parent layout flags; mutating parent-getter/event backends; actual clamps execute','Four-word original/fit buffers anduint8 predicates','Coordinate/invalidate/event49/42/flagOR2/scrollbar/refresh sequence','Entire8KiB fixture region/SP/R4-R11/caller guard','Null89diagnostic andpre-store address/value/width'],'selected':False,'limits':['20lower backends controlled; child count0 fixtures; scrollable enabled/disabled andmode0/1/2/3 with empty active-input list; nonempty child/input integration remains','Null store stopped before execution; no physical fault claim','No full branch/access/image/hardware claim']};(D/'probe-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
finally:
 p.terminate();p.communicate(timeout=5)
