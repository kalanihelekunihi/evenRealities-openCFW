# SPDX-License-Identifier: MIT
"""Qualify and export reconstructed UART receive completion for source admission."""
import json,shutil
from pathlib import Path
from verify_gx8002_uart_receive_complete import verify as core,ROOT,sha
from verify_gx8002_logging import check_paths
from verify_gx8002_dma_irq_completion import verify as completion


def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk)
    qualification=core();composed=json.loads(json.dumps(completion()))
    candidate=qualification['candidate'];item=candidate['functions'][0]
    if not item['fits']:raise ValueError('UART receive completion envelope')
    row={key:item[key] for key in ('symbol','compiled_bytes','compiled_sha256')}
    row['section_name']='.text'
    row['stock_occurrences']=[{'symbol':item['symbol'],'package_offset':item['package_offset'],
        'bytes':item['envelope_bytes'],'sha256':item['stock_sha256'],'region':'image_a_xip_text'}]
    if output:
        output=Path(output);output.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/'build/gx8002-uart-receive-complete/complete.elf',output/'complete.elf')
    evidence={name:sha((ROOT/'tools'/name).read_bytes()) for name in
        ('build_gx8002_uart_receive_complete.py','verify_gx8002_uart_receive_complete.py','verify_gx8002_uart_receive_complete_source.py','verify_gx8002_memcpy_source.py','verify_gx8002_dma_irq_completion.py',
         'verify_gx8002_dma_deallocate.py','verify_gx8002_dma_release.py')}
    return {'functions':[row],'qualification':qualification,'completion_composition':composed,'evidence_sha256':evidence,
        'source_admitted':True,'hardware_qualified':False,
        'limits':['Decoded channel release, cache range and mutable callback argument order verified; nested IRQ completion preserves allocation state across channels. Separate frames, modeled clock/application callbacks and physical coherence remain unqualified.']}

if __name__=='__main__':
    report=verify();(ROOT/'docs/research/gx8002-uart-receive-complete-source-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print('UART receive completion source qualification passed')
