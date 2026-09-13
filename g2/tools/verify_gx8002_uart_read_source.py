# SPDX-License-Identifier: MIT
"""Qualify recovered UART buffer read and decoded polling composition."""
import json,shutil
from pathlib import Path
from verify_gx8002_uart_read import verify as core,ROOT,sha
from verify_gx8002_uart_read_composition import verify as composed
from verify_gx8002_logging import check_paths


def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk)
    qualification=core();composition=json.loads(json.dumps(composed()))
    item=qualification['candidate']
    if not item['fits']:raise ValueError('UART read envelope')
    if composition['candidate']!=item:raise ValueError('UART read composition identity')
    symbol='open_cfw_gx8002_uart_read'
    row={'symbol':symbol,'compiled_bytes':item['compiled_bytes'],'compiled_sha256':item['compiled_sha256'],'section_name':'.text',
        'stock_occurrences':[{'symbol':symbol,'package_offset':item['package_offset'],'bytes':item['envelope_bytes'],'sha256':item['stock_sha256'],'region':'image_a_xip_text'}]}
    if output:
        output=Path(output);output.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/'build/gx8002-uart-read/read.elf',output/'read.elf')
    names=('build_gx8002_uart_read.py','verify_gx8002_uart_read.py','verify_gx8002_uart_read_composition.py','verify_gx8002_uart_read_source.py','verify_gx8002_memcpy_source.py','build_gx8002_uart_receive_byte.py','verify_gx8002_uart_receive_byte.py')
    return {'functions':[row],'qualification':qualification,'polling_composition':composition,
        'evidence_sha256':{name:sha((ROOT/'tools'/name).read_bytes()) for name in names},
        'source_admitted':True,'hardware_qualified':False,
        'limits':['Finite signed-length, byte forwarding and ordered memory checks, plus nested decoded polling including stalled prefixes. Peripheral stimuli modeled; physical UART timing and complete firmware execution unqualified.']}

if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-uart-read-source-verification.json').write_text(json.dumps(r,indent=2)+'\n');print('UART read admission passed')
