from pathlib import Path
import hashlib,json,itertools
from unicorn import *
from unicorn.arm_const import *
b=Path('g2/build/pseudocode-first/20260930T190500Z');o=Path('reviews/P2-touch-descriptor-init-prefix-independent-review-1356/001/replay-output');o.mkdir(parents=True,exist_ok=False);src=b/'attempts/P2-touch-reset-pseudocode-108/001/touch.flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();rows=[]
for flags,fill in itertools.product(itertools.product([0,0xa5,0xff],repeat=3),[0,0xa5,0xff]):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x10000);u.mem_write(0x3300,d);u.mem_map(0x20000000,0x10000);u.mem_write(0x20002008,(0x20002100).to_bytes(4,'little')+(0x20002200).to_bytes(4,'little'));u.mem_write(0x20002200,(0x20002300).to_bytes(4,'little'));u.mem_write(0x20002100,bytes([fill])*0x80)
 for i,v in enumerate(flags):u.mem_write(0x20002323+i*0x3c,bytes([v]))
 u.reg_write(UC_ARM_REG_SP,0x2000f000);u.reg_write(UC_ARM_REG_R0,0x20002000);writes=[]
 def code(u,p,s,x):
  if p==0x4cb2:u.emu_stop()
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,lambda u,t,a,s,v,x:writes.append([a,s,v&((1<<(s*8))-1)]) if a<0x2000e000 else None);u.emu_start(0x4c7d,0,count=100)
 expected=[[0x20002174,1,0],[0x20002175,1,0]]+[[0x20002100+x,4,0] for x in [0,4,12,8]]+[[0x20002323+i*0x3c,1,v|6] for i,v in enumerate(flags)]
 assert writes==expected and u.reg_read(UC_ARM_REG_PC)==0x4cb2
 rows.append(dict(initial_flags=flags,initial_fill=fill,writes=writes))
(o/'replays.json').write_text(json.dumps(rows,indent=2)+'\n');(o/'pseudocode.md').write_text('''# Touch descriptor initialization prefix 4C7C

This packet covers the nonnull prefix4C7C..4CB2 only. Save a six-word frame and retain descriptor. Load context pointer from descriptor+8. Clear context bytes74/75 and words0,4,C,8 in that exact order. Load descriptor+12 pointer, then its first word as row base. Iterate exactly three rows with stride3C: freshly read row byte23, OR6, store it, advance. Stop at4CB2 before subsequent initialization. No deeper helper is reached by this prefix.

Eighty-one original-instruction fixtures vary each of three row bytes across0/A5/FF and initial contextfill across0/A5/FF. Exact ordered writes are independently modeled. Null descriptor, invalid pointers, remaining initialization, return/frame restoration and physical row meaning remain unresolved. This is prefix evidence, not full helper pseudocode or ownership closure. No canonical admission or C implementation.
''');(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(source=dict(path=str(src),sha256=h(d)),fixtures=len(rows),files={p.name:h(p.read_bytes()) for p in sorted(o.iterdir())},accepted=False),indent=2)+'\n');print('PASS',len(rows))
