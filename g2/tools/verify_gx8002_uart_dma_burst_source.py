# SPDX-License-Identifier: MIT
"""Qualify and export reconstructed UART DMA burst selection for source admission."""
import json,shutil
from pathlib import Path
from verify_gx8002_uart_dma_burst import verify as core,ROOT,sha
from verify_gx8002_logging import check_paths
from verify_gx8002_uart_dma_burst_composition import verify as receive
from verify_gx8002_uart_transmit_dma_burst import verify as transmit


def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk)
    qualification=core();checks=json.loads(json.dumps({'receive':receive(),'transmit':transmit()}))
    candidate=qualification['candidate'];item=candidate['functions'][0]
    if not item['fits']:raise ValueError('UART DMA burst envelope')
    row={key:item[key] for key in ('symbol','compiled_bytes','compiled_sha256')}
    row['section_name']='.text'
    row['stock_occurrences']=[{'symbol':item['symbol'],'package_offset':item['package_offset'],
        'bytes':item['envelope_bytes'],'sha256':item['stock_sha256'],'region':'image_a_xip_text'}]
    if output:
        output=Path(output);output.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/'build/gx8002-uart-dma-burst/burst.elf',output/'burst.elf')
    evidence={name:sha((ROOT/'tools'/name).read_bytes()) for name in
        ('build_gx8002_uart_dma_burst.py','verify_gx8002_uart_dma_burst.py','verify_gx8002_uart_dma_burst_source.py','verify_gx8002_memcpy_source.py','verify_gx8002_uart_dma_burst_composition.py',
         'verify_gx8002_uart_transmit_dma_burst.py')}
    return {'functions':[row],'qualification':qualification,'compositions':checks,'evidence_sha256':evidence,
        'source_admitted':True,'hardware_qualified':False,
        'limits':['Decoded burst mapping and both descriptor reads checked, including receive/transmit setup compositions. Separate descriptor snapshots; physical concurrent mutation remains unqualified.']}

if __name__=='__main__':
    report=verify();(ROOT/'docs/research/gx8002-uart-dma-burst-source-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print('UART DMA burst source qualification passed')
