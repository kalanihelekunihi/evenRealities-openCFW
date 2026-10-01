from pathlib import Path
import json,hashlib,struct,itertools
from unicorn import *
from unicorn.arm_const import *
b=Path('g2/build/pseudocode-first/20260930T190500Z');o=Path('reviews/P2-touch-chunked-delay-independent-review-1316/001/replay-output');o.mkdir(parents=True,exist_ok=False);src=b/'attempts/P2-touch-reset-pseudocode-108/001/touch.flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();word=lambda a:struct.unpack_from('<I',d,a-0x3300)[0];chunk=word(0xa318);step=word(0xa31c);scale=word(0xa320);rows=[]
for value,factor in itertools.product([0,1,32768,32769,65536,65537],[0,1,3]):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x10000);u.mem_write(0x3300,d);u.mem_map(0x20000000,0x10000);u.mem_write(chunk,(4).to_bytes(4,'little'));u.mem_write(scale,factor.to_bytes(4,'little'));u.mem_map(0x09000000,0x1000);u.reg_write(UC_ARM_REG_SP,0x2000f000);u.reg_write(UC_ARM_REG_LR,0x09000001);u.reg_write(UC_ARM_REG_R0,value);args=[]
 def code(u,p,s,x):
  if p==0x09000000:u.emu_stop()
  elif p==0x4480:args.append(u.reg_read(UC_ARM_REG_R0))
 u.hook_add(UC_HOOK_CODE,code);u.emu_start(0xa2f1,0,count=200000)
 remaining=value;expected=[]
 while remaining>32768:expected.append(4);remaining=(remaining+step)&0xffffffff
 expected.append((remaining*factor)&0xffffffff)
 assert args==expected and u.reg_read(UC_ARM_REG_PC)==0x09000000 and u.reg_read(UC_ARM_REG_R0)==0 and u.reg_read(UC_ARM_REG_SP)==0x2000f000
 rows.append(dict(input=value,scale=factor,actual_delay_arguments=args,return_value=0))
(o/'replays.json').write_text(json.dumps(rows,indent=2)+'\n');(o/'pseudocode.md').write_text('''# Touch chunked delay A2F0

Body A2F0..A318 is 40 instruction bytes, excluding three literal words. Retain input in R4. While unsigned remaining exceeds 32768, freshly load chunk-delay word at literal address A318, call original 4480 with that value, and add literal FFFF8000 to remaining (subtract 32768 modulo 2^32). Then freshly load scale word at literal address A320, multiply remaining modulo 2^32, call original 4480 once more, restore frame and return its zero result.

Eighteen original-instruction fixtures observe every delay-call argument without modifying execution. They cover zero, one, exact threshold, one above threshold and the next chunk boundary, with three scale values. RAM-derived delays are explicitly supplied small fixture values. Loop count, arguments, zero result and SP agree with the separate model; physical elapsed time and asynchronous changes remain unresolved. No canonical admission or C implementation.
''');(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(source=dict(path=str(src),sha256=h(d)),fixtures=len(rows),literals=dict(chunk_address=chunk,step=step,scale_address=scale),files={p.name:h(p.read_bytes()) for p in sorted(o.iterdir())},accepted=False),indent=2)+'\n');print('PASS',len(rows))
