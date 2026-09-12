# SPDX-License-Identifier: MIT
"""Qualify and export reconstructed DMA callback registration for source admission."""
import json,shutil
from pathlib import Path
from verify_gx8002_dma_callback import verify as core,ROOT,sha
from verify_gx8002_logging import check_paths


def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk)
    qualification=core();candidate=qualification['candidate'];item=candidate['functions'][0]
    if not item['fits']:raise ValueError('DMA callback envelope')
    row={key:item[key] for key in ('symbol','compiled_bytes','compiled_sha256')}
    row['section_name']='.text'
    row['stock_occurrences']=[{'symbol':item['symbol'],'package_offset':item['package_offset'],
        'bytes':item['envelope_bytes'],'sha256':item['stock_sha256'],'region':'image_a_xip_text'}]
    if output:
        output=Path(output);output.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/'build/gx8002-dma-callback/callback.elf',output/'callback.elf')
    evidence={name:sha((ROOT/'tools'/name).read_bytes()) for name in
        ('build_gx8002_dma_callback.py','verify_gx8002_dma_callback.py','verify_gx8002_dma_callback_source.py','verify_gx8002_memcpy_source.py')}
    return {'functions':[row],'qualification':qualification,'evidence_sha256':evidence,
        'source_admitted':True,'hardware_qualified':False,
        'limits':['Decoded ordered callback/context stores and ABI verified. Valid allocated channels are 0/1; extreme values test arithmetic only. Shared storage initialization and physical interrupt concurrency remain unqualified.']}

if __name__=='__main__':
    report=verify();(ROOT/'docs/research/gx8002-dma-callback-source-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print('DMA callback source qualification passed')
