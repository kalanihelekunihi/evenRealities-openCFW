# SPDX-License-Identifier: MIT
"""Check tick source pool against registered active callback ownership."""
import json
from build_gx8002_tws_tick_candidate import build,ROOT,Elf32,sha

def verify():
    evidence=build();path=ROOT/'build/gx8002-source-candidate/active-snpu/active-snpu.elf';elf=Elf32(path.read_bytes(),'owner')
    report=json.loads((ROOT/'docs/research/gx8002-active-snpu-source-verification.json').read_text())
    row=next(r for r in report['functions'] if r['section_name']=='.pool');section=next(s for s in elf.sections if s['name']=='.pool');data=elf.contents(section)
    assert sha(data)==row['compiled_sha256'] and len(data)==row['compiled_bytes']==4
    assert section['address']==0x100264d4 and data==(0x2002e6ec).to_bytes(4,'little')
    candidate=Elf32((ROOT/'build/gx8002-board/tws-tick-split.elf').read_bytes(),'tick');pool=next(s for s in candidate.sections if s['name']=='.pool')
    assert pool['address']==section['address'] and candidate.contents(pool)==data
    source=next(s for s in candidate.sections if s['name']=='.text');body=candidate.contents(source)
    # Independently decode CK804 short LRW: destination r0/r3 and imm8 words,
    # with the PC base rounded down to a word boundary.
    targets=[]
    for offset,reg in ((10,0),(64,3)):
        opcode=int.from_bytes(body[offset:offset+2],'little')
        assert opcode&0xf000==0x1000 and (opcode>>5)&7==reg
        displacement=(((opcode>>8)&3)<<5)|(opcode&31)
        target=((source['address']+offset)&~3)+4*displacement
        assert target==pool['address'];targets.append(target)
    return {'candidate':evidence,'owner_elf_sha256':sha(path.read_bytes()),'literal_targets':targets,'source_admitted':False,'limits':['Both encoded tick LRW targets resolve to already registered source-owned pointer. Tick admission must claim text only, avoiding duplicate pool ownership. Other tick qualification remains separate.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-tws-tick-pool.json').write_text(json.dumps(r,indent=2)+'\n');print(r['literal_targets'])
