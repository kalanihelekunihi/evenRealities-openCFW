# SPDX-License-Identifier: MIT
"""Admit VAD-query C and readable diagnostics after decoded qualification."""
import json,shutil
from verify_gx8002_vad_query_complete import check as complete,ROOT
from verify_gx8002_vad_query_result import check as results
from verify_gx8002_vad_query_weight_padding import check as padding
from analyze_gx8002_upstream_objects import sha
from verify_gx8002_logging import check_paths


def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk);full=complete();result=results();weights=padding();candidate=full['transitions']['candidate']
    if candidate!=result['transitions']['candidate'] or not candidate['fits']:raise ValueError('Query candidate consistency')
    symbol='open_cfw_gx8002_audio_input_query_vad'
    rows=[{'symbol':symbol,'section_name':'.text','compiled_bytes':candidate['compiled_bytes'],'compiled_sha256':candidate['compiled_sha256'],
      'stock_occurrences':[{'symbol':symbol,'package_offset':0x10990,'bytes':452,'sha256':candidate['stock_sha256'],'region':'image_a_xip_text'}]}]
    for d in candidate['diagnostics']:
        symbol='open_cfw_vad_level_'+str(d['level'])+'_message'
        rows.append({'symbol':symbol,'section_name':'.rodata.level'+str(d['level']),'compiled_bytes':d['bytes'],'compiled_sha256':d['sha256'],'ownership_kind':'generated_source_data',
          'stock_occurrences':[{'symbol':symbol,'package_offset':d['package_offset'],'bytes':d['bytes'],'sha256':d['sha256'],'region':'image_a_xip_rodata'}]})
    if output:
        output.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/'build/gx8002-audio-input-query-vad/index.elf',output/'query.elf')
    files=('verify_gx8002_audio_input_query_vad_source.py','verify_gx8002_vad_query_complete.py','verify_gx8002_vad_query_result.py','verify_gx8002_vad_query_transitions.py','verify_gx8002_vad_query_weight_padding.py','build_gx8002_audio_input_query_vad.py','verify_gx8002_audio_fftvad_w.py','build_gx8002_audio_fftvad_w.py','verify_gx8002_memcpy_source.py')
    return {'functions':rows,'complete':full,'result':result,'padding':weights,'source_admitted':True,'hardware_qualified':False,
      'evidence_sha256':{n:sha((ROOT/'tools'/n).read_bytes()) for n in files},
      'limits':['Fixed firmware state layout. Modeled hardware helpers; selected synchronous mutations checked. Weight ABI padding ignored only after consumer qualification. Physical behavior, asynchronous access and timing remain unqualified.']}


if __name__=='__main__':
    report=verify();(ROOT/'docs/research/gx8002-audio-input-query-vad-source-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('VAD query source admission passed')
