# SPDX-License-Identifier: MIT
"""Qualify and export reconstructed DMA configuration for source admission."""
import json,shutil
from pathlib import Path
from verify_gx8002_dma_configure import verify as core,ROOT,sha
from verify_gx8002_logging import check_paths
from verify_gx8002_dma_configure_validation import verify as validation
from verify_gx8002_uart_transmit_configure import verify as uart


def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk)
    qualification=core();checks={'validation':validation(),'uart':uart()}
    candidate=qualification['candidate'];item=candidate['functions'][0]
    if not item['fits']:raise ValueError('DMA configuration envelope')
    row={key:item[key] for key in ('symbol','compiled_bytes','compiled_sha256')}
    row['section_name']='.text'
    row['stock_occurrences']=[{'symbol':item['symbol'],'package_offset':item['package_offset'],
        'bytes':item['envelope_bytes'],'sha256':item['stock_sha256'],'region':'image_a_xip_text'}]
    if output:
        output=Path(output);output.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/'build/gx8002-dma-configure/configure.elf',output/'configure.elf')
    evidence={name:sha((ROOT/'tools'/name).read_bytes()) for name in
        ('build_gx8002_dma_configure.py','verify_gx8002_dma_configure.py','verify_gx8002_dma_configure_source.py','verify_gx8002_memcpy_source.py','execute_gx8002_dma_configure.py',
         'verify_gx8002_dma_configure_validation.py','execute_gx8002_dma_configure_validation.py',
         'verify_gx8002_uart_transmit_configure.py')}
    return {'functions':[row],'qualification':qualification,'checks':checks,'evidence_sha256':evidence,
        'source_admitted':True,'hardware_qualified':False,
        'limits':['Decoded configuration, early rejection, capacity boundaries and nested UART clear/bus/descriptor/cache checks. Separate frames and descriptor memory; physical DMA and concurrency remain unqualified.']}

if __name__=='__main__':
    report=verify();(ROOT/'docs/research/gx8002-dma-configure-source-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print('DMA configuration source qualification passed')
