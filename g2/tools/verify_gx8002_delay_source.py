# SPDX-License-Identifier: MIT
"""Experimental admission of the recovered Delay routines."""
import json,re,shutil
from verify_gx8002_delay_nested import verify as compare
from verify_gx8002_logging import check_paths
from analyze_gx8002_upstream_objects import ROOT,IMAGE,sha
from build_transparent_image import Elf32
from verify_gx8002_memcpy_source import decode

def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk);evidence=compare();candidate=evidence['boundaries']['candidate']
    path=ROOT/'build/gx8002-board/delay-candidate.elf';elf=Elf32(path.read_bytes(),str(path))
    code=decode((ROOT/'build/gx8002-board/delay-candidate.disassembly.txt').read_text())
    branches=[(pc,args,width) for pc,(op,args,width) in code.items() if op=='bnezad']
    if len(branches)!=1:raise ValueError('Backoff branch count')
    pc,args,width=branches[0];target=int(args.split(',')[-1].strip(),0)
    if code[target]!=('mov','r0, r0',2) or pc!=target+2 or width!=4:raise ValueError('Inline backoff sequence')
    expected={'.text':(0x17958,72),'.milliseconds':(0x179a0,16)}
    rows=[];stock=IMAGE.read_bytes()
    for section in elf.sections:
        if not section['flags']&2 or not section['size']:continue
        name=section['name']
        if name not in expected:raise ValueError('Unexpected allocation')
        offset,size=expected[name];data=elf.contents(section)
        if section['address']!=offset+0x1000dfec or len(data)>size or elf.relocations(section['index']):raise ValueError('Placement')
        symbol='open_cfw_gx8002_delay_'+('us' if name=='.text' else 'ms')
        rows.append({'symbol':symbol,'section_name':name,'ownership_kind':'compiled_assembly' if name=='.text' else 'compiled_c','compiled_bytes':len(data),'compiled_sha256':sha(data),'stock_occurrences':[{'symbol':symbol,'package_offset':offset,'bytes':size,'sha256':sha(stock[offset:offset+size]),'region':'image_a_sram'}]})
    if len(rows)!=2 or any(s['name'] and s['section']==0 for s in elf.symbols()):raise ValueError('Missing/unresolved section')
    registry=(ROOT/'tools/build_gx8002_source_candidate.py').read_text()
    for name in set(re.findall(r"'(gx8002-[^']+\.json)'",registry)):
        if name=='gx8002-delay-source-verification.json':continue
        p=ROOT/'docs/research'/name
        if not p.exists():continue
        r=json.loads(p.read_text())
        for row in r.get('functions',[r]):
            for occurrence in row.get('stock_occurrences',row.get('exact_stock_occurrences',[])):
                start=occurrence.get('package_offset');size=occurrence.get('bytes')
                if start is not None and size is not None and any(start<o+n and o<start+size for o,n in expected.values()):raise ValueError(('Ownership overlap',name))
    if output:
        output.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,output/'delay.elf')
    files=('verify_gx8002_delay_source.py','verify_gx8002_delay_nested.py','verify_gx8002_delay.py','execute_gx8002_delay.py','build_gx8002_delay_candidate.py')
    evidence['ownership_note']='Conservative accounting: the entire 60-byte microsecond routine is classified compiled_assembly because it contains six bytes of authored inline assembly; the remaining instructions come from C. No retained binary payload.'
    return {'functions':rows,'evidence':evidence,'evidence_sha256':{n:sha((ROOT/'tools'/n).read_bytes()) for n in files},'source_admitted':True,'hardware_qualified':False,'limits':evidence['limits']+['Experimental hybrid admission only; complete source-only firmware unfinished.']}

if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-delay-source-verification.json').write_text(json.dumps(r,indent=2)+'\n');print('Delay routines experimental admission passed')
