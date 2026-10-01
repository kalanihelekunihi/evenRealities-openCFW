from pathlib import Path
import hashlib,json,itertools
from unicorn import *
from unicorn.arm_const import *
b=Path('g2/build/pseudocode-first/20260930T190500Z');o=Path('reviews/P2-touch-descriptor-init-middle-independent-review-1359/001/replay-output');o.mkdir(parents=True,exist_ok=False);src=b/'attempts/P2-touch-reset-pseudocode-108/001/touch.flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();rows=[]
for flags,fill in itertools.product(itertools.product([0,0xa5,0xff],repeat=3),[0,0xa5,0xff]):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x10000);u.mem_write(0x3300,d);u.mem_map(0x20000000,0x10000);u.mem_write(0x20002000,(0x20002400).to_bytes(4,'little'));u.mem_write(0x20002400,bytes(range(64)));u.mem_write(0x20002008,(0x20002100).to_bytes(4,'little')+(0x20002200).to_bytes(4,'little'));u.mem_write(0x20002200,(0x20002300).to_bytes(4,'little'));u.mem_write(0x20002100,bytes([fill])*0x80)
 for i,v in enumerate(flags):u.mem_write(0x20002323+i*0x3c,bytes([v]))
 u.reg_write(UC_ARM_REG_SP,0x2000f000);u.reg_write(UC_ARM_REG_R0,0x20002000);writes=[]
 def code(u,p,s,x):
  if p==0x4d3e:u.emu_stop()
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,lambda u,t,a,s,v,x:writes.append([a,s,v&((1<<(s*8))-1)]) if a<0x2000e000 else None);u.emu_start(0x4c7d,0,count=300)
 expected=[[0x20002174,1,0],[0x20002175,1,0]]+[[0x20002100+x,4,0] for x in [0,4,12,8]]+[[0x20002323+i*0x3c,1,v|6] for i,v in enumerate(flags)]
 word=lambda a:int.from_bytes(d[a-0x3300:a-0x3300+4],'little')
 expected += [[0x2000211c,4,0],[0x2000212c,4,word(0x4da8)],[0x20002114,4,0],[0x2000214c,1,0],[0x20002157,1,47],[0x20002158,1,45],[0x20002159,1,49],[0x20002130,2,0x1716],[0x20002132,2,0x1918],[0x20002153,1,52],[0x20002154,1,53],[0x2000213c,2,word(0x4dac)&65535],[0x2000214e,1,0],[0x2000214f,1,255],[0x20002150,1,142],[0x20002151,1,1]]
 for i,v in enumerate(flags):expected += [[0x20002323+i*0x3c,1,(v|6)|8],[0x20002323+i*0x3c,1,(v|6)|24]]
 assert writes==expected and u.reg_read(UC_ARM_REG_PC)==0x4d3e
 rows.append(dict(initial_flags=flags,initial_fill=fill,writes=writes))
(o/'replays.json').write_text(json.dumps(rows,indent=2)+'\n');(o/'pseudocode.md').write_text('# Touch descriptor initialization middle\n\nExtend the nonnull original prefix through4D3E, before the following halfword copies and deeper calls. After1355 header/row operations, clear context1C/14/4C; put literal4DA8 at2C. Copy configbytes2F→context57,2D→58,31→59,34→53,35→54; confighalfwords16→30 and18→32. Put lowhalf literal4DAC at3C. Set contextbytes4E=0,4F=255,50=142,51=1.\n\nTraverse the same three rows with stride3C again. Zero rowhalfword4 sets flagbyte23 bit3; zero rowhalfword6 sets bit4, each through a fresh read and ordered byte write. Fixture rowhalfwords are suppliedzero. Eighty-one original-instruction fixtures retain priorflag/fill variation and use a deterministic configbytepattern to verify exactcopyoffsets and all orderedwrites. Nonzero rowhalfword branches, null path, remainder, return and hardware semantics remain outstanding. This is bounded partial pseudocode, not full helper coverage. No canonical admission or C implementation.\n');(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(source=dict(path=str(src),sha256=h(d)),fixtures=len(rows),files={p.name:h(p.read_bytes()) for p in sorted(o.iterdir())},accepted=False),indent=2)+'\n');print('PASS',len(rows))
