# SPDX-License-Identifier: MIT
"""Export qualified reconstructed PCM output input setup as source-owned code."""
import json,shutil
from pathlib import Path
from verify_gx8002_audio_output_pcm import verify as core,ROOT,sha
from verify_gx8002_logging import check_paths


def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk);qualification=core();item=qualification['candidate']
    if not item['fits']:raise ValueError('PCM output setup envelope')
    row={key:item[key] for key in ('symbol','compiled_bytes','compiled_sha256')}
    row['section_name']='.text'
    row['stock_occurrences']=[{'symbol':item['symbol'],'package_offset':item['package_offset'],'bytes':item['stock_envelope_bytes'],'sha256':item['stock_sha256'],'region':'image_a_xip_text'}]
    if output:
        output=Path(output);output.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/'build/gx8002-audio-output-pcm/pcm.elf',output/'pcm.elf')
    evidence=('build_gx8002_audio_output_pcm.py','verify_gx8002_audio_output_pcm.py','verify_gx8002_audio_output_pcm_source.py','verify_gx8002_memcpy_source.py','build_gx8002_pcm_channel_setting_candidate.py','verify_gx8002_pcm_channel_setting.py')
    return {'functions':[row],'qualification':qualification,'evidence_sha256':{name:sha((ROOT/'tools'/name).read_bytes()) for name in evidence},
        'source_admitted':True,'hardware_qualified':False,
        'limits':['Pinned SDK aggregate ABI and nested buffer helper checked against stock and independent ordered effects. Invalid selectors and unaligned buffers stop before output-state updates. Physical PCM delivery unqualified.']}

if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-audio-output-pcm-source-verification.json').write_text(json.dumps(r,indent=2)+'\n');print('PCM output setup source admission passed')
