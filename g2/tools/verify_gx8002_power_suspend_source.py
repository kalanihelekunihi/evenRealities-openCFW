# SPDX-License-Identifier: MIT
"""Admit reconstructed power suspend sequence."""
import json,shutil
from verify_gx8002_power_suspend import verify as core,ROOT,sha
from verify_gx8002_logging import check_paths


def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk);evidence=core();functions=[]
    for candidate in evidence['candidate']['functions']:
        if not candidate['fits']:raise ValueError('Initialization envelope')
        row={k:candidate[k] for k in ('symbol','section_name','compiled_bytes','compiled_sha256')}
        if 'ownership_kind' in candidate:row['ownership_kind']=candidate['ownership_kind']
        row['stock_occurrences']=[{'symbol':candidate['symbol'],'package_offset':candidate['package_offset'],
          'bytes':candidate['stock_envelope_bytes'],'sha256':candidate['stock_sha256'],'region':'image_a_xip_text'}]
        functions.append(row)
    if output:
        output.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/'build/gx8002-power-suspend/buffers.elf',output/'buffers.elf')
    files=('verify_gx8002_power_suspend_source.py','verify_gx8002_power_suspend.py','build_gx8002_power_suspend.py','verify_gx8002_memcpy_source.py','verify_gx8002_power_suspend.py')
    return {'functions':functions,'evidence':evidence,'source_admitted':True,'hardware_qualified':False,
      'evidence_sha256':{n:sha((ROOT/'tools'/n).read_bytes()) for n in files},
      'limits':evidence['limits']}


if __name__=='__main__':
    report=verify();(ROOT/'docs/research/gx8002-power-suspend-source-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('Power initialization source admission passed')
