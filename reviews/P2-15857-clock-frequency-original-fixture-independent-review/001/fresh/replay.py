from pathlib import Path
import hashlib,json,random,struct,math
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
b=Path('g2/build/pseudocode-first/20260930T190500Z');d=(b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin').read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x438000,(len(d)+4095)&~4095);u.mem_write(0x438000,d);base=0x21000000;u.mem_map(base,4096);sp=base+4000;rng=random.Random(16262);regs=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11,UC_ARM_REG_R12]
f32=lambda x:struct.unpack('<f',struct.pack('<f',x))[0]
for i in range(2048):
 exponent=(i%16)|(rng.randrange(1<<24)<<8);shift=1<<(exponent&255);source=rng.randrange(shift,0xffffffff+1);requested=rng.randrange(0, min(0xffffffff,(source//shift)*100)+1);ram=bytearray(rng.randbytes(4096));u.mem_write(base,bytes(ram));expected=bytearray(ram);quotient=source//shift;ratio=f32(f32(requested)/f32(quotient));value=int(ratio*32768);assert 0<=value<=0xffffffff;struct.pack_into('<I',expected,128,value)
 vals=[rng.getrandbits(32) for _ in regs]
 for reg,x in zip(regs,vals):u.reg_write(reg,x)
 for reg,x in [(UC_ARM_REG_R0,source),(UC_ARM_REG_R1,requested),(UC_ARM_REG_R2,exponent),(UC_ARM_REG_R3,base+128),(UC_ARM_REG_SP,sp),(UC_ARM_REG_LR,0x438101),(UC_ARM_REG_XPSR,0x01000000),(UC_ARM_REG_PRIMASK,i%2),(UC_ARM_REG_FPSCR,0),(UC_ARM_REG_FPEXC,1<<30)]:u.reg_write(reg,x)
 u.emu_start(0x4d38eb,0x438100,count=30)
 assert u.reg_read(UC_ARM_REG_R0)==0 and u.reg_read(UC_ARM_REG_R1)==1 and u.reg_read(UC_ARM_REG_R2)==shift and u.reg_read(UC_ARM_REG_R3)==base+128 and bytes(u.mem_read(base,4096))==expected and u.reg_read(UC_ARM_REG_SP)==sp and u.reg_read(UC_ARM_REG_PC)==0x438100 and u.reg_read(UC_ARM_REG_PRIMASK)==i%2 and all(u.reg_read(reg)==x for reg,x in zip(regs,vals)),(i,value,bytes(u.mem_read(base+128,4)).hex())
assert bytes(u.mem_read(0x438000,len(d)))==d
o=Path('reviews/P2-15857-clock-frequency-original-fixture-independent-review/001/fresh');o.mkdir(parents=True,exist_ok=False);(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'results.json').write_text(json.dumps(dict(accepted=False,status='partial',cases=2048,input_sha256=h(d),checks=['Original FP instructions no hooks','Positive nonzero quotient exponentlow8 0..15 random upperbits finite ratio0..100','Per-operation nearest singleprecision oracle then fixedpointtruncate15; fullRAM SP PC PRIMASK callees R1R2R3 immutableflash'],limitations=['FPSCR zero initialized FP enabled; FPSCR result flags not checked','No zero quotient NaN overflow trap alternate FP rounding or subnormal qualification','Python doubledivision followed by F32 oracle selected finite cohort only','No C admission freeze gates']),indent=2)+'\n');print('PASS2048')
