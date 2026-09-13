# SPDX-License-Identifier: MIT
"""Admit PCM code and source-authored diagnostic with complete evidence."""
import json,shutil
from pathlib import Path
from verify_gx8002_audio_output_config_pcm import verify as core,ROOT,sha
from verify_gx8002_audio_output_config_pcm_clock import verify as clock
from verify_gx8002_audio_output_config_pcm_nested import verify as nested
from verify_gx8002_logging import check_paths

def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk);qualification=core();clock_report=clock();nested_report=nested();rows=[]
    for item in qualification['candidate']['functions']:
        if not item['fits']:raise ValueError('PCM envelope')
        row={key:item[key] for key in ('symbol','section_name','compiled_bytes','compiled_sha256')}
        row['ownership_kind']=item.get('ownership_kind','compiled_c')
        row['stock_occurrences']=[{'symbol':item['symbol'],'package_offset':item['package_offset'],'bytes':item['stock_envelope_bytes'],'sha256':item['stock_sha256'],'region':'image_a_xip_text' if row['ownership_kind']=='compiled_c' else 'image_a_xip_rodata'}]
        rows.append(row)
    if output:
        output=Path(output);output.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/'build/gx8002-audio-output-config-pcm/bits.elf',output/'bits.elf')
    evidence=('build_gx8002_audio_output_config_pcm.py','verify_gx8002_audio_output_config_pcm.py','verify_gx8002_audio_output_config_pcm_clock.py','verify_gx8002_audio_output_config_pcm_nested.py','verify_gx8002_audio_output_config_pcm_source.py','verify_gx8002_memcpy_source.py','verify_gx8002_audio_output_i2s_config.py','build_gx8002_audio_output_i2s_config.py','verify_gx8002_audio_output_dac.py','build_gx8002_audio_output_dac.py','verify_gx8002_audio_output_lodac.py','build_gx8002_audio_output_lodac.py')
    return {'functions':rows,'qualification':qualification,'clock_qualification':clock_report,'nested_qualification':nested_report,'evidence_sha256':{name:sha((ROOT/'tools'/name).read_bytes()) for name in evidence},'source_admitted':True,'hardware_qualified':False,'limits':['Experimental function and diagnostic source admission. Nonzero module frequency with zero sample_rate, invalid memory, physical hardware and whole-firmware closure remain unqualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-audio-output-config-pcm-source-verification.json').write_text(json.dumps(r,indent=2)+'\n');print('PCM code and diagnostic source admission passed')
