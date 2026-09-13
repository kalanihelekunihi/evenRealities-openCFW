# SPDX-License-Identifier: MIT
"""Admit the upstream-derived scorer to the experimental hybrid build."""
import json,shutil
from verify_gx8002_max_score import verify as compare
from verify_gx8002_max_score_mutations import verify as mutations
from verify_gx8002_max_score_placement import verify as placement
from verify_gx8002_logging import check_paths
from analyze_gx8002_upstream_objects import ROOT,sha

def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk)
    baseline=compare();changed=mutations();layout=placement()
    if not baseline['candidate']==changed['candidate']==layout['candidate']:raise ValueError('Candidate changed across checks')
    rows=[]
    for region in layout['regions']:
        symbol='open_cfw_gx8002_max_score' if region['section_name']=='.text' else 'open_cfw_gx8002_max_score_diagnostic'
        rows.append({'symbol':symbol,'section_name':region['section_name'],'ownership_kind':region['ownership_kind'],'compiled_bytes':region['compiled_bytes'],'compiled_sha256':region['compiled_sha256'],'stock_occurrences':[{'symbol':symbol,'package_offset':region['package_offset'],'bytes':region['stock_envelope_bytes'],'sha256':region['stock_sha256'],'region':'image_a_xip_text'}]})
    files=('verify_gx8002_max_score_source.py','verify_gx8002_max_score.py','verify_gx8002_max_score_mutations.py','verify_gx8002_max_score_placement.py','execute_gx8002_max_score.py','build_gx8002_max_score_candidate.py','verify_gx8002_memcpy_source.py','verify_gx8002_power_initialize.py')
    notice=ROOT/'components/shared/gx8002/NATIONALCHIP-MAX-NOTICE.txt'
    if output:
        output.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/'build/gx8002-max-score/candidate.elf',output/'max-score.elf');shutil.copyfile(notice,output/notice.name)
    return {'functions':rows,'baseline':baseline,'mutations':changed,'placement':layout,'evidence_sha256':{name:sha((ROOT/'tools'/name).read_bytes()) for name in files},'notice_sha256':sha(notice.read_bytes()),'source_admitted':True,'hardware_qualified':False,'limits':['Experimental source replacement supported by bounded decoded comparisons and source provenance. Helpers remain modeled in this check. Floating exception flags/traps, alternate rounding modes, arbitrary invalid storage, concurrency and physical hardware remain unqualified. This admission does not establish complete source-only firmware.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-max-score-source-verification.json').write_text(json.dumps(r,indent=2)+'\n');print('MAX scorer experimental source qualification passed')
