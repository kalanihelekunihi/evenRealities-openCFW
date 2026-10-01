from pathlib import Path
import json,hashlib,itertools
from unicorn import *
from unicorn.arm_const import *
b=Path('g2/build/pseudocode-first/20260930T190500Z');o=Path('reviews/P2-touch-threshold-flags-independent-review-1432/001/replay-output');o.mkdir(parents=True,exist_ok=False);src=b/'attempts/P2-touch-reset-pseudocode-108/001/touch.flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();rows=[]
for scale,offset,extra in itertools.product([0,1,2,3,4,7,8,15,16,255,256,32768,65535],[0,1,255],[0,1,2,63,64,8191,16383,65535]):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x10000);u.mem_write(0x3300,d);u.mem_map(0x20000000,0x10000);u.mem_map(0x09000000,0x1000);R=0x20002000;D=0x20002100;C=0x20002200
 u.mem_write(R+44,extra.to_bytes(2,'little'));u.mem_write(D+8,C.to_bytes(4,'little'));u.mem_write(C+77,bytes([offset]));u.mem_write(C+60,scale.to_bytes(2,'little'));u.reg_write(UC_ARM_REG_R0,R);u.reg_write(UC_ARM_REG_R1,D);u.reg_write(UC_ARM_REG_SP,0x2000f000);u.reg_write(UC_ARM_REG_LR,0x09000001);pcs=[]
 def code(u,p,s,x):
  pcs.append(p)
  if p==0x09000000:u.emu_stop()
 u.hook_add(UC_HOOK_CODE,code);u.emu_start(0x623d,0,count=150)
 bit_scale=(1<<max(1,scale.bit_length()))-1;threshold=(bit_scale+1)>>2;expected=10 if offset+extra>=threshold else 8
 assert u.reg_read(UC_ARM_REG_R0)==expected and u.reg_read(UC_ARM_REG_SP)==0x2000f000 and u.reg_read(UC_ARM_REG_PC)==0x09000000 and 0x6220 in pcs
 rows.append(dict(scale=scale,offset=offset,extra=extra,threshold=threshold,result=expected))
(o/'replays.json').write_text(json.dumps(rows,indent=2)+'\n');(o/'pseudocode.md').write_text('# Threshold flags at 623C\n\nThe 38-byte body [623C,6262) reads row halfword +44 and context byte +77 through descriptor word +8, then adds them as unsigned values. It calls original 6220 with context halfword +60. Threshold is (returned scale + 1) >> 2. Return 10 if the sum is at least threshold, otherwise 8. No persistent writes occur.\n\nThe 312 fixtures execute both original routines and check threshold boundaries, high scales, offsets, returned flags and frame restoration. The bit-scale helper has separate exhaustive halfword evidence in 1429. Pointer validity and physical field meanings remain unresolved. No canonical admission or C implementation.\n');(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(source=dict(path=str(src),sha256=h(d)),fixtures=len(rows),files={p.name:h(p.read_bytes()) for p in sorted(o.iterdir())},accepted=False),indent=2)+'\n');print('PASS',len(rows))
