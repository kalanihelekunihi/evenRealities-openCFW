#!/usr/bin/env python3
"""Existing QEMU CortexM3 diagnostic loader/RSP inspection, no target acceptance."""
from pathlib import Path
import subprocess,socket,json,tempfile,time,hashlib
R=Path(__file__).resolve().parents[4];H=Path(__file__).resolve().parent;EXE='/opt/homebrew/bin/qemu-system-arm';F=R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin';payload=H/'reference-payload.bin';payload.write_bytes(F.read_bytes()[32:]);results=[]
class RSP:
 def __init__(self,path):self.s=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM);self.s.settimeout(5);self.s.connect(path)
 def recv(self):
  while True:
   c=self.s.recv(1)
   if c==b'$':break
   if not c:raise RuntimeError('RSP closed')
  data=b''
  while True:
   c=self.s.recv(1)
   if c==b'#':break
   data+=c
  checksum=self.s.recv(2);assert int(checksum,16)==sum(data)%256;self.s.sendall(b'+');return data.decode()
 def cmd(self,cmd):
  b=cmd.encode();self.s.sendall(b'$'+b+b'#'+f'{sum(b)%256:02x}'.encode());return self.recv()
 def close(self):self.s.close()
for image,label in [(payload,'native'),(R/'g2/analysis/component-goal-20261013/case-wave039-list-cursor-contract/final/case.elf','source')]:
 with tempfile.TemporaryDirectory(prefix='case-qemu-',dir='/tmp') as t:
  path=Path(t)/'gdb.sock';cmd=[EXE,'-machine','netduino2','-S','-display','none','-monitor','none','-serial','none','-nodefaults','-kernel',str(image),'-gdb',f'unix:{path},server=on,wait=off'];p=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
  result={'label':label,'command':cmd}
  try:
   deadline=time.monotonic()+3
   while not path.exists() and time.monotonic()<deadline:
    if p.poll() is not None:raise RuntimeError('QEMU loader exited')
    time.sleep(.01)
   rsp=RSP(str(path));result['supported']=rsp.cmd('qSupported');result['stop']=rsp.cmd('?');result['target_xml']=rsp.cmd('qXfer:features:read:target.xml:0,fff');result['registers']=rsp.cmd('g');result['vectors']=rsp.cmd('m8000000,b8');result['status']='REFERENCE_M3_LOADER_RSP_AVAILABLE';rsp.close()
  except (OSError,RuntimeError,AssertionError) as e:result['status']='UNAVAILABLE';result['error']=str(e)
  finally:
   p.terminate()
   try:p.wait(timeout=3)
   except subprocess.TimeoutExpired:p.kill();p.wait(timeout=3)
   result['stderr']=p.stderr.read().decode()
  results.append(result)
r={'status':'QEMU_REFERENCE_M3_RSP_CAPABILITY_PROBE','QEMU_sha256':hashlib.sha256(Path(EXE).read_bytes()).hexdigest(),'payload_sha256':hashlib.sha256(payload.read_bytes()).hexdigest(),'results':results,'limits':['Netduino2 is actuallyCortexM3, not CASE/M0 target; diagnosticcommonThumb/controller testing only','Images loaded unchanged while CPU suspended; no boot/chipperipheral execution, physicaldevice or flashing','Nativepayload is a referenceoracle only, never source replacement']};(H/'verification.json').write_text(json.dumps(r,indent=2)+'\n');print([(x['label'],x['status'],x.get('target_xml','')[:300]) for x in results])
