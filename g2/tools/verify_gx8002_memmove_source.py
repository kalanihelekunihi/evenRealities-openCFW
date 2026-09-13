# SPDX-License-Identifier: MIT
"""Source admission for decoded overlap-aware memory move."""
import json,shutil
from pathlib import Path
from verify_gx8002_memmove import verify as core,ROOT,sha
from verify_gx8002_logging import check_paths

def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk)
    qualification=core();candidate=qualification['candidate']
    if not candidate['fits']:raise ValueError('Memmove envelope')
    symbol=candidate['symbol']
    row={'symbol':symbol,'section_name':'.text','compiled_bytes':candidate['compiled_bytes'],
         'compiled_sha256':candidate['compiled_sha256'],'ownership_kind':'compiled_c',
         'stock_occurrences':[{'symbol':symbol,'package_offset':candidate['package_offset'],
                               'bytes':candidate['stock_envelope_bytes'],'sha256':candidate['stock_sha256'],
                               'region':'image_a_xip_text'}]}
    if output:
        output.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/'build/gx8002-memmove/memmove.elf',output/'memmove.elf')
    files=('verify_gx8002_memmove_source.py','verify_gx8002_memmove.py','build_gx8002_memmove_candidate.py','verify_gx8002_memcpy_source.py')
    return {'functions':[row],'qualification':qualification,
            'evidence_sha256':{name:sha((ROOT/'tools'/name).read_bytes()) for name in files},
            'source_admitted':True,'hardware_qualified':False,
            'limits':['Valid RAM with nonwrapping pointers. Nested source memcpy tested; physical timing and asynchronous memory mutation unqualified.']}
if __name__=='__main__':
    report=verify()
    (ROOT/'docs/research/gx8002-memmove-source-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Memmove source admission passed')
