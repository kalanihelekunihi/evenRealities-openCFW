from pathlib import Path
import json,hashlib,itertools
from unicorn import *
from unicorn.arm_const import *
b=Path('g2/build/pseudocode-first/20260930T190500Z');o=Path('/Users/kalani/Repo/evenRealities-openCFW/reviews/P2-touch-activation-adapters-independent-review-1551/001/run');o.mkdir(parents=True,exist_ok=True);src=b/'attempts/P2-touch-reset-pseudocode-108/001/touch.flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();rows=[];D=0x20002000;R=D+256;P=R+1024
cases=[(entry,0,0,status) for entry in [0x5ca2,0x7bb8] for status in [0,7,0xffffffff]]+[(0x5c7a,p,0,status) for p in [0,D] for status in [0,7,0xffffffff]]+[(0x5c8e,v,0,0) for v in [0,1,127,128,129,255,0xffffffff]]+[(0x5c02,idx,flag,status) for idx,flag,status in itertools.product(range(3),[0,7,255],[0,7,0xffffffff])]
for entry,a,flag,status in cases:
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x10000);u.mem_write(0x3300,d);u.mem_map(0x20000000,0x10000);u.mem_map(0x09000000,0x1000);args=[D,0x11223344,0x55667788,0x99aabbcc]
 helper={0x5ca2:0x7b62,0x7bb8:0x7b6a,0x5c7a:0x5c72,0x5c02:0x5bc0}.get(entry)
 if entry==0x5c7a:args[0]=a
 if entry==0x5c8e:u.mem_write(D+4,P.to_bytes(4,'little'));u.mem_write(P+8,a.to_bytes(4,'little'))
 if entry==0x5c02:args[:2]=[a,D];u.mem_write(D+12,R.to_bytes(4,'little'));u.mem_write(R+144*a+123,bytes([flag]))
 for r,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],args):u.reg_write(r,v)
 u.reg_write(UC_ARM_REG_SP,0x2000f000);u.reg_write(UC_ARM_REG_LR,0x09000001);calls=[]
 def code(u,p,s,x):
  if p==0x09000000:u.emu_stop()
  elif p==helper:calls.append([u.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]]);u.reg_write(UC_ARM_REG_R0,status);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,code);u.emu_start(entry|1,0,count=100)
 expected=status;expected_calls=[args]
 if entry==0x5c7a:expected=status if a else 1;expected_calls=[[0,5,a,args[3]]] if a else []
 if entry==0x5c8e:expected=a&128;expected_calls=[]
 if entry==0x5c02:expected=a if flag==7 else status;expected_calls=[] if flag==7 else [[args[0],args[1],123,flag]]
 assert calls==expected_calls and u.reg_read(UC_ARM_REG_R0)==expected and u.reg_read(UC_ARM_REG_PC)==0x09000000 and u.reg_read(UC_ARM_REG_SP)==0x2000f000
 rows.append(dict(entry=entry,args=args,flag=flag,status=status,calls=calls,result=expected))
bodies={};lines=[]
for a,z,nins in [(0x5c02,0x5c1e,13),(0x5c7a,0x5c8e,9),(0x5c8e,0x5c98,5),(0x5ca2,0x5caa,3),(0x7bb8,0x7bc0,3)]:
 body=d[a-0x3300:z-0x3300];assert len(body)==z-a;bodies[hex(a)]=dict(end=z,bytes=len(body),instructions=nins,sha256=h(body))
(o/'disassembly.txt').write_text('\n'.join(lines)+'\n');(o/'replays.json').write_text(json.dumps(rows,indent=2)+'\n');(o/'pseudocode.md').write_text(f'''# Activation adapters

5CA2 [5CA2,5CAA) and 7BB8 [7BB8,7BC0) preserve incoming arguments, call 7B62 and 7B6A respectively, forward the raw R0 result and restore an eight-byte frame.

5C7A [5C7A,5C8E) returns 1 for null incoming R0. Otherwise it calls 5C72 with R0=0, R1=5, R2=the incoming pointer and R3 unchanged; it forwards the raw result. It restores an eight-byte frame on both paths.

5C8E [5C8E,5C98) loads pointer at incoming R0+4, reads its word+8, and returns that word & 0x80. This is a raw mask result, either 0 or 128; there is no frame or helper.

5C02 [5C02,5C1E) takes index in R0 and descriptor in R1. Select record at descriptor word+12 + 144*index; if record byte123 is 7, return the unchanged incoming index without calling a helper. Otherwise call 5BC0 with original R0/R1, scratch R2=123 and R3=record byte123 and return its raw result. Restore the eight-byte frame.

{len(rows)} original-instruction fixtures check null handling, all three row indices, exact byte gating, status masks, raw return propagation, helper argument registers and stack restoration. Deeper callees remain controlled; no physical or whole-firmware claim is made. No canonical admission or C implementation.
''');(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(source=dict(path=str(src),sha256=h(d)),bodies=bodies,fixtures=len(rows),files={p.name:h(p.read_bytes()) for p in sorted(o.iterdir())},accepted=False),indent=2)+'\n');print('PASS',len(rows))
