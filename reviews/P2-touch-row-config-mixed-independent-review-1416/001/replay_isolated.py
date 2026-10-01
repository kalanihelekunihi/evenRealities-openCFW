from pathlib import Path
import json,hashlib,itertools
from unicorn import *
from unicorn.arm_const import *
b=Path('g2/build/pseudocode-first/20260930T190500Z');o=Path('reviews/P2-touch-row-config-mixed-independent-review-1416/001/replay-output');o.mkdir(parents=True,exist_ok=False);src=b/'attempts/P2-touch-reset-pseudocode-108/001/touch.flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();rows=[]
for modes,widths in itertools.product(itertools.product([0,1,10],repeat=3),itertools.product([0,8,4097],repeat=3)):
 flags=0;signed=0
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x10000);u.mem_write(0x3300,d);u.mem_map(0x20000000,0x10000);u.mem_map(0x09000000,0x1000);D=0x20002000;C=0x20002100;T=0x20002200
 u.mem_write(D+8,C.to_bytes(4,'little'));u.mem_write(D+12,T.to_bytes(4,'little'));u.mem_write(C+0x4e,bytes([5]))
 for i in range(3):
  r=0x20002400+i*0x100;u.mem_write(T+i*144,r.to_bytes(4,'little'));u.mem_write(T+i*144+0x7a,bytes([modes[i]]));u.mem_write(r+0x21,bytes([flags]));u.mem_write(r+0x38,bytes([signed]));u.mem_write(r+14,widths[i].to_bytes(2,'little'))
 u.reg_write(UC_ARM_REG_R0,D);u.reg_write(UC_ARM_REG_SP,0x2000f000);u.reg_write(UC_ARM_REG_LR,0x09000001);calls=[];writes=[]
 def code(u,p,s,x):
  if p==0x09000000:u.emu_stop()
  elif p in [0x623c,0x6352,0x6294,0x6262]:
   calls.append([p,u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1)]);u.reg_write(UC_ARM_REG_R0,3 if p==0x6262 else 7 if p==0x6352 else flags);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,lambda u,t,a,s,v,x:writes.append([a,s,v]) if a<0x2000e000 else None);u.emu_start(0x6385,0,count=1000)
 status=0;minimum=0;expected_calls=[];expected_writes=[]
 for i in range(3):
  r=0x20002400+i*0x100;rec=T+i*144;mode=modes[i];width=widths[i]
  if flags&4 or flags&3==1:
   if signed&128:expected_calls.append([0x6352,rec,D]);expected_writes.append([r+0x38,1,7])
   if flags&4:expected_calls.append([0x6294,rec,D]);expected_writes.append([r+0x21,1,flags])
  elif flags&8:expected_calls.append([0x623c,r,D]);expected_writes.append([r+0x21,1,flags])
  if mode in [1,10]:minimum=8
  else:status=1
  if flags&3==1:expected_calls.append([0x6262,(7 if signed&128 else signed)&~128,5]);minimum=(minimum+3)&0xffffffff
  if width<minimum or width>4096:status=2048;break
 assert calls==expected_calls and writes==expected_writes and u.reg_read(UC_ARM_REG_R0)==status and u.reg_read(UC_ARM_REG_SP)==0x2000f000 and u.reg_read(UC_ARM_REG_PC)==0x09000000
 rows.append(dict(flags=flags,modes=modes,widths=widths,signed=signed,result=status,calls=calls,writes=writes))
(o/'replays.json').write_text(json.dumps(rows,indent=2)+'\n');(o/'pseudocode.md').write_text('# Mixed-row state checks for 6384\n\nThis extends the complete local-flow packet 1413 with 729 original-instruction fixtures. Each of three records independently selects mode 0, 1 or 10 and width 0, 8 or 4097. Flags and signed bytes are zero, so no helper boundaries are reached. The independent model checks that modes 1 and 10 set minimum to 8, other modes set status 1 while retaining the earlier minimum, and out-of-range widths immediately replace status with 2048. Exact return, stack restoration, empty helper trace and absence of row writes are checked.\n\nHelper effects and mixed flags remain covered only by the controlled uniform-row fixtures in 1413. Physical behavior and pointer validity remain unresolved. No canonical admission or C implementation.\n');(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(source=dict(path=str(src),sha256=h(d)),fixtures=len(rows),files={p.name:h(p.read_bytes()) for p in sorted(o.iterdir())},accepted=False),indent=2)+'\n');print('PASS',len(rows))
