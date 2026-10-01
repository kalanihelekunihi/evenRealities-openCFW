from pathlib import Path
import json,hashlib,itertools,struct
from capstone import *
from unicorn import *
from unicorn.arm_const import *
b=Path('g2/build/pseudocode-first/20260930T190500Z');o=b/'analysis/touch-timing-adapters-1536/001';o.mkdir(parents=True,exist_ok=False);src=b/'attempts/P2-touch-reset-pseudocode-108/001/touch.flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();rows=[]
def machine(args):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x10000);u.mem_write(0x3300,d);u.mem_map(0x20000000,0x10000);u.mem_map(0x09000000,0x1000)
 for r,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2],args):u.reg_write(r,v)
 u.reg_write(UC_ARM_REG_SP,0x2000f000);u.reg_write(UC_ARM_REG_LR,0x09000001);return u
for a,bv,c in itertools.product([0,1,315,0xffffffff],[0,48,1000000,0xffffffff],[0,1,5,0xffffffff]):
 u=machine([a,bv,c]);pcs=[]
 def code(u,p,s,x):
  pcs.append(p)
  if p==0x09000000:u.emu_stop()
 u.hook_add(UC_HOOK_CODE,code);u.emu_start(0x5fa5,0,count=10000);expected=0xffffffff if c==0 else ((a*bv)&0xffffffff)//c
 assert u.reg_read(UC_ARM_REG_R0)==expected and u.reg_read(UC_ARM_REG_PC)==0x09000000 and u.reg_read(UC_ARM_REG_SP)==0x2000f000
 assert (0xa6c0 in pcs)==bool(c);rows.append(dict(entry=0x5fa4,args=[a,bv,c],result=expected,division_executed=bool(c)))
for a,freq in itertools.product([0,1,315,0xffff,0xffffffff],[0,1,48,255]):
 u=machine([a]);u.mem_write(0x20000870,bytes([freq]));calls=[]
 def code(u,p,s,x):
  if p==0x09000000:u.emu_stop()
  elif p==0x4480:calls.append(u.reg_read(UC_ARM_REG_R0));u.reg_write(UC_ARM_REG_R0,0x12345678);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,code);u.emu_start(0xa325,0,count=30)
 assert calls==[(a*freq)&0xffffffff] and u.reg_read(UC_ARM_REG_R0)==0x12345678 and u.reg_read(UC_ARM_REG_SP)==0x2000f000 and u.reg_read(UC_ARM_REG_PC)==0x09000000
 rows.append(dict(entry=0xa324,input=a,frequency_byte=freq,delay_args=calls,result=0x12345678))
md=Cs(CS_ARCH_ARM,CS_MODE_THUMB|CS_MODE_MCLASS);bodies={};lines=[]
for start,end in [(0x5fa4,0x5fba),(0xa324,0xa332)]:
 body=d[start-0x3300:end-0x3300];ins=list(md.disasm(body,start));assert sum(i.size for i in ins)==len(body);bodies[hex(start)]=dict(end=end,bytes=len(body),instructions=len(ins),sha256=h(body));lines.extend(f'{i.address:04X}: {i.mnemonic} {i.op_str}' for i in ins)
(o/'disassembly.txt').write_text('\n'.join(lines)+'\n');(o/'replays.json').write_text(json.dumps(rows,indent=2)+'\n');(o/'pseudocode.md').write_text('''# Touch timing adapters

5FA4 is the exact 22-byte body [5FA4,5FBA). Inputs are value, multiplier and divisor. If divisor is zero, return 0xFFFFFFFF without calling division. Otherwise multiply value by multiplier modulo 2^32, call A6C0 with that product and divisor, and return its quotient. The eight-byte frame is restored. All 64 fixtures execute the original division helper where applicable and compare the unsigned quotient, including overflow and large divisors.

A324 is the exact 14-byte body [A324,A332). Read a byte from literal address 0x20000870 (literal at A334), multiply the full incoming R0 by it modulo 2^32, and call 4480 with the product. Return its incidental R0 and restore the eight-byte frame. The machine body itself does not narrow the input to uint16, despite the historical upstream signature label. Twenty fixtures validate the full input width, frequency byte, wrapped product and helper result with 4480 controlled. The delay loop's separate recovery remains relevant; physical elapsed time is not established here.

These are private pseudocode evidence only. No canonical admission, whole-corpus freeze or C implementation is claimed.
''');(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(source=dict(path=str(src),sha256=h(d)),bodies=bodies,fixtures=len(rows),files={p.name:h(p.read_bytes()) for p in sorted(o.iterdir())},accepted=False),indent=2)+'\n');print('PASS',len(rows))
