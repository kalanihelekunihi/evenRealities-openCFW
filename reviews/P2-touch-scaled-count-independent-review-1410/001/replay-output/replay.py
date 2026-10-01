from pathlib import Path
import json,hashlib,itertools,struct
from unicorn import *
from unicorn.arm_const import *
b=Path('g2/build/pseudocode-first/20260930T190500Z');o=Path('reviews/P2-touch-scaled-count-independent-review-1410/001/replay-output');o.mkdir(parents=True,exist_ok=False);src=b/'attempts/P2-touch-reset-pseudocode-108/001/touch.flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();rows=[]
values=[0,1,16383,16384,16385,65535,65536,0x3fffffff,0x40000000,0x80000000,0xffffffff]
for value,factor in itertools.product(values,values):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x10000);u.mem_write(0x3300,d);u.mem_map(0x20000000,0x10000);u.mem_map(0x09000000,0x1000);u.mem_write(0x20002008,(0x20002100).to_bytes(4,'little'));u.mem_write(0x2000212c,factor.to_bytes(4,'little'));u.reg_write(UC_ARM_REG_R0,value);u.reg_write(UC_ARM_REG_R1,0x20002000);u.reg_write(UC_ARM_REG_SP,0x2000f000);u.reg_write(UC_ARM_REG_LR,0x09000001);pcs=[];writes=[]
 def hook(u,p,s,x):
  pcs.append(p)
  if p==0x09000000:u.emu_stop()
 u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_WRITE,lambda u,t,a,s,v,x:writes.append([a,s,v]));u.emu_start(0x5d71,0,count=30)
 scaled=((value*factor)&0xffffffff)>>14;expected=0 if scaled==0 else min(scaled-1,65535)
 assert u.reg_read(UC_ARM_REG_R0)==expected and u.reg_read(UC_ARM_REG_SP)==0x2000f000 and u.reg_read(UC_ARM_REG_PC)==0x09000000 and not writes
 rows.append(dict(value=value,factor=factor,scaled=scaled,result=expected,pcs=pcs))
assert struct.unpack_from('<I',d,0x5d8c-0x3300)[0]==65535
(o/'replays.json').write_text(json.dumps(rows,indent=2)+'\n');(o/'pseudocode.md').write_text('# Scaled count helper at 5D70\n\nRead the context pointer at descriptor + 8, then its word at offset 44. Multiply the input by that word with unsigned 32-bit wraparound and shift right by 14. If the scaled value is zero, return zero. Otherwise subtract one and return the smaller of that result and 65535. There are no stores, calls or stack changes.\n\nThe instruction span is [5D70,5D8A), 26 bytes. The halfword at 5D8A is alignment NOP; the word at 5D8C is the 65535 literal. The 121 original-instruction fixtures check wraparound, zero, decrement and saturation against an independent arithmetic model. Pointer validity and physical meaning remain unresolved. This packet provides private pseudocode evidence without canonical admission or C implementation.\n');(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(source=dict(path=str(src),sha256=h(d)),fixtures=len(rows),files={p.name:h(p.read_bytes()) for p in sorted(o.iterdir())},accepted=False),indent=2)+'\n');print('PASS',len(rows))
