from pathlib import Path
import sys,json,struct,itertools,hashlib
from unicorn import UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
D=Path(__file__).resolve().parent;s=D.parent/'touch-slider-producer-closure-2026-10-08/verify.py';ns={'__file__':str(s)};exec(s.read_text().split('patterns=')[0],ns)
def guest(divider=24,clock=2,chop=1,large=False):
 u=ns['guest']();u.mem_map(0x40000000,0x4000);u.mem_write(0x20002000,struct.pack('<4I',0x20003000,0,0x20003500,0x20004000));u.mem_write(0x20003000,struct.pack('<3I',24000000,0,0x20003100));u.mem_write(0x20003100,struct.pack('<I',0x40000000));u.mem_write(0x20004000,struct.pack('<I',0x20005000));u.mem_write(0x20004000+132,bytes([chop]));u.mem_write(0x20005000+14,struct.pack('<H',divider));u.mem_write(0x20005000+33,bytes([clock]));u.mem_write(0x20005000+44,struct.pack('<H',65535 if large else 16));i=bytearray(128)
 for off,val in [(48,20),(50,30),(62,96),(64,2),(66,100),(68,4)]:struct.pack_into('<H',i,off,65535 if large else val)
 i[77]=255 if large else 8;i[83]=255 if large else 3;u.mem_write(0x20003500,bytes(i));return u
counts={'watchdog':0,'wait':0}
for divider,clock,chop,large in itertools.product([0,1,3,4,24,65535],range(4),[0,1,255],[False,True]):
 vals=[]
 for native in [False,True]:
  u=guest(divider,clock,chop,large);vals.append(ns['call'](u,ns['symbols']['touch_scan_watchdog'] if native else 0x7288,[0,999,0x20002000]))
 assert vals[0]==vals[1],(divider,clock,chop,large,vals);counts['watchdog']+=1
for watchdog,hz,done_after in itertools.product([0,1,5,10,100],[0,999999,1000000,24000000],[0,1,2,5,1000]):
 vals=[]
 for native in [False,True]:
  u=guest();u.mem_write(0x20003000,struct.pack('<I',hz));state={'reads':0,'writes':[],'cleared':False}
  def read(u,access,a,n,v,user):
   if a==0x40000100:
    u.mem_write(a,struct.pack('<I',0 if state['cleared'] else 0x100 if state['reads']>=done_after else 0));state['reads']+=1
  def write(u,access,a,n,v,user):
   if a==0x40000100:state['writes'].append(v);state['cleared']=True
  u.hook_add(UC_HOOK_MEM_READ,read);u.hook_add(UC_HOOK_MEM_WRITE,write);r=ns['call'](u,ns['symbols']['touch_scan_wait'] if native else 0x6980,[watchdog,0x20002000]);vals.append((r,state))
 assert vals[0]==vals[1],(watchdog,hz,done_after,vals);counts['wait']+=1
(D/'results.json').write_text(json.dumps({'status':'PASS','cases':counts,'elf_sha256':hashlib.sha256(Path(sys.argv[1]).read_bytes()).hexdigest(),'limits':['Synthetic context and MMIO completion-read sequence; no physical time or ADC acquisition.','Original division/multiplication code executes; no call-entry stubs.','Write-to-clear semantics modeled for interrupt register, not full peripheral emulator.']},indent=2)+'\n');print('PASS',counts)
