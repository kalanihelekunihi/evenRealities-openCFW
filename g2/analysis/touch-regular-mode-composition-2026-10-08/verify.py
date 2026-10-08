from pathlib import Path
import sys,json,struct,itertools,hashlib
from unicorn import UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
D=Path(__file__).resolve().parent;s=D.parent/'touch-mode-closure-2026-10-08/verify.py';ns={'__file__':str(s)};exec(s.read_text().split('for old,desired,busy')[0],ns);g=ns['g'];rows=[]
for old,desired,lock,freq,irq in itertools.product([0,2,3,5,255],[0,1,2,3,4,5,6,8,255],[0,2,255],[0,3,6,7],[0,1]):
 vals=[]
 for native in [False,True]:
  u=ns['fixture']();u.mem_map(0x40004000,0xc000);u.mem_map(0x40020000,0x1000);u.mem_map(0x40040000,0x1000);u.mem_map(0x0fff0000,0x10000);u.mem_write(0x0fff0000,bytes(range(256))*256);u.mem_write(0x20003500+85,bytes([old]));u.mem_write(0x20003700,bytes([lock]));base=[j*0x1020304 for j in range(64)];base[17]=(base[17]&~7)|freq;u.mem_write(0x20003600,struct.pack('<64I',*base));u.mem_write(0x20002000+20,struct.pack('<II',0x20006000,0x20006018));u.mem_write(0x20003000+12,struct.pack('<H',3));u.mem_write(0x20003000+44,b'\x01');u.mem_write(0x20006000,b''.join(struct.pack('<IB3x',0x40040000+(j%2)*256,j) for j in range(4)));u.mem_write(0x20003100+8,struct.pack('<IB3xIB3x',0x40040000,6,0x40040100,7));u.reg_write(UC_ARM_REG_PRIMASK,irq);bus=[]
  def read(u,access,a,n,v,data):
   if 0x40000000<=a<0x40041000 or 0x0fff0000<=a<0x10000000:bus.append(['read',a,n,u.reg_read(UC_ARM_REG_PRIMASK)])
  def write(u,access,a,n,v,data):
   if 0x40000000<=a<0x40041000:bus.append(['write',a,n,v,u.reg_read(UC_ARM_REG_PRIMASK)])
  u.hook_add(UC_HOOK_MEM_READ,read);u.hook_add(UC_HOOK_MEM_WRITE,write);r=g['call'](u,g['symbols']['touch_switch_regular_dependency'] if native else 0x6ac0,[desired,0x20002000]);vals.append((r,bus,u.mem_read(0x20003200,32).hex(),u.mem_read(0x20003400,128).hex(),u.mem_read(0x20003500,128).hex(),u.reg_read(UC_ARM_REG_PRIMASK)))
 assert vals[0]==vals[1],(old,desired,lock,freq,irq,vals);rows.append({'old':old,'desired':desired,'lock':lock,'frequency':freq,'primask':irq,'return':vals[0][0],'current_mode':bytes.fromhex(vals[0][4])[85],'bus':vals[0][1]})
(D/'results.json').write_text(json.dumps({'status':'PASS','cases':len(rows),'comparisons':rows,'elf_sha256':hashlib.sha256(Path(sys.argv[1]).read_bytes()).hexdigest(),'limits':['No function-entry stubs; original helpers and independent GPIO/CPU/MRSS/source plus public pinned PDL configure execute.','Desiredmode7 excluded; currentmode7 guard covered in earlier modecore tests.','Synthetic GPIO/MSCLP/SFLASH, no hardware behavior or analog timing.','Public PDL configure behavior matches; bytes differ in loop layout.']},indent=2)+'\n');print('PASS',len(rows))
