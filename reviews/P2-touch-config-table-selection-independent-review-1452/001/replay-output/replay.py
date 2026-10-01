from pathlib import Path
import json,hashlib,struct,itertools
from unicorn import *
from unicorn.arm_const import *
b=Path('/Users/kalani/Repo/evenRealities-openCFW/g2/build/pseudocode-first/20260930T190500Z');o=Path('/Users/kalani/Repo/evenRealities-openCFW/reviews/P2-touch-config-table-selection-independent-review-1452/001/replay-output');o.mkdir(parents=True,exist_ok=False);src=b/'attempts/P2-touch-reset-pseudocode-108/001/touch.flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();L={a:struct.unpack_from('<I',d,a-0x3300)[0] for a in range(0x5368,0x5378,4)};rows=[]
for first,second,third,special in itertools.product([0,1,2],[0,1,2],[0,1,2],[0,5,255]):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x10000);u.mem_write(0x3300,d);u.mem_map(0x20000000,0x10000);u.mem_map(0x09000000,0x1000);D=0x20002000;C=0x20002100;O=0x20002200
 u.mem_write(D+8,C.to_bytes(4,'little'));u.mem_write(D+36,O.to_bytes(4,'little'));u.mem_write(O,bytes([0xa5])*256)
 for off,v in [(90,first),(91,second),(92,third),(117,special)]:u.mem_write(C+off,bytes([v]))
 u.reg_write(UC_ARM_REG_R0,D);u.reg_write(UC_ARM_REG_SP,0x2000f000);u.reg_write(UC_ARM_REG_LR,0x09000001);u.hook_add(UC_HOOK_CODE,lambda u,p,s,x:u.emu_stop() if p==0x09000000 else None);u.emu_start(0x52bd,0,count=200)
 expected=bytearray([0xa5]*256);expected[144:228]=d[L[0x5368]-0x3300:L[0x5368]-0x3300+84]
 for flag,off,lit in [(first,144,0x536c),(second,172,0x5370),(third,200,0x5374)]:
  if flag==1:expected[off:off+28]=d[L[lit]-0x3300:L[lit]-0x3300+28]
 if special==5:expected[188:192]=(int.from_bytes(expected[188:192],'little')|256).to_bytes(4,'little')
 ret=int.from_bytes(expected[212:216],'little') if third==1 else D
 assert bytes(u.mem_read(O,256))==expected and u.reg_read(UC_ARM_REG_R0)==ret and u.reg_read(UC_ARM_REG_SP)==0x2000f000 and u.reg_read(UC_ARM_REG_PC)==0x09000000
 rows.append(dict(flags=[first,second,third],special=special,return_value=ret,output=expected.hex()))
(o/'replays.json').write_text(json.dumps(rows,indent=2)+'\n');(o/'pseudocode.md').write_text('# Configuration table selection at 52BC\n\nThe 172-byte body [52BC,5368) is followed by four literal pointers. Copy 84 authenticated table bytes from the first literal to output +144 through descriptor word +36. If context bytes +90, +91 or +92 equal exactly 1, replace respective 28-byte rows at output +144, +172 or +200 from the three other literal tables. Context byte +117 equal 5 ORs 256 into output word +188, after second-row replacement and before third-row replacement.\n\nNo calls occur. R0 retains the incoming descriptor unless the third replacement executes; then it retains the fourth copied word of that table. The 81 fixtures check all output bytes, literal-backed tables, exact-equality conditions, returned register and frame restoration. Table field meanings and global ownership remain unresolved. No canonical admission or C implementation.\n');(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(source=dict(path=str(src),sha256=h(d)),fixtures=len(rows),literals=L,files={p.name:h(p.read_bytes()) for p in sorted(o.iterdir())},accepted=False),indent=2)+'\n');print('PASS',len(rows))
