# SPDX-License-Identifier: MIT
"""Check scorer ELF ownership and authenticated reference inputs; no admission."""
import json,re
from pathlib import Path
from build_gx8002_max_score_candidate import build,ROOT,sha,Elf32
from analyze_gx8002_upstream_objects import IMAGE,IMAGE_SHA

def verify():
    candidate=build();p=ROOT/'build/gx8002-max-score/candidate.elf';elf=Elf32(p.read_bytes(),str(p))
    stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA:raise ValueError('Stock authentication')
    expected={'.text':(0x102086dc,0x11c68,420),'.rodata':(0x1020b276,0x14802,56)}
    rows=[]
    for section in elf.sections:
        if not section['flags']&2 or not section['size']:continue
        if section['name'] not in expected:raise ValueError(('Unexpected allocated section',section['name']))
        address,offset,envelope=expected[section['name']]
        if section['address']!=address or section['size']>envelope or elf.relocations(section['index']):raise ValueError('Placement or relocation')
        payload=elf.contents(section)
        if section['name']=='.rodata' and payload!=stock[offset:offset+envelope]:raise ValueError('Diagnostic source mismatch')
        rows.append({'section_name':section['name'],'address':address,'package_offset':offset,'compiled_bytes':len(payload),'compiled_sha256':sha(payload),'stock_envelope_bytes':envelope,'stock_sha256':sha(stock[offset:offset+envelope]),'ownership_kind':'compiled_c' if section['name']=='.text' else 'generated_source_data'})
    if {r['section_name'] for r in rows}!=set(expected):raise ValueError('Missing section')
    registry=(ROOT/'tools/build_gx8002_source_candidate.py').read_text();overlaps=[]
    for name in sorted(set(re.findall(r"'(gx8002-[^']+\.json)'",registry))):
        if name=='gx8002-max-score-source-verification.json':continue
        path=ROOT/'docs/research'/name
        if not path.exists():continue
        report=json.loads(path.read_text())
        for function in report.get('functions',[report]):
            for occurrence in function.get('stock_occurrences',function.get('exact_stock_occurrences',[])):
                a=occurrence.get('package_offset');n=occurrence.get('bytes')
                if a is None or n is None:continue
                for row in rows:
                    b=row['package_offset'];size=row['stock_envelope_bytes']
                    if a<b+size and b<a+n:overlaps.append({'report':name,'offset':a,'bytes':n,'candidate_section':row['section_name']})
    if overlaps:raise ValueError(('Existing ownership overlap',overlaps))
    return {'candidate':candidate,'regions':rows,'registered_overlap':overlaps,'source_admitted':False,'limits':['Placement and source-generated diagnostic ownership only. Behavioral qualifications are separate; no firmware replacement performed.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-max-score-placement.json').write_text(json.dumps(r,indent=2)+'\n');print(r['regions'])
