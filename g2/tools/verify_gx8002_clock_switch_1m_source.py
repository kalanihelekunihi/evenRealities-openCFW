# SPDX-License-Identifier: MIT
"""Experimental admission of the recovered 1 MHz clock switch."""
import json,re,shutil
from verify_gx8002_clock_switch_1m_shared import verify as compare
from verify_gx8002_logging import check_paths
from analyze_gx8002_upstream_objects import ROOT,IMAGE,sha
from build_transparent_image import Elf32

def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk);evidence=compare();candidate=evidence['evidence']['candidate']
    path=ROOT/'build/gx8002-board/clock-switch-1m-candidate.elf';elf=Elf32(path.read_bytes(),str(path))
    expected={'.text':(0x17a28,116),'.rodata':(0x17ce4,16),'.pll':(0x188dc,56)}
    rows=[];stock=IMAGE.read_bytes()
    for section in elf.sections:
        if not section['flags']&2 or not section['size']:continue
        name=section['name']
        if name=='.saved_gate':
            if section['type']!=8 or section['address']!=0x20027318 or section['size']!=4 or section['flags']!=3 or elf.relocations(section['index']):raise ValueError('Runtime BSS allocation')
            continue
        if name not in expected:raise ValueError('Unexpected allocation')
        offset,size=expected[name];data=elf.contents(section)
        if section['address']!=offset+(0x2000dfec if name=='.pll' else 0x1000dfec) or len(data)>size or elf.relocations(section['index']):raise ValueError('Placement')
        if name!='.text' and data!=stock[offset:offset+size]:raise ValueError('Diagnostic mismatch')
        symbol='open_cfw_gx8002_clock_switch_1m'+('' if name=='.text' else '_'+name.split('.')[-1])
        rows.append({'symbol':symbol,'section_name':name,'ownership_kind':'compiled_c' if name=='.text' else 'generated_source_data','compiled_bytes':len(data),'compiled_sha256':sha(data),'stock_occurrences':[{'symbol':symbol,'package_offset':offset,'bytes':size,'sha256':sha(stock[offset:offset+size]),'region':'image_a_dram' if name=='.pll' else 'image_a_sram'}]})
    if len(rows)!=3 or any(s['name'] and s['section']==0 for s in elf.symbols()):raise ValueError('Missing/unresolved section')
    registry=(ROOT/'tools/build_gx8002_source_candidate.py').read_text()
    for name in set(re.findall(r"'(gx8002-[^']+\.json)'",registry)):
        if name=='gx8002-clock-switch-1m-source-verification.json':continue
        p=ROOT/'docs/research'/name
        if not p.exists():continue
        r=json.loads(p.read_text())
        for row in r.get('functions',[r]):
            for occurrence in row.get('stock_occurrences',row.get('exact_stock_occurrences',[])):
                start=occurrence.get('package_offset');size=occurrence.get('bytes')
                if start is not None and size is not None and any(start<o+n and o<start+size for o,n in expected.values()):raise ValueError(('Ownership overlap',name))
    if output:
        output.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,output/'clock-switch-1m.elf')
    files=('verify_gx8002_clock_switch_1m_source.py','verify_gx8002_clock_switch_1m_shared.py','verify_gx8002_clock_switch_1m.py','build_gx8002_clock_switch_1m_candidate.py','load_gx8002_clock_context.py','load_gx8002_clock_decoded_helpers.py','load_gx8002_divider_decoded_helpers.py')
    return {'runtime_state':candidate['runtime_state'],'functions':rows,'evidence':evidence,'evidence_sha256':{n:sha((ROOT/'tools'/n).read_bytes()) for n in files},'source_admitted':True,'hardware_qualified':False,'limits':evidence['limits']+['Experimental hybrid admission only; complete source-only firmware unfinished.']}

if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-clock-switch-1m-source-verification.json').write_text(json.dumps(r,indent=2)+'\n');print('1 MHz clock switch experimental admission passed')
