# SPDX-License-Identifier: MIT
"""Probe BSS placement versus materialized registered linked source allocations."""
import json,re
from build_transparent_image import Elf32
from build_gx8002_flash_probe_candidate import build,ROOT,sha


def verify():
    candidate=build();address=0x20026ff4;end=address+1
    text=(ROOT/'tools/build_gx8002_source_candidate.py').read_text()
    rows=re.findall(r"\('([^']+)',\s*\w+,\s*'([^']+)',\s*'(gx8002-[^']+\.json)'\)",text)
    checked=[];missing=[];relative=[]
    for kind,artifact,report in rows:
        if kind=='flash-probe':continue
        path=ROOT/'build/gx8002-source-candidate'/kind/artifact
        if not path.exists():missing.append(kind);continue
        elf=Elf32(path.read_bytes(),str(path));sections=0
        for section in elf.sections:
            if not section['flags']&2 or not section['size']:continue
            start=section['address']
            if start==0:
                if section['type']==8:relative.append({'kind':kind,'section':section['name'],'bytes':section['size']})
                continue
            if start<end and address<start+section['size']:raise ValueError(('Probe BSS overlaps registered allocation',kind,section['name']))
            sections+=1
        checked.append({'kind':kind,'elf_sha256':sha(path.read_bytes()),'fixed_allocations':sections})
    assert checked
    return {'candidate':candidate,'checked_artifacts':len(checked),'artifacts':checked,'missing_artifacts':missing,'unplaced_bss':relative,'source_admitted':False,
            'limits':['No overlap with materialized registered fixed-address ELF allocations. Missing artifacts and unplaced relocatable BSS are explicitly excluded.',
                       'Not a proof of absence of indirect firmware writers; retained code remains outside this source allocation audit.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-flash-probe-state.json').write_text(json.dumps(r,indent=2)+'\n');print(r['checked_artifacts'],r['missing_artifacts'],len(r['unplaced_bss']))
