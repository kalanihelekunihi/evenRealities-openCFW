from pathlib import Path
import json,hashlib
from unicorn import *
from unicorn.arm_const import *
b=Path('g2/build/pseudocode-first/20260930T190500Z');o=Path('reviews/P2-touch-frequency-derived-state-4734-1260-independent-review-1261/001/replay-output');o.mkdir(parents=True,exist_ok=False);src=b/'attempts/P2-touch-reset-pseudocode-108/001/touch.flash.bin';d=src.read_bytes();h=lambda v:hashlib.sha256(v).hexdigest();rows=[]
for freq in [0,1,999,1000,1001,999999,1000000,1000001,48000000,0xffffffff]:
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x10000);u.mem_write(0x3300,d);u.mem_map(0x20000000,0x10000);u.mem_write(0x2000086c,b'\xa5'*16);u.mem_map(0x09000000,0x1000);u.reg_write(UC_ARM_REG_SP,0x2000f000);u.reg_write(UC_ARM_REG_LR,0x09000001);writes=[];calls=[]
 def code(u,p,s,x):
  if p==0x09000000:u.emu_stop()
  elif p==0x46f8:u.reg_write(UC_ARM_REG_R0,freq);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  elif p==0xa6c0:calls.append([u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1)])
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,lambda u,t,p,s,v,x:writes.append([p,s,v&((1<<(8*s))-1)]) if p<0x2000e000 and p>=0x20000000 else None);u.emu_start(0x4735,0,count=10000)
 expected=0
 if freq:
  million=(freq-1)//1000000+1;thousand=(freq-1)//1000+1;expected=(thousand<<15)&0xffffffff
  assert calls==[[freq-1,1000000],[freq-1,1000]]
  assert writes==[[0x20000878,4,freq],[0x20000870,1,million&255],[0x20000874,4,thousand],[0x2000086c,4,expected]]
 else:assert not calls and not writes and bytes(u.mem_read(0x2000086c,16))==b'\xa5'*16
 assert u.reg_read(UC_ARM_REG_PC)==0x09000000 and u.reg_read(UC_ARM_REG_SP)==0x2000f000 and u.reg_read(UC_ARM_REG_R0)==expected
 rows.append(dict(frequency=freq,division_calls=calls,writes=writes,raw_return=expected))
(o/'replays.json').write_text(json.dumps(rows,indent=2)+'\n');(o/'pseudocode.md').write_text('''# Touch frequency-derived state4734

Actual4734 calls46F8. A zero rawresult returnszero with no derived-state writes. NonzeroF storesF at20000878, then executes actualA6C0 unsigneddivision on(F-1,1000000), addsone and writes only thelowbyte at20000870. It executes actualA6C0 on(F-1,1000), addsone, stores theword at20000874, shifts thatwordleft15 modulo2^32 andstores at2000086C. The shiftedvalue is rawR0 on return; R4 andeightbyteframe restore.

Ten original-instruction fixtures replace only46F8 and execute both divisions. Independent integerceil postconditions check boundaryfrequencies, byte truncation and wordoverflow. Frequency source andphysicaltiming meanings remain unresolved; syntheticRAMtests do not validatehardware clocks. A6C0's general behavior outside these pairs remains separate. Body4734..476A excludesNOP/pool. No canonical admission orCimplementation.
''');(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(source=dict(path=str(src),sha256=h(d)),runtime_span=[0x4734,0x476a],fixtures=len(rows),files={p.name:h(p.read_bytes()) for p in sorted(o.iterdir())},accepted=False),indent=2)+'\n');print('PASS',len(rows),'frequency-state fixtures')
