from pathlib import Path
import sys,json,struct,itertools,hashlib
from unicorn.arm_const import *
D=Path(__file__).resolve().parent;s=D.parent/'touch-slider-producer-closure-2026-10-08/verify.py';ns={'__file__':str(s)};exec(s.read_text().split('patterns=')[0],ns);n=0
for fifo,divider,clock,method,chop in itertools.product([0,1,2,100,65535],[0,1,2,3,7,4095],range(4),[0,1,10],[0,1,2,255]):
 u=ns['guest']();u.mem_write(0x20004000+132,bytes([chop]));u.mem_write(0x20004000+122,bytes([method]));u.mem_write(0x20005000+33,bytes([clock]));u.mem_write(0x20007000,struct.pack('<I',65535));u.mem_write(0x20008000+20,struct.pack('<I',divider<<16));
 for r,v in [(UC_ARM_REG_R4,0x20007000),(UC_ARM_REG_R5,0x20004000),(UC_ARM_REG_R7,0x20005000),(UC_ARM_REG_R2,fifo),(UC_ARM_REG_SP,0x20008000)]:u.reg_write(r,v)
 u.emu_start(0x7c4f,0x7c9a,count=1000);a=struct.unpack('<I',u.mem_read(0x20007000,4))[0]
 v=ns['guest']();v.mem_write(0x20008000,struct.pack('<I',chop));v.reg_write(UC_ARM_REG_R3,method);b=ns['call'](v,ns['symbols']['touch_saturated_max'],[fifo,divider<<16,clock]);assert a==b,(fifo,divider,clock,method,chop,a,b);n+=1
(D/'results.json').write_text(json.dumps({'status':'PASS','cases':n,'scope':'Original7c4e..7c9a register-seeded arithmetic slice; native helper; no scan-call stubs or analog scan claim','elf_sha256':hashlib.sha256(Path(sys.argv[1]).read_bytes()).hexdigest()},indent=2)+'\n');print('PASS',n)
