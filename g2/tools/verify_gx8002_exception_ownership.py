# SPDX-License-Identifier: MIT
"""Check upstream exception stack allocation against startup and linked owners."""
import json,re,subprocess
from build_gx8002_exception_candidate import build,ROOT,sha,Elf32
from compare_gx8002_clear_bss import execute,START,END
from verify_gx8002_memcpy_source import decode

def verify():
    candidate=build();path=ROOT/'build/gx8002-exception/exception.elf';elf=Elf32(path.read_bytes(),'exception');s=next(s for s in elf.sections if s['name']=='.stack');start=s['address'];end=start+s['size'];assert (start,end,s['type'],s['flags'])==(0x20027010,0x20027314,8,3)
    path=ROOT/'build/gx8002-clear-bss/clear.elf';elf=Elf32(path.read_bytes(),'clear');report=json.loads((ROOT/'docs/research/gx8002-clear-bss-verification.json').read_text());row=report['functions'][0];s=next(s for s in elf.sections if s['name']==row['section_name']);assert sha(elf.contents(s))==row['compiled_sha256']
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');trace=execute(decode(subprocess.check_output([pre,'-d',str(path)],text=True)),s['address'],91);assert trace==[[a,0] for a in range(START,END,4)]
    writes=dict(trace);assert all(writes[a]==0 for a in range(start,end,4));clear_sha=sha(path.read_bytes());checked=0
    for kind,artifact in re.findall(r"\('([^']+)',\s*\w+,\s*'([^']+)',\s*'gx8002-[^']+\.json'\)",(ROOT/'tools/build_gx8002_source_candidate.py').read_text()):
        if kind=='exception':continue
        path=ROOT/'build/gx8002-source-candidate'/kind/artifact;assert path.exists(),kind;elf=Elf32(path.read_bytes(),kind);checked+=1
        for s in elf.sections:
            if s['flags']&2 and s['size'] and s['address']:assert not(s['address']<end and start<s['address']+s['size']),(kind,s['name'],hex(s['address']))
    return {'candidate':candidate,'checked_artifacts':checked,'clear_elf_sha256':clear_sha,'cleared_words':(end-start)//4,'frame_start':0x20027310-72,'frame_end':0x20027310,'source_admitted':False,'hardware_qualified':False,'limits':['Source 768-byte stack plus saved-SP word is allocated, disjoint from fixed registered sections, and cleared by authenticated decoded startup.','Does not rule out retained indirect writes or qualify exception nesting and original-SP minus4 write. No firmware admission.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-exception-ownership.json').write_text(json.dumps(r,indent=2)+'\n');print('Exception stack words cleared:',r['cleared_words'])
