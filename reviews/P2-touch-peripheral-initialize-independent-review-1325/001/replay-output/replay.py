from pathlib import Path
import hashlib,json,struct,itertools
from unicorn import *
from unicorn.arm_const import *
b=Path('g2/build/pseudocode-first/20260930T190500Z');o=Path('reviews/P2-touch-peripheral-initialize-independent-review-1325/001/replay-output');o.mkdir(parents=True,exist_ok=False);src=b/'attempts/P2-touch-reset-pseudocode-108/001/touch.flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();l={a:struct.unpack_from('<I',d,a-0x3300)[0] for a in range(0x36dc,0x3704,4)};ctx=l[0x36dc];base=l[0x36e4];irq=l[0x36fc];rows=[]
for flag,old in itertools.product([0,1,255],[0,0xa5a5a5a5,0xffffffff]):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x10000);u.mem_write(0x3300,d);u.mem_map(0x20000000,0x10000);u.mem_write(ctx+2,bytes([flag]));u.mem_map(0x40000000,0x100000);u.mem_map(base,0x1000);u.mem_map(0xe000e000,0x1000);u.mem_write(base,old.to_bytes(4,'little'));u.mem_write(base+0x6c,old.to_bytes(4,'little'));u.mem_map(0x09000000,0x1000);u.reg_write(UC_ARM_REG_SP,0x2000f000);u.reg_write(UC_ARM_REG_LR,0x09000001);calls=[];writes=[]
 def code(u,p,s,x):
  if p==0x09000000:u.emu_stop()
  elif p in [0x98f4,0xa2a8,0x9ad8,0x9af0]:calls.append(dict(pc=p,args=[u.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]]));u.reg_write(UC_ARM_REG_R0,0xffffffff);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,lambda u,t,a,s,v,x:writes.append([a,s,v]) if a<0x2000e000 or a>=0x40000000 else None);u.emu_start(0x3679,0,count=150)
 assert [c['pc'] for c in calls]==[0x98f4,0xa2a8,0x9ad8,0x9af0]
 assert calls[0]['args'][:3]==[base,l[0x36e0],ctx] and calls[1]['args'][:2]==[l[0x36ec],l[0x36e8]]
 assert calls[2]['args']==[base,l[0x36f0],16,ctx] and calls[3]['args']==[base,l[0x36f4],16,ctx]
 assert writes==[[ctx+0x44,4,l[0x36f8]],[irq+0x180,4,128],[irq,4,128],[base,4,old|0x80000000],[base+0x6c,4,old|(0x100 if flag else 0)]]
 assert u.reg_read(UC_ARM_REG_PC)==0x09000000 and u.reg_read(UC_ARM_REG_SP)==0x2000f000
 rows.append(dict(flag=flag,old=old,calls=calls,writes=writes,raw_return=u.reg_read(UC_ARM_REG_R0)))
(o/'replays.json').write_text(json.dumps(rows,indent=2)+'\n');(o/'pseudocode.md').write_text('''# Touch peripheral initialization 3678

Body 3678..36DA is 98 instruction bytes, excluding NOP and literal pool. Four deeper helpers are called in order: 98F4(base,configuration,context), A2A8(literal,literal), 9AD8(base,buffer1,16,context), 9AF0(base,buffer2,16,context). Their results are ignored. Store callback literal to context+44, write bit seven to interrupt base+180 then interrupt base, freshly read peripheral base and set bit31. Freshly read base+6C and context byte+2; if the byte is nonzero OR bit8, otherwise leave the read word unchanged. Store that word to base+6C and restore four-word frame. The zero-byte path does not clear bit8.

Nine original-instruction fixtures cover three context flags and three register patterns. Four deeper helpers are controlled with all-ones return and no memory effects. Literal-derived call arguments and all local writes/SP are checked; helper functionality, physical peripheral effects and concurrent access remain unresolved. No canonical admission or C implementation.
''');(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(source=dict(path=str(src),sha256=h(d)),fixtures=len(rows),literals={hex(a):hex(v) for a,v in l.items()},files={p.name:h(p.read_bytes()) for p in sorted(o.iterdir())},accepted=False),indent=2)+'\n');print('PASS',len(rows))
