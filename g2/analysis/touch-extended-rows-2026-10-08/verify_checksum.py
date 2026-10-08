from pathlib import Path
import sys,json,hashlib,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC
D=Path(__file__).resolve().parent;ROOT=D.parents[2];fw=(ROOT/'g2/blobs/official/g2-2.2.6.10/firmware_touch.bin').read_bytes();assert hashlib.sha256(fw).hexdigest()=='0d13d8bb1337bf22989dc16143e3d5eca29a31cc1ed753ff624668750ea9470d';im=fw[32:];elfpath=Path(sys.argv[1]);segments=[]
with elfpath.open('rb') as f:
 e=ELFFile(f)
 for s in e.iter_segments():
  if s['p_type']=='PT_LOAD':segments.append((s['p_vaddr'],s.data()))
 entry=next(s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols() if s.name=='touch_row_checksum')
def run(native,row,size):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x3000,0x9000);u.mem_map(0x100000,0x20000);u.mem_map(0x20000000,0x10000)
 if native:
  for a,b in segments:u.mem_write(a,b)
 else:u.mem_write(0x3300,im)
 u.mem_write(0x20003000,row);u.reg_write(UC_ARM_REG_R0,0x20003000);u.reg_write(UC_ARM_REG_R1,size);u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20000001);u.emu_start((entry if native else 0x7f6c)|1,0x20000000,count=30000);assert u.reg_read(UC_ARM_REG_PC)==0x20000000;return u.reg_read(UC_ARM_REG_R0)
cases=[]
for size,seed in itertools.product([4,5,16,64,128,256],[0,0xff,0x1234]):
 raw=bytearray((seed+i*13)&255 for i in range(size));tail=raw.copy();tail[-3:]=bytes(x^0xff for x in tail[-3:]);first=raw.copy();first[0]^=0xff
 variants=[raw,tail,first]
 if size>4:included=raw.copy();included[1]^=1;variants.append(included)
 answers=[]
 for row in variants:
  a=run(False,bytes(row),size);b=run(True,bytes(row),size);assert a==b;answers.append(a);cases.append({'size':size,'row':bytes(row).hex(),'crc':a})
 assert answers[0]==answers[1]==answers[2]
 if size>4:assert answers[3]!=answers[0]
r={'status':'PASS_STOCK_BYTE_ONE_CHECKSUM_SPAN','cases':len(cases),'elf_sha256':hashlib.sha256(elfpath.read_bytes()).hexdigest(),'comparisons':cases,'limits':['Actual stock wrapper/CRC versus independent native C; no semantic cuts.','Bounded row sizes4..256; uint16 loop behavior for impossible larger lengths not exercised.','CRC excludes byte0 and last3 row bytes; no claim of persistence/authentication strength.']};(D/'checksum-results.json').write_text(json.dumps(r,indent=2)+'\n');print('PASS',len(cases),'checksum/span cases')
