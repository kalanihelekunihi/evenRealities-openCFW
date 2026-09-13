# SPDX-License-Identifier: MIT
"""Export qualified reconstructed I2S output setup as source-owned code."""
import json,shutil
from pathlib import Path
from verify_gx8002_audio_output_i2s import verify as core,ROOT,sha
from verify_gx8002_logging import check_paths


def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk);qualification=core();item=qualification['candidate']
    if not item['fits']:raise ValueError('I2S setup envelope')
    row={key:item[key] for key in ('symbol','compiled_bytes','compiled_sha256')}
    row['section_name']='.text'
    row['stock_occurrences']=[{'symbol':item['symbol'],'package_offset':item['package_offset'],'bytes':item['stock_envelope_bytes'],'sha256':item['stock_sha256'],'region':'image_a_xip_text'}]
    if output:
        output=Path(output);output.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/'build/gx8002-audio-output-i2s/i2s.elf',output/'i2s.elf')
    evidence=('build_gx8002_audio_output_i2s.py','verify_gx8002_audio_output_i2s.py','verify_gx8002_audio_output_i2s_source.py','verify_gx8002_memcpy_source.py')
    return {'functions':[row],'qualification':qualification,'evidence_sha256':{name:sha((ROOT/'tools'/name).read_bytes()) for name in evidence},
        'source_admitted':True,'hardware_qualified':False,
        'limits':['Pinned SDK aggregate ABI and C bitfield layout checked against stock and independent ordered masks, including raw unsigned format selection. Clock gate modeled with mutation and clobbers. Physical I2S/TDM behavior unqualified.']}

if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-audio-output-i2s-source-verification.json').write_text(json.dumps(r,indent=2)+'\n');print('I2S setup source admission passed')
