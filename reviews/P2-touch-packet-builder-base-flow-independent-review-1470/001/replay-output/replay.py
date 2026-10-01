from pathlib import Path
import json,hashlib,itertools
from unicorn import *
from unicorn.arm_const import *
b=Path('/Users/kalani/Repo/evenRealities-openCFW/g2/build/pseudocode-first/20260930T190500Z');o=Path('/Users/kalani/Repo/evenRealities-openCFW/reviews/P2-touch-packet-builder-base-flow-independent-review-1470/001/replay-output');o.mkdir(parents=True,exist_ok=False);src=b/'attempts/P2-touch-reset-pseudocode-108/001/touch.flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();rows=[]
for group,mode117,mode116 in itertools.product([0,1],[0,2,5],[0,2,4]):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x10000);u.mem_write(0x3300,d);u.mem_map(0x20000000,0x10000);u.mem_map(0x09000000,0x1000);D=0x20002000;F=0x20002100;C=0x20002200;T=0x20002300;O=0x20002500;I=0x20002700
 for off,v in [(0,F),(8,C),(12,T),(20,I),(24,I),(40,O),(44,O),(48,I),(52,I)]:u.mem_write(D+off,v.to_bytes(4,'little'))
 for off,v in [(99,17),(100,31),(107,43),(109,59),(116,mode116),(117,mode117)]:u.mem_write(C+off,bytes([v]))
 u.reg_write(UC_ARM_REG_R0,group);u.reg_write(UC_ARM_REG_R1,D);u.reg_write(UC_ARM_REG_SP,0x2000f000);u.reg_write(UC_ARM_REG_LR,0x09000001);calls=[]
 def code(u,p,s,x):
  if p==0x09000000:u.emu_stop()
  elif p in [0x5548,0x5188]:calls.append([p]+[u.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]]);u.reg_write(UC_ARM_REG_R0,3);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,code);u.emu_start(0x56a5,0,count=2000)
 count=4 if group else 5;stride=44 if group else 28;expected=[]
 for i in range(count):expected.extend([[0x5548,group,i,O+stride*i,D],[0x5188,0,31,O+stride*i+(20 if group else 0)]])
 assert [c[:len(e)] for c,e in zip(calls,expected)]==expected and len(calls)==len(expected) and u.reg_read(UC_ARM_REG_R0)==3 and u.reg_read(UC_ARM_REG_SP)==0x2000f000 and u.reg_read(UC_ARM_REG_PC)==0x09000000
 rows.append(dict(group=group,mode117=mode117,mode116=mode116,calls=calls,return_value=3))
(o/'replays.json').write_text(json.dumps(rows,indent=2)+'\n');(o/'pseudocode.md').write_text('# Packet builder base flow at 56A4\n\nThe complete 452-byte body [56A4,5868) begins with the two-list mask described by 1467. Select a context mapping: mode +117 equal 2 uses +100, equal 5 uses +109, otherwise +99. Retain +100 separately. A second mapping uses +100 for mode +116 equal 2, +107 for mode 4, otherwise +99.\n\nGroup 1 selects descriptor output word +44, index-table word +52 and four iterations; other groups select words +40/+48 and five iterations. Each iteration calls 5548(group,index,currentOutput,descriptor). Read two halfwords from indexTable +4*index: the first selects a stride-144 record, the second selects its subrecord. Record mode +122 equal 1 uses the second mapping; mode 2 uses the first mapping; other modes use context +100. Group 1 advances output by 20 before 5188(mask,mapping,output), then by 24, giving stride44. Group0 stride is28. Extra list/subrecord mask paths remain outside these fixtures.\n\nEighteen original-instruction fixtures use record mode zero and empty lists, checking exact two-helper call sequences, mode selection setup, both iteration counts/strides, incidental R0 from the last controlled helper, and restored frame. 5548/5188 remain controlled. Full extra-mask behavior and their contracts remain open. No canonical admission or C implementation.\n');(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(source=dict(path=str(src),sha256=h(d)),fixtures=len(rows),files={p.name:h(p.read_bytes()) for p in sorted(o.iterdir())},accepted=False),indent=2)+'\n');print('PASS',len(rows))
