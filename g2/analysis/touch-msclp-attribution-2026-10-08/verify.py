from pathlib import Path
import sys,json,struct,itertools,hashlib
from unicorn import UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.arm_const import UC_ARM_REG_R3
D=Path(__file__).resolve().parent;s=D.parent/'touch-slider-producer-closure-2026-10-08/verify.py';ns={'__file__':str(s)};exec(s.read_text().split('patterns=')[0],ns);rows=[]
for key,lock,freq,pattern in itertools.product([0,1,2,255],[0,2,255],[0,1,3,6,7],[0,1,0xffffffff]):
 vals=[]
 for native in [False,True]:
  u=ns['guest']();u.mem_map(0x40000000,0x10000);u.mem_map(0x0fff0000,0x10000);u.mem_write(0x0fff0000,bytes(range(256))*256);data=[((j*0x1020304)+pattern)&0xffffffff for j in range(64)];data[17]=(data[17]&~7)|freq;u.mem_write(0x20007000,struct.pack('<64I',*data));u.mem_write(0x20007300,bytes([lock]));u.reg_write(UC_ARM_REG_R3,0x20007300);bus=[]
  def read(u,access,a,n,v,data):
   if 0x40000000<=a<0x40010000 or 0x0fff0000<=a<0x10000000:bus.append(['read',a,n])
  def write(u,access,a,n,v,data):
   if 0x40000000<=a<0x40010000:bus.append(['write',a,n,v])
  u.hook_add(UC_HOOK_MEM_READ,read);u.hook_add(UC_HOOK_MEM_WRITE,write);r=ns['call'](u,ns['symbols']['Cy_MSCLP_Configure'] if native else 0x8fd0,[0x40000000,0x20007000,key]);vals.append((r,bus,u.mem_read(0x40000000,0x10000).hex()))
 assert vals[0]==vals[1],(key,lock,freq,pattern,vals);rows.append({'key':key,'lock':lock,'frequency_field':freq,'pattern':pattern,'status':vals[0][0],'bus':vals[0][1]})
(D/'public-results.json').write_text(json.dumps({'status':'PASS','cases':len(rows),'comparisons':rows,'elf_sha256':hashlib.sha256(Path(sys.argv[1]).read_bytes()).hexdigest(),'limits':['Pinned public PDL source is behaviorally equivalent under these coherent configurations; Configure bytes differ from stock.','SFLASH factory trims and MMIO synthetic; physical frequency is not validated.','No function-entry stubs or retained stock instructions on public side.']},indent=2)+'\n');print('PASS',len(rows))
