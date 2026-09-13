# SPDX-License-Identifier: MIT
"""Admit source output configuration after decoded boundary qualification."""
import json,shutil
from verify_gx8002_audio_input_output import verify as core,ROOT,sha
from verify_gx8002_logging import check_paths


def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk);evidence=core();candidate=evidence['candidate']
    if not candidate['fits']:raise ValueError('Output configuration envelope')
    symbol='open_cfw_gx8002_audio_input_output'
    row={'symbol':symbol,'section_name':'.text','compiled_bytes':candidate['compiled_bytes'],'compiled_sha256':candidate['compiled_sha256'],
         'stock_occurrences':[{'symbol':symbol,'package_offset':0x105fc,'bytes':452,'sha256':candidate['stock_sha256'],'region':'image_a_xip_text'}]}
    if output:
        output.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/'build/gx8002-audio-input-output/index.elf',output/'output.elf')
    files=('verify_gx8002_audio_input_output_source.py','verify_gx8002_audio_input_output.py','gx8002_audio_input_output_oracle.py','build_gx8002_audio_input_output.py','verify_gx8002_memcpy_source.py')
    return {'functions':[row],'evidence':evidence,'source_admitted':True,'hardware_qualified':False,
      'evidence_sha256':{name:sha((ROOT/'tools'/name).read_bytes()) for name in files},
      'limits':['Fixed board layout; modeled returning drivers with selected synchronous board mutations. Decoded nested copies and by-value arguments checked. Physical hardware, asynchronous mutation and timing remain unqualified.']}


if __name__=='__main__':
    report=verify();(ROOT/'docs/research/gx8002-audio-input-output-source-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('Output configuration source admission passed')
