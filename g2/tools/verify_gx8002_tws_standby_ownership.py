# SPDX-License-Identifier: MIT
"""Source-owned standby state and existing shared pool qualification."""
import json,re,subprocess
from build_gx8002_tws_standby_candidate import build,ROOT,sha,Elf32
from compare_gx8002_clear_bss import execute,START,END
from verify_gx8002_memcpy_source import decode

def verify():
    evidence=build();candidate=Elf32((ROOT/'build/gx8002-board/tws-standby-split.elf').read_bytes(),'standby');state=next(s for s in candidate.sections if s['name']=='.state')
    assert (state['address'],state['size'],state['type'],state['flags'])==(0x2002e738,8,8,3)
    owner_path=ROOT/'build/gx8002-source-candidate/active-snpu/active-snpu.elf';owner=Elf32(owner_path.read_bytes(),'pool');report=json.loads((ROOT/'docs/research/gx8002-active-snpu-source-verification.json').read_text());row=next(r for r in report['functions'] if r['section_name']=='.pool');pool=next(s for s in owner.sections if s['name']=='.pool')
    assert sha(owner.contents(pool))==row['compiled_sha256'] and pool['address']==0x100264d4 and owner.contents(pool)==(0x2002e6ec).to_bytes(4,'little')
    for name,offset in (('.setter',2),('.loop',0)):
        section=next(s for s in candidate.sections if s['name']==name);body=candidate.contents(section);opcode=int.from_bytes(body[offset:offset+2],'little');assert opcode&0xf000==0x1000 and (opcode>>5)&7==3
        target=((section['address']+offset)&~3)+4*((((opcode>>8)&3)<<5)|(opcode&31));assert target==pool['address']
    clear_path=ROOT/'build/gx8002-clear-bss/clear.elf';clear=Elf32(clear_path.read_bytes(),'clear');report=json.loads((ROOT/'docs/research/gx8002-clear-bss-verification.json').read_text());row=report['functions'][0];section=next(s for s in clear.sections if s['name']==row['section_name']);assert sha(clear.contents(section))==row['compiled_sha256']
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');trace=execute(decode(subprocess.check_output([pre,'-d',str(clear_path)],text=True)),section['address'],91);assert trace==[[a,0] for a in range(START,END,4)];assert dict(trace)[0x2002e738]==dict(trace)[0x2002e73c]==0
    checked=0
    for kind,artifact in re.findall(r"\('([^']+)',\s*\w+,\s*'([^']+)',\s*'gx8002-[^']+\.json'\)",(ROOT/'tools/build_gx8002_source_candidate.py').read_text()):
        if kind=='tws-standby':continue
        path=ROOT/'build/gx8002-source-candidate'/kind/artifact;assert path.exists(),kind;elf=Elf32(path.read_bytes(),str(path));checked+=1
        for s in elf.sections:
            if s['flags']&2 and s['size'] and s['address']:assert not (s['address']<0x2002e740 and 0x2002e738<s['address']+s['size']),(kind,s['name'])
    return {'candidate':evidence,'checked_artifacts':checked,'pool_owner_sha256':sha(owner_path.read_bytes()),'clear_elf_sha256':sha(clear_path.read_bytes()),'source_admitted':False,'limits':['Exact C BSS state, decoded startup zero and both encoded shared source pointer loads checked. Fixed-section audit excludes retained indirect writes and physical concurrency.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-tws-standby-ownership.json').write_text(json.dumps(r,indent=2)+'\n');print(r['checked_artifacts'])
