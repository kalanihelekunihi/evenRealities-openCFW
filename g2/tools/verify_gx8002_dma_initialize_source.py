# SPDX-License-Identifier: MIT
"""Qualify and export reconstructed DMA initialization for source admission."""
import json,shutil
from pathlib import Path
from verify_gx8002_dma_initialize import verify as core,ROOT,sha
from verify_gx8002_logging import check_paths
from verify_gx8002_dma_owned_initialize import verify as owned


def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk)
    qualification=core();storage=json.loads(json.dumps(owned()))
    candidate=qualification['candidate'];item=candidate['functions'][0]
    if not item['fits']:raise ValueError('DMA initialization envelope')
    row={key:item[key] for key in ('symbol','compiled_bytes','compiled_sha256')}
    row['section_name']='.text'
    row['stock_occurrences']=[{'symbol':item['symbol'],'package_offset':item['package_offset'],
        'bytes':item['envelope_bytes'],'sha256':item['stock_sha256'],'region':'image_a_xip_text'}]
    if output:
        output=Path(output);output.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/'build/gx8002-dma-initialize/initialize.elf',output/'initialize.elf')
    evidence={name:sha((ROOT/'tools'/name).read_bytes()) for name in
        ('build_gx8002_dma_initialize.py','verify_gx8002_dma_initialize.py','verify_gx8002_dma_initialize_source.py','verify_gx8002_memcpy_source.py','verify_gx8002_dma_owned_initialize.py',
         'link_gx8002_dma_uart_source.py','execute_gx8002_linked_irq_registration.py')}
    return {'functions':[row],'qualification':qualification,'owned_storage_check':storage,'evidence_sha256':evidence,
        'source_admitted':True,'hardware_qualified':False,
        'limits':['Decoded initializer order and relocated source-owned storage with separate clock and IRQ registration frames. Stock-address admission retains existing RAM locations; startup BSS and physical hardware initialization remain unqualified.']}

if __name__=='__main__':
    report=verify();(ROOT/'docs/research/gx8002-dma-initialize-source-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print('DMA initialization source qualification passed')
