from pathlib import Path
import hashlib,json,random,struct
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
b=Path('g2/build/pseudocode-first/20260930T190500Z');d=(b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin').read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x438000,(len(d)+4095)&~4095);u.mem_write(0x438000,d);base=0x21000000;u.mem_map(base,4096);sp=base+4000;rng=random.Random(16268);regs=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11,UC_ARM_REG_R12]
for i in range(4096):
 mode=i%4;polarity=0 if mode<2 else rng.randrange(1,256);arg=polarity|(rng.randrange(1<<24)<<8);word=rng.getrandbits(32);mask=rng.getrandbits(32);expected=word&mask
 if mode%2:expected^=1<<(i//4%32)
 equality=(word&mask)==expected;status=0 if equality==bool(polarity) else 4;ram=bytearray(rng.randbytes(4096));struct.pack_into('<I',ram,64,word);struct.pack_into('<I',ram,4000,arg);u.mem_write(base,bytes(ram));vals=[rng.getrandbits(32) for _ in regs]
 for reg,x in zip(regs,vals):u.reg_write(reg,x)
 for reg,x in [(UC_ARM_REG_R0,0),(UC_ARM_REG_R1,base+64),(UC_ARM_REG_R2,mask),(UC_ARM_REG_R3,expected),(UC_ARM_REG_SP,sp),(UC_ARM_REG_LR,0x438101),(UC_ARM_REG_XPSR,0x01000000),(UC_ARM_REG_PRIMASK,i%2)]:u.reg_write(reg,x)
 u.emu_start(0x480827,0x438100,count=50);ar=bytes(u.mem_read(base,4096));assert u.reg_read(UC_ARM_REG_R0)==status and ar[:3976]==ram[:3976] and ar[4000:]==ram[4000:] and u.reg_read(UC_ARM_REG_SP)==sp and u.reg_read(UC_ARM_REG_PC)==0x438100 and u.reg_read(UC_ARM_REG_PRIMASK)==i%2 and all(u.reg_read(reg)==x for reg,x in zip(regs,vals)),i
assert bytes(u.mem_read(0x438000,len(d)))==d
o=Path('reviews/P2-15863-masked-poll-zero-budget-independent-review/001/fresh');o.mkdir(parents=True,exist_ok=False);(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'results.json').write_text(json.dumps(dict(accepted=False,status='partial',cases=4096,input_sha256=h(d),checks=['Original polling instructions nohooks zero budget','Both equality and inequality low8 polarity upperbits ignored expectednotmasked','Status0 or4 full RAMoutside24stack SP PC PRIMASK callees flash'],limitations=['No delays residentROM40 timing unavailable','OrdinaryRAM no MMIO aliases faults concurrency validation','No C admission freeze gates']),indent=2)+'\n');print('PASS4096')
