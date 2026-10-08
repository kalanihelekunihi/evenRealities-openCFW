"""Execute stock simple-mode body; provider read/program are explicit RAM cuts."""
from pathlib import Path
import hashlib,json,struct,itertools
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC
D=Path(__file__).resolve().parent;ROOT=D.parents[2];fw=(ROOT/'g2/blobs/official/g2-2.2.6.10/firmware_touch.bin').read_bytes();assert hashlib.sha256(fw).hexdigest()=='0d13d8bb1337bf22989dc16143e3d5eca29a31cc1ed753ff624668750ea9470d';im=fw[32:];cases=[]
for addr,n,row,fail in itertools.product([0,1,15,31],[1,8,17,32],[16,32],[-1,0,1]):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x3000,0x9000);u.mem_map(0x20000000,0x10000);u.mem_write(0x3300,im);ctx=0x200008c8;provider=0x20002000;data=0x20003000;flash=0x20004000;handle=0x12345678;readpc=0x20001000;scratch=0x20000cd4
 c=bytearray(32);struct.pack_into('<I',c,4,row);struct.pack_into('<I',c,16,flash);struct.pack_into('<I',c,24,0xfeedface);struct.pack_into('<I',c,28,provider);c[13]=1;u.mem_write(ctx,bytes(c));u.mem_write(provider,struct.pack('<I',handle));u.mem_write(provider+20,struct.pack('<I',readpc|1));old=bytes((i*3)&255 for i in range(256));source=bytes((0xa0+i)&255 for i in range(n));u.mem_write(flash,old);u.mem_write(data,source)
 for r,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],[addr,data,n,ctx]):u.reg_write(r,v)
 u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20000001);calls=[];attempts=0;consumed=0;expected=bytearray(old);last=0xfeedface
 def code(u,pc,size,user):
  global attempts,consumed,last
  if pc==readpc:
   args=[u.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];assert args[0]==handle and args[2:]==[row,scratch];calls.append(['row-read',args]);u.mem_write(scratch,bytes(u.mem_read(args[1],row)));u.reg_write(UC_ARM_REG_R0,0);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  if pc==0x8554:
   args=[u.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2]];assert args[1:]==[scratch,ctx];offset=(addr%row) if attempts==0 else 0;take=min(row-offset,n-consumed);want=bytearray(expected[args[0]-flash:args[0]-flash+row]);want[offset:offset+take]=source[consumed:consumed+take];actual=bytes(u.mem_read(scratch,row));assert actual==bytes(want),(addr,n,row,fail,attempts,actual,want);calls.append(['row-program',args,actual.hex()]);status=3 if attempts==fail else 0
   if not status:u.mem_write(args[0],actual);expected[args[0]-flash:args[0]-flash+row]=actual;last=args[0];consumed+=take
   attempts+=1;u.reg_write(UC_ARM_REG_R0,status);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,code);u.emu_start(0x85d5,0x20000000,count=10000);assert u.reg_read(UC_ARM_REG_PC)==0x20000000;assert bytes(u.mem_read(data,n))==source;assert bytes(u.mem_read(flash,256))==bytes(expected);assert int.from_bytes(u.mem_read(ctx+24,4),'little')==last;assert u.reg_read(UC_ARM_REG_R0)==(3 if 0<=fail<attempts else 0)
 cases.append({'inputs':[addr,n,row,fail],'calls':calls,'return':u.reg_read(UC_ARM_REG_R0),'source_unchanged':True,'last_row':last})
r={'status':'PASS_STOCK_SIMPLE_MODE_WRITE_DIRECTION','cases':len(cases),'stock_body_sha256':hashlib.sha256(im[0x52d4:0x537c]).hexdigest(),'comparisons':cases,'limits':['Actual stock simple-mode/division/memcpy instructions; provider vtable row-read and row-program helper0x8554 are explicit synthetic RAM/status cuts.','Proves direction into row buffer, preserved other row bytes, source unchanged, row progress/error handling under these cuts; no physical programming or persistence.','This suite is original-body behavior evidence, not native source equivalence or exact public-source attribution.']};(D/'simple-direction-results.json').write_text(json.dumps(r,indent=2)+'\n');print('PASS',len(cases),'stock simple-mode direction/copy cases; read/program cuts explicit')
