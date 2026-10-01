from pathlib import Path
import hashlib,json,itertools
from unicorn import *
from unicorn.arm_const import *
b=Path('g2/build/pseudocode-first/20260930T190500Z');o=Path('/Users/kalani/Repo/evenRealities-openCFW/reviews/P2-touch-status-wait-independent-review-1533/001/run');o.mkdir(parents=True,exist_ok=True);src=b/'attempts/P2-touch-reset-pseudocode-108/001/touch.flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();body=d[0x3308:0x334a];assert len(body)==0x42;ins=[];rows=[]
for mode,count,exit_at in itertools.product([0,1,2,3,4,0xffffffff],[0,1,3],[0,1,4]):
 mask=0x1000000 if mode in [2,3] else 1;expected=((mode<<24)&mask) if mode in [2,3] else mode
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x10000);u.mem_write(0x3300,d);u.mem_map(0x20000000,0x10000);u.mem_map(0x40000000,0x1000);u.mem_map(0x09000000,0x1000);D=0x20002000;F=D+256;X=F+256;P=0x40000000
 for a,v in [(D,F),(F+8,X),(X,P)]:u.mem_write(a,v.to_bytes(4,'little'))
 for r,v in [(UC_ARM_REG_R0,count),(UC_ARM_REG_R1,mode),(UC_ARM_REG_R2,D),(UC_ARM_REG_SP,0x2000f000),(UC_ARM_REG_LR,0x09000001)]:u.reg_write(r,v)
 reads=[];calls=[]
 def read(u,t,a,s,v,x):
  if a==P+0x180:
   val=expected if len(reads)<exit_at else expected^mask
   u.mem_write(a,(val&0xffffffff).to_bytes(4,'little'));reads.append(val&0xffffffff)
 def code(u,p,s,x):
  if p==0x09000000:u.emu_stop()
  elif p==0xa324:calls.append(u.reg_read(UC_ARM_REG_R0));u.reg_write(UC_ARM_REG_R0,0xdeadbeef);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_MEM_READ,read);u.hook_add(UC_HOOK_CODE,code);u.emu_start(0x6609,0,count=500)
 n=0
 while True:
  value=expected if n<exit_at else expected^mask;n+=1
  if (value&mask)!=expected:ret=0;break
  if n-1==count:ret=4;break
 assert u.reg_read(UC_ARM_REG_PC)==0x09000000 and u.reg_read(UC_ARM_REG_R0)==ret and u.reg_read(UC_ARM_REG_SP)==0x2000f000
 assert len(reads)==n and calls==[1]*(n-1)
 rows.append(dict(mode=mode,count=count,exit_at=exit_at,reads=reads,delay_calls=calls,result=ret))
(o/'disassembly.txt').write_text('\n'.join(f'{i.address:04X}: {i.mnemonic} {i.op_str}' for i in ins)+'\n');(o/'replays.json').write_text(json.dumps(rows,indent=2)+'\n')
(o/'pseudocode.md').write_text(f'''# Status wait at 6608

The exact 66-byte body [6608,664A) contains {len(ins)} instructions. Inputs are a decrementing budget, a mode and a descriptor. For modes 2 and 3, select mask 0x01000000 and expected value (mode << 24) & mask. Otherwise select mask 1 and retain the full mode as expected value. This means modes outside 0–3 cannot match the masked status.

Repeatedly resolve the peripheral through descriptor[0], that object's word at offset 8, and the resulting object's first word. Read status at peripheral + 0x180. Return 0 immediately if (status & mask) differs from expected. If it matches and budget is zero, return 4. Otherwise call A324(1), decrement budget with unsigned wrapping and repeat. The helper return is ignored. Restore the 24-byte frame and saved registers.

{len(rows)} original-instruction fixtures exercise six modes, three budgets and three controlled status transitions. They verify every status read, delay call, result and restored stack. The delay helper remains controlled; physical status transitions and time units are unresolved. This is private pseudocode evidence, with no canonical admission or C implementation.
''');(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(source=dict(path=str(src),sha256=h(d)),body_sha256=h(body),instruction_count=len(ins),fixtures=len(rows),files={p.name:h(p.read_bytes()) for p in sorted(o.iterdir())},accepted=False),indent=2)+'\n');print('PASS',len(rows),len(ins))
