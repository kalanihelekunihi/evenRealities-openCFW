# SPDX-License-Identifier: MIT
"""Admit decoded audio-input environmental-noise query."""
import json,shutil
from verify_gx8002_audio_input_env_noise import verify as core,ROOT,sha
from verify_gx8002_logging import check_paths


def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk);evidence=core();candidate=evidence['candidate']
    if not candidate['fits']:raise ValueError('Configuration envelope')
    symbol='open_cfw_gx8002_audio_input_env_noise'
    row={'symbol':symbol,'section_name':'.text','compiled_bytes':candidate['compiled_bytes'],'compiled_sha256':candidate['compiled_sha256'],
         'stock_occurrences':[{'symbol':symbol,'package_offset':0x10b54,'bytes':124,'sha256':candidate['stock_sha256'],'region':'image_a_xip_text'}]}
    if output:
        output.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/'build/gx8002-audio-input-env-noise/index.elf',output/'noise.elf')
    files=('verify_gx8002_audio_input_env_noise_source.py','verify_gx8002_audio_input_env_noise.py','build_gx8002_audio_input_env_noise.py','verify_gx8002_memcpy_source.py')
    return {'functions':[row],'evidence':evidence,'source_admitted':True,'hardware_qualified':False,
      'evidence_sha256':{name:sha((ROOT/'tools'/name).read_bytes()) for name in files},
      'limits':['Fixed SDK board layout. Ordered state effects, thresholds, wrapping counters and overlapping storage checked; noise getter modeled. No physical startup, asynchronous concurrency or timing qualification.']}


if __name__=='__main__':
    report=verify();(ROOT/'docs/research/gx8002-audio-input-env-noise-source-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('Configuration callback source admission passed')
