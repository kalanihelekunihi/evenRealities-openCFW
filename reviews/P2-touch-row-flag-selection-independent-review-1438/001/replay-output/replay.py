from pathlib import Path
import json,hashlib,itertools
from unicorn import *
from unicorn.arm_const import *
b=Path('g2/build/pseudocode-first/20260930T190500Z');o=Path('reviews/P2-touch-row-flag-selection-independent-review-1438/001/replay-output');o.mkdir(parents=True,exist_ok=False);src=b/'attempts/P2-touch-reset-pseudocode-108/001/touch.flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();rows=[]
for mode,width,percent,shift,kind,scale,offset,extra,codebyte in itertools.product([0,1,10],[0,8,65535],[0,255],[0,32],[0,2],[0,65535],[0,255],[0,65535],[0,131]):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x10000);u.mem_write(0x3300,d);u.mem_map(0x20000000,0x10000);u.mem_map(0x09000000,0x1000);R=0x20002000;D=0x20002100;C=0x20002200;W=0x20002300
 for a,v in [(R,W),(D+8,C)]:u.mem_write(a,v.to_bytes(4,'little'))
 for a,v in [(W+14,width),(W+44,extra),(C+60,scale)]:u.mem_write(a,v.to_bytes(2,'little'))
 for a,v in [(R+122,mode),(R+136,kind),(R+135,percent),(W+56,codebyte),(C+77,offset),(C+78,shift)]:u.mem_write(a,bytes([v]))
 u.reg_write(UC_ARM_REG_R0,R);u.reg_write(UC_ARM_REG_R1,D);u.reg_write(UC_ARM_REG_SP,0x2000f000);u.reg_write(UC_ARM_REG_LR,0x09000001);calls=[]
 def code(u,p,s,x):
  if p==0x09000000:u.emu_stop()
  elif p in [0xa6c0,0xa7cc]:
   a=u.reg_read(UC_ARM_REG_R0);den=u.reg_read(UC_ARM_REG_R1);calls.append([p,a,den]);u.reg_write(UC_ARM_REG_R0,a//den if den else 0);u.reg_write(UC_ARM_REG_R1,a%den if den else 0);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,code);u.emu_start(0x6295,0,count=300)
 total=min(offset+extra,65535);bit_scale=(1<<max(1,scale.bit_length()))-1;count=(((codebyte&127)&3)+shift+1)&255;factor=(1<<count)&0xffffffff if count<32 else 0;base=8 if mode in [1,10] else 4;prod=(width*percent)&0xffffffff;quot=prod//100;cap=(width-base)&0xffffffff;budget=min(quot>>shift if shift<32 else 0,cap>>shift if shift<32 else 0);valid=int(factor<=budget)
 if kind!=2:
  if total<bit_scale:valid=0
  if kind==0 and total%bit_scale:valid=0
 expected=valid|4;ec=[[0xa6c0,prod,100]]+([[0xa7cc,total,bit_scale]] if kind==0 else [])
 assert calls==ec and u.reg_read(UC_ARM_REG_R0)==expected and u.reg_read(UC_ARM_REG_SP)==0x2000f000 and u.reg_read(UC_ARM_REG_PC)==0x09000000
 rows.append(dict(mode=mode,width=width,percent=percent,shift=shift,kind=kind,scale=scale,offset=offset,extra=extra,codebyte=codebyte,result=expected,calls=calls))
(o/'replays.json').write_text(json.dumps(rows,indent=2)+'\n');(o/'pseudocode.md').write_text('# Row flag selection at 6294\n\nThe 150-byte code body [6294,632A) is followed by alignment NOP and literal 65535 at 632C. Sum row halfword +44 and context byte +77, saturating at 65535. Clear bit 7 of row byte +56, read context byte +78 as shift, record byte +136 as decision mode and +135 as percentage. Original 6220 yields the context halfword +60 scale; original 6262 yields a shift factor from the cleared row byte and shift.\n\nOriginal 6270 receives row halfword +14, base 8 for record mode +122 equal to 1 or 10, otherwise 4, percentage and shift. Original 61F0 receives decision mode, factor, returned budget, scale, and saturated total as its fifth stack argument. Return its boolean OR 4.\n\nThe 1152 fixtures execute the entire recovered helper chain. Only unsigned division helpers A6C0/A7CC are controlled; their exact argument traces, returned flag and restored frame are checked against a separate arithmetic model. No zero scale divisor occurs because 6220 returns at least 1. Wider inputs, division bodies, pointer validity and physical meanings remain open. No canonical admission or C implementation.\n');(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(source=dict(path=str(src),sha256=h(d)),fixtures=len(rows),files={p.name:h(p.read_bytes()) for p in sorted(o.iterdir())},accepted=False),indent=2)+'\n');print('PASS',len(rows))
