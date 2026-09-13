# SPDX-License-Identifier: MIT
"""Experimental admission of the upstream-derived complete clock initializer."""
import json,re,shutil
from verify_gx8002_clock_init_trim import verify as compare
from verify_gx8002_logging import check_paths
from analyze_gx8002_upstream_objects import ROOT,IMAGE,sha
from build_transparent_image import Elf32
from verify_gx8002_clock_init_bindings import verify as verify_bindings

def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk);evidence=json.loads(json.dumps(compare(True)))
    path=ROOT/'build/gx8002-board/clock-init-pointer-candidate.elf';elf=Elf32(path.read_bytes(),str(path))
    expected={'.text':(0x17a9c,564),'.rodata':(0x17cf4,36),'.trim':(0x18914,4),'.osc':(0x18918,80),'.xtal':(0x18968,80)}
    rows=[];stock=IMAGE.read_bytes()
    for section in elf.sections:
        if not section['flags']&2 or not section['size']:continue
        name=section['name']
        if name not in expected:raise ValueError('Unexpected allocation')
        offset,size=expected[name];data=elf.contents(section)
        if section['address']!=offset+(0x2000dfec if name in ('.trim','.osc','.xtal') else 0x1000dfec) or len(data)>size or elf.relocations(section['index']):raise ValueError('Placement')
        if name!='.text' and data!=stock[offset:offset+size]:raise ValueError('Diagnostic mismatch')
        symbol='open_cfw_gx8002_clock_init_pointer'+('' if name=='.text' else '_'+name.split('.')[-1])
        rows.append({'symbol':symbol,'section_name':name,'ownership_kind':'compiled_c' if name=='.text' else 'generated_source_data','compiled_bytes':len(data),'compiled_sha256':sha(data),'stock_occurrences':[{'symbol':symbol,'package_offset':offset,'bytes':size,'sha256':sha(stock[offset:offset+size]),'region':'image_a_dram' if name in ('.trim','.osc','.xtal') else 'image_a_sram'}]})
    if len(rows)!=5 or any(s['name'] and s['section']==0 for s in elf.symbols()):raise ValueError('Missing/unresolved section')
    registry=(ROOT/'tools/build_gx8002_source_candidate.py').read_text()
    for name in set(re.findall(r"'(gx8002-[^']+\.json)'",registry)):
        if name=='gx8002-clock-init-source-verification.json':continue
        p=ROOT/'docs/research'/name
        if not p.exists():continue
        r=json.loads(p.read_text())
        for row in r.get('functions',[r]):
            for occurrence in row.get('stock_occurrences',row.get('exact_stock_occurrences',[])):
                start=occurrence.get('package_offset');size=occurrence.get('bytes')
                if start is not None and size is not None and any(start<o+n and o<start+size for o,n in expected.values()):raise ValueError(('Ownership overlap',name))
    if output:
        output.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,output/'clock-init.elf')
    files=sorted({p.name for p in (ROOT/'tools').glob('*gx8002_clock_init*.py')})
    bindings=verify_bindings()
    return {'binding_ownership':bindings,'functions':rows,'evidence':evidence,'evidence_sha256':{n:sha((ROOT/'tools'/n).read_bytes()) for n in files},'source_admitted':True,'hardware_qualified':False,'limits':[
        'Experimental hybrid admission: decoded helper composition uses marshalled private frames and scripted mode/trim/lock/timer inputs.',
        'Gate lookup abstraction inherited from prior admission; physical boot and timing remain unqualified.',
        'Uses admitted corrected module switching and digital reserved-bit initialization; these deliberate differences remain explicit.',
        'PLL state and saved gate BSS are externally owned by the admitted 1 MHz clock switch; only this initializer code and four data sections are replaced.',
        'Invalid mode and trim values are injected defensive coverage, not decoded hardware query outputs.',
        'Complete source-only firmware remains unfinished.']}

if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-clock-init-source-verification.json').write_text(json.dumps(r,indent=2)+'\n');print('Clock initialization experimental admission passed')
