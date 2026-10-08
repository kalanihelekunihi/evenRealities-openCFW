from pathlib import Path
import sys,json,hashlib,struct,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_MEM_WRITE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_PRIMASK
D=Path(__file__).resolve().parent;ROOT=D.parents[2];fw=(ROOT/'g2/blobs/official/g2-2.2.6.10/firmware_touch.bin').read_bytes();assert hashlib.sha256(fw).hexdigest()=='0d13d8bb1337bf22989dc16143e3d5eca29a31cc1ed753ff624668750ea9470d';im=fw[32:];elfpath=Path(sys.argv[1]);segments=[];symbols={}
with elfpath.open('rb') as f:
 e=ELFFile(f)
 for s in e.iter_segments():
  if s['p_type']=='PT_LOAD':segments.append((s['p_vaddr'],s.data()))
 for s in e.get_section_by_name('.symtab').iter_symbols():symbols[s.name]=s['st_value']
def guest(native):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
 for a,n in [(0x3000,0x9000),(0x100000,0x20000),(0x20000000,0x10000),(0x40100000,0x1000),(0x40030000,0x1000)]:u.mem_map(a,n)
 if native:
  for a,b in segments:u.mem_write(a,b)
 else:u.mem_write(0x3300,im)
 return u
cases=[]
for n,offset in itertools.product([0,1,16,128,512],[0,1,16,512]):
 results=[]
 for native in [False,True]:
  u=guest(native);u.mem_write(0x20003000,bytes(i&255 for i in range(1536)));args=[0x12345678,0x20003000,n,0x20003000+offset]
  for r,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],args):u.reg_write(r,v)
  u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20000001);u.emu_start((symbols['touch_storage_copy'] if native else 0x4860)|1,0x20000000,count=15000);assert u.reg_read(UC_ARM_REG_PC)==0x20000000;results.append({'memory':u.mem_read(0x20003000,1536).hex(),'sp':u.reg_read(UC_ARM_REG_SP)})
 assert results[0]==results[1];cases.append({'size':n,'offset':offset,'result':results[0]})
r={'status':'PASS_REAL_COPY_CALLBACK','cases':len(cases),'elf_sha256':hashlib.sha256(elfpath.read_bytes()).hexdigest(),'comparisons':cases,'limits':['Actual stock copy callback/memcpy and native source execute with no cuts; valid mapped guest buffers only.','Raw overlap reproduces forward-copy behavior, not a recommended memcpy overlap contract; void return/flags outside comparison.']};(D/'copy-results.json').write_text(json.dumps(r,indent=2)+'\n');print('PASS',len(cases),'copy callback cases')
