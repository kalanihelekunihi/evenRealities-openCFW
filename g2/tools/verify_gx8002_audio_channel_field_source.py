# SPDX-License-Identifier: MIT
"""Export qualified reconstructed PDM channel delay as source-owned code."""
import json,shutil
from pathlib import Path
from verify_gx8002_audio_channel_field import verify as core,ROOT,sha
from verify_gx8002_logging import check_paths
from analyze_gx8002_audio_channel_field import analyze


def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk);qualification=core();item=qualification['candidate'];provenance=analyze()
    if not item['fits']:raise ValueError('PDM channel delay envelope')
    row={key:item[key] for key in ('symbol','compiled_bytes','compiled_sha256')}
    row['section_name']='.text'
    row['stock_occurrences']=[{'symbol':item['symbol'],'package_offset':item['package_offset'],'bytes':item['stock_envelope_bytes'],'sha256':item['stock_sha256'],'region':'image_a_xip_text'}]
    if output:
        output=Path(output);output.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/'build/gx8002-audio-channel-field/field.elf',output/'field.elf')
    evidence=('build_gx8002_audio_channel_field.py','verify_gx8002_audio_channel_field.py','verify_gx8002_audio_channel_field_source.py','verify_gx8002_memcpy_source.py','analyze_gx8002_audio_channel_field.py')
    return {'functions':[row],'qualification':qualification,'caller_provenance':provenance,'evidence_sha256':{name:sha((ROOT/'tools'/name).read_bytes()) for name in evidence},
        'source_admitted':True,'hardware_qualified':False,
        'limits':['Experimental function-level admission; arithmetic and word-access behavior preserved for all tested inputs. Observed command270 uses index0/value1. Broader physical register domain and whole firmware source-only closure remain unqualified.']}


if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-audio-channel-field-source-verification.json').write_text(json.dumps(r,indent=2)+'\n');print('PDM channel delay source admission passed')
