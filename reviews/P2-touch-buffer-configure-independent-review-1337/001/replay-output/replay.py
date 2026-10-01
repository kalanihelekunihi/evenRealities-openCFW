from pathlib import Path
import json,hashlib,itertools
from unicorn import *
from unicorn.arm_const import *
b=Path('g2/build/pseudocode-first/20260930T190500Z');o=Path('reviews/P2-touch-buffer-configure-independent-review-1337/001/replay-output');o.mkdir(parents=True,exist_ok=False);src=b/'attempts/P2-touch-reset-pseudocode-108/001/touch.flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();rows=[]
for entry,pointer,length in itertools.product([0x9ad8,0x9af0],[0,0x200009b0],[0,1,16,0xffffffff]):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x10000);u.mem_write(0x3300,d);u.mem_map(0x20000000,0x10000);u.mem_write(0x20002000,bytes([0xa5])*80);u.mem_map(0x09000000,0x1000);u.reg_write(UC_ARM_REG_LR,0x09000001)
 for r,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],[0x40250000,pointer,length,0x20002000]):u.reg_write(r,v)
 writes=[];trap=0x9aec if entry==0x9ad8 else 0x9b02
 def code(u,p,s,x):
  if p in [0x09000000,trap]:u.emu_stop()
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,lambda u,t,a,s,v,x:writes.append([a,s,v]));u.emu_start(entry|1,0,count=30)
 invalid=length!=0 and pointer==0;offset=0x28 if entry==0x9ad8 else 0x38;expected=[] if invalid else [[0x20002000+offset,4,pointer],[0x20002000+offset+4,4,length],[0x20002000+offset+8,4,0]]+([[0x20002000+offset+12,4,0]] if entry==0x9ad8 else [])
 assert writes==expected and u.reg_read(UC_ARM_REG_PC)==(trap if invalid else 0x09000000) and u.reg_read(UC_ARM_REG_R0)==0x40250000
 rows.append(dict(entry=entry,pointer=pointer,length=length,writes=writes,stop=u.reg_read(UC_ARM_REG_PC)))
(o/'replays.json').write_text(json.dumps(rows,indent=2)+'\n');(o/'pseudocode.md').write_text('''# Touch buffer configuration adapters

9AD8..9AF0 is 24 instruction bytes. A nonzero length with null buffer reaches BKPT9AEC before stores. Otherwise store buffer at context+28, length at+2C, zero at+30 and+34, return through LR preserving incoming R0. 9AF0..9B06 is22 instruction bytes: same guard at9B02, store buffer at+38,length at+3C,zero at+40. Both allow null buffer when length is zero. No context-pointer guard, stack frame or interrupt masking occurs. The following9B06 routine is excluded.

Sixteen original-instruction fixtures cover both adapters, null/nonnull buffers and four lengths, checking exact stores, guard stop and R0 preservation. Breakpoint continuation, invalid context pointers, buffer use and concurrent access remain unresolved. No canonical admission or C implementation.
''');(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(source=dict(path=str(src),sha256=h(d)),fixtures=len(rows),files={p.name:h(p.read_bytes()) for p in sorted(o.iterdir())},accepted=False),indent=2)+'\n');print('PASS',len(rows))
