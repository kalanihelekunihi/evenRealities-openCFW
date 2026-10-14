#!/usr/bin/env python3
"""Actual NVIC entry/return diagnostic on explicit CortexM3 reference board."""
from pathlib import Path
import socket,subprocess,tempfile,time,json,hashlib,re,xml.etree.ElementTree as ET,struct
R=Path(__file__).resolve().parents[4];H=Path(__file__).resolve().parent;EXE='/opt/homebrew/bin/qemu-system-arm';P=H.parent/'case-wave039-list-cursor-contract';F=R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin';payload=H/'reference-payload.bin';payload.write_bytes(F.read_bytes()[32:]);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
class RSP:
 def __init__(self,path):self.s=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM);self.s.settimeout(10);self.s.connect(path)
 def exact(self,n):
  b=b''
  while len(b)<n:
   x=self.s.recv(n-len(b))
   if not x:raise RuntimeError('RSP closed')
   b+=x
  return b
 def recv(self):
  while self.exact(1)!=b'$':pass
  raw=b''
  while True:
   c=self.exact(1)
   if c==b'#':break
   raw+=c
  check=self.exact(2);assert int(check,16)==sum(raw)%256;self.s.sendall(b'+');out=bytearray();i=0
  while i<len(raw):
   c=raw[i]
   if c==125:i+=1;out.append(raw[i]^32)
   elif c==42:i+=1;out.extend(bytes([out[-1]])*(raw[i]-29))
   else:out.append(c)
   i+=1
  return out.decode()
 def cmd(self,cmd):
  b=cmd.encode();self.s.sendall(b'$'+b+b'#'+f'{sum(b)%256:02x}'.encode())
  while True:
   r=self.recv()
   if not (r.startswith('O') and r!='OK'):return r
 def xml(self,name):
  s=''
  while True:
   r=self.cmd(f'qXfer:features:read:{name}:{len(s):x},fff');assert r[0] in 'lm';s+=r[1:]
   if r[0]=='l':return s
 def close(self):self.s.close()
results=[]
for scenario in ['same_priority','higher_priority','suspended','fallback_priority','only_current']:
 pair=[]
 for native in [True,False]:
  label='native' if native else 'source';meta=json.loads((H/(label+'-'+scenario+'.input.json')).read_text());image=payload if native else P/'final/case.elf'
  with tempfile.TemporaryDirectory(prefix='case-controller-',dir='/tmp') as t:
   path=Path(t)/'gdb.sock';cmd=[EXE,'-machine','netduino2','-S','-display','none','-monitor','none','-serial','none','-nodefaults','-kernel',str(image),'-gdb',f'unix:{path},server=on,wait=off'];p=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE);row={'label':label,'scenario':scenario,'command':cmd}
   try:
    deadline=time.monotonic()+3
    while not path.exists() and time.monotonic()<deadline:
     if p.poll() is not None:raise RuntimeError('QEMU exited')
     time.sleep(.01)
    g=RSP(str(path));g.cmd('qSupported');g.cmd('?');target=g.xml('target.xml');regs={};next_num=0;features={}
    for name in re.findall(r'href="([^"]+)"',target):
     text=g.xml(name);features[name]=text
     for reg in ET.fromstring(text).iter('reg'):
      n=int(reg.attrib['regnum']) if 'regnum' in reg.attrib else next_num;regs[reg.attrib['name']]={'num':n,'bits':int(reg.attrib['bitsize'])};next_num=n+1
    (H/'gdb-features.json').write_text(json.dumps({'features':features,'registers':regs},indent=2)+'\n')
    def put(name,value):
     item=regs[name];valuebytes=value.to_bytes(item['bits']//8,'little');r=g.cmd(f"P{item['num']:x}="+valuebytes.hex());assert r=='OK',(name,r)
    def get(name):
     r=g.cmd(f"p{regs[name]['num']:x}");assert not r.startswith('E'),(name,r);return int.from_bytes(bytes.fromhex(r),'little')
    def mem(address,data):
     for offset in range(0,len(data),1024):
      chunk=data[offset:offset+1024];assert g.cmd(f'M{address+offset:x},{len(chunk):x}:'+chunk.hex())=='OK'
    def read(address,count):
     r=g.cmd(f'm{address:x},{count:x}');assert not r.startswith('E'),r;return bytes.fromhex(r)
    def bp(address,add=True):assert g.cmd(f'{"Z" if add else "z"}0,{address:x},2')=='OK'
    def run_to(address):
     bp(address);reply=g.cmd('c');pc=get('pc');assert pc==address,(reply,hex(pc),hex(address));bp(address,False);return reply
    mem(0x20000000,Path(meta['ram_file']).read_bytes());put('xpsr',0x01000000);put('sp',meta['MSP']);put('pc',meta['first_handoff']);put('lr',0x2000f001)
    run_to(meta['thread_entry']);row['initial_thread']={k:get(k) for k in ['pc','sp','xpsr','control','msp','psp']};assert get('sp')==meta['tops'][0] and get('control')&2
    for i,value in enumerate(meta['input_registers']):put('r'+str(i+4),value)
    # Hardware pending interrupt through real NVIC MMIO, not forcedIPSR/handlerPC.
    bp(meta['pendsv_entry']);mem(0xe000ed04,struct.pack('<I',0x10000000));reply=g.cmd('c');assert get('pc')==meta['pendsv_entry'];assert get('xpsr')&0x1ff==14;bp(meta['pendsv_entry'],False);row['hardware_entry']={k:get(k) for k in ['pc','sp','xpsr','control','msp','psp']}
    run_to(meta['exception_return_instruction']);row['pre_return']={k:get(k) for k in ['pc','sp','xpsr','control','msp','psp','r3']};assert get('r3')==0xfffffffd
    current=struct.unpack('<I',read(0x20000128,4))[0];assert current==meta['expected_new'];row['current_TCB']=hex(current)
    run_to(meta['thread_entry']);row['returned_thread']={k:get(k) for k in ['pc','sp','xpsr','control','msp','psp','r0','lr']};assert get('xpsr')&0x1ff==0 and get('control')&2;selected=0 if current==meta['tasks'][0] else 1;assert get('sp')==meta['tops'][selected]
    actual=[get('r'+str(i)) for i in range(4,12)];expected=meta['input_registers'] if selected==0 else [0xa5a5a5a5]*8;assert actual==expected;assert get('r0')==0x11110000+selected;assert get('lr')==meta['task_return'];row['restored_registers']=actual;row['status']='PASS_ACTUAL_REFERENCE_M3_NVIC_ENTRY_RETURN'
    g.close()
   except (OSError,RuntimeError,AssertionError,ValueError,KeyError,ET.ParseError) as error:row['status']='DIAGNOSTIC_FAILURE';row['error']=str(error)
   finally:
    p.terminate()
    try:p.wait(timeout=3)
    except subprocess.TimeoutExpired:p.kill();p.wait(timeout=3)
    row['stderr']=p.stderr.read().decode()
   pair.append(row)
  if row['status']!='PASS_ACTUAL_REFERENCE_M3_NVIC_ENTRY_RETURN':break
 results.append({'scenario':scenario,'pair':pair})
 if len(pair)!=2 or any(x['status']!='PASS_ACTUAL_REFERENCE_M3_NVIC_ENTRY_RETURN' for x in pair):break
r={'status':'QEMU_REFERENCE_M3_CONTROLLER_CONTEXT_DIAGNOSTIC','QEMU_sha256':sha(Path(EXE)),'source_ELF_sha256':sha(P/'final/case.elf'),'native_payload_sha256':sha(payload),'results':results,'limits':['Explicit CortexM3/netduino2 reference, not physical CASE CortexM0+ target validation','Unchanged native/source images; data setup from genuine qualified providers; actual NVIC entry and EXC_RETURN with debugger observation only','No CASE peripherals, clock, external flash or firmware package/acceptance promotion']};(H/'controller-verification.json').write_text(json.dumps(r,indent=2)+'\n');print([(x['scenario'],[(y['label'],y['status'],y.get('error')) for y in x['pair']]) for x in results])
