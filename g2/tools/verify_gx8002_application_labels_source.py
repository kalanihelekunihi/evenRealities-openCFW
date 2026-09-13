# SPDX-License-Identifier: MIT
"""Admit readable application strings, excluding unqualified adjacent fill."""
import json,re,shutil
from build_gx8002_application_labels import build,ROOT,ROWS,sha,Elf32
from verify_gx8002_logging import check_paths

def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk);candidate=build();path=ROOT/'build/gx8002-application-labels/labels.elf';elf=Elf32(path.read_bytes(),'labels');rows=[]
    symbols={'soft_off':'open_cfw_gx8002_soft_off_label','sample_labels':'open_cfw_gx8002_sample_app_labels'}
    for name,offset,size in ROWS:
        s=next(s for s in elf.sections if s['name']=='.'+name);data=elf.contents(s);symbol=symbols[name];actual=next(s for s in elf.symbols() if s['name']==symbol);assert actual['value']==offset+0x101f6a74 and actual['size']==size
        rows.append({'symbol':symbol,'section_name':'.'+name,'ownership_kind':'generated_source_data','compiled_bytes':size,'compiled_sha256':sha(data),'stock_occurrences':[{'symbol':symbol,'package_offset':offset,'bytes':size,'sha256':sha(data),'region':'image_a_xip_text'}]})
    for name in sorted(set(re.findall(r"'(gx8002-[^']+\.json)'",(ROOT/'tools/build_gx8002_source_candidate.py').read_text()))):
        if name=='gx8002-application-labels-source-verification.json':continue
        p=ROOT/'docs/research'/name;assert p.exists();report=json.loads(p.read_text())
        for row in report.get('functions',[report]):
            for o in row.get('stock_occurrences',row.get('exact_stock_occurrences',[])):
                a=o.get('package_offset');n=o.get('bytes')
                if a is not None and n is not None:assert not any(a<start+size and start<a+n for _,start,size in ROWS),(name,o)
    assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    if output:
        output.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,output/'labels.elf')
    files=('build_gx8002_application_labels.py','verify_gx8002_application_labels_source.py')
    return {'functions':rows,'candidate':candidate,'evidence_sha256':{n:sha((ROOT/'tools'/n).read_bytes()) for n in files},'source_admitted':True,'hardware_qualified':False,'limits':['Readable source text exactly reproduces original address/length including terminators. Four adjacent zero bytes remain outside admission. No runtime reachability claim.','Experimental hybrid data replacement; original application source lineage and full firmware behavior remain incomplete.']}
if __name__=='__main__':
    r=verify();assert json.loads(json.dumps(r))==r;(ROOT/'docs/research/gx8002-application-labels-source-verification.json').write_text(json.dumps(r,indent=2)+'\n');print('Application label admission checks passed')
