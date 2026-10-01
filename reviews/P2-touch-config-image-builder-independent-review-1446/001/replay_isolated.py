from pathlib import Path
import json,hashlib,struct,itertools
from unicorn import *
from unicorn.arm_const import *
b=Path('/Users/kalani/Repo/evenRealities-openCFW/g2/build/pseudocode-first/20260930T190500Z');o=Path('/Users/kalani/Repo/evenRealities-openCFW/reviews/P2-touch-config-image-builder-independent-review-1446/001/replay-output');o.mkdir(parents=True,exist_ok=False);src=b/'attempts/P2-touch-reset-pseudocode-108/001/touch.flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();L={a:struct.unpack_from('<I',d,a-0x3300)[0] for a in [0x5518,0x551c,0x5520,0x5524]};rows=[]
for fill,status in itertools.product([0,1,0xa5,0xff],[0,9,0xffffffff]):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x10000);u.mem_write(0x3300,d);u.mem_map(0x20000000,0x10000);u.mem_map(0x09000000,0x1000);D=0x20002000;C=0x20002100;F=0x20002200;O=0x20002300
 for a,v in [(D,F),(D+8,C),(D+36,O)]:u.mem_write(a,v.to_bytes(4,'little'))
 u.mem_write(C,bytes([fill])*128);u.mem_write(F,bytes([fill])*128);u.mem_write(O,bytes([0xcc])*112);u.reg_write(UC_ARM_REG_R0,D);u.reg_write(UC_ARM_REG_SP,0x2000f000);u.reg_write(UC_ARM_REG_LR,0x09000001);calls=[]
 def code(u,p,s,x):
  if p==0x09000000:u.emu_stop()
  elif p in [0x52bc,0x50e4]:calls.append([p,u.reg_read(UC_ARM_REG_R0)]);u.reg_write(UC_ARM_REG_R0,status if p==0x50e4 else 7);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,code);u.emu_start(0x5379,0,count=10000)
 half=fill*257;words={a:0 for a in [8,12,16,24,56,60,64,72,76,80,84,88,92,108]};words.update({0:L[0x5518]|((fill<<16)&0x30000),4:0x10000000|(fill&7)|((fill<<8)&256),20:fill,28:65536,48:257,96:L[0x551c],100:L[0x551c],104:L[0x551c]})
 words[8]=((half<<8)&0xf00 if half else 256)|(half&255 if half else 1)|((fill<<12)&4096)
 words[12]=(half&4095)|((half<<16)&L[0x5520]);words[24]=fill|((half<<16)&0xf0000)|((half<<8)&0x1f00);words[32]=(half&4095)|((fill<<16)&0xf0000);words[36]=0;words[44]=fill|(fill<<16);words[40]=fill<<8;words[68]=6|(((fill-1)<<16)&L[0x5524])
 expected=bytearray([0xcc]*112)
 for a,v in words.items():expected[a:a+4]=(v&0xffffffff).to_bytes(4,'little')
 assert bytes(u.mem_read(O,112))==expected and calls==[[0x52bc,D],[0x50e4,D]] and u.reg_read(UC_ARM_REG_R0)==status and u.reg_read(UC_ARM_REG_SP)==0x2000f000 and u.reg_read(UC_ARM_REG_PC)==0x09000000
 rows.append(dict(fill=fill,status=status,output=expected.hex(),words=words,calls=calls))
(o/'replays.json').write_text(json.dumps(rows,indent=2)+'\n');(o/'pseudocode.md').write_text('# Configuration image builder at 5378\n\nThe instruction body [5378,5518) is 416 bytes, followed by four literal words through 5528. Save the nine-word register frame and allocate 260 stack bytes. Original A9D4 clears 256 scratch bytes. Populate the output at descriptor word +36 with defaults, then combine fields from configuration descriptor word 0 and context descriptor word +8. The retained fixture word map gives exact independently computed outputs and masks; output word +52 is not written and retains its prior value.\n\nZero context halfword +68 substitutes 256 for its shifted field; zero halfword +66 substitutes 1 for its low byte. Other fields use explicit shift masks. Call 52BC(descriptor), ignore its return, then 50E4(descriptor) and return that status after restoring the frame. Both are controlled boundaries; original A9D4 executes. Twelve original-instruction fixtures vary uniform source fill and final status, checking all 112 output bytes and exact calls. Independent source-field variation, real downstream effects and physical meaning remain open. No canonical admission or C implementation.\n');(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(source=dict(path=str(src),sha256=h(d)),fixtures=len(rows),literals=L,files={p.name:h(p.read_bytes()) for p in sorted(o.iterdir())},accepted=False),indent=2)+'\n');print('PASS',len(rows))
