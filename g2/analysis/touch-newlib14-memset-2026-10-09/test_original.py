from pathlib import Path
import itertools,json,hashlib
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
O=Path(__file__).resolve().parent;R=O.parents[2];p=R/'g2/blobs/official/g2-2.2.6.10/firmware_touch.bin';b=p.read_bytes();assert hashlib.sha256(b).hexdigest()=='0d13d8bb1337bf22989dc16143e3d5eca29a31cc1ed753ff624668750ea9470d';rows=[]
for alignment,n,value in itertools.product(range(4),[0,1,2,3,4,15,16,128],[0,1,0x7f,0x80,0x100,0x12345678,0xffffffff]):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x20000);u.mem_write(0x3300,b[32:]);u.mem_map(0x20000000,0x2000);dst=0x20001000+alignment;u.mem_write(0x20001000,b'\xee'*256);u.reg_write(UC_ARM_REG_R0,dst);u.reg_write(UC_ARM_REG_R1,value);u.reg_write(UC_ARM_REG_R2,n);u.reg_write(UC_ARM_REG_SP,0x20001ff0);u.reg_write(UC_ARM_REG_LR,0x2001);done=[];writes=[]
 def code(uc,pc,size,_):
  if pc==0x2000:done.append(True);uc.emu_stop()
 def mem(uc,access,a,size,v,_):
  if 0x20001000<=a<0x20001100:writes.append([a,size,v&0xff])
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,mem);u.emu_start(0xa9d5,0,count=2000);assert done
 expected=b'\xee'*alignment+bytes([value&0xff])*n+b'\xee'*(256-alignment-n);assert bytes(u.mem_read(0x20001000,256))==expected;assert u.reg_read(UC_ARM_REG_R0)==dst;assert writes==[[dst+i,1,value&0xff] for i in range(n)]
 rows.append({'alignment':alignment,'length':n,'input_value':hex(value),'stored_byte':value&0xff,'writes':len(writes),'guards_and_return_match':True})
(O/'original-results.json').write_text(json.dumps({'status':'PASS','cases':len(rows),'results':rows,'limits':'Original instructions over synthetic writable RAM. Caller validity supplied, no MMIO/device/concurrent mutation or huge-length behavior inferred.'},indent=2)+'\n');print('memset original cases PASS',len(rows))
