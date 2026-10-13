from pathlib import Path
from elftools.elf.elffile import ELFFile
import subprocess,socket,time,xml.etree.ElementTree as ET,struct,json,hashlib
R=Path('/Users/kalani/Repo/evenRealities-openCFW/g2');B=R/'analysis/c-source-completion-20261011/peripherals';D=B/'root-nema-rotated-arc-trace-round308';D.mkdir(exist_ok=True);source=B/'root-nema-full-postprocessor-draft-round306/candidate-unadmitted.c';s=source.read_text();(D/'candidate-diagnostic-only.c').write_text(s)
build=(B/'root-nema-degenerate-qualification-round311/probe_degenerate.py').read_text();build=build.replace("D=R/'analysis/c-source-completion-20261011/peripherals/root-nema-full-postprocessor-draft-round306'","D=R/'analysis/c-source-completion-20261011/peripherals/root-nema-rotated-arc-trace-round308'").replace("D/'candidate-unadmitted.c'","D/'candidate-diagnostic-only.c'").replace('mutation=0;mutation<13','mutation=5;mutation<6').replace('slot=0;slot<8','slot=1;slot<2').replace('relative=0;relative<2','relative=0;relative<1').replace('arc=0;arc<4','arc=0;arc<1').replace('guard=0;guard<3','guard=0;guard<1').replace('round=0;round<4','round=0;round<1').replace('extra=0;extra<2','extra=0;extra<1').replace('k=0;k<12','k=0;k<12');build=build[:build.index("r=subprocess.run(['qemu-system-arm'")];(D/'build-diagnostic.py').write_text(build);subprocess.run(['/tmp/g2-peripherals-venv/bin/python',str(D/'build-diagnostic.py')],check=True,stdout=subprocess.DEVNULL)
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
 import re
 listing=subprocess.check_output(['arm-none-eabi-objdump','-D','-b','binary','-m','arm','-M','force-thumb','--adjust-vma=0x438000','--start-address=0x561c68','--stop-address=0x563954','/tmp/opencfw-main-native.bin'],text=True)
 branches={}
 for line in listing.splitlines():
  m=re.match(r'\s*([0-9a-f]+):\s+((?:[0-9a-f]{4}\s+)+)(b(?:eq|ne|cs|cc|mi|pl|vs|vc|hi|ls|ge|lt|gt|le)(?:\.[nw])?|cbz|cbnz)\s+(.*)',line)
  if m:branches[int(m[1],16)]={'instruction':m[3]+' '+m[4],'size':len(m[2].split())*2,'successors':{},'observations':0}
 for address,name in [(0x562a48,'native WLS'),(0x562b36,'native LE')]:branches[address]={'instruction':name,'size':4,'successors':{},'observations':0}
 delta=0x28100000-0x438000
 for address in branches:assert command('Z1,'+hex(address+delta)[2:]+',2')=='OK'
 entry=0x561c68+delta
 for case in range(768):
  assert command('Z1,'+hex(entry)[2:]+',2')=='OK';command('c');assert command('z1,'+hex(entry)[2:]+',2')=='OK'
  end=int.from_bytes(reg('lr'),'little')&~1;assert command('Z1,'+hex(end)[2:]+',2')=='OK'
  for count in range(500):
   stop=command('c');pc=int.from_bytes(reg('pc'),'little')
   if pc==end:break
   address=pc-delta
   if address not in branches:raise RuntimeError('Unexpected stop '+hex(pc)+' '+stop)
   assert command('z1,'+hex(pc)[2:]+',2')=='OK';command('s');successor=int.from_bytes(reg('pc'),'little')-delta;assert command('Z1,'+hex(pc)[2:]+',2')=='OK'
   row=branches[address];key=hex(successor);row['successors'][key]=row['successors'].get(key,0)+1;row['observations']+=1
  else:raise RuntimeError('Branch event bound')
  assert command('z1,'+hex(end)[2:]+',2')=='OK';print('CASE',case,'BRANCH_EVENTS',count,flush=True)
 result={'status':'DIRECTED_NATIVE_BRANCH_CANDIDATE_COVERAGE','branches':{hex(k):v for k,v in branches.items()},'branch_candidates':len(branches),'visited':sum(bool(v['observations']) for v in branches.values()),'both_successors_observed':sum(len(v['successors'])>=2 for v in branches.values()),'scope':'768 deterministic degenerate/varied fixtures, defaultcontrols; disassembly-derived branch candidates include possible literal-pool decoding artifacts pending classification; no whole-function coverage claim','candidate_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'production_selected':False}
 (B/'root-nema-branch-outcomes-round316/branch-coverage-degenerate.json').write_text(json.dumps(result,indent=2)+'\n');print({k:v for k,v in result.items() if k!='branches'})

finally:
 p.terminate();p.communicate(timeout=5)
