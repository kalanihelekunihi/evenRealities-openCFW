# SPDX-License-Identifier: MIT
"""Admission gate for semantically reconstructed audio lookup data."""
import json,re,shutil
from build_gx8002_audio_mapping_tables import build,ROOT,ROWS,sha,Elf32
from verify_gx8002_logging import check_paths

def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk);candidate=build();path=ROOT/'build/gx8002-audio-mapping-tables/tables.elf';elf=Elf32(path.read_bytes(),'tables');rows=[]
    for name,offset,size in ROWS:
        s=next(s for s in elf.sections if s['name']=='.'+name);body=elf.contents(s);symbol='open_cfw_gx8002_'+name
        rows.append({'symbol':symbol,'section_name':'.'+name,'ownership_kind':'generated_source_data','compiled_bytes':size,'compiled_sha256':sha(body),'stock_occurrences':[{'symbol':symbol,'package_offset':offset,'bytes':size,'sha256':sha(body),'region':'image_a_xip_text'}]})
    for name in sorted(set(re.findall(r"'(gx8002-[^']+\.json)'",(ROOT/'tools/build_gx8002_source_candidate.py').read_text()))):
        if name=='gx8002-audio-mapping-tables-source-verification.json':continue
        p=ROOT/'docs/research'/name;assert p.exists();r=json.loads(p.read_text())
        for row in r.get('functions',[r]):
            for o in row.get('stock_occurrences',row.get('exact_stock_occurrences',[])):
                a=o.get('package_offset');n=o.get('bytes')
                if a is not None and n is not None:assert not any(a<start+size and start<a+n for _,start,size in ROWS),(name,o)
    if output:
        output.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,output/'tables.elf')
    files=('build_gx8002_audio_mapping_tables.py','verify_gx8002_audio_mapping_tables_source.py')
    return {'functions':rows,'candidate':candidate,'evidence_sha256':{n:sha((ROOT/'tools'/n).read_bytes()) for n in files},'source_admitted':True,'hardware_qualified':False,'limits':['Experimental source-data admission using PGA arithmetic and named channel selector definitions. Complete finite table domains checked; no raw binary arrays.','Does not claim tables remain reachable after consumer rewrites; full firmware source reconstruction remains incomplete.']}
if __name__=='__main__':
    r=verify();assert json.loads(json.dumps(r))==r;(ROOT/'docs/research/gx8002-audio-mapping-tables-source-verification.json').write_text(json.dumps(r,indent=2)+'\n');print('Audio table admission passed')
