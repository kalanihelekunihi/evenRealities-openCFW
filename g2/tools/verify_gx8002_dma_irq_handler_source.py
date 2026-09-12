# SPDX-License-Identifier: MIT
"""Qualify and export reconstructed DMA interrupt handling for source admission."""
import json,shutil
from pathlib import Path
from verify_gx8002_dma_irq_handler import verify as core,ROOT,sha
from verify_gx8002_logging import check_paths
from verify_gx8002_dma_irq_completion import verify as completion


def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk)
    qualification=core();composed=json.loads(json.dumps(completion()))
    candidate=qualification['candidate'];item=candidate['functions'][0]
    if not item['fits']:raise ValueError('DMA interrupt handler envelope')
    row={key:item[key] for key in ('symbol','compiled_bytes','compiled_sha256')}
    row['section_name']='.text'
    row['stock_occurrences']=[{'symbol':item['symbol'],'package_offset':item['package_offset'],
        'bytes':item['envelope_bytes'],'sha256':item['stock_sha256'],'region':'image_a_xip_text'}]
    if output:
        output=Path(output);output.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/'build/gx8002-dma-irq-handler/irq_handler.elf',output/'irq_handler.elf')
    evidence={name:sha((ROOT/'tools'/name).read_bytes()) for name in
        ('build_gx8002_dma_irq_handler.py','verify_gx8002_dma_irq_handler.py','verify_gx8002_dma_irq_handler_source.py','verify_gx8002_memcpy_source.py','verify_gx8002_dma_irq_completion.py',
         'verify_gx8002_dma_deallocate.py','verify_gx8002_dma_release.py')}
    return {'functions':[row],'qualification':qualification,'completion_composition':composed,'evidence_sha256':evidence,
        'source_admitted':True,'hardware_qualified':False,
        'limits':['Decoded status sampling, ordered helpers and mutable callback lookup verified; nested completion preserves allocation state across channels. Separate frames, modeled clock/application callbacks and physical IRQ delivery remain unqualified.']}

if __name__=='__main__':
    report=verify();(ROOT/'docs/research/gx8002-dma-irq-handler-source-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print('DMA interrupt handler source qualification passed')
