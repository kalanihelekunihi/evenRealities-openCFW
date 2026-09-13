# SPDX-License-Identifier: MIT
"""Admit Public channel code and source-defined diagnostic label with complete evidence."""
import json,shutil
from pathlib import Path
from verify_gx8002_audio_output_public_channel import verify as core,ROOT,sha
from verify_gx8002_logging import check_paths

def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk);qualification=core();rows=[]
    for item in qualification['candidate']['functions']:
        if not item['fits']:raise ValueError('Public channel envelope')
        row={key:item[key] for key in ('symbol','section_name','compiled_bytes','compiled_sha256')}
        row['ownership_kind']=item.get('ownership_kind','compiled_c')
        row['stock_occurrences']=[{'symbol':item['symbol'],'package_offset':item['package_offset'],'bytes':item['stock_envelope_bytes'],'sha256':item['stock_sha256'],'region':'image_a_xip_text' if row['ownership_kind']=='compiled_c' else 'image_a_xip_rodata'}]
        rows.append(row)
    if output:
        output=Path(output);output.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/'build/gx8002-audio-output-public-channel/bits.elf',output/'bits.elf')
    evidence=('build_gx8002_audio_output_public_channel.py','verify_gx8002_audio_output_public_channel.py','verify_gx8002_audio_output_public_channel_source.py','verify_gx8002_memcpy_source.py','analyze_gx8002_audio_output_public.py')
    return {'functions':rows,'qualification':qualification,'evidence_sha256':{name:sha((ROOT/'tools'/name).read_bytes()) for name in evidence},'source_admitted':True,'hardware_qualified':False,'limits':['Public channel and diagnostics source admission. Callback bodies, global BSS lifecycle, concurrent mutation outside tested boundary and whole-firmware closure remain unqualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-audio-output-public-channel-source-verification.json').write_text(json.dumps(r,indent=2)+'\n');print('Public channel code and diagnostic label source admission passed')
