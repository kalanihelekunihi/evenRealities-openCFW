from pathlib import Path
import hashlib,json,random,struct
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
b=Path('g2/build/pseudocode-first/20260930T190500Z');d=(b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin').read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x438000,(len(d)+4095)&~4095);u.mem_write(0x438000,d);base=0x21000000;u.mem_map(base,4096);u.mem_map(0x20074000,4096);rng=random.Random(16270);sp=base+4000
preserved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11,UC_ARM_REG_R12]
for i in range(2048):
 pointer=base+128;ram=bytearray(rng.randbytes(4096));struct.pack_into('<I',ram,128,0);u.mem_write(base,bytes(ram));expected=bytearray(ram);saved_r2=rng.getrandbits(32);saved_r3=rng.getrandbits(32);active=i%2;glob=bytearray(rng.randbytes(4096));glob[0xf58]=0 if active==0 else rng.randrange(1,256);u.mem_write(0x20074000,bytes(glob))
 if active:glob[0xf58]=0;struct.pack_into('<I',glob,0x268,0)
 vals=[rng.getrandbits(32) for _ in preserved]
 for reg,v in zip(preserved,vals):u.reg_write(reg,v)
 u.reg_write(UC_ARM_REG_R0,pointer);u.reg_write(UC_ARM_REG_R1,rng.getrandbits(32));u.reg_write(UC_ARM_REG_R2,saved_r2);u.reg_write(UC_ARM_REG_R3,saved_r3);u.reg_write(UC_ARM_REG_SP,sp);u.reg_write(UC_ARM_REG_LR,0x438101);u.reg_write(UC_ARM_REG_XPSR,0x01000000);u.reg_write(UC_ARM_REG_PRIMASK,i%2)
 u.emu_start(0x4c4059,0x438100,count=120)
 assert u.reg_read(UC_ARM_REG_PC)==0x438100 and u.reg_read(UC_ARM_REG_R0)==(i%2 if active else saved_r2) and u.reg_read(UC_ARM_REG_R1)==saved_r3,i
 assert bytes(u.mem_read(base,3968))==expected[:3968] and bytes(u.mem_read(base+4000,96))==expected[4000:] and bytes(u.mem_read(0x20074000,4096))==glob and u.reg_read(UC_ARM_REG_SP)==sp and u.reg_read(UC_ARM_REG_PRIMASK)==i%2 and all(u.reg_read(reg)==v for reg,v in zip(preserved,vals)),i
assert bytes(u.mem_read(0x438000,len(d)))==d
o=Path('reviews/P2-15865-class-five-cleanup-independent-review/001/fresh');o.mkdir(parents=True,exist_ok=False);(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'results.json').write_text(json.dumps(dict(accepted=False,status='partial',cases=2048,input_sha256=h(d),checks=['Originalclass5cleanup plus immediatewait and interruptmask child without hooks','Inactiveflag retains globalpointer and flags; activeNZcounter0 ordered postwait flag58=0 pointerzero','Exactglobalpage RAMoutside32nestedstack branch-dependentR0 R1entryR3 preservedR4-R12SPPCPRIMASKimmutableflash'],limitations=['Activepathcounterzero only; delaytransition timeout faults aliases concurrentmutation excluded','No physicalclock qualification C globaladmission corpusfreeze gateadvance']),indent=2)+'\n');print('PASS 2048')
