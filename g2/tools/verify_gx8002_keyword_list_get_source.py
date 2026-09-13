# SPDX-License-Identifier: MIT
"""Source admission gate for the typed keyword-list accessor."""
import json,re,shutil
from verify_gx8002_keyword_list_get import verify as behavior,ROOT,sha,Elf32
from analyze_gx8002_upstream_objects import IMAGE,IMAGE_SHA
from verify_gx8002_logging import check_paths

def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk);qualification=behavior();path=ROOT/'build/gx8002-keyword-list-get/get.elf';elf=Elf32(path.read_bytes(),'get');s=next(s for s in elf.sections if s['name']=='.text');data=elf.contents(s);stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    assert s['address']==0x100264dc and len(data)==8 and data==stock[0x184f0:0x184f8]
    for name in sorted(set(re.findall(r"'(gx8002-[^']+\.json)'",(ROOT/'tools/build_gx8002_source_candidate.py').read_text()))):
        if name=='gx8002-keyword-list-get-source-verification.json':continue
        p=ROOT/'docs/research'/name;assert p.exists(),name;report=json.loads(p.read_text())
        for row in report.get('functions',[report]):
            for o in row.get('stock_occurrences',row.get('exact_stock_occurrences',[])):
                a=o.get('package_offset');n=o.get('bytes')
                if a is not None and n is not None:assert not(a<0x184f8 and 0x184f0<a+n),(name,o)
    symbol='open_cfw_gx8002_keyword_list_get'
    row={'symbol':symbol,'section_name':'.text','ownership_kind':'compiled_c','compiled_bytes':8,'compiled_sha256':sha(data),'stock_occurrences':[{'symbol':symbol,'package_offset':0x184f0,'bytes':8,'sha256':sha(data),'region':'image_a_sram'}]}
    if output:
        output.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,output/'get.elf')
    files=('build_gx8002_keyword_list_get.py','verify_gx8002_keyword_list_get.py','verify_gx8002_keyword_list_get_source.py')
    return {'functions':[row],'qualification':qualification,'evidence_sha256':{n:sha((ROOT/'tools'/n).read_bytes()) for n in files},'source_admitted':True,'hardware_qualified':False,'limits':['Experimental hybrid admission; typed accessor returns the authenticated existing source list allocation. Generated private literal included, no duplicate state.','Does not reconstruct remaining model data or establish physical firmware behavior.']}
if __name__=='__main__':
    r=verify();assert json.loads(json.dumps(r))==r;(ROOT/'docs/research/gx8002-keyword-list-get-source-verification.json').write_text(json.dumps(r,indent=2)+'\n');print('Keyword-list accessor admission gate passed')
