# SPDX-License-Identifier: MIT
"""Qualify and export reconstructed UART receive DMA setup for source admission."""
import json,shutil
from pathlib import Path
from verify_gx8002_uart_receive_dma import verify as core,ROOT,sha
from verify_gx8002_logging import check_paths
from verify_gx8002_uart_receive_dma_select import verify as select
from verify_gx8002_uart_receive_dma_cache import verify as cache
from verify_gx8002_uart_receive_dma_callback import verify as callback


def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk)
    qualification=core();checks=json.loads(json.dumps({'select':select(),'cache':cache(),'callback':callback()}))
    candidate=qualification['candidate'];item=candidate['functions'][0]
    if not item['fits']:raise ValueError('UART receive DMA envelope')
    row={key:item[key] for key in ('symbol','compiled_bytes','compiled_sha256')}
    row['section_name']='.text'
    row['stock_occurrences']=[{'symbol':item['symbol'],'package_offset':item['package_offset'],
        'bytes':item['envelope_bytes'],'sha256':item['stock_sha256'],'region':'image_a_xip_text'}]
    if output:
        output=Path(output);output.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/'build/gx8002-uart-receive-dma/dma.elf',output/'dma.elf')
    evidence={name:sha((ROOT/'tools'/name).read_bytes()) for name in
        ('build_gx8002_uart_receive_dma.py','verify_gx8002_uart_receive_dma.py','verify_gx8002_uart_receive_dma_source.py','verify_gx8002_memcpy_source.py','verify_gx8002_uart_receive_dma_select.py',
         'verify_gx8002_uart_receive_dma_cache.py','verify_gx8002_uart_receive_dma_callback.py')}
    return {'functions':[row],'qualification':qualification,'compositions':checks,'evidence_sha256':evidence,
        'source_admitted':True,'hardware_qualified':False,
        'limits':['Decoded setup and separate allocation/cache/callback compositions. Valid UART ports are 0/1; stock error behavior retained for other ports. Transfer body and physical DMA receipt remain outside this finite admission scope.']}

if __name__=='__main__':
    report=verify();(ROOT/'docs/research/gx8002-uart-receive-dma-source-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print('UART receive DMA source qualification passed')
