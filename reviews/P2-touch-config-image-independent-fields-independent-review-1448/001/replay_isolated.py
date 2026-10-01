from pathlib import Path
import json,hashlib,struct,itertools
from unicorn import *
from unicorn.arm_const import *
b=Path('/Users/kalani/Repo/evenRealities-openCFW/g2/build/pseudocode-first/20260930T190500Z');o=Path('/Users/kalani/Repo/evenRealities-openCFW/reviews/P2-touch-config-image-independent-fields-independent-review-1448/001/replay-output');o.mkdir(parents=True,exist_ok=False);src=b/'attempts/P2-touch-reset-pseudocode-108/001/touch.flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();L={a:struct.unpack_from('<I',d,a-0x3300)[0] for a in [0x5518,0x551c,0x5520,0x5524]};rows=[]
for seed in range(128):
 status=[0,9,0xffffffff][seed%3];import random;rng=random.Random(seed);cb=bytes(rng.randrange(256) for _ in range(128));fb=bytes(rng.randrange(256) for _ in range(128))
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x10000);u.mem_write(0x3300,d);u.mem_map(0x20000000,0x10000);u.mem_map(0x09000000,0x1000);D=0x20002000;C=0x20002100;F=0x20002200;O=0x20002300
 for a,v in [(D,F),(D+8,C),(D+36,O)]:u.mem_write(a,v.to_bytes(4,'little'))
 u.mem_write(C,cb);u.mem_write(F,fb);u.mem_write(O,bytes([0xcc])*112);u.reg_write(UC_ARM_REG_R0,D);u.reg_write(UC_ARM_REG_SP,0x2000f000);u.reg_write(UC_ARM_REG_LR,0x09000001);calls=[]
 def code(u,p,s,x):
  if p==0x09000000:u.emu_stop()
  elif p in [0x52bc,0x50e4]:calls.append([p,u.reg_read(UC_ARM_REG_R0)]);u.reg_write(UC_ARM_REG_R0,status if p==0x50e4 else 7);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,code);u.emu_start(0x5379,0,count=10000)
 H=lambda a:int.from_bytes(cb[a:a+2],'little')
 words={a:0 for a in [16,56,60,64,72,76,80,84,88,92,108]}
 words.update({0:L[0x5518]|((cb[113]<<16)&0x30000),4:0x10000000|(fb[55]&7)|((fb[56]<<8)&256),20:cb[83],28:65536,48:257,96:L[0x551c],100:L[0x551c],104:L[0x551c]})
 words[8]=((H(68)<<8)&0xf00 if H(68) else 256)|(H(66)&255 if H(66) else 1)|((fb[54]<<12)&4096)
 words[12]=(H(48)&4095)|((H(50)<<16)&L[0x5520]);words[24]=cb[77]|((H(64)<<16)&0xf0000)|((H(62)<<8)&0x1f00);words[32]=(H(60)&4095)|((cb[78]<<16)&0xf0000);words[36]=0;words[44]=cb[79]|(cb[80]<<16);words[40]=cb[84]<<8;words[68]=6|(((cb[81]-1)<<16)&L[0x5524])
 expected=bytearray([0xcc]*112)
 for a,v in words.items():expected[a:a+4]=(v&0xffffffff).to_bytes(4,'little')
 assert bytes(u.mem_read(O,112))==expected and calls==[[0x52bc,D],[0x50e4,D]] and u.reg_read(UC_ARM_REG_R0)==status and u.reg_read(UC_ARM_REG_SP)==0x2000f000 and u.reg_read(UC_ARM_REG_PC)==0x09000000
 rows.append(dict(seed=seed,context=cb.hex(),config=fb.hex(),status=status,output=expected.hex(),words=words,calls=calls))
(o/'replays.json').write_text(json.dumps(rows,indent=2)+'\n');(o/'pseudocode.md').write_text('# Configuration builder independent-field checks\n\nThis extends packet 1445 with 128 reproducible independently varied context and configuration byte arrays. Every output word is computed from its exact source offsets using a separate explicit arithmetic map retained in replay.py and the fixture records. All 112 output bytes, including unwritten word +52, exact downstream call arguments, final status and frame restoration are checked against original 5378 instructions with original scratch clear A9D4.\n\n52BC and 50E4 remain controlled. These seeded cases supplement the zero/default cases in 1445 and do not exhaust all input combinations. Physical field meanings and downstream effects remain unresolved. No canonical admission or C implementation.\n');(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(source=dict(path=str(src),sha256=h(d)),fixtures=len(rows),literals=L,files={p.name:h(p.read_bytes()) for p in sorted(o.iterdir())},accepted=False),indent=2)+'\n');print('PASS',len(rows))
