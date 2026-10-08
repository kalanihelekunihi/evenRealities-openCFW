from pathlib import Path
import sys,json,struct,itertools,hashlib
from unicorn import UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
D=Path(__file__).resolve().parent;s=D.parent/'touch-slider-producer-closure-2026-10-08/verify.py';ns={'__file__':str(s)};exec(s.read_text().split('patterns=')[0],ns);n=0
for port,pin,dm,mux,analog,irq in itertools.product([0x40040000,0x40040100],[0,3,7],[0,9,15],[0,1,15],[0,1],[0,1]):
 vals=[]
 for native in [False,True]:
  u=ns['guest']();u.mem_map(0x40020000,0x1000);u.mem_map(0x40040000,0x1000);u.mem_write(0x40020000,b'\xa5'*0x1000);u.mem_write(0x40040000,b'\x5a'*0x1000);u.mem_write(0x20008000,struct.pack('<I',analog));u.reg_write(UC_ARM_REG_R3,mux);u.reg_write(UC_ARM_REG_PRIMASK,irq);bus=[]
  def read(u,access,a,n,v,data):
   if 0x40020000<=a<0x40041000:bus.append(['read',a,n,u.reg_read(UC_ARM_REG_PRIMASK)])
  def write(u,access,a,n,v,data):
   if 0x40020000<=a<0x40041000:bus.append(['write',a,n,v,u.reg_read(UC_ARM_REG_PRIMASK)])
  u.hook_add(UC_HOOK_MEM_READ,read);u.hook_add(UC_HOOK_MEM_WRITE,write);ns['call'](u,ns['symbols']['touch_config_pin'] if native else 0x5fc6,[port,pin,dm]);vals.append((bus,u.mem_read(0x40020000,0x1000).hex(),u.mem_read(0x40040000,0x1000).hex(),u.reg_read(UC_ARM_REG_PRIMASK)))
 assert vals[0]==vals[1],(port,pin,dm,mux,analog,irq,vals);n+=1
(D/'results.json').write_text(json.dumps({'status':'PASS','cases':n,'elf_sha256':hashlib.sha256(Path(sys.argv[1]).read_bytes()).hexdigest(),'scope':'Original5fc6 with actual GPIO/HSIOM/critical helpers versus independent C; valid inputs, synthetic MMIO, ordered accesses and PRIMASK compared.','limits':['Wrapper electrode/shield/CMOD composition tested separately.','No physical pin, IRQ concurrency or malformed-input behavior claim.']},indent=2)+'\n');print('PASS',n)
