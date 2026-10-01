from pathlib import Path
import json,hashlib,struct,itertools
from unicorn import *
from unicorn.arm_const import *
b=Path('g2/build/pseudocode-first/20260930T190500Z');o=Path('reviews/P2-touch-vector-exchange-independent-review-1333/001/replay-output');o.mkdir(parents=True,exist_ok=False);src=b/'attempts/P2-touch-reset-pseudocode-108/001/touch.flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();word=lambda a:struct.unpack_from('<I',d,a-0x3300)[0];sys=word(0xa29c);ram=word(0xa2a0);flash=word(0xa2a4);rows=[]
for index,callback,relocated in itertools.product([-15,-1,0,7,15],[0,0x3625,0xffffffff],[0,1]):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x10000);u.mem_write(0x3300,d);u.mem_map(0x20000000,0x10000);u.mem_map(0xe000e000,0x1000);u.mem_write(sys+8,(ram if relocated else 0).to_bytes(4,'little'));u.mem_map(0x09000000,0x1000);u.reg_write(UC_ARM_REG_LR,0x09000001);u.reg_write(UC_ARM_REG_R0,index&0xffffffff);u.reg_write(UC_ARM_REG_R1,callback);address=(ram if relocated else flash)+4*(index+16);old=0xa5a5a5a5 if relocated else int.from_bytes(u.mem_read(address,4),'little')
 if relocated:u.mem_write(address,old.to_bytes(4,'little'))
 writes=[]
 def code(u,p,s,x):
  if p in [0x09000000,0xa298]:u.emu_stop()
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,lambda u,t,a,s,v,x:writes.append([a,s,v]));u.emu_start(0xa275,0,count=50)
 if relocated and not callback:assert u.reg_read(UC_ARM_REG_PC)==0xa298 and not writes
 else:assert u.reg_read(UC_ARM_REG_PC)==0x09000000 and u.reg_read(UC_ARM_REG_R0)==old and writes==([[address,4,callback]] if relocated else [])
 rows.append(dict(index=index,callback=callback,relocated=relocated,address=address,old=old,stop=u.reg_read(UC_ARM_REG_PC),writes=writes))
(o/'replays.json').write_text(json.dumps(rows,indent=2)+'\n');(o/'pseudocode.md').write_text('''# Touch vector exchange A274

Body A274..A29C is 40 instruction bytes, followed by three literals. Freshly read system base+8 and compare against RAM vector base. If unequal, load and return the word at flash vector base + 4*u32(index+16), ignoring callback input. If equal, zero callback reaches BKPT A298; otherwise load old RAM vector word at the same modular index, store callback and return old word. No stack frame or index guard exists. Breakpoint continuation branches into the write path but is not executed by these fixtures.

Thirty original-instruction fixtures cover five signed indices, three callback words and both vector-base cases. Exact destination writes, returned old words and guard stops are checked; physical vector activation, architectural index validity and concurrent access remain unresolved. No canonical admission or C implementation.
''');(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(source=dict(path=str(src),sha256=h(d)),fixtures=len(rows),literals=dict(system=sys,ram=ram,flash=flash),files={p.name:h(p.read_bytes()) for p in sorted(o.iterdir())},accepted=False),indent=2)+'\n');print('PASS',len(rows))
