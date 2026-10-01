from pathlib import Path
import json,hashlib,itertools
from unicorn import *
from unicorn.arm_const import *
b=Path('/Users/kalani/Repo/evenRealities-openCFW/g2/build/pseudocode-first/20260930T190500Z');o=Path('/Users/kalani/Repo/evenRealities-openCFW/reviews/P2-touch-packet-pin-mask-prefix-independent-review-1468/001/replay-output');o.mkdir(parents=True,exist_ok=False);src=b/'attempts/P2-touch-reset-pseudocode-108/001/touch.flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();rows=[]
for n,m,shift in itertools.product([0,1,3],[0,1,3],[0,1,31,32,255]):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x10000);u.mem_write(0x3300,d);u.mem_map(0x20000000,0x10000);D=0x20002000;F=0x20002100;C=0x20002200;A=0x20002300;B=0x20002400
 for off,v in [(0,F),(8,C),(20,A),(24,B)]:u.mem_write(D+off,v.to_bytes(4,'little'))
 u.mem_write(F+12,n.to_bytes(2,'little'));u.mem_write(F+44,bytes([m]))
 vals=[]
 for count,base in [(n,A),(m,B)]:
  for i in range(count):v=(shift+i)&255;vals.append(v);u.mem_write(base+8*i+5,bytes([v]))
 u.reg_write(UC_ARM_REG_R0,1);u.reg_write(UC_ARM_REG_R1,D);u.reg_write(UC_ARM_REG_SP,0x2000f000);u.hook_add(UC_HOOK_CODE,lambda u,p,s,x:u.emu_stop() if p==0x56f4 else None);u.emu_start(0x56a5,0,count=300)
 expected=0
 for v in vals:expected|=(1<<v)&0xffffffff if v<32 else 0
 assert u.reg_read(UC_ARM_REG_R1)==expected and u.reg_read(UC_ARM_REG_SP)==0x2000efb8 and u.reg_read(UC_ARM_REG_PC)==0x56f4
 rows.append(dict(first_count=n,second_count=m,shift=shift,pins=vals,mask=expected))
(o/'replays.json').write_text(json.dumps(rows,indent=2)+'\n');(o/'pseudocode.md').write_text('# Packet pin-mask prefix at 56A4\n\nThe prefix [56A4,56F4) is 80 instruction bytes. Save a nine-word frame and allocate 36 scratch bytes. Start a zero mask. Traverse descriptor word +20 records with stride 8, count from configuration halfword +12; OR 1 shifted by record byte +5. Then traverse descriptor word +24 records with the same stride, count from configuration byte +44, and OR the corresponding shifts. Register shifts at least 32 contribute zero. Retain descriptor/context pointers for the remaining body.\n\nForty-five original-instruction fixtures check zero/nonzero counts, two-list union, shift boundaries, stop PC and 72-byte frame. This is only a bounded prefix; the packet-building suffix and full return are unresolved. No canonical admission or C implementation.\n');(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(source=dict(path=str(src),sha256=h(d)),fixtures=len(rows),files={p.name:h(p.read_bytes()) for p in sorted(o.iterdir())},accepted=False),indent=2)+'\n');print('PASS',len(rows))
