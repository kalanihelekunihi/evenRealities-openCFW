# SPDX-License-Identifier: MIT
"""Qualify and export reconstructed UART FIFO depth decoding for source admission."""
import json,shutil
from pathlib import Path
from verify_gx8002_uart_fifo_depth import verify as core,ROOT,sha
from verify_gx8002_logging import check_paths


def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk)
    qualification=core();candidate=qualification['candidate'];item=candidate['functions'][0]
    if not item['fits']:raise ValueError('UART FIFO depth envelope')
    row={key:item[key] for key in ('symbol','compiled_bytes','compiled_sha256')}
    row['section_name']='.text'
    row['stock_occurrences']=[{'symbol':item['symbol'],'package_offset':item['package_offset'],
        'bytes':item['envelope_bytes'],'sha256':item['stock_sha256'],'region':'image_a_xip_text'}]
    if output:
        output=Path(output);output.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/'build/gx8002-uart-fifo-depth/fifo_depth.elf',output/'fifo_depth.elf')
    evidence={name:sha((ROOT/'tools'/name).read_bytes()) for name in
        ('build_gx8002_uart_fifo_depth.py','verify_gx8002_uart_fifo_depth.py','verify_gx8002_uart_fifo_depth_source.py','verify_gx8002_memcpy_source.py')}
    return {'functions':[row],'qualification':qualification,'evidence_sha256':evidence,
        'source_admitted':True,'hardware_qualified':False,
        'limits':['All 256 FIFO encodings checked with unrelated-bit patterns and two device bases. Ordered reads and preserved registers verified; physical FIFO behavior is unqualified.']}

if __name__=='__main__':
    report=verify();(ROOT/'docs/research/gx8002-uart-fifo-depth-source-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print('UART FIFO depth source qualification passed')
