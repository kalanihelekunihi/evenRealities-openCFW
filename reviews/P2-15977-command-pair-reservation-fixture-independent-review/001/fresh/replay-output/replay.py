from pathlib import Path
import hashlib,json,random,struct
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
b=Path('g2/build/pseudocode-first/20260930T190500Z');src=b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x438000,(len(d)+4095)&~4095);u.mem_write(0x438000,d);base=0x21000000;u.mem_map(base,4096);sp=base+4000;slot=int.from_bytes(d[0x514d94-0x438000:0x514d98-0x438000],'little');page=slot&~4095;u.mem_map(page,4096);rng=random.Random(16374);regs=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11,UC_ARM_REG_R12];cohorts={'linear':0,'ring':0,'negative_request':0,'boundary_request':0}
for i in range(2048):
 ram=bytearray(rng.randbytes(4096));objectptr=base+128;buf=base+256;backing=base+512;mask=(rng.getrandbits(32)&~0x28)|8;ring=i%2==1
 if ring:
  mask|=32;length=rng.randrange(64,1025);old=rng.randrange(length*4);free=length-(old%length);half=free//2
  if half==0:old-=1;free=length-(old%length);half=free//2
  cap=rng.getrandbits(32);maximum=half-1;cohorts['ring']+=1
 else:
  old=rng.randrange(512);half=rng.randrange(3,101);cap=old+2*half;length=rng.getrandbits(32);maximum=half-2;cohorts['linear']+=1
 if i%4==0:request=-rng.randrange(1,33);cohorts['negative_request']+=1
 elif i%4==1:request=maximum;cohorts['boundary_request']+=1
 else:request=rng.randrange(maximum+1)
 for off,v in [(132,buf),(264,backing),(272,cap),(276,old),(280,mask),(300,length)]:struct.pack_into('<I',ram,off,v)
 globalsram=bytearray(rng.randbytes(4096));struct.pack_into('<I',globalsram,slot-page,objectptr);u.mem_write(page,bytes(globalsram));u.mem_write(base,bytes(ram));expected=bytearray(ram);struct.pack_into('<I',expected,280,mask&~8);new=(old+(request&0xffffffff)*2)&0xffffffff;struct.pack_into('<I',expected,276,new);vals=[rng.getrandbits(32) for _ in regs];lr=0x438101
 for j,v in enumerate(vals[:3]+[lr]):struct.pack_into('<I',expected,3984+j*4,v)
 for reg,v in zip(regs,vals):u.reg_write(reg,v)
 for reg,v in [(UC_ARM_REG_R0,request&0xffffffff),(UC_ARM_REG_R1,rng.getrandbits(32)),(UC_ARM_REG_R2,rng.getrandbits(32)),(UC_ARM_REG_R3,rng.getrandbits(32)),(UC_ARM_REG_SP,sp),(UC_ARM_REG_LR,lr),(UC_ARM_REG_XPSR,0x01000000),(UC_ARM_REG_PRIMASK,i%2)]:u.reg_write(reg,v)
 u.emu_start(0x514aed,0x438100,count=80)
 assert bytes(u.mem_read(base,4096))==expected and bytes(u.mem_read(page,4096))==globalsram,(i,ring,request,maximum,'memory')
 assert u.reg_read(UC_ARM_REG_R0)==(backing+old*4)&0xffffffff and u.reg_read(UC_ARM_REG_R1)==buf and u.reg_read(UC_ARM_REG_R2)==new,(i,'result')
 assert all(u.reg_read(reg)==v for reg,v in zip(regs,vals)) and u.reg_read(UC_ARM_REG_SP)==sp and u.reg_read(UC_ARM_REG_LR)==lr and u.reg_read(UC_ARM_REG_PC)==0x438100 and u.reg_read(UC_ARM_REG_PRIMASK)==i%2
assert bytes(u.mem_read(0x438000,len(d)))==d
o=Path('/tmp/review2-graphics-pair-fixture');o.mkdir(parents=True,exist_ok=False);(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'results.json').write_text(json.dumps(dict(status='partial',accepted=False,cases=2048,cohorts=cohorts,input_sha256=h(d),global_slot=slot,executed_span=[0x514aec,0x514b76],checks=['Original instructions nohooks, childfree ring/linear capacity branches','Independent ring modulo vs instructionSDIV/MLA; pairindex updates, boundary/negative/zero requests','ExactfullRAM inclsavedframe and bit3clear; unchangedglobals; R0R1R2 callee registers SP LR PC mask immutableflash'],limitations=['No childcalls (flush/grow/NULLbuffer/errorreport), concurrency or invalidring/dividezero/fault qualification','Backed ordinaryRAM only, nohardware/ownership qualification','APSR and caller R3 not checked','No admission C freeze gates']),indent=2)+'\n');print('PASS2048',cohorts)
