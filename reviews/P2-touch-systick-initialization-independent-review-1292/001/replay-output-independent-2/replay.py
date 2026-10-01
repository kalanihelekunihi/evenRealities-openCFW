from pathlib import Path
import hashlib,json,itertools
from unicorn import *
from unicorn.arm_const import *
b=Path('g2/build/pseudocode-first/20260930T190500Z');o=Path('reviews/P2-touch-systick-initialization-independent-review-1292/001/replay-output-independent-2');o.mkdir(parents=True,exist_ok=False);src=b/'attempts/P2-touch-reset-pseudocode-108/001/touch.flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();rows=[]
for clock,reload,old in itertools.product([0,1,2,0xffffffff],[0,1,40,0xfffffe,0xffffff,0x1000000],[0,0xa5a5a5a5,0xffffffff]):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x10000);u.mem_write(0x3300,d);u.mem_map(0x20000000,0x10000);u.mem_write(0x20000f40,bytes([0xa5])*20);u.mem_map(0xe000e000,0x1000);u.mem_write(0xe000e010,old.to_bytes(4,'little'));u.mem_map(0x09000000,0x1000);u.reg_write(UC_ARM_REG_SP,0x2000f000);u.reg_write(UC_ARM_REG_LR,0x09000001);u.reg_write(UC_ARM_REG_R0,clock);u.reg_write(UC_ARM_REG_R1,reload);writes=[];pcs=[]
 def code(u,p,s,x):
  pcs.append(p)
  if p in [0x09000000,0xa65c,0xa682]:u.emu_stop()
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,lambda u,t,a,s,v,x:writes.append([a,s,v]) if a<0x2000e000 or a>=0xe0000000 else None);u.emu_start(0xa651,0,count=200)
 if reload>=0x1000000:assert u.reg_read(UC_ARM_REG_PC)==0xa65c and not writes
 else:
  chosen=(old&0xfffffffb)|((clock<<2)&4);expected=[[0x20000f40+4*i,4,0] for i in range(5)]+[[0x2000043c,4,0xa5f5],[0xe000e010,4,chosen],[0xe000e014,4,reload],[0xe000e018,4,0],[0xe000e010,4,chosen|2],[0xe000e010,4,chosen|3]]
  assert writes==expected and u.reg_read(UC_ARM_REG_PC)==0x09000000 and u.reg_read(UC_ARM_REG_SP)==0x2000f000
 rows.append(dict(clock_input=clock,reload=reload,initial_control=old,stop=u.reg_read(UC_ARM_REG_PC),writes=writes,pcs=pcs))
(o/'replays.json').write_text(json.dumps(rows,indent=2)+'\n');(o/'pseudocode.md').write_text('''# Touch SysTick initialization hierarchy

A650..A696 is 70 instruction bytes, excluding NOP and four literal words. Save R4..R6 and LR. Unsigned reload must be below 2^24; otherwise reach BKPT A65C before data writes. Clear five callback words at 20000F40..20000F54, then store literal A5F5 to 2000043C. Actual A638 freshly reads E000E010, replaces bit two with incoming R0 bit zero, stores once and preserves incoming R0 shifted left two. A638 body A638..A64A is 18 bytes, excluding NOP and literal.

Check retained reload below 2^24 again at A67E, with BKPT A682 on failure. Mask to 24 bits, store at E000E014, clear E000E018. Actual A620 freshly reads E000E010, sets bit one and stores; freshly reads it again, sets bit zero and stores. A620..A634 is 20 instruction bytes excluding literal. Restore saved frame and return. Fresh read order matters under concurrent hardware changes; fixtures use stable synthetic registers.

Receipt-derived fixtures cover four clock inputs, six reloads and three initial control patterns. Valid paths execute both helpers without substitution and check every non-stack write and frame restoration. Invalid reload stops before the first breakpoint; breakpoint continuation and between-check register mutation remain unresolved. These code-derived addresses identify standard system register accesses; physical timing and interrupt dispatch are not tested. No canonical admission or C implementation.
''');(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(source=dict(path=str(src),sha256=h(d)),fixtures=len(rows),files={p.name:h(p.read_bytes()) for p in sorted(o.iterdir())},accepted=False),indent=2)+'\n');print('PASS',len(rows))
