from pathlib import Path
import json,hashlib,itertools
from unicorn import *
from unicorn.arm_const import *
b=Path('g2/build/pseudocode-first/20260930T190500Z');o=Path('reviews/P2-touch-enable-control-a0bc-independent-review-1226/001/replay-output');o.mkdir(parents=True,exist_ok=False);src=b/'attempts/P2-touch-reset-pseudocode-108/001/touch.flash.bin';d=src.read_bytes();h=lambda v:hashlib.sha256(v).hexdigest();rows=[]
for selector,mode,value in itertools.product([0,1,2,3,4,0xffffffff],[0,1,2,3,4,258,259],[0,1,2,0xffffffff]):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x10000);u.mem_write(0x3300,d);u.mem_map(0x40010000,0x1000);u.mem_map(0x09000000,0x1000)
 for r,v in [(UC_ARM_REG_R0,selector),(UC_ARM_REG_R1,mode),(UC_ARM_REG_R2,value),(UC_ARM_REG_SP,0x2000f000),(UC_ARM_REG_LR,0x09000001)]:u.reg_write(r,v)
 writes=[]
 def code(u,p,s,x):
  if p==0x09000000:u.emu_stop()
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,lambda u,t,p,s,v,x:writes.append([p,s,v]));u.emu_start(0xa0bd,0,count=100)
 valid=selector<=3 and ((mode==1 and value<=1) or (((mode-2)&255)<=1 and value==0))
 assert writes==([[0x40010100+4*selector,4,((mode<<6)&255)|(value&63)]] if valid else[])
 assert u.reg_read(UC_ARM_REG_PC)==0x09000000 and u.reg_read(UC_ARM_REG_R0)==(0 if valid else 0x004a0001) and u.reg_read(UC_ARM_REG_SP)==0x2000f000
 rows.append(dict(selector=selector,mode=mode,value=value,valid=valid,writes=writes))
(o/'replays.json').write_text(json.dumps(rows,indent=2)+'\n');(o/'pseudocode.md').write_text('''# Touch enable-control word A0BC

Accept only unsigned R0<=3 and either (R1==1 and unsigned R2<=1) or (((R1-2) modulo256)<=1 and R2==0). This preserves the eight-bit aliases for modes258/259. Success writes ((R1<<6)&255)|(R2&63) as one word at40010100+4*R0 and returnszero. Rejection returns004A0001 with no write. No helper or stack frame occurs. BodyA0BC..A0FA excludes the trailing NOP and literal pool.

168 original-instruction fixtures check boundaries, aliases, exact write address/value, return and SP. Memory is synthetic; device meaning and physical accesses remain unresolved. No canonical admission or C implementation.
''');(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(source=dict(path=str(src),sha256=h(d)),runtime_span=[0xa0bc,0xa0fa],fixtures=len(rows),files={p.name:h(p.read_bytes()) for p in sorted(o.iterdir())},accepted=False),indent=2)+'\n');print('PASS',len(rows),'enable-control fixtures')
