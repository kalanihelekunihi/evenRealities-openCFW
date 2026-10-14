#!/usr/bin/env python3
"""Observe unchanged cold boot on diagnosticM0 board, no CASE peripheralclaims."""
from pathlib import Path
import socket,subprocess,tempfile,time,json,hashlib,re,xml.etree.ElementTree as ET
R=Path(__file__).resolve().parents[4];H=Path(__file__).resolve().parent;P=H.parent/'case-wave039-list-cursor-contract';EXE='/opt/homebrew/bin/qemu-system-arm';F=R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin';payload=H/'reference-payload.bin';payload.write_bytes(F.read_bytes()[32:]);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
text=(H.parent/'case-wave048-qemu-controller-context/controller.py').read_text();a=text.index('class RSP:');b=text.index('results=[]',a);exec(text[a:b],globals());results=[]
for native in [True,False]:
 label='native' if native else 'source';image=payload if native else P/'final/case.elf'
 with tempfile.TemporaryDirectory(prefix='case-coldboot-',dir='/tmp') as t:
  path=Path(t)/'gdb.sock';cmd=[EXE,'-machine','microbit','-global','nrf51-soc.flash-size=134479872','-S','-display','none','-monitor','none','-serial','none','-nodefaults','-kernel',str(image),'-gdb',f'unix:{path},server=on,wait=off']
  if native:cmd+=['-device',f'loader,file={payload},addr=0x08000000,force-raw=on']
  else:cmd+=['-device',f'loader,file={H.parent/"case-wave050-qemu-m0-controller-context/source-vectors.bin"},addr=0x0,force-raw=on']
  p=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE);row={'label':label,'command':cmd}
  try:
   deadline=time.monotonic()+3
   while not path.exists() and time.monotonic()<deadline:
    if p.poll() is not None:raise RuntimeError('QEMU exited')
    time.sleep(.01)
   g=RSP(str(path));g.cmd('qSupported');g.cmd('?');target=g.xml('target.xml');regs={};next_num=0
   for name in re.findall(r'href="([^"]+)"',target):
    for reg in ET.fromstring(g.xml(name)).iter('reg'):
     n=int(reg.attrib['regnum']) if 'regnum' in reg.attrib else next_num;regs[reg.attrib['name']]=n;next_num=n+1
   def get(name):return int.from_bytes(bytes.fromhex(g.cmd(f'p{regs[name]:x}')),'little')
   row['reset']={k:hex(get(k)) for k in ['pc','sp','xpsr']}
   observations=[]
   for _ in range(3):
    g.s.sendall(b'$c#63');time.sleep(.1);g.s.sendall(b'\x03');reply=g.recv();observations.append({'reply':reply,'registers':{k:hex(get(k)) for k in ['pc','sp','xpsr','r0','r1','r2','r3']},'RCC_40021000':g.cmd('m40021000,4'),'RCC_40021008':g.cmd('m40021008,4'),'tick_20000120':g.cmd('m20000120,4')})
   row['observations']=observations;row['status']='DIAGNOSTIC_COLD_BOOT_OBSERVED';g.close()
  except (OSError,RuntimeError,AssertionError,ValueError,KeyError,ET.ParseError) as e:row['status']='DIAGNOSTIC_UNAVAILABLE';row['error']=str(e)
  finally:
   p.terminate()
   try:p.wait(timeout=3)
   except subprocess.TimeoutExpired:p.kill();p.wait(timeout=3)
   row['stderr']=p.stderr.read().decode()
  results.append(row)
r={'status':'COLD_BOOT_PERIPHERAL_FRONTIER_OBSERVED','QEMU_sha256':sha(Path(EXE)),'source_ELF_sha256':sha(P/'final/case.elf'),'results':results,'limits':['DiagnosticNRF51/microbit board has no STM32G0 RCC/FLASH/PWR/ADC/UART/YHM2510 model; no fabricated readybits orfactoryvalues supplied','Coldboot observations on wrong peripheralboard are not firmware failure orCASE acceptance','Localdebug/CASEUSB unavailable in recordedaccesscheck; chipmodel orhardwaretrace is required for these peripheralgates']};(H/'verification.json').write_text(json.dumps(r,indent=2)+'\n');print([(x['label'],x['status'],[y['registers']['pc'] for y in x.get('observations',[])]) for x in results])
