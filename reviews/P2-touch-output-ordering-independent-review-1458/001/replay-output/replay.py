from pathlib import Path
import json,hashlib,struct,itertools
from unicorn import *
from unicorn.arm_const import *
b=Path('/Users/kalani/Repo/evenRealities-openCFW/g2/build/pseudocode-first/20260930T190500Z');o=Path('/Users/kalani/Repo/evenRealities-openCFW/reviews/P2-touch-output-ordering-independent-review-1458/001/replay-output');o.mkdir(parents=True,exist_ok=False);src=b/'attempts/P2-touch-reset-pseudocode-108/001/touch.flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();L=struct.unpack_from('<I',d,0x5184-0x3300)[0];table=d[L-0x3300:L-0x3300+56];rows=[]
for mode,fill in itertools.product([0,1,2,3,255],[0,0xa5,0xff]):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x10000);u.mem_write(0x3300,d);u.mem_map(0x20000000,0x10000);u.mem_map(0x09000000,0x1000);D=0x20002000;C=0x20002100;O=0x20002200
 u.mem_write(D+8,C.to_bytes(4,'little'));u.mem_write(D+36,O.to_bytes(4,'little'));cb=bytearray([fill]*128);cb[116]=mode;u.mem_write(C,bytes(cb));u.mem_write(O,bytes([fill])*256);u.reg_write(UC_ARM_REG_R0,D);u.reg_write(UC_ARM_REG_SP,0x2000f000);u.reg_write(UC_ARM_REG_LR,0x09000001);pcs=[]
 def code(u,p,s,x):
  pcs.append(p)
  if p==0x09000000:u.emu_stop()
 u.hook_add(UC_HOOK_CODE,code);u.emu_start(0x50e5,0,count=2000)
 cb[99:113]=bytes([255])*14;cb[104]=0;cb[98]=3 if mode in [1,2] else 2;cb[107]=2 if mode in [1,2] else 1
 if mode==1:cb[99]=1
 if mode==2:cb[100]=1
 expected=bytearray([fill]*256);mapping={5:0,8:cb[107]}
 if mode==1:mapping[0]=1
 if mode==2:mapping[1]=1
 for i,j in mapping.items():expected[112+4*j:116+4*j]=table[4*i:4*i+4]
 assert bytes(u.mem_read(C,128))==cb and bytes(u.mem_read(O,256))==expected and u.reg_read(UC_ARM_REG_R0)==0 and u.reg_read(UC_ARM_REG_SP)==0x2000f000 and u.reg_read(UC_ARM_REG_PC)==0x09000000 and 0xaa2c in pcs
 rows.append(dict(mode=mode,fill=fill,context=cb.hex(),output=expected.hex(),mapping=mapping))
(o/'replays.json').write_text(json.dumps(rows,indent=2)+'\n');(o/'pseudocode.md').write_text('# Output ordering at 50E4\n\nThe 158-byte code body [50E4,5182) is followed by alignment NOP and table pointer at 5184. Copy the authenticated 14-word table into a 56-byte stack buffer using original AA2C. Set context bytes +99 through +112 to 255, then set +104 to zero. Context mode +116 equal 1 assigns mapping byte +99 to 1; mode 2 assigns +100 to 1; other modes leave both 255. Assign +107 to 2 for modes 1/2, otherwise 1, and set count byte +98 to that value plus one.\n\nFor each of 14 mapping bytes that is not 255, copy the corresponding scratch table word into output +112 plus four times the mapping value. Return zero and restore the 80-byte frame. Fifteen original-instruction fixtures check entire context/output buffers, exact modes and original copy execution. Prior mapping bytes are overwritten before use. Physical meanings and global ownership remain unresolved. No canonical admission or C implementation.\n');(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(source=dict(path=str(src),sha256=h(d)),fixtures=len(rows),table_pointer=L,table_sha256=h(table),files={p.name:h(p.read_bytes()) for p in sorted(o.iterdir())},accepted=False),indent=2)+'\n');print('PASS',len(rows))
