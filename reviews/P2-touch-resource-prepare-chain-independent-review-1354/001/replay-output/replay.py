from pathlib import Path
import hashlib,json,itertools
from unicorn import *
from unicorn.arm_const import *
b=Path('g2/build/pseudocode-first/20260930T190500Z');o=Path('reviews/P2-touch-resource-prepare-chain-independent-review-1354/001/replay-output');o.mkdir(parents=True,exist_ok=False);src=b/'attempts/P2-touch-reset-pseudocode-108/001/touch.flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();rows=[]
for entry,flag,prepare,setup in itertools.product([0x4c44,0x4c72],[0,1,255],[0,1,0xffffffff],[0,2,0xffffffff]):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x10000);u.mem_write(0x3300,d);u.mem_map(0x20000000,0x10000)
 for a,v in [(0x20002000,0x20002100),(0x20002108,0x20002200),(0x20002200,0x40250000),(0x20002204,0x20002300)]:u.mem_write(a,v.to_bytes(4,'little'))
 u.mem_write(0x20002300,bytes([flag]));u.mem_map(0x09000000,0x1000);u.reg_write(UC_ARM_REG_SP,0x2000f000);u.reg_write(UC_ARM_REG_LR,0x09000001);u.reg_write(UC_ARM_REG_R0,0x20002000);calls=[]
 def code(u,p,s,x):
  if p==0x09000000:u.emu_stop()
  elif p in [0x8fa0,0x6ac0]:calls.append([p,u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1)]);u.reg_write(UC_ARM_REG_R0,prepare if p==0x8fa0 else setup);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,code);u.emu_start(entry|1,0,count=100)
 expected=[] if flag else [[0x8fa0,0x40250000,2]]+([] if prepare else [[0x6ac0,1,0x20002000]])
 ret=128 if flag else (8 if prepare else setup)
 assert calls==expected and u.reg_read(UC_ARM_REG_R0)==ret and u.reg_read(UC_ARM_REG_PC)==0x09000000 and u.reg_read(UC_ARM_REG_SP)==0x2000f000
 rows.append(dict(entry=entry,flag=flag,prepare_status=prepare,setup_status=setup,calls=calls,return_value=ret))
(o/'replays.json').write_text(json.dumps(rows,indent=2)+'\n');(o/'pseudocode.md').write_text('''# Touch resource preparation chain

4C44..4C72 is46 instruction bytes. Follow descriptorword0, then word+8, then word+4 to flagpointer. Nonzero flagbyte returns128. Otherwise load resourceword0 from the intermediate record and call8FA0(resource,2). Nonzero returns8. Zero calls6AC0(1,originaldescriptor), returning its raw result. Restore two-word frame. 4C72..4C7A is six-byte forwarding adapter with its own two-word frame. No pointer guards occur locally.

Receipt-derived originalinstruction fixtures cover bothentries, three flags and three statuses for each explicit controlled deeperhelper. Exact calls/arguments, conversions/rawresult andSP are checked. Pointer validity, deeper effects and concurrency remain unresolved. No canonical admission or C implementation.
''');(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(source=dict(path=str(src),sha256=h(d)),fixtures=len(rows),files={p.name:h(p.read_bytes()) for p in sorted(o.iterdir())},accepted=False),indent=2)+'\n');print('PASS',len(rows))
