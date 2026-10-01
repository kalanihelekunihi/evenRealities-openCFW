from pathlib import Path
import json,hashlib,itertools
from unicorn import *
from unicorn.arm_const import *
b=Path('g2/build/pseudocode-first/20260930T190500Z');o=Path('reviews/P2-touch-zero-return-independent-review-1298/001/replay-output');o.mkdir(parents=True,exist_ok=False);src=b/'attempts/P2-touch-reset-pseudocode-108/001/touch.flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();rows=[]
for args in itertools.product([0,0xffffffff],repeat=4):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x10000);u.mem_write(0x3300,d);u.mem_map(0x20000000,0x10000);u.mem_map(0x09000000,0x1000);u.reg_write(UC_ARM_REG_SP,0x2000f000);u.reg_write(UC_ARM_REG_LR,0x09000001)
 regs=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]
 for r,v in zip(regs,args):u.reg_write(r,v)
 def code(u,p,s,x):
  if p==0x09000000:u.emu_stop()
 u.hook_add(UC_HOOK_CODE,code);u.emu_start(0x3ee1,0,count=20)
 assert u.reg_read(UC_ARM_REG_PC)==0x09000000 and u.reg_read(UC_ARM_REG_SP)==0x2000f000 and [u.reg_read(r) for r in regs]==[0,*args[1:]]
 assert bytes(u.mem_read(0x2000eff0,16))==b''.join(v.to_bytes(4,'little') for v in args)
 rows.append(dict(args=args,return_value=0,discarded_stack_words=args))
(o/'replays.json').write_text(json.dumps(rows,indent=2)+'\n');(o/'pseudocode.md').write_text('''# Touch 3EE0 zero-return routine

The eight-byte body 3EE0..3EE8 pushes R0..R3, sets R0 zero, adds 16 to SP and returns through LR. It preserves R1..R3 and restores SP, leaving the four incoming argument words below the restored stack pointer. There is no helper call or pointer dereference. Sixteen original-instruction fixtures cover all combinations of zero and all-ones arguments, verifying registers, frame restoration and discarded stack contents. Original application caller passes three flash literals. No meaning is inferred from the routine's zero return; no canonical admission or C implementation.
''');(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(source=dict(path=str(src),sha256=h(d)),fixtures=len(rows),files={p.name:h(p.read_bytes()) for p in sorted(o.iterdir())},accepted=False),indent=2)+'\n');print('PASS',len(rows))
