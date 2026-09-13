# SPDX-License-Identifier: MIT
"""Experimental admission of the recovered stock audio range callback."""
import json,re,shutil
from verify_gx8002_next_range import verify as compare
from verify_gx8002_logging import check_paths
from analyze_gx8002_upstream_objects import ROOT,sha
from build_transparent_image import Elf32

def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk);evidence=compare();candidate=evidence['candidate']
    path=ROOT/'build/gx8002-next-range/candidate.elf';elf=Elf32(path.read_bytes(),str(path))
    allocated=[s for s in elf.sections if s['flags']&2 and s['size']]
    if len(allocated)!=1:raise ValueError('Unexpected allocated sections')
    section=allocated[0]
    if section['name']!='.text' or section['address']!=0x10208d98 or not section['flags']&4 or not candidate['fits'] or elf.relocations(section['index']):raise ValueError('Placement/relocation')
    if sha(elf.contents(section))!=candidate['compiled_sha256']:raise ValueError('Payload')
    if any(s['name'] and s['section']==0 for s in elf.symbols()):raise ValueError('Unresolved symbol')
    registry=(ROOT/'tools/build_gx8002_source_candidate.py').read_text()
    for name in set(re.findall(r"'(gx8002-[^']+\.json)'",registry)):
        if name=='gx8002-next-range-source-verification.json':continue
        p=ROOT/'docs/research'/name
        if not p.exists():continue
        r=json.loads(p.read_text())
        for row in r.get('functions',[r]):
            for occurrence in row.get('stock_occurrences',row.get('exact_stock_occurrences',[])):
                start=occurrence.get('package_offset');size=occurrence.get('bytes')
                if start is not None and size is not None and start<0x12358 and 0x12324<start+size:raise ValueError(('Ownership overlap',name))
    if output:
        output.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,output/'next-range.elf')
    files=('verify_gx8002_next_range_source.py','verify_gx8002_next_range.py','execute_gx8002_next_range.py','build_gx8002_next_range_candidate.py','verify_gx8002_memcpy_source.py','verify_gx8002_power_initialize.py')
    return {'functions':[{'symbol':'open_cfw_gx8002_next_range','section_name':'.text','compiled_bytes':candidate['compiled_bytes'],'compiled_sha256':candidate['compiled_sha256'],'stock_occurrences':[{'symbol':'audio_range_callback','package_offset':0x12324,'bytes':52,'sha256':candidate['stock_sha256'],'region':'image_a_xip_text'}]}],'evidence':evidence,'evidence_sha256':{n:sha((ROOT/'tools'/n).read_bytes()) for n in files},'source_admitted':True,'hardware_qualified':False,'limits':evidence['limits']+['Experimental hybrid admission only; complete source-only firmware remains unfinished.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-next-range-source-verification.json').write_text(json.dumps(r,indent=2)+'\n');print('Audio range callback experimental admission passed')
