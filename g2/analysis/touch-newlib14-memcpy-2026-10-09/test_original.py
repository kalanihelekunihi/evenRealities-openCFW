from pathlib import Path
import itertools,json,hashlib
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE,UC_MEM_READ
from unicorn.arm_const import *
O=Path(__file__).resolve().parent;R=O.parents[2];p=R/'g2/blobs/official/g2-2.2.6.10/firmware_touch.bin';b=p.read_bytes();assert hashlib.sha256(b).hexdigest()=='0d13d8bb1337bf22989dc16143e3d5eca29a31cc1ed753ff624668750ea9470d';rows=[]
for sa,da,n in itertools.product(range(4),range(4),[0,1,2,3,4,15,16,128]):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x20000);u.mem_write(0x3300,b[32:]);u.mem_map(0x20000000,0x2000);src=0x20001000+sa;dst=0x20001200+da;data=bytes((i*17+7)&255 for i in range(256));u.mem_write(0x20001000,data);u.mem_write(0x20001200,b'\xee'*256);u.reg_write(UC_ARM_REG_R0,dst);u.reg_write(UC_ARM_REG_R1,src);u.reg_write(UC_ARM_REG_R2,n);u.reg_write(UC_ARM_REG_R4,0x12345678);u.reg_write(UC_ARM_REG_SP,0x20001ff0);u.reg_write(UC_ARM_REG_LR,0x2001);reads=[];writes=[];done=[]
 def code(uc,pc,size,_):
  if pc==0x2000:done.append(True);uc.emu_stop()
 def mem(uc,access,a,size,value,_):
  if 0x20001000<=a<0x20001100 and access==UC_MEM_READ:reads.append([a,size])
  if 0x20001200<=a<0x20001300 and access!=UC_MEM_READ:writes.append([a,size])
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_READ|UC_HOOK_MEM_WRITE,mem);u.emu_start(0xaa2d,0,count=2000);assert done
 expected=b'\xee'*da+data[sa:sa+n]+b'\xee'*(256-da-n);assert bytes(u.mem_read(0x20001200,256))==expected;assert u.reg_read(UC_ARM_REG_R0)==dst and u.reg_read(UC_ARM_REG_R4)==0x12345678 and u.reg_read(UC_ARM_REG_SP)==0x20001ff0;assert reads==[[src+i,1] for i in range(n)] and writes==[[dst+i,1] for i in range(n)]
 rows.append({'source_alignment':sa,'destination_alignment':da,'length':n,'return_pointer':hex(dst),'byte_reads':len(reads),'byte_writes':len(writes),'guards_and_saved_register_match':True})
(O/'original-results.json').write_text(json.dumps({'status':'PASS','cases':len(rows),'stock_sha256':hashlib.sha256(b).hexdigest(),'results':rows,'limits':'Original instructions over non-overlapping synthetic RAM buffers; source/destination validity supplied, no overlap contract, MMIO/device behavior or concurrency inferred.'},indent=2)+'\n');print('memcpy original cases PASS',len(rows))
