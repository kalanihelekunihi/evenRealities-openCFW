from pathlib import Path
import json,hashlib,struct
from unicorn import *
from unicorn.arm_const import *
b=Path('g2/build/pseudocode-first/20260930T190500Z');o=Path('reviews/P2-touch-tick-callback-independent-review-1296/001/replay-output');o.mkdir(parents=True,exist_ok=False);src=b/'attempts/P2-touch-reset-pseudocode-108/001/touch.flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();address=struct.unpack_from('<I',d,0x35f0-0x3300)[0];rows=[]
for old in [0,1,0x7fffffff,0xfffffffe,0xffffffff]:
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x10000);u.mem_write(0x3300,d);u.mem_map(0x20000000,0x10000);u.mem_write(address,old.to_bytes(4,'little'));u.mem_map(0x09000000,0x1000);u.reg_write(UC_ARM_REG_LR,0x09000001);u.reg_write(UC_ARM_REG_R0,0x12345678);reads=[];writes=[]
 def code(u,p,s,x):
  if p==0x09000000:u.emu_stop()
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_READ,lambda u,t,a,s,v,x:reads.append([a,s]) if a>=0x20000000 else None);u.hook_add(UC_HOOK_MEM_WRITE,lambda u,t,a,s,v,x:writes.append([a,s,v]));u.emu_start(0x35e5,0,count=20);expected=(old+1)&0xffffffff
 assert u.reg_read(UC_ARM_REG_PC)==0x09000000 and u.reg_read(UC_ARM_REG_R0)==0x12345678 and reads==[[address,4]] and writes==[[address,4,expected]]
 rows.append(dict(old=old,new=expected,reads=reads,writes=writes))
(o/'replays.json').write_text(json.dumps(rows,indent=2)+'\n');(o/'pseudocode.md').write_text('''# Touch tick callback 35E4

Original 3638 installs odd pointer 35E5 in callback slot zero. Its Thumb body 35E4..35EE is ten instruction bytes, excluding adjacent NOP and literal. Read word at literal address 200008E8, increment modulo 2^32, store it and return through LR. R0 remains unchanged. No frame, helper or interrupt exclusion is used. Five original-instruction fixtures verify exact read/write and overflow behavior. Supplied callback entry proves its local behavior; timer dispatch, tick duration and concurrent access remain unresolved. No canonical admission or C implementation.
''');(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(source=dict(path=str(src),sha256=h(d)),fixtures=len(rows),address=address,files={p.name:h(p.read_bytes()) for p in sorted(o.iterdir())},accepted=False),indent=2)+'\n');print('PASS',len(rows),hex(address))
