#!/usr/bin/env python3
"""Read-only suspended QEMU controller/CPU property inspection."""
from pathlib import Path
import subprocess,json,selectors,time,hashlib
H=Path(__file__).resolve().parent;EXE='/opt/homebrew/bin/qemu-system-arm';results=[]
for machine,extra in [('microbit',[]),('netduino2',[]),('netduino2',['-global','armv7m.cpu-type=cortex-m0']),('stm32vldiscovery',['-global','armv7m.cpu-type=cortex-m0'])]:
 cmd=[EXE,'-machine',machine,'-S','-display','none','-monitor','none','-serial','none','-nodefaults','-qmp','stdio',*extra];p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,bufsize=1);sel=selectors.DefaultSelector();sel.register(p.stdout,selectors.EVENT_READ)
 def receive():
  if not sel.select(3):raise TimeoutError('QMP response timeout')
  line=p.stdout.readline()
  if not line:raise RuntimeError('QEMU exited before QMP response')
  return json.loads(line)
 def request(name,arguments=None):
  p.stdin.write(json.dumps({'execute':name,**({'arguments':arguments} if arguments else {})})+'\n');p.stdin.flush()
  while True:
   r=receive()
   if 'event' not in r:return r
 result={'machine':machine,'command':cmd}
 try:
  result['greeting']=receive();result['capabilities']=request('qmp_capabilities');found=[]
  def inspect(path,depth=0):
   r=request('qom-list',{'path':path})
   if 'return' not in r:return
   props=r['return'];names={x['name'] for x in props}
   for name in ['cpu-type','sram-size','flash-size']:
    if name in names:found.append({'path':path,'property':name,'value':request('qom-get',{'path':path,'property':name})})
   for x in props:
    typ=x['type']
    if typ.startswith('child<') and depth<4 and any(t in (x['name']+' '+typ).lower() for t in ['soc','arm','cpu','nrf','stm32']):
     child=path+'/'+x['name'];found.append({'path':child,'type':typ});inspect(child,depth+1)
  inspect('/machine');result['properties']=found;result['status']='SUSPENDED_QMP_READ_COMPLETE'
 except (TimeoutError,RuntimeError,json.JSONDecodeError) as e:result['status']='UNAVAILABLE';result['error']=str(e)
 finally:
  p.terminate()
  try:p.wait(timeout=3)
  except subprocess.TimeoutExpired:p.kill();p.wait(timeout=3)
  result['stderr']=p.stderr.read();sel.close()
 results.append(result)
r={'status':'CONTROLLER_CAPABILITY_PROBE_COMPLETE','QEMU_sha256':hashlib.sha256(Path(EXE).read_bytes()).hexdigest(),'results':results,'limits':['Suspended empty machines only; no firmware/image/device access or hardware operation','Different board peripherals are not CASE hardware validation; CPU/memory compatibility must be established before execution']};(H/'verification.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
