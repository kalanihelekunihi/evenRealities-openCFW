from pathlib import Path
import sys,json,struct,itertools,hashlib
from unicorn import UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
D=Path(__file__).resolve().parent;s=D.parent/'touch-slider-producer-closure-2026-10-08/verify.py';ns={'__file__':str(s)};exec(s.read_text().split('patterns=')[0],ns);rows=[]
for start,mode,pattern,control in itertools.product([False,True],[0,5,6,11,255],[[0]*11,list(range(11)),[0xffffffff]*11],[0,0x12345678]):
 vals=[]
 for native in [False,True]:
  u=ns['guest']();u.mem_map(0x40000000,0x4000);u.mem_write(0x40000000,struct.pack('<I',control));u.mem_write(0x20007000,struct.pack('<11I',*pattern));u.mem_write(0x20002000,struct.pack('<I',0x20003000));u.mem_write(0x20003000+8,struct.pack('<I',0x20003100));u.mem_write(0x20003100,struct.pack('<I',0x40000000));bus=[]
  def read(u,access,a,n,v,user):
   if 0x40000000<=a<0x40004000:bus.append(['read',a-0x40000000,n])
  def write(u,access,a,n,v,user):
   if 0x40000000<=a<0x40004000:bus.append(['write',a-0x40000000,n,v])
  u.hook_add(UC_HOOK_MEM_READ,read);u.hook_add(UC_HOOK_MEM_WRITE,write)
  if start:ns['call'](u,ns['symbols']['touch_start_scan_frame'] if native else 0x6928,[0x20007000,0x20002000])
  else:ns['call'](u,ns['symbols']['touch_load_scan_frame'] if native else 0x9178,[0x40000000,mode,0x20007000])
  vals.append((bus,u.mem_read(0x40000000,0x4000).hex()))
 assert vals[0]==vals[1],(start,mode,pattern,control,vals);rows.append({'start':start,'mode':mode,'frame':pattern,'control':control,'bus':vals[0][0]})
(D/'results.json').write_text(json.dumps({'status':'PASS','cases':len(rows),'comparisons':rows,'elf_sha256':hashlib.sha256(Path(sys.argv[1]).read_bytes()).hexdigest(),'limits':['Synthetic register backing and coherent frame pointers; actual hardware sideeffects not modeled.','MMIO read/write order and values compared; no function call stubs.','Repeated start cases differ in unused mode parameter deliberately.']},indent=2)+'\n');print('PASS',len(rows))
