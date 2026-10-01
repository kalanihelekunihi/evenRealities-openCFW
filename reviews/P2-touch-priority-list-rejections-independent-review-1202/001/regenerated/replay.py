from pathlib import Path
import json,hashlib
from unicorn import *
from unicorn.arm_const import *
b=Path('g2/build/pseudocode-first/20260930T190500Z');o=Path('reviews/P2-touch-priority-list-rejections-independent-review-1202/001/regenerated');o.mkdir(parents=True,exist_ok=False);src=b/'attempts/P2-touch-reset-pseudocode-108/001/touch.flash.bin';pred=b/'analysis/touch-priority-list-insert-1199/001/receipt.json';d=src.read_bytes();h=lambda v:hashlib.sha256(v).hexdigest();rows=[];P=0x20002000;A=0x20003000;Z=0x20003020;T=0x20000f34
for case in ['null','missing12','missing0','duplicate_head','duplicate_middle','duplicate_tail']:
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x10000);u.mem_write(0x3300,d);u.mem_map(0x20000000,0x10000);u.mem_map(0x09000000,0x1000)
 def word(a,v):u.mem_write(a,v.to_bytes(4,'little'))
 word(P,0 if case=='missing0' else 1);word(P+12,0 if case=='missing12' else 1);u.mem_write(P+4,b'\x01');u.mem_write(P+24,b'\x64')
 sequence={'duplicate_head':[P,A,Z],'duplicate_middle':[A,P,Z],'duplicate_tail':[A,Z,P]}.get(case,[])
 word(T+4,sequence[0] if sequence else 0)
 for i,n in enumerate(sequence):word(n+16,sequence[i-1] if i else 0);word(n+20,sequence[i+1] if i+1<len(sequence) else 0)
 before=bytes(u.mem_read(0x20000000,0xe000));writes=[];trace=[];u.reg_write(UC_ARM_REG_R0,0 if case=='null' else P);u.reg_write(UC_ARM_REG_SP,0x2000f000);u.reg_write(UC_ARM_REG_LR,0x09000001)
 def code(u,p,s,x):
  trace.append(p)
  if p==0x09000000:u.emu_stop()
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,lambda u,t,a,s,v,x:writes.append([a,s,v]));u.emu_start(0xa3b1,0,count=1000)
 assert u.reg_read(UC_ARM_REG_PC)==0x09000000 and u.reg_read(UC_ARM_REG_R0)==0 and u.reg_read(UC_ARM_REG_SP)==0x2000f000
 assert before==bytes(u.mem_read(0x20000000,0xe000)) and all(a>=0x2000e000 for a,s,v in writes)
 rows.append(dict(case=case,trace=trace,return_value=0,list_region_unchanged=True,stack_writes=writes))
(o/'replays.json').write_text(json.dumps(rows,indent=2)+'\n');(o/'notes.md').write_text('''# Priority-list rejection probes

Six original-instruction fixtures exercise null input, zero required word at input+12, zero required word at input+0, and the supplied input already present at head, middle or tail of a finite linked list. Every case returns zero and restores SP. The entire non-stack synthetic RAM region remains byte-identical; only frame stores occur. These fixtures supplement1199 without altering it.

Duplicate rejection traverses to the supplied pointer and does not reinsert it. The tests do not establish termination for cyclic lists that never contain the input, index bounds, memory validity or concurrent access. No canonical admission or C implementation.
''');(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(input_pins={str(src):h(d),str(pred):h(pred.read_bytes())},files={p.name:h(p.read_bytes()) for p in sorted(o.iterdir())},accepted=False),indent=2)+'\n');print('PASS six rejection paths')
