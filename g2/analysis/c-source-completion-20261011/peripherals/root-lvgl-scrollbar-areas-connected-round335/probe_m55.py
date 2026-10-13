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
 saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11];seeds=[0x12345000+i*0x101 for i in range(8)]
 OBJ=0x20003000;SPEC=OBJ+0x500;NODE1=OBJ+0x1000;NODE2=OBJ+0x1100;DISPLAY=OBJ+0x1800;ROOTS=[0x2006f548,symbols['audio_uart_display_lv_root']];case={};H=V=0;root_initial=b''
 def words(a):return struct.unpack('<4I',u.mem_read(a,16))
 def run(entry,initial):
  u.reg_write(UC_ARM_REG_CPSR,0x01000000);u.reg_write(UC_ARM_REG_SP,0x2007ff00);u.reg_write(UC_ARM_REG_LR,stop_address|1);u.reg_write(UC_ARM_REG_R0,OBJ);u.reg_write(UC_ARM_REG_R1,H);u.reg_write(UC_ARM_REG_R2,V);u.reg_write(UC_ARM_REG_PC,entry&~1)
  for r,v in zip(saved,seeds):u.reg_write(r,v)
  u.mem_write(0x2007ff00,b'\xa5'*16);u.mem_write(OBJ,initial);seen=[];dpi_count=direction_count=0
  for root in ROOTS:u.mem_write(root,root_initial)
  for step in range(128):
   response=command('c');pc=u.reg_read(UC_ARM_REG_PC)
   if pc==stop_address:break
   name=targets.get(pc);assert name,(hex(pc),response)
   a=u.reg_read(UC_ARM_REG_R0);b=u.reg_read(UC_ARM_REG_R1);c=u.reg_read(UC_ARM_REG_R2);args=(a,);result=0
   if 'has_flag_' in name:args=(a,b);assert args==(OBJ,16);result=case['flag']
   elif 'obj_y_' in name:result=case['st']
   elif 'scroll_bottom_' in name:result=case['sb']
   elif 'scroll_left_' in name:result=case['sl']
   elif 'scroll_right_' in name:result=case['sr']
   elif 'obj_height_' in name:result=case['height']
   elif 'obj_width_' in name:result=case['width']
   elif 'display_default_get' in name:
    args=();result=DISPLAY if case['has_display'] else 0
    if result:u.mem_write(DISPLAY+24,struct.pack('<I',(case['dpi']+dpi_count*case['dpi_increment'])&0xffffffff))
    dpi_count+=1
   elif 'style_property_' in name:
    args=(a,b,c);assert (a,b)==(OBJ,0x10000)
    prop_key={1:'thickness',3:'length',16:'top',17:'bottom',18:'left',19:'right',29:'bg_opa',50:'border_opa',39:'rtl'};assert c in prop_key;result=case[prop_key[c]]
   else:raise AssertionError(name)
   result&=0xffffffff;seen.append((name,args,result,words(H),words(V),words(OBJ+20)));u.reg_write(UC_ARM_REG_R0,result);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR)&~1)
  else:raise AssertionError('Child stop bound')
  assert u.reg_read(UC_ARM_REG_SP)==0x2007ff00 and [u.reg_read(r) for r in saved]==seeds
  assert bytes(u.mem_read(0x2007ff00,16))==b'\xa5'*16
  for root in ROOTS:assert bytes(u.mem_read(root,512))==root_initial
  return list(seen),bytes(u.mem_read(OBJ,0x2400))
 rng=random.Random(334);total=0;dpi_hist={};alias_counts={}
 for trial in range(384):
  case={'flag':0 if trial%17==0 else 1,'mode':trial%4,'dir':[0,3,12,15][trial//4%4],'rtl':[0,1,2,255][trial//16%4],'bg_opa':[0,1,2,255][trial//64%4],'border_opa':[0,1,2,255][trial//11%4],'nodes':trial%3,'match':trial//3%3-1,'input_directions':[[12,3],[3,12],[0,15],[12,12]][trial//7%4],'dpi':[0,1,31,32,130,160,0x7fffffff,0x80000000,0xffffffff][trial//5%9],'dpi_increment':[0,1,0x10000000][trial//13%3]}
  for key in ['st','sb','sl','sr','height','width','top','bottom','left','right','thickness','length']:
   case[key]=rng.getrandbits(32) if trial%3==0 else rng.choice([0,1,2,10,20,200,0xffffffff])
  if trial>=256:
   case.update(mode=rng.randrange(4),dir=rng.randrange(16),rtl=rng.choice([0,1,2,255]),bg_opa=rng.choice([0,1,2,255]),border_opa=rng.choice([0,1,2,255]),nodes=rng.randrange(3),match=rng.randrange(-1,2))
  alias=trial%4;H=OBJ+0x2000;V=OBJ+0x2020
  if alias==1:V=H
  elif alias==2:H=OBJ+20
  elif alias==3:V=OBJ+20
  case['has_display']=trial%11!=0
  initial=bytearray(rng.getrandbits(8) for _ in range(0x2400));root=bytearray(rng.getrandbits(8) for _ in range(512));struct.pack_into('<I',initial,8,SPEC);struct.pack_into('<H',initial,SPEC-OBJ+50,case['mode']|(case['dir']<<6)|(rng.randrange(16)<<2));node_size=[172,176,200,224][trial%4];struct.pack_into('<I',root,0x44,node_size);struct.pack_into('<I',root,0x48,NODE1 if case['nodes'] else 0)
  for index,node in enumerate([NODE1,NODE2]):
   off=node-OBJ;initial[off]=[1,3,2,255][(trial//5+index)%4];initial[off+168]=case['input_directions'][index];struct.pack_into('<I',initial,off+112,OBJ if index==case['match'] else 0);struct.pack_into('<I',initial,off+node_size+4,NODE2 if index==0 and case['nodes']>1 else 0)
  root_initial=bytes(root);initial=bytes(initial);native=run(0x44eb28+delta,initial);candidate=run(symbols['audio_uart_lv_get_scrollbar_areas_44eb28'],initial)
  if candidate!=native:
   (D/'mismatch.json').write_text(json.dumps({'trial':trial,'case':case,'alias':alias,'native_calls':native[0],'C_calls':candidate[0],'memory_equal':native[1]==candidate[1]},indent=2)+'\n');raise AssertionError((trial,'see mismatch.json'))
  total+=1;dpi_calls=sum('display_default_get' in item[0] for item in native[0]);dpi_hist[str(dpi_calls)]=dpi_hist.get(str(dpi_calls),0)+1;alias_counts[str(alias)]=alias_counts.get(str(alias),0)+1
  if total%32==0:print(json.dumps({'passed':total,'target':384}),flush=True)
 receipt={'status':'PASS_ACTUAL_SELECTED_TU_M55_CONNECTED_SCROLLBAR_AREAS','native_comparisons':total,'candidate_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'native_payload_bytes_unchanged':True,'controlled_child_targets':9,'actual_connected_helpers':['area-set','raw style getters/base direction/width/length/opacities','mode/direction fields','input-list/head/next/input-type fields','display DPI including changing default-display data'],'alias_cases':alias_counts,'dpi_call_counts':dpi_hist,'checks':['Ordered9lower backend inputs/outputs','Per-call horizontal/vertical/object-coordinate snapshots','Entire9KiB fixture region including output aliases','DPI word24/default-null resolution/repeated macro evaluation','32bit wrap and observed signed-division paths','SP/R4-R11/caller guard'],'selected':False,'limits':['Nine lower backends controlled: flag,scrollY,three extents,width,height,property engine,default display; full image/hardware remains unproven','No invalid-pointer/full-image/hardware claim']};(D/'probe-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
finally:
 p.terminate();p.communicate(timeout=5)
