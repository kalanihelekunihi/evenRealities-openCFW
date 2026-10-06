from pathlib import Path
import hashlib,json,random,struct
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
b=Path('g2/build/pseudocode-first/20260930T190500Z');d=(b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin').read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x438000,(len(d)+4095)&~4095);u.mem_write(0x438000,d);base=0x21000000;pb=0x40004000;u.mem_map(base,4096);u.mem_map(pb,4096);sp=base+4000;rng=random.Random(16258);regs=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11,UC_ARM_REG_R12]
for i in range(2048):
 mode=i%4;cfg=[0,base+64,pb+0x48,pb+0x50][mode];ram=bytearray(rng.randbytes(4096));per=bytearray(rng.randbytes(4096));u.mem_write(base,bytes(ram));u.mem_write(pb,bytes(per));er=bytearray(ram);ep=bytearray(per)
 def region(addr):return (ep,addr-pb) if pb<=addr<pb+4096 else (er,addr-base)
 def rd(addr):v,o=region(addr);return struct.unpack_from('<I',v,o)[0]
 def rb(addr):v,o=region(addr);return v[o]
 def wr(addr,x):v,o=region(addr);struct.pack_into('<I',v,o,x&0xffffffff)
 if cfg:
  wr(pb+0x4c,rd(pb+0x4c)|7);wr(pb+0x48,(rd(pb+0x48)&~0x20000000)|((rb(cfg)&1)<<29));wr(pb+0x50,(rd(pb+0x50)&~3)|(rb(cfg+1)&3));wr(pb+0x50,(rd(pb+0x50)&~0x7ffffffc)|((rd(cfg+4)&0x1fffffff)<<2));wr(pb+0x48,rd(pb+0x48)|1)
 vals=[rng.getrandbits(32) for _ in regs]
 for reg,x in zip(regs,vals):u.reg_write(reg,x)
 for reg,x in [(UC_ARM_REG_R0,cfg),(UC_ARM_REG_SP,sp),(UC_ARM_REG_LR,0x438101),(UC_ARM_REG_XPSR,0x01000000),(UC_ARM_REG_PRIMASK,i%2)]:u.reg_write(reg,x)
 u.emu_start(0x4d3993,0x438100,count=60);ar=bytes(u.mem_read(base,4096));assert u.reg_read(UC_ARM_REG_R0)==(0 if cfg else 6) and ar[:3996]==er[:3996] and ar[4000:]==er[4000:] and bytes(u.mem_read(pb,4096))==ep and u.reg_read(UC_ARM_REG_SP)==sp and u.reg_read(UC_ARM_REG_PC)==0x438100 and u.reg_read(UC_ARM_REG_PRIMASK)==i%2 and all(u.reg_read(reg)==x for reg,x in zip(regs,vals)),i
 # Run original disable after configuration, retaining every other write.
 wr(pb+0x48,rd(pb+0x48)&~1)
 u.reg_write(UC_ARM_REG_LR,0x438101);u.emu_start(0x4d39e5,0x438100,count=20)
 ar=bytes(u.mem_read(base,4096))
 assert u.reg_read(UC_ARM_REG_R0)==0 and u.reg_read(UC_ARM_REG_R1)==rd(pb+0x48) and ar[:3996]==er[:3996] and ar[4000:]==er[4000:] and bytes(u.mem_read(pb,4096))==ep and u.reg_read(UC_ARM_REG_SP)==sp and u.reg_read(UC_ARM_REG_PC)==0x438100 and u.reg_read(UC_ARM_REG_PRIMASK)==i%2 and all(u.reg_read(reg)==x for reg,x in zip(regs,vals)),i
assert bytes(u.mem_read(0x438000,len(d)))==d
o=Path('reviews/P2-15853-clock-class5-config-disable-independent-review/001/fresh');o.mkdir(parents=True,exist_ok=False);(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'results.json').write_text(json.dumps(dict(accepted=False,status='partial',cases=2048,original_invocations=4096,input_sha256=h(d),checks=['Original configuration followed by disable no hooks; disable clears only bit0 and returns newwordR1','NULL ordinary cfg and cfg aliases40004048/40004050','Sequential oracle full peripheral/localRAMoutside4stack preservedbit31 twoCwrites lowbits SP PC mask callees immutableflash'],limitations=['Two selected aliases ordinary backing only not physical clock semantics','No fault concurrency generalalias coverage','No C admission freeze gates']),indent=2)+'\n');print('PASS2048')
