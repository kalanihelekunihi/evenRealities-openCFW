from pathlib import Path
import json,hashlib
from capstone import *
from capstone.arm import ARM_OP_MEM,ARM_REG_PC
b=Path('g2/build/pseudocode-first/20260930T190500Z');src=b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';c=Cs(CS_ARCH_ARM,CS_MODE_THUMB|CS_MODE_MCLASS);c.detail=True;ranges=[];refs=[]
for a,z in [(0x5398e0,0x53993c),(0x539944,0x539994),(0x4800e4,0x4800f4),(0x48009e,0x4800de)]:
 raw=d[a-0x438000:z-0x438000];ins=[]
 for i in c.disasm(raw,a):
  ins.append(dict(address=i.address,bytes=i.bytes.hex(),mnemonic=i.mnemonic,operands=i.op_str))
  for op in i.operands:
   if op.type==ARM_OP_MEM and op.mem.base==ARM_REG_PC:
    p=((i.address+4)&~3)+op.mem.disp;refs.append(dict(consumer=i.address,address=p,word=int.from_bytes(d[p-0x438000:p-0x438000+4],'little')))
 assert sum(len(bytes.fromhex(i['bytes'])) for i in ins)==z-a;ranges.append(dict(start=a,end=z,instructions=ins))
o=Path('reviews/P2-15881-instruction-format-repair-independent-review/001/fresh/map-3');o.mkdir(parents=True,exist_ok=False);(o/'instructions.json').write_text(json.dumps(ranges,indent=2)+'\n');(o/'pseudocode.md').write_text('Private scoped partial accepted:false.252 instruction bytes across creation/release/status/powerdisable excluding literalpools. Create frame16R4R5R6LR: full32 index!=0 return5 before outputpointer nullcheck6. Slotwordbit24 occupied returns7. Else setbit24, freshslotword retain upperbyte ORliteral tag (tag has bit24), slot+4=index0,480058 ignoredreturn, write slotpointer tooutput,return0. Release frame16R3R4R5LR: null/bad maskedtag return2; valid SPbyte0=0, if freshwordbit25 set callsdisable539A10 result retained. Status4800E4 writes inverse MMIO bit31 toSPbyte andreturns0; ifbyte!=0 calls48009E ignoredresult; freshhandleword clearsbit24;returnretaineddisable result0. POPR1 entryR3 with lowbyte replaced status on valid path. Status leaf fresh MMIO ->1-bit31 tooutputbyte return0. Powerdisable48009E frame8R7LR criticalmaskSP0; fresh MMIO OR80000000 thenfresh OR40000000; chipwordlowbyte>=22hex invokesdelay4807A0(1), fresh otherregister OR00200000; restoremask return0 POPR1mask. External createpower helper/timing/physicalMMIO and whole corpus C equality incomplete.\n');(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input=dict(path=str(src),sha256=h(d)),files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS',sum(r['end']-r['start'] for r in ranges),'instructionbytes',refs)
