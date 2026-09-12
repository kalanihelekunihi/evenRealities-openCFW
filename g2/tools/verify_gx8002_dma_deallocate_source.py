# SPDX-License-Identifier: MIT
"""Qualify and export reconstructed DMA channel deallocation for source admission."""
import json,shutil
from pathlib import Path
from verify_gx8002_dma_deallocate import verify as core,ROOT,sha
from verify_gx8002_logging import check_paths
from verify_gx8002_dma_deallocate_irq import verify as irq


def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk)
    qualification=core();interrupts=json.loads(json.dumps(irq()))
    candidate=qualification['candidate'];item=candidate['functions'][0]
    if not item['fits']:raise ValueError('DMA deallocation envelope')
    row={key:item[key] for key in ('symbol','compiled_bytes','compiled_sha256')}
    row['section_name']='.text'
    row['stock_occurrences']=[{'symbol':item['symbol'],'package_offset':item['package_offset'],
        'bytes':item['envelope_bytes'],'sha256':item['stock_sha256'],'region':'image_a_xip_text'}]
    if output:
        output=Path(output);output.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/'build/gx8002-dma-deallocate/deallocate.elf',output/'deallocate.elf')
    evidence={name:sha((ROOT/'tools'/name).read_bytes()) for name in
        ('build_gx8002_dma_deallocate.py','verify_gx8002_dma_deallocate.py','verify_gx8002_dma_deallocate_source.py','verify_gx8002_memcpy_source.py','verify_gx8002_dma_deallocate_irq.py','verify_gx8002_uart_receive_irq.py')}
    return {'functions':[row],'qualification':qualification,'interrupt_composition':interrupts,'evidence_sha256':evidence,
        'source_admitted':True,'hardware_qualified':False,
        'limits':['Ordered allocation clear and exact-one scan verified with decoded interrupt exclusion. Hardware channel domain is 0/1; clock effects remain modeled and physical concurrency is unqualified.']}

if __name__=='__main__':
    report=verify();(ROOT/'docs/research/gx8002-dma-deallocate-source-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print('DMA deallocation source qualification passed')
