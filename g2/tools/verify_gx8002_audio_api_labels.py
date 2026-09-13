# SPDX-License-Identifier: MIT
"""Check each diagnostic label address and exclusion from registered ownership."""
import json,re
from build_gx8002_audio_api_labels import build,ROOT,ROWS,sha,Elf32

def verify():
    candidate=build();path=ROOT/'build/gx8002-audio-api-labels/labels.elf';elf=Elf32(path.read_bytes(),'labels');allocated=[s for s in elf.sections if s['flags']&2 and s['size']];assert len(allocated)==4
    labels=[]
    for name,offset,size in ROWS:
        s=next(s for s in allocated if s['name']=='.'+name);body=elf.contents(s);assert s['address']==offset+0x101f6a74 and s['flags']==2 and not elf.relocations(s['index']);cursor=0
        for label in body.split(b'\0')[:-1]:
            assert label and all(32<=b<127 for b in label)
            labels.append({'label':label.decode(),'runtime_address':s['address']+cursor,'package_offset':offset+cursor,'bytes':len(label)+1});cursor+=len(label)+1
        assert cursor==size
    checked=0
    for name in sorted(set(re.findall(r"'(gx8002-[^']+\.json)'",(ROOT/'tools/build_gx8002_source_candidate.py').read_text()))):
        if name=='gx8002-audio-api-labels-source-verification.json':continue
        p=ROOT/'docs/research'/name;assert p.exists();r=json.loads(p.read_text());checked+=1
        for row in r.get('functions',[r]):
            for o in row.get('stock_occurrences',row.get('exact_stock_occurrences',[])):
                a=o.get('package_offset');n=o.get('bytes')
                if a is not None and n is not None:assert not any(a<start+size and start<a+n for _,start,size in ROWS),(name,o)
    assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    return {'candidate':candidate,'labels':labels,'checked_reports':checked,'source_admitted':False,'hardware_qualified':False,'limits':['All ten NUL-terminated labels retain exact original addresses and bytes in read-only sections, disjoint from registered ownership.','This verifies data replacement, not runtime reachability or additional API functionality. Source admission pending.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-audio-api-labels-verification.json').write_text(json.dumps(r,indent=2)+'\n');print('Diagnostic label addresses:',len(r['labels']))
