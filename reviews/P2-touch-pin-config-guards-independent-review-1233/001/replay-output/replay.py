from pathlib import Path
import json,hashlib
from unicorn import *
from unicorn.arm_const import *
b=Path('g2/build/pseudocode-first/20260930T190500Z');o=Path('reviews/P2-touch-pin-config-guards-independent-review-1233/001/replay-output');o.mkdir(parents=True,exist_ok=False);src=b/'attempts/P2-touch-reset-pseudocode-108/001/touch.flash.bin';d=src.read_bytes();h=lambda v:hashlib.sha256(v).hexdigest();rows=[];P=0x40040000;C=0x20001000
cases=[('null_base',None,None,0),('null_config',None,None,0),('pin',None,None,0x8ef8)]+[(f'field_{i}',i,v,p) for i,v,p in [(0,2,0x8f00),(1,16,0x8f08),(2,16,0x8f10),(3,4,0x8f18),(4,2,0x8f20),(5,2,0x8f28)]]+[('mutate16',4,2,0x8f58),('mutate20',5,2,0x8f72)]
for name,index,value,stop in cases:
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x10000);u.mem_write(0x3300,d);u.mem_map(0x20000000,0x10000);u.mem_map(P,0x1000);u.mem_map(0x09000000,0x1000)
 for i,v in enumerate([1,15,15,3,1,1]):u.mem_write(C+4*i,v.to_bytes(4,'little'))
 if index is not None and not name.startswith('mutate'):u.mem_write(C+4*index,value.to_bytes(4,'little'))
 for r,v in [(UC_ARM_REG_R0,0 if name=='null_base' else P),(UC_ARM_REG_R1,8 if name=='pin' else 7),(UC_ARM_REG_R2,0 if name=='null_config' else C),(UC_ARM_REG_SP,0x2000f000),(UC_ARM_REG_LR,0x09000001)]:u.reg_write(r,v)
 calls=[];writes=[]
 def code(u,p,s,x):
  if p==stop or p==0x09000000:u.emu_stop()
  elif p in [0x8e64,0x8e84,0x8e28,0x8ebe]:
   calls.append(p)
   if p==0x8ebe and name.startswith('mutate'):u.mem_write(C+4*index,value.to_bytes(4,'little'))
   u.reg_write(UC_ARM_REG_R0,0);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,lambda u,t,p,s,v,x:writes.append([p,s,v]) if p>=0x40000000 else None);u.emu_start(0x8ee5,0,count=300)
 if name.startswith('null'):assert u.reg_read(UC_ARM_REG_PC)==0x09000000 and u.reg_read(UC_ARM_REG_R0)==0x005a0001 and u.reg_read(UC_ARM_REG_SP)==0x2000f000 and not calls
 else:assert u.reg_read(UC_ARM_REG_PC)==stop and u.reg_read(UC_ARM_REG_SP)==0x2000eff0
 assert writes==([[P+8,4,1<<24]] if name=='mutate20' else[])
 assert len(calls)==(4 if name.startswith('mutate') else 0)
 rows.append(dict(case=name,stop_pc=u.reg_read(UC_ARM_REG_PC),calls=calls,mmio_writes=writes,sp=u.reg_read(UC_ARM_REG_SP)))
(o/'replays.json').write_text(json.dumps(rows,indent=2)+'\n');(o/'notes.md').write_text('''# Pin configuration guard and mutation probes

Eleven original-instruction fixtures cover both null returns, seven initial breakpoint conditions, and two post-helper configuration mutations. Each breakpoint fixture stops immediately before the original BKPT instruction; it does not turn a breakpoint into an ordinary return or model debugger behavior. Initial invalid fields produce no helper calls or MMIO writes. Null paths return005A0001 with frame restored.

A controlled last helper changes configuration+16 or+20 to2 after initial validation. Actual later reloads reach respectively BKPT8F58 or8F72. The latter occurs after the bit24 write, preserving that partial MMIO effect. The former makes no MMIO write. This demonstrates fresh validation and partial effects; physical mutation timing, bus semantics and breakpoint continuation remain unresolved. Prior1230 is unchanged. No canonical admission or C implementation.
''');(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(source=dict(path=str(src),sha256=h(d)),fixtures=len(rows),files={p.name:h(p.read_bytes()) for p in sorted(o.iterdir())},accepted=False),indent=2)+'\n');print('PASS',len(rows),'guard/mutation paths')
