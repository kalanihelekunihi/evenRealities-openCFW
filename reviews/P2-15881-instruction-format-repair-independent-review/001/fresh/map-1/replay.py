from pathlib import Path
import json,hashlib
from capstone import *
from capstone.arm import ARM_OP_MEM,ARM_REG_PC
b=Path('g2/build/pseudocode-first/20260930T190500Z');src=b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';c=Cs(CS_ARCH_ARM,CS_MODE_THUMB|CS_MODE_MCLASS);c.detail=True;ranges=[];refs=[]
for a,z in [(0x480826,0x48086a)]:
 raw=d[a-0x438000:z-0x438000];ins=[]
 for i in c.disasm(raw,a):
  ins.append(dict(address=i.address,bytes=i.bytes.hex(),mnemonic=i.mnemonic,operands=i.op_str))
  for op in i.operands:
   if op.type==ARM_OP_MEM and op.mem.base==ARM_REG_PC:
    p=((i.address+4)&~3)+op.mem.disp;refs.append(dict(consumer=i.address,address=p,word=int.from_bytes(d[p-0x438000:p-0x438000+4],'little')))
 assert sum(len(bytes.fromhex(i['bytes'])) for i in ins)==z-a;ranges.append(dict(start=a,end=z,instructions=ins))
o=Path('reviews/P2-15881-instruction-format-repair-independent-review/001/fresh/map-1');o.mkdir(parents=True,exist_ok=False);(o/'instructions.json').write_text(json.dumps(ranges,indent=2)+'\n');(o/'pseudocode.md').write_text('Private scoped partial accepted:false. 68 instruction bytes. Frame24 R4R5R6R7R8LR; budgetR5=entryR0,addressR6=R1,maskR7=R2,expectedR8=R3,selectorR4=caller stackword. Repeated fresh register read, masked equality compared to full32 expected. UXT B selector nonzero success equality; zero success inequality. Success returns0 immediately even budget0. Failure oldbudget==0 returns4 after decrement wraps internally; otherwise budget-- and4807A0(1), retry. Thus initial read plus up to budget delay/read cycles; selector upperbits discarded. Poll has no register writes or interrupt changes. Timing/ROM/volatile external behavior and whole corpus C equality incomplete.\n');(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input=dict(path=str(src),sha256=h(d)),files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS',sum(r['end']-r['start'] for r in ranges),'instructionbytes',refs)
