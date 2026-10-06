from pathlib import Path
import hashlib,json,random,struct
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
b=Path('g2/build/pseudocode-first/20260930T190500Z');d=(b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin').read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x438000,(len(d)+4095)&~4095);u.mem_write(0x438000,d);base=0x21000000;u.mem_map(base,4096);page=0x20074000;slot=0x20074efc;assert all(int.from_bytes(d[a-0x438000:a-0x438000+4],'little')==slot for a in [0x4b178c,0x514b78]);u.mem_map(page,4096);sp=base+4000;rng=random.Random(16448);regs=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11];counts={'fixed_overflow':0,'flush_null':0,'flush_empty':0,'mode_cached':0}
for i in range(2048):
 mode=i%4;ram=bytearray(rng.randbytes(4096));obj=base+128;buf=base+256;error=rng.getrandbits(32);vals=[rng.getrandbits(32) for _ in regs];lr=0x438101;expectedlr=lr;x,y=[rng.getrandbits(32) for _ in range(2)];r0expect=0;expectedargs={};struct.pack_into('<I',ram,132,buf);struct.pack_into('<I',ram,160,error)
 if mode==0:
  entry=0x514846;old=rng.randrange(1,100);flags=(rng.getrandbits(32)&~0x2a)|8
  struct.pack_into('<III',ram,272,old+rng.randrange(2),old,flags);r0expect=error|8;expectedargs={UC_ARM_REG_R1:obj,UC_ARM_REG_R2:error,UC_ARM_REG_R3:obj};expectedlr=0x5148ef;counts['fixed_overflow']+=1
 elif mode==1:
  entry=0x5147b0;x=0;r0expect=error|8192;expectedargs={UC_ARM_REG_R1:obj,UC_ARM_REG_R2:error};counts['flush_null']+=1
 elif mode==2:
  entry=0x5147b0;x=buf;ring=i%8==2;flags=(rng.getrandbits(32)&~32)|(32 if ring else 0);length=rng.randrange(1,100);old=length*rng.randrange(1,8) if ring else 0
  struct.pack_into('<I',ram,276,old);struct.pack_into('<I',ram,280,flags);struct.pack_into('<I',ram,300,length);counts['flush_empty']+=1
 else:
  entry=0x4b0748;x=obj;m=y;struct.pack_into('<I',ram,208,m);ram[212:215]=bytes([0,1,255]);r0expect=0xffffffff;expectedargs={UC_ARM_REG_R1:0,UC_ARM_REG_R2:vals[3],UC_ARM_REG_R3:1};expectedlr=0x4b075d;counts['mode_cached']+=1
 expected=bytearray(ram)
 if mode==0:
  struct.pack_into('<I',expected,160,r0expect);struct.pack_into('<I',expected,280,flags&~8)
  for j,v in enumerate(vals+[lr]):struct.pack_into('<I',expected,3964+j*4,v)
 elif mode in [1,2]:
  for j,v in enumerate([vals[0],lr]):struct.pack_into('<I',expected,3992+j*4,v)
  if mode==1:struct.pack_into('<I',expected,160,r0expect)
 else:
  for j,v in enumerate([0xffffffff,0,vals[3],lr]):struct.pack_into('<I',expected,3984+j*4,v)
  for j,v in enumerate(vals[:5]+[0x4b075d]):struct.pack_into('<I',expected,3960+j*4,v)
 globalsram=bytearray(rng.randbytes(4096));struct.pack_into('<I',globalsram,slot-page,obj);u.mem_write(page,bytes(globalsram));u.mem_write(base,bytes(ram))
 for reg,v in zip(regs,vals):u.reg_write(reg,v)
 for reg,v in [(UC_ARM_REG_R0,x),(UC_ARM_REG_R1,y),(UC_ARM_REG_R2,rng.getrandbits(32)),(UC_ARM_REG_R3,rng.getrandbits(32)),(UC_ARM_REG_R12,rng.getrandbits(32)),(UC_ARM_REG_SP,sp),(UC_ARM_REG_LR,lr),(UC_ARM_REG_XPSR,0x01000000),(UC_ARM_REG_PRIMASK,i%2)]:u.reg_write(reg,v)
 u.emu_start(entry|1,0x438100,count=180)
 assert bytes(u.mem_read(base,4096))==expected and bytes(u.mem_read(page,4096))==globalsram,(mode,i,'fullRAM')
 assert u.reg_read(UC_ARM_REG_R0)==r0expect and all(u.reg_read(reg)==v for reg,v in expectedargs.items()),(mode,i,'calleroutputs')
 assert all(u.reg_read(reg)==v for reg,v in zip(regs,vals)) and u.reg_read(UC_ARM_REG_LR)==expectedlr and u.reg_read(UC_ARM_REG_SP)==sp and u.reg_read(UC_ARM_REG_PC)==0x438100 and u.reg_read(UC_ARM_REG_PRIMASK)==i%2
assert bytes(u.mem_read(0x438000,len(d)))==d
o=b/'/private/tmp/independent-errorflush-fixture';o.mkdir(parents=True,exist_ok=False);(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'results.json').write_text(json.dumps(dict(status='partial',accepted=False,cases=2048,cohorts=counts,input_sha256=h(d),checks=['Original linkedcode nohooks, writerfixedoverflowcallsactualerrorORleaf','Nullflush tailrecords8192; emptylinear/ringflush returns0','Modewrappercallsactualcachehit with overwritten savedslots and outputsFFFFFFFF,0,entryR7','ExactfullRAMincl72/8/40byteframes, unchangedglobals, calleeRegs/SP/PC/PRIMASK, pathappropriateLRcontext and immutableflash'],limitations=['No nonemptyflush/submission, backingfault/concurrentupdates or hardwarequalification','No APSR/callerR12 qualification; readclearleafnotexecuted','No C admission freeze gates']),indent=2)+'\n');print('PASS2048',counts)
