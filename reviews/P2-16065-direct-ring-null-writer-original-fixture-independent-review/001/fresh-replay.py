from pathlib import Path
import hashlib,json,random,struct
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
b=Path('g2/build/pseudocode-first/20260930T190500Z');d=(b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin').read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x438000,(len(d)+4095)&~4095);u.mem_write(0x438000,d);base=0x21000000;u.mem_map(base,4096);gbase=0x20073000;u.mem_map(gbase,8192);sp=base+4000;slot=int.from_bytes(d[0x514b78-0x438000:0x514b7c-0x438000],'little');desc=int.from_bytes(d[0x52404c-0x438000:0x524050-0x438000],'little');assert slot==0x20074efc and desc==0x20073db0;rng=random.Random(16462);regs=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11];counts={'standalone':0,'null_writer_fallback':0,'padding_wrap':0,'exact_pair_wrap':0}
for i in range(2048):
 nested=i%2==1;cap=rng.randrange(4,65);old=cap-1 if i%3==0 else cap-2 if i%3==1 else rng.randrange(cap);cmd=rng.getrandbits(24);payload=rng.getrandbits(32);obj=base+128;back=base+1024;ram=bytearray(rng.randbytes(4096));struct.pack_into('<I',ram,132,0);struct.pack_into('<I',ram,144,old);expected=bytearray(ram);cursor=old
 if old+2>cap:
  for k in range(old,cap):struct.pack_into('<I',expected,1024+k*4,65536)
  cursor=0;counts['padding_wrap']+=1
 elif old+2==cap:counts['exact_pair_wrap']+=1
 struct.pack_into('<I',expected,1024+cursor*4,cmd);cursor=(cursor+1)%cap;struct.pack_into('<I',expected,1024+cursor*4,payload);cursor=(cursor+1)%cap;struct.pack_into('<I',expected,144,cursor)
 vals=[rng.getrandbits(32) for _ in regs];lr=0x438101
 if nested:
  entry=0x514846;counts['null_writer_fallback']+=1;expectedlr=0x514867;r0expect=0
  for j,v in enumerate(vals+[lr]):struct.pack_into('<I',expected,3964+j*4,v)
  for j,v in enumerate([vals[0],cmd,payload,slot,0x514867]):struct.pack_into('<I',expected,3908+j*4,v)
 else:
  entry=0x523e92;counts['standalone']+=1;expectedlr=lr;r0expect=cursor
  for j,v in enumerate(vals[:4]+[lr]):struct.pack_into('<I',expected,3980+j*4,v)
 globalram=bytearray(rng.randbytes(8192));struct.pack_into('<I',globalram,slot-gbase,obj);struct.pack_into('<IIII',globalram,desc-gbase,obj,back,back,cap);u.mem_write(gbase,bytes(globalram));u.mem_write(base,bytes(ram))
 for reg,v in zip(regs,vals):u.reg_write(reg,v)
 for reg,v in [(UC_ARM_REG_R0,cmd),(UC_ARM_REG_R1,payload),(UC_ARM_REG_R2,rng.getrandbits(32)),(UC_ARM_REG_R3,rng.getrandbits(32)),(UC_ARM_REG_R12,rng.getrandbits(32)),(UC_ARM_REG_SP,sp),(UC_ARM_REG_LR,lr),(UC_ARM_REG_XPSR,0x01000000),(UC_ARM_REG_PRIMASK,i%2)]:u.reg_write(reg,v)
 u.emu_start(entry|1,0x438100,count=1000)
 assert bytes(u.mem_read(base,4096))==expected and bytes(u.mem_read(gbase,8192))==globalram,(i,'exactRAM')
 assert u.reg_read(UC_ARM_REG_R0)==r0expect and u.reg_read(UC_ARM_REG_R1)==payload and u.reg_read(UC_ARM_REG_R2)==cmd and u.reg_read(UC_ARM_REG_R3)==obj,(i,'outputs')
 assert all(u.reg_read(reg)==v for reg,v in zip(regs,vals)) and u.reg_read(UC_ARM_REG_LR)==expectedlr and u.reg_read(UC_ARM_REG_SP)==sp and u.reg_read(UC_ARM_REG_PC)==0x438100 and u.reg_read(UC_ARM_REG_PRIMASK)==i%2
assert bytes(u.mem_read(0x438000,len(d)))==d
o=b/'/private/tmp/independent-ring-fixture';o.mkdir(parents=True,exist_ok=False);(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'results.json').write_text(json.dumps(dict(status='partial',accepted=False,cases=2048,cohorts=counts,input_sha256=h(d),checks=['Original directring or parentNULLbuffer callsactualdirectring nohooks','Validcap4..64 signednormalindices, random24bitcommands payloads, padding65536 and exactpair/endwrap','ExactfullRAMincl24or96byteframe saves, untouchedglobals, R0R1R2R3 callee regs SP LR PC mask immutableflash'],limitations=['Highcommandbytezero only; submission5140EA/514046 and invalidcapacity/indices/concurrency/fault paths unqualified','No APSR/callerR12 qualification or hardwareequivalence','No C admission freeze gates']),indent=2)+'\n');print('PASS2048',counts)
