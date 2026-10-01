from pathlib import Path
import hashlib,json,itertools
from unicorn import *
from unicorn.arm_const import *
b=Path('g2/build/pseudocode-first/20260930T190500Z');o=Path('reviews/P2-touch-descriptor-validate-independent-review-1387/001/replay-output');o.mkdir(parents=True,exist_ok=False);src=b/'attempts/P2-touch-reset-pseudocode-108/001/touch.flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();offsets=[0,4,8,12,16,20,28];rows=[]
for flags in itertools.product([0,1],repeat=7):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x10000);u.mem_write(0x3300,d);u.mem_map(0x20000000,0x10000)
 for offset,present in zip(offsets,flags):u.mem_write(0x20002000+offset,(0xffffffff if present else 0).to_bytes(4,'little'))
 u.mem_map(0x09000000,0x1000);u.reg_write(UC_ARM_REG_SP,0x2000f000);u.reg_write(UC_ARM_REG_LR,0x09000001);u.reg_write(UC_ARM_REG_R0,0x20002000);reads=[]
 def code(u,p,s,x):
  if p==0x09000000:u.emu_stop()
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_READ,lambda u,t,a,s,v,x:reads.append([a,s]) if 0x20002000<=a<0x20002020 else None);u.emu_start(0x7d93,0,count=100)
 assert reads==[[0x20002000+x,4] for x in offsets] and u.reg_read(UC_ARM_REG_R0)==(0 if all(flags) else 2) and u.reg_read(UC_ARM_REG_PC)==0x09000000 and u.reg_read(UC_ARM_REG_SP)==0x2000f000
 rows.append(dict(present=flags,reads=reads,return_value=0 if all(flags) else 2))
(o/'replays.json').write_text(json.dumps(rows,indent=2)+'\n');(o/'pseudocode.md').write_text('''# Touch descriptor validation 7D92

Body7D92..7DDE is76 instructionbytes; next7DDEentry excluded. Load seven descriptorwords atoffsets0,4,8,C,10,14,1C, in that order, before checking any. Returnzero iff allseven words are nonzero; otherwise returntwo. Checks continue after eachnullvalue; loadedpointervalues are notdereferenced. Restorefive-wordframe. No guard for nullincomingdescriptor exists.

128 originalinstruction fixtures cover everyzero/nonzero fieldcombination. Exactsevenloadsequence,return andSP matchindependentmodel. Nonzerofields useallones to confirm no pointeeaccess. Actualpointervalidity,nonnull semanticcontracts andconcurrency remainunresolved. No canonicaladmission orCimplementation.
''');(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(source=dict(path=str(src),sha256=h(d)),fixtures=len(rows),files={p.name:h(p.read_bytes()) for p in sorted(o.iterdir())},accepted=False),indent=2)+'\n');print('PASS',len(rows))
