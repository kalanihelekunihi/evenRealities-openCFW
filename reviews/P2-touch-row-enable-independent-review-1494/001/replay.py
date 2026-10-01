from pathlib import Path
import json,hashlib,itertools
from unicorn import *
from unicorn.arm_const import *
b=Path('g2/build/pseudocode-first/20260930T190500Z');o=Path('/Users/kalani/Repo/evenRealities-openCFW/reviews/P2-touch-row-enable-independent-review-1494/001');o.mkdir(parents=True,exist_ok=True);src=o/'touch.flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();rows=[]
for index,flag in itertools.product([0,1,2,3,255,0xffffffff],range(256)):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x10000);u.mem_write(0x3300,d);u.mem_map(0x20000000,0x10000);u.mem_map(0x09000000,0x1000);D=0x20002000;R=0x20002100
 u.mem_write(D+16,R.to_bytes(4,'little'))
 for i in range(3):u.mem_write(R+60*i+35,bytes([flag]))
 u.reg_write(UC_ARM_REG_R0,index);u.reg_write(UC_ARM_REG_R1,D);u.reg_write(UC_ARM_REG_SP,0x2000f000);u.reg_write(UC_ARM_REG_LR,0x09000001);reads=[];writes=[]
 u.hook_add(UC_HOOK_CODE,lambda u,p,s,x:u.emu_stop() if p==0x09000000 else None);u.hook_add(UC_HOOK_MEM_READ,lambda u,t,a,s,v,x:reads.append([a,s]));u.hook_add(UC_HOOK_MEM_WRITE,lambda u,t,a,s,v,x:writes.append([a,s,v]));u.emu_start(0x7ddf,0,count=30)
 expected=int(index<=2 and flag&6==6)
 assert u.reg_read(UC_ARM_REG_R0)==expected and u.reg_read(UC_ARM_REG_SP)==0x2000f000 and not writes and reads==([[D+16,4],[R+60*index+35,1]] if index<=2 else [])
 rows.append(dict(index=index,flag=flag,result=expected,reads=reads))
(o/'replays.json').write_text(json.dumps(rows,indent=2)+'\n');(o/'pseudocode.md').write_text('# Row enable at 7DDE\n\nThe 38-byte leaf [7DDE,7E04) returns zero without memory access for unsigned index greater than2. Otherwise read descriptor word+16 and row byte+35 at stride60. Return1 exactly when both bits1 and2 are set, else0. No stores,calls orstackchanges.\n\nThe1536 original-instruction fixtures exhaustall256flagbytes acrossvalidindices0/1/2 andthreeinvalidindices, checking exactreads and no writes. Pointervalidity andphysicalmeaningremainunresolved. No canonical admission or C implementation.\n');(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(source=dict(path=str(src),sha256=h(d)),fixtures=len(rows),files={p.name:h(p.read_bytes()) for p in sorted(o.iterdir())},accepted=False),indent=2)+'\n');print('PASS',len(rows))
