# SPDX-License-Identifier: MIT
"""Qualify and export reconstructed UART transmit buffer submission for source admission."""
import json,shutil
from pathlib import Path
from verify_gx8002_uart_transmit_buffer import verify as core,ROOT,sha
from verify_gx8002_logging import check_paths


def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk)
    qualification=core();candidate=qualification['candidate'];item=candidate['functions'][0]
    if not item['fits']:raise ValueError('UART transmit buffer envelope')
    row={key:item[key] for key in ('symbol','compiled_bytes','compiled_sha256')}
    row['section_name']='.text'
    row['stock_occurrences']=[{'symbol':item['symbol'],'package_offset':item['package_offset'],
        'bytes':item['envelope_bytes'],'sha256':item['stock_sha256'],'region':'image_a_xip_text'}]
    if output:
        output=Path(output);output.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/'build/gx8002-uart-transmit-buffer/buffer.elf',output/'buffer.elf')
    evidence={name:sha((ROOT/'tools'/name).read_bytes()) for name in
        ('build_gx8002_uart_transmit_buffer.py','verify_gx8002_uart_transmit_buffer.py','verify_gx8002_uart_transmit_buffer_source.py','verify_gx8002_memcpy_source.py')}
    return {'functions':[row],'qualification':qualification,'evidence_sha256':evidence,
        'source_admitted':True,'hardware_qualified':False,
        'limits':['Finite stock/source ordered descriptor accesses, fifth stack argument, saved-register ABI and DMA/IRQ argument checks. Helper bodies modeled; physical buffer receipt and concurrency remain unqualified.']}

if __name__=='__main__':
    report=verify();(ROOT/'docs/research/gx8002-uart-transmit-buffer-source-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print('UART transmit buffer source qualification passed')
