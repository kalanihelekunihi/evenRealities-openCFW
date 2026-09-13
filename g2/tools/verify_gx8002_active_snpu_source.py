# SPDX-License-Identifier: MIT
"""Qualification adapter for source active callback, shared pointer and BSS."""
import json,re,shutil
from verify_gx8002_active_snpu_queue import verify as queue
from verify_gx8002_active_snpu_ownership import verify as ownership
from build_gx8002_active_snpu_split import ROOT,IMAGE,IMAGE_SHA,sha,Elf32
from verify_gx8002_logging import check_paths

def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk);behavior=queue();state=ownership()
    assert not state['missing_artifacts'] and not state['overlapping_allocations']
    path=ROOT/'build/gx8002-board/active-snpu-split.elf';elf=Elf32(path.read_bytes(),'active split');assert sha(path.read_bytes())==state['candidate']['elf_sha256']
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    expected={'.text':(0x18354,24,'compiled_c'),'.pool':(0x184e8,4,'generated_source_data')};rows=[]
    for name,(offset,size,kind) in expected.items():
        s=next(s for s in elf.sections if s['name']==name);payload=elf.contents(s)
        assert s['address']==offset+0x1000dfec and len(payload)<=size and not elf.relocations(s['index'])
        assert bool(s['flags']&4)==(kind=='compiled_c')
        if kind=='generated_source_data':assert payload==stock[offset:offset+size]
        symbol='open_cfw_gx8002_active_snpu_callback' if name=='.text' else 'open_cfw_gx8002_active_snpu_queue_pointer'
        rows.append({'symbol':symbol,'section_name':name,'ownership_kind':kind,'compiled_bytes':len(payload),'compiled_sha256':sha(payload),'stock_occurrences':[{'symbol':symbol,'package_offset':offset,'bytes':size,'sha256':sha(stock[offset:offset+size]),'region':'image_a_sram'}]})
    registry=(ROOT/'tools/build_gx8002_source_candidate.py').read_text()
    for name in set(re.findall(r"'(gx8002-[^']+\.json)'",registry)):
        if name=='gx8002-active-snpu-source-verification.json':continue
        p=ROOT/'docs/research'/name
        if not p.exists():continue
        r=json.loads(p.read_text())
        for row in r.get('functions',[r]):
            for o in row.get('stock_occurrences',row.get('exact_stock_occurrences',[])):
                a=o.get('package_offset');n=o.get('bytes')
                if a is not None and n is not None:
                    assert not any(a<offset+size and offset<a+n for offset,size,_ in expected.values()),name
    if output:
        output.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,output/'active-snpu.elf')
    files=sorted({p.name for p in (ROOT/'tools').glob('*gx8002_active_snpu*.py')}|{'execute_gx8002_active_queue.py'})
    return {'functions':rows,'behavior':behavior,'ownership':state,'evidence_sha256':{n:sha((ROOT/'tools'/n).read_bytes()) for n in files},'source_admitted':True,'hardware_qualified':False,'limits':['Experimental hybrid admission; full composed build remains a separate check.','Compiler assembly pool relocation preserves exact stock instructions; pointer generated from source symbol. Queue initializer body and application lifecycle not fully composed; hardware execution unqualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-active-snpu-source-verification.json').write_text(json.dumps(r,indent=2)+'\n');print('Active SNPU qualification passed')
