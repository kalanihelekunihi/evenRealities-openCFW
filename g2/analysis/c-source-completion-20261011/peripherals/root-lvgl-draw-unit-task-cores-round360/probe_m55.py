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
 ROOT=FS+0x1000;LAYER=FS+0x500;T1=FS+0x100;T2=FS+0x200;T3=FS+0x300;UNIT=FS+0x700;DISPLAY=FS+0x1600;CELL=ROOT+328;assert symbols['audio_uart_display_lv_root']==ROOT
 def run(entry,kind,initial):
  u.mem_write(FS,initial);u.reg_write(UC_ARM_REG_CPSR,0x01000000);u.reg_write(UC_ARM_REG_SP,0x2007ff00);u.reg_write(UC_ARM_REG_LR,stop_address|1)
  for register,value in [(UC_ARM_REG_R0,case['size'] if kind=='create' else LAYER),(UC_ARM_REG_R1,case.get('previous',0)),(UC_ARM_REG_R2,case.get('id',0)),(UC_ARM_REG_R3,0xfeed1234),(UC_ARM_REG_PC,entry&~1)]:u.reg_write(register,value)
  for register,value in zip(saved,seeds):u.reg_write(register,value)
  u.mem_write(0x2007ff00,b'\xa5'*32);seen=[]
  for step in range(16):
   response=command('c');pc=u.reg_read(UC_ARM_REG_PC)
   if pc==stop_address:break
   name=targets.get(pc);assert name,(kind,hex(pc),response);a=u.reg_read(UC_ARM_REG_R0);b=u.reg_read(UC_ARM_REG_R1);c=u.reg_read(UC_ARM_REG_R2);d=u.reg_read(UC_ARM_REG_R3);sp=u.reg_read(UC_ARM_REG_SP)
   if name=='audio_uart_lvgl_log':
    args=(a,string(b),c,string(d),string(word(sp)),string(word(sp+4)),string(word(sp+8)));seen.append((name,args));assert a==3 and c==84
    assert bytes(u.mem_read(0x2007ff00,32))==b'\xa5'*32
    return 'oom-boundary',seen,bytes(u.mem_read(FS,8192))
   if name=='audio_uart_lv_heap_alloc':
    assert a==case['size'];args=(a,);result=case['allocation']
    if result:u.mem_write(result,bytes(a))
   elif name=='audio_uart_lv_draw_task_independent_4848b2':
    assert a==LAYER and b in [T1,T2,T3];args=(a,b);result=case['independent'].get(b,1)
    put(b+84,0x13579bdf)
    if result==0:put(b,T3)
   elif name=='audio_uart_display_default_get':args=();result=DISPLAY
   elif name=='audio_uart_lv_anim_mutex_ensure_4d47fa':
    assert a==CELL;args=(a,);result=0x87654321;put(CELL,0x999)
   elif name in ['stock_enter_critical','stock_exit_critical']:args=();result=0xabcdef01
   else:
    assert name=='audio_notify_task' and (a,b,c,d,word(sp))==(case['waiter'],0,0,2,0);args=(a,b,c,d,word(sp));result=0xffffffff;put(CELL+4,0x2468ace0)
   seen.append((name,args,result));u.reg_write(UC_ARM_REG_R0,result&0xffffffff);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR)&~1)
  else:raise AssertionError('callee/loopbound')
  assert u.reg_read(UC_ARM_REG_SP)==0x2007ff00 and [u.reg_read(r) for r in saved]==seeds,(kind,hex(entry),'ABI')
  assert bytes(u.mem_read(0x2007ff00,32))==b'\xa5'*32
  return (0 if kind=='dispatch' else u.reg_read(UC_ARM_REG_R0)),seen,bytes(u.mem_read(FS,8192))
 rng=random.Random(360);counts={};oom=0
 def fixture():return bytearray(rng.getrandbits(8) for _ in range(8192))
 def store(mem,address,value):struct.pack_into('<I',mem,address-FS,value&0xffffffff)
 def compare(kind,address,name,initial):
  global oom
  native=run(address+delta,kind,bytes(initial));candidate=run(symbols[name],kind,bytes(initial))
  if native!=candidate:
   (D/'mismatch.json').write_text(json.dumps({'kind':kind,'case':case,'native_result':native[0],'C_result':candidate[0],'native_calls':native[1],'C_calls':candidate[1],'memory_equal':native[2]==candidate[2]},indent=2)+'\n');raise AssertionError('mismatch.json')
  oom+=native[0]=='oom-boundary';counts[kind]=counts.get(kind,0)+1
 import itertools
 for count,head,size,allocation in itertools.product([0,1,255,0xffffffff],[0,T1],[12,16,228],[0,UNIT,ROOT+312,ROOT+316]):
  case={'size':size,'allocation':allocation};initial=fixture();store(initial,ROOT+316,head);store(initial,ROOT+320,count);compare('create',0x484398,'audio_uart_lv_draw_unit_create_484398',initial)
 for waiter,pending in itertools.product([0,T1,0xffffffff],[0,1,0xffffffff]):
  case={'size':0,'waiter':waiter};initial=fixture();store(initial,CELL+4,pending);store(initial,CELL+8,waiter);compare('dispatch',0x48462e,'audio_uart_lv_draw_dispatch_request_48462e',initial)
 for pointer in [0,DISPLAY,T1,0xffffffff]:
  case={'size':0};initial=fixture();store(initial,ROOT+16,pointer);compare('refresh',0x453604,'audio_uart_lv_refreshing_display_453604',initial)
 for head,state in itertools.product([0,T1],[0,1,2,0xffffffff]):
  case={'size':0};initial=fixture();store(initial,LAYER+68,head);store(initial,T1+80,state);compare('first',0x4849fc,'audio_uart_lv_draw_first_available_4849fc',initial)
 for kind,address,name in [('available',0x48463a,'audio_uart_lv_draw_get_available_task_48463a'),('next',0x484656,'audio_uart_lv_draw_next_available_484656')]:
  units=[0,1,2,0xffffffff] if kind=='available' else [2]
  for unit_count,unit_id,previous,scenario,dimensions in itertools.product(units,[0,9,256,511],[0,T1,T2],range(6),[(640,480,0),(480,640,3),(0,0,0),(0x80000000,0xffffffff,1)]):
   width,height,rotation=dimensions;case={'size':0,'id':unit_id,'previous':previous,'scenario':scenario,'independent':{T1:0 if scenario==5 else 1,T2:0x100,T3:0xffffffff}};initial=fixture();store(initial,ROOT+320,unit_count);store(initial,ROOT+16,DISPLAY);store(initial,DISPLAY,width);store(initial,DISPLAY+4,height);initial[DISPLAY-FS+0x2fc]=rotation
   w,h=(height,width) if rotation in [1,3] else (width,height)
   store(initial,LAYER+68,0 if scenario==0 else T1)
   for task,nxt in [(T1,T2),(T2,T3),(T3,0)]:
    store(initial,task,nxt);store(initial,task+80,1);initial[task-FS+88]=9 if task==T2 else 0
    for offset,value in [(8,1),(12,1),(16,2),(20,2)]:store(initial,task+offset,value)
   if scenario in [2,3]:store(initial,T1+80,2)
   if scenario==3:
    for offset,value in [(8,0),(12,0),(16,w-1),(20,h-1)]:store(initial,T1+offset,value)
   if scenario==4:initial[T1-FS+88]=2
   compare(kind,address,name,initial)
  print(json.dumps({'kind':kind,'passed':counts[kind]}),flush=True)
 receipt={'status':'PASS_SIX_COMPLETE_DRAW_BODIES_SELECTED_TU_M55','native_comparisons':sum(counts.values()),'per_function':counts,'oom_boundary_cases':oom,'candidate_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'controlled_lower_backends':8,'actual_native_and_selected_execute':['dimensiongetters','refreshgetter','firsttask','multitaskselector','availabilitywrapper','existingsyncsignal'],'checks':['Unitallocationzeroed/listinsertion/counterwrap/indexandrereads/aliasfixtures','ExactOOM84logsource/function/format/expression/reasonbeforefatalhandler','Singleunitonlyfirsttask/multipleunitpriornext/state/preferredUXTB/independence','Fullscreenbusyhead/signedcoordinates/unsigneddimensionminus1/rotation','Syncpending/waiteratomicsequence/notifyargumentsandmemorymutations','Whole8KiBfixture/SP/R4-R11/caller32byteguard'],'selected':False,'limits':['Heap/log/independence/defaultdisplay/syncensure/critical/notifybackendscontrolled','OOMstoppedatloggerentry;fatalstore notexecuted','Syntheticalias/dimensionboundaryfixtures arenothardwareconfigproof','No completeimage/layout/byteidentity/hardwareclaim']};(D/'probe-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
finally:
 p.terminate();p.communicate(timeout=5)
