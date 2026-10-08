from pathlib import Path
import sys,json,hashlib
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_PRIMASK
D=Path(__file__).resolve().parent;ROOT=D.parents[2];fw=(ROOT/'g2/blobs/official/g2-2.2.6.10/firmware_touch.bin').read_bytes();assert hashlib.sha256(fw).hexdigest()=='0d13d8bb1337bf22989dc16143e3d5eca29a31cc1ed753ff624668750ea9470d';segments=[]
with Path(sys.argv[1]).open('rb') as f:
 e=ELFFile(f)
 for s in e.iter_sections():
  if s.name.startswith('.match_'):segments.append((s['sh_addr'],s.data()))
def run(sdk,data,mask):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x3000,0x9000);u.mem_map(0x20000000,0x10000);u.mem_write(0x3300,fw[32:])
 if sdk:
  for a,b in segments:u.mem_write(a,b)
 u.mem_write(0x20002000,data);u.reg_write(UC_ARM_REG_R0,0x20002000);u.reg_write(UC_ARM_REG_R1,len(data));u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20000001);u.reg_write(UC_ARM_REG_PRIMASK,mask);u.emu_start(0x7e69,0x20000000,count=50000);assert u.reg_read(UC_ARM_REG_PC)==0x20000000
 return dict(crc=u.reg_read(UC_ARM_REG_R0),sp=u.reg_read(UC_ARM_REG_SP),primask=u.reg_read(UC_ARM_REG_PRIMASK),input=u.mem_read(0x20002000,len(data)).hex())
results=[]
for seed in range(256):
 for size in [1,124]:
  data=bytes((seed+i*17)&255 for i in range(size));a=run(False,data,seed&1);b=run(True,data,seed&1);assert a==b,(seed,size,a,b);results.append(dict(seed=seed,size=size,result=a))
for size in [0,4,128]:
 a=run(False,bytes(range(size)),0);b=run(True,bytes(range(size)),0);assert a==b;results.append(dict(seed=0,size=size,result=a))
(D/'sdk-crc-results.json').write_text(json.dumps(dict(status='PASS_ORIGINAL_SDK_CRC_SEMANTICS',cases=len(results),sdk_elf_sha256=hashlib.sha256(Path(sys.argv[1]).read_bytes()).hexdigest(),comparisons=results,limits=['OnlyCalcChecksum exercised; no function cuts or external calls; bounded byte buffers0..128.','SDK CRC differs in byte layout but matches these original instruction outcomes; not exactbytes or all-input proof.']),indent=2)+'\n');print('PASS',len(results),'SDK/original CRC cases')
