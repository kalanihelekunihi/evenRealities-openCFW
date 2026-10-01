from pathlib import Path
import json,hashlib,struct,itertools
from unicorn import *
from unicorn.arm_const import *
b=Path('g2/build/pseudocode-first/20260930T190500Z');o=Path('reviews/P2-touch-callback-exchange-a6a8-independent-review-1290/001/replay-output');o.mkdir(parents=True,exist_ok=False);src=b/'attempts/P2-touch-reset-pseudocode-108/001/touch.flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();base=struct.unpack_from('<I',d,0xa6bc-0x3300)[0];rows=[]
for index,new,old in itertools.product([0,1,2,3,4,5,0xffffffff],[0,0x35e5,0xffffffff],[0,0xa5a5a5a5,0xffffffff]):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x10000);u.mem_write(0x3300,d);u.mem_map(0x20000000,0x10000);u.mem_write(base,old.to_bytes(4,'little')*5);u.mem_map(0x09000000,0x1000);u.reg_write(UC_ARM_REG_LR,0x09000001);u.reg_write(UC_ARM_REG_R0,index);u.reg_write(UC_ARM_REG_R1,new);reads=[];writes=[]
 def code(u,p,s,x):
  if p==0x09000000:u.emu_stop()
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_READ,lambda u,t,a,s,v,x:reads.append([a,s]) if a>=0x20000000 else None);u.hook_add(UC_HOOK_MEM_WRITE,lambda u,t,a,s,v,x:writes.append([a,s,v]));u.emu_start(0xa6a9,0,count=30)
 assert u.reg_read(UC_ARM_REG_PC)==0x09000000 and u.reg_read(UC_ARM_REG_R0)==(old if index<=4 else 0)
 assert reads==([[base+4*index,4]] if index<=4 else []) and writes==([[base+4*index,4,new]] if index<=4 else [])
 rows.append(dict(index=index,new=new,old=old,return_value=u.reg_read(UC_ARM_REG_R0),reads=reads,writes=writes))
(o/'replays.json').write_text(json.dumps(rows,indent=2)+'\n');(o/'pseudocode.md').write_text('''# Touch callback slot exchange A6A8

Body A6A8..A6BA is 18 instruction bytes; adjacent NOP and literal are excluded. If unsigned index exceeds four, return zero without data access. Otherwise load the old word from literal base plus four times index, store incoming R1 to the same slot, and return the old word in R0. No stack frame, indirect call or interrupt exclusion occurs. Concurrent atomicity is not established.

Sixty-three original-instruction fixtures cover all five valid slots, two invalid indices, three new words and three old words. Exact reads, writes and returns match the separate model. This establishes exchange behavior, not callback target validity or dispatch. No canonical admission or C implementation.
''');(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(source=dict(path=str(src),sha256=h(d)),fixtures=len(rows),base=base,files={p.name:h(p.read_bytes()) for p in sorted(o.iterdir())},accepted=False),indent=2)+'\n');print('PASS',len(rows),hex(base))
