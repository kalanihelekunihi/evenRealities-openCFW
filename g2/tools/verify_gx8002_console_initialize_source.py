# SPDX-License-Identifier: MIT
"""Qualify and export reconstructed console initialization for source admission."""
import json,shutil
from pathlib import Path
from verify_gx8002_console_initialize import verify as core,ROOT,sha
from verify_gx8002_logging import check_paths


def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk)
    qualification=core();candidate=qualification['candidate'];item=candidate['functions'][0]
    if not item['fits'] or item['compiled_sha256']!=item['stock_sha256']:raise ValueError('Console initialization envelope')
    row={key:item[key] for key in ('symbol','compiled_bytes','compiled_sha256')}
    row['section_name']='.text'
    row['stock_occurrences']=[{'symbol':item['symbol'],'package_offset':item['package_offset'],
        'bytes':item['envelope_bytes'],'sha256':item['stock_sha256'],'region':'image_a_xip_text'}]
    if output:
        output=Path(output);output.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/'build/gx8002-console-initialize/initialize.elf',output/'initialize.elf')
    evidence={name:sha((ROOT/'tools'/name).read_bytes()) for name in
        ('build_gx8002_console_initialize.py','verify_gx8002_console_initialize.py','verify_gx8002_console_initialize_source.py','verify_gx8002_memcpy_source.py','build_gx8002_uart_initialize.py','verify_gx8002_uart_initialize.py')}
    return {'functions':[row],'qualification':qualification,'evidence_sha256':evidence,
        'source_admitted':True,'hardware_qualified':False,
        'limits':['Byte-identical wrapper preserves port storage before initialization and forwards arguments and result. Nested initializer decoded; clock/configuration helper effects and physical console behavior remain unqualified.']}

if __name__=='__main__':
    report=verify();(ROOT/'docs/research/gx8002-console-initialize-source-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Console initialization source qualification passed')
