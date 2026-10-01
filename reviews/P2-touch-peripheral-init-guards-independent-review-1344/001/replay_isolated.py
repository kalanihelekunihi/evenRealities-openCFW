from pathlib import Path
import json,hashlib,struct
from unicorn import *
from unicorn.arm_const import *
b=Path('g2/build/pseudocode-first/20260930T190500Z');o=Path('reviews/P2-touch-peripheral-init-guards-independent-review-1344/001/replay-output');o.mkdir(parents=True,exist_ok=False);src=b/'attempts/P2-touch-reset-pseudocode-108/001/touch.flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();error=struct.unpack_from('<I',d,0x9ad4-0x3300)[0];cases=[('valid',None,None,0x9942)]+[(f'null-{i}',i,None,0x09000000) for i in range(3)]+[('mode-zero',None,(0,1,0),0x9912),('mode-four',None,(0,1,4),0x9912),('conflicting-flags',None,(5,1,1),0x9920),('signed-negative',None,(3,1,128),0x999a),('odd-field',None,(4,1,1),0x9930),('length16-too-large',None,(16,4,17),0x9938),('length12-too-large',None,(12,4,17),0x9940)];rows=[]
for name,null,mutation,stop in cases:
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x10000);u.mem_write(0x3300,d);u.mem_map(0x20000000,0x10000);config=bytearray(20);config[0]=1;config[1]=1
 if mutation:offset,width,value=mutation;config[offset:offset+width]=value.to_bytes(width,'little')
 u.mem_write(0x20002000,bytes(config));u.mem_map(0x40250000,0x1000);u.mem_map(0x09000000,0x1000);u.reg_write(UC_ARM_REG_SP,0x2000f000);u.reg_write(UC_ARM_REG_LR,0x09000001);args=[0x40250000,0x20002000,0x20002100]
 if null is not None:args[null]=0
 for r,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2],args):u.reg_write(r,v)
 stores=[]
 def code(u,p,s,x):
  if p in [0x09000000,0x9942,0x9912,0x9920,0x999a,0x9930,0x9938,0x9940]:u.emu_stop()
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,lambda u,t,a,s,v,x:stores.append([a,s,v]) if a<0x2000e000 or a>=0x40000000 else None);u.emu_start(0x98f5,0,count=100)
 assert u.reg_read(UC_ARM_REG_PC)==stop and not stores
 if null is not None:assert u.reg_read(UC_ARM_REG_R0)==error and u.reg_read(UC_ARM_REG_SP)==0x2000f000
 rows.append(dict(name=name,args=args,configuration=config.hex(),stop=stop,stores=stores))
(o/'replays.json').write_text(json.dumps(rows,indent=2)+'\n');(o/'pseudocode.md').write_text('''# Touch 98F4 initialization guards

This packet covers the guard prefix and null-return branches only, not the complete helper. Null peripheral, configuration or context pointer returns the same literal error and restores the saved frame. Nonnull input requires mode byte0 in1..3; byte1 and byte5 cannot both be nonzero; signed byte3 must be nonnegative; byte4 bitzero must be clear; words+16/+12 must each be at most16. Violations reach their original BKPT before local data writes. A valid guard fixture stops at9942 before configuration-dependent programming.

Receipt-derived fixtures cover all three null cases, both mode-bound violations and each other guard plus one valid prefix. Breakpoints are observed before execution. Exact stops, absence of non-stack writes and null-path return/frame are checked. Full programming pseudocode, later guards, continuation after breakpoints and physical behavior remain outstanding. No canonical admission or C implementation.
''');(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(source=dict(path=str(src),sha256=h(d)),fixtures=len(rows),null_error=error,files={p.name:h(p.read_bytes()) for p in sorted(o.iterdir())},accepted=False),indent=2)+'\n');print('PASS',len(rows),hex(error))
