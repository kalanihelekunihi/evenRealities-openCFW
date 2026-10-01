from pathlib import Path
import json,hashlib,itertools
from unicorn import *
from unicorn.arm_const import *
b=Path('g2/build/pseudocode-first/20260930T190500Z');o=Path('reviews/P2-touch-device-activate-wrapper-independent-review-1383/001/replay-output');o.mkdir(parents=True,exist_ok=False);src=b/'attempts/P2-touch-reset-pseudocode-108/001/touch.flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();rows=[]
for first,second,flag in itertools.product([0,1,0xffffffff],[0,2,0xffffffff],[0,1,255]):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x10000);u.mem_write(0x3300,d);u.mem_map(0x20000000,0x10000);u.mem_write(0x20002004,(0x20002100).to_bytes(4,'little'));u.mem_write(0x20002107,bytes([flag]));u.mem_map(0x09000000,0x1000);u.reg_write(UC_ARM_REG_SP,0x2000f000);u.reg_write(UC_ARM_REG_LR,0x09000001);u.reg_write(UC_ARM_REG_R0,0x20002000);calls=[];writes=[];rets={0x7d92:first,0x58f8:0xffffffff,0x71c8:second,0x7e04:0xffffffff}
 def code(u,p,s,x):
  if p==0x09000000:u.emu_stop()
  elif p in rets:calls.append([p,u.reg_read(UC_ARM_REG_R0)]);u.reg_write(UC_ARM_REG_R0,rets[p]);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,lambda u,t,a,s,v,x:writes.append([a,s,v]) if a<0x2000e000 else None);u.emu_start(0x4abf,0,count=100)
 expected=[[0x7d92,0x20002000]]+([] if first else [[0x58f8,0x20002000],[0x71c8,0x20002000]]+([[0x7e04,0x20002000]] if not flag else []))
 assert calls==expected and writes==([[0x20002107,1,1]] if not first and not flag else []) and u.reg_read(UC_ARM_REG_R0)==(first if first else second) and u.reg_read(UC_ARM_REG_PC)==0x09000000 and u.reg_read(UC_ARM_REG_SP)==0x2000f000
 rows.append(dict(first_status=first,second_status=second,initial_flag=flag,calls=calls,writes=writes,return_value=first if first else second))
(o/'replays.json').write_text(json.dumps(rows,indent=2)+'\n');(o/'pseudocode.md').write_text('''# Touch activation wrapper 4ABE

Body 4ABE..4AF2 is 52 instruction bytes, excluding adjacent zero halfword. Retain incoming descriptor and call 7D92(descriptor). Nonzero returns that status immediately. On zero call 58F8(descriptor), ignore its return, then call 71C8(descriptor) and retain its status. Freshly load descriptor+4 pointer, then its byte+7. If zero call 7E04(descriptor), freshly reload descriptor+4 pointer and set its byte+7 to one. Return retained 71C8 status regardless of 58F8/7E04 results. Restore four-word frame. No null-pointer guards occur locally.

Twenty-seven original-instruction fixtures cover three first statuses, three second statuses and three initial flags. Four deeper helpers are controlled without memory effects. Exact reached calls, flag writes, result and SP are checked. Fresh pointer reload permits helper-induced pointer changes, which these fixtures do not exercise. Real activation, pointer validity and concurrency remain unresolved. No canonical admission or C implementation.
''');(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(source=dict(path=str(src),sha256=h(d)),fixtures=len(rows),files={p.name:h(p.read_bytes()) for p in sorted(o.iterdir())},accepted=False),indent=2)+'\n');print('PASS',len(rows))
