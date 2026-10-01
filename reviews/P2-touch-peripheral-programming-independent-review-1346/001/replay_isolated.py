from pathlib import Path
import json,hashlib,itertools
from unicorn import *
from unicorn.arm_const import *
b=Path('g2/build/pseudocode-first/20260930T190500Z');o=Path('reviews/P2-touch-peripheral-programming-independent-review-1346/001/replay-output');o.mkdir(parents=True,exist_ok=False);src=b/'attempts/P2-touch-reset-pseudocode-108/001/touch.flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();rows=[]
for mode,flags,width in itertools.product([1,2,3],itertools.product([0,1],repeat=7),[0,1,16]):
 f1,f2,f5,f6,f7,f8,f9=flags
 if f1 and f5:continue
 cfg=bytearray(22);cfg[0]=mode;cfg[1]=f1;cfg[2]=f2;cfg[3]=12;cfg[4]=254;cfg[5]=f5;cfg[6]=f6;cfg[7]=f7;cfg[8]=f8;cfg[9]=f9;cfg[12:16]=width.to_bytes(4,'little');cfg[16:20]=width.to_bytes(4,'little');cfg[20:22]=(1234).to_bytes(2,'little')
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x10000);u.mem_write(0x3300,d);u.mem_map(0x20000000,0x10000);u.mem_write(0x20002000,bytes(cfg));u.mem_map(0x40250000,0x1000);u.mem_map(0x09000000,0x1000);u.reg_write(UC_ARM_REG_SP,0x2000f000);u.reg_write(UC_ARM_REG_LR,0x09000001)
 for r,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2],[0x40250000,0x20002000,0x20002100]):u.reg_write(r,v)
 writes=[]
 def code(u,p,s,x):
  if p==0x09000000:u.emu_stop()
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,lambda u,t,a,s,v,x:writes.append([a,s,v&((1<<(8*s))-1)]) if a<0x2000e000 or a>=0x40000000 else None);u.emu_start(0x98f5,0,count=300)
 ctl=(f5<<16)|(f8<<8);rx=(((width-1)&15)|(0 if f6 else 0x800)|(((width-1)<<4)&255)|(mode<<30))&0xffffffff
 p=[[0,ctl],[0x60,rx],[0,ctl&0xffff3fff],[0x80,f7<<31]]
 if mode!=1 and f9:p += [[0x300,0x307],[0x70,0x2a0003]]
 else:p += [[0x300,0x107],[0x70,0x2a1013]]
 p += [[0x304,15 if f1 else 0],[0x310,24|(254<<16)],[0x200,0x107],[0x204,8 if f2 else 1]]+[[x,0] for x in [0xec8,0xe88,0xfc8,0xf88,0xf08]]
 val=0 if mode==2 else 0x1d1;p += [[0xf48,val],[0xf48,val|(0x3000000 if f7 and mode!=2 else 0)]]
 expected=[[0x40250000+a,4,v] for a,v in p]+[[0x20002100,1,f1],[0x20002101,1,f2],[0x20002150,2,1234],[0x20002102,1,int(mode!=2 and bool(f7))],[0x20002104,4,0x10000000]]+[[0x20002100+x,4,0] for x in [8,0x18,0x20,0x40,0x3c,0x30,0x2c,0x44,0x48,0x4c]]
 assert writes==expected,(mode,flags,width,writes,expected)
 assert u.reg_read(UC_ARM_REG_PC)==0x09000000 and u.reg_read(UC_ARM_REG_R0)==0 and u.reg_read(UC_ARM_REG_SP)==0x2000f000
 rows.append(dict(mode=mode,flags=flags,width=width,writes=writes))
(o/'replays.json').write_text(json.dumps(rows,indent=2)+'\n');(o/'pseudocode.md').write_text('''# Touch 98F4 configuration programming

Body98F4..9AAA has438 instruction bytes, excluding NOP/literals. Guard behavior is separately recorded in1343. Valid paths derive control from boolean config bytes5/8 at bits16/8, store base+0, then derive base+60 from low four bits(width16-1), bit11 iff byte6zero, low byte((width12-1)<<4), and mode<<30. Freshly read control and maskFFFF3FFF. Store byte7 boolean atbit31 tobase+80.

If mode differs from1 and byte9nonzero, store307 atbase+300 and2A0003 at+70; otherwise107 and2A1013. Store15 iff byte1nonzero at+304; store lowbyte(byte3<<1) OR byte4<<16 at+310. Store107 at+200 and8 iff byte2nonzero otherwise1 at+204. Clear+EC8,+E88,+FC8,+F88,+F08. At+F48 store0 for mode2 otherwise1D1, freshly read it and OR03000000 iff byte7nonzero and mode differs from2, then store again.

Context receives byte1 at0, byte2 at1, halfword config+20 at+50, boolean(mode!=2 && byte7!=0) at2 and10000000 at4. Clear context word offsets8,18,20,40,3C,30,2C,44,48,4C. Returnzero and restoreframe. Null/error and guard paths are described in1343; continuation afterBKPT remains unresolved.

Receipt-derived original-instruction fixtures vary all seven boolean fields, all three modes and widths0/1/16, excluding the explicitly invalid simultaneous byte1/5 combination. Exact ordered peripheral/context writes match the independent model with no helper substitutions. Other signed-byte values and distinct width pairs are not fixture-covered. Physical peripheral behavior, concurrency and global ownership remain unresolved. No canonical admission or C implementation.
''');(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(source=dict(path=str(src),sha256=h(d)),fixtures=len(rows),files={p.name:h(p.read_bytes()) for p in sorted(o.iterdir())},accepted=False),indent=2)+'\n');print('PASS',len(rows))
