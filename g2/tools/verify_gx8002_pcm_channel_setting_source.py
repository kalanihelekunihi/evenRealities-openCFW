# SPDX-License-Identifier: MIT
"""Export qualified reconstructed PCM channel setup as source-owned code."""
import json,shutil
from pathlib import Path
from verify_gx8002_pcm_channel_setting import verify as core,ROOT,sha
from verify_gx8002_logging import check_paths


def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk);qualification=core();item=qualification['candidate']
    if not item['fits']:raise ValueError('PCM setting envelope')
    row={key:item[key] for key in ('symbol','compiled_bytes','compiled_sha256','section_name')}
    row['stock_occurrences']=[{'symbol':item['symbol'],'package_offset':item['package_offset'],'bytes':item['stock_envelope_bytes'],'sha256':item['stock_sha256'],'region':'image_a_xip_text'}]
    if output:
        output=Path(output);output.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/'build/gx8002-board/pcm-channel-setting-candidate.elf',output/'setting.elf')
    evidence=('build_gx8002_pcm_channel_setting_candidate.py','verify_gx8002_pcm_channel_setting.py','verify_gx8002_pcm_channel_setting_source.py','verify_gx8002_memcpy_source.py')
    return {'functions':[row],'qualification':qualification,'evidence_sha256':{name:sha((ROOT/'tools'/name).read_bytes()) for name in evidence},
        'source_admitted':True,'hardware_qualified':False,
        'limits':['Reconstructed C checked against authenticated SDK/stock instructions and independent ordered effects. Alignment-invalid inputs produce no MMIO writes. Valid hardware channel remains a caller contract; physical audio delivery unqualified.']}

if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-pcm-channel-setting-source-verification.json').write_text(json.dumps(r,indent=2)+'\n');print('PCM setting source admission passed')
