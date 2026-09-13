# SPDX-License-Identifier: MIT
"""Export reconstructed audio-output setters with strict qualification evidence."""
import json,shutil
from pathlib import Path
from verify_gx8002_audio_output_i2s_config import verify as core,ROOT,sha
from verify_gx8002_logging import check_paths
from analyze_gx8002_audio_output_i2s_mapping import analyze

def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk);qualification=core();mapping=analyze();rows=[]
    for item in qualification['candidate']['functions']:
        if not item['fits']:raise ValueError('Audio output setter envelope')
        row={key:item[key] for key in ('symbol','section_name','compiled_bytes','compiled_sha256')}
        row['stock_occurrences']=[{'symbol':item['symbol'],'package_offset':item['package_offset'],'bytes':item['stock_envelope_bytes'],'sha256':item['stock_sha256'],'region':'image_a_xip_text'}]
        rows.append(row)
    if output:
        output=Path(output);output.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/'build/gx8002-audio-output-i2s-config/bits.elf',output/'bits.elf')
    evidence=('build_gx8002_audio_output_i2s_config.py','verify_gx8002_audio_output_i2s_config.py','verify_gx8002_audio_output_i2s_config_source.py','verify_gx8002_memcpy_source.py','analyze_gx8002_audio_output_i2s_mapping.py')
    return {'functions':rows,'qualification':qualification,'field_mapping':mapping,'evidence_sha256':{name:sha((ROOT/'tools'/name).read_bytes()) for name in evidence},'source_admitted':True,'hardware_qualified':False,'limits':['Experimental function-level source admission; physical register semantics, caller composition and whole firmware source-only closure remain unqualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-audio-output-i2s-config-source-verification.json').write_text(json.dumps(r,indent=2)+'\n');print('Audio output setters source admission passed')
