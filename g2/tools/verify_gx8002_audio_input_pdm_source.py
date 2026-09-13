# SPDX-License-Identifier: MIT
"""Export qualified reconstructed PDM input setup as source-owned code."""
import json,shutil
from pathlib import Path
from verify_gx8002_audio_input_pdm import verify as core,ROOT,sha
from verify_gx8002_logging import check_paths


def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk);qualification=core();item=qualification['candidate']
    if not item['fits']:raise ValueError('PDM setup envelope')
    row={key:item[key] for key in ('symbol','compiled_bytes','compiled_sha256')}
    row['section_name']='.text'
    row['stock_occurrences']=[{'symbol':item['symbol'],'package_offset':item['package_offset'],'bytes':item['stock_envelope_bytes'],'sha256':item['stock_sha256'],'region':'image_a_xip_text'}]
    if output:
        output=Path(output);output.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/'build/gx8002-audio-input-pdm/pdm.elf',output/'pdm.elf')
    evidence=('build_gx8002_audio_input_pdm.py','verify_gx8002_audio_input_pdm.py','verify_gx8002_audio_input_pdm_source.py','verify_gx8002_memcpy_source.py')
    return {'functions':[row],'qualification':qualification,'evidence_sha256':{name:sha((ROOT/'tools'/name).read_bytes()) for name in evidence},
        'source_admitted':True,'hardware_qualified':False,
        'limits':['Reconstructed C bitfield layout checked against stock and independent ordered register masks. Clock and delay helpers modeled with gate mutation and clobbers. Physical PDM input and delay timing unqualified.']}

if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-audio-input-pdm-source-verification.json').write_text(json.dumps(r,indent=2)+'\n');print('PDM setup source admission passed')
