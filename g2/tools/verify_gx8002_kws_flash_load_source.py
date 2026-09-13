# SPDX-License-Identifier: MIT
"""Admit reconstructed loader and textual diagnostics with explicit repair."""
import json,shutil
from verify_gx8002_kws_flash_layout import verify as core,ROOT
from analyze_gx8002_upstream_objects import sha
from verify_gx8002_logging import check_paths

def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk);evidence=core();rows=[]
    for item in evidence['candidate']['functions']:
        if not item['fits']:raise ValueError('Loader envelope')
        row={k:item[k] for k in ('symbol','section_name','compiled_bytes','compiled_sha256','ownership_kind')}
        row['stock_occurrences']=[{'symbol':item['symbol'],'package_offset':item['package_offset'],'bytes':item['stock_envelope_bytes'],'sha256':item['stock_sha256'],'region':'image_a_xip_text' if item['ownership_kind']=='compiled_c' else 'image_a_xip_rodata'}]
        rows.append(row)
    if output:
        output.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/'build/gx8002-kws-flash-load/loader.elf',output/'loader.elf')
    files=('verify_gx8002_kws_flash_load_source.py','verify_gx8002_kws_flash_layout.py','build_gx8002_kws_flash_load.py','analyze_gx8002_kws_flash_load.py','verify_gx8002_memcpy_source.py')
    return {'functions':rows,'qualification':evidence,'evidence_sha256':{n:sha((ROOT/'tools'/n).read_bytes()) for n in files},'source_admitted':True,'hardware_qualified':False,
            'repair':'Initialize module/input/output to zero before publication; stock copied indeterminate stack words.',
            'limits':['Flash, clock and publication helper effects modeled; physical flash/NPU behavior unqualified. Model command and weight data remain opaque and separate.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-kws-flash-load-source-verification.json').write_text(json.dumps(r,indent=2)+'\n');print('Loader source admission passed')
