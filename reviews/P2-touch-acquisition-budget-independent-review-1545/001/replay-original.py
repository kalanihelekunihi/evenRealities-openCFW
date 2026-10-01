from pathlib import Path
import hashlib,json,itertools
from unicorn import *
from unicorn.arm_const import *
b=Path('g2/build/pseudocode-first/20260930T190500Z');o=Path('/Users/kalani/Repo/evenRealities-openCFW/reviews/P2-touch-acquisition-budget-independent-review-1545/001/run');o.mkdir(parents=True,exist_ok=True);src=b/'attempts/P2-touch-reset-pseudocode-108/001/touch.flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();rows=[]
for index,mode,seed,factor in itertools.product(range(3),range(4),[0,1,65535],[0,1,255]):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x10000);u.mem_write(0x3300,d);u.mem_map(0x20000000,0x10000);u.mem_map(0x09000000,0x1000);D=0x20002000;C=D+256;R=C+256;P=R+1024;record=R+144*index;fields={offset:(seed+offset*37)&65535 for offset in [48,50,62,64,66,68]};byteset={77:(seed+17)&255,83:(seed+29)&255};width=seed;extra=(seed+123)&65535
 for a,v in [(D+8,C),(D+12,R),(record,P)]:u.mem_write(a,v.to_bytes(4,'little'))
 for offset,v in fields.items():u.mem_write(C+offset,v.to_bytes(2,'little'))
 for offset,v in byteset.items():u.mem_write(C+offset,bytes([v]))
 u.mem_write(P+14,width.to_bytes(2,'little'));u.mem_write(P+33,bytes([mode|0xa0]));u.mem_write(P+44,extra.to_bytes(2,'little'));u.mem_write(record+132,bytes([factor]))
 for r,v in [(UC_ARM_REG_R0,index),(UC_ARM_REG_R1,0xdeadbeef),(UC_ARM_REG_R2,D),(UC_ARM_REG_SP,0x2000f000),(UC_ARM_REG_LR,0x09000001)]:u.reg_write(r,v)
 pcs=[];writes=[]
 def code(u,p,s,x):
  pcs.append(p)
  if p==0x09000000:u.emu_stop()
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,lambda u,t,a,s,v,x:writes.append([a,s,v]));u.emu_start(0x7289,0,count=10000)
 base=fields[48]+fields[50]+byteset[83];pair=fields[62]+fields[66] if mode==2 else fields[64]+fields[68];raw=(base+(width>>2)*pair+width*(byteset[77]+extra))&0xffffffff
 if mode==2:raw=(raw*2)&0xffffffff
 numerator=(raw*factor)&0xffffffff;expected=((numerator//46)*5)&0xffffffff
 assert u.reg_read(UC_ARM_REG_R0)==expected and u.reg_read(UC_ARM_REG_PC)==0x09000000 and u.reg_read(UC_ARM_REG_SP)==0x2000f000 and 0xa6c0 in pcs
 assert all(0x2000eff0-128<=w[0]<0x2000f000 for w in writes)
 rows.append(dict(index=index,mode=mode,seed=seed,factor=factor,context_halfwords=fields,context_bytes=byteset,width=width,extra=extra,numerator=numerator,result=expected))
body=d[0x3f88:0x3ff8];ins=list(Cs(CS_ARCH_ARM,CS_MODE_THUMB|CS_MODE_MCLASS).disasm(body,0x7288));assert sum(i.size for i in ins)==112
(o/'disassembly.txt').write_text('\n'.join(f'{i.address:04X}: {i.mnemonic} {i.op_str}' for i in ins)+'\n');(o/'replays.json').write_text(json.dumps(rows,indent=2)+'\n');(o/'pseudocode.md').write_text(f'''# Acquisition budget at 7288

The exact 112-byte body [7288,72F8) has {len(ins)} instructions. R0 selects a 144-byte record from descriptor word +12; R2 is the descriptor. R1 is overwritten before use. Resolve row through record word +0 and context through descriptor word +8. Let width be row halfword +14 and mode be row byte +33 & 3.

Compute base = context halfword +48 + context halfword +50 + context byte +83. Add (width >> 2) times a halfword pair: offsets 62 and 66 for mode 2, otherwise offsets 64 and 68. Then add width times (context byte +77 + row halfword +44). For mode 2, double the resulting wrapped word. Multiply by record byte +132 modulo 2^32, divide unsigned by 46 using original A6C0, then return quotient times 5 modulo 2^32. All intermediate machine additions and multiplications wrap at 32 bits. Restore the 24-byte frame.

{len(rows)} original-instruction fixtures vary all three indices, all four modes, independent patterned fields, width extrema and factors 0/1/255. Original division executes. Fixtures verify quotient and wrapped result, return and restored frame, and absence of non-stack writes. No sensor acquisition occurs in this body; the historical acquisition boundary was a timing calculation. Index and pointer validity are caller obligations. Physical time units remain unresolved. No canonical admission or C implementation.
''');(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(source=dict(path=str(src),sha256=h(d)),body_sha256=h(body),instructions=len(ins),fixtures=len(rows),files={p.name:h(p.read_bytes()) for p in sorted(o.iterdir())},accepted=False),indent=2)+'\n');print('PASS',len(rows),len(ins))
