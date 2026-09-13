# SPDX-License-Identifier: MIT
"""Admission gate for reconstructed distance-noise MMIO query."""
import json,re,shutil
from verify_gx8002_distance_noise import verify as behavior,ROOT,IMAGE,IMAGE_SHA,sha,Elf32
from verify_gx8002_logging import check_paths

def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk);qualification=behavior();path=ROOT/'build/gx8002-distance-noise/noise.elf';elf=Elf32(path.read_bytes(),'noise');section=next(s for s in elf.sections if s['name']=='.text');data=elf.contents(section);stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    assert section['address']==0x102047ac and len(data)==12
    assert not any(elf.relocations(s['index']) for s in elf.sections)
    assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    checked=[]
    for name in sorted(set(re.findall(r"'(gx8002-[^']+\.json)'",(ROOT/'tools/build_gx8002_source_candidate.py').read_text()))):
        if name=='gx8002-distance-noise-source-verification.json':continue
        p=ROOT/'docs/research'/name;assert p.exists(),name;r=json.loads(p.read_text())
        for row in r.get('functions',[r]):
            for occurrence in row.get('stock_occurrences',row.get('exact_stock_occurrences',[])):
                a=occurrence.get('package_offset');size=occurrence.get('bytes')
                if a is not None and size is not None:assert not (a<0xdd44 and 0xdd38<a+size),(name,occurrence)
        checked.append(name)
    symbol='open_cfw_gx8002_distance_noise'
    row={'symbol':symbol,'section_name':'.text','ownership_kind':'compiled_c','compiled_bytes':12,'compiled_sha256':sha(data),'stock_occurrences':[{'symbol':symbol,'package_offset':0xdd38,'bytes':12,'sha256':sha(stock[0xdd38:0xdd44]),'region':'image_a_xip_text'}]}
    if output:
        output.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,output/'noise.elf')
    files=('build_gx8002_distance_noise.py','verify_gx8002_distance_noise.py','verify_gx8002_distance_noise_source.py','verify_gx8002_memcpy_source.py')
    return {'functions':[row],'qualification':qualification,'overlap_reports_checked':checked,'evidence_sha256':{n:sha((ROOT/'tools'/n).read_bytes()) for n in files},'source_admitted':True,'hardware_qualified':False,'limits':['Experimental hybrid admission. Compiler-generated private literal and alignment included in 12-byte function section; symbolic execution checks return before both.','Stock/SDK leaf identity and one-read behavior qualified; physical peripheral and complete firmware remain unqualified.']}
if __name__=='__main__':
    r=verify();assert json.loads(json.dumps(r))==r;(ROOT/'docs/research/gx8002-distance-noise-source-verification.json').write_text(json.dumps(r,indent=2)+'\n');print('Distance-noise admission gate passed')
