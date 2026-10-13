from pathlib import Path
from elftools.elf.elffile import ELFFile
import subprocess,socket,time,xml.etree.ElementTree as ET,struct,json,hashlib
R=Path('/Users/kalani/Repo/evenRealities-openCFW/g2');B=R/'analysis/c-source-completion-20261011/peripherals';D=B/'root-nema-rotated-arc-trace-round308';D.mkdir(exist_ok=True);source=R/'components/audio/uart_thread_source_candidate/display_lv_init_children.c';s=source.read_text();(D/'candidate-diagnostic-only.c').write_text(s)
build=(B/'root-nema-source-admission-round317/probe_selected.py').read_text();build=build.replace("D=R/'analysis/c-source-completion-20261011/peripherals/root-nema-full-postprocessor-draft-round306'","D=R/'analysis/c-source-completion-20261011/peripherals/root-nema-rotated-arc-trace-round308'").replace("D/'candidate-unadmitted.c'","D/'candidate-diagnostic-only.c'").replace('mutation=0;mutation<13','mutation=5;mutation<6').replace('slot=0;slot<8','slot=1;slot<2').replace('relative=0;relative<2','relative=0;relative<1').replace('arc=0;arc<4','arc=0;arc<1').replace('guard=0;guard<3','guard=0;guard<1').replace('round=0;round<4','round=0;round<1').replace('extra=0;extra<2','extra=0;extra<1').replace('k=0;k<12','k=0;k<12');build=build[:build.index("r=subprocess.run(['qemu-system-arm'")];(D/'build-diagnostic.py').write_text(build);subprocess.run(['/tmp/g2-peripherals-venv/bin/python',str(D/'build-diagnostic.py')],check=True,stdout=subprocess.DEVNULL)
reserve=socket.socket();reserve.bind(('127.0.0.1',0));port=reserve.getsockname()[1];reserve.close();p=subprocess.Popen(['qemu-system-arm','-M','mps3-an547','-cpu','cortex-m55','-display','none','-monitor','none','-serial','none','-semihosting-config','enable=on,target=native','-kernel',str(D/'probe/test.elf'),'-S','-gdb','tcp:127.0.0.1:'+str(port)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
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
 with (D/'probe/test.elf').open('rb') as ef:
  ee=ELFFile(ef);source_entry=next(v['st_value'] for v in ee.get_section_by_name('.symtab').iter_symbols() if v.name=='audio_uart_nema_vg_path_process_561c68')&~1
 entries=[0x561c68+(0x28100000-0x438000),source_entry]
 traces=[]
 import re
 listing=subprocess.check_output(['arm-none-eabi-objdump','-D','-M','force-thumb',str(D/'probe/test.elf')],text=True)
 instructions={}
 for line in listing.splitlines():
  match=re.match(r'\s*([0-9a-f]+):\s+(?:[0-9a-f]{4,8}\s+)+([a-z][a-z0-9.]*)\s+(.*)',line)
  if match:instructions[int(match[1],16)]=(match[2],match[3].split('@')[0].strip())
 def register_value(name):
  name={'sl':'r10','fp':'r11','ip':'r12','sb':'r9'}.get(name,name)
  return int.from_bytes(reg(name),'little')
 def access(pc):
  mnemonic,operands=instructions[pc]
  match=re.search(r'\[([^]]+)\]',operands)
  if not match:raise RuntimeError('Undecoded memory instruction '+hex(pc)+' '+mnemonic+' '+operands)
  pieces=[x.strip() for x in match[1].split(',')];address=register_value(pieces[0])
  if len(pieces)>1:
   x=pieces[1];offset=int(x[1:],0) if x.startswith('#') else register_value(x)
   if len(pieces)>2:offset<<=int(pieces[2].split('#')[1],0)
   address=(address+offset)&0xffffffff
  width=1 if mnemonic.startswith('ldrb') else (2 if mnemonic.startswith('ldrh') else (8 if mnemonic.startswith('ldrd') else 4))
  return address,width,mnemonic,operands
 for case in range(44):
  pair=[]
  for entry in entries:
   assert command('Z1,'+hex(entry)[2:]+',2')=='OK';stop=command('c');assert command('z1,'+hex(entry)[2:]+',2')=='OK'
   end=int.from_bytes(reg('lr'),'little')&~1
   assert command('Z1,'+hex(end)[2:]+',2')=='OK'
   assert command('Z4,20010000,2080')=='OK'
   events=[]
   for count in range(600):
    stop=command('c')
    if 'awatch:' not in stop:break
    address=int(stop.split('awatch:')[1].split(';')[0],16)
    pc_int=int.from_bytes(reg('pc'),'little');address,width,mnemonic,operands=access(pc_int);pc=hex(pc_int);assert command('z4,20010000,2080')=='OK';command('s');events.append({'address':hex(address),'pc':pc,'path':command('m'+hex(address)[2:]+','+hex(width)[2:]),'width':width,'access':'write' if mnemonic.startswith(('str','vstr','stm','vstm')) else 'read','instruction':mnemonic+' '+operands});assert command('Z4,20010000,2080')=='OK'
   else:raise RuntimeError('Watchpoint event bound')
   assert command('z4,20010000,2080')=='OK';assert command('z1,'+hex(end)[2:]+',2')=='OK'
   pair.append(events)
  native,candidate=pair
  comparable=lambda events:[{'address':v['address'],'path':v['path'],'width':v['width'],'access':v['access']} for v in events]
  traces.append({'case':case,'native':native,'candidate':candidate,'match':comparable(native)==comparable(candidate)})
  print('CASE',case,'EVENTS',len(native),len(candidate),'MATCH',traces[-1]['match'],flush=True)
 receipt={'status':'BOUNDED_EXTERNAL_INPUT_READ_WATCHPOINT_TRACE','traces':traces,'selected':False,'scope':'GDB QEMU write watchpoints; segment+coordinate input range4128bytes, twelve directed fixtures, roundnearest/defaultcontrols; addresses and post-stop snapshot compared, access-width/multiple-store semantics not yet qualified'}
 (B/'root-nema-source-admission-round317/selected-joint-access.json').write_text(json.dumps(receipt,indent=2)+'\n')

finally:
 p.terminate();p.communicate(timeout=5)
