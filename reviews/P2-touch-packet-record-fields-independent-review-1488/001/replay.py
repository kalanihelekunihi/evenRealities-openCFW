from pathlib import Path
import json,hashlib,itertools
from unicorn import *
from unicorn.arm_const import *
b=Path('g2/build/pseudocode-first/20260930T190500Z');o=Path('/Users/kalani/Repo/evenRealities-openCFW/reviews/P2-touch-packet-record-fields-independent-review-1488/001');o.mkdir(parents=True,exist_ok=True);src=o/'touch.flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();rows=[]
for mode,enable,bypass,sub,threshold,fill in itertools.product([0,1,2,10],[0,1],[0,1],[0,1],[0,2],[0,1,255]):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x10000);u.mem_write(0x3300,d);u.mem_map(0x20000000,0x10000);u.mem_map(0x09000000,0x1000);D=0x20002000;C=0x20002100;T=0x20002200;R=0x20002400;G=0x20002500;F=0x20002600;A=0x20002700;I=0x20002800;O=0x20002900
 for off,v in [(4,F),(8,C),(12,T),(16,R)]:u.mem_write(D+off,v.to_bytes(4,'little'))
 u.mem_write(T,G.to_bytes(4,'little'));u.mem_write(T+4,A.to_bytes(4,'little'));u.mem_write(T+122,bytes([mode]));u.mem_write(T+58,bytes([threshold]));u.mem_write(I+2,sub.to_bytes(2,'little'));u.mem_write(F+8,(4096*bypass).to_bytes(4,'little'));u.mem_write(R+54,(fill*257).to_bytes(2,'little'))
 for off in [90,91,92]:u.mem_write(C+off,bytes([enable]))
 for off,v in [(46,11),(47,22),(48,33),(49,44),(51,55)]:u.mem_write(G+off,bytes([v]))
 u.mem_write(A+9,bytes([17]));u.mem_write(A+19,bytes([34]));u.mem_write(O,bytes([0xa5])*20);u.reg_write(UC_ARM_REG_R0,I);u.reg_write(UC_ARM_REG_R1,O);u.reg_write(UC_ARM_REG_R2,D);u.reg_write(UC_ARM_REG_SP,0x2000f000);u.reg_write(UC_ARM_REG_LR,0x09000001);u.hook_add(UC_HOOK_CODE,lambda u,p,s,x:u.emu_stop() if p==0x09000000 else None);u.emu_start(0x51bd,0,count=200)
 half=fill*257;word12=0xa5a5a5a5|((((half-1) if half else 0)<<16)&0x0fff0000);word16=(0xc00000|((55<<28)&0x70000000)) if mode in [1,2,10] and enable else 0x400000
 if not bypass:
  alt=mode==1 and threshold<=sub;word16|=(22 if alt else 11)|(((44 if alt else 33)<<16)&0x1f0000)
  if mode==1:word16|=([17,34][sub]<<8)
 expected=bytes([0xa5])*12+word12.to_bytes(4,'little')+word16.to_bytes(4,'little')
 assert bytes(u.mem_read(O,20))==expected and u.reg_read(UC_ARM_REG_R0)==0 and u.reg_read(UC_ARM_REG_SP)==0x2000f000 and u.reg_read(UC_ARM_REG_PC)==0x09000000
 rows.append(dict(mode=mode,enable=enable,bypass=bypass,sub=sub,threshold=threshold,fill=fill,output=expected.hex()))
(o/'replays.json').write_text(json.dumps(rows,indent=2)+'\n');(o/'pseudocode.md').write_text('# Packet record fields at 51BC\n\nThe 250-byte body [51BC,52B6) is followed by alignment and mask literal. Index pair halfwords select a stride144 record and its stride10 item. OR decremented-nonzero row-configuration halfword +54, shifted16 and masked0FFF0000, into output word12.\n\nStart output word16 at00400000. Record modes1/2/10 with matching context enable byte90/91/92 equal1 instead use00C00000 OR record-config byte51 shifted28 masked70000000. Descriptor word4 pointing to word+8 with bit12 set bypasses further fields. Otherwise combine config byte46 and byte48 shifted16 masked001F0000; mode1 with record byte58<=subindex uses bytes47/49 instead. Mode1 also ORs item byte9 shifted8. Store word16, return0 and restore frame.\n\nThe192 original-instruction fixtures distinguish source fields and cover enable,bypass,threshold,index andhalfwordcases, with no helpercontrols. Global ownership, pointervalidity andphysicalmeaningremainopen. No canonical admission or C implementation.\n');(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(source=dict(path=str(src),sha256=h(d)),fixtures=len(rows),files={p.name:h(p.read_bytes()) for p in sorted(o.iterdir())},accepted=False),indent=2)+'\n');print('PASS',len(rows))
