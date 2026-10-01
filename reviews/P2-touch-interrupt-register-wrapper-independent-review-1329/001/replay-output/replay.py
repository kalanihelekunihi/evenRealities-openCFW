from pathlib import Path
import json,hashlib,struct,itertools
from unicorn import *
from unicorn.arm_const import *
b=Path('g2/build/pseudocode-first/20260930T190500Z');o=Path('reviews/P2-touch-interrupt-register-wrapper-independent-review-1329/001/replay-output');o.mkdir(parents=True,exist_ok=False);src=b/'attempts/P2-touch-reset-pseudocode-108/001/touch.flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();word=lambda a:struct.unpack_from('<I',d,a-0x3300)[0];mmio=word(0xa2e4);ram=word(0xa2e8);nullerr=word(0xa2ec);rows=[]
for pointer,priority,index,vector in itertools.product([0,0x20002000],[0,3,4],[0,7,0xffff],[0,ram]):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x10000);u.mem_write(0x3300,d);u.mem_map(0x20000000,0x10000);u.mem_write(0x20002000,index.to_bytes(2,'little')+bytes(2)+priority.to_bytes(4,'little'));u.mem_map(0xe000e000,0x1000);u.mem_write(mmio+8,vector.to_bytes(4,'little'));u.mem_map(0x09000000,0x1000);u.reg_write(UC_ARM_REG_SP,0x2000f000);u.reg_write(UC_ARM_REG_LR,0x09000001);u.reg_write(UC_ARM_REG_R0,pointer);u.reg_write(UC_ARM_REG_R1,0x3625);calls=[]
 def code(u,p,s,x):
  if p in [0x09000000,0xa2b8]:u.emu_stop()
  elif p in [0xa214,0xa274]:calls.append([p,u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1)]);u.reg_write(UC_ARM_REG_R0,0xffffffff);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,code);u.emu_start(0xa2a9,0,count=100)
 if not pointer:assert not calls and u.reg_read(UC_ARM_REG_R0)==nullerr and u.reg_read(UC_ARM_REG_PC)==0x09000000
 elif priority>3:assert not calls and u.reg_read(UC_ARM_REG_PC)==0xa2b8
 else:
  signed=index if index<0x8000 else index-65536;expected=[[0xa214,signed&0xffffffff,priority]]+([[0xa274,signed&0xffffffff,0x3625]] if vector==ram else [])
  assert calls==expected and u.reg_read(UC_ARM_REG_R0)==0 and u.reg_read(UC_ARM_REG_PC)==0x09000000
 if u.reg_read(UC_ARM_REG_PC)==0x09000000:assert u.reg_read(UC_ARM_REG_SP)==0x2000f000
 rows.append(dict(pointer=pointer,priority=priority,index=index,vector=vector,calls=calls,stop=u.reg_read(UC_ARM_REG_PC),return_value=u.reg_read(UC_ARM_REG_R0)))
(o/'replays.json').write_text(json.dumps(rows,indent=2)+'\n');(o/'pseudocode.md').write_text('''# Touch interrupt registration wrapper A2A8

Body A2A8..A2E4 is 60 instruction bytes. Null descriptor returns the null-input literal. Otherwise unsigned priority word at descriptor+4 must be at most three; violations reach BKPT A2B8. Sign-extend descriptor halfword at offset zero and call A214(index,priority). Freshly read literal system base+8 (vector table offset register), compare with RAM vector-base literal; only equality calls A274(index,incoming callback). Return zero regardless of deeper helper returns and restore four-word frame.

Thirty-six original-instruction fixtures cover null/nonnull descriptor, valid/invalid priorities, signed indices and both vector values. Two deeper helpers are controlled with all-ones return. Exact calls/arguments, guard stop, return and restored SP are checked. Deeper priority/vector writes, invalid pointers and physical interrupt dispatch remain unresolved. No canonical admission or C implementation.
''');(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(source=dict(path=str(src),sha256=h(d)),fixtures=len(rows),literals=dict(system_base=mmio,ram_vector=ram,null_error=nullerr),files={p.name:h(p.read_bytes()) for p in sorted(o.iterdir())},accepted=False),indent=2)+'\n');print('PASS',len(rows))
