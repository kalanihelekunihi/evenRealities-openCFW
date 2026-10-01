from pathlib import Path
import json,hashlib,itertools,struct
from unicorn import *
from unicorn.arm_const import *
b=Path('g2/build/pseudocode-first/20260930T190500Z');o=Path('reviews/P2-touch-register-field-9fd4-independent-review-1216/001/regenerated');o.mkdir(parents=True,exist_ok=False);src=b/'attempts/P2-touch-reset-pseudocode-108/001/touch.flash.bin';d=src.read_bytes();h=lambda v:hashlib.sha256(v).hexdigest();assert struct.unpack_from('<II',d,0xa014-0x3300)==(0xff0000ff,0x00ffff00);rows=[]
for a,c,v,old in itertools.product([0,1,2,257],[0,1,2,0xffffffff],[0,3,65535,65536,0xffffffff],[0,0xa5a5a5a5,0xffffffff]):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x10000);u.mem_write(0x3300,d);u.mem_map(0x20000000,0x10000);u.mem_map(0x40010000,0x1000);u.mem_map(0x09000000,0x1000)
 for p in [0x40010300,0x40010304]:u.mem_write(p,old.to_bytes(4,'little'))
 for r,x in [(UC_ARM_REG_R0,a),(UC_ARM_REG_R1,c),(UC_ARM_REG_R2,v),(UC_ARM_REG_R4,0x12345678),(UC_ARM_REG_SP,0x2000f000),(UC_ARM_REG_LR,0x09000001)]:u.reg_write(r,x)
 writes=[];reads=[]
 def code(u,p,s,x):
  if p==0x09000000:u.emu_stop()
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,lambda u,t,p,s,x,z:writes.append([p,s,x]) if p>=0x40000000 else None);u.hook_add(UC_HOOK_MEM_READ,lambda u,t,p,s,x,z:reads.append([p,s]) if p>=0x40000000 else None);u.emu_start(0x9fd5,0,count=100)
 valid=a==1 and c<=1 and v<65536;target=0x40010300+4*c;expected=(old&0xff0000ff)|((v<<8)&0x00ffff00)
 assert writes==([[target,4,expected]] if valid else[]) and reads==([[target,4]] if valid else[])
 assert u.reg_read(UC_ARM_REG_PC)==0x09000000 and u.reg_read(UC_ARM_REG_R0)==(0 if valid else 0x004a0001) and u.reg_read(UC_ARM_REG_R4)==0x12345678 and u.reg_read(UC_ARM_REG_SP)==0x2000f000
 rows.append(dict(input0=a,input1=c,value=v,initial_word=old,valid=valid,writes=writes,reads=reads))
(o/'replays.json').write_text(json.dumps(rows,indent=2)+'\n');(o/'pseudocode.md').write_text('''# Touch 16-bit register field update9FD4

Exact9FD4..A00C savesR4/LR. Accept onlyR0==1, unsignedR1<=1 and unsignedR2<65536; failuresreturnliteral004A0001 andrestoreframewithoutMMIOaccess. Successreadsonefreshwordat40010000+4*(R1+192),preservesitsbits31..24and7..0,placesR2inbits23..8,writesonewordtothesameaddress,returnszeroandrestoresR4/SP.

Twohundredfortyoriginal-instructionfixturesindependentlycheckthepredicate,onefreshread,maskedwrite,returnandframe. Theycoverboundaryvaluesandthreeinitialwordpatterns. Accessesareto syntheticmemory; physicaldevicebehavior,concurrencyandcallerreachabilityremainunresolved. No canonicaladmissionorCimplementation.
''');(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(source=dict(path=str(src),sha256=h(d)),runtime_span=[0x9fd4,0xa00c],fixtures=len(rows),files={p.name:h(p.read_bytes()) for p in sorted(o.iterdir())},accepted=False),indent=2)+'\n');print('PASS',len(rows),'field-update fixtures')
