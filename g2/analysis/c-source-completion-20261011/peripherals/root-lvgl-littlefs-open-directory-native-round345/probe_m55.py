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
 faults={0x4c8fac+delta:(UC_ARM_REG_R1,UC_ARM_REG_R0),0x4c90b2+delta:(UC_ARM_REG_R1,UC_ARM_REG_R0),0x280000b8:(UC_ARM_REG_R0,UC_ARM_REG_R1)}
 for address in faults:assert command('Z1,'+hex(address)[2:]+',2')=='OK'
 DRIVER=0x20003000;FILE=DRIVER+0x400;PATH=DRIVER+0x800;FILENAME=DRIVER+0x1000;CTX=DRIVER+0x1200;CTX2=DRIVER+0x1400;case={}
 saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11];seeds=[0x12345000+i*0x101 for i in range(8)]
 def word(a):return struct.unpack('<I',u.mem_read(a,4))[0]
 def put(a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
 def string(a):
  out=bytearray()
  for offset in range(0,1024,64):
   data=bytes(u.mem_read(a+offset,64));out.extend(data.split(b'\0',1)[0])
   if b'\0' in data:return bytes(out)
  raise AssertionError('unbounded string')
 def run(entry,kind,initial,oom=False):
  u.mem_write(DRIVER,initial);u.reg_write(UC_ARM_REG_CPSR,0x01000000);u.reg_write(UC_ARM_REG_SP,0x2007ff00);u.reg_write(UC_ARM_REG_LR,stop_address|1);u.reg_write(UC_ARM_REG_R0,DRIVER);u.reg_write(UC_ARM_REG_R1,FILE if kind=='dir_read' else PATH);u.reg_write(UC_ARM_REG_R2,FILENAME if kind=='dir_read' else case['mode']);u.reg_write(UC_ARM_REG_R3,case['length']);u.reg_write(UC_ARM_REG_PC,entry&~1)
  for r,v in zip(saved,seeds):u.reg_write(r,v)
  u.mem_write(0x2007ff00,b'\xa5'*16);seen=[];ordinal=0
  for step in range(128):
   response=command('c');pc=u.reg_read(UC_ARM_REG_PC)
   if pc==stop_address:break
   if pc in faults:
    assert oom;ar,vr=faults[pc];assert u.reg_read(ar)==0xffffffff and u.reg_read(vr)==0;assert bytes(u.mem_read(0x2007ff00,16))==b'\xa5'*16;return ('pre-store',0xffffffff,0,4),seen
   name=targets.get(pc);assert name,(hex(pc),response);a=u.reg_read(UC_ARM_REG_R0);b=u.reg_read(UC_ARM_REG_R1);c=u.reg_read(UC_ARM_REG_R2);e=u.reg_read(UC_ARM_REG_R3);result=0;args=(a,)
   if name=='audio_uart_lv_malloc':assert a==(84 if kind=='open' else 52);result=0 if oom else FILE
   elif name=='audio_uart_lv_heap_free':assert a==FILE;u.mem_write(FILE,b'\xdd'*32)
   elif name=='audio_uart_lvgl_log':
    sp=u.reg_read(UC_ARM_REG_SP);args=(a,string(b).decode(),c,string(e).decode(),string(word(sp)).decode(),string(word(sp+4)).decode(),string(word(sp+8)).decode());assert oom
   elif 'snprintf_' in name:
    fmt=string(c);value=string(e);assert fmt in [b'%s',b'/%s'];args=('filename' if a==FILENAME else 'pathbuffer',b,fmt.decode(),value.decode());out=(b'/' if fmt==b'/%s' else b'')+value
    if b:u.mem_write(a,out[:b-1]+b'\0')
    result=len(out);put(DRIVER+48,CTX2)
   elif 'strlcpy_' in name:
    value=string(b);args=(a,value.decode(),c)
    if c:u.mem_write(a,value[:c-1]+b'\0')
    result=len(value);put(DRIVER+48,CTX2)
   elif name=='audio_file_lfs_open':
    args=(a,b,string(c).decode(),e);assert a==CTX2 and b==FILE;expected={1:2,2:1,3:3}.get(case['mode']&255,0);assert e==expected;result=case['return']
   elif 'dir_open_' in name:args=(a,b,string(c).decode());assert a==CTX2 and b==FILE;result=case['return']
   elif 'dir_read_' in name:
    assert a==CTX and b==FILE;row=case['entries'][ordinal] if ordinal<len(case['entries']) else (0,0,'');ordinal+=1;rc,typ,value=row;args=(a,b,ordinal,rc,typ,value);info=bytearray(264);info[0]=typ;struct.pack_into('<I',info,4,0x12345678);data=value.encode();assert len(data)<=255;info[8:8+len(data)]=data;u.mem_write(c,info);result=rc
   else:raise AssertionError(name)
   result&=0xffffffff;seen.append((name,args,result,word(DRIVER+48),bytes(u.mem_read(FILENAME,16)).hex()));u.reg_write(UC_ARM_REG_R0,result);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR)&~1)
  else:raise AssertionError('callee bound')
  assert not oom
  assert u.reg_read(UC_ARM_REG_SP)==0x2007ff00 and [u.reg_read(r) for r in saved]==seeds
  assert bytes(u.mem_read(0x2007ff00,16))==b'\xa5'*16
  return u.reg_read(UC_ARM_REG_R0),seen,bytes(u.mem_read(DRIVER,0x2000))
 import itertools
 rng=random.Random(345);counts={};entries={'open':(0x4c8f58,'audio_uart_lv_fs_open_4c8f58'),'dir_open':(0x4c9080,'audio_uart_lv_fs_dir_open_4c9080'),'dir_read':(0x4c9104,'audio_uart_lv_fs_dir_read_4c9104')}
 def fixture(path=''):
  initial=bytearray(rng.getrandbits(8) for _ in range(0x2000));struct.pack_into('<I',initial,48,CTX);data=path.encode()+b'\0';initial[PATH-DRIVER:PATH-DRIVER+len(data)]=data;return bytes(initial)
 def compare(kind,initial):
  address,name=entries[kind];native=run(address+delta,kind,initial);candidate=run(symbols[name],kind,initial)
  if native!=candidate:
   (D/'mismatch.json').write_text(json.dumps({'kind':kind,'case':case,'native_result':native[0],'C_result':candidate[0],'native_calls':native[1],'C_calls':candidate[1],'memory_equal':native[2]==candidate[2]},indent=2)+'\n');raise AssertionError((kind,'mismatch.json'))
  counts[kind]=counts.get(kind,0)+1;return native
 paths=['','a','x/../y','a'*255,'b'*256,'c'*300]
 for mode,path,result in itertools.product([0,1,2,3,255,256,257,258,259,0xffffffff],paths,[0,1,0x80000000,0xffffffff]):
  case={'mode':mode,'length':256,'return':result};v=compare('open',fixture(path));assert v[0]==(FILE if result==0 else 0);assert not any(row[0]=='audio_uart_lv_heap_free' for row in v[1])
 for path,result in itertools.product(paths,[0,1,0x80000000,0xffffffff]):
  case={'mode':0,'length':256,'return':result};v=compare('dir_open',fixture(path));assert v[0]==(FILE if result==0 else 0);assert sum(row[0]=='audio_uart_lv_heap_free' for row in v[1])==int(result!=0)
 scenarios=[[],[(-1,0,'')],[(1,1,'alpha')],[(1,2,'alpha')],[(1,2,'.'),(1,2,'..'),(1,1,'file')],[(1,1,'.')],[(1,1,'/.'),(0,0,'')],[(1,2,'.'),(-5,0,'')],[(1,3,'other')],[(1,2,'z'*255)],[(1,2,'..'),(1,2,'.'),(1,2,'folder')]]
 for rows,length in itertools.product(scenarios,[0,1,2,3,4,8,32,255,256,300]):
  case={'mode':0,'length':length,'entries':rows};v=compare('dir_read',fixture());assert v[0] in [0,11,12]
  if length==0:assert v[0]==11 and not v[1]
 nulls=[]
 for kind,line,expression in [('open',83,'lf != NULL'),('dir_open',204,'ld != NULL')]:
  case={'mode':3,'length':256,'return':0};address,name=entries[kind];initial=fixture('oom');n=run(address+delta,kind,initial,True);c=run(symbols[name],kind,initial,True);assert n==c;log=next(row for row in n[1] if row[0]=='audio_uart_lvgl_log');args=log[1];assert args[0]==3 and args[2:]==(line,'fs_open' if kind=='open' else 'fs_dir_open','Asserted at expression: %s (%s)',expression,'Out of memory');nulls.append({'kind':kind,'line':line,'fault_context':n[0]})
 receipt={'status':'PASS_ACTUAL_SELECTED_TU_M55_OPEN_DIRECTORY_CALLBACKS','positive_native_comparisons':sum(counts.values()),'per_function':counts,'oom_pre_store_comparisons':len(nulls),'candidate_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'controlled_child_targets':8,'actual_native_and_source_string_compare_execute':True,'instruction_bytes_unchanged':True,'ordinary_pointer_bindings':'oracle-bindings.json','checks':['Allocation84/52 andmode UXTB mapping','Path truncation256/formatter andbackend argument order','Fileerrornofree/direrrorfree','Info264/type0/name8/filenameclear','Dot-entry short-circuit/shortbuffer truncation/errorafter skip/eof/length0','Cached dir-read filesystem vsopen userdata afterformat','Entire8KiB region/SP/R4-R11/caller guard','TwoOOM diagnostic/pre-store address/value/width'],'oom_receipts':nulls,'selected':False,'limits':['Eight backend bodies controlled includingformatter/copy/allocator/LittleFS','No actual heap/filesystem/invalid-pointer/fullimage/hardware proof','OOM faultstores stoppedbeforeexecution']};(D/'probe-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
finally:
 p.terminate();p.communicate(timeout=5)
