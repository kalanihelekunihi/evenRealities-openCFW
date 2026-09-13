# SPDX-License-Identifier: MIT
"""Admit source-written audio API diagnostic labels."""
import json,shutil
from verify_gx8002_audio_api_labels import verify as core,ROOT,ROWS,sha,Elf32
from verify_gx8002_logging import check_paths

def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk);qualification=core();path=ROOT/'build/gx8002-audio-api-labels/labels.elf';elf=Elf32(path.read_bytes(),'labels');rows=[]
    for name,offset,size in ROWS:
        section=next(s for s in elf.sections if s['name']=='.'+name);body=elf.contents(section);symbol='open_cfw_gx8002_audio_labels_'+name
        rows.append({'symbol':symbol,'section_name':'.'+name,'ownership_kind':'generated_source_data','compiled_bytes':size,'compiled_sha256':sha(body),'stock_occurrences':[{'symbol':symbol,'package_offset':offset,'bytes':size,'sha256':sha(body),'region':'image_a_xip_text'}]})
    if output:
        output.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,output/'labels.elf')
    files=('build_gx8002_audio_api_labels.py','verify_gx8002_audio_api_labels.py','verify_gx8002_audio_api_labels_source.py')
    return {'functions':rows,'qualification':qualification,'evidence_sha256':{n:sha((ROOT/'tools'/n).read_bytes()) for n in files},'source_admitted':True,'hardware_qualified':False,'limits':['Experimental source data admission: readable API names, exact original addresses, pinned SDK provenance. No code or binary arrays introduced.','Runtime reachability and full firmware completion not established by string replacement.']}
if __name__=='__main__':
    r=verify();assert json.loads(json.dumps(r))==r;(ROOT/'docs/research/gx8002-audio-api-labels-source-verification.json').write_text(json.dumps(r,indent=2)+'\n');print('Audio API label admission passed')
