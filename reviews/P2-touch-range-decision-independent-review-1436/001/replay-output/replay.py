from pathlib import Path
import json,hashlib,itertools
from unicorn import *
from unicorn.arm_const import *
b=Path('g2/build/pseudocode-first/20260930T190500Z');o=Path('reviews/P2-touch-range-decision-independent-review-1436/001/replay-output');o.mkdir(parents=True,exist_ok=False);src=b/'attempts/P2-touch-reset-pseudocode-108/001/touch.flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();rows=[]
for mode,left,right,divisor,total,remainder in itertools.product([0,1,2,255],[0,4],[0,4],[0,1,4],[0,1,4],[0,1]):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x10000);u.mem_write(0x3300,d);u.mem_map(0x20000000,0x10000);u.mem_map(0x09000000,0x1000);sp=0x2000f000;u.mem_write(sp,total.to_bytes(4,'little'));u.reg_write(UC_ARM_REG_SP,sp);u.reg_write(UC_ARM_REG_LR,0x09000001)
 for reg,value in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],[mode,left,right,divisor]):u.reg_write(reg,value)
 calls=[]
 def code(u,p,s,x):
  if p==0x09000000:u.emu_stop()
  elif p==0xa7cc:
   calls.append([p,u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1)]);u.reg_write(UC_ARM_REG_R0,123);u.reg_write(UC_ARM_REG_R1,remainder);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,code);u.emu_start(0x61f1,0,count=50)
 expected=0 if left>right else 1
 if mode!=2:
  if total<divisor:expected=0
  if mode==0 and remainder:expected=0
 expected_calls=[[0xa7cc,total,divisor]] if mode==0 else []
 assert calls==expected_calls and u.reg_read(UC_ARM_REG_R0)==expected and u.reg_read(UC_ARM_REG_SP)==sp and u.reg_read(UC_ARM_REG_PC)==0x09000000
 rows.append(dict(mode=mode,left=left,right=right,divisor=divisor,total=total,remainder=remainder,result=expected,calls=calls))
(o/'replays.json').write_text(json.dumps(rows,indent=2)+'\n');(o/'pseudocode.md').write_text('# Range decision helper at 61F0\n\nThe 48-byte body [61F0,6220) starts a boolean result from unsigned (second argument <= third argument). If mode is 2, return that result. Otherwise load a fifth argument from the incoming stack and clear the result if it is below the fourth argument. For mode zero, call A7CC(fifth argument,fourth argument); clear the result when the returned R1 remainder is nonzero. Other modes do not call division. Restore the frame and return the boolean.\n\nThe 288 original-instruction fixtures vary the comparison, mode, stack argument and controlled remainder, including a zero divisor. A7CC remains explicitly controlled; zero-divisor behavior is not inferred. Exact call arguments, result and frame are checked. Physical meanings remain unresolved. No canonical admission or C implementation.\n');(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(source=dict(path=str(src),sha256=h(d)),fixtures=len(rows),files={p.name:h(p.read_bytes()) for p in sorted(o.iterdir())},accepted=False),indent=2)+'\n');print('PASS',len(rows))
