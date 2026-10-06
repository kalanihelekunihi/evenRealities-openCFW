from pathlib import Path
import hashlib,json,random,struct
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
b=Path('g2/build/pseudocode-first/20260930T190500Z');d=(b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin').read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x438000,(len(d)+4095)&~4095);u.mem_write(0x438000,d);base=0x21000000;u.mem_map(base,4096);sp=base+4000;slot=int.from_bytes(d[0x514b78-0x438000:0x514b7c-0x438000],'little');page=slot&~4095;u.mem_map(page,4096);rng=random.Random(16438);regs=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11];wrap=lambda x:x&0xffffffff;pack=lambda x,y:(x&65535)|((y&65535)<<16);signed=lambda x:x if x<0x80000000 else x-0x100000000;counts={'direct':0,'viewport':0,'ring':0,'fixed':0,'expand_sufficient':0}
for i in range(4096):
 viewport=i>=2048;mode=i%3;ram=bytearray(rng.randbytes(4096));obj=base+128;buf=base+256;back=base+1024;old=rng.randrange(0,100);flags=(rng.getrandbits(32)&~0x2a)|8
 if mode==0:
  flags|=32;length=rng.randrange(16,65);old=rng.randrange(0,2*length)
  while length-(old%length)<8:old=rng.randrange(0,2*length)
  cap=rng.getrandbits(32);counts['ring']+=1
 else:
  if mode==2:flags|=2;counts['expand_sufficient']+=1
  else:counts['fixed']+=1
  cap=old+(8 if viewport or mode==2 else 2)+rng.randrange(0,20);length=rng.getrandbits(32)
 for off,v in [(132,buf),(264,back),(272,cap),(276,old),(280,flags),(300,length)]:struct.pack_into('<I',ram,off,v)
 x,y,w,ht=[rng.getrandbits(32) for _ in range(4)]
 if viewport:
  entry=0x4b1516;commands=[272,pack(0 if signed(x)<0 else x,0 if signed(y)<0 else y),276,pack(wrap(x+w),wrap(y+ht))];counts['viewport']+=1
 else:entry=0x514846;commands=[x,y];counts['direct']+=1
 expected=bytearray(ram);struct.pack_into('<I',expected,280,flags&~8);new=old+len(commands);struct.pack_into('<I',expected,276,new)
 for n,v in enumerate(commands):struct.pack_into('<I',expected,1024+(old+n)*4,v)
 vals=[rng.getrandbits(32) for _ in regs];lr=0x438101
 if not viewport:
  for n,v in enumerate(vals+[lr]):struct.pack_into('<I',expected,3964+n*4,v)
 globalsram=bytearray(rng.randbytes(4096));struct.pack_into('<I',globalsram,slot-page,obj);u.mem_write(page,bytes(globalsram));u.mem_write(base,bytes(ram))
 for reg,v in zip(regs,vals):u.reg_write(reg,v)
 for reg,v in [(UC_ARM_REG_R0,x),(UC_ARM_REG_R1,y),(UC_ARM_REG_R2,w),(UC_ARM_REG_R3,ht),(UC_ARM_REG_R12,rng.getrandbits(32)),(UC_ARM_REG_SP,sp),(UC_ARM_REG_LR,lr),(UC_ARM_REG_XPSR,0x01000000),(UC_ARM_REG_PRIMASK,i%2)]:u.reg_write(reg,v)
 u.emu_start(entry|1,0x438100,count=250);actual=bytes(u.mem_read(base,4096))
 if viewport:assert actual[:3912]==expected[:3912] and actual[4000:]==expected[4000:],(i,'outside88byteframe')
 else:assert actual==expected,(i,'fullRAM')
 assert bytes(u.mem_read(page,4096))==globalsram and u.reg_read(UC_ARM_REG_R0)==buf and u.reg_read(UC_ARM_REG_R1)==new and u.reg_read(UC_ARM_REG_R2)==back,(i,'return/context')
 assert all(u.reg_read(reg)==v for reg,v in zip(regs,vals)) and u.reg_read(UC_ARM_REG_SP)==sp and u.reg_read(UC_ARM_REG_PC)==0x438100 and u.reg_read(UC_ARM_REG_LR)==lr and u.reg_read(UC_ARM_REG_PRIMASK)==i%2
assert bytes(u.mem_read(0x438000,len(d)))==d
o=b/'/private/tmp/independent-writer-extra-0';o.mkdir(parents=True,exist_ok=False);(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'results.json').write_text(json.dumps(dict(status='partial',accepted=False,cases=4096,cohorts=counts,input_sha256=h(d),global_slot=slot,checks=['Original writer and viewport commandpair nohooks, no external children','Random packedviewport endcomputedbefore signedstartclamp, low16truncation','Ring ample space, fixed exact/enoughspace, linked sufficientspace publication','ExactdirectfullRAM saved72frame; viewport exactoutside88byteactiveframe (stackinsideunverified)','Commands cursor bit3clear globals unchanged R0R1R2 callees SP LR PC mask immutableflash'],limitations=['No lowoverheadpaddingloops flush/grow/NULLbuffer/error/chainexecution','No physicalfault/concurrent backing-pointer mutation qualification','APSR R3/R12 and viewportstackinterior unverified','No C admission freeze gates']),indent=2)+'\n');print('PASS4096',counts)
