from pathlib import Path
import json,hashlib
from capstone import *
from capstone.arm import ARM_OP_MEM,ARM_REG_PC
b=Path('g2/build/pseudocode-first/20260930T190500Z');src=b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';c=Cs(CS_ARCH_ARM,CS_MODE_THUMB|CS_MODE_MCLASS);c.detail=True;ranges=[];refs=[]
for a,z in [(0x539994,0x539a40)]:
 raw=d[a-0x438000:z-0x438000];ins=[]
 for i in c.disasm(raw,a):
  ins.append(dict(address=i.address,bytes=i.bytes.hex(),mnemonic=i.mnemonic,operands=i.op_str))
  for op in i.operands:
   if op.type==ARM_OP_MEM and op.mem.base==ARM_REG_PC:
    p=((i.address+4)&~3)+op.mem.disp;refs.append(dict(consumer=i.address,address=p,word=int.from_bytes(d[p-0x438000:p-0x438000+4],'little')))
 assert sum(len(bytes.fromhex(i['bytes'])) for i in ins)==z-a;ranges.append(dict(start=a,end=z,instructions=ins))
o=Path('reviews/P2-15881-instruction-format-repair-independent-review/001/fresh/map-4');o.mkdir(parents=True,exist_ok=False);(o/'instructions.json').write_text(json.dumps(ranges,indent=2)+'\n');(o/'pseudocode.md').write_text('Private scoped partial accepted:false.172 instruction bytes. Both leaves validate handle nonnull and (handleword &01FFFFFFhex)==literal tag else2; high7bits ignored includes lifecycleflags. Enable994 reads handleoffset4 then discards value, fresh handlewordbit25 set returns0. Else hardware gate checks fresh registerbits19,18,17,16 sequentially shortcircuit all mustset else7. Success fresh controlregister OR20000000hex then freshhandleword OR02000000hex returns0. DisableA10 reads handleoffset4 then discards, fresh controlregister clearsbit29, freshhandleword clearsbit25 returns0. No stackframe/no interruptmask; ignored offset4reads still real accesses. Volatile ordering/peripheral/concurrency and wholecorpus C equality incomplete.\n');(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input=dict(path=str(src),sha256=h(d)),files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS',sum(r['end']-r['start'] for r in ranges),'instructionbytes',refs)
