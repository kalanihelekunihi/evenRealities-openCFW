# SPDX-License-Identifier: MIT
"""Admit decoded audio-input configuration callback."""
import json,shutil
from verify_gx8002_audio_input_config import verify as core,ROOT,sha
from verify_gx8002_logging import check_paths


def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk);evidence=core();candidate=evidence['candidate']
    if not candidate['fits']:raise ValueError('Configuration envelope')
    symbol='open_cfw_gx8002_audio_input_config'
    row={'symbol':symbol,'section_name':'.text','compiled_bytes':candidate['compiled_bytes'],'compiled_sha256':candidate['compiled_sha256'],
         'stock_occurrences':[{'symbol':symbol,'package_offset':0x107c0,'bytes':352,'sha256':candidate['stock_sha256'],'region':'image_a_xip_text'}]}
    if output:
        output.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/'build/gx8002-audio-input-config/index.elf',output/'config.elf')
    files=('verify_gx8002_audio_input_config_source.py','verify_gx8002_audio_input_config.py','build_gx8002_audio_input_config.py','verify_gx8002_memcpy_source.py')
    return {'functions':[row],'evidence':evidence,'source_admitted':True,'hardware_qualified':False,
      'evidence_sha256':{name:sha((ROOT/'tools'/name).read_bytes()) for name in files},
      'limits':['Fixed SDK board layout. Driver arguments, cached masks, bitfields and selected helper-induced mutations checked; helpers modeled. No physical startup, asynchronous concurrency or timing qualification.']}


if __name__=='__main__':
    report=verify();(ROOT/'docs/research/gx8002-audio-input-config-source-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('Configuration callback source admission passed')
