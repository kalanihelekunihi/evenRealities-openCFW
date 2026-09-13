# SPDX-License-Identifier: MIT
"""Admit source buffer initialization with decoded nested memory clears."""
import json,shutil
from verify_gx8002_buffer_initialize import verify as core,ROOT,sha
from verify_gx8002_logging import check_paths


def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk);qualification=core();candidate=qualification['candidate']
    if not candidate['fits']:raise ValueError('Buffer initializer envelope')
    symbol='open_cfw_gx8002_buffer_initialize'
    row={'symbol':symbol,'section_name':'.text','compiled_bytes':candidate['compiled_bytes'],
         'compiled_sha256':candidate['compiled_sha256'],'ownership_kind':'compiled_c',
         'stock_occurrences':[{'symbol':symbol,'package_offset':0x1034c,'bytes':172,
                               'sha256':candidate['stock_sha256'],'region':'image_a_xip_text'}]}
    if output:
        output.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/'build/gx8002-buffer-initialize/buffer.elf',output/'buffer.elf')
    files=('verify_gx8002_buffer_initialize_source.py','verify_gx8002_buffer_initialize.py',
           'build_gx8002_buffer_initialize.py','compare_gx8002_memset.py',
           'build_gx8002_memset_candidate.py','verify_gx8002_memcpy_source.py')
    return {'functions':[row],'qualification':qualification,
            'evidence_sha256':{name:sha((ROOT/'tools'/name).read_bytes()) for name in files},
            'source_admitted':True,'hardware_qualified':False,
            'limits':['Fixed firmware RAM layout; nested decoded stock/source clears and neighboring memory checked. Physical startup, timing and concurrent access remain unqualified.']}


if __name__=='__main__':
    report=verify()
    (ROOT/'docs/research/gx8002-buffer-initialize-source-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Buffer initializer source admission passed')
