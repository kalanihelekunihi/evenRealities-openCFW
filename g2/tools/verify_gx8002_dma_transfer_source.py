# SPDX-License-Identifier: MIT
"""Qualify and export reconstructed DMA transfer submission for source admission."""
import json,shutil
from pathlib import Path
from verify_gx8002_dma_transfer import verify as core,ROOT,sha
from verify_gx8002_logging import check_paths
from verify_gx8002_uart_transmit_configure import verify as composed


def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk)
    qualification=core();nested=json.loads(json.dumps(composed()))
    candidate=qualification['candidate'];item=candidate['functions'][0]
    if not item['fits']:raise ValueError('DMA transfer envelope')
    row={key:item[key] for key in ('symbol','compiled_bytes','compiled_sha256')}
    row['section_name']='.text'
    row['stock_occurrences']=[{'symbol':item['symbol'],'package_offset':item['package_offset'],
        'bytes':item['envelope_bytes'],'sha256':item['stock_sha256'],'region':'image_a_xip_text'}]
    if output:
        output=Path(output);output.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/'build/gx8002-dma-transfer/transfer.elf',output/'transfer.elf')
    evidence={name:sha((ROOT/'tools'/name).read_bytes()) for name in
        ('build_gx8002_dma_transfer.py','verify_gx8002_dma_transfer.py','verify_gx8002_dma_transfer_source.py','verify_gx8002_memcpy_source.py','verify_gx8002_uart_transmit_configure.py')}
    return {'functions':[row],'qualification':qualification,'configuration_composition':nested,'evidence_sha256':evidence,
        'source_admitted':True,'hardware_qualified':False,
        'limits':['Decoded transfer arguments, error handling and cache/MMIO order checked, including nested UART configuration with decoded helper bodies. Separate frames and descriptor memory; physical DMA and cache coherence remain unqualified.']}

if __name__=='__main__':
    report=verify();(ROOT/'docs/research/gx8002-dma-transfer-source-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print('DMA transfer source qualification passed')
