# SPDX-License-Identifier: MIT
"""Admission gate for the original upstream exception behavior and stack."""
import json,re,shutil
from verify_gx8002_exception_frame import verify as frame
from verify_gx8002_exception_ownership import verify as ownership
from verify_gx8002_exception_routing import verify as routing
from build_gx8002_exception_candidate import ROOT,IMAGE,sha,Elf32
from verify_gx8002_logging import check_paths

def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk);checks={'frame':frame(),'ownership':ownership(),'routing':routing()}
    path=ROOT/'build/gx8002-exception/exception.elf';elf=Elf32(path.read_bytes(),'exception');stock=IMAGE.read_bytes();rows=[]
    for name,symbol,offset,envelope,address,kind in (('.handler','trap_c',0x15604,12,0x100235f0,'compiled_c'),('.entry','trap',0x15610,80,0x100235fc,'compiled_assembly')):
        s=next(s for s in elf.sections if s['name']==name);data=elf.contents(s);assert s['address']==address and len(data)<=envelope and data==stock[offset:offset+len(data)]
        rows.append({'symbol':symbol,'section_name':name,'ownership_kind':kind,'compiled_bytes':len(data),'compiled_sha256':sha(data),'stock_occurrences':[{'symbol':symbol,'package_offset':offset,'bytes':envelope,'sha256':sha(stock[offset:offset+envelope]),'region':'image_a_sram'}]})
    assert not any(elf.relocations(s['index']) for s in elf.sections)
    for report_name in sorted(set(re.findall(r"'(gx8002-[^']+\.json)'",(ROOT/'tools/build_gx8002_source_candidate.py').read_text()))):
        if report_name=='gx8002-exception-source-verification.json':continue
        p=ROOT/'docs/research'/report_name;assert p.exists();r=json.loads(p.read_text())
        for row in r.get('functions',[r]):
            for occurrence in row.get('stock_occurrences',row.get('exact_stock_occurrences',[])):
                a=occurrence.get('package_offset');n=occurrence.get('bytes')
                if a is not None and n is not None:assert not(a<0x15660 and 0x15604<a+n),(report_name,occurrence)
    if output:
        output.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,output/'exception.elf')
    files=sorted(p.name for p in (ROOT/'tools').glob('*gx8002_exception*.py'))+['verify_gx8002_memcpy_source.py','compare_gx8002_clear_bss.py','analyze_g2_codec_stage2_sections.py']
    return {'functions':rows,'checks':checks,'evidence_sha256':{n:sha((ROOT/'tools'/n).read_bytes()) for n in files},'source_admitted':True,'hardware_qualified':False,'limits':['Experimental hybrid admission of existing stock exception behavior using unmodified Apache2.0 SDK sources. No missing application functionality replaced by a trap.','31 vector routes and single-entry frame qualified; physical dispatch, nested exceptions and invalid original stack not qualified. Complete source-only goal remains unfinished.']}
if __name__=='__main__':
    r=verify();assert json.loads(json.dumps(r))==r;(ROOT/'docs/research/gx8002-exception-source-verification.json').write_text(json.dumps(r,indent=2)+'\n');print('Exception admission checks passed')
