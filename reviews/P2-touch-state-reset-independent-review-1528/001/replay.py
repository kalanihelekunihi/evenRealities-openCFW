from pathlib import Path
import json,hashlib,struct,itertools
from unicorn import *
from unicorn.arm_const import *
b=Path('g2/build/pseudocode-first/20260930T190500Z');o=Path('/Users/kalani/Repo/evenRealities-openCFW/reviews/P2-touch-state-reset-independent-review-1528/001/run');o.mkdir(parents=True,exist_ok=True);src=b/'attempts/P2-touch-reset-pseudocode-108/001/touch.flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();L={a:struct.unpack_from('<I',d,a-0x3300)[0] for a in [0x68e0,0x68e4,0x68e8]};rows=[]
for old,ready,status in itertools.product([0,0xa5a5a5a5,0xffffffff],[0,1],[0,7,0xffffffff]):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x10000);u.mem_write(0x3300,d);u.mem_map(0x20000000,0x10000);u.mem_map(0x40000000,0x10000);u.mem_map(0x09000000,0x1000);D=0x20002000;F=0x20002100;X=0x20002200;C=0x20002300;P=0x40000000
 for a,v in [(D,F),(D+8,C),(F+8,X),(X,P),(P,old),(P+8,old),(P+0x180,ready)]:u.mem_write(a,v.to_bytes(4,'little'))
 u.mem_write(C+113,bytes([255]));u.reg_write(UC_ARM_REG_R0,D);u.reg_write(UC_ARM_REG_SP,0x2000f000);u.reg_write(UC_ARM_REG_LR,0x09000001);calls=[];writes=[]
 def code(u,p,s,x):
  if p==0x09000000:u.emu_stop()
  elif p==0x6608:calls.append([u.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2]]);u.reg_write(UC_ARM_REG_R0,status);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,lambda u,t,a,s,v,x:writes.append([a,s,v]) if a>=P or a==C+113 else None);u.emu_start(0x685d,0,count=150)
 expected=[[P,4,old&0x7fffffff],[P+0x80,4,0]]+([] if ready else [[P+0x144,4,1]])+[[P,4,old|0x80000000],[P+0x74,4,0],[P+0x128,4,0],[P+0x120,4,L[0x68e0]],[P+0x100,4,L[0x68e4]],[C+113,1,0],[P,4,(old|0x80000000)&L[0x68e8]],[P+8,4,old|0x10000000]]
 assert writes==expected and calls==([] if ready else [[315,0,D]]) and u.reg_read(UC_ARM_REG_R0)==(D if ready else status) and u.reg_read(UC_ARM_REG_SP)==0x2000f000 and u.reg_read(UC_ARM_REG_PC)==0x09000000
 rows.append(dict(old=old,ready=ready,status=status,writes=writes,calls=calls))
(o/'replays.json').write_text(json.dumps(rows,indent=2)+'\n');(o/'pseudocode.md').write_text('# State reset at 685C\n\nThe130-byte body [685C,68DE) is followed byalignment andthree literals. Resolveperipheralthroughdescriptor/configurationpointers. Clearcontrolbit31 andwrite0 at80. If freshlyreadword180 bit0clear,write1 at144 andcall6608(315,0,descriptor). Then setcontrolbit31,zero74 and128,write/readbackliteralvaluesat120 and100,clearcontextbyte113,andmaskcontrolwithFFFCFFFF. ORbit28intoword8. ReturnpreservedR0:descriptoronthefastpath,controlledhelperstatusonthecallpath. Restore16-byteframe.\n\nEighteenoriginal-instructionfixtures checkeveryorderedwrite,branch/helperarguments,returnandframe.6608remainscontrolledwithnoMMIOeffects;hardwarebehaviorissynthetic. Pointervalidityandphysicalmeaningremainopen. No canonicaladmission orCimplementation.\n');(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(source=dict(path=str(src),sha256=h(d)),fixtures=len(rows),literals=L,files={p.name:h(p.read_bytes()) for p in sorted(o.iterdir())},accepted=False),indent=2)+'\n');print('PASS',len(rows))
