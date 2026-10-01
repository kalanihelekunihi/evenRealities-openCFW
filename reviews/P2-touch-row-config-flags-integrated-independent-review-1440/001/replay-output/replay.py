from pathlib import Path
import json,hashlib,itertools
from unicorn import *
from unicorn.arm_const import *
b=Path('g2/build/pseudocode-first/20260930T190500Z');o=Path('reviews/P2-touch-row-config-flags-integrated-independent-review-1440/001/replay-output');o.mkdir(parents=True,exist_ok=False);src=b/'attempts/P2-touch-reset-pseudocode-108/001/touch.flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();rows=[]
for flags,mode,width,signed in itertools.product([0,1,4,8,9,12],[0,1,10],[0,7,8,11,4096,4097],[0,128]):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x10000);u.mem_write(0x3300,d);u.mem_map(0x20000000,0x10000);u.mem_map(0x09000000,0x1000);D=0x20002000;C=0x20002100;T=0x20002200
 u.mem_write(D+8,C.to_bytes(4,'little'));u.mem_write(D+12,T.to_bytes(4,'little'));u.mem_write(C+0x4e,bytes([5]))
 for i in range(3):
  r=0x20002400+i*0x100;u.mem_write(T+i*144,r.to_bytes(4,'little'));u.mem_write(T+i*144+0x7a,bytes([mode]));u.mem_write(r+0x21,bytes([flags]));u.mem_write(r+0x38,bytes([signed]));u.mem_write(r+14,width.to_bytes(2,'little'))
 u.reg_write(UC_ARM_REG_R0,D);u.reg_write(UC_ARM_REG_SP,0x2000f000);u.reg_write(UC_ARM_REG_LR,0x09000001);calls=[];writes=[]
 def code(u,p,s,x):
  if p==0x09000000:u.emu_stop()
  elif p in [0xa6c0,0xa7cc]:
   calls.append([p,u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1)]);u.reg_write(UC_ARM_REG_R0,calls[-1][1]//calls[-1][2]);u.reg_write(UC_ARM_REG_R1,calls[-1][1]%calls[-1][2]);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,lambda u,t,a,s,v,x:writes.append([a,s,v]) if a<0x2000e000 else None);u.emu_start(0x6385,0,count=1000)
 status=0;minimum=0;expected_calls=[];expected_writes=[]
 for i in range(3):
  r=0x20002400+i*0x100;rec=T+i*144
  if flags&4 or flags&3==1:
   if signed&128:
    expected_calls.append([0xa6c0,0,100]);expected_writes.append([r+0x38,1,128])
   if flags&4:
    expected_calls.extend([[0xa6c0,0,100],[0xa7cc,0,1]]);expected_writes.append([r+0x21,1,4])
  elif flags&8:expected_writes.append([r+0x21,1,10])
  if mode in [1,10]:minimum=8
  else:status=1
  if flags&3==1:
   shift=((((128 if signed&128 else signed)&~128)&3)+5+1)&255;minimum=(minimum+((1<<shift)&0xffffffff if shift<32 else 0))&0xffffffff
  if width<minimum or width>4096:status=2048;break
 assert calls==expected_calls and writes==expected_writes and u.reg_read(UC_ARM_REG_R0)==status and u.reg_read(UC_ARM_REG_SP)==0x2000f000 and u.reg_read(UC_ARM_REG_PC)==0x09000000
 rows.append(dict(flags=flags,mode=mode,width=width,signed=signed,result=status,calls=calls,writes=writes))
(o/'replays.json').write_text(json.dumps(rows,indent=2)+'\n');(o/'pseudocode.md').write_text('# Validator with complete local flag helper chain\n\nOriginal 6384 now executes original 6294 in addition to all recovered range, threshold and shift helpers. Only A6C0 and A7CC remain controlled with unsigned quotient/remainder responses. Initialized percentage, decision-mode and context fields are zero: the 6294 path calls A6C0(0,100) then A7CC(0,1) and returns flag 4. The parent stores that byte while retaining its original flags for later decisions.\n\nThe 216 fixtures check exact division calls, row writes, final status and restored frame. Wider helper inputs are separately exercised in 1437/002 and the earlier helper packets. Division bodies, mixed flags, pointer validity and physical meaning remain unresolved. No canonical admission or C implementation.\n');(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(source=dict(path=str(src),sha256=h(d)),fixtures=len(rows),files={p.name:h(p.read_bytes()) for p in sorted(o.iterdir())},accepted=False),indent=2)+'\n');print('PASS',len(rows))
