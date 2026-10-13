from pathlib import Path
from elftools.elf.elffile import ELFFile
import subprocess,socket,time,xml.etree.ElementTree as ET,struct,json,hashlib
R=Path('/Users/kalani/Repo/evenRealities-openCFW/g2');B=R/'analysis/c-source-completion-20261011/peripherals';D=B/'root-nema-rotated-arc-trace-round308';D.mkdir(exist_ok=True);source=B/'root-nema-full-postprocessor-draft-round306/candidate-unadmitted.c';s=source.read_text();(D/'candidate-diagnostic-only.c').write_text(s)
build=(B/'root-nema-nonfinite-qualification-round309/probe_nonfinite.py').read_text();build=build.replace("D=R/'analysis/c-source-completion-20261011/peripherals/root-nema-full-postprocessor-draft-round306'","D=R/'analysis/c-source-completion-20261011/peripherals/root-nema-rotated-arc-trace-round308'").replace("D/'candidate-unadmitted.c'","D/'candidate-diagnostic-only.c'").replace('mutation=0;mutation<13','mutation=6;mutation<7').replace('slot=0;slot<8','slot=3;slot<4').replace('relative=0;relative<2','relative=0;relative<1').replace('arc=0;arc<4','arc=0;arc<1').replace('guard=0;guard<3','guard=0;guard<1').replace('round=0;round<4','round=1;round<2').replace('extra=0;extra<2','extra=0;extra<1').replace('k=0;k<12','k=9;k<10');build=build[:build.index("r=subprocess.run(['qemu-system-arm'")];(D/'build-diagnostic.py').write_text(build);subprocess.run(['/tmp/g2-peripherals-venv/bin/python',str(D/'build-diagnostic.py')],check=True,stdout=subprocess.DEVNULL)
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
 address=source_entry
 assert command('Z1,'+hex(address)[2:]+',2')=='OK'
 stop=command('c');assert command('z1,'+hex(address)[2:]+',2')=='OK'
 history=[]
 for step in range(6000):
  pc=int.from_bytes(reg('pc'),'little');fp=int.from_bytes(reg('fpscr'),'little')
  history.append({'pc':hex(pc),'fpscr':hex(fp)})
  if fp&4:
   receipt={'status':'FIRST_CANDIDATE_UNDERFLOW','history':history[-12:],'sregisters':{str(i):hex(sreg(i)) for i in range(32)},'candidate_entry':hex(source_entry),'steps':step,'production_selected':False}
   (B/'root-nema-nonfinite-qualification-round309/polygon-overflow-trace.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2));break
  command('s')
 else:raise RuntimeError('No underflow within step bound')

finally:
 p.terminate();p.communicate(timeout=5)
