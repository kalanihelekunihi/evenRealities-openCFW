from pathlib import Path
import hashlib,json,struct,itertools
from unicorn import *
from unicorn.arm_const import *
b=Path('g2/build/pseudocode-first/20260930T190500Z');o=Path('reviews/P2-touch-interrupt-priority-independent-review-1331/001/replay-output');o.mkdir(parents=True,exist_ok=False);src=b/'attempts/P2-touch-reset-pseudocode-108/001/touch.flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();word=lambda a:struct.unpack_from('<I',d,a-0x3300)[0];ext=word(0xa26c);sys=word(0xa270);rows=[]
for index,priority,old in itertools.product(range(-16,16),[0,1,2,3,255],[0,0xa5a5a5a5,0xffffffff]):
 raw=index&0xffffffff;shift=(raw&3)*8
 address=(ext+((raw>>2)+192)*4)&0xffffffff if index>=0 else (sys+((((((raw&15)-8)&0xffffffff)>>2)+6)*4)+4)&0xffffffff
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x10000);u.mem_write(0x3300,d);u.mem_map(0x20000000,0x10000);u.mem_map(address&~0xfff,0x1000);u.mem_write(address,old.to_bytes(4,'little'));u.mem_map(0x09000000,0x1000);u.reg_write(UC_ARM_REG_SP,0x2000f000);u.reg_write(UC_ARM_REG_LR,0x09000001);u.reg_write(UC_ARM_REG_R0,raw);u.reg_write(UC_ARM_REG_R1,priority);writes=[]
 def code(u,p,s,x):
  if p==0x09000000:u.emu_stop()
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,lambda u,t,a,s,v,x:writes.append([a,s,v]) if a==address else None);u.emu_start(0xa215,0,count=100)
 expected=(old&~(255<<shift))|(((priority<<6)&255)<<shift)
 assert writes==[[address,4,expected]] and u.reg_read(UC_ARM_REG_PC)==0x09000000 and u.reg_read(UC_ARM_REG_SP)==0x2000f000
 rows.append(dict(index=index,priority=priority,old=old,address=address,writes=writes))
(o/'replays.json').write_text(json.dumps(rows,indent=2)+'\n');(o/'pseudocode.md').write_text('''# Touch interrupt priority A214

Body A214..A26C is 88 instruction bytes, followed by two literal words. Signed nonnegative interrupt index selects word at external base + 4*(unsigned(index)>>2 + 192). Signed negative index selects system base + 4*(unsigned(u32((index&15)-8))>>2 + 6) + 4, with 32-bit modular arithmetic throughout. Both paths freshly load that word, select byte lane (index&3)*8, clear that byte, replace it with low byte of priority<<6, store and restore four-word frame. No index or priority guard occurs locally; caller supplies its guard.

Receipt-derived original-instruction fixtures cover indices minus16 through15, five priority inputs and three old words. Exact write address/value and frame restoration match the separate instruction-derived model. Negative indices outside architectural interrupt validity are included as arithmetic evidence, not valid interrupt claims. Physical priority semantics, invalid mappings and concurrent register changes remain unresolved. No canonical admission or C implementation.
''');(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(source=dict(path=str(src),sha256=h(d)),fixtures=len(rows),bases=dict(external=ext,system=sys),files={p.name:h(p.read_bytes()) for p in sorted(o.iterdir())},accepted=False),indent=2)+'\n');print('PASS',len(rows))
