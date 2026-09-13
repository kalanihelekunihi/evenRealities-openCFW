# SPDX-License-Identifier: MIT
"""Experimental admission of the recovered stock MAX dispatcher."""
import json,re,shutil
from verify_gx8002_max_decoder import verify as compare
from verify_gx8002_logging import check_paths
from analyze_gx8002_upstream_objects import ROOT,sha
from build_transparent_image import Elf32

def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk);evidence=compare();candidate=evidence['candidate']
    path=ROOT/'build/gx8002-max-decoder/candidate.elf';elf=Elf32(path.read_bytes(),str(path))
    allocated=[s for s in elf.sections if s['flags']&2 and s['size']]
    if len(allocated)!=1:raise ValueError('Unexpected allocated sections')
    section=allocated[0]
    if section['name']!='.text' or section['address']!=0x102088f8 or not section['flags']&4 or not candidate['fits'] or elf.relocations(section['index']):raise ValueError('Placement/relocation')
    if sha(elf.contents(section))!=candidate['compiled_sha256']:raise ValueError('Payload')
    if any(s['name'] and s['section']==0 for s in elf.symbols()):raise ValueError('Unresolved symbol')
    registry=(ROOT/'tools/build_gx8002_source_candidate.py').read_text()
    for name in set(re.findall(r"'(gx8002-[^']+\.json)'",registry)):
        if name=='gx8002-max-decoder-source-verification.json':continue
        p=ROOT/'docs/research'/name
        if not p.exists():continue
        r=json.loads(p.read_text())
        for row in r.get('functions',[r]):
            for occurrence in row.get('stock_occurrences',row.get('exact_stock_occurrences',[])):
                start=occurrence.get('package_offset');size=occurrence.get('bytes')
                if start is not None and size is not None and start<0x11ed0 and 0x11e84<start+size:raise ValueError(('Ownership overlap',name))
    if output:
        output.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,output/'max-decoder.elf')
    files=('verify_gx8002_max_decoder_source.py','verify_gx8002_max_decoder.py','execute_gx8002_max_decoder.py','build_gx8002_max_decoder_candidate.py','verify_gx8002_memcpy_source.py','verify_gx8002_power_initialize.py')
    return {'functions':[{'symbol':'open_cfw_gx8002_max_decoder','section_name':'.text','compiled_bytes':candidate['compiled_bytes'],'compiled_sha256':candidate['compiled_sha256'],'stock_occurrences':[{'symbol':'LvpDoMaxDecoder','package_offset':0x11e84,'bytes':76,'sha256':candidate['stock_sha256'],'region':'image_a_xip_text'}]}],'evidence':evidence,'evidence_sha256':{n:sha((ROOT/'tools'/n).read_bytes()) for n in files},'source_admitted':True,'hardware_qualified':False,'limits':evidence['limits']+['Experimental hybrid admission only; complete source-only firmware remains unfinished.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-max-decoder-source-verification.json').write_text(json.dumps(r,indent=2)+'\n');print('MAX decoder experimental admission passed')
