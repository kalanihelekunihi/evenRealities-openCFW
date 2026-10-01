from pathlib import Path
import json,struct,hashlib,itertools
from unicorn import *
from unicorn.arm_const import *
b=Path('g2/build/pseudocode-first/20260930T190500Z');o=Path('reviews/P2-touch-storage-init-wrapper-independent-review-1307/001/replay-output');o.mkdir(parents=True,exist_ok=False);src=b/'attempts/P2-touch-reset-pseudocode-108/001/touch.flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();l={a:struct.unpack_from('<I',d,a-0x3300)[0] for a in range(0x350c,0x3520,4)};rows=[]
for flag,status in itertools.product([0,1,255],[0,l[0x351c],1,0xffffffff]):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x10000);u.mem_write(0x3300,d);u.mem_map(0x20000000,0x10000);u.mem_write(l[0x350c],bytes([flag]));u.mem_map(0x09000000,0x1000);u.reg_write(UC_ARM_REG_SP,0x2000f000);u.reg_write(UC_ARM_REG_LR,0x09000001);calls=[];writes=[]
 def code(u,p,s,x):
  if p==0x09000000:u.emu_stop()
  elif p==0x8a38:calls.append([u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1)]);u.reg_write(UC_ARM_REG_R0,status);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,lambda u,t,a,s,v,x:writes.append([a,s,v&((1<<(8*s))-1)]) if a<0x2000e000 else None);u.emu_start(0x34d9,0,count=100)
 success=bool(flag) or status in [0,l[0x351c]];expected=[] if flag else [[l[0x3514]+8,4,l[0x3510]]]+([[l[0x350c],1,1]] if success else [])
 assert writes==expected and calls==([] if flag else [[l[0x3514],l[0x3518]]]) and u.reg_read(UC_ARM_REG_R0)==(0 if success else 1) and u.reg_read(UC_ARM_REG_PC)==0x09000000 and u.reg_read(UC_ARM_REG_SP)==0x2000f000
 rows.append(dict(initial_flag=flag,controlled_status=status,calls=calls,writes=writes,return_value=0 if success else 1))
(o/'replays.json').write_text(json.dumps(rows,indent=2)+'\n');(o/'pseudocode.md').write_text('''# Touch storage initialization wrapper 34D8

Body 34D8..350A is 50 instruction bytes, excluding NOP and five literal words. Freshly read the initialized flag byte; nonzero returns zero without calling the deeper helper. Otherwise store a literal at context+8, call 8A38(context, other literal). Status zero or the accepted-status literal sets flag one and returns zero. Other statuses leave the flag unchanged and return one. Restore the two-word frame. Twelve original-instruction fixtures cover three flag values and four helper statuses; the deeper helper is explicitly controlled without memory effects. Exact calls, writes, return and SP are checked. Storage behavior and concurrent initialization remain unresolved. No canonical admission or C implementation.
''');(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(source=dict(path=str(src),sha256=h(d)),fixtures=len(rows),literals={hex(a):hex(v) for a,v in l.items()},files={p.name:h(p.read_bytes()) for p in sorted(o.iterdir())},accepted=False),indent=2)+'\n');print('PASS',len(rows))
