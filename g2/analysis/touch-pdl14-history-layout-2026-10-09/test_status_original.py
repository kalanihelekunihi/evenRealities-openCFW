from pathlib import Path
import json,hashlib
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
O=Path(__file__).resolve().parent;R=O.parents[2];p=R/'g2/blobs/official/g2-2.2.6.10/firmware_touch.bin';b=p.read_bytes();assert hashlib.sha256(b).hexdigest()=='0d13d8bb1337bf22989dc16143e3d5eca29a31cc1ed753ff624668750ea9470d'
statuses=list(range(0xf0000000,0xf0000016))+[0xf000ffff,0xffffffff,0xa0000000,0xa0000001,0xafffffff,0,1,0x70000000,0xb0000000,0xefffffff];rows=[]
errors={1:0x520001,3:0x520004,4:0x520004,5:0x520005,7:0,8:0x500008,9:0x500009,17:0x520021,19:0x520021,20:0x520021}
for status in statuses:
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x20000);u.mem_write(0x3300,b[32:]);u.mem_map(0x40100000,0x1000);u.mem_write(0x40100008,status.to_bytes(4,'little'));u.reg_write(UC_ARM_REG_LR,0x2001);done=[];reads=[];writes=[]
 def hook(uc,pc,size,_):
  if pc==0x2000:done.append(True);uc.emu_stop()
 def mem(uc,access,a,size,value,_):
  if 0x40100000<=a<0x40101000:(reads if access==16 else writes).append([hex(a),size])
 u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_READ|UC_HOOK_MEM_WRITE,mem);u.emu_start(0x8bf5,0,count=1000);assert done
 expected=0 if status&0xf0000000==0xa0000000 else errors.get(status-0xf0000000,0x5200ff) if status&0xf0000000==0xf0000000 else 0x500023
 observed=u.reg_read(UC_ARM_REG_R0);assert observed==expected;assert reads==[['0x40100008',4]] and not writes
 rows.append({'status_word':hex(status),'returned_status':hex(observed),'MMIO_reads':reads,'MMIO_writes':writes})
(O/'status-original-results.json').write_text(json.dumps({'cases':len(rows),'status':'PASS','stock_sha256':hashlib.sha256(b).hexdigest(),'results':rows,'limits':'Original pure decoder with synthetic CPUSS status backing; no SROM request, device write, busy/completion timeline or physical flash outcome simulated.'},indent=2)+'\n');print('SROM decoder original cases PASS',len(rows))
